"""
Quiz attempt models for tracking quiz performance and analytics.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.core.database import Base


class QuizAttempt(Base):
    """
    Quiz attempt tracking for students.
    
    Records complete quiz sessions with questions, answers, and performance metrics.
    """
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Quiz metadata
    quiz_title = Column(String(200), nullable=False)
    subject_area = Column(String(100), nullable=True)
    topic = Column(String(200), nullable=True)
    difficulty_level = Column(Float, default=0.5)  # 0.0 to 1.0
    
    # Quiz content
    total_questions = Column(Integer, nullable=False)
    questions_data = Column(JSON, nullable=False)  # Store all questions and options
    
    # Performance metrics
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    skipped_questions = Column(Integer, default=0)
    accuracy_percentage = Column(Float, default=0.0)
    
    # Timing metrics
    total_time_minutes = Column(Float, nullable=True)
    average_time_per_question = Column(Float, nullable=True)
    
    # Status
    status = Column(String(20), default="in_progress")  # in_progress, completed, abandoned
    completion_percentage = Column(Float, default=0.0)
    
    # Results
    final_score = Column(Float, nullable=True)  # 0 to 100
    grade = Column(String(5), nullable=True)  # A, B, C, D, F
    passed = Column(Boolean, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="quiz_attempts")
    question_responses = relationship("QuizQuestionResponse", back_populates="quiz_attempt", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, student_id={self.student_id}, title='{self.quiz_title}')>"
    
    def calculate_score(self):
        """Calculate and update quiz score."""
        if self.total_questions > 0:
            self.accuracy_percentage = (self.correct_answers / self.total_questions) * 100
            self.final_score = self.accuracy_percentage
            
            # Assign grade based on score
            if self.final_score >= 90:
                self.grade = "A"
            elif self.final_score >= 80:
                self.grade = "B"
            elif self.final_score >= 70:
                self.grade = "C"
            elif self.final_score >= 60:
                self.grade = "D"
            else:
                self.grade = "F"
            
            # Determine if passed (typically 70% or above)
            self.passed = self.final_score >= 70
        
        return self.final_score
    
    def complete_quiz(self):
        """Mark quiz as completed and calculate final metrics."""
        self.status = "completed"
        self.completed_at = func.now()
        self.completion_percentage = 100.0
        
        # Calculate final score
        self.calculate_score()
        
        # Calculate timing metrics
        if self.completed_at and self.started_at:
            duration = (self.completed_at - self.started_at).total_seconds() / 60
            self.total_time_minutes = round(duration, 2)
            if self.total_questions > 0:
                self.average_time_per_question = round(self.total_time_minutes / self.total_questions, 2)


class QuizQuestionResponse(Base):
    """
    Individual question responses within a quiz attempt.
    """
    __tablename__ = "quiz_question_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"), nullable=False)
    
    # Question details
    question_number = Column(Integer, nullable=False)
    question_id = Column(String(50), nullable=False)  # Unique identifier for the question
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), default="multiple_choice")  # multiple_choice, true_false, short_answer
    
    # Options and answers
    answer_options = Column(JSON, nullable=True)  # For multiple choice questions
    correct_answer = Column(Text, nullable=False)
    student_answer = Column(Text, nullable=True)
    
    # Response metrics
    is_correct = Column(Boolean, nullable=False)
    is_skipped = Column(Boolean, default=False)
    response_time_seconds = Column(Float, nullable=True)
    
    # Additional data
    explanation = Column(Text, nullable=True)  # Explanation of correct answer
    difficulty_level = Column(Float, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    answered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    quiz_attempt = relationship("QuizAttempt", back_populates="question_responses")
    
    def __repr__(self):
        return f"<QuizQuestionResponse(id={self.id}, quiz_attempt_id={self.quiz_attempt_id}, question_number={self.question_number})>"
    
    def submit_answer(self, answer: str, response_time: float = None):
        """Submit answer for this question."""
        self.student_answer = answer
        self.answered_at = func.now()
        self.is_correct = (answer == self.correct_answer)
        
        if response_time:
            self.response_time_seconds = response_time
        
        return self.is_correct
    
    def skip_question(self):
        """Mark this question as skipped."""
        self.is_skipped = True
        self.answered_at = func.now()
        self.is_correct = False
