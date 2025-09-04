"""
Real Quiz Management Endpoints
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

@router.post("/generate")
async def generate_quiz(
    quiz_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a new AI-powered quiz."""
    try:
        # Extract parameters
        subject = quiz_request.get("subject", "General")
        topic = quiz_request.get("topic", "Introduction")
        difficulty = quiz_request.get("difficulty_level", "intermediate")
        num_questions = quiz_request.get("num_questions", 5)
        quiz_type = quiz_request.get("quiz_type", "multiple_choice")
        
        logger.info(f"Generating quiz for user {current_user.id}: {subject} - {topic}")
        
        # Generate quiz using advanced AI
        quiz_content = await advanced_ai_generator.generate_quiz(
            topic=topic,
            subject=subject,
            num_questions=num_questions,
            difficulty_level=difficulty,
            question_types=[quiz_type] if quiz_type else ["multiple_choice"]
        )
        
        if not quiz_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate quiz content"
            )
        
        # Add metadata
        quiz_data = {
            "quiz_id": f"quiz_{current_user.id}_{hash(f'{subject}_{topic}_{difficulty}')}",
            "user_id": current_user.id,
            "subject": subject,
            "topic": topic,
            "difficulty_level": difficulty,
            "num_questions": num_questions,
            "quiz_type": quiz_type,
            **quiz_content,
            "generated_at": "now",
            "time_limit_minutes": quiz_content.get("time_limit_minutes", num_questions * 2)
        }
        
        return {
            "success": True,
            "quiz": quiz_data,
            "message": f"Successfully generated {difficulty} quiz on {topic} in {subject}"
        }
        
    except Exception as e:
        logger.error(f"Error generating quiz for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate quiz"
        )

@router.post("/submit")
async def submit_quiz(
    submission_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Submit quiz answers and get results."""
    try:
        quiz_data = submission_data.get("quiz_data", {})
        user_answers = submission_data.get("answers", {})
        time_spent = submission_data.get("time_spent_minutes", 10)
        
        if not quiz_data or not user_answers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Quiz data and answers are required"
            )
        
        logger.info(f"Processing quiz submission for user {current_user.id}")
        
        # Grade the quiz
        questions = quiz_data.get("questions", [])
        total_questions = len(questions)
        correct_answers = 0
        incorrect_answers = 0
        detailed_results = []
        
        for i, question in enumerate(questions):
            question_id = str(i)
            user_answer = user_answers.get(question_id, "")
            correct_answer = question.get("correct_answer", "")
            
            is_correct = user_answer.lower().strip() == correct_answer.lower().strip()
            if is_correct:
                correct_answers += 1
            else:
                incorrect_answers += 1
            
            detailed_results.append({
                "question_number": i + 1,
                "question": question.get("question", ""),
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "explanation": question.get("explanation", ""),
                "options": question.get("options", [])
            })
        
        # Calculate results
        accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        attempt_results = {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "incorrect_answers": incorrect_answers,
            "skipped_questions": 0,
            "time_spent_minutes": time_spent,
            "question_details": detailed_results
        }
        
        # Record attempt using progress service
        progress_result = await progress_service.record_quiz_attempt(
            user_id=current_user.id,
            quiz_data=quiz_data,
            attempt_results=attempt_results,
            db=db
        )
        
        return {
            "success": True,
            "results": {
                "accuracy": accuracy,
                "grade": progress_result["grade"],
                "passed": progress_result["passed"],
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "time_spent_minutes": time_spent,
                "detailed_results": detailed_results
            },
            "progress_update": progress_result["updated_progress"],
            "new_achievements": progress_result["new_achievements"],
            "message": f"Quiz completed! You scored {accuracy:.1f}%"
        }
        
    except Exception as e:
        logger.error(f"Error processing quiz submission for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process quiz submission"
        )

@router.get("/history")
async def get_quiz_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get user's quiz attempt history."""
    try:
        from backend.models.user_analytics import QuizAttemptRecord
        
        # Get recent quiz attempts
        attempts = db.query(QuizAttemptRecord).filter(
            QuizAttemptRecord.user_id == current_user.id
        ).order_by(QuizAttemptRecord.completed_at.desc()).limit(limit).all()
        
        history = []
        for attempt in attempts:
            history.append({
                "quiz_id": attempt.quiz_id,
                "subject": attempt.subject,
                "topic": attempt.topic,
                "difficulty_level": attempt.difficulty_level,
                "total_questions": attempt.total_questions,
                "correct_answers": attempt.correct_answers,
                "accuracy_percentage": attempt.accuracy_percentage,
                "grade": attempt.grade,
                "passed": attempt.passed,
                "time_spent_minutes": attempt.time_spent_minutes,
                "completed_at": attempt.completed_at.isoformat()
            })
        
        return {
            "success": True,
            "history": history,
            "total_attempts": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error fetching quiz history for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch quiz history"
        )

@router.get("/statistics")
async def get_quiz_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed quiz statistics for user."""
    try:
        from backend.models.user_analytics import QuizAttemptRecord
        
        # Get all quiz attempts
        all_attempts = db.query(QuizAttemptRecord).filter(
            QuizAttemptRecord.user_id == current_user.id
        ).all()
        
        if not all_attempts:
            return {
                "success": True,
                "statistics": {
                    "total_quizzes": 0,
                    "overall_accuracy": 0,
                    "average_grade": "N/A",
                    "total_questions_answered": 0,
                    "total_time_spent": 0,
                    "subject_breakdown": {},
                    "difficulty_breakdown": {},
                    "recent_trend": "No data"
                }
            }
        
        # Calculate statistics
        total_quizzes = len(all_attempts)
        overall_accuracy = sum(attempt.accuracy_percentage for attempt in all_attempts) / total_quizzes
        total_questions = sum(attempt.total_questions for attempt in all_attempts)
        total_time = sum(attempt.time_spent_minutes for attempt in all_attempts)
        
        # Grade distribution
        grades = [attempt.grade for attempt in all_attempts]
        grade_counts = {}
        for grade in grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        most_common_grade = max(grade_counts, key=grade_counts.get) if grade_counts else "N/A"
        
        # Subject breakdown
        subject_stats = {}
        for attempt in all_attempts:
            subject = attempt.subject
            if subject not in subject_stats:
                subject_stats[subject] = {
                    "attempts": 0,
                    "total_accuracy": 0,
                    "avg_accuracy": 0,
                    "best_score": 0
                }
            
            subject_stats[subject]["attempts"] += 1
            subject_stats[subject]["total_accuracy"] += attempt.accuracy_percentage
            subject_stats[subject]["best_score"] = max(
                subject_stats[subject]["best_score"], 
                attempt.accuracy_percentage
            )
        
        # Calculate averages
        for subject, stats in subject_stats.items():
            stats["avg_accuracy"] = stats["total_accuracy"] / stats["attempts"]
        
        # Difficulty breakdown
        difficulty_stats = {}
        for attempt in all_attempts:
            diff = attempt.difficulty_level
            if diff not in difficulty_stats:
                difficulty_stats[diff] = {
                    "attempts": 0,
                    "avg_accuracy": 0,
                    "total_accuracy": 0
                }
            
            difficulty_stats[diff]["attempts"] += 1
            difficulty_stats[diff]["total_accuracy"] += attempt.accuracy_percentage
        
        # Calculate difficulty averages
        for diff, stats in difficulty_stats.items():
            stats["avg_accuracy"] = stats["total_accuracy"] / stats["attempts"]
        
        # Recent trend (last 5 vs previous 5)
        recent_trend = "stable"
        if total_quizzes >= 10:
            recent_5 = all_attempts[:5]  # Most recent 5
            previous_5 = all_attempts[5:10]  # Previous 5
            
            recent_avg = sum(attempt.accuracy_percentage for attempt in recent_5) / 5
            previous_avg = sum(attempt.accuracy_percentage for attempt in previous_5) / 5
            
            if recent_avg > previous_avg + 5:
                recent_trend = "improving"
            elif recent_avg < previous_avg - 5:
                recent_trend = "declining"
        
        return {
            "success": True,
            "statistics": {
                "total_quizzes": total_quizzes,
                "overall_accuracy": round(overall_accuracy, 1),
                "average_grade": most_common_grade,
                "total_questions_answered": total_questions,
                "total_time_spent_hours": round(total_time / 60, 1),
                "subject_breakdown": {
                    subject: {
                        "attempts": stats["attempts"],
                        "avg_accuracy": round(stats["avg_accuracy"], 1),
                        "best_score": round(stats["best_score"], 1)
                    }
                    for subject, stats in subject_stats.items()
                },
                "difficulty_breakdown": {
                    diff: {
                        "attempts": stats["attempts"],
                        "avg_accuracy": round(stats["avg_accuracy"], 1)
                    }
                    for diff, stats in difficulty_stats.items()
                },
                "grade_distribution": grade_counts,
                "recent_trend": recent_trend
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching quiz statistics for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch quiz statistics"
        )

@router.post("/practice-mode")
async def generate_practice_quiz(
    practice_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a practice quiz based on user's weak areas."""
    try:
        # Get user's progress to identify weak areas
        progress_summary = await progress_service.get_user_progress_summary(current_user.id, db)
        subject_progress = progress_summary.get("subject_progress", {})
        
        # Find subjects/topics that need improvement
        weak_subjects = []
        for subject, stats in subject_progress.items():
            if stats.get("avg_score", 100) < 75:  # Below 75% average
                weak_subjects.append(subject)
        
        # If no weak subjects found, use requested subject or default
        target_subject = practice_request.get("subject")
        if not target_subject and weak_subjects:
            target_subject = weak_subjects[0]
        elif not target_subject:
            target_subject = "Mathematics"  # Default
        
        # Generate targeted practice quiz
        quiz_content = await advanced_ai_generator.generate_quiz(
            subject=target_subject,
            topic=practice_request.get("topic", "Review"),
            difficulty_level="intermediate",  # Good for practice
            num_questions=practice_request.get("num_questions", 10),
            quiz_type="multiple_choice"
        )
        
        if not quiz_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate practice quiz"
            )
        
        quiz_data = {
            "quiz_id": f"practice_{current_user.id}_{hash(f'{target_subject}_practice')}",
            "user_id": current_user.id,
            "subject": target_subject,
            "topic": "Practice Review",
            "difficulty_level": "intermediate",
            "quiz_type": "practice",
            **quiz_content,
            "is_practice": True,
            "based_on_weakness": target_subject in weak_subjects
        }
        
        return {
            "success": True,
            "quiz": quiz_data,
            "message": f"Practice quiz generated for {target_subject}",
            "recommendation": {
                "reason": f"Based on your performance, practicing {target_subject} will help improve your overall scores.",
                "weak_areas": weak_subjects
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating practice quiz for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate practice quiz"
        )
