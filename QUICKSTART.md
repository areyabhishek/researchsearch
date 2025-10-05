# Quick Start Guide

## 🚀 Getting Started

### 1. Set up your OpenAI API Key
```bash
# Copy the environment template
cp env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 2. Run the Application
```bash
# Make the startup script executable and run it
chmod +x start.sh
./start.sh

# Or run directly with Python
python main.py
```

### 3. Access the Application
- **Chat Interface**: http://localhost:8000/chat
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/docs

## 🔐 Authentication Tokens
- **Admin Token**: `admin123` (for uploading PDFs)
- **Public Token**: `public123` (for searching papers)

## 📁 How to Use

### Admin Panel (Upload Papers)
1. Go to `/admin`
2. Drag and drop PDF files or click to browse
3. Click "Upload Selected Files"
4. Papers are automatically processed and indexed

### Chat Interface (Search Papers)
1. Go to `/chat`
2. Ask questions like:
   - "What are the main findings in the papers about machine learning?"
   - "Summarize the methodology used in the research"
   - "What conclusions were drawn from the studies?"

## 🌐 Deploy to Render

### Option 1: Using render.yaml (Recommended)
1. Push your code to GitHub
2. Connect your repository to Render
3. Render will automatically detect the `render.yaml` file
4. Set your `OPENAI_API_KEY` in the Render dashboard
5. Deploy!

### Option 2: Manual Setup
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ADMIN_TOKEN`: admin123 (or your custom token)
   - `PUBLIC_TOKEN`: public123 (or your custom token)
5. Deploy!

## 🔧 Troubleshooting

### Common Issues
1. **"OpenAI API Key Error"**: Make sure your API key is set correctly in `.env`
2. **"PDF Processing Fails"**: Check if your PDF files are readable
3. **"Vector Store Issues"**: Delete the `vector_db` folder to reset
4. **"Memory Issues"**: Reduce chunk size in `pdf_processor.py`

### Getting Help
- Check the application logs for detailed error messages
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify your OpenAI API key has sufficient credits

## 📊 Features Overview

✅ **PDF Upload & Processing**: Upload research papers in PDF format  
✅ **Intelligent Search**: Natural language queries powered by LangChain  
✅ **Vector Storage**: Efficient similarity search with ChromaDB  
✅ **Admin Panel**: Dedicated interface for file management  
✅ **Chat Interface**: User-friendly search interface  
✅ **Authentication**: Separate access for admin and public users  
✅ **Responsive Design**: Works on desktop and mobile devices  
✅ **Source Citations**: See which papers provided the answers  
✅ **Paper Summaries**: Get comprehensive summaries of individual papers  

## 🎯 Next Steps

1. **Customize**: Modify the UI, add more features, or integrate with other services
2. **Scale**: Add database support, implement user management, or add more file formats
3. **Enhance**: Add more sophisticated search features, implement caching, or add analytics

Happy searching! 🔍📚
