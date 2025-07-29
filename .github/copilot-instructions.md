<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# AI Personal Tutor Development Guidelines

This is an AI-Powered Personal Tutor project built with Python FastAPI backend and modern ML/AI technologies.

## Project Architecture
- **Backend**: FastAPI with async/await patterns
- **Database**: SQLAlchemy ORM with migration support
- **AI/ML**: OpenAI API integration, scikit-learn for analytics
- **Authentication**: JWT-based auth with secure password hashing
- **WebSocket**: Real-time chat communication

## Code Style Guidelines
- Use async/await for all database operations and external API calls
- Follow RESTful API design principles
- Implement proper error handling with custom exceptions
- Use Pydantic models for request/response validation
- Follow the repository pattern for database operations
- Write comprehensive docstrings for all functions and classes
- Use type hints throughout the codebase

## AI/ML Best Practices
- Implement adaptive learning algorithms that adjust to student performance
- Use proper prompt engineering for AI tutor interactions
- Implement caching for AI responses to improve performance
- Track and analyze student engagement metrics
- Use progressive difficulty adjustment based on student progress

## Security Considerations
- Always validate and sanitize user inputs
- Implement proper authentication and authorization
- Use environment variables for sensitive configuration
- Follow OWASP security guidelines for web applications
