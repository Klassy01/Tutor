"""
Real Lesson Management Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from backend.api.dependencies import get_current_user, get_db
from backend.services.advanced_ai_generator import advanced_ai_generator
from backend.services.progress_service import progress_service
from backend.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/subjects")
async def get_available_subjects(
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """Get list of available subjects."""
    return [
        "Mathematics",
        "Computer Science",
        "Physics",
        "Chemistry",
        "Biology",
        "History",
        "Literature",
        "Economics",
        "Psychology",
        "Philosophy"
    ]

@router.get("/topics/{subject}")
async def get_subject_topics(
    subject: str,
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """Get available topics for a subject."""
    topic_map = {
        "Mathematics": ["Algebra", "Calculus", "Geometry", "Statistics", "Linear Algebra", "Discrete Math"],
        "Computer Science": ["Data Structures", "Algorithms", "Machine Learning", "Web Development", "Databases", "Operating Systems"],
        "Physics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Quantum Physics", "Relativity", "Optics"],
        "Chemistry": ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Biochemistry", "Analytical Chemistry"],
        "Biology": ["Cell Biology", "Genetics", "Evolution", "Ecology", "Microbiology", "Human Anatomy"],
        "History": ["Ancient History", "Medieval History", "Modern History", "World Wars", "American History", "European History"],
        "Literature": ["Classic Literature", "Modern Literature", "Poetry", "Drama", "Literary Analysis", "World Literature"],
        "Economics": ["Microeconomics", "Macroeconomics", "International Economics", "Economic Theory", "Behavioral Economics"],
        "Psychology": ["Cognitive Psychology", "Social Psychology", "Developmental Psychology", "Abnormal Psychology", "Research Methods"],
        "Philosophy": ["Ethics", "Logic", "Metaphysics", "Philosophy of Mind", "Political Philosophy", "Ancient Philosophy"]
    }
    
    return topic_map.get(subject, ["General Topics", "Introduction", "Advanced Topics"])

@router.post("/generate")
async def generate_lesson(
    lesson_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a new AI-powered lesson."""
    try:
        # Extract parameters
        subject = lesson_request.get("subject", "General")
        topic = lesson_request.get("topic", "Introduction")
        difficulty = lesson_request.get("difficulty_level", "intermediate")
        learning_objectives = lesson_request.get("learning_objectives", [])
        
        logger.info(f"Generating lesson for user {current_user.id}: {subject} - {topic}")
        
        # Generate lesson using advanced AI
        lesson_content = await advanced_ai_generator.generate_lesson(
            subject=subject,
            topic=topic,
            difficulty_level=difficulty,
            learning_objectives=learning_objectives
        )
        
        if not lesson_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate lesson content"
            )
        
        # Add metadata
        lesson_data = {
            "id": f"lesson_{current_user.id}_{hash(f'{subject}_{topic}_{difficulty}')}",
            "user_id": current_user.id,
            "subject": subject,
            "topic": topic,
            "difficulty_level": difficulty,
            "learning_objectives": learning_objectives,
            **lesson_content,
            "generated_at": "now",
            "estimated_duration": lesson_content.get("estimated_duration", "15-20 minutes")
        }
        
        return {
            "success": True,
            "lesson": lesson_data,
            "message": f"Successfully generated {difficulty} lesson on {topic} in {subject}"
        }
        
    except Exception as e:
        logger.error(f"Error generating lesson for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate lesson"
        )

@router.post("/complete")
async def complete_lesson(
    completion_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Mark a lesson as completed and update progress."""
    try:
        lesson_data = completion_data.get("lesson_data", {})
        time_spent = completion_data.get("time_spent_minutes", 15)
        
        if not lesson_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Lesson data is required"
            )
        
        logger.info(f"Recording lesson completion for user {current_user.id}")
        
        # Record completion using progress service
        result = await progress_service.record_lesson_completion(
            user_id=current_user.id,
            lesson_data=lesson_data,
            time_spent=time_spent,
            db=db
        )
        
        return {
            "success": True,
            "message": "Lesson completion recorded successfully",
            **result
        }
        
    except Exception as e:
        logger.error(f"Error recording lesson completion for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record lesson completion"
        )

@router.get("/history")
async def get_lesson_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's lesson completion history."""
    try:
        from backend.models.user_analytics import LessonCompletion
        
        # Get recent lesson completions
        completions = db.query(LessonCompletion).filter(
            LessonCompletion.user_id == current_user.id
        ).order_by(LessonCompletion.completed_at.desc()).limit(limit).all()
        
        history = []
        for completion in completions:
            history.append({
                "lesson_id": completion.lesson_id,
                "subject": completion.subject,
                "topic": completion.topic,
                "difficulty_level": completion.difficulty_level,
                "time_spent_minutes": completion.time_spent_minutes,
                "completion_percentage": completion.completion_percentage,
                "completed_at": completion.completed_at.isoformat()
            })
        
        return {
            "success": True,
            "history": history,
            "total_lessons": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error fetching lesson history for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch lesson history"
        )

@router.get("/recommendations")
async def get_lesson_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get personalized lesson recommendations."""
    try:
        # Get user progress summary
        progress_summary = await progress_service.get_user_progress_summary(current_user.id, db)
        
        recommendations = []
        
        # Analyze subject progress to recommend next topics
        subject_progress = progress_summary.get("subject_progress", {})
        
        # If user is new, recommend beginner topics
        if progress_summary["overall_stats"]["total_lessons_completed"] == 0:
            recommendations.extend([
                {
                    "type": "beginner",
                    "subject": "Mathematics",
                    "topic": "Algebra",
                    "difficulty_level": "beginner",
                    "reason": "Great starting point for mathematical concepts",
                    "estimated_time": "15 minutes"
                },
                {
                    "type": "beginner",
                    "subject": "Computer Science",
                    "topic": "Data Structures",
                    "difficulty_level": "beginner",
                    "reason": "Essential foundation for programming",
                    "estimated_time": "20 minutes"
                }
            ])
        else:
            # Recommend based on performance
            for subject, stats in subject_progress.items():
                if stats.get("avg_score", 0) > 80:
                    # User is doing well, suggest advanced topics
                    recommendations.append({
                        "type": "advanced",
                        "subject": subject,
                        "topic": "Advanced Topics",
                        "difficulty_level": "advanced",
                        "reason": f"You're excelling in {subject}! Ready for advanced concepts.",
                        "estimated_time": "25 minutes"
                    })
                elif stats.get("avg_score", 0) < 60:
                    # User needs review
                    recommendations.append({
                        "type": "review",
                        "subject": subject,
                        "topic": "Fundamentals Review",
                        "difficulty_level": "beginner",
                        "reason": f"Let's strengthen your {subject} foundation.",
                        "estimated_time": "15 minutes"
                    })
        
        # If no specific recommendations, provide general ones
        if not recommendations:
            recommendations.extend([
                {
                    "type": "explore",
                    "subject": "Physics",
                    "topic": "Mechanics",
                    "difficulty_level": "intermediate",
                    "reason": "Expand your knowledge with fundamental physics",
                    "estimated_time": "20 minutes"
                },
                {
                    "type": "explore",
                    "subject": "History",
                    "topic": "Ancient History",
                    "difficulty_level": "intermediate",
                    "reason": "Discover fascinating historical events",
                    "estimated_time": "18 minutes"
                }
            ])
        
        return {
            "success": True,
            "recommendations": recommendations[:5],  # Limit to top 5
            "based_on": {
                "total_lessons": progress_summary["overall_stats"]["total_lessons_completed"],
                "overall_accuracy": progress_summary["overall_stats"]["overall_accuracy"],
                "strongest_subjects": list(subject_progress.keys())[:3]
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating lesson recommendations for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate lesson recommendations"
        )
