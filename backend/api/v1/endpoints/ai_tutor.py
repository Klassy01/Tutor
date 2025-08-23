"""
Advanced AI Tutor API endpoints.

Provides intelligent tutoring, quiz generation, content recommendations,
and adaptive learning features using multiple AI models.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from backend.core.database import get_db
from backend.core.security import verify_token
from backend.models.user import User
from backend.models.student import Student
from backend.models.learning_session import LearningSession, SessionInteraction
from backend.services.simple_ai_tutor import simple_tutor_service
from backend.services.ai_models import ai_model_manager
from backend.services.recommendation_engine import recommendation_engine

router = APIRouter()
security = HTTPBearer()
logger = logging.getLogger(__name__)


# Pydantic models
class ChatMessage(BaseModel):
    """Chat message model."""
    message: str = Field(..., description="Student's message to the AI tutor")
    session_id: Optional[int] = Field(None, description="Learning session ID")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class QuizRequest(BaseModel):
    """Quiz generation request."""
    topic: str = Field(..., description="Topic for the quiz")
    difficulty_level: float = Field(0.5, ge=0.0, le=1.0, description="Difficulty level (0.0-1.0)")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions")
    num_options: int = Field(4, ge=2, le=6, description="Number of multiple choice options")


class AnswerSubmission(BaseModel):
    """Answer submission model."""
    question_id: int = Field(..., description="Question ID")
    answer: str = Field(..., description="Student's answer")
    question_text: Optional[str] = Field(None, description="Original question text")
    correct_answer: Optional[str] = Field(None, description="Correct answer for feedback")


class ContentRecommendationRequest(BaseModel):
    """Content recommendation request."""
    query: Optional[str] = Field(None, description="Search query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    num_recommendations: int = Field(5, ge=1, le=20, description="Number of recommendations")


class TutorResponse(BaseModel):
    """AI tutor response model."""
    response: str
    confidence: float
    recommendations: List[Dict[str, Any]]
    follow_up_questions: List[str]
    difficulty_adjustment: Optional[Dict[str, Any]]
    timestamp: str


class QuizResponse(BaseModel):
    """Quiz response model."""
    questions: List[Dict[str, Any]]
    quiz_id: str
    topic: str
    difficulty_level: float
    estimated_duration: int


class FeedbackResponse(BaseModel):
    """Feedback response model."""
    is_correct: bool
    feedback: str
    confidence: float
    suggested_resources: List[Dict[str, Any]]
    timestamp: str


@router.post("/chat", response_model=TutorResponse)
async def chat_with_tutor(
    message: ChatMessage,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Chat with the AI tutor for personalized learning assistance.
    
    This endpoint provides intelligent, context-aware responses using
    advanced AI models and adaptive learning algorithms.
    """
    # Verify token and get user
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Ensure user is a student
    if user.user_type != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can chat with the tutor"
        )
    
    try:
        # Get AI tutor response
        response = await simple_tutor_service.get_tutoring_response(
            message=message.message,
            student_id=user.id,
            session_id=message.session_id,
            context=message.context
        )
        
        # Log interaction in background
        background_tasks.add_task(
            log_chat_interaction,
            user.id,
            message.message,
            response['response'],
            message.session_id,
            db
        )
        
        return TutorResponse(**response)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate tutor response"
        )


@router.post("/generate-quiz", response_model=QuizResponse)
async def generate_quiz(
    quiz_request: QuizRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Generate a personalized quiz using AI.
    
    Creates multiple-choice questions adapted to the student's level
    and learning preferences.
    """
    # Verify token and get user
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        # Generate quiz using AI
        quiz_data = await simple_tutor_service.generate_quiz(
            topic=quiz_request.topic,
            difficulty_level=quiz_request.difficulty_level,
            num_questions=quiz_request.num_questions,
            num_options=quiz_request.num_options
        )
        
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate quiz questions"
            )
        
        # Generate quiz ID
        quiz_id = f"quiz_{user_id}_{int(datetime.utcnow().timestamp())}"
        
        return QuizResponse(
            questions=questions,
            quiz_id=quiz_id,
            topic=quiz_request.topic,
            difficulty_level=quiz_request.difficulty_level,
            estimated_duration=len(questions) * 2  # 2 minutes per question
        )
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz"
        )


@router.post("/submit-answer", response_model=FeedbackResponse)
async def submit_answer(
    answer: AnswerSubmission,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Submit an answer and receive intelligent feedback.
    
    Provides detailed feedback, explanations, and suggestions
    for improvement based on the student's response.
    """
    # Verify token and get user
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        # Get feedback from AI tutor
        feedback = await advanced_tutor_service.provide_feedback(
            student_answer=answer.answer,
            correct_answer=answer.correct_answer or "Unknown",
            question=answer.question_text or "Unknown question",
            student_id=int(user_id)
        )
        
        return FeedbackResponse(**feedback)
        
    except Exception as e:
        logger.error(f"Error providing feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to provide feedback"
        )


@router.post("/recommendations")
async def get_content_recommendations(
    request: ContentRecommendationRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get personalized content recommendations.
    
    Uses ML-powered recommendation engine to suggest content
    based on learning history and preferences.
    """
    # Verify token and get user
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        recommendations = await simple_tutor_service.get_learning_recommendations(
            student_id=int(user_id),
            query=request.query,
            context=request.context,
            num_recommendations=request.num_recommendations
        )
        
        return {
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recommendations"
        )


@router.get("/similar-content/{content_id}")
async def get_similar_content(
    content_id: int,
    num_similar: int = 3,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get content similar to a specific item.
    
    Uses content embeddings to find semantically similar
    educational materials.
    """
    # Verify token
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        similar_content = await recommendation_engine.get_similar_content(
            content_id=content_id,
            num_similar=num_similar
        )
        
        return {
            "similar_content": similar_content,
            "reference_content_id": content_id,
            "count": len(similar_content)
        }
        
    except Exception as e:
        logger.error(f"Error getting similar content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get similar content"
        )


@router.get("/ai-providers")
async def get_ai_provider_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get information about available AI providers and models.
    
    Returns configuration and status of AI services.
    """
    # Verify token (admin only for detailed info)
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    provider_info = ai_model_manager.get_provider_info()
    
    return {
        "provider_info": provider_info,
        "status": "active",
        "last_updated": datetime.utcnow().isoformat()
    }


@router.post("/explain-concept")
async def explain_concept(
    concept: str,
    difficulty_level: float = 0.5,
    learning_style: str = "visual",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get a detailed explanation of a concept.
    
    Provides comprehensive explanations adapted to the student's
    level and preferred learning style.
    """
    # Verify token
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    try:
        # Create explanation prompt
        prompt = f"""
        Explain the concept of "{concept}" in detail.
        
        Student Level: {difficulty_level} (0.0 = beginner, 1.0 = advanced)
        Learning Style: {learning_style}
        
        Please provide:
        1. Clear definition
        2. Key characteristics
        3. Examples and analogies
        4. Common misconceptions
        5. Related concepts to explore
        
        Adapt your explanation to be appropriate for the student's level and learning style.
        """
        
        response = await ai_model_manager.get_response(prompt)
        
        return {
            "concept": concept,
            "explanation": response,
            "difficulty_level": difficulty_level,
            "learning_style": learning_style,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error explaining concept: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate concept explanation"
        )


@router.get("/learning-tips")
async def get_learning_tips(
    subject: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get personalized learning tips and study strategies.
    
    Provides actionable advice based on the student's learning
    history and preferences.
    """
    # Verify token and get user
    user_id = verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        # Get student profile
        student = db.query(Student).filter(Student.user_id == user.id).first()
        
        # Generate personalized learning tips
        prompt = f"""
        Generate 5-7 personalized learning tips for a student with the following profile:
        
        Learning Style: {student.learning_style if student else 'mixed'}
        Difficulty Level: {student.preferred_difficulty if student else 0.5}
        Subject Focus: {subject or 'general studies'}
        
        Provide practical, actionable tips that would help this student learn more effectively.
        Format as a numbered list with brief explanations.
        """
        
        tips = await ai_model_manager.get_response(prompt)
        
        return {
            "learning_tips": tips,
            "subject": subject or "general",
            "personalized_for": user.username,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating learning tips: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate learning tips"
        )


# Helper functions
async def log_chat_interaction(
    student_id: int,
    message: str,
    response: str,
    session_id: Optional[int],
    db: Session
):
    """Log chat interaction to database."""
    try:
        # Create learning interaction record
        interaction = SessionInteraction(
            session_id=session_id,
            interaction_type="ai_chat",
            content_data={
                "student_message": message,
                "ai_response": response,
                "timestamp": datetime.utcnow().isoformat()
            },
            response_time=1.0,  # Would be calculated in real implementation
            is_correct=None  # Not applicable for chat
        )
        
        if session_id:
            db.add(interaction)
            db.commit()
            
    except Exception as e:
        logger.error(f"Error logging chat interaction: {e}")
        # Don't raise exception as this is background task

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json

from backend.core.database import get_db
from backend.models.student import Student
from backend.models.learning_session import LearningSession, SessionInteraction
from backend.services.ai_tutor_service import AITutorService
from backend.services.adaptive_learning import AdaptiveLearningEngine
from backend.api.dependencies import get_current_student

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
