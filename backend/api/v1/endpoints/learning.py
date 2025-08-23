"""
Learning session management API endpoints.

Handles learning session lifecycle, session interactions,
and real-time learning progress tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.models.student import Student
from backend.models.learning_session import LearningSession, SessionInteraction
from backend.models.content import Content
from backend.api.dependencies import get_current_student

router = APIRouter()


# Pydantic models
class SessionCreateRequest(BaseModel):
    """Create learning session request model."""
    session_type: str = "practice"
    subject_area: str
    topic: Optional[str] = None
    content_id: Optional[int] = None
    target_questions: Optional[int] = 10


class SessionResponse(BaseModel):
    """Learning session response model."""
    id: int
    session_type: str
    subject_area: str
    topic: Optional[str]
    status: str
    questions_attempted: int
    questions_correct: int
    accuracy_rate: Optional[float]
    difficulty_level_start: Optional[float]
    difficulty_level_end: Optional[float]
    duration_minutes: Optional[float]
    engagement_score: Optional[float]
    hints_used: int
    completion_percentage: float
    started_at: datetime
    ended_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InteractionCreateRequest(BaseModel):
    """Create session interaction request model."""
    interaction_type: str
    question_text: Optional[str] = None
    student_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    response_time_seconds: Optional[float] = None
    hint_used: bool = False
    hint_content: Optional[str] = None
    confidence_level: Optional[float] = None


class InteractionResponse(BaseModel):
    """Session interaction response model."""
    id: int
    session_id: int
    interaction_type: str
    sequence_number: int
    question_text: Optional[str]
    student_answer: Optional[str]
    is_correct: Optional[bool]
    response_time_seconds: Optional[float]
    hint_used: bool
    ai_feedback_given: Optional[str]
    difficulty_level: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


@router.post("/sessions", response_model=SessionResponse)
async def create_learning_session(
    session_request: SessionCreateRequest,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Create a new learning session.
    
    Initializes a new learning session with the specified parameters
    and sets up adaptive learning context for the student.
    """
    # Validate content if specified
    content = None
    if session_request.content_id:
        content = db.query(Content).filter(
            Content.id == session_request.content_id,
            Content.is_published == True,
            Content.is_active == True
        ).first()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found or not available"
            )
    
    # Create learning session
    session = LearningSession(
        student_id=current_student.id,
        session_type=session_request.session_type,
        subject_area=session_request.subject_area,
        topic=session_request.topic,
        difficulty_level_start=current_student.current_difficulty_level,
        status="active"
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return SessionResponse.from_orm(session)


@router.get("/sessions", response_model=List[SessionResponse])
async def get_learning_sessions(
    status: Optional[str] = None,
    session_type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get student's learning sessions with optional filtering.
    
    Returns paginated list of learning sessions with optional
    filtering by status and session type.
    """
    query = db.query(LearningSession).filter(
        LearningSession.student_id == current_student.id
    )
    
    if status:
        query = query.filter(LearningSession.status == status)
    
    if session_type:
        query = query.filter(LearningSession.session_type == session_type)
    
    sessions = query.order_by(
        LearningSession.started_at.desc()
    ).offset(offset).limit(limit).all()
    
    return [SessionResponse.from_orm(session) for session in sessions]


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_learning_session(
    session_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get specific learning session details.
    
    Returns detailed information about a specific learning session
    including all interactions and progress metrics.
    """
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.student_id == current_student.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    return SessionResponse.from_orm(session)


@router.post("/sessions/{session_id}/interactions", response_model=InteractionResponse)
async def create_session_interaction(
    session_id: int,
    interaction_request: InteractionCreateRequest,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Create a new interaction within a learning session.
    
    Records student interactions such as answering questions,
    requesting hints, or other learning activities.
    """
    # Validate session
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.student_id == current_student.id,
        LearningSession.status == "active"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active learning session not found"
        )
    
    # Get next sequence number
    last_interaction = db.query(SessionInteraction).filter(
        SessionInteraction.session_id == session_id
    ).order_by(SessionInteraction.sequence_number.desc()).first()
    
    sequence_number = (last_interaction.sequence_number + 1) if last_interaction else 1
    
    # Create interaction
    interaction = SessionInteraction(
        session_id=session_id,
        interaction_type=interaction_request.interaction_type,
        sequence_number=sequence_number,
        question_text=interaction_request.question_text,
        student_answer=interaction_request.student_answer,
        is_correct=interaction_request.is_correct,
        response_time_seconds=interaction_request.response_time_seconds,
        hint_used=interaction_request.hint_used,
        hint_content=interaction_request.hint_content,
        confidence_level=interaction_request.confidence_level,
        difficulty_level=session.difficulty_level_start
    )
    
    if interaction_request.is_correct is not None:
        interaction.completed_at = datetime.utcnow()
    
    db.add(interaction)
    
    # Update session metrics
    if interaction_request.interaction_type == "question":
        session.questions_attempted += 1
        if interaction_request.is_correct:
            session.questions_correct += 1
        if interaction_request.hint_used:
            session.hints_used += 1
        
        # Recalculate accuracy
        session.calculate_accuracy()
    
    db.commit()
    db.refresh(interaction)
    
    return InteractionResponse.from_orm(interaction)


@router.get("/sessions/{session_id}/interactions", response_model=List[InteractionResponse])
async def get_session_interactions(
    session_id: int,
    interaction_type: Optional[str] = None,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get interactions for a specific learning session.
    
    Returns chronological list of all interactions within
    the specified learning session.
    """
    # Validate session ownership
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.student_id == current_student.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    query = db.query(SessionInteraction).filter(
        SessionInteraction.session_id == session_id
    )
    
    if interaction_type:
        query = query.filter(SessionInteraction.interaction_type == interaction_type)
    
    interactions = query.order_by(SessionInteraction.sequence_number).all()
    
    return [InteractionResponse.from_orm(interaction) for interaction in interactions]


@router.put("/sessions/{session_id}/pause")
async def pause_learning_session(
    session_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Pause an active learning session.
    
    Pauses the current session and saves progress without
    marking it as completed.
    """
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.student_id == current_student.id,
        LearningSession.status == "active"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active learning session not found"
        )
    
    session.status = "paused"
    
    # Calculate current duration
    if not session.duration_minutes:
        duration = (datetime.utcnow() - session.started_at).total_seconds() / 60
        session.duration_minutes = round(duration, 2)
    
    db.commit()
    
    return {
        "message": "Session paused successfully",
        "session_id": session_id,
        "status": session.status,
        "duration_minutes": session.duration_minutes
    }


@router.put("/sessions/{session_id}/resume")
async def resume_learning_session(
    session_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Resume a paused learning session.
    
    Resumes a previously paused session and continues
    progress tracking from where it left off.
    """
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.student_id == current_student.id,
        LearningSession.status == "paused"
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paused learning session not found"
        )
    
    session.status = "active"
    db.commit()
    
    return {
        "message": "Session resumed successfully",
        "session_id": session_id,
        "status": session.status
    }


@router.put("/sessions/{session_id}/complete")
async def complete_learning_session(
    session_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Complete a learning session.
    
    Marks the session as completed, finalizes all metrics,
    and updates student progress and statistics.
    """
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.student_id == current_student.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    if session.status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is already completed"
        )
    
    # Complete the session
    session.complete_session()
    session.difficulty_level_end = current_student.current_difficulty_level
    
    # Update student statistics
    if session.duration_minutes:
        current_student.add_study_time(int(session.duration_minutes))
    
    # Calculate engagement score based on interactions
    engagement_score = _calculate_engagement_score(session)
    session.engagement_score = engagement_score
    
    # Update student engagement score
    current_student.engagement_score = (
        current_student.engagement_score * 0.8 + engagement_score * 0.2
    )
    
    # Award points for session completion
    points_earned = _calculate_session_points(session)
    current_student.award_points(points_earned)
    
    db.commit()
    
    return {
        "message": "Session completed successfully",
        "session_id": session_id,
        "final_metrics": {
            "duration_minutes": session.duration_minutes,
            "questions_attempted": session.questions_attempted,
            "questions_correct": session.questions_correct,
            "accuracy_rate": session.accuracy_rate,
            "engagement_score": session.engagement_score,
            "difficulty_progression": session.difficulty_level_end - session.difficulty_level_start,
            "points_earned": points_earned
        },
        "student_progress": {
            "total_sessions": current_student.sessions_completed,
            "total_study_time": current_student.total_study_time,
            "total_points": current_student.points_earned,
            "current_difficulty": current_student.current_difficulty_level,
            "engagement_score": current_student.engagement_score
        }
    }


@router.get("/sessions/{session_id}/analytics")
async def get_session_analytics(
    session_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a learning session.
    
    Returns comprehensive analytics including performance patterns,
    time distribution, difficulty progression, and learning insights.
    """
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.student_id == current_student.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    # Get all interactions
    interactions = db.query(SessionInteraction).filter(
        SessionInteraction.session_id == session_id
    ).order_by(SessionInteraction.sequence_number).all()
    
    # Calculate analytics
    analytics = {
        "session_overview": {
            "id": session.id,
            "duration_minutes": session.duration_minutes,
            "questions_attempted": session.questions_attempted,
            "accuracy_rate": session.accuracy_rate,
            "engagement_score": session.engagement_score,
            "status": session.status
        },
        "performance_analysis": _analyze_session_performance(session, interactions),
        "time_analysis": _analyze_session_timing(interactions),
        "difficulty_analysis": _analyze_difficulty_progression(session, interactions),
        "learning_insights": _generate_learning_insights(session, interactions),
        "interaction_summary": {
            "total_interactions": len(interactions),
            "question_interactions": len([i for i in interactions if i.interaction_type == "question"]),
            "hint_requests": len([i for i in interactions if i.hint_used]),
            "average_response_time": sum(
                i.response_time_seconds for i in interactions 
                if i.response_time_seconds
            ) / max(1, len([i for i in interactions if i.response_time_seconds]))
        }
    }
    
    return analytics


def _calculate_engagement_score(session: LearningSession) -> float:
    """Calculate engagement score for a session."""
    base_score = 0.5
    
    # Accuracy bonus
    if session.accuracy_rate:
        if session.accuracy_rate > 80:
            base_score += 0.2
        elif session.accuracy_rate > 60:
            base_score += 0.1
    
    # Persistence bonus (completing questions)
    if session.questions_attempted > 5:
        base_score += 0.1
    
    # Hint usage (moderate hint usage shows engagement)
    if session.hints_used > 0 and session.questions_attempted > 0:
        hint_ratio = session.hints_used / session.questions_attempted
        if 0.1 <= hint_ratio <= 0.3:  # Optimal hint usage
            base_score += 0.1
    
    # Duration consideration (not too short, not too long)
    if session.duration_minutes:
        if 10 <= session.duration_minutes <= 60:  # Optimal session length
            base_score += 0.1
    
    return min(1.0, max(0.0, base_score))


def _calculate_session_points(session: LearningSession) -> int:
    """Calculate points earned for session completion."""
    base_points = 20  # Base completion points
    
    # Accuracy bonus
    if session.accuracy_rate:
        accuracy_bonus = int(session.accuracy_rate * 0.5)  # Up to 50 bonus points
        base_points += accuracy_bonus
    
    # Question volume bonus
    question_bonus = min(30, session.questions_attempted * 2)
    base_points += question_bonus
    
    # Difficulty bonus
    if session.difficulty_level_start:
        difficulty_bonus = int(session.difficulty_level_start * 20)
        base_points += difficulty_bonus
    
    return base_points


def _analyze_session_performance(session: LearningSession, interactions: List[SessionInteraction]) -> Dict[str, Any]:
    """Analyze performance patterns in the session."""
    correct_answers = [i for i in interactions if i.is_correct is True]
    incorrect_answers = [i for i in interactions if i.is_correct is False]
    
    return {
        "overall_accuracy": session.accuracy_rate,
        "correct_answers": len(correct_answers),
        "incorrect_answers": len(incorrect_answers),
        "improvement_trend": "stable",  # This would be calculated based on sequence
        "strong_areas": [],  # Would analyze by topic/skill
        "areas_for_improvement": []
    }


def _analyze_session_timing(interactions: List[SessionInteraction]) -> Dict[str, Any]:
    """Analyze timing patterns in the session."""
    response_times = [i.response_time_seconds for i in interactions if i.response_time_seconds]
    
    if not response_times:
        return {"average_response_time": 0, "timing_consistency": "N/A"}
    
    avg_response_time = sum(response_times) / len(response_times)
    
    return {
        "average_response_time": avg_response_time,
        "fastest_response": min(response_times),
        "slowest_response": max(response_times),
        "timing_consistency": "consistent" if max(response_times) - min(response_times) < 30 else "variable"
    }


def _analyze_difficulty_progression(session: LearningSession, interactions: List[SessionInteraction]) -> Dict[str, Any]:
    """Analyze difficulty progression during the session."""
    return {
        "starting_difficulty": session.difficulty_level_start,
        "ending_difficulty": session.difficulty_level_end,
        "difficulty_change": (session.difficulty_level_end or session.difficulty_level_start) - session.difficulty_level_start,
        "adaptive_adjustments": 0  # Would track actual adjustments made
    }


def _generate_learning_insights(session: LearningSession, interactions: List[SessionInteraction]) -> List[str]:
    """Generate learning insights based on session data."""
    insights = []
    
    if session.accuracy_rate and session.accuracy_rate > 85:
        insights.append("Excellent performance! You're ready for more challenging content.")
    elif session.accuracy_rate and session.accuracy_rate < 50:
        insights.append("Consider reviewing the fundamentals before moving forward.")
    
    hint_usage = session.hints_used / max(1, session.questions_attempted)
    if hint_usage > 0.5:
        insights.append("You're making good use of hints to learn. This shows active learning!")
    elif hint_usage == 0 and session.accuracy_rate and session.accuracy_rate > 70:
        insights.append("Great independent problem-solving skills!")
    
    if session.duration_minutes and session.duration_minutes > 45:
        insights.append("Long study session - remember to take breaks to maintain focus.")
    
    return insights
