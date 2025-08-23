"""
Student model and profile for personalized learning.

Defines student-specific information, learning preferences, and
adaptive learning algorithm parameters.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Student(Base):
    """
    Student profile with learning preferences and adaptive parameters.
    
    Extends the base User with student-specific information needed
    for personalized learning and adaptive algorithms.
    """
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Academic information
    grade_level = Column(String(20), nullable=True)  # e.g., "9th", "college", "adult"
    academic_goals = Column(Text, nullable=True)
    subjects_of_interest = Column(JSON, nullable=True)  # List of subjects
    
    # Learning preferences
    learning_style = Column(String(50), nullable=True)  # visual, auditory, kinesthetic, etc.
    preferred_difficulty = Column(Float, default=0.5)  # 0.0 to 1.0
    pace_preference = Column(String(20), default="medium")  # slow, medium, fast
    
    # Adaptive learning parameters
    current_difficulty_level = Column(Float, default=0.5)
    knowledge_level = Column(Float, default=0.0)  # Overall knowledge assessment
    engagement_score = Column(Float, default=0.5)  # Engagement tracking
    
    # Performance metrics
    total_study_time = Column(Integer, default=0)  # in minutes
    sessions_completed = Column(Integer, default=0)
    average_session_duration = Column(Float, default=0.0)  # in minutes
    
    # Achievements and progress
    points_earned = Column(Integer, default=0)
    badges_earned = Column(JSON, nullable=True)  # List of badge IDs
    current_streak = Column(Integer, default=0)  # consecutive days
    longest_streak = Column(Integer, default=0)
    
    # Preferences and settings
    reminder_enabled = Column(Boolean, default=True)
    notification_preferences = Column(JSON, nullable=True)
    study_schedule = Column(JSON, nullable=True)  # Preferred study times
    
    # AI tutor interaction preferences
    tutor_personality = Column(String(50), default="friendly")  # friendly, professional, casual
    feedback_frequency = Column(String(20), default="moderate")  # low, moderate, high
    hint_preference = Column(String(20), default="progressive")  # immediate, progressive, minimal
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_active = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="student_profile")
    learning_sessions = relationship("LearningSession", back_populates="student")
    progress_records = relationship("Progress", back_populates="student")
    engagement_metrics = relationship("EngagementMetrics", back_populates="student")
    
    def __repr__(self):
        return f"<Student(id={self.id}, user_id={self.user_id}, level={self.current_difficulty_level})>"
    
    def update_difficulty_level(self, performance_score: float, adjustment_rate: float = 0.1):
        """
        Update difficulty level based on performance.
        
        Args:
            performance_score: Score from 0.0 (poor) to 1.0 (excellent)
            adjustment_rate: How quickly to adjust difficulty
        """
        if performance_score > 0.8:
            # Increase difficulty if performing well
            self.current_difficulty_level = min(
                1.0, 
                self.current_difficulty_level + adjustment_rate
            )
        elif performance_score < 0.4:
            # Decrease difficulty if struggling
            self.current_difficulty_level = max(
                0.1, 
                self.current_difficulty_level - adjustment_rate
            )
        # No change for moderate performance (0.4-0.8)
    
    def add_study_time(self, minutes: int):
        """Add study time and update session statistics."""
        self.total_study_time += minutes
        self.sessions_completed += 1
        self.average_session_duration = self.total_study_time / self.sessions_completed
    
    def award_points(self, points: int):
        """Award points for achievements."""
        self.points_earned += points
    
    def update_streak(self, is_active_today: bool):
        """Update learning streak counters."""
        if is_active_today:
            self.current_streak += 1
            self.longest_streak = max(self.longest_streak, self.current_streak)
        else:
            self.current_streak = 0


class StudentProfile(Base):
    """
    Extended student profile with detailed learning analytics.
    
    Stores detailed analytics and learning patterns for advanced
    adaptive algorithms and recommendation systems.
    """
    __tablename__ = "student_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=False)
    
    # Detailed learning analytics
    learning_patterns = Column(JSON, nullable=True)  # Time-based learning patterns
    knowledge_graph = Column(JSON, nullable=True)  # Subject knowledge mapping
    skill_assessments = Column(JSON, nullable=True)  # Detailed skill evaluations
    
    # Behavioral analysis
    interaction_patterns = Column(JSON, nullable=True)  # How student interacts with content
    attention_span_data = Column(JSON, nullable=True)  # Attention span measurements
    mistake_patterns = Column(JSON, nullable=True)  # Common error analysis
    
    # Personalization data
    content_preferences = Column(JSON, nullable=True)  # Preferred content types
    successful_strategies = Column(JSON, nullable=True)  # What works for this student
    challenge_areas = Column(JSON, nullable=True)  # Areas needing improvement
    
    # Predictive model data
    performance_predictions = Column(JSON, nullable=True)  # ML model predictions
    recommendation_weights = Column(JSON, nullable=True)  # Personalized recommendation weights
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", backref="detailed_profile")
    
    def __repr__(self):
        return f"<StudentProfile(id={self.id}, student_id={self.student_id})>"
