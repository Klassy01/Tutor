"""
Student management API endpoints.

Handles student profile management, preferences, settings,
and student-specific data operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.models.student import Student, StudentProfile
from backend.models.user import User
from backend.api.dependencies import get_current_student, get_current_user, validate_student_access

router = APIRouter()


# Pydantic models
class StudentResponse(BaseModel):
    """Student profile response model."""
    id: int
    user_id: int
    grade_level: Optional[str]
    academic_goals: Optional[str]
    subjects_of_interest: Optional[List[str]]
    learning_style: Optional[str]
    preferred_difficulty: float
    pace_preference: str
    current_difficulty_level: float
    knowledge_level: float
    engagement_score: float
    total_study_time: int
    sessions_completed: int
    points_earned: int
    current_streak: int
    longest_streak: int
    tutor_personality: str
    feedback_frequency: str
    hint_preference: str
    
    class Config:
        from_attributes = True


class StudentUpdate(BaseModel):
    """Student profile update model."""
    grade_level: Optional[str] = None
    academic_goals: Optional[str] = None
    subjects_of_interest: Optional[List[str]] = None
    learning_style: Optional[str] = None
    preferred_difficulty: Optional[float] = None
    pace_preference: Optional[str] = None
    tutor_personality: Optional[str] = None
    feedback_frequency: Optional[str] = None
    hint_preference: Optional[str] = None
    reminder_enabled: Optional[bool] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    study_schedule: Optional[Dict[str, Any]] = None


class StudentPreferences(BaseModel):
    """Student learning preferences model."""
    learning_style: str
    tutor_personality: str
    feedback_frequency: str
    hint_preference: str
    pace_preference: str
    reminder_enabled: bool
    notification_preferences: Dict[str, Any]
    study_schedule: Optional[Dict[str, Any]] = None


class StudentStats(BaseModel):
    """Student statistics model."""
    total_study_time: int
    sessions_completed: int
    average_session_duration: float
    points_earned: int
    current_streak: int
    longest_streak: int
    badges_earned: List[str]
    current_difficulty_level: float
    knowledge_level: float
    engagement_score: float


@router.get("/profile", response_model=StudentResponse)
async def get_student_profile(
    current_student: Student = Depends(get_current_student)
):
    """
    Get current student's profile information.
    
    Returns comprehensive profile data including learning preferences,
    progress metrics, and personalization settings.
    """
    return StudentResponse.from_orm(current_student)


@router.put("/profile", response_model=StudentResponse)
async def update_student_profile(
    profile_update: StudentUpdate,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Update student profile information.
    
    Allows students to modify their learning preferences, goals,
    and personalization settings.
    """
    # Update fields that are provided
    update_data = profile_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_student, field):
            setattr(current_student, field, value)
    
    # Update timestamp
    current_student.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_student)
    
    return StudentResponse.from_orm(current_student)


@router.get("/preferences", response_model=StudentPreferences)
async def get_student_preferences(
    current_student: Student = Depends(get_current_student)
):
    """
    Get student's learning preferences and settings.
    
    Returns learning style, tutor personality, feedback preferences,
    and other personalization settings.
    """
    return StudentPreferences(
        learning_style=current_student.learning_style or "mixed",
        tutor_personality=current_student.tutor_personality,
        feedback_frequency=current_student.feedback_frequency,
        hint_preference=current_student.hint_preference,
        pace_preference=current_student.pace_preference,
        reminder_enabled=current_student.reminder_enabled,
        notification_preferences=current_student.notification_preferences or {},
        study_schedule=current_student.study_schedule
    )


@router.put("/preferences", response_model=StudentPreferences)
async def update_student_preferences(
    preferences: StudentPreferences,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Update student's learning preferences.
    
    Allows customization of learning experience including tutor
    personality, feedback frequency, and notification settings.
    """
    current_student.learning_style = preferences.learning_style
    current_student.tutor_personality = preferences.tutor_personality
    current_student.feedback_frequency = preferences.feedback_frequency
    current_student.hint_preference = preferences.hint_preference
    current_student.pace_preference = preferences.pace_preference
    current_student.reminder_enabled = preferences.reminder_enabled
    current_student.notification_preferences = preferences.notification_preferences
    current_student.study_schedule = preferences.study_schedule
    current_student.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(current_student)
    
    return StudentPreferences.from_orm(current_student)


@router.get("/stats", response_model=StudentStats)
async def get_student_statistics(
    current_student: Student = Depends(get_current_student)
):
    """
    Get student's learning statistics and achievements.
    
    Returns comprehensive stats including study time, streaks,
    points, badges, and performance metrics.
    """
    return StudentStats(
        total_study_time=current_student.total_study_time,
        sessions_completed=current_student.sessions_completed,
        average_session_duration=current_student.average_session_duration,
        points_earned=current_student.points_earned,
        current_streak=current_student.current_streak,
        longest_streak=current_student.longest_streak,
        badges_earned=current_student.badges_earned or [],
        current_difficulty_level=current_student.current_difficulty_level,
        knowledge_level=current_student.knowledge_level,
        engagement_score=current_student.engagement_score
    )


@router.get("/dashboard")
async def get_student_dashboard(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get student dashboard with overview information.
    
    Returns a comprehensive dashboard with recent activity,
    progress summaries, recommendations, and key metrics.
    """
    from backend.models.learning_session import LearningSession
    from backend.models.progress import Progress
    from backend.services.adaptive_learning import AdaptiveLearningEngine
    
    # Get recent sessions
    recent_sessions = db.query(LearningSession).filter(
        LearningSession.student_id == current_student.id
    ).order_by(LearningSession.started_at.desc()).limit(5).all()
    
    # Get progress in various subjects
    progress_records = db.query(Progress).filter(
        Progress.student_id == current_student.id,
        Progress.mastery_level > 0
    ).all()
    
    # Calculate subject progress
    subject_progress = {}
    for progress in progress_records:
        if progress.learning_objective and progress.learning_objective.category:
            subject = progress.learning_objective.category.name
            if subject not in subject_progress:
                subject_progress[subject] = {"total": 0, "mastered": 0, "avg_mastery": 0}
            
            subject_progress[subject]["total"] += 1
            if progress.is_mastered:
                subject_progress[subject]["mastered"] += 1
            subject_progress[subject]["avg_mastery"] += progress.mastery_level
    
    # Calculate averages
    for subject_data in subject_progress.values():
        if subject_data["total"] > 0:
            subject_data["avg_mastery"] /= subject_data["total"]
            subject_data["completion_rate"] = (
                subject_data["mastered"] / subject_data["total"] * 100
            )
    
    # Get recommendations
    adaptive_engine = AdaptiveLearningEngine()
    recommendations = await adaptive_engine.generate_personalized_recommendations(
        current_student, db, recommendation_count=3
    )
    
    return {
        "student_info": {
            "name": current_student.user.display_name,
            "current_level": current_student.current_difficulty_level,
            "knowledge_score": current_student.knowledge_level,
            "engagement_score": current_student.engagement_score
        },
        "recent_activity": [
            {
                "session_id": session.id,
                "subject": session.subject_area,
                "topic": session.topic,
                "accuracy": session.accuracy_rate,
                "duration": session.duration_minutes,
                "date": session.started_at.isoformat()
            }
            for session in recent_sessions
        ],
        "subject_progress": subject_progress,
        "achievements": {
            "points_earned": current_student.points_earned,
            "current_streak": current_student.current_streak,
            "badges": current_student.badges_earned or [],
            "total_study_time": current_student.total_study_time
        },
        "recommendations": recommendations,
        "quick_stats": {
            "sessions_this_week": len([
                s for s in recent_sessions 
                if (datetime.utcnow() - s.started_at).days < 7
            ]),
            "average_accuracy": sum(
                s.accuracy_rate for s in recent_sessions if s.accuracy_rate
            ) / len(recent_sessions) if recent_sessions else 0,
            "preferred_subjects": current_student.subjects_of_interest or []
        }
    }


@router.get("/learning-history")
async def get_learning_history(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0
):
    """
    Get student's learning history with pagination.
    
    Returns chronological list of learning sessions with
    performance metrics and progress indicators.
    """
    from backend.models.learning_session import LearningSession
    
    sessions = db.query(LearningSession).filter(
        LearningSession.student_id == current_student.id
    ).order_by(
        LearningSession.started_at.desc()
    ).offset(offset).limit(limit).all()
    
    history = []
    for session in sessions:
        history.append({
            "session_id": session.id,
            "date": session.started_at.isoformat(),
            "subject_area": session.subject_area,
            "topic": session.topic,
            "session_type": session.session_type,
            "duration_minutes": session.duration_minutes,
            "questions_attempted": session.questions_attempted,
            "questions_correct": session.questions_correct,
            "accuracy_rate": session.accuracy_rate,
            "difficulty_level": session.difficulty_level_start,
            "engagement_score": session.engagement_score,
            "hints_used": session.hints_used,
            "status": session.status
        })
    
    return {
        "history": history,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": db.query(LearningSession).filter(
                LearningSession.student_id == current_student.id
            ).count()
        }
    }


@router.get("/achievements")
async def get_student_achievements(
    current_student: Student = Depends(get_current_student)
):
    """
    Get student's achievements, badges, and milestones.
    
    Returns comprehensive achievement data including earned badges,
    progress milestones, and recognition for learning accomplishments.
    """
    # Calculate various achievement metrics
    achievements = {
        "badges": current_student.badges_earned or [],
        "points": {
            "total_earned": current_student.points_earned,
            "rank": "Beginner",  # This would be calculated based on point ranges
            "next_milestone": 1000 - (current_student.points_earned % 1000)
        },
        "streaks": {
            "current": current_student.current_streak,
            "longest": current_student.longest_streak,
            "streak_badges": []  # Based on streak achievements
        },
        "learning_milestones": {
            "sessions_completed": current_student.sessions_completed,
            "total_study_hours": round(current_student.total_study_time / 60, 1),
            "knowledge_level": current_student.knowledge_level,
            "difficulty_progression": current_student.current_difficulty_level
        },
        "recent_achievements": [],  # This would track recent badge/milestone unlocks
        "progress_towards_next": {
            "next_badge": "Dedicated Learner",
            "requirement": "Complete 50 sessions",
            "current_progress": current_student.sessions_completed,
            "target": 50,
            "percentage": min(100, (current_student.sessions_completed / 50) * 100)
        }
    }
    
    # Determine rank based on points
    if current_student.points_earned >= 5000:
        achievements["points"]["rank"] = "Expert"
    elif current_student.points_earned >= 2000:
        achievements["points"]["rank"] = "Advanced"
    elif current_student.points_earned >= 500:
        achievements["points"]["rank"] = "Intermediate"
    
    return achievements


@router.post("/goals")
async def set_learning_goals(
    goals: Dict[str, Any],
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Set or update student's learning goals.
    
    Allows students to define academic goals, target achievements,
    and learning objectives for personalized recommendations.
    """
    current_student.academic_goals = goals.get("academic_goals", current_student.academic_goals)
    
    # Store additional goal data in student profile
    if hasattr(current_student, 'detailed_profile') and current_student.detailed_profile:
        profile = current_student.detailed_profile
        if not profile.learning_patterns:
            profile.learning_patterns = {}
        profile.learning_patterns["goals"] = goals
        profile.updated_at = datetime.utcnow()
    
    current_student.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Learning goals updated successfully", "goals": goals}


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student_by_id(
    student_id: int,
    student: Student = Depends(validate_student_access),
    current_user: User = Depends(get_current_user)
):
    """
    Get student profile by ID (admin/teacher access).
    
    Allows authorized users (teachers, admins) to access
    student profile information for educational purposes.
    """
    return StudentResponse.from_orm(student)
