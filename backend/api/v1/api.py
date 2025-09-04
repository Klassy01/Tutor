"""
API v1 router configuration.

Real production endpoints for the AI Learning Platform.
All demo endpoints have been removed.
"""

from fastapi import APIRouter

from backend.api.v1.endpoints import (
    auth,
    lessons, 
    quizzes,
    ai_tutor,
    dashboard,
    learning,
    students,
    progress,
    content
)

api_router = APIRouter()

# Include all real endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(quizzes.router, prefix="/quizzes", tags=["quizzes"])
api_router.include_router(ai_tutor.router, prefix="/ai-tutor", tags=["ai-tutor"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
