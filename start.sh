#!/bin/bash

# Research Paper Search Application Startup Script

echo "Starting Research Paper Search Application..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "Please edit .env file and add your OpenAI API key before running again."
    echo "You can get an API key from: https://platform.openai.com/api-keys"
    exit 1
fi

# Check if OpenAI API key is set
if grep -q "your_openai_api_key_here" .env; then
    echo "Please set your OpenAI API key in the .env file"
    echo "You can get an API key from: https://platform.openai.com/api-keys"
    exit 1
fi

# Create necessary directories
mkdir -p uploads vector_db static templates

# Install dependencies if requirements.txt exists
if [ -f requirements.txt ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the application
echo "Starting FastAPI application..."
echo "Chat Interface: http://localhost:8000/chat"
echo "Admin Panel: http://localhost:8000/admin"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the application"

python main.py
