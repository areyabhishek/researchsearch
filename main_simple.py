import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request
import uvicorn
from dotenv import load_dotenv
import logging
from datetime import datetime
import json
import PyPDF2

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Research Paper Search API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Create necessary directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Simple admin token (in production, use proper JWT or OAuth)
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin123")
PUBLIC_TOKEN = os.getenv("PUBLIC_TOKEN", "public123")

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify authentication token"""
    if credentials.credentials not in [ADMIN_TOKEN, PUBLIC_TOKEN]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
    return credentials.credentials

def verify_admin_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin authentication token"""
    if credentials.credentials != ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return credentials.credentials

@app.get("/")
async def root():
    """Root endpoint - serve the main application"""
    return {"message": "Research Paper Search API", "status": "running"}

@app.get("/chat", response_class=HTMLResponse)
async def chat_interface(request: Request):
    """Serve the chat interface"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    """Serve the admin panel"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    token: str = Depends(verify_admin_token)
):
    """Upload a PDF file (admin only)"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    logger.info(f"Uploaded file: {file.filename}")
    
    return {
        "message": f"File {file.filename} uploaded successfully",
        "filename": file.filename,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/papers")
async def list_papers(token: str = Depends(verify_token)):
    """List all uploaded research papers"""
    papers = []
    for file_path in UPLOAD_DIR.glob("*.pdf"):
        papers.append({
            "filename": file_path.name,
            "size": file_path.stat().st_size,
            "uploaded_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            "processed": True,
            "status": "available"
        })
    
    return {"papers": papers}

@app.post("/chat")
async def chat_with_papers(
    message: dict,
    token: str = Depends(verify_token)
):
    """Chat endpoint for querying research papers"""
    question = message.get("message", "")
    
    if not question.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Simple text search in PDFs (without LangChain for now)
    results = []
    for file_path in UPLOAD_DIR.glob("*.pdf"):
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                # Simple keyword search
                if question.lower() in text.lower():
                    results.append({
                        "source": file_path.name,
                        "content": text[:200] + "...",
                        "relevance": "Found keyword match"
                    })
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
    
    if results:
        response = f"Found {len(results)} relevant papers. Here are the matches:"
        for result in results:
            response += f"\n\nFrom {result['source']}: {result['content']}"
    else:
        response = "No relevant papers found. Try uploading some PDF files first or rephrase your question."
    
    return {
        "response": response,
        "sources": results,
        "question": question,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/paper/{filename}/summary")
async def get_paper_summary(filename: str, token: str = Depends(verify_token)):
    """Get summary of a specific paper"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Paper not found")
    
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            # Simple summary (first 500 characters)
            summary = text[:500] + "..." if len(text) > 500 else text
            
            return {
                "filename": filename,
                "summary": summary,
                "total_pages": len(pdf_reader.pages),
                "total_characters": len(text)
            }
    except Exception as e:
        logger.error(f"Error reading PDF {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading PDF: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
