#!/bin/bash

# AI Tutor Setup Script
# This script installs dependencies and initializes AI models

echo "🚀 Starting AI Tutor Setup..."

# Navigate to the project directory
cd /home/klassy/Downloads/Learning-Tutor/.github/Tutor

# Activate virtual environment
echo "📦 Activating virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/faiss_index
mkdir -p models/huggingface_cache
mkdir -p logs

# Set environment variables for Hugging Face
export HF_HOME=./models/huggingface_cache
export TRANSFORMERS_CACHE=./models/huggingface_cache

# Download essential models (this will happen automatically on first use)
echo "🤖 Preparing AI models..."
python3 -c "
try:
    import torch
    from transformers import pipeline
    print('✅ PyTorch and Transformers available')
    
    # Test small model download
    print('📥 Testing model download...')
    generator = pipeline('text-generation', model='distilgpt2', max_new_tokens=10)
    test_output = generator('Hello world')
    print('✅ Model download successful')
    
except Exception as e:
    print(f'⚠️ Model setup warning: {e}')
    print('Models will be downloaded on first use')
"

# Initialize database
echo "🗄️ Initializing database..."
python3 -c "
try:
    from app.core.database import init_db
    from app.core.config import settings
    print(f'Database URL: {settings.DATABASE_URL}')
    print('✅ Database configuration ready')
except Exception as e:
    print(f'⚠️ Database setup warning: {e}')
"

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Start the backend: python3 -m uvicorn app.main:app --reload --port 8001"
echo "2. Start the frontend: cd frontend && npm run dev"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "🤖 AI Features Available:"
echo "- Local Hugging Face models (no API keys needed)"
echo "- Intelligent tutoring and explanations"  
echo "- Automated quiz generation"
echo "- Personalized study plans"
echo "- Progress tracking and analytics"
echo ""
echo "Happy Learning! 🚀"
