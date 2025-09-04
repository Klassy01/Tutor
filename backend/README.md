# AI-Powered Personal Tutor - Backend

FastAPI-based backend for the AI-Powered Personal Tutor system, providing RESTful APIs, WebSocket support, and AI integration for educational content generation.

## 🏗️ Architecture

### Core Components
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **SQLite**: Development database (PostgreSQL ready)
- **JWT**: Authentication and authorization
- **WebSocket**: Real-time communication

### AI Integration
- **OpenAI API**: GPT models for content generation
- **Ollama**: Local AI models (Llama 3, Mistral, Qwen)
- **Fallback System**: Automatic fallback between AI providers

## 📁 Project Structure

```
backend/
├── api/                          # API layer
│   ├── v1/
│   │   ├── endpoints/            # API endpoints
│   │   │   ├── auth.py           # Authentication
│   │   │   ├── students.py       # Student management
│   │   │   ├── content.py        # Content management
│   │   │   ├── learning.py       # Learning sessions
│   │   │   ├── lessons.py        # Lesson generation
│   │   │   ├── quizzes.py        # Quiz generation
│   │   │   ├── progress.py       # Progress tracking
│   │   │   ├── dashboard.py      # Dashboard analytics
│   │   │   └── ai_tutor.py       # AI tutor interactions
│   │   └── api.py                # API router configuration
│   └── dependencies.py           # API dependencies
├── core/                         # Core functionality
│   ├── config.py                 # Application configuration
│   ├── database.py               # Database setup
│   └── security.py               # Security utilities
├── models/                       # Database models
│   ├── user.py                   # User and authentication
│   ├── student.py                # Student profiles
│   ├── content.py                # Learning content
│   ├── learning_session.py       # Learning sessions
│   ├── quiz_attempt.py           # Quiz attempts
│   ├── progress.py               # Progress tracking
│   └── user_analytics.py         # User analytics
├── services/                     # Business logic services
│   ├── advanced_ai_generator.py  # AI content generation
│   ├── openai_service.py         # OpenAI API integration
│   ├── ai_models.py              # Local AI models (Ollama)
│   ├── adaptive_learning.py      # Adaptive algorithms
│   ├── progress_service.py       # Progress tracking
│   ├── recommendation_engine.py  # Content recommendations
│   └── websocket_manager.py      # WebSocket management
├── main.py                       # Application entry point
└── requirements.txt              # Python dependencies
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- OpenAI API key (optional, for enhanced features)
- Ollama (optional, for local AI models)

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database**
   ```bash
   # Run migrations
   alembic upgrade head
   ```

4. **Configure environment (optional)**
   ```bash
   # For OpenAI integration
   export OPENAI_API_KEY=your-openai-api-key
   
   # For local AI models
   # Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh
   # Pull models: ollama pull llama3:8b
   ```

5. **Start the server**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📚 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/demo/login` - Demo login

### Learning & Content
- `POST /api/v1/lessons/generate` - Generate AI lesson
- `POST /api/v1/quizzes/generate` - Generate AI quiz
- `POST /api/v1/quizzes/submit` - Submit quiz answers
- `POST /api/v1/learning/sessions` - Start learning session
- `GET /api/v1/learning/sessions/{id}` - Get session details

### AI Tutor
- `POST /api/v1/ai-tutor/ask-quick` - Quick AI question
- `POST /api/v1/ai-tutor/chat` - Chat with AI tutor
- `WebSocket /ws` - Real-time tutoring

### Dashboard & Progress
- `GET /api/v1/dashboard/overview` - Dashboard overview
- `GET /api/v1/progress/overview` - Progress overview
- `GET /api/v1/students/profile` - Student profile

### System
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

## 🧠 AI Services

### Advanced AI Generator
The `advanced_ai_generator.py` service orchestrates AI content generation:

- **Lesson Generation**: Creates structured lessons with content, examples, and key concepts
- **Quiz Generation**: Generates multiple question types with explanations
- **Chat Responses**: Provides contextual AI tutoring responses
- **Multi-Provider Support**: OpenAI API with Ollama fallback

### OpenAI Service
The `openai_service.py` handles OpenAI API integration:

- **Content Generation**: High-quality content using GPT models
- **Error Handling**: Graceful fallback when API is unavailable
- **Rate Limiting**: Built-in request management

### Local AI Models
The `ai_models.py` manages local Ollama models:

- **Model Management**: Automatic model loading and switching
- **Content Generation**: Local AI content generation
- **Privacy-First**: Complete local operation without external APIs

## 🗄️ Database Models

### Core Models
- **User**: Authentication and user management
- **Student**: Student profiles and preferences
- **LearningSession**: Learning session tracking
- **QuizAttempt**: Quiz performance tracking
- **Progress**: Learning progress analytics
- **UserAnalytics**: Detailed user behavior analytics

### Relationships
- Users have one Student profile
- Students have many LearningSessions
- LearningSessions have many QuizAttempts
- Progress is aggregated from sessions and attempts

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection | `sqlite:///./learning_tutor.db` |
| `SECRET_KEY` | JWT secret key | `dev-secret-key-change-in-production-12345` |
| `OPENAI_API_KEY` | OpenAI API key | Optional |
| `AI_PROVIDER` | AI provider preference | `openai` |
| `DEBUG` | Debug mode | `True` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost:5173` |

### Database Configuration
- **Development**: SQLite (no setup required)
- **Production**: PostgreSQL (configure DATABASE_URL)
- **Migrations**: Alembic for schema management

## 🛠️ Development

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_auth.py
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality
```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

## 🔒 Security

### Authentication
- **JWT Tokens**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password security
- **Token Refresh**: Automatic token renewal
- **Demo Mode**: Safe demo login for testing

### API Security
- **CORS**: Configured cross-origin resource sharing
- **Input Validation**: Pydantic models for request validation
- **Rate Limiting**: Built-in request rate limiting
- **Error Handling**: Secure error responses

## 📊 Monitoring

### Health Checks
- **Database Connectivity**: Automatic database health checks
- **AI Provider Status**: OpenAI and Ollama availability
- **WebSocket Connections**: Active connection monitoring
- **System Metrics**: Performance and usage statistics

### Logging
- **Structured Logging**: JSON-formatted logs
- **Error Tracking**: Comprehensive error logging
- **Performance Metrics**: Request timing and performance
- **AI Usage**: AI provider usage tracking

## 🚀 Deployment

### Production Setup
1. **Set production environment variables**
2. **Configure PostgreSQL database**
3. **Set up reverse proxy (nginx)**
4. **Configure SSL certificates**
5. **Set up monitoring and logging**

### Docker Deployment
```bash
# Build image
docker build -t ai-tutor-backend .

# Run container
docker run -p 8000:8000 ai-tutor-backend
```

### Environment-Specific Configuration
- **Development**: Debug mode, SQLite, local AI models
- **Staging**: Production-like setup with test data
- **Production**: Optimized for performance and security

## 🤝 Contributing

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Document new features
- Update API documentation
- Use type hints throughout

### Code Structure
- **Services**: Business logic and AI integration
- **Models**: Database models and relationships
- **API**: RESTful endpoints and WebSocket handlers
- **Core**: Configuration and utilities

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with FastAPI, SQLAlchemy, and AI integration for modern educational technology.**
