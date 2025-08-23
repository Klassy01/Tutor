#!/bin/bash

# AI-Powered Personal Tutor - PostgreSQL Setup Script
# This script sets up PostgreSQL database for the learning tutor system

set -e

echo "🚀 Setting up AI-Powered Personal Tutor with PostgreSQL..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if PostgreSQL is installed
check_postgresql() {
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL is already installed"
        return 0
    else
        print_warning "PostgreSQL is not installed"
        return 1
    fi
}

# Install PostgreSQL on different systems
install_postgresql() {
    print_status "Installing PostgreSQL..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Ubuntu/Debian
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib libpq-dev
        # CentOS/RHEL/Fedora
        elif command -v yum &> /dev/null; then
            sudo yum install -y postgresql postgresql-server postgresql-devel
            sudo postgresql-setup initdb
            sudo systemctl enable postgresql
            sudo systemctl start postgresql
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y postgresql postgresql-server postgresql-devel
            sudo postgresql-setup --initdb
            sudo systemctl enable postgresql
            sudo systemctl start postgresql
        else
            print_error "Unsupported Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install postgresql
            brew services start postgresql
        else
            print_error "Homebrew is required for macOS installation"
            exit 1
        fi
    else
        print_error "Unsupported operating system"
        exit 1
    fi
}

# Start PostgreSQL service
start_postgresql() {
    print_status "Starting PostgreSQL service..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql
    fi
    
    print_success "PostgreSQL service started"
}

# Create database and user
setup_database() {
    print_status "Setting up database and user..."
    
    # Create user and database
    sudo -u postgres psql << EOF
CREATE USER tutor_user WITH PASSWORD 'tutor_password';
CREATE DATABASE ai_tutor_db OWNER tutor_user;
GRANT ALL PRIVILEGES ON DATABASE ai_tutor_db TO tutor_user;
\q
EOF
    
    print_success "Database and user created successfully"
}

# Setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    # Check if Python 3.8+ is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    source venv/bin/activate
    
    # Initialize Alembic if not already done
    if [ ! -f "alembic.ini" ]; then
        alembic init alembic
    fi
    
    # Run migrations
    alembic upgrade head
    
    print_success "Database migrations completed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data
    mkdir -p models/huggingface_cache
    mkdir -p logs
    
    print_success "Directories created"
}

# Download AI models
download_models() {
    print_status "Downloading AI models (this may take a while)..."
    
    source venv/bin/activate
    
    python3 << EOF
import os
from transformers import AutoTokenizer, AutoModel, pipeline
import torch

# Set cache directory
cache_dir = "./models/huggingface_cache"
os.makedirs(cache_dir, exist_ok=True)

print("Downloading DialoGPT model...")
try:
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium", cache_dir=cache_dir)
    model = AutoModel.from_pretrained("microsoft/DialoGPT-medium", cache_dir=cache_dir)
    print("✓ DialoGPT model downloaded")
except Exception as e:
    print(f"⚠ Error downloading DialoGPT: {e}")

print("Downloading sentence transformer model...")
try:
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=cache_dir)
    print("✓ Sentence transformer model downloaded")
except Exception as e:
    print(f"⚠ Error downloading sentence transformer: {e}")

print("Downloading text generation pipeline...")
try:
    generator = pipeline('text-generation', model='gpt2', cache_dir=cache_dir)
    print("✓ GPT-2 model downloaded")
except Exception as e:
    print(f"⚠ Error downloading GPT-2: {e}")

print("Model download completed!")
EOF
    
    print_success "AI models downloaded"
}

# Main execution
main() {
    print_status "Starting AI-Powered Personal Tutor setup..."
    
    # Check and install PostgreSQL
    if ! check_postgresql; then
        install_postgresql
    fi
    
    # Start PostgreSQL service
    start_postgresql
    
    # Wait for PostgreSQL to be ready
    print_status "Waiting for PostgreSQL to be ready..."
    sleep 5
    
    # Setup database
    setup_database
    
    # Setup Python environment
    setup_python_env
    
    # Create directories
    create_directories
    
    # Run migrations
    run_migrations
    
    # Download AI models
    download_models
    
    print_success "🎉 Setup completed successfully!"
    print_status "You can now start the application with:"
    print_status "  source venv/bin/activate"
    print_status "  uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload"
    print_status ""
    print_status "Database connection details:"
    print_status "  Host: localhost"
    print_status "  Port: 5432"
    print_status "  Database: ai_tutor_db"
    print_status "  User: tutor_user"
    print_status "  Password: tutor_password"
}

# Run main function
main "$@"
