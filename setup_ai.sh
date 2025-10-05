#!/bin/bash

# AI Setup Script for Research Paper Search Application
echo "🤖 Setting up AI-powered research paper search..."

# Step 1: Collect secrets and create .env file
echo "📝 Creating .env file with API key..."

read -p "Enter your OpenAI API key: " OPENAI_API_KEY
read -p "Enter an admin token (leave blank to use default): " ADMIN_TOKEN_INPUT
read -p "Enter a public token (leave blank to use default): " PUBLIC_TOKEN_INPUT

ADMIN_TOKEN_VALUE=${ADMIN_TOKEN_INPUT:-admin123}
PUBLIC_TOKEN_VALUE=${PUBLIC_TOKEN_INPUT:-public123}

cat > .env << EOF
OPENAI_API_KEY=${OPENAI_API_KEY}
ADMIN_TOKEN=${ADMIN_TOKEN_VALUE}
PUBLIC_TOKEN=${PUBLIC_TOKEN_VALUE}
DEBUG=True
HOST=0.0.0.0
PORT=8000
EOF

echo "✅ .env file created successfully"

# Step 2: Activate virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Step 3: Install AI dependencies
echo "📦 Installing AI dependencies..."
echo "Installing OpenAI..."
pip install openai

echo "Installing LangChain..."
pip install langchain

echo "Installing LangChain OpenAI..."
pip install langchain-openai

echo "Installing ChromaDB..."
pip install chromadb

echo "✅ All AI dependencies installed successfully"

# Step 4: Test API key
echo "🔑 Testing API key..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if api_key and api_key.startswith('sk-'):
    print('✅ API key loaded successfully')
    print(f'Key starts with: {api_key[:10]}...')
else:
    print('❌ API key not found or invalid')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ API key test passed"
else
    echo "❌ API key test failed"
    exit 1
fi

# Step 5: Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads vector_db static templates

# Step 6: Test AI imports
echo "🧪 Testing AI imports..."
python -c "
try:
    import openai
    import langchain
    import chromadb
    print('✅ All AI packages imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ AI imports test passed"
else
    echo "❌ AI imports test failed"
    exit 1
fi

echo ""
echo "🎉 AI setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Stop the current server (Ctrl+C)"
echo "2. Run: python main.py"
echo "3. Go to http://localhost:8000/admin"
echo "4. Click 'Reprocess All' to process your PDFs with AI"
echo "5. Test the chat interface with intelligent questions"
echo ""
echo "Your XYY syndrome research papers are ready for AI analysis! 🚀"
