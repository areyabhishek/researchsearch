# Research Paper Search Application

A web application that allows users to search and query research papers using natural language. Built with FastAPI, LangChain, and ChromaDB.

## Features

- **PDF Upload**: Admin panel for uploading research papers in PDF format
- **Intelligent Search**: Chat interface powered by LangChain and OpenAI for querying papers
- **Vector Storage**: Uses ChromaDB for efficient similarity search
- **Authentication**: Separate access for admin (upload) and public (search) users
- **Responsive UI**: Modern web interface with Bootstrap

## Architecture

- **Backend**: FastAPI with LangChain integration
- **Vector Database**: ChromaDB for document embeddings
- **Frontend**: HTML templates with Bootstrap and JavaScript
- **Authentication**: Token-based authentication
- **File Processing**: PyPDF2 for PDF text extraction

## Setup Instructions

### 1. Environment Setup

```bash
# Clone or download the project
cd "research-paper-search"

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env file with your OpenAI API key
# OPENAI_API_KEY=your_actual_api_key_here
```

### 2. Run Locally

```bash
# Start the application
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Access the Application

- **Chat Interface**: http://localhost:8000/chat
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/docs

## Usage

### Admin Panel (Upload Papers)
1. Go to `/admin`
2. Use token: `admin123` (or set ADMIN_TOKEN in .env)
3. Upload PDF files by dragging and dropping or clicking to browse
4. Papers are automatically processed and indexed

### Chat Interface (Search Papers)
1. Go to `/chat`
2. Use token: `public123` (or set PUBLIC_TOKEN in .env)
3. Ask questions about the uploaded research papers
4. View source citations for each answer

## API Endpoints

- `POST /upload` - Upload PDF files (admin only)
- `GET /papers` - List all uploaded papers
- `POST /chat` - Query papers with natural language
- `POST /reprocess` - Reprocess all papers (admin only)
- `GET /paper/{filename}/summary` - Get paper summary

## Deployment on Render

### 1. Prepare for Deployment

```bash
# Create a render.yaml file (optional)
# Set environment variables in Render dashboard
```

### 2. Environment Variables for Render

Set these in your Render service:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ADMIN_TOKEN`: Admin access token
- `PUBLIC_TOKEN`: Public access token

### 3. Deploy

1. Connect your GitHub repository to Render
2. Choose "Web Service"
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy!

## File Structure

```
research-paper-search/
├── main.py                 # FastAPI application
├── pdf_processor.py        # LangChain PDF processing
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── env.example            # Environment template
├── templates/             # HTML templates
│   ├── chat.html         # Chat interface
│   └── admin.html        # Admin panel
├── uploads/              # PDF storage (created at runtime)
└── vector_db/           # ChromaDB storage (created at runtime)
```

## Security Notes

- Change default tokens in production
- Use proper JWT authentication for production
- Implement rate limiting
- Add file size limits
- Validate file types strictly

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Make sure your API key is set correctly
2. **PDF Processing Fails**: Check if PyPDF2 can read your PDF files
3. **Vector Store Issues**: Delete `vector_db` folder to reset
4. **Memory Issues**: Reduce chunk size in pdf_processor.py

### Logs

Check application logs for detailed error messages:
```bash
# Run with debug logging
python main.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
