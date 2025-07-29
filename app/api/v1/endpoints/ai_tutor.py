"""
AI Tutor API endpoints for real-time tutoring interactions.

Provides endpoints for AI-powered tutoring sessions, adaptive
questioning, personalized feedback, and intelligent content delivery.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json

from app.core.database import get_db
from app.models.student import Student
from app.models.learning_session import LearningSession, SessionInteraction
from app.services.ai_tutor_service import AITutorService
from app.services.adaptive_learning import AdaptiveLearningEngine
from app.api.dependencies import get_current_student

router = APIRouter()


# Pydantic models for request/response
class TutorQuestionRequest(BaseModel):
    """Request model for asking the AI tutor a question."""
    question: str
    context: Optional[str] = None
    subject_area: Optional[str] = None
    difficulty_preference: Optional[str] = None


class TutorResponse(BaseModel):
    """Response model for AI tutor interactions."""
    response: str
    confidence_level: float
    suggested_actions: List[str]
    follow_up_questions: List[str]
    learning_resources: List[Dict[str, Any]]


class ExerciseRequest(BaseModel):
    """Request model for generating adaptive exercises."""
    subject_area: str
    topic: Optional[str] = None
    difficulty_level: Optional[float] = None
    question_count: Optional[int] = 5
    question_types: Optional[List[str]] = None


class ExerciseResponse(BaseModel):
    """Response model for generated exercises."""
    session_id: int
    questions: List[Dict[str, Any]]
    estimated_duration: int
    difficulty_level: float
    learning_objectives: List[str]


class AnswerSubmission(BaseModel):
    """Model for submitting answers to exercises."""
    session_id: int
    question_id: str
    answer: str
    confidence_level: Optional[float] = None
    time_spent: Optional[float] = None


class FeedbackResponse(BaseModel):
    """Response model for answer feedback."""
    is_correct: bool
    explanation: str
    hints: List[str]
    next_question: Optional[Dict[str, Any]]
    progress_update: Dict[str, Any]


@router.post("/ask-question", response_model=TutorResponse)
async def ask_tutor_question(
    request: TutorQuestionRequest,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Ask the AI tutor a question and get an intelligent response.
    
    The AI tutor provides contextual, personalized responses based on
    the student's learning history and current difficulty level.
    """
    ai_tutor = AITutorService()
    
    # Get student's learning context
    student_context = {
        "current_difficulty": current_student.current_difficulty_level,
        "learning_style": current_student.learning_style,
        "subject_interests": current_student.subjects_of_interest,
        "recent_performance": await ai_tutor.get_recent_performance(current_student.id, db)
    }
    
    # Generate AI response
    response = await ai_tutor.generate_response(
        question=request.question,
        context=request.context,
        student_context=student_context,
        subject_area=request.subject_area
    )
    
    return TutorResponse(**response)


@router.post("/generate-exercise", response_model=ExerciseResponse)
async def generate_adaptive_exercise(
    request: ExerciseRequest,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Generate adaptive exercises tailored to student's level and needs.
    
    Uses the adaptive learning engine to create personalized exercises
    that adjust difficulty based on student performance and learning goals.
    """
    adaptive_engine = AdaptiveLearningEngine()
    ai_tutor = AITutorService()
    
    # Determine optimal difficulty level
    if request.difficulty_level is None:
        difficulty_level = current_student.current_difficulty_level
    else:
        difficulty_level = request.difficulty_level
    
    # Create new learning session
    session = LearningSession(
        student_id=current_student.id,
        session_type="exercise",
        subject_area=request.subject_area,
        topic=request.topic,
        difficulty_level_start=difficulty_level,
        status="active"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    
    # Generate adaptive questions
    questions = await ai_tutor.generate_adaptive_questions(
        subject_area=request.subject_area,
        topic=request.topic,
        difficulty_level=difficulty_level,
        question_count=request.question_count,
        question_types=request.question_types,
        student_profile=current_student
    )
    
    # Estimate duration based on question complexity
    estimated_duration = len(questions) * 3  # 3 minutes per question average
    
    # Get learning objectives for this topic
    learning_objectives = await adaptive_engine.get_learning_objectives(
        request.subject_area, request.topic, db
    )
    
    return ExerciseResponse(
        session_id=session.id,
        questions=questions,
        estimated_duration=estimated_duration,
        difficulty_level=difficulty_level,
        learning_objectives=[obj.title for obj in learning_objectives]
    )


@router.post("/submit-answer", response_model=FeedbackResponse)
async def submit_answer(
    submission: AnswerSubmission,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Submit an answer and receive intelligent feedback.
    
    Provides immediate feedback, explanations, and adaptive
    adjustments based on the student's response.
    """
    # Get the learning session
    session = db.query(LearningSession).filter(
        LearningSession.id == submission.session_id,
        LearningSession.student_id == current_student.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    ai_tutor = AITutorService()
    adaptive_engine = AdaptiveLearningEngine()
    
    # Evaluate the answer
    evaluation = await ai_tutor.evaluate_answer(
        question_id=submission.question_id,
        student_answer=submission.answer,
        session_context=session,
        student_profile=current_student
    )
    
    # Create session interaction record
    interaction = SessionInteraction(
        session_id=session.id,
        interaction_type="question",
        question_text=evaluation.get("question_text"),
        student_answer=submission.answer,
        is_correct=evaluation["is_correct"],
        response_time_seconds=submission.time_spent,
        confidence_level=submission.confidence_level,
        ai_feedback_given=evaluation["explanation"],
        difficulty_level=session.difficulty_level_start
    )
    
    db.add(interaction)
    
    # Update session metrics
    session.add_interaction({
        "correct": evaluation["is_correct"],
        "hint_used": False,
        "time_spent": submission.time_spent
    })
    
    # Apply adaptive learning adjustments
    await adaptive_engine.update_student_model(
        student=current_student,
        interaction=interaction,
        db=db
    )
    
    # Generate next question if available
    next_question = None
    if session.questions_attempted < 10:  # Example limit
        next_question = await ai_tutor.get_next_adaptive_question(
            session=session,
            student=current_student,
            db=db
        )
    
    # Get progress update
    progress_update = await adaptive_engine.calculate_progress_update(
        student=current_student,
        interaction=interaction,
        db=db
    )
    
    db.commit()
    
    return FeedbackResponse(
        is_correct=evaluation["is_correct"],
        explanation=evaluation["explanation"],
        hints=evaluation.get("hints", []),
        next_question=next_question,
        progress_update=progress_update
    )


@router.get("/session-status/{session_id}")
async def get_session_status(
    session_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get the current status of a learning session."""
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.student_id == current_student.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    return {
        "session_id": session.id,
        "status": session.status,
        "questions_attempted": session.questions_attempted,
        "questions_correct": session.questions_correct,
        "accuracy_rate": session.accuracy_rate,
        "duration_minutes": session.duration_minutes,
        "difficulty_level": session.difficulty_level_start,
        "engagement_score": session.engagement_score,
        "completion_percentage": session.completion_percentage
    }


@router.post("/end-session/{session_id}")
async def end_learning_session(
    session_id: int,
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """End a learning session and get final results."""
    session = db.query(LearningSession).filter(
        LearningSession.id == session_id,
        LearningSession.student_id == current_student.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found"
        )
    
    # Complete the session
    session.complete_session()
    
    # Update student statistics
    current_student.add_study_time(int(session.duration_minutes or 0))
    
    # Generate session summary
    adaptive_engine = AdaptiveLearningEngine()
    session_summary = await adaptive_engine.generate_session_summary(
        session=session,
        student=current_student,
        db=db
    )
    
    db.commit()
    
    return {
        "session_summary": session_summary,
        "performance_metrics": {
            "accuracy": session.accuracy_rate,
            "questions_answered": session.questions_attempted,
            "correct_answers": session.questions_correct,
            "duration": session.duration_minutes,
            "engagement_score": session.engagement_score
        },
        "learning_progress": {
            "difficulty_change": session.difficulty_level_end - session.difficulty_level_start,
            "knowledge_gained": session_summary.get("knowledge_gained", 0),
            "next_recommendations": session_summary.get("recommendations", [])
        }
    }


@router.get("/personalized-recommendations")
async def get_personalized_recommendations(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get personalized learning recommendations for the student."""
    adaptive_engine = AdaptiveLearningEngine()
    
    recommendations = await adaptive_engine.generate_personalized_recommendations(
        student=current_student,
        db=db
    )
    
    return recommendations
