"""
User model for authentication and basic user management.

Defines the core User entity with authentication capabilities.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.core.database import Base


class User(Base):
    """
    User model for system authentication.
    
    Base user entity that can be extended for different user types
    (students, teachers, administrators).
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    full_name = Column(String(200), nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # User type and role
    user_type = Column(String(50), default="student")  # student, teacher, admin
    role = Column(String(100), nullable=True)
    
    # Profile and preferences
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    timezone = Column(String(50), default="UTC")
    language_preference = Column(String(10), default="en")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    student_profile = relationship("Student", back_populates="user", uselist=False)
    progress = relationship("UserProgress", back_populates="user", uselist=False)
    lesson_completions = relationship("LessonCompletion", back_populates="user")
    quiz_attempts = relationship("QuizAttemptRecord", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")
    learning_goals = relationship("LearningGoal", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    weekly_reports = relationship("WeeklyReport", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    @property
    def display_name(self) -> str:
        """Get display name for the user."""
        if self.full_name:
            return self.full_name
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        else:
            return self.username
    
    def is_student(self) -> bool:
        """Check if user is a student."""
        return self.user_type == "student"
    
    def is_teacher(self) -> bool:
        """Check if user is a teacher."""
        return self.user_type == "teacher"
    
    def is_admin(self) -> bool:
        """Check if user is an administrator."""
        return self.user_type == "admin" or self.is_superuser
