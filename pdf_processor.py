import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.schema import Document
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

class ResearchPaperProcessor:
    def __init__(self, upload_dir: str = "uploads", vector_db_dir: str = "vector_db"):
        self.upload_dir = Path(upload_dir)
        self.vector_db_dir = Path(vector_db_dir)
        self.vector_db_dir.mkdir(exist_ok=True)
        
        # Track processed papers in a simple JSON file
        self.processed_papers_file = self.vector_db_dir / "processed_papers.json"
        self.processed_papers = self._load_processed_papers()
        
        # Initialize OpenAI components
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize ChromaDB
        self.vectorstore = None
        self.qa_chain = None
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        self._initialize_vectorstore()
    
    def _load_processed_papers(self) -> Dict[str, Any]:
        """Load processed papers from JSON file"""
        try:
            if self.processed_papers_file.exists():
                with open(self.processed_papers_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading processed papers: {e}")
            return {}
    
    def _save_processed_papers(self):
        """Save processed papers to JSON file"""
        try:
            with open(self.processed_papers_file, 'w') as f:
                json.dump(self.processed_papers, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving processed papers: {e}")
    
    def _initialize_vectorstore(self):
        """Initialize the vector store"""
        try:
            logger.info("Initializing vector store...")
            
            # Create persistent ChromaDB
            self.vectorstore = Chroma(
                persist_directory=str(self.vector_db_dir),
                embedding_function=self.embeddings,
                collection_name="research_papers"
            )
            
            logger.info(f"Vector store created: {self.vectorstore is not None}")
            
            # Initialize QA chain
            llm = OpenAI(temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(search_kwargs={"k": 4}),
                return_source_documents=True
            )
            
            logger.info(f"QA chain created: {self.qa_chain is not None}")
            logger.info("Vector store initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
            self.vectorstore = None
            self.qa_chain = None
    
    def process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Process a PDF file and add it to the vector store"""
        try:
            logger.info(f"Processing PDF: {file_path}")
            
            # Load PDF
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            
            # Split documents into chunks
            texts = self.text_splitter.split_documents(documents)
            
            # Add metadata
            for i, text in enumerate(texts):
                text.metadata.update({
                    "source": file_path.name,
                    "chunk_id": i,
                    "file_type": "pdf"
                })
            
            # Add to vector store
            if self.vectorstore:
                self.vectorstore.add_documents(texts)
                # ChromaDB auto-persists when using persist_directory
            
            # Track processed paper
            self.processed_papers[file_path.name] = {
                "processed_at": datetime.now().isoformat(),
                "chunks_processed": len(texts),
                "total_characters": sum(len(text.page_content) for text in texts),
                "status": "processed"
            }
            self._save_processed_papers()
            
            logger.info(f"Successfully processed {len(texts)} chunks from {file_path.name}")
            
            return {
                "status": "success",
                "filename": file_path.name,
                "chunks_processed": len(texts),
                "total_characters": sum(len(text.page_content) for text in texts)
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            return {
                "status": "error",
                "filename": file_path.name,
                "error": str(e)
            }
    
    def query_papers(self, question: str) -> Dict[str, Any]:
        """Query the research papers using the QA chain"""
        try:
            # Try vector store approach first
            if self.qa_chain and self.vectorstore:
                logger.info(f"Querying papers with question: {question[:100]}...")
                
                # Get response from QA chain
                result = self.qa_chain({"query": question})
                
                logger.info(f"QA chain result keys: {result.keys()}")
                
                # Extract source documents
                sources = []
                if "source_documents" in result:
                    logger.info(f"Found {len(result['source_documents'])} source documents")
                    for doc in result["source_documents"]:
                        sources.append({
                            "content": doc.page_content[:200] + "...",  # Truncate for display
                            "source": doc.metadata.get("source", "Unknown"),
                            "chunk_id": doc.metadata.get("chunk_id", 0)
                        })
                    
                    return {
                        "answer": result["result"],
                        "sources": sources,
                        "question": question
                    }
                else:
                    logger.warning("No source_documents found in result")
            else:
                logger.warning("Vector store or QA chain not available")
            
            # Fallback: Search through actual paper content and cite specific papers
            logger.info("Using enhanced fallback with paper content search")
            try:
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                # Search through actual paper content for relevant information
                relevant_papers = []
                search_terms = question.lower().split()
                
                for filename, info in self.processed_papers.items():
                    if info.get("status") == "processed":
                        # Load and search through the actual paper content
                        try:
                            pdf_path = self.upload_dir / filename
                            if pdf_path.exists():
                                loader = PyPDFLoader(str(pdf_path))
                                documents = loader.load()
                                paper_content = "\n".join([doc.page_content for doc in documents])
                                
                                # Simple keyword matching to find relevant papers
                                content_lower = paper_content.lower()
                                relevance_score = 0
                                
                                for term in search_terms:
                                    if term in content_lower:
                                        relevance_score += content_lower.count(term)
                                
                                # Also check for XYY-related terms
                                xyy_terms = ["xyy", "47,xyy", "jacob", "syndrome", "trisomy", "chromosome"]
                                for term in xyy_terms:
                                    if term in content_lower:
                                        relevance_score += content_lower.count(term) * 2
                                
                                if relevance_score > 0:
                                    # Extract relevant snippets (first 2000 chars)
                                    relevant_snippet = paper_content[:2000] + "..." if len(paper_content) > 2000 else paper_content
                                    relevant_papers.append({
                                        "filename": filename,
                                        "relevance_score": relevance_score,
                                        "content": relevant_snippet
                                    })
                        except Exception as e:
                            logger.warning(f"Error processing paper {filename} for search: {e}")
                            continue
                
                # Sort by relevance and take top 3 papers
                relevant_papers.sort(key=lambda x: x["relevance_score"], reverse=True)
                top_papers = relevant_papers[:3]
                
                if top_papers:
                    # Create context from most relevant papers
                    context_parts = []
                    sources = []
                    
                    for i, paper in enumerate(top_papers):
                        context_parts.append(f"Paper {i+1}: {paper['filename']}\nContent: {paper['content']}\n")
                        sources.append({
                            "content": paper['content'][:200] + "...",
                            "source": paper['filename'],
                            "chunk_id": i
                        })
                    
                    context_text = "\n".join(context_parts)
                    
                    # Generate response with specific paper citations
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": f"You are a research assistant. Answer the user's question based on the following research papers about XYY syndrome. Always cite the specific papers you reference using their filenames. Be specific and accurate.\n\nResearch Papers:\n{context_text}"},
                            {"role": "user", "content": question}
                        ],
                        max_tokens=600,
                        temperature=0.3
                    )

                    answer = response.choices[0].message.content

                    # Add clickable links to the sources
                    enhanced_sources = []
                    for source in sources:
                        filename = source["source"]
                        enhanced_sources.append({
                            "content": source["content"],
                            "source": filename,
                            "chunk_id": source["chunk_id"],
                            "pdf_link": f"/paper/{filename}",
                            "summary_link": f"/paper/{filename}/summary"
                        })

                    return {
                        "answer": answer,
                        "sources": enhanced_sources,
                        "question": question
                    }
                else:
                    # No relevant papers found, provide general answer
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a research assistant helping users find information about XYY syndrome. Provide helpful information based on your knowledge, but mention that you have access to a collection of research papers that may contain more specific information."},
                            {"role": "user", "content": question}
                        ],
                        max_tokens=500,
                        temperature=0.3
                    )
                    
                    answer = response.choices[0].message.content
                    
                    return {
                        "answer": answer,
                        "sources": [{"content": "General knowledge about XYY syndrome", "source": "AI Knowledge Base", "chunk_id": 0}],
                        "question": question
                    }
                
            except Exception as e:
                logger.error(f"OpenAI fallback failed: {e}")
                return {
                    "answer": f"I'm sorry, I'm having trouble accessing the research papers right now. Please try again later. Error: {str(e)}",
                    "sources": [],
                    "question": question
                }
            
        except Exception as e:
            logger.error(f"Error querying papers: {e}")
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "question": question
            }
    
    def get_paper_summary(self, filename: str) -> Dict[str, Any]:
        """Get a summary of a specific paper"""
        try:
            # Check if paper is processed
            if filename not in self.processed_papers:
                return {
                    "filename": filename,
                    "summary": "Paper not found or not processed yet.",
                    "sources": []
                }
            
            # Try to get summary from vector store first
            try:
                if self.vectorstore and self.qa_chain:
                    summary_query = f"Provide a comprehensive summary of the research paper {filename}. Include the main research question, methodology, key findings, and conclusions."
                    result = self.query_papers(summary_query)
                    
                    if result["sources"]:
                        return {
                            "filename": filename,
                            "summary": result["answer"],
                            "sources": result["sources"]
                        }
            except Exception as e:
                logger.warning(f"Vector store query failed: {e}")
            
            # Fallback: Generate a basic summary using OpenAI directly
            try:
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
                # Read the PDF file and extract text
                pdf_path = self.upload_dir / filename
                if pdf_path.exists():
                    loader = PyPDFLoader(str(pdf_path))
                    documents = loader.load()
                    text_content = "\n".join([doc.page_content for doc in documents])
                    
                    # Truncate if too long
                    if len(text_content) > 4000:
                        text_content = text_content[:4000] + "..."
                    
                    # Generate summary using OpenAI
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a research assistant. Provide a comprehensive summary of research papers."},
                            {"role": "user", "content": f"Please provide a comprehensive summary of this research paper:\n\n{text_content}"}
                        ],
                        max_tokens=500,
                        temperature=0.3
                    )
                    
                    summary = response.choices[0].message.content
                    
                    return {
                        "filename": filename,
                        "summary": summary,
                        "sources": [{"content": "Summary generated from full paper content", "source": filename, "chunk_id": 0}]
                    }
                else:
                    return {
                        "filename": filename,
                        "summary": "Paper file not found.",
                        "sources": []
                    }
                    
            except Exception as e:
                logger.error(f"OpenAI fallback failed: {e}")
                return {
                    "filename": filename,
                    "summary": f"Unable to generate summary: {str(e)}",
                    "sources": []
                }
            
        except Exception as e:
            logger.error(f"Error getting paper summary for {filename}: {e}")
            return {
                "filename": filename,
                "summary": f"Error generating summary: {str(e)}",
                "sources": []
            }
    
    def list_processed_papers(self) -> List[Dict[str, Any]]:
        """List all processed papers using simple tracking"""
        try:
            papers = []
            for filename, info in self.processed_papers.items():
                if info.get("status") == "processed":
                    papers.append({
                        "filename": filename,
                        "processed": True,
                        "status": "available",
                        "processed_at": info.get("processed_at"),
                        "chunks_processed": info.get("chunks_processed", 0)
                    })
            
            logger.info(f"Found {len(papers)} processed papers")
            return papers
            
        except Exception as e:
            logger.error(f"Error listing processed papers: {e}")
            return []
    
    def reprocess_all_papers(self) -> Dict[str, Any]:
        """Reprocess all PDFs in the upload directory"""
        try:
            pdf_files = list(self.upload_dir.glob("*.pdf"))
            results = []
            
            # Clear existing vector store and tracking
            if self.vectorstore:
                self.vectorstore.delete_collection()
            
            # Clear processed papers tracking
            self.processed_papers = {}
            self._save_processed_papers()
            
            # Reinitialize vector store after clearing
            self._initialize_vectorstore()
            
            for pdf_file in pdf_files:
                result = self.process_pdf(pdf_file)
                results.append(result)
            
            # Ensure vector store is properly initialized after processing
            if not self.vectorstore:
                self._initialize_vectorstore()
            
            logger.info(f"Reprocessing completed. Processed {len(results)} files.")
            
            return {
                "status": "completed",
                "total_files": len(pdf_files),
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error reprocessing papers: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

# Global processor instance
paper_processor = None

def get_paper_processor() -> ResearchPaperProcessor:
    """Get or create the paper processor instance"""
    global paper_processor
    if paper_processor is None:
        paper_processor = ResearchPaperProcessor()
    return paper_processor
