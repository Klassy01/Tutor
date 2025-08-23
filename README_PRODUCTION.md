# 🎓 AI-Powered Learning Tutor Platform

A comprehensive, production-ready learning platform powered by advanced AI models including **Llama 3** and **Mistral 7B** for intelligent lesson generation, quiz creation, and personalized tutoring.

## 🌟 Key Features

### 🤖 Advanced AI Integration
- **Llama 3 & Mistral 7B**: Powered by cutting-edge language models via Hugging Face
- **Intelligent Lesson Generation**: AI creates comprehensive lessons on any topic
- **Dynamic Quiz Creation**: Contextual quizzes with detailed explanations
- **Personal AI Tutor**: Interactive chat sessions with subject expertise
- **Adaptive Learning**: Content adjusts based on user performance and preferences

### 📊 Comprehensive Analytics
- **Real-time Progress Tracking**: Monitor lessons, quizzes, and study time
- **Subject Performance Breakdown**: Detailed analytics per subject and topic
- **Learning Streaks & Achievements**: Gamified experience with badges and points
- **Interactive Dashboards**: Visual charts and progress indicators
- **Personalized Recommendations**: AI-powered content suggestions

### 🎯 Professional User Experience
- **LeetCode-Inspired Design**: Clean, professional interface
- **Responsive Design**: Works seamlessly on all devices
- **Real Authentication System**: Secure user registration and login
- **Professional Typography**: Modern, readable design
- **Dark/Light Theme Support**: Customizable visual experience

## 🏗️ Technical Architecture

### Backend (FastAPI + PostgreSQL)
```
backend/
├── api/v1/endpoints/          # API endpoints
│   ├── auth.py               # Authentication
│   ├── lessons.py            # Lesson management
│   ├── quizzes.py            # Quiz system
│   ├── ai_tutor.py           # AI chat interface
│   └── dashboard.py          # Analytics dashboard
├── services/                  # Business logic
│   ├── advanced_ai_generator.py  # Llama 3/Mistral AI
│   ├── progress_service.py       # Progress tracking
│   └── huggingface_content_generator.py  # Content AI
├── models/                    # Database models
│   ├── user.py               # User management
│   ├── user_analytics.py     # Analytics & progress
│   └── ...
└── core/                     # Configuration
    ├── database.py           # PostgreSQL setup
    ├── config.py             # Settings
    └── security.py           # Authentication
```

### Frontend (React + TypeScript + Material-UI)
```
frontend/src/
├── components/               # Reusable components
├── pages/                   # Application pages
├── services/api.ts          # API integration
├── contexts/               # React contexts
└── assets/                 # Static assets
```

### AI Models & Services
- **Hugging Face Transformers**: Local model execution
- **Hugging Face Inference API**: Cloud-based Llama 3, Mistral 7B
- **Content Generation**: Dynamic lessons and quizzes
- **Chat Interface**: Interactive AI tutoring sessions

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 18+**
- **PostgreSQL 12+**
- **Git**

### 1. Clone Repository
```bash
git clone https://github.com/your-username/Learning-Tutor.git
cd Learning-Tutor
```

### 2. Backend Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your PostgreSQL connection string
```

### 3. Database Setup
```bash
# Initialize database tables
python init_db.py
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 5. Start Backend
```bash
# From project root
python -m backend.main
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/learning_tutor

# Hugging Face (optional - for cloud models)
HUGGINGFACE_API_TOKEN=your_token_here

# JWT Security
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Settings
API_V1_STR=/api/v1
CORS_ORIGINS=["http://localhost:3000"]
```

### PostgreSQL Setup
```sql
-- Create database and user
CREATE DATABASE learning_tutor;
CREATE USER tutor_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE learning_tutor TO tutor_user;
```

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user

### Lesson Management
- `GET /api/v1/lessons/subjects` - Get available subjects
- `GET /api/v1/lessons/topics/{subject}` - Get topics for subject
- `POST /api/v1/lessons/generate` - Generate AI lesson
- `POST /api/v1/lessons/complete` - Mark lesson complete
- `GET /api/v1/lessons/history` - Get lesson history
- `GET /api/v1/lessons/recommendations` - Get personalized recommendations

### Quiz System
- `POST /api/v1/quizzes/generate` - Generate AI quiz
- `POST /api/v1/quizzes/submit` - Submit quiz answers
- `GET /api/v1/quizzes/history` - Get quiz history
- `GET /api/v1/quizzes/statistics` - Get detailed quiz stats
- `POST /api/v1/quizzes/practice-mode` - Generate practice quiz

### AI Tutor Chat
- `POST /api/v1/ai-tutor/start-session` - Start chat session
- `POST /api/v1/ai-tutor/send-message` - Send message to AI
- `GET /api/v1/ai-tutor/sessions` - Get chat sessions
- `POST /api/v1/ai-tutor/ask-quick` - Quick question without session
- `POST /api/v1/ai-tutor/explain-concept` - Get concept explanation

### Analytics Dashboard
- `GET /api/v1/dashboard/overview` - Complete dashboard data
- `GET /api/v1/dashboard/progress-chart` - Progress visualization
- `GET /api/v1/dashboard/subject-breakdown` - Subject performance
- `GET /api/v1/dashboard/achievements` - User achievements
- `GET /api/v1/dashboard/learning-streaks` - Streak information

## 🤖 AI Model Configuration

### Supported Models
1. **Llama 3** (via Hugging Face Inference API)
2. **Mistral 7B** (via Hugging Face Inference API)
3. **DialoGPT-Large** (local/cloud)
4. **GPT2** (fallback)

### Model Fallback Chain
```
Llama 3 → Mistral 7B → DialoGPT-Large → GPT2 → Rule-based
```

### Hugging Face Setup
```bash
# Install Hugging Face CLI
pip install huggingface_hub

# Login (optional for private models)
huggingface-cli login
```

## 📊 Database Schema

### Core Tables
- **users**: User accounts and authentication
- **user_progress**: Overall learning progress
- **lesson_completions**: Individual lesson records
- **quiz_attempt_records**: Quiz performance data
- **study_sessions**: Learning session tracking
- **achievements**: User achievements and badges
- **learning_goals**: Personal learning objectives

### Analytics Features
- Real-time progress calculation
- Subject-wise performance tracking
- Learning streak computation
- Achievement system
- Personalized recommendations

## 🎯 Production Features

### Security
- JWT-based authentication
- Password hashing with bcrypt
- CORS protection
- SQL injection prevention
- Input validation and sanitization

### Performance
- Database connection pooling
- Async request handling
- Caching for AI responses
- Optimized database queries
- Frontend code splitting

### Monitoring
- Structured logging
- Error tracking
- Performance metrics
- User activity analytics

## 🚀 Deployment

### Docker Deployment
```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/learning_tutor
    depends_on:
      - db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: learning_tutor
      POSTGRES_USER: tutor_user
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Cloud Deployment (AWS/GCP/Azure)
- Use managed PostgreSQL (RDS, Cloud SQL, Azure DB)
- Deploy backend on container services
- Use CDN for frontend static files
- Configure environment variables securely

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend

# Run specific test file
pytest tests/test_ai_generator.py
```

### Frontend Tests
```bash
cd frontend
npm test
npm run test:coverage
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Add tests for new features
- Update documentation
- Follow semantic versioning

## 📋 Roadmap

### Version 2.0
- [ ] Voice interaction with AI tutor
- [ ] Video lesson generation
- [ ] Advanced learning analytics
- [ ] Multi-language support
- [ ] Mobile app (React Native)

### Version 1.5
- [ ] Collaborative learning features
- [ ] Teacher dashboard
- [ ] Custom course creation
- [ ] Integration with LMS systems

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection string in .env
DATABASE_URL=postgresql://user:password@localhost:5432/learning_tutor
```

#### AI Model Loading Issues
```bash
# Clear Hugging Face cache
rm -rf ~/.cache/huggingface/

# Reinstall transformers
pip uninstall transformers
pip install transformers
```

#### Frontend Build Errors
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/Learning-Tutor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/Learning-Tutor/discussions)
- **Email**: support@learningtutor.ai

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Hugging Face** for providing excellent AI models and infrastructure
- **FastAPI** team for the amazing web framework
- **React** team for the powerful frontend library
- **PostgreSQL** for the robust database system
- **Material-UI** for the beautiful component library

---

**Made with ❤️ for learners everywhere**
