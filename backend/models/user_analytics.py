"""
User Progress and Learning Analytics Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from backend.core.database import Base

class UserProgress(Base):
    """Track detailed user learning progress."""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Overall Statistics
    total_lessons_completed = Column(Integer, default=0)
    total_quizzes_taken = Column(Integer, default=0)
    total_study_time_minutes = Column(Integer, default=0)
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    last_activity_date = Column(DateTime, default=datetime.utcnow)
    
    # Performance Metrics
    overall_accuracy = Column(Float, default=0.0)  # Percentage
    average_quiz_score = Column(Float, default=0.0)
    preferred_difficulty = Column(String(20), default="intermediate")
    
    # Subject-wise Progress (JSON)
    subject_progress = Column(JSON, default=dict)  # {"math": {"completed": 5, "avg_score": 85}, ...}
    
    # Learning Analytics
    learning_velocity = Column(Float, default=0.0)  # Lessons per week
    retention_rate = Column(Float, default=0.0)    # How well they remember
    engagement_score = Column(Float, default=0.0)  # Overall engagement
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    lesson_completions = relationship("LessonCompletion", back_populates="user_progress")
    quiz_attempts = relationship("QuizAttemptRecord", back_populates="user_progress")

class LessonCompletion(Base):
    """Track individual lesson completions."""
    __tablename__ = "lesson_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Lesson Details
    lesson_id = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    difficulty_level = Column(String(20), nullable=False)
    
    # Completion Stats
    time_spent_minutes = Column(Integer, nullable=False)
    completion_percentage = Column(Float, default=100.0)
    notes = Column(Text, nullable=True)
    
    # Performance
    understanding_rating = Column(Integer, nullable=True)  # 1-5 scale
    liked = Column(Boolean, default=None)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    user_progress = relationship("UserProgress", back_populates="lesson_completions")

class QuizAttemptRecord(Base):
    """Detailed quiz attempt records."""
    __tablename__ = "quiz_attempt_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_progress_id = Column(Integer, ForeignKey("user_progress.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Quiz Details
    quiz_id = Column(String(100), nullable=False)
    subject = Column(String(100), nullable=False)
    topic = Column(String(200), nullable=False)
    difficulty_level = Column(String(20), nullable=False)
    
    # Attempt Results
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    incorrect_answers = Column(Integer, nullable=False)
    skipped_questions = Column(Integer, default=0)
    
    # Performance Metrics
    accuracy_percentage = Column(Float, nullable=False)
    time_spent_minutes = Column(Integer, nullable=False)
    average_time_per_question = Column(Float, nullable=False)
    
    # Scoring
    final_score = Column(Float, nullable=False)
    grade = Column(String(2), nullable=True)  # A, B, C, D, F
    passed = Column(Boolean, nullable=False)
    
    # Detailed Results (JSON)
    question_results = Column(JSON, nullable=False)  # Detailed question-by-question results
    
    # Timestamps
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    user_progress = relationship("UserProgress", back_populates="quiz_attempts")

class StudySession(Base):
    """Track study sessions for analytics."""
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session Details
    session_type = Column(String(50), nullable=False)  # lesson, quiz, practice, review
    subject = Column(String(100), nullable=True)
    topics_covered = Column(JSON, nullable=True)  # List of topics
    
    # Duration and Engagement
    duration_minutes = Column(Integer, nullable=False)
    activities_completed = Column(Integer, default=0)
    engagement_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Performance
    accuracy_rate = Column(Float, nullable=True)
    improvement_rate = Column(Float, nullable=True)
    
    # Context
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    location_context = Column(String(100), nullable=True)  # home, school, library
    
    # Timestamps
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class LearningGoal(Base):
    """User-defined learning goals and tracking."""
    __tablename__ = "learning_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Goal Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(100), nullable=False)
    target_topics = Column(JSON, nullable=False)  # List of topics to master
    
    # Progress Tracking
    target_completion_date = Column(DateTime, nullable=True)
    current_progress_percentage = Column(Float, default=0.0)
    status = Column(String(20), default="active")  # active, completed, paused, cancelled
    
    # Metrics
    lessons_to_complete = Column(Integer, default=0)
    lessons_completed = Column(Integer, default=0)
    quizzes_to_pass = Column(Integer, default=0)
    quizzes_passed = Column(Integer, default=0)
    target_accuracy = Column(Float, default=80.0)
    current_accuracy = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")

class UserAchievement(Base):
    """User achievements and badges."""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Achievement Details
    achievement_type = Column(String(50), nullable=False)  # streak, accuracy, completion, speed
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    badge_icon = Column(String(100), nullable=True)
    badge_color = Column(String(20), nullable=True)
    
    # Achievement Data
    achievement_data = Column(JSON, nullable=True)  # Flexible data for different achievements
    points_earned = Column(Integer, default=0)
    rarity = Column(String(20), default="common")  # common, rare, epic, legendary
    
    # Timestamps
    earned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class WeeklyReport(Base):
    """Automated weekly progress reports."""
    __tablename__ = "weekly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Report Period
    week_start_date = Column(DateTime, nullable=False)
    week_end_date = Column(DateTime, nullable=False)
    
    # Weekly Stats
    lessons_completed = Column(Integer, default=0)
    quizzes_taken = Column(Integer, default=0)
    total_study_time = Column(Integer, default=0)  # in minutes
    average_quiz_score = Column(Float, default=0.0)
    subjects_studied = Column(JSON, default=list)
    
    # Progress Metrics
    week_over_week_improvement = Column(Float, default=0.0)
    streak_maintained = Column(Boolean, default=False)
    goals_progress = Column(JSON, default=dict)
    
    # Insights (JSON)
    strengths = Column(JSON, default=list)  # Areas where user performed well
    areas_for_improvement = Column(JSON, default=list)  # Areas needing focus
    recommended_actions = Column(JSON, default=list)  # Specific recommendations
    
    # Generated Report
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
