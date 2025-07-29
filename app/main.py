"""
AI-Powered Personal Tutor - Main Application Entry Point

A scalable, adaptive learning system that provides personalized tutoring
experiences with AI-powered content delivery and real-time interaction.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from typing import List, Dict
import json

from app.core.config import settings
from app.core.database import engine, create_tables
from app.api.v1.api import api_router
from app.services.websocket_manager import ConnectionManager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    # Startup
    logger.info("Starting AI Personal Tutor application...")
    await create_tables()
    logger.info("Database tables created successfully")
    yield
    # Shutdown
    logger.info("Shutting down AI Personal Tutor application...")


# Create FastAPI application
app = FastAPI(
    title="AI-Powered Personal Tutor",
    description="A scalable, adaptive learning system for enhanced student engagement",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
    logger.warning("Static files directory not found. Skipping static file mounting.")


@app.get("/")
async def root():
    """Root endpoint with application information."""
    return {
        "message": "AI-Powered Personal Tutor API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "ai-personal-tutor",
        "timestamp": "2025-07-29T00:00:00Z"
    }


@app.websocket("/ws/tutor/{student_id}")
async def websocket_tutor_endpoint(websocket: WebSocket, student_id: int):
    """
    WebSocket endpoint for real-time AI tutor chat.
    
    Provides interactive communication between students and the AI tutor
    with adaptive learning responses and engagement tracking.
    """
    await manager.connect(websocket, student_id)
    try:
        while True:
            # Receive message from student
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message through AI tutor service
            # This will be implemented in the AI service layer
            response = {
                "type": "tutor_response",
                "content": f"AI Tutor response to: {message_data.get('content', '')}",
                "student_id": student_id,
                "timestamp": "2025-07-29T00:00:00Z"
            }
            
            # Send response back to student
            await manager.send_personal_message(json.dumps(response), student_id)
            
    except WebSocketDisconnect:
        manager.disconnect(student_id)
        logger.info(f"Student {student_id} disconnected from tutor chat")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
