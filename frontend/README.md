# AI-Powered Personal Tutor - Frontend

React-based frontend for the AI-Powered Personal Tutor system, built with TypeScript, Vite, and Material-UI for a modern, responsive learning experience.

## 🎯 Features

### Core Learning Interface
- **Interactive Learning Sessions**: Dynamic lesson delivery with AI-generated content
- **Quiz System**: Interactive quizzes with multiple question types and instant feedback
- **AI Tutor Chat**: Real-time chat interface with AI tutor for immediate help
- **Progress Dashboard**: Comprehensive progress tracking and analytics
- **Demo Mode**: Instant access without registration for testing

### User Experience
- **Responsive Design**: Mobile-first design with Material-UI components
- **Dark/Light Theme**: Adaptive theming for user preference
- **Real-time Updates**: Live progress tracking and session updates
- **Accessibility**: WCAG-compliant interface design
- **Performance**: Optimized with Vite for fast development and builds

## 🏗️ Architecture

### Tech Stack
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe development with full type coverage
- **Vite**: Fast build tool and development server
- **Material-UI (MUI)**: Comprehensive component library
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **React Context**: State management for authentication

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- npm or yarn
- Backend server running (see backend README)

### Installation

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   # .env file is already configured with:
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

4. **Access the application**
   - Open http://localhost:5173 in your browser
   - Click "Try Demo" for instant access
   - Or register/login to create an account

## 🎮 Demo Mode

### Quick Demo Access
1. **Start the application** (follow Quick Start above)
2. **Click "Try Demo"** on the login page
3. **Explore features**:
   - Create AI-generated lessons
   - Take interactive quizzes
   - Chat with the AI tutor
   - View progress dashboard

### Demo Features
- **No registration required** - Instant access with demo credentials
- **Full functionality** - All features available in demo mode
- **Sample data** - Pre-populated with example content
- **Reset capability** - Fresh start for each demo session

## 🧩 Key Components

### LearningSession.tsx
The main learning interface component featuring:
- **Lesson Generation**: Create AI-generated lessons on any topic
- **Interactive Quizzes**: Take quizzes with multiple question types
- **Progress Tracking**: Real-time progress updates
- **Content Display**: Rich text rendering with formatting
- **Navigation**: Seamless flow between lessons and quizzes

### QuizDisplay.tsx
Dedicated quiz interface with:
- **Multiple Question Types**: Multiple choice, true/false, short answer
- **Timer Support**: Optional time limits for questions
- **Progress Indicators**: Visual progress through quiz
- **Answer Validation**: Real-time answer checking
- **Navigation Controls**: Previous/next question navigation

### QuizResults.tsx
Quiz results display featuring:
- **Score Calculation**: Automatic scoring and percentage
- **Answer Review**: Detailed review of all answers
- **Performance Analysis**: Correct/incorrect answer breakdown
- **Retake Options**: Option to retake quiz
- **Progress Integration**: Results saved to user progress

## 🔧 Development

### Available Scripts
```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Lint code with ESLint
npm run type-check   # TypeScript type checking
```

### Building for Production
```bash
# Build optimized production bundle
npm run build

# Preview production build locally
npm run preview
```

## 🚀 Deployment

### Production Build
```bash
# Build for production
npm run build

# The build output will be in the 'dist' directory
```

### Environment Configuration
```bash
# Production environment variables
VITE_API_BASE_URL=https://your-api-domain.com/api/v1
```

### Deployment Options
- **Static Hosting**: Deploy to Vercel, Netlify, or GitHub Pages
- **CDN**: Use CloudFront or similar for global distribution
- **Docker**: Containerize for container orchestration
- **Traditional Hosting**: Deploy to any web server

## 📱 Responsive Design

### Breakpoints
- **Mobile**: < 600px
- **Tablet**: 600px - 960px
- **Desktop**: > 960px

### Mobile Features
- **Touch-Friendly**: Optimized for touch interactions
- **Responsive Navigation**: Mobile-optimized navigation
- **Adaptive Layout**: Layout adapts to screen size
- **Performance**: Optimized for mobile performance

## 🤝 Contributing

### Development Guidelines
- Follow React best practices
- Use TypeScript for all new code
- Write comprehensive tests
- Follow Material-UI design patterns
- Ensure accessibility compliance

### Code Style
- Use functional components with hooks
- Implement proper error boundaries
- Use TypeScript interfaces for props
- Follow ESLint configuration
- Write meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with React, TypeScript, and Material-UI for modern educational technology.**