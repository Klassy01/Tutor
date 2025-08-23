"""
Quiz API endpoints for quiz attempts and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.models.quiz_attempt import QuizAttempt, QuizQuestionResponse
from backend.models.student import Student
from backend.api.dependencies import get_current_user
from backend.models.user import User

router = APIRouter()

# Pydantic models for request/response
class QuizQuestionCreate(BaseModel):
    question_id: str
    question_text: str
    answer_options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    difficulty_level: Optional[float] = 0.5

class QuizAttemptCreate(BaseModel):
    quiz_title: str
    subject_area: Optional[str] = None
    topic: Optional[str] = None
    difficulty_level: Optional[float] = 0.5
    questions: List[QuizQuestionCreate]

class QuizAnswerSubmit(BaseModel):
    question_id: str
    student_answer: str
    response_time_seconds: Optional[float] = None

class QuizAttemptResponse(BaseModel):
    id: int
    quiz_title: str
    subject_area: Optional[str]
    topic: Optional[str]
    total_questions: int
    correct_answers: int
    accuracy_percentage: float
    status: str
    final_score: Optional[float]
    grade: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

@router.post("/quiz-attempts", response_model=QuizAttemptResponse)
async def create_quiz_attempt(
    quiz_data: QuizAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new quiz attempt for the current user."""
    
    # Get student profile
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        # Create student profile if it doesn't exist
        student = Student(user_id=current_user.id)
        db.add(student)
        db.flush()
    
    # Create quiz attempt
    quiz_attempt = QuizAttempt(
        student_id=student.id,
        quiz_title=quiz_data.quiz_title,
        subject_area=quiz_data.subject_area,
        topic=quiz_data.topic,
        difficulty_level=quiz_data.difficulty_level,
        total_questions=len(quiz_data.questions),
        questions_data=[{
            "question_id": q.question_id,
            "question_text": q.question_text,
            "answer_options": q.answer_options,
            "correct_answer": q.correct_answer,
            "explanation": q.explanation,
            "difficulty_level": q.difficulty_level
        } for q in quiz_data.questions]
    )
    
    db.add(quiz_attempt)
    db.flush()
    
    # Create question responses
    for i, question in enumerate(quiz_data.questions):
        response = QuizQuestionResponse(
            quiz_attempt_id=quiz_attempt.id,
            question_number=i + 1,
            question_id=question.question_id,
            question_text=question.question_text,
            answer_options=question.answer_options,
            correct_answer=question.correct_answer,
            explanation=question.explanation,
            difficulty_level=question.difficulty_level,
            is_correct=False  # Will be updated when answered
        )
        db.add(response)
    
    db.commit()
    db.refresh(quiz_attempt)
    
    return quiz_attempt

@router.get("/quiz-attempts", response_model=List[QuizAttemptResponse])
async def get_quiz_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all quiz attempts for the current user."""
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        return []
    
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == student.id
    ).order_by(QuizAttempt.started_at.desc()).all()
    
    return attempts

@router.get("/quiz-attempts/{attempt_id}", response_model=QuizAttemptResponse)
async def get_quiz_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific quiz attempt."""
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.student_id == student.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    return attempt

@router.post("/quiz-attempts/{attempt_id}/submit-answer")
async def submit_quiz_answer(
    attempt_id: int,
    answer_data: QuizAnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit an answer for a specific question in a quiz attempt."""
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    # Get quiz attempt
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.student_id == student.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    # Get question response
    question_response = db.query(QuizQuestionResponse).filter(
        QuizQuestionResponse.quiz_attempt_id == attempt_id,
        QuizQuestionResponse.question_id == answer_data.question_id
    ).first()
    
    if not question_response:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Submit answer
    is_correct = question_response.submit_answer(
        answer_data.student_answer,
        answer_data.response_time_seconds
    )
    
    # Update quiz attempt statistics
    if is_correct:
        attempt.correct_answers += 1
    else:
        attempt.incorrect_answers += 1
    
    # Calculate progress
    answered_questions = attempt.correct_answers + attempt.incorrect_answers + attempt.skipped_questions
    attempt.completion_percentage = (answered_questions / attempt.total_questions) * 100
    
    # Check if quiz is complete
    if answered_questions >= attempt.total_questions:
        attempt.complete_quiz()
    
    db.commit()
    
    return {
        "is_correct": is_correct,
        "correct_answer": question_response.correct_answer,
        "explanation": question_response.explanation,
        "quiz_completed": attempt.status == "completed",
        "final_score": attempt.final_score if attempt.status == "completed" else None
    }

@router.post("/quiz-attempts/{attempt_id}/complete")
async def complete_quiz_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a quiz attempt as completed."""
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.student_id == student.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    attempt.complete_quiz()
    db.commit()
    
    return {
        "message": "Quiz completed successfully",
        "final_score": attempt.final_score,
        "grade": attempt.grade,
        "passed": attempt.passed
    }

@router.get("/quiz-attempts/{attempt_id}/results")
async def get_quiz_results(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed results for a completed quiz attempt."""
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.student_id == student.id
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz attempt not found")
    
    # Get all question responses
    responses = db.query(QuizQuestionResponse).filter(
        QuizQuestionResponse.quiz_attempt_id == attempt_id
    ).order_by(QuizQuestionResponse.question_number).all()
    
    return {
        "quiz_attempt": attempt,
        "questions_and_answers": [{
            "question_number": r.question_number,
            "question_text": r.question_text,
            "answer_options": r.answer_options,
            "correct_answer": r.correct_answer,
            "student_answer": r.student_answer,
            "is_correct": r.is_correct,
            "explanation": r.explanation,
            "response_time_seconds": r.response_time_seconds
        } for r in responses]
    }
