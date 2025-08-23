#!/bin/bash

# AI Personal Tutor - Quick Setup Script
# This script sets up the development environment for the Learning Tutor system

set -e  # Exit on any error

echo "🎓 AI Personal Tutor - Setup Script"
echo "====================================="
echo

# Color codes for output
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.8+ is required but not found"
        echo "Please install Python 3.8 or higher and try again"
        exit 1
    fi
    
    # Check Node.js (optional but recommended)
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_warning "Node.js not found - some development scripts won't work"
        print_status "You can install Node.js from https://nodejs.org/"
    fi
    
    # Check pip
    if command_exists pip3; then
        print_success "pip3 found"
    else
        print_error "pip3 is required but not found"
        exit 1
    fi
    
    echo
}

# Setup Python virtual environment
setup_venv() {
    print_status "Setting up Python virtual environment..."
    
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
        else
            print_status "Using existing virtual environment"
            return
        fi
    fi
    
    python3 -m venv venv
    print_success "Virtual environment created"
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "pip upgraded"
    
    echo
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Make sure virtual environment is activated
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    pip install -r requirements.txt
    print_success "Python dependencies installed"
    
    # Install development dependencies if they exist
    if [ -f "requirements-dev.txt" ]; then
        pip install -r requirements-dev.txt
        print_success "Development dependencies installed"
    fi
    
    echo
}

# Setup environment configuration
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Created .env file from .env.example"
        else
            # Create basic .env file
            cat > .env << EOF
# Database Configuration
DATABASE_URL=sqlite:///./learning_tutor.db

# Security Configuration
SECRET_KEY=$(openssl rand -hex 32)

# AI Configuration (Required - Get from OpenAI)
OPENAI_API_KEY=your-openai-api-key-here

# Application Configuration
DEBUG=True
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# External Services (Optional)
REDIS_URL=redis://localhost:6379

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-email-password
EOF
            print_success "Created basic .env file"
        fi
        
        print_warning "Please edit .env file and add your OpenAI API key"
        print_status "You can get an API key from: https://platform.openai.com/api-keys"
    else
        print_warning ".env file already exists"
    fi
    
    echo
}

# Install Node.js dependencies (if package.json exists)
setup_nodejs() {
    if [ -f "package.json" ] && command_exists npm; then
        print_status "Installing Node.js dependencies..."
        npm install
        print_success "Node.js dependencies installed"
        echo
    fi
}

# Initialize database
setup_database() {
    print_status "Setting up database..."
    
    # Make sure virtual environment is activated
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # Check if alembic is configured
    if [ -f "alembic.ini" ]; then
        print_status "Running database migrations..."
        alembic upgrade head
        print_success "Database migrations completed"
    else
        print_status "Creating database tables..."
        python -c "
from app.core.database import create_tables
create_tables()
print('Database tables created successfully')
"
        print_success "Database initialized"
    fi
    
    echo
}

# Create sample data (optional)
create_sample_data() {
    read -p "Do you want to create sample data for testing? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Creating sample data..."
        
        # Make sure virtual environment is activated
        if [[ "$VIRTUAL_ENV" == "" ]]; then
            source venv/bin/activate
        fi
        
        python -c "
# Sample data creation script
from app.core.database import SessionLocal, create_tables
from app.models.user import User
from app.models.student import Student, StudentProfile
from app.models.content import ContentCategory, LearningObjective, Content
from app.core.security import get_password_hash
from sqlalchemy.orm import Session

def create_sample_data():
    db = SessionLocal()
    try:
        # Create sample user
        sample_user = User(
            email='demo@example.com',
            username='demo_student',
            hashed_password=get_password_hash('demo123'),
            is_active=True
        )
        db.add(sample_user)
        db.flush()
        
        # Create sample student profile
        sample_student = Student(
            user_id=sample_user.id,
            first_name='Demo',
            last_name='Student',
            date_of_birth=None,
            grade_level='10'
        )
        db.add(sample_student)
        db.flush()
        
        # Create sample content categories
        math_category = ContentCategory(
            name='Mathematics',
            description='Mathematical concepts and problem solving',
            level=0,
            sort_order=1,
            is_active=True
        )
        algebra_category = ContentCategory(
            name='Algebra',
            description='Algebraic equations and expressions',
            level=1,
            parent_id=None,  # Will be set after math_category is saved
            sort_order=1,
            is_active=True
        )
        
        db.add(math_category)
        db.add(algebra_category)
        db.flush()
        
        # Set parent relationship
        algebra_category.parent_id = math_category.id
        
        # Create sample learning objectives
        linear_equations = LearningObjective(
            category_id=algebra_category.id,
            title='Linear Equations',
            description='Solve linear equations in one variable',
            difficulty_level='beginner',
            estimated_time=30,
            prerequisites=[],
            is_active=True
        )
        
        db.add(linear_equations)
        db.commit()
        
        print('Sample data created successfully!')
        print('Demo login: demo@example.com / demo123')
        
    except Exception as e:
        print(f'Error creating sample data: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    create_sample_data()
"
        print_success "Sample data created"
        print_status "Demo login: demo@example.com / demo123"
        echo
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Make sure virtual environment is activated
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        source venv/bin/activate
    fi
    
    # Test import
    python -c "
import app.main
print('✓ Application imports successfully')

from app.core.database import engine
print('✓ Database connection works')

from app.core.config import settings
print('✓ Configuration loaded')
"
    
    print_success "Installation verified successfully!"
    echo
}

# Display next steps
show_next_steps() {
    echo "🎉 Setup Complete!"
    echo "================="
    echo
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo
    echo "2. Edit the .env file and add your OpenAI API key:"
    echo "   nano .env"
    echo
    echo "3. Start the development server:"
    echo "   uvicorn app.main:app --reload"
    echo "   OR: npm run dev (if Node.js is installed)"
    echo
    echo "4. Access the application:"
    echo "   • API Documentation: http://localhost:8000/docs"
    echo "   • Health Check: http://localhost:8000/health"
    echo "   • WebSocket Test: ws://localhost:8000/ws"
    echo
    echo "5. For production deployment:"
    echo "   • Set DEBUG=False in .env"
    echo "   • Use PostgreSQL instead of SQLite"
    echo "   • Configure proper CORS origins"
    echo
    print_success "Happy learning! 🎓"
}

# Main setup process
main() {
    echo "Starting setup process..."
    echo
    
    check_prerequisites
    setup_venv
    install_dependencies
    setup_nodejs
    setup_environment
    setup_database
    create_sample_data
    verify_installation
    show_next_steps
}

# Handle script interruption
trap 'echo -e "\n${RED}Setup interrupted${NC}"; exit 1' INT

# Run main setup
main "$@"
