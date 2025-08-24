# 🚀 AI-Powered Learning Platform

A production-ready, AI-driven personalized tutoring system built with **FastAPI**, **React**, **PostgreSQL**, and **local Ollama models**.

## ✨ Features

### 🎯 **Core Capabilities**
- **🤖 AI-Powered Content** - Generate lessons and quizzes using local Llama 3, Mistral, and Qwen models
- **👤 Real Authentication** - JWT-based user accounts with secure password hashing
- **📊 Analytics Dashboard** - Track learning progress with PostgreSQL analytics  
- **💬 Interactive AI Tutor** - Real-time chat with educational AI assistant
- **🎨 Modern UI** - Responsive React interface with Material-UI components
- **🔒 Privacy First** - All AI processing happens locally (no external APIs)

### 🛠️ **Technical Stack**
- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Alembic migrations
- **Frontend**: React 18, TypeScript, Material-UI, Axios
- **AI Models**: Ollama (Llama 3 8B, Mistral 7B, Qwen 3 8B)
- **Database**: PostgreSQL with comprehensive analytics
- **Authentication**: JWT tokens with bcrypt password hashing

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL
- [Ollama](https://ollama.ai/) with models: `llama3:8b`, `mistral:7b`, `qwen:8b`

### 1. **Backend Setup**
```bash
# Clone and setup
git clone <repository>
cd Learning-Tutor

# Install dependencies
pip install -r requirements.txt

# Setup database
./setup_postgres.sh
python init_db.py

# Start backend
python3 -m backend.main
```

### 2. **Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

### 3. **Access Application**
- **Frontend**: http://localhost:3001
- **API Documentation**: http://localhost:8000/docs
- **Database**: PostgreSQL on localhost:5432

## 🎮 Usage Guide

### **1. Create Account**
- Register with email/password
- Automatic student profile creation
- JWT token authentication

### **2. Interactive Learning**
- **📚 AI Lessons** - Generate comprehensive lessons on any topic
- **🧠 AI Quizzes** - Create personalized quizzes with explanations
- **💬 AI Tutor** - Ask questions and get instant help
- **📈 Progress Tracking** - Monitor learning analytics

### **3. Dashboard Analytics**
- Session completion rates
- Accuracy trends over time  
- Subject area breakdowns
- Learning time statistics

## 🏗️ Architecture

### **Backend Services**
```python
# AI Content Generation
advanced_ai_generator.py  # Lesson & quiz generation
local_ai_models.py        # Ollama integration  
ai_tutor_service.py       # Interactive tutoring

# Data & Analytics  
progress_service.py       # Learning analytics
recommendation_engine.py  # Content suggestions
websocket_manager.py      # Real-time features
```

### **API Endpoints**
```
/api/v1/auth/*           # Authentication  
/api/v1/lessons/*        # AI lesson generation
/api/v1/quizzes/*        # AI quiz generation
/api/v1/ai-tutor/*       # Interactive AI chat
/api/v1/dashboard/*      # Analytics dashboard
/api/v1/learning/*       # Session management
```

### **Database Schema**
- **Users & Authentication** - Secure user accounts
- **Students & Profiles** - Learning preferences & history
- **Content & Sessions** - Generated lessons and quizzes  
- **Progress & Analytics** - Comprehensive learning metrics

## 🤖 AI Models

All AI processing uses **local Ollama models** for complete privacy:

- **🦙 Llama 3 8B** - Primary content generation, comprehensive lessons
- **🔥 Mistral 7B** - Quiz generation, focused Q&A format
- **⚡ Qwen 3 8B** - Technical content, coding examples

**Benefits:**
- ✅ **100% Private** - No data sent to external services
- ✅ **Always Available** - No API rate limits or downtime  
- ✅ **Cost Effective** - No per-request charges
- ✅ **Customizable** - Full control over AI behavior

## 📁 Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed architecture overview.

## 🔧 Development

### **Backend Development**
```bash
# Run with auto-reload
python3 -m backend.main

# Database migrations  
alembic upgrade head
alembic revision --autogenerate -m "Description"

# Run tests
pytest backend/tests/
```

### **Frontend Development**
```bash
cd frontend
npm run dev      # Development server
npm run build    # Production build  
npm run test     # Run tests
```

### **AI Model Management**
```bash
# Install Ollama models
ollama pull llama3:8b
ollama pull mistral:7b  
ollama pull qwen:8b

# Test models
ollama run llama3:8b "Hello"
```

## 📊 Production Deployment

### **Docker Support** (Coming Soon)
```bash
docker-compose up -d
```

### **Manual Deployment**
- Use `gunicorn` for production WSGI server
- Configure PostgreSQL with connection pooling
- Set up reverse proxy (nginx) for static files
- Enable HTTPS with SSL certificates

## 📝 License

MIT License - see LICENSE file for details.

---

**🎯 Built for Education** | **🔒 Privacy First** | **🚀 Production Ready**
