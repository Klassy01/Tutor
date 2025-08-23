"""
API v1 router configuration.

Combines all API endpoints into a single router for the
AI Personal Tutor system.
"""

from fastapi import APIRouter

from backend.api.v1.endpoints import (
    auth,
    students, 
    content,
    learning,
    progress,
    ai_tutor,
    demo
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
api_router.include_router(ai_tutor.router, prefix="/ai-tutor", tags=["ai-tutor"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
