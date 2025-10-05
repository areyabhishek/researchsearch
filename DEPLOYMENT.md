# Deployment Guide - Research Paper Search Application

This guide will help you deploy your research paper application to make it publicly accessible on the internet.

## 🚀 Quick Deploy to Render.com (Recommended)

Render.com offers a free tier that's perfect for this application. The deployment is already configured!

### Step 1: Prepare Your Repository

1. **Create a GitHub repository** (if you haven't already):
   ```bash
   cd "research-paper-search"
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

### Step 2: Deploy to Render

1. **Go to [Render.com](https://render.com)** and sign up/login

2. **Click "New +" → "Web Service"**

3. **Connect your GitHub repository**:
   - Grant Render access to your GitHub account
   - Select your repository

4. **Configure the service** (most settings are pre-filled from render.yaml):
   - Name: `research-paper-search` (or your choice)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

5. **Add Environment Variables**:
   - Click "Advanced" → "Add Environment Variable"
   - Add these variables:

     | Key | Value | Notes |
     |-----|-------|-------|
     | `OPENAI_API_KEY` | `your-api-key-here` | Required: Get from OpenAI |
     | `ADMIN_TOKEN` | Auto-generated or custom | Render will auto-generate |
     | `PUBLIC_TOKEN` | Auto-generated or custom | Render will auto-generate |

6. **Enable Persistent Disk** (Important for file storage):
   - Scroll to "Disks" section
   - Add disk:
     - Name: `research-data`
     - Mount Path: `/opt/render/project/src/data`
     - Size: `1 GB` (free tier)

7. **Click "Create Web Service"**

8. **Wait for deployment** (3-5 minutes)
   - Watch the logs for any errors
   - Once deployed, you'll get a URL like: `https://research-paper-search.onrender.com`

### Step 3: Access Your Application

Your app will be live at: `https://YOUR_APP_NAME.onrender.com`

- **Chat Interface**: `https://YOUR_APP_NAME.onrender.com/chat`
- **Admin Panel**: `https://YOUR_APP_NAME.onrender.com/admin`
- **API Docs**: `https://YOUR_APP_NAME.onrender.com/docs`

### Step 4: Get Your Access Tokens

After deployment, go to the Render dashboard → Your service → Environment:
1. Find `ADMIN_TOKEN` value - use this for the admin panel
2. Find `PUBLIC_TOKEN` value - use this for the chat interface

---

## 🔧 Alternative Deployment Options

### Option 2: Railway.app

Railway offers simple deployment with automatic HTTPS and custom domains.

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login and deploy**:
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Add environment variables**:
   ```bash
   railway variables set OPENAI_API_KEY=your-key-here
   railway variables set ADMIN_TOKEN=your-admin-token
   railway variables set PUBLIC_TOKEN=your-public-token
   ```

4. **Add persistent volume**:
   - Go to Railway dashboard
   - Add volume: `/data` → 1GB
   - Set env vars: `UPLOAD_DIR=/data/uploads`, `VECTOR_DB_DIR=/data/vector_db`

### Option 3: Fly.io

Fly.io provides free tier with excellent performance.

1. **Install Fly CLI**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Create Dockerfile** (if not exists):
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
   ```

3. **Deploy**:
   ```bash
   fly launch
   fly secrets set OPENAI_API_KEY=your-key-here
   fly volumes create research_data --size 1
   fly deploy
   ```

### Option 4: DigitalOcean App Platform

1. Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Click "Create App" → Connect GitHub
3. Select your repository
4. DigitalOcean auto-detects Python
5. Add environment variables
6. Add managed database or volume for persistence
7. Deploy!

---

## 🔐 Security Best Practices

### 1. Change Default Tokens
Never use `admin123` or `public123` in production!

Generate secure tokens:
```bash
# Generate random tokens
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. CORS Configuration
Update [main.py](main.py#L30) for production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Replace with your domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting
Consider adding rate limiting to prevent abuse:
```bash
pip install slowapi
```

### 4. HTTPS Only
Most platforms (Render, Railway, Fly.io) provide HTTPS automatically.

---

## 📊 Monitoring & Maintenance

### Check Application Logs
- **Render**: Dashboard → Logs tab
- **Railway**: Dashboard → Deployments → View logs
- **Fly.io**: `fly logs`

### Monitor OpenAI API Usage
- Go to [OpenAI Usage Dashboard](https://platform.openai.com/usage)
- Set up billing alerts

### Backup Vector Database
Periodically backup your vector database:
```bash
# Download from Render
render disk snapshot research-data

# Or use the API to export processed papers
curl -H "Authorization: Bearer YOUR_PUBLIC_TOKEN" \
  https://your-app.onrender.com/papers
```

---

## 🐛 Troubleshooting

### Issue: "OpenAI API Error"
**Solution**: Check your API key in environment variables

### Issue: "Files not persisting"
**Solution**: Ensure persistent disk/volume is configured correctly

### Issue: "Memory errors"
**Solution**: Upgrade to paid tier or reduce chunk size in [pdf_processor.py](pdf_processor.py#L38)

### Issue: "Slow responses"
**Solution**:
- Render free tier spins down after inactivity (30 sec startup)
- Upgrade to paid tier for always-on service
- Or use Railway/Fly.io which have better free tier performance

### Issue: "CORS errors"
**Solution**: Update CORS configuration in [main.py](main.py#L30)

---

## 💰 Cost Estimates

### Free Tier (Adequate for testing/personal use)
- **Render**: Free (with limitations)
- **Railway**: $5 credit/month
- **Fly.io**: 3 VMs free
- **OpenAI API**: Pay per use (~$0.002 per 1K tokens)

### Paid Tier (For production)
- **Render**: $7/month (Starter)
- **Railway**: ~$5-10/month
- **Fly.io**: ~$5-10/month
- **OpenAI API**: Depends on usage

---

## 🎯 Next Steps After Deployment

1. **Test your deployment**:
   - Upload a test PDF via admin panel
   - Ask questions in chat interface
   - Verify file persistence

2. **Share with users**:
   - Share the chat URL: `https://your-app.onrender.com/chat`
   - Provide PUBLIC_TOKEN for access

3. **Optional enhancements**:
   - Add custom domain
   - Implement user management
   - Add analytics
   - Configure email notifications

---

## 📞 Getting Help

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Fly.io Docs**: https://fly.io/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **LangChain Docs**: https://python.langchain.com

---

**Ready to deploy?** Start with Render.com using the steps above - it's the easiest option! 🚀
