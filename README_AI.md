# 🤖 AI-Powered Personal Tutor

A comprehensive, scalable AI tutoring system built with modern web technologies and local AI models. This system provides personalized learning experiences without requiring external API keys.

## 🌟 Features

### 🧠 AI-Powered Learning
- **Local AI Models**: Uses Hugging Face transformers locally (no API keys required)
- **Intelligent Tutoring**: Context-aware responses adapted to student learning style
- **Automated Quiz Generation**: AI-generated quizzes with multiple question types
- **Personalized Study Plans**: Custom learning paths based on student performance
- **Progress Analytics**: Track learning patterns and provide insights

### 💻 Technical Stack
- **Backend**: FastAPI, SQLAlchemy, Python 3.8+
- **Frontend**: React, TypeScript, Vite, Material-UI
- **AI/ML**: Hugging Face Transformers, PyTorch, Sentence Transformers
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT tokens with secure password hashing

### 🎯 Learning Features
- **Adaptive Difficulty**: Questions adjust based on student performance
- **Multi-Subject Support**: Mathematics, Science, History, English, and more
- **Interactive Chat**: Real-time AI tutor conversations
- **Visual Progress Tracking**: Comprehensive dashboards and analytics
- **Achievement System**: Gamified learning with points and badges

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- Git

### Automated Setup
```bash
# Clone the repository
git clone <repository-url>
cd Learning-Tutor/.github/Tutor

# Run the automated setup script
./setup_ai.sh

# Start the backend server
python3 -m uvicorn app.main:app --reload --port 8001

# In a new terminal, start the frontend
cd frontend
npm install
npm run dev
```

### Manual Setup
```bash
# Backend setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install

# Environment configuration
cp .env.example .env
# Edit .env with your configuration
```

## 🔧 Configuration

### Environment Variables

The system uses a comprehensive `.env` file for configuration:

```properties
# AI Configuration (Local models - no API keys needed)
AI_PROVIDER=huggingface
HUGGINGFACE_MODEL=microsoft/DialoGPT-medium

# Database
DATABASE_URL=sqlite:///./learning_tutor.db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Parameters
MAX_TOKENS=256
TEMPERATURE=0.7
```

### AI Model Configuration

The system supports multiple AI providers:

1. **Hugging Face (Default)**: Local models, no API key required
   - Models: DialoGPT, DistilGPT-2, GPT-2
   - Automatic model download on first use
   
2. **OpenAI (Optional)**: Requires API key
   - Models: GPT-3.5-turbo, GPT-4
   
3. **Google Gemini (Optional)**: Requires API key
   - Models: Gemini-1.5-flash

## 🎓 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Token refresh

### AI Tutoring
- `POST /api/v1/demo/ai-tutor/chat` - Interactive AI chat
- `GET /api/v1/demo/ai-tutor/suggestions` - Learning suggestions

### Quiz Generation
- `POST /api/v1/demo/quiz/generate` - Generate AI quizzes
- `POST /api/v1/demo/quiz/adaptive` - Adaptive quiz based on performance

### Learning Analytics
- `GET /api/v1/demo/dashboard` - Student dashboard data
- `GET /api/v1/demo/progress/overview` - Progress analytics
- `POST /api/v1/demo/study-plan/generate` - Personalized study plans

### System Status
- `GET /health` - System health check
- `GET /api/v1/demo/ai-models/status` - AI model status

## 🧠 AI Capabilities

### 1. Intelligent Tutoring
```python
# Example API call
{
  "message": "Explain quadratic equations",
  "student_id": 1,
  "context": {
    "subject": "mathematics",
    "topic": "algebra"
  }
}
```

### 2. Quiz Generation
```python
# Generate custom quiz
{
  "subject": "Mathematics",
  "topic": "Algebra", 
  "difficulty_level": "intermediate",
  "num_questions": 5,
  "question_types": ["multiple_choice", "true_false"]
}
```

### 3. Study Plans
```python
# Generate study plan
{
  "student_id": 1,
  "subject": "Physics",
  "goals": ["Understand mechanics", "Solve problems"],
  "timeframe_days": 30
}
```

## 📊 Learning Analytics

### Student Progress Tracking
- Session completion rates
- Accuracy trends over time
- Subject mastery levels
- Learning velocity metrics

### Adaptive Learning
- Difficulty adjustment based on performance
- Personalized content recommendations
- Weak area identification and reinforcement
- Learning style adaptation

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **CORS Protection**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic models for request/response validation

## 🏗️ Architecture

### Backend Architecture
```
app/
├── api/v1/endpoints/     # API route handlers
├── core/                 # Core configuration and database
├── models/              # SQLAlchemy database models
├── services/            # Business logic and AI services
├── schemas/             # Pydantic schemas
└── main.py             # FastAPI application entry point
```

### Frontend Architecture
```
frontend/src/
├── components/          # React components
├── contexts/           # React contexts (auth, etc.)
├── services/           # API service calls
├── pages/              # Page components
└── utils/              # Utility functions
```

### AI Services Architecture
```
services/
├── ai_models.py         # Core AI model management
├── enhanced_ai_tutor.py # Advanced tutoring service
├── ai_quiz_generator.py # Quiz generation service
└── recommendation_engine.py # Learning recommendations
```

## 🧪 Development

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
cd frontend
npm test
```

### Development Mode
```bash
# Backend with hot reload
uvicorn app.main:app --reload --port 8001

# Frontend with hot reload
cd frontend
npm run dev
```

### Code Quality
```bash
# Python code formatting
black app/
flake8 app/

# TypeScript/JavaScript formatting
cd frontend
npm run lint
npm run format
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

### Manual Deployment
1. Configure environment variables for production
2. Set up PostgreSQL database
3. Configure reverse proxy (nginx/apache)
4. Set up SSL certificates
5. Configure monitoring and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for new frontend code
- Write comprehensive tests
- Document new features
- Follow semantic versioning

## 📚 Learning Subjects Supported

- **Mathematics**: Algebra, Geometry, Calculus, Statistics
- **Science**: Physics, Chemistry, Biology
- **Computer Science**: Programming, Algorithms, Data Structures
- **History**: World History, Specific Periods and Events
- **English**: Grammar, Literature, Writing
- **Languages**: Vocabulary, Grammar, Conversation

## 🎮 Gamification Features

- **Points System**: Earn points for completing activities
- **Achievement Badges**: Unlock badges for milestones
- **Learning Streaks**: Maintain daily learning consistency
- **Leaderboards**: Compare progress with other learners
- **Challenges**: Weekly and monthly learning challenges

## 🔧 Troubleshooting

### Common Issues

1. **AI Models Not Loading**
   - Check internet connection for initial model download
   - Verify disk space (models require 1-5GB)
   - Check HuggingFace cache permissions

2. **Database Connection Errors**
   - Verify DATABASE_URL in .env file
   - Check database server status
   - Run database migrations: `alembic upgrade head`

3. **Frontend Not Loading**
   - Check if backend is running on port 8001
   - Verify VITE_API_BASE_URL in frontend/.env
   - Clear browser cache and reload

### Performance Optimization

1. **AI Model Performance**
   - Use GPU acceleration if available
   - Configure model caching appropriately
   - Consider smaller models for faster responses

2. **Database Performance**
   - Add database indexes for frequently queried fields
   - Use connection pooling for high traffic
   - Regular database maintenance

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Hugging Face for providing excellent transformer models
- FastAPI team for the outstanding web framework
- React and Material-UI teams for frontend technologies
- Open source community for various supporting libraries

## 📞 Support

- 📧 Email: support@ai-tutor.example.com
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📖 Documentation: Wiki

---

Built with ❤️ for personalized learning and education accessibility.
