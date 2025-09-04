# AI-Powered Personal Tutor: Adaptive Learning System

A comprehensive, adaptive learning platform that provides personalized AI tutoring, real-time progress tracking, and intelligent content generation. Built with FastAPI backend and React frontend, featuring both OpenAI and local AI model support.

## 🎯 Features

### Core Learning Features
- **Adaptive AI Tutoring**: Personalized tutoring sessions powered by OpenAI GPT models or local Ollama models
- **Real-time Chat Interface**: WebSocket-based instant messaging with AI tutor
- **Dynamic Content Generation**: AI-generated lessons, quizzes, and explanations
- **Comprehensive Progress Tracking**: Detailed mastery metrics and learning analytics
- **Interactive Learning Sessions**: Engaging lesson delivery with quiz integration

### Advanced Capabilities
- **Multi-AI Provider Support**: OpenAI API integration with local Ollama model fallback
- **Adaptive Exercise Generation**: Dynamic quiz creation with multiple question types
- **Learning Path Optimization**: Personalized learning sequences based on performance
- **Real-time Progress Analytics**: Live tracking of learning metrics and achievements
- **Responsive Web Interface**: Modern React-based UI with Material-UI components

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: High-performance async Python web framework
- **SQLAlchemy + Alembic**: ORM and database migrations
- **SQLite**: Development database (PostgreSQL ready for production)
- **WebSocket**: Real-time communication
- **JWT Authentication**: Secure token-based authentication

### AI/ML Stack
- **OpenAI API**: GPT models for conversational AI tutoring and content generation
- **Ollama**: Local AI models (Llama 3, Mistral, Qwen) for privacy-first learning
- **scikit-learn**: Machine learning algorithms for adaptive learning
- **NumPy/Pandas**: Data processing and analysis

### Security & Performance
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Rate Limiting**: API rate limiting and abuse prevention
- **CORS**: Cross-origin resource sharing configuration
- **Input Validation**: Pydantic models for request/response validation

## 📁 Project Structure

```
Tutor/
├── backend/                      # FastAPI backend application
│   ├── api/                     # API layer
│   │   ├── v1/
│   │   │   ├── endpoints/       # API endpoints
│   │   │   │   ├── auth.py      # Authentication endpoints
│   │   │   │   ├── students.py  # Student management
│   │   │   │   ├── content.py   # Content management
│   │   │   │   ├── learning.py  # Learning sessions
│   │   │   │   ├── lessons.py   # Lesson generation
│   │   │   │   ├── quizzes.py   # Quiz generation
│   │   │   │   ├── progress.py  # Progress tracking
│   │   │   │   ├── dashboard.py # Dashboard analytics
│   │   │   │   └── ai_tutor.py  # AI tutor interactions
│   │   │   └── api.py           # API router configuration
│   │   └── dependencies.py      # API dependencies
│   ├── core/                    # Core functionality
│   │   ├── config.py           # Application configuration
│   │   ├── database.py         # Database setup
│   │   └── security.py         # Security utilities
│   ├── models/                  # Database models
│   │   ├── user.py             # User and authentication
│   │   ├── student.py          # Student profiles
│   │   ├── content.py          # Learning content
│   │   ├── learning_session.py # Learning sessions
│   │   ├── quiz_attempt.py     # Quiz attempts
│   │   ├── progress.py         # Progress tracking
│   │   └── user_analytics.py   # User analytics
│   ├── services/                # Business logic services
│   │   ├── advanced_ai_generator.py # AI content generation
│   │   ├── openai_service.py   # OpenAI API integration
│   │   ├── ai_models.py        # Local AI models (Ollama)
│   │   ├── adaptive_learning.py # Adaptive algorithms
│   │   ├── progress_service.py # Progress tracking
│   │   ├── recommendation_engine.py # Content recommendations
│   │   └── websocket_manager.py # WebSocket management
│   ├── main.py                 # Application entry point
│   └── requirements.txt        # Backend dependencies
├── frontend/                    # React frontend application
│   ├── public/                 # Static assets
│   ├── src/
│   │   ├── components/         # React components
│   │   │   ├── auth/           # Authentication components
│   │   │   ├── dashboard/      # Dashboard components
│   │   │   ├── learning/       # Learning session components
│   │   │   │   ├── LearningSession.tsx # Main learning interface
│   │   │   │   ├── QuizDisplay.tsx     # Quiz interface
│   │   │   │   └── QuizResults.tsx     # Quiz results
│   │   │   ├── progress/       # Progress tracking components
│   │   │   ├── ai-tutor/       # AI tutor chat components
│   │   │   ├── layout/         # Layout components
│   │   │   ├── profile/        # User profile components
│   │   │   └── common/         # Shared components
│   │   ├── contexts/           # React contexts
│   │   │   └── AuthContext.tsx # Authentication context
│   │   ├── services/           # API services
│   │   │   └── api.ts          # API client
│   │   └── App.tsx             # Main App component
│   ├── package.json            # Frontend dependencies
│   └── .env                    # Frontend environment variables
├── alembic/                    # Database migrations
├── requirements.txt            # Python dependencies
├── alembic.ini                # Alembic configuration
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
└── README.md                  # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- SQLite (included, no setup required)
- OpenAI API key (optional, for enhanced AI features)
- Ollama (optional, for local AI models)

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Tutor
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Initialize the database**
   ```bash
   # Run database migrations
   alembic upgrade head
   ```

4. **Configure environment variables (optional)**
   ```bash
   # For enhanced AI features, set OpenAI API key:
   export OPENAI_API_KEY=your-openai-api-key
   
   # For local AI models, install Ollama:
   # curl -fsSL https://ollama.ai/install.sh | sh
   # ollama pull llama3:8b
   ```

5. **Start the backend server**
   ```bash
   # Activate virtual environment and start server
   source venv/bin/activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Start the frontend development server**
   ```bash
   npm run dev
   # Automatically opens http://localhost:5173 (Vite default)
   ```

### Full-Stack Development

To run both backend and frontend simultaneously:
```bash
# Terminal 1 - Backend
source venv/bin/activate && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Access the Application
- **Backend API**: http://localhost:8000
  - API Documentation: http://localhost:8000/docs
  - Health Check: http://localhost:8000/health
- **Frontend**: http://localhost:5173 (Vite default)
- **WebSocket**: ws://localhost:8000/ws

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/demo/login` - Demo login (for testing)

### Learning & Content
- `POST /api/v1/lessons/generate` - Generate AI lesson content
- `POST /api/v1/quizzes/generate` - Generate AI quiz
- `POST /api/v1/quizzes/submit` - Submit quiz answers
- `POST /api/v1/learning/sessions` - Start learning session
- `GET /api/v1/learning/sessions/{id}` - Get session details

### AI Tutor
- `POST /api/v1/ai-tutor/ask-quick` - Quick AI tutor question
- `POST /api/v1/ai-tutor/chat` - Chat with AI tutor
- `WebSocket /ws` - Real-time tutoring session

### Dashboard & Progress
- `GET /api/v1/dashboard/overview` - Dashboard overview
- `GET /api/v1/progress/overview` - Progress overview
- `GET /api/v1/students/profile` - Student profile

### Health & Monitoring
- `GET /health` - System health check
- `GET /api/v1/docs` - Interactive API documentation

## 🧠 AI & Machine Learning Features

### Multi-Provider AI Support
- **OpenAI Integration**: GPT models for high-quality content generation and tutoring
- **Local AI Models**: Ollama integration with Llama 3, Mistral, and Qwen models
- **Fallback System**: Automatic fallback to local models when API is unavailable
- **Privacy-First Option**: Complete local operation without external API calls

### AI Content Generation
- **Dynamic Lesson Creation**: AI-generated lessons with structured content, examples, and key concepts
- **Adaptive Quiz Generation**: Multiple question types (multiple choice, true/false, short answer)
- **Contextual Explanations**: AI explanations tailored to student's learning level
- **Real-time Chat**: Interactive AI tutor for immediate help and guidance

### Learning Analytics
- **Progress Tracking**: Comprehensive tracking of learning sessions and quiz performance
- **Performance Analytics**: Detailed insights into learning patterns and achievements
- **Adaptive Recommendations**: AI-driven content suggestions based on performance
- **Engagement Metrics**: Tracking of learning engagement and session duration

## 🎮 Demo & Testing

### Quick Demo
1. **Start the application** (follow Quick Start guide above)
2. **Access the frontend** at http://localhost:5173
3. **Click "Try Demo"** to log in with demo credentials
4. **Explore features**:
   - Create AI-generated lessons
   - Take interactive quizzes
   - Chat with the AI tutor
   - View progress dashboard

### Demo Features
- **No registration required** - Use demo login for immediate access
- **Full AI functionality** - Experience all AI features without setup
- **Sample content** - Pre-generated examples to explore
- **Interactive learning** - Complete learning sessions with quizzes

## 🛠️ Development

### Available Scripts
```bash
# Backend Development
source venv/bin/activate && uvicorn backend.main:app --reload  # Start backend
alembic upgrade head                                          # Run migrations
alembic revision --autogenerate -m "Description"             # Create migration

# Frontend Development
cd frontend && npm run dev    # Start frontend dev server
cd frontend && npm run build  # Build for production
cd frontend && npm run lint   # Lint frontend code

# Testing
pytest                        # Run backend tests
pytest --cov=backend         # Run with coverage
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

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

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./learning_tutor.db` |
| `SECRET_KEY` | JWT secret key | `dev-secret-key-change-in-production-12345` |
| `OPENAI_API_KEY` | OpenAI API key | Optional (for enhanced features) |
| `AI_PROVIDER` | AI provider preference | `openai` |
| `DEBUG` | Enable debug mode | `True` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000,http://localhost:5173` |

### Advanced Configuration
- **Rate Limiting**: Configure in `backend/core/config.py`
- **WebSocket Settings**: Modify `backend/services/websocket_manager.py`
- **AI Model Settings**: Adjust in `backend/services/advanced_ai_generator.py`
- **Learning Algorithms**: Customize in `backend/services/adaptive_learning.py`

## 📊 Monitoring & Analytics

### Health Monitoring
- Health check endpoint: `/health`
- Database connectivity check
- External service status
- Performance metrics

### Learning Analytics
- Student engagement metrics
- Content effectiveness analysis
- Learning outcome predictions
- System usage statistics

## 🔒 Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- Secure password hashing
- Token refresh mechanism

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Rate limiting and abuse prevention

### Privacy Compliance
- GDPR-compliant data handling
- Secure data storage
- User consent management
- Data retention policies

## 🚀 Deployment

### Production Deployment
1. **Set up production database**
2. **Configure environment variables**
3. **Install dependencies**
4. **Run database migrations**
5. **Start the application server**

### Docker Deployment
```bash
# Build Docker image
docker build -t learning-tutor .

# Run container
docker run -p 8000:8000 learning-tutor
```

### Cloud Deployment
The application is ready for deployment on:
- **Heroku**: Use the included Procfile
- **AWS**: Deploy with Elastic Beanstalk or ECS
- **Google Cloud**: Use Cloud Run or App Engine
- **Azure**: Deploy with App Service

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Document new features
- Update API documentation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when running
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join community discussions
- **Email**: Contact the development team

## 🔮 Roadmap

### Phase 1 (Completed ✅)
- ✅ Core backend API with FastAPI
- ✅ AI tutoring system with OpenAI & Ollama support
- ✅ Progress tracking and analytics
- ✅ Adaptive learning engine
- ✅ React frontend with Material-UI
- ✅ Interactive learning sessions
- ✅ AI-generated lessons and quizzes
- ✅ Real-time chat with AI tutor
- ✅ Demo mode for easy testing

### Phase 2 (In Progress 🔄)
- 🔄 Enhanced mobile responsiveness
- 🔄 Advanced analytics dashboard
- 🔄 Collaborative learning features
- 🔄 User profile management
- 🔄 Content library expansion

### Phase 3 (Future 📋)
- 📋 Multi-language support
- 📋 Advanced AI models integration
- 📋 Integration with LMS platforms
- 📋 Offline learning capabilities
- 📋 Mobile app development

---

**Built with ❤️ for learners everywhere**
