import os
import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import Request
import uvicorn
from dotenv import load_dotenv
import logging
from datetime import datetime
import json
from pdf_processor import get_paper_processor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Research Paper Search API", version="1.0.0")

# CORS middleware - configure for production
# For development: use ["*"]
# For production: use your actual domain like ["https://yourdomain.com"]
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Create necessary directories
# Support both local development and production deployment
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
VECTOR_DB_DIR = Path(os.getenv("VECTOR_DB_DIR", "vector_db"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Authentication tokens
# WARNING: Change these in production! Never use defaults in production.
# Generate secure tokens: python -c "import secrets; print(secrets.token_urlsafe(32))"
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin123")
PUBLIC_TOKEN = os.getenv("PUBLIC_TOKEN", "public123")

# Security check: warn if using default tokens
if ADMIN_TOKEN == "admin123" or PUBLIC_TOKEN == "public123":
    logger.warning("⚠️  WARNING: Using default tokens! Change ADMIN_TOKEN and PUBLIC_TOKEN in production!")

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
    
    # Process the PDF with LangChain
    try:
        processor = get_paper_processor()
        process_result = processor.process_pdf(file_path)
        
        return {
            "message": f"File {file.filename} uploaded and processed successfully",
            "filename": file.filename,
            "timestamp": datetime.now().isoformat(),
            "processing_result": process_result
        }
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return {
            "message": f"File {file.filename} uploaded but processing failed",
            "filename": file.filename,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/papers")
async def list_papers(token: str = Depends(verify_token)):
    """List all uploaded research papers"""
    papers = []
    for file_path in UPLOAD_DIR.glob("*.pdf"):
        papers.append({
            "filename": file_path.name,
            "size": file_path.stat().st_size,
            "uploaded_at": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        })
    
    # Get processed papers info
    try:
        processor = get_paper_processor()
        processed_papers = processor.list_processed_papers()
        
        # Merge information
        for paper in papers:
            processed_info = next((p for p in processed_papers if p["filename"] == paper["filename"]), None)
            if processed_info:
                paper["processed"] = True
                paper["status"] = "available"
            else:
                paper["processed"] = False
                paper["status"] = "needs_processing"
    except Exception as e:
        logger.error(f"Error getting processed papers info: {e}")
        for paper in papers:
            paper["processed"] = False
            paper["status"] = "unknown"
    
    return {"papers": papers}

@app.post("/chat")
async def chat_with_papers(
    message: dict,
    token: str = Depends(verify_token)
):
    """Chat endpoint for querying research papers"""
    try:
        processor = get_paper_processor()
        question = message.get("message", "")
        
        if not question.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Query the papers
        result = processor.query_papers(question)
        
        return {
            "response": result["answer"],
            "sources": result["sources"],
            "question": question,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/reprocess")
async def reprocess_papers(token: str = Depends(verify_admin_token)):
    """Reprocess all papers (admin only)"""
    try:
        processor = get_paper_processor()
        result = processor.reprocess_all_papers()
        
        return {
            "message": "Papers reprocessed successfully",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error reprocessing papers: {e}")
        raise HTTPException(status_code=500, detail=f"Error reprocessing papers: {str(e)}")

@app.get("/paper/{filename}")
async def view_paper(filename: str, token: str = Query(None)):
    """View a research paper PDF"""
    # Verify token
    if not token or token not in [os.getenv("ADMIN_TOKEN"), os.getenv("PUBLIC_TOKEN")]:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # Return the PDF file
    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )



@app.get("/paper/{filename}/summary")
async def get_paper_summary(filename: str, token: str = Depends(verify_token)):
    """Get summary of a specific paper"""
    try:
        processor = get_paper_processor()
        result = processor.get_paper_summary(filename)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting paper summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting paper summary: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
