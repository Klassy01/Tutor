"""
AI-Powered Personal Tutor - Main Application Entry Point

A scalable, adaptive learning system that provides personalized tutoring
experiences with AI-powered content delivery and real-time interaction.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from typing import List, Dict
import json
import asyncio
from datetime import datetime

# Try absolute imports first, fall back to relative imports
try:
    from backend.core.config import settings
    from backend.core.database import engine, create_tables
    from backend.api.v1.api import api_router
    from backend.services.websocket_manager import ConnectionManager
    from backend.services.recommendation_engine import recommendation_engine
    from backend.services.ai_models import ai_model_manager
except ImportError:
    # Running from within backend directory - use relative imports
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from backend.core.config import settings
    from backend.core.database import engine, create_tables
    from backend.api.v1.api import api_router
    from backend.services.websocket_manager import ConnectionManager
    from backend.services.recommendation_engine import recommendation_engine
    from backend.services.ai_models import ai_model_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    # Startup
    logger.info("🚀 Starting AI Personal Tutor application...")
    
    try:
        # Initialize database
        logger.info("📊 Initializing database...")
        await create_tables()
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.warning("⚠️  Continuing without database connection for testing...")
        # Don't exit - allow the server to start for frontend testing        # Initialize AI models
        logger.info("🤖 Initializing educational AI models...")
        provider_info = ai_model_manager.get_model_info()
        logger.info(f"Available educational models: {provider_info['available_models']}")
        logger.info(f"Educational focus: {provider_info['educational_focus']}")
        logger.info(f"Supported content types: {provider_info['content_types']}")
        
        # Warm up educational models
        await ai_model_manager.warmup_models()
        
        # Load recommendation engine index if available
        logger.info("🎯 Loading recommendation engine...")
        await recommendation_engine.load_index()
        
        # Start background tasks
        logger.info("⚙️  Starting background tasks...")
        asyncio.create_task(periodic_index_update())
        
        logger.info("🎉 AI Personal Tutor application started successfully!")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AI Personal Tutor application...")


async def periodic_index_update():
    """Periodically update the recommendation index."""
    while True:
        try:
            await asyncio.sleep(3600)  # Update every hour
            logger.info("🔄 Updating recommendation index...")
            # This would fetch latest content from database and rebuild index
            # For now, just log the action
            logger.info("📈 Recommendation index update completed")
        except Exception as e:
            logger.error(f"Error updating recommendation index: {e}")


# Create FastAPI application
app = FastAPI(
    title="AI-Powered Personal Tutor",
    description="""
    ## 🎓 AI-Powered Personal Tutor System
    
    A scalable, adaptive learning system that provides:
    
    * **🤖 Intelligent Tutoring**: AI-powered personalized learning assistance
    * **📚 Adaptive Content**: Dynamic difficulty adjustment and personalized recommendations
    * **💬 Real-time Chat**: WebSocket-based interactive tutoring sessions
    * **📊 Progress Tracking**: Comprehensive learning analytics and progress monitoring
    * **🔐 Secure Authentication**: JWT-based user authentication and authorization
    * **🎯 Smart Recommendations**: Content recommendations using ML embeddings
    * **📱 Multi-platform**: REST API supporting web, mobile, and desktop clients
    
    ### 🔧 AI Models Supported:
    * OpenAI GPT models
    * Google Gemini
    * Hugging Face Transformers (local and API)
    
    ### 🎨 Features:
    * Quiz generation and automated grading
    * Learning session tracking
    * Achievement system
    * Multi-language support
    * Voice interaction (optional)
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "AI Tutor Team",
        "email": "support@ai-tutor.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# WebSocket manager for real-time communication
manager = ConnectionManager()

# Static files (for frontend)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    logger.warning("⚠️  Static files directory not found. Skipping static file mounting.")


@app.get("/")
async def root():
    """Root endpoint with application information."""
    return {
        "message": "🎓 AI-Powered Personal Tutor API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "🤖 Intelligent AI Tutoring",
            "📚 Adaptive Learning Content",
            "💬 Real-time WebSocket Chat",
            "📊 Progress Analytics",
            "🎯 Smart Recommendations",
            "🔐 Secure Authentication"
        ],
        "docs": "/docs",
        "redoc": "/redoc",
        "ai_providers": ai_model_manager.get_provider_info()
    }


@app.get("/health")
async def health_check():
    """Enhanced health check endpoint for monitoring."""
    try:
        # Check database connection
        from backend.core.database import get_db
        next(get_db()).execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check AI providers
    ai_status = ai_model_manager.get_provider_info()
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "ai-personal-tutor",
        "version": "2.0.0",
        "timestamp": "2024-01-01T00:00:00Z",
        "checks": {
            "database": db_status,
            "ai_providers": ai_status,
            "websocket_connections": len(manager.active_connections)
        },
        "uptime": "System running",
        "environment": "development" if settings.DEBUG else "production"
    }


@app.get("/api-info")
async def api_info():
    """Get comprehensive API information."""
    return {
        "api_version": "v1",
        "total_endpoints": len(app.routes),
        "authentication": "JWT Bearer Token",
        "rate_limiting": "Not implemented",
        "supported_formats": ["JSON"],
        "websocket_endpoints": [
            "/ws/tutor/{student_id}",
            "/ws/notifications/{user_id}"
        ],
        "main_endpoints": {
            "authentication": "/api/v1/auth/*",
            "ai_tutor": "/api/v1/ai-tutor/*",
            "content": "/api/v1/content/*",
            "progress": "/api/v1/progress/*",
            "learning": "/api/v1/learning/*"
        }
    }


@app.websocket("/ws/tutor/{student_id}")
async def websocket_tutor_endpoint(websocket: WebSocket, student_id: int):
    """
    WebSocket endpoint for real-time AI tutor chat.
    
    Provides interactive communication between students and the AI tutor
    with adaptive learning responses and engagement tracking.
    """
    await manager.connect(websocket, student_id)
    logger.info(f"👋 Student {student_id} connected to AI tutor")
    
    try:
        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "message": f"Hello! I'm your AI tutor. How can I help you learn today? 📚",
            "timestamp": "2024-01-01T00:00:00Z",
            "suggestions": [
                "Ask me a question about any topic",
                "Request practice problems",
                "Get help with homework",
                "Explore new subjects"
            ]
        }
        await manager.send_personal_message(json.dumps(welcome_message), student_id)
        
        while True:
            # Receive message from student
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            logger.info(f"💬 Student {student_id} message: {message_data.get('message', '')[:100]}...")
            
            # Process message through AI tutor service
            from backend.services.advanced_ai_generator import advanced_ai_generator
            
            ai_response_text = await advanced_ai_generator.generate_chat_response(
                user_message=message_data.get('message', ''),
                conversation_history=[],
                subject=message_data.get('subject', 'General')
            )
            
            # Prepare response
            response = {
                "type": "tutor_response",
                "content": ai_response_text,
                "confidence": 0.8,
                "recommendations": [],
                "follow_up_questions": [],
                "student_id": student_id,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send response back to student
            await manager.send_personal_message(json.dumps(response), student_id)
            
            logger.info(f"🤖 AI tutor responded to student {student_id}")
            
    except WebSocketDisconnect:
        manager.disconnect(student_id)
        logger.info(f"👋 Student {student_id} disconnected from tutor chat")
    except Exception as e:
        logger.error(f"❌ WebSocket error for student {student_id}: {e}")
        manager.disconnect(student_id)


@app.websocket("/ws/notifications/{user_id}")
async def websocket_notifications_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint for real-time notifications.
    
    Sends notifications about achievements, reminders, and system updates.
    """
    await manager.connect(websocket, user_id, connection_type="notifications")
    logger.info(f"🔔 User {user_id} connected to notifications")
    
    try:
        # Send connection confirmation
        confirmation = {
            "type": "connection_confirmed",
            "message": "Connected to notification service",
            "user_id": user_id,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        await manager.send_personal_message(json.dumps(confirmation), user_id)
        
        # Keep connection alive
        while True:
            try:
                # Wait for ping or just keep connection alive
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
                
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        logger.info(f"🔔 User {user_id} disconnected from notifications")


# Background task for sending periodic notifications
async def send_learning_reminders():
    """Send learning reminders to students."""
    while True:
        try:
            await asyncio.sleep(3600)  # Every hour
            
            # This would query the database for students who need reminders
            # For demo purposes, we'll just log
            logger.info("📅 Checking for learning reminders...")
            
            # Example: Send reminder to active connections
            reminder_message = {
                "type": "learning_reminder",
                "message": "📚 Don't forget to continue your learning journey!",
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            # Send to all connected students (in a real app, you'd be more selective)
            for connection_id in list(manager.active_connections.keys()):
                try:
                    await manager.send_personal_message(
                        json.dumps(reminder_message), 
                        connection_id
                    )
                except:
                    pass  # Connection might be closed
                    
        except Exception as e:
            logger.error(f"Error sending learning reminders: {e}")


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Starting AI Personal Tutor server...")
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        access_log=settings.DEBUG
    )
