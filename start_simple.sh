#!/bin/bash

# Research Paper Search Application Startup Script (Simple Version)

echo "Starting Research Paper Search Application (Simple Version)..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install minimal dependencies
echo "Installing dependencies..."
pip install -r requirements-minimal.txt

# Create necessary directories
mkdir -p uploads static templates

# Start the application
echo "Starting FastAPI application..."
echo "Chat Interface: http://localhost:8000/chat"
echo "Admin Panel: http://localhost:8000/admin"
echo "API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the application"

python main_simple.py
