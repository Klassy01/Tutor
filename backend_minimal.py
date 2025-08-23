"""
Minimal AI-Powered Personal Tutor Backend

This is a simplified version that starts the core services without 
heavy dependencies, then loads AI features as they become available.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import os
from datetime import datetime

# Core imports that should always work
from backend.core.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Personal Tutor System with Progressive Feature Loading",
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check models
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    features: dict

class SystemInfo(BaseModel):
    app_name: str
    version: str
    database_status: str
    ai_status: str
    features_loaded: list

# Global feature status
features_status = {
    "database": False,
    "ai_models": False,
    "recommendation_engine": False,
    "authentication": False,
    "websockets": False
}

@app.on_event("startup")
async def startup_event():
    """Initialize services progressively"""
    logger.info("🚀 Starting AI-Powered Personal Tutor Backend...")
    
    # Test database connection
    try:
        from backend.core.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        features_status["database"] = True
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.warning(f"⚠️ Database connection failed: {e}")
        features_status["database"] = False
    
    # Test AI models
    try:
        from backend.services.ai_models import ai_model_manager
        features_status["ai_models"] = True
        logger.info("✅ AI models initialized")
    except Exception as e:
        logger.warning(f"⚠️ AI models failed to initialize: {e}")
        features_status["ai_models"] = False
    
    # Test recommendation engine
    try:
        from backend.services.recommendation_engine import recommendation_engine
        features_status["recommendation_engine"] = True
        logger.info("✅ Recommendation engine initialized")
    except Exception as e:
        logger.warning(f"⚠️ Recommendation engine failed: {e}")
        features_status["recommendation_engine"] = False
    
    logger.info("🎯 Backend startup completed with available features")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "running",
        "features_available": sum(features_status.values()),
        "total_features": len(features_status)
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if features_status["database"] else "degraded",
        timestamp=datetime.now().isoformat(),
        version=settings.APP_VERSION,
        features=features_status
    )

@app.get("/system/info", response_model=SystemInfo)
async def system_info():
    """System information endpoint"""
    return SystemInfo(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        database_status="connected" if features_status["database"] else "disconnected",
        ai_status="available" if features_status["ai_models"] else "unavailable",
        features_loaded=[k for k, v in features_status.items() if v]
    )

@app.get("/api/demo/dashboard")
async def demo_dashboard():
    """Demo dashboard endpoint"""
    try:
        from backend.api.v1.endpoints.demo import demo_dashboard
        return await demo_dashboard()
    except Exception as e:
        logger.warning(f"Demo dashboard failed: {e}")
        return {
            "message": "Demo dashboard temporarily unavailable",
            "reason": "AI services loading",
            "fallback_data": {
                "students_count": 0,
                "sessions_today": 0,
                "ai_interactions": 0,
                "avg_session_time": 0
            }
        }

@app.get("/api/demo/ai-chat")
async def demo_ai_chat():
    """Demo AI chat endpoint"""
    if not features_status["ai_models"]:
        return {
            "response": "AI chat is temporarily unavailable while models are loading. Please try again in a few minutes.",
            "status": "loading"
        }
    
    try:
        from backend.api.v1.endpoints.demo import demo_ai_chat
        return await demo_ai_chat()
    except Exception as e:
        logger.error(f"AI chat failed: {e}")
        return {
            "response": "I'm currently experiencing some technical difficulties. Please try again later.",
            "status": "error"
        }

# Add basic API endpoints for testing
@app.get("/api/test")
async def test_api():
    """Test API endpoint"""
    return {
        "message": "API is working",
        "features": features_status,
        "timestamp": datetime.now().isoformat()
    }

# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "An internal error occurred",
            "type": type(exc).__name__,
            "detail": str(exc) if settings.DEBUG else "Internal server error"
        }
    )

# Try to mount static files if they exist
try:
    static_path = "static"
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
        logger.info("✅ Static files mounted")
except Exception as e:
    logger.warning(f"⚠️ Static files not mounted: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level="info",
        reload=settings.DEBUG
    )
