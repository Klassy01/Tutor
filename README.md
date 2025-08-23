# AI-Powered Personal Tutor: Adaptive Learning System

A scalable, adaptive learning system designed to enhance student engagement through personalized AI tutoring, real-time progress tracking, and intelligent content recommendations.

## 🎯 Features

### Core Learning Features
- **Adaptive AI Tutoring**: Personalized tutoring sessions powered by Google Gemini Flash or OpenAI GPT models
- **Real-time Chat Interface**: WebSocket-based instant messaging with AI tutor
- **Smart Content Recommendations**: ML-driven content suggestions based on learning patterns
- **Comprehensive Progress Tracking**: Detailed mastery metrics and learning analytics
- **Gamified Learning Experience**: Points, streaks, achievements, and progress visualization

### Advanced Capabilities
- **Knowledge Gap Analysis**: Intelligent identification of learning gaps and prerequisites
- **Adaptive Exercise Generation**: Dynamic difficulty adjustment based on student performance
- **Learning Path Optimization**: Personalized learning sequences using adaptive algorithms
- **Engagement Analytics**: Deep insights into student motivation and focus patterns
- **Multi-modal Content Support**: Support for various content types and learning objectives

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: High-performance async Python web framework
- **SQLAlchemy + Alembic**: ORM and database migrations
- **PostgreSQL/SQLite**: Production and development databases
- **Redis**: Caching and session management
- **WebSocket**: Real-time communication

### AI/ML Stack
- **Google Gemini / OpenAI API**: Gemini Flash or GPT models for conversational AI tutoring
- **scikit-learn**: Machine learning algorithms for adaptive learning
- **transformers**: Hugging Face models for NLP tasks
- **PyTorch**: Deep learning framework for custom models
- **NumPy/Pandas**: Data processing and analysis

### Security & Performance
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **Rate Limiting**: API rate limiting and abuse prevention
- **CORS**: Cross-origin resource sharing configuration
- **Input Validation**: Pydantic models for request/response validation

## 📁 Project Structure

```
Learning-Tutor/
├── app/                          # Backend application
│   ├── api/                      # API layer
│   │   ├── v1/
│   │   │   ├── endpoints/        # API endpoints
│   │   │   │   ├── auth.py       # Authentication endpoints
│   │   │   │   ├── students.py   # Student management
│   │   │   │   ├── content.py    # Content management
│   │   │   │   ├── learning.py   # Learning sessions
│   │   │   │   ├── progress.py   # Progress tracking
│   │   │   │   └── ai_tutor.py   # AI tutor interactions
│   │   │   └── api.py            # API router configuration
│   │   └── dependencies.py       # API dependencies
│   ├── core/                     # Core functionality
│   │   ├── config.py            # Application configuration
│   │   ├── database.py          # Database setup
│   │   └── security.py          # Security utilities
│   ├── models/                   # Database models
│   │   ├── user.py              # User and authentication
│   │   ├── student.py           # Student profiles
│   │   ├── content.py           # Learning content
│   │   ├── learning_session.py  # Learning sessions
│   │   └── progress.py          # Progress tracking
│   ├── services/                 # Business logic services
│   │   ├── ai_tutor_service.py  # AI tutoring logic
│   │   ├── adaptive_learning.py # Adaptive algorithms
│   │   └── websocket_manager.py # WebSocket management
│   └── main.py                  # Application entry point
├── frontend/                     # React frontend application
│   ├── public/                  # Static assets
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── auth/            # Authentication components
│   │   │   ├── dashboard/       # Dashboard components
│   │   │   ├── learning/        # Learning session components
│   │   │   ├── progress/        # Progress tracking components
│   │   │   ├── ai-tutor/        # AI tutor chat components
│   │   │   ├── layout/          # Layout components
│   │   │   └── common/          # Shared components
│   │   ├── contexts/            # React contexts
│   │   ├── services/            # API services
│   │   └── App.tsx              # Main App component
│   ├── package.json             # Frontend dependencies
│   └── .env                     # Frontend environment variables
├── requirements.txt             # Python dependencies
├── package.json                 # Development scripts
├── run-dev.sh                   # Backend startup script
├── setup.sh                     # Automated setup script
├── .env.example                 # Environment template
├── .github/
│   └── copilot-instructions.md  # GitHub Copilot guidance
└── README.md                    # Project documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+ (for frontend and development scripts)
- PostgreSQL (for production) or SQLite (for development)
- Gemini API key (recommended) or OpenAI API key

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Learning-Tutor
   ```

2. **Set up Python environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your settings (minimum required):
   DATABASE_URL=sqlite:///./learning_tutor.db
   SECRET_KEY=your-secret-key-here
   
   # Choose your AI provider and configure accordingly:
   AI_PROVIDER=gemini  # or "openai"
   
   # For Gemini (recommended):
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=gemini-1.5-flash
   
   # For OpenAI (alternative):
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-3.5-turbo
   ```
   
   **Getting API Keys:**
   - **Gemini API**: Get your free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)
   - **OpenAI API**: Get your API key at [OpenAI Platform](https://platform.openai.com/api-keys)

4. **Test your AI configuration (optional but recommended)**
   ```bash
   # Test Gemini integration
   python test_gemini.py
   
   # If using OpenAI, you can test manually through the web interface
   ```

5. **Start the backend server**
   ```bash
   npm run dev
   # Or directly: source venv/bin/activate && uvicorn app.main:app --reload
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

3. **Configure frontend environment**
   ```bash
   # Create .env file (already configured)
   # REACT_APP_API_URL=http://localhost:8000/api/v1
   ```

4. **Start the frontend development server**
   ```bash
   npm start
   # Automatically opens http://localhost:3001 (or next available port)
   ```

### Full-Stack Development

To run both backend and frontend simultaneously:
```bash
# Terminal 1 - Backend
npm run dev

# Terminal 2 - Frontend
cd frontend && npm start
```

### Access the Application
- **Backend API**: http://localhost:8000
  - API Documentation: http://localhost:8000/docs
  - Health Check: http://localhost:8000/health
- **Frontend**: http://localhost:3001 (or displayed port)
- **WebSocket**: ws://localhost:8000/ws

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Get current user

### Student Management
- `GET /api/v1/students/profile` - Get student profile
- `PUT /api/v1/students/profile` - Update profile
- `GET /api/v1/students/dashboard` - Learning dashboard
- `GET /api/v1/students/achievements` - View achievements

### Content Management
- `GET /api/v1/content/categories` - Browse content categories
- `GET /api/v1/content/search` - Search content
- `GET /api/v1/content/recommendations` - Get recommendations
- `POST /api/v1/content/{id}/complete` - Mark content complete

### Learning Sessions
- `POST /api/v1/learning/sessions` - Start learning session
- `GET /api/v1/learning/sessions/{id}` - Get session details
- `POST /api/v1/learning/sessions/{id}/interactions` - Log interaction
- `POST /api/v1/learning/sessions/{id}/complete` - Complete session

### Progress Tracking
- `GET /api/v1/progress/overview` - Progress overview
- `GET /api/v1/progress/detailed` - Detailed progress
- `GET /api/v1/progress/mastery-map` - Visual mastery map
- `GET /api/v1/progress/analytics` - Progress analytics

### AI Tutor
- `POST /api/v1/ai-tutor/chat` - Chat with AI tutor
- `POST /api/v1/ai-tutor/exercises` - Generate adaptive exercises
- `POST /api/v1/ai-tutor/submit-answer` - Submit exercise answer
- `WebSocket /ws` - Real-time tutoring session

## 🧠 AI & Machine Learning Features

### Adaptive Learning Engine
The system uses advanced ML algorithms to:
- **Personalize Learning Paths**: Analyzes student performance to recommend optimal learning sequences
- **Adjust Difficulty**: Dynamically modifies content difficulty based on mastery levels
- **Identify Knowledge Gaps**: Detects prerequisite skills that need reinforcement
- **Predict Learning Outcomes**: Forecasts student success probability for different content

### AI Tutor Capabilities
- **Natural Language Processing**: Understands student questions in natural language
- **Contextual Responses**: Provides relevant explanations based on current learning context
- **Socratic Method**: Guides students to discover answers through strategic questioning
- **Multi-modal Explanations**: Supports text, diagrams, and step-by-step problem solving

### Analytics & Insights
- **Learning Pattern Recognition**: Identifies optimal study times and preferences
- **Engagement Scoring**: Measures focus, motivation, and learning velocity
- **Performance Prediction**: Early warning system for students at risk
- **Curriculum Optimization**: Data-driven insights for content improvement

## 🛠️ Development

### Available Scripts
```bash
# Development
npm run dev          # Start development server
npm run test         # Run tests
npm run lint         # Lint code
npm run format       # Format code

# Database
npm run db:upgrade   # Run migrations
npm run db:downgrade # Rollback migration
npm run db:reset     # Reset database
npm run db:seed      # Seed with sample data

# Production
npm start           # Start production server
npm run build       # Build for production
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
| `SECRET_KEY` | JWT secret key | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` |
| `DEBUG` | Enable debug mode | `False` |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` |

### Advanced Configuration
- **Rate Limiting**: Configure in `app/core/config.py`
- **WebSocket Settings**: Modify `app/services/websocket_manager.py`
- **AI Model Settings**: Adjust in `app/services/ai_tutor_service.py`
- **Learning Algorithms**: Customize in `app/services/adaptive_learning.py`

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

### Phase 1 (Current)
- ✅ Core backend API
- ✅ AI tutoring system
- ✅ Progress tracking
- ✅ Adaptive learning engine

### Phase 2 (Next)
- 🔄 Frontend React application
- 🔄 Mobile app development
- 🔄 Advanced analytics dashboard
- 🔄 Collaborative learning features

### Phase 3 (Future)
- 📋 Multi-language support
- 📋 Advanced AI models
- 📋 Integration with LMS platforms
- 📋 Offline learning capabilities

---

**Built with ❤️ for learners everywhere**
