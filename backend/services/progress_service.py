"""
User Progress Tracking and Analytics Service
"""

from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging

from backend.models.user_analytics import (
    UserProgress, LessonCompletion, QuizAttemptRecord, 
    StudySession, LearningGoal, UserAchievement, WeeklyReport
)
from backend.models.user import User
from backend.core.database import get_db

logger = logging.getLogger(__name__)

class ProgressTrackingService:
    """Service for tracking and analyzing user learning progress."""
    
    def __init__(self):
        self.achievement_definitions = self._load_achievement_definitions()
    
    def _load_achievement_definitions(self) -> Dict[str, Any]:
        """Define available achievements."""
        return {
            "first_lesson": {
                "title": "First Steps",
                "description": "Completed your first lesson",
                "badge_icon": "🎓",
                "badge_color": "green",
                "points": 10
            },
            "quiz_ace": {
                "title": "Quiz Ace",
                "description": "Scored 100% on a quiz",
                "badge_icon": "🏆",
                "badge_color": "gold",
                "points": 25
            },
            "week_streak": {
                "title": "Week Warrior",
                "description": "Maintained a 7-day learning streak",
                "badge_icon": "🔥",
                "badge_color": "orange",
                "points": 50
            },
            "subject_master": {
                "title": "Subject Master",
                "description": "Completed 10 lessons in one subject",
                "badge_icon": "🎯",
                "badge_color": "purple",
                "points": 75
            },
            "speed_learner": {
                "title": "Speed Learner",
                "description": "Completed 5 lessons in one day",
                "badge_icon": "⚡",
                "badge_color": "blue",
                "points": 30
            }
        }
    
    async def get_or_create_user_progress(self, user_id: int, db: Session) -> UserProgress:
        """Get existing user progress or create new one."""
        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        
        if not progress:
            progress = UserProgress(user_id=user_id)
            db.add(progress)
            db.commit()
            db.refresh(progress)
            logger.info(f"Created new progress tracking for user {user_id}")
        
        return progress
    
    async def record_lesson_completion(
        self, 
        user_id: int,
        lesson_data: Dict[str, Any],
        time_spent: int,
        db: Session
    ) -> Dict[str, Any]:
        """Record a completed lesson and update progress."""
        
        # Get or create user progress
        progress = await self.get_or_create_user_progress(user_id, db)
        
        # Record lesson completion
        completion = LessonCompletion(
            user_progress_id=progress.id,
            user_id=user_id,
            lesson_id=lesson_data.get("id", "unknown"),
            subject=lesson_data.get("subject", "General"),
            topic=lesson_data.get("topic", "Unknown"),
            difficulty_level=lesson_data.get("difficulty_level", "intermediate"),
            time_spent_minutes=time_spent,
            completion_percentage=100.0,
            started_at=datetime.utcnow() - timedelta(minutes=time_spent),
            completed_at=datetime.utcnow()
        )
        
        db.add(completion)
        
        # Update progress stats
        progress.total_lessons_completed += 1
        progress.total_study_time_minutes += time_spent
        progress.last_activity_date = datetime.utcnow()
        
        # Update subject progress
        subject = lesson_data.get("subject", "General")
        if not progress.subject_progress:
            progress.subject_progress = {}
        
        if subject not in progress.subject_progress:
            progress.subject_progress[subject] = {"lessons": 0, "quizzes": 0, "avg_score": 0}
        
        progress.subject_progress[subject]["lessons"] += 1
        
        # Update streak
        await self._update_learning_streak(progress, db)
        
        db.commit()
        
        # Check for achievements
        achievements = await self._check_lesson_achievements(user_id, progress, db)
        
        return {
            "completion_recorded": True,
            "total_lessons": progress.total_lessons_completed,
            "new_achievements": achievements,
            "updated_progress": await self.get_user_progress_summary(user_id, db)
        }
    
    async def record_quiz_attempt(
        self,
        user_id: int,
        quiz_data: Dict[str, Any],
        attempt_results: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Record a quiz attempt and update progress."""
        
        progress = await self.get_or_create_user_progress(user_id, db)
        
        # Calculate metrics
        accuracy = (attempt_results["correct_answers"] / attempt_results["total_questions"]) * 100
        time_spent = attempt_results.get("time_spent_minutes", 10)
        avg_time_per_question = time_spent / attempt_results["total_questions"]
        
        # Determine grade
        grade = self._calculate_grade(accuracy)
        passed = accuracy >= 60.0
        
        # Record quiz attempt
        attempt_record = QuizAttemptRecord(
            user_progress_id=progress.id,
            user_id=user_id,
            quiz_id=quiz_data.get("quiz_id", "unknown"),
            subject=quiz_data.get("subject", "General"),
            topic=quiz_data.get("topic", "Unknown"),
            difficulty_level=quiz_data.get("difficulty_level", "intermediate"),
            total_questions=attempt_results["total_questions"],
            correct_answers=attempt_results["correct_answers"],
            incorrect_answers=attempt_results["incorrect_answers"],
            skipped_questions=attempt_results.get("skipped_questions", 0),
            accuracy_percentage=accuracy,
            time_spent_minutes=time_spent,
            average_time_per_question=avg_time_per_question,
            final_score=accuracy,
            grade=grade,
            passed=passed,
            question_results=attempt_results.get("question_details", {}),
            started_at=datetime.utcnow() - timedelta(minutes=time_spent),
            completed_at=datetime.utcnow()
        )
        
        db.add(attempt_record)
        
        # Update progress stats
        progress.total_quizzes_taken += 1
        progress.total_study_time_minutes += time_spent
        progress.last_activity_date = datetime.utcnow()
        
        # Update overall accuracy (weighted average)
        total_questions_ever = progress.total_quizzes_taken * 5  # Estimate
        current_total_correct = (progress.overall_accuracy / 100) * (total_questions_ever - attempt_results["total_questions"])
        new_total_correct = current_total_correct + attempt_results["correct_answers"]
        progress.overall_accuracy = (new_total_correct / total_questions_ever) * 100
        
        # Update subject progress
        subject = quiz_data.get("subject", "General")
        if not progress.subject_progress:
            progress.subject_progress = {}
        
        if subject not in progress.subject_progress:
            progress.subject_progress[subject] = {"lessons": 0, "quizzes": 0, "avg_score": 0}
        
        current_quizzes = progress.subject_progress[subject]["quizzes"]
        current_avg = progress.subject_progress[subject]["avg_score"]
        new_avg = ((current_avg * current_quizzes) + accuracy) / (current_quizzes + 1)
        
        progress.subject_progress[subject]["quizzes"] += 1
        progress.subject_progress[subject]["avg_score"] = new_avg
        
        db.commit()
        
        # Check for achievements
        achievements = await self._check_quiz_achievements(user_id, progress, accuracy, db)
        
        return {
            "attempt_recorded": True,
            "accuracy": accuracy,
            "grade": grade,
            "passed": passed,
            "new_achievements": achievements,
            "updated_progress": await self.get_user_progress_summary(user_id, db)
        }
    
    async def get_user_progress_summary(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Get comprehensive progress summary for user."""
        progress = await self.get_or_create_user_progress(user_id, db)
        
        # Get recent completions
        recent_lessons = db.query(LessonCompletion).filter(
            LessonCompletion.user_id == user_id
        ).order_by(LessonCompletion.completed_at.desc()).limit(5).all()
        
        recent_quizzes = db.query(QuizAttemptRecord).filter(
            QuizAttemptRecord.user_id == user_id
        ).order_by(QuizAttemptRecord.completed_at.desc()).limit(5).all()
        
        # Get achievements
        achievements = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).order_by(UserAchievement.earned_at.desc()).all()
        
        # Calculate learning velocity (lessons per week)
        if progress.total_lessons_completed > 0:
            days_since_start = (datetime.utcnow() - progress.created_at).days
            weeks_active = max(days_since_start / 7, 1)
            learning_velocity = progress.total_lessons_completed / weeks_active
        else:
            learning_velocity = 0
        
        return {
            "user_id": user_id,
            "overall_stats": {
                "total_lessons_completed": progress.total_lessons_completed,
                "total_quizzes_taken": progress.total_quizzes_taken,
                "total_study_time_hours": round(progress.total_study_time_minutes / 60, 1),
                "current_streak_days": progress.current_streak_days,
                "overall_accuracy": round(progress.overall_accuracy, 1),
                "learning_velocity": round(learning_velocity, 2)
            },
            "subject_progress": progress.subject_progress or {},
            "recent_activity": {
                "lessons": [
                    {
                        "subject": lesson.subject,
                        "topic": lesson.topic,
                        "completed_at": lesson.completed_at.isoformat(),
                        "time_spent": lesson.time_spent_minutes
                    } for lesson in recent_lessons
                ],
                "quizzes": [
                    {
                        "subject": quiz.subject,
                        "topic": quiz.topic,
                        "accuracy": quiz.accuracy_percentage,
                        "grade": quiz.grade,
                        "completed_at": quiz.completed_at.isoformat()
                    } for quiz in recent_quizzes
                ]
            },
            "achievements": [
                {
                    "title": achievement.title,
                    "description": achievement.description,
                    "badge_icon": achievement.badge_icon,
                    "earned_at": achievement.earned_at.isoformat(),
                    "points": achievement.points_earned
                } for achievement in achievements
            ],
            "total_points": sum(a.points_earned for a in achievements)
        }
    
    async def get_detailed_analytics(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Get detailed learning analytics for dashboard."""
        progress = await self.get_or_create_user_progress(user_id, db)
        
        # Weekly progress for the last 8 weeks
        weekly_data = []
        for week in range(8, 0, -1):
            week_start = datetime.utcnow() - timedelta(weeks=week)
            week_end = week_start + timedelta(days=7)
            
            week_lessons = db.query(LessonCompletion).filter(
                LessonCompletion.user_id == user_id,
                LessonCompletion.completed_at >= week_start,
                LessonCompletion.completed_at < week_end
            ).count()
            
            week_quizzes = db.query(QuizAttemptRecord).filter(
                QuizAttemptRecord.user_id == user_id,
                QuizAttemptRecord.completed_at >= week_start,
                QuizAttemptRecord.completed_at < week_end
            ).all()
            
            week_avg_score = sum(q.accuracy_percentage for q in week_quizzes) / len(week_quizzes) if week_quizzes else 0
            
            weekly_data.append({
                "week": week_start.strftime("%Y-%m-%d"),
                "lessons": week_lessons,
                "quizzes": len(week_quizzes),
                "avg_score": round(week_avg_score, 1)
            })
        
        # Subject performance breakdown
        subject_stats = {}
        for subject, stats in (progress.subject_progress or {}).items():
            lessons = db.query(LessonCompletion).filter(
                LessonCompletion.user_id == user_id,
                LessonCompletion.subject == subject
            ).all()
            
            quizzes = db.query(QuizAttemptRecord).filter(
                QuizAttemptRecord.user_id == user_id,
                QuizAttemptRecord.subject == subject
            ).all()
            
            total_time = sum(l.time_spent_minutes for l in lessons)
            avg_accuracy = sum(q.accuracy_percentage for q in quizzes) / len(quizzes) if quizzes else 0
            
            subject_stats[subject] = {
                "lessons_completed": len(lessons),
                "quizzes_taken": len(quizzes),
                "total_time_minutes": total_time,
                "average_accuracy": round(avg_accuracy, 1),
                "improvement_trend": "stable"  # Could calculate actual trend
            }
        
        return {
            "weekly_progress": weekly_data,
            "subject_performance": subject_stats,
            "learning_patterns": {
                "most_active_day": "Monday",  # Could calculate from actual data
                "preferred_study_time": "Evening",  # Could calculate from timestamps
                "average_session_length": progress.total_study_time_minutes // max(progress.total_lessons_completed, 1),
                "consistency_score": min(progress.current_streak_days * 10, 100)
            },
            "recommendations": self._generate_recommendations(progress, subject_stats)
        }
    
    def _calculate_grade(self, accuracy: float) -> str:
        """Calculate letter grade from accuracy percentage."""
        if accuracy >= 97: return "A+"
        elif accuracy >= 93: return "A"
        elif accuracy >= 90: return "A-"
        elif accuracy >= 87: return "B+"
        elif accuracy >= 83: return "B"
        elif accuracy >= 80: return "B-"
        elif accuracy >= 77: return "C+"
        elif accuracy >= 73: return "C"
        elif accuracy >= 70: return "C-"
        elif accuracy >= 67: return "D+"
        elif accuracy >= 65: return "D"
        else: return "F"
    
    async def _update_learning_streak(self, progress: UserProgress, db: Session):
        """Update learning streak based on activity."""
        today = datetime.utcnow().date()
        last_activity = progress.last_activity_date.date() if progress.last_activity_date else today
        
        days_diff = (today - last_activity).days
        
        if days_diff == 0:  # Activity today
            pass  # Keep current streak
        elif days_diff == 1:  # Activity yesterday, increment streak
            progress.current_streak_days += 1
            if progress.current_streak_days > progress.longest_streak_days:
                progress.longest_streak_days = progress.current_streak_days
        else:  # Streak broken
            progress.current_streak_days = 1
    
    async def _check_lesson_achievements(self, user_id: int, progress: UserProgress, db: Session) -> List[Dict]:
        """Check and award lesson-related achievements."""
        new_achievements = []
        
        # First lesson achievement
        if progress.total_lessons_completed == 1:
            achievement = await self._award_achievement(user_id, "first_lesson", db)
            if achievement:
                new_achievements.append(achievement)
        
        # Subject master achievement (10 lessons in one subject)
        for subject, stats in (progress.subject_progress or {}).items():
            if stats.get("lessons", 0) == 10:
                achievement_data = {
                    "subject": subject,
                    "lessons_completed": 10
                }
                achievement = await self._award_achievement(
                    user_id, "subject_master", db, achievement_data
                )
                if achievement:
                    new_achievements.append(achievement)
        
        # Speed learner (5 lessons in one day)
        today_lessons = db.query(LessonCompletion).filter(
            LessonCompletion.user_id == user_id,
            LessonCompletion.completed_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count()
        
        if today_lessons == 5:
            achievement = await self._award_achievement(user_id, "speed_learner", db)
            if achievement:
                new_achievements.append(achievement)
        
        return new_achievements
    
    async def _check_quiz_achievements(self, user_id: int, progress: UserProgress, accuracy: float, db: Session) -> List[Dict]:
        """Check and award quiz-related achievements."""
        new_achievements = []
        
        # Perfect score achievement
        if accuracy == 100.0:
            achievement = await self._award_achievement(user_id, "quiz_ace", db)
            if achievement:
                new_achievements.append(achievement)
        
        return new_achievements
    
    async def _award_achievement(self, user_id: int, achievement_key: str, db: Session, data: Dict = None) -> Optional[Dict]:
        """Award an achievement to a user if they haven't earned it yet."""
        # Check if already earned
        existing = db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_type == achievement_key
        ).first()
        
        if existing:
            return None  # Already earned
        
        # Get achievement definition
        definition = self.achievement_definitions.get(achievement_key)
        if not definition:
            return None
        
        # Create achievement
        achievement = UserAchievement(
            user_id=user_id,
            achievement_type=achievement_key,
            title=definition["title"],
            description=definition["description"],
            badge_icon=definition["badge_icon"],
            badge_color=definition["badge_color"],
            points_earned=definition["points"],
            achievement_data=data or {}
        )
        
        db.add(achievement)
        db.commit()
        
        logger.info(f"Awarded achievement '{achievement_key}' to user {user_id}")
        
        return {
            "title": achievement.title,
            "description": achievement.description,
            "badge_icon": achievement.badge_icon,
            "points": achievement.points_earned
        }
    
    def _generate_recommendations(self, progress: UserProgress, subject_stats: Dict) -> List[str]:
        """Generate personalized learning recommendations."""
        recommendations = []
        
        if progress.current_streak_days >= 7:
            recommendations.append("🔥 Keep up your amazing streak! You're on fire!")
        elif progress.current_streak_days == 0:
            recommendations.append("📚 Let's get back into the learning habit. Start with a quick lesson today!")
        
        if progress.overall_accuracy < 70:
            recommendations.append("🎯 Focus on reviewing concepts before taking quizzes to improve your accuracy.")
        elif progress.overall_accuracy > 90:
            recommendations.append("🚀 Excellent performance! Consider trying more challenging topics.")
        
        # Subject-specific recommendations
        if subject_stats:
            weakest_subject = min(subject_stats.items(), key=lambda x: x[1]["average_accuracy"])
            if weakest_subject[1]["average_accuracy"] < 80:
                recommendations.append(f"📖 Consider spending more time on {weakest_subject[0]} - review the basics!")
        
        if not recommendations:
            recommendations.append("✨ You're doing great! Keep exploring new topics and challenging yourself.")
        
        return recommendations

# Global instance
progress_service = ProgressTrackingService()
