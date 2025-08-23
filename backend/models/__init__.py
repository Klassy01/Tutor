"""Database models for the AI Personal Tutor system."""

# Import all models to ensure they're available
from .user import User
from .student import Student, StudentProfile
from .learning_session import LearningSession, SessionInteraction
from .content import Content, ContentCategory, LearningObjective
from .progress import Progress, ProgressTracker, EngagementMetrics
from .quiz_attempt import QuizAttempt, QuizQuestionResponse
from .user_analytics import (
    UserProgress, 
    LessonCompletion, 
    QuizAttemptRecord, 
    StudySession, 
    LearningGoal, 
    UserAchievement, 
    WeeklyReport
)

__all__ = [
    "User",
    "Student", 
    "StudentProfile",
    "LearningSession",
    "SessionInteraction", 
    "Content",
    "ContentCategory",
    "LearningObjective",
    "Progress",
    "ProgressTracker",
    "EngagementMetrics",
    "QuizAttempt",
    "QuizQuestionResponse",
    "UserProgress",
    "LessonCompletion", 
    "QuizAttemptRecord", 
    "StudySession", 
    "LearningGoal", 
    "UserAchievement", 
    "WeeklyReport"
]
