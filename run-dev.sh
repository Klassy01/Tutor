#!/bin/bash

# Enhanced development server script for AI-Powered Personal Tutor
# Runs the FastAPI backend with all AI features enabled

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${CYAN}$1${NC}"
}

# Header
echo
print_header "🚀 AI-Powered Personal Tutor - Development Server"
print_header "================================================="
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found!"
    print_status "Please run ./setup.sh first to set up the environment."
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found!"
    print_status "Using default configuration. Some features may not work."
    print_status "Please create .env file from .env.example for full functionality."
else
    print_success ".env configuration loaded"
fi

# Check database connection
print_status "Checking database connection..."
python3 << EOF
try:
    from backend.core.database import engine
    from sqlalchemy import text
    
    # Test database connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
    
    print("✅ Database connection successful")
except Exception as e:
    print(f"⚠️  Database connection warning: {e}")
    print("The application will start but database features may not work properly.")
EOF

# Check AI provider configuration
print_status "Checking AI provider configuration..."
python3 << EOF
try:
    from backend.core.config import settings
    
    providers = []
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
        providers.append("OpenAI")
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your-gemini-api-key-here":
        providers.append("Gemini")
    if settings.HUGGINGFACE_API_TOKEN and settings.HUGGINGFACE_API_TOKEN != "your-huggingface-token-here":
        providers.append("Hugging Face")
    
    if providers:
        print(f"✅ AI Providers configured: {', '.join(providers)}")
        print(f"🎯 Active provider: {settings.AI_PROVIDER}")
    else:
        print("⚠️  No AI providers configured!")
        print("Please add API keys to .env file for AI tutoring features.")
        print("Supported providers: OpenAI, Google Gemini, Hugging Face")
        
except Exception as e:
    print(f"❌ Configuration error: {e}")
EOF

# Create necessary directories if they don't exist
print_status "Creating necessary directories..."
mkdir -p data/faiss_index
mkdir -p models
mkdir -p logs
mkdir -p static
print_success "Directories ready"

# Check for optional dependencies
print_status "Checking optional features..."

# Check Redis (for caching and background tasks)
python3 << EOF
import subprocess
import sys

try:
    import redis
    # Try to connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    print("✅ Redis available for caching and background tasks")
except redis.ConnectionError:
    print("⚠️  Redis not running - caching features disabled")
except ImportError:
    print("⚠️  Redis library not installed - caching features disabled")
except Exception as e:
    print(f"⚠️  Redis check failed: {e}")
EOF

# Check if we can load ML models
python3 << EOF
try:
    from sentence_transformers import SentenceTransformer
    print("✅ Sentence Transformers available for content recommendations")
except ImportError:
    print("⚠️  Sentence Transformers not installed - using basic recommendations")
except Exception as e:
    print(f"⚠️  ML libraries check failed: {e}")

try:
    import faiss
    print("✅ FAISS available for similarity search")
except ImportError:
    print("⚠️  FAISS not installed - using basic similarity search")
except Exception as e:
    print(f"⚠️  FAISS check failed: {e}")
EOF

# Start the development server
echo
print_header "🎯 Starting Development Server"
print_header "==============================="
print_status "Server will be available at: http://localhost:8001"
print_status "API Documentation: http://localhost:8001/docs"
print_status "Alternative Docs: http://localhost:8001/redoc"
print_status "Health Check: http://localhost:8001/health"
print_status "WebSocket Chat: ws://localhost:8001/ws/tutor/{student_id}"
echo

# Display feature status
print_header "🔧 Available Features:"
echo "📚 Core Features:"
echo "   ✅ REST API with FastAPI"
echo "   ✅ JWT Authentication"
echo "   ✅ WebSocket Real-time Chat"
echo "   ✅ Database Integration"
echo
echo "🤖 AI Features:"
echo "   • Multi-provider AI support (OpenAI, Gemini, Hugging Face)"
echo "   • Intelligent tutoring responses"
echo "   • Automated quiz generation"
echo "   • Personalized feedback"
echo "   • Content recommendations"
echo
echo "📊 Analytics & Tracking:"
echo "   • Learning session tracking"
echo "   • Progress monitoring"
echo "   • Adaptive difficulty adjustment"
echo "   • Performance analytics"
echo

print_warning "Press Ctrl+C to stop the server"
echo

# Run the server with enhanced settings
uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8001 \
    --reload \
    --reload-dir backend \
    --log-level info \
    --access-log \
    --use-colors
