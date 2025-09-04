"""
Dashboard Analytics Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging

from backend.api.dependencies import get_current_user
from backend.core.database import get_db
from backend.services.progress_service import progress_service
from backend.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get complete dashboard overview with all user analytics."""
    try:
        logger.info(f"Fetching dashboard overview for user {current_user.id}")
        
        # Get comprehensive progress summary
        progress_summary = await progress_service.get_user_progress_summary(current_user.id, db)
        
        # Get detailed analytics
        detailed_analytics = await progress_service.get_detailed_analytics(current_user.id, db)
        
        return {
            "success": True,
            "user_info": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email,
                "member_since": current_user.created_at.isoformat()
            },
            "progress_summary": progress_summary,
            "analytics": detailed_analytics,
            "quick_stats": {
                "total_lessons": progress_summary["overall_stats"]["total_lessons_completed"],
                "total_quizzes": progress_summary["overall_stats"]["total_quizzes_taken"],
                "study_hours": progress_summary["overall_stats"]["total_study_time_hours"],
                "current_streak": progress_summary["overall_stats"]["current_streak_days"],
                "overall_accuracy": progress_summary["overall_stats"]["overall_accuracy"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard overview for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch dashboard overview"
        )

@router.get("/progress-chart")
async def get_progress_chart_data(
    timeframe: str = "month",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get progress chart data for visualization."""
    try:
        from backend.models.user_analytics import LessonCompletion, QuizAttemptRecord
        from datetime import datetime, timedelta
        
        # Determine time range
        if timeframe == "week":
            start_date = datetime.utcnow() - timedelta(days=7)
            interval = "day"
        elif timeframe == "month":
            start_date = datetime.utcnow() - timedelta(days=30)
            interval = "day"
        elif timeframe == "year":
            start_date = datetime.utcnow() - timedelta(days=365)
            interval = "week"
        else:
            start_date = datetime.utcnow() - timedelta(days=30)
            interval = "day"
        
        # Get lessons and quizzes in timeframe
        lessons = db.query(LessonCompletion).filter(
            LessonCompletion.user_id == current_user.id,
            LessonCompletion.completed_at >= start_date
        ).all()
        
        quizzes = db.query(QuizAttemptRecord).filter(
            QuizAttemptRecord.user_id == current_user.id,
            QuizAttemptRecord.completed_at >= start_date
        ).all()
        
        # Group by time interval
        chart_data = []
        current_date = start_date
        
        while current_date <= datetime.utcnow():
            if interval == "day":
                end_date = current_date + timedelta(days=1)
                date_label = current_date.strftime("%Y-%m-%d")
            else:  # week
                end_date = current_date + timedelta(days=7)
                date_label = current_date.strftime("%Y-W%W")
            
            # Count activities in this period
            period_lessons = [l for l in lessons if current_date <= l.completed_at < end_date]
            period_quizzes = [q for q in quizzes if current_date <= q.completed_at < end_date]
            
            avg_quiz_score = sum(q.accuracy_percentage for q in period_quizzes) / len(period_quizzes) if period_quizzes else 0
            
            chart_data.append({
                "date": date_label,
                "lessons": len(period_lessons),
                "quizzes": len(period_quizzes),
                "avg_score": round(avg_quiz_score, 1),
                "study_time": sum(l.time_spent_minutes for l in period_lessons) + sum(q.time_spent_minutes for q in period_quizzes)
            })
            
            current_date = end_date
        
        return {
            "success": True,
            "timeframe": timeframe,
            "chart_data": chart_data,
            "summary": {
                "total_lessons": len(lessons),
                "total_quizzes": len(quizzes),
                "avg_score": round(sum(q.accuracy_percentage for q in quizzes) / len(quizzes), 1) if quizzes else 0,
                "total_study_minutes": sum(l.time_spent_minutes for l in lessons) + sum(q.time_spent_minutes for q in quizzes)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching progress chart data for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch progress chart data"
        )

@router.get("/subject-breakdown")
async def get_subject_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed breakdown by subject."""
    try:
        from backend.models.user_analytics import LessonCompletion, QuizAttemptRecord
        
        # Get all user activities
        lessons = db.query(LessonCompletion).filter(
            LessonCompletion.user_id == current_user.id
        ).all()
        
        quizzes = db.query(QuizAttemptRecord).filter(
            QuizAttemptRecord.user_id == current_user.id
        ).all()
        
        # Group by subject
        subjects = {}
        
        for lesson in lessons:
            subject = lesson.subject
            if subject not in subjects:
                subjects[subject] = {
                    "lessons": 0,
                    "quizzes": 0,
                    "total_time_minutes": 0,
                    "quiz_scores": [],
                    "topics": set()
                }
            
            subjects[subject]["lessons"] += 1
            subjects[subject]["total_time_minutes"] += lesson.time_spent_minutes
            subjects[subject]["topics"].add(lesson.topic)
        
        for quiz in quizzes:
            subject = quiz.subject
            if subject not in subjects:
                subjects[subject] = {
                    "lessons": 0,
                    "quizzes": 0,
                    "total_time_minutes": 0,
                    "quiz_scores": [],
                    "topics": set()
                }
            
            subjects[subject]["quizzes"] += 1
            subjects[subject]["total_time_minutes"] += quiz.time_spent_minutes
            subjects[subject]["quiz_scores"].append(quiz.accuracy_percentage)
            subjects[subject]["topics"].add(quiz.topic)
        
        # Calculate averages and format
        formatted_subjects = []
        for subject, data in subjects.items():
            avg_score = sum(data["quiz_scores"]) / len(data["quiz_scores"]) if data["quiz_scores"] else 0
            
            formatted_subjects.append({
                "subject": subject,
                "lessons_completed": data["lessons"],
                "quizzes_taken": data["quizzes"],
                "avg_quiz_score": round(avg_score, 1),
                "total_time_hours": round(data["total_time_minutes"] / 60, 1),
                "topics_studied": len(data["topics"]),
                "topic_list": list(data["topics"])
            })
        
        # Sort by total activity
        formatted_subjects.sort(key=lambda x: x["lessons_completed"] + x["quizzes_taken"], reverse=True)
        
        return {
            "success": True,
            "subjects": formatted_subjects,
            "total_subjects": len(formatted_subjects)
        }
        
    except Exception as e:
        logger.error(f"Error fetching subject breakdown for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subject breakdown"
        )

@router.get("/achievements")
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get all user achievements and available achievements."""
    try:
        from backend.models.user_analytics import UserAchievement
        
        # Get earned achievements
        earned_achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == current_user.id
        ).order_by(UserAchievement.earned_at.desc()).all()
        
        # Get progress summary to check for new achievements
        progress_summary = await progress_service.get_user_progress_summary(current_user.id, db)
        
        # Available achievements (not yet earned)
        available_achievements = []
        earned_types = {a.achievement_type for a in earned_achievements}
        
        all_achievement_types = {
            "first_lesson": {"title": "First Steps", "description": "Complete your first lesson", "points": 10},
            "quiz_ace": {"title": "Quiz Ace", "description": "Score 100% on a quiz", "points": 25},
            "week_streak": {"title": "Week Warrior", "description": "Maintain a 7-day learning streak", "points": 50},
            "subject_master": {"title": "Subject Master", "description": "Complete 10 lessons in one subject", "points": 75},
            "speed_learner": {"title": "Speed Learner", "description": "Complete 5 lessons in one day", "points": 30}
        }
        
        for achievement_type, details in all_achievement_types.items():
            if achievement_type not in earned_types:
                # Check progress toward achievement
                progress = 0
                target = 1
                
                if achievement_type == "first_lesson":
                    progress = min(progress_summary["overall_stats"]["total_lessons_completed"], 1)
                elif achievement_type == "week_streak":
                    progress = progress_summary["overall_stats"]["current_streak_days"]
                    target = 7
                elif achievement_type == "subject_master":
                    max_subject_lessons = max(
                        stats.get("lessons", 0) 
                        for stats in progress_summary.get("subject_progress", {}).values()
                    ) if progress_summary.get("subject_progress") else 0
                    progress = min(max_subject_lessons, 10)
                    target = 10
                
                available_achievements.append({
                    "achievement_type": achievement_type,
                    "title": details["title"],
                    "description": details["description"],
                    "points": details["points"],
                    "progress": progress,
                    "target": target,
                    "progress_percentage": min((progress / target) * 100, 100)
                })
        
        # Format earned achievements
        earned_formatted = [
            {
                "achievement_type": a.achievement_type,
                "title": a.title,
                "description": a.description,
                "badge_icon": a.badge_icon,
                "badge_color": a.badge_color,
                "points": a.points_earned,
                "earned_at": a.earned_at.isoformat()
            }
            for a in earned_achievements
        ]
        
        total_points = sum(a.points_earned for a in earned_achievements)
        
        return {
            "success": True,
            "earned_achievements": earned_formatted,
            "available_achievements": available_achievements,
            "total_points": total_points,
            "achievements_count": len(earned_achievements)
        }
        
    except Exception as e:
        logger.error(f"Error fetching achievements for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch achievements"
        )

@router.get("/learning-streaks")
async def get_learning_streaks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get learning streak information and calendar."""
    try:
        from backend.models.user_analytics import LessonCompletion, QuizAttemptRecord
        from datetime import datetime, timedelta
        
        # Get activity for the last 90 days
        start_date = datetime.utcnow() - timedelta(days=90)
        
        lessons = db.query(LessonCompletion).filter(
            LessonCompletion.user_id == current_user.id,
            LessonCompletion.completed_at >= start_date
        ).all()
        
        quizzes = db.query(QuizAttemptRecord).filter(
            QuizAttemptRecord.user_id == current_user.id,
            QuizAttemptRecord.completed_at >= start_date
        ).all()
        
        # Create activity calendar
        activity_by_date = {}
        
        for lesson in lessons:
            date_str = lesson.completed_at.date().isoformat()
            if date_str not in activity_by_date:
                activity_by_date[date_str] = {"lessons": 0, "quizzes": 0}
            activity_by_date[date_str]["lessons"] += 1
        
        for quiz in quizzes:
            date_str = quiz.completed_at.date().isoformat()
            if date_str not in activity_by_date:
                activity_by_date[date_str] = {"lessons": 0, "quizzes": 0}
            activity_by_date[date_str]["quizzes"] += 1
        
        # Calculate streaks
        current_date = datetime.utcnow().date()
        current_streak = 0
        longest_streak = 0
        temp_streak = 0
        
        # Check last 365 days for streak calculation
        for i in range(365):
            check_date = current_date - timedelta(days=i)
            date_str = check_date.isoformat()
            
            if date_str in activity_by_date:
                temp_streak += 1
                if i == 0 or (current_date - check_date).days <= current_streak + 1:
                    current_streak = temp_streak
            else:
                longest_streak = max(longest_streak, temp_streak)
                temp_streak = 0
                
                # Break current streak if today has no activity
                if i == 0:
                    current_streak = 0
        
        longest_streak = max(longest_streak, temp_streak, current_streak)
        
        # Create calendar data for last 90 days
        calendar_data = []
        for i in range(90):
            date = current_date - timedelta(days=89 - i)
            date_str = date.isoformat()
            
            activity = activity_by_date.get(date_str, {"lessons": 0, "quizzes": 0})
            total_activity = activity["lessons"] + activity["quizzes"]
            
            calendar_data.append({
                "date": date_str,
                "lessons": activity["lessons"],
                "quizzes": activity["quizzes"],
                "total_activity": total_activity,
                "has_activity": total_activity > 0
            })
        
        return {
            "success": True,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "active_days_last_90": len([d for d in calendar_data if d["has_activity"]]),
            "calendar_data": calendar_data,
            "streak_stats": {
                "total_active_days": len(activity_by_date),
                "consistency_rate": round((len([d for d in calendar_data if d["has_activity"]]) / 90) * 100, 1),
                "average_daily_lessons": round(sum(d["lessons"] for d in calendar_data) / 90, 2),
                "average_daily_quizzes": round(sum(d["quizzes"] for d in calendar_data) / 90, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching learning streaks for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch learning streaks"
        )
