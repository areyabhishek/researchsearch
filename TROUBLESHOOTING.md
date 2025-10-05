# 🚨 Troubleshooting Guide

## ✅ **GOOD NEWS: Your Application is Working!**

The application is currently running successfully on `http://localhost:8000`. Here's what you can access:

### **Available Interfaces:**
- **Chat Interface**: http://localhost:8000/chat
- **Admin Panel**: http://localhost:8000/admin  
- **API Documentation**: http://localhost:8000/docs

## 🔧 **If You Can't Access the Interfaces:**

### **1. Check if the server is running:**
```bash
# Check if the server is responding
curl http://localhost:8000/

# Should return: {"message":"Research Paper Search API","status":"running"}
```

### **2. If the server isn't running, start it:**
```bash
# Method 1: Use the simple startup script
./start_simple.sh

# Method 2: Manual start
source venv/bin/activate
python main_simple.py
```

### **3. Check for port conflicts:**
```bash
# Check what's using port 8000
lsof -i :8000

# If something else is using it, kill it or use a different port
```

### **4. Browser Issues:**
- Try refreshing the page (Ctrl+F5 or Cmd+Shift+R)
- Clear browser cache
- Try a different browser
- Check if you have any browser extensions blocking localhost

## 🎯 **How to Use the Application:**

### **Admin Panel (Upload Papers):**
1. Go to http://localhost:8000/admin
2. Drag and drop PDF files or click to browse
3. Click "Upload Selected Files"
4. Papers will be processed and available for search

### **Chat Interface (Search Papers):**
1. Go to http://localhost:8000/chat
2. Ask questions about uploaded papers
3. Example questions:
   - "What are the main findings?"
   - "Summarize the methodology"
   - "What conclusions were drawn?"

## 🔍 **Testing the Application:**

### **Test API Endpoints:**
```bash
# Test root endpoint
curl http://localhost:8000/

# Test papers list
curl -H "Authorization: Bearer public123" http://localhost:8000/papers

# Test chat (you need to upload a PDF first)
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer public123" \
  -d '{"message":"test question"}' http://localhost:8000/chat
```

## 🚀 **Next Steps:**

### **For Full LangChain Integration:**
1. Get an OpenAI API key from https://platform.openai.com/api-keys
2. Install the full requirements:
   ```bash
   source venv/bin/activate
   pip install langchain langchain-openai chromadb
   ```
3. Use `main.py` instead of `main_simple.py`

### **For Production Deployment:**
1. Change the default tokens in the environment
2. Use proper authentication (JWT tokens)
3. Add rate limiting and security measures
4. Deploy to Render using the provided configuration

## 📝 **Current Features (Simple Version):**

✅ **PDF Upload**: Upload research papers through admin panel  
✅ **Basic Search**: Simple keyword search in PDF text  
✅ **File Management**: List and manage uploaded papers  
✅ **Web Interface**: Modern, responsive UI  
✅ **Authentication**: Token-based access control  
✅ **API Documentation**: Auto-generated API docs  

## 🆘 **Still Having Issues?**

### **Common Problems & Solutions:**

1. **"Module not found" errors:**
   ```bash
   source venv/bin/activate
   pip install -r requirements-minimal.txt
   ```

2. **"Permission denied" errors:**
   ```bash
   chmod +x start_simple.sh
   ```

3. **"Port already in use" errors:**
   ```bash
   # Kill existing processes
   pkill -f "python.*main_simple"
   # Or use a different port by editing main_simple.py
   ```

4. **"File not found" errors:**
   ```bash
   # Make sure you're in the right directory
   cd "research-paper-search"
   ```

## 🎉 **Success Indicators:**

You'll know everything is working when:
- ✅ Server responds to `curl http://localhost:8000/`
- ✅ Chat interface loads at http://localhost:8000/chat
- ✅ Admin panel loads at http://localhost:8000/admin
- ✅ You can upload PDF files
- ✅ You can search through uploaded papers

The application is ready to use! 🚀
