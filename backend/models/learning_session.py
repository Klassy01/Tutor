"""
Learning session models for tracking student interactions.

Defines learning sessions and individual interactions within sessions
for comprehensive learning analytics and progress tracking.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.core.database import Base


class LearningSession(Base):
    """
    Learning session tracking student study periods.
    
    Represents a complete learning session with overall metrics,
    outcomes, and adaptive learning adjustments.
    """
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Session metadata
    session_type = Column(String(50), nullable=True)  # practice, assessment, review, etc.
    subject_area = Column(String(100), nullable=True)
    topic = Column(String(200), nullable=True)
    
    # Session metrics
    duration_minutes = Column(Float, nullable=True)
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    hints_used = Column(Integer, default=0)
    
    # Performance metrics
    accuracy_rate = Column(Float, nullable=True)  # percentage correct
    average_response_time = Column(Float, nullable=True)  # seconds
    difficulty_level_start = Column(Float, nullable=True)
    difficulty_level_end = Column(Float, nullable=True)
    
    # Engagement metrics
    engagement_score = Column(Float, nullable=True)  # 0.0 to 1.0
    attention_level = Column(Float, nullable=True)  # derived from interaction patterns
    frustration_indicators = Column(Integer, default=0)
    
    # Learning outcomes
    learning_objectives_met = Column(JSON, nullable=True)  # List of objectives achieved
    skills_practiced = Column(JSON, nullable=True)  # Skills worked on
    knowledge_gains = Column(JSON, nullable=True)  # New knowledge acquired
    
    # Adaptive algorithm data
    algorithm_adjustments = Column(JSON, nullable=True)  # Changes made to difficulty/content
    recommendation_actions = Column(JSON, nullable=True)  # Actions taken by recommender
    
    # Session state
    status = Column(String(20), default="active")  # active, completed, paused, abandoned
    completion_percentage = Column(Float, default=0.0)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="learning_sessions")
    interactions = relationship("SessionInteraction", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<LearningSession(id={self.id}, student_id={self.student_id}, subject='{self.subject_area}')>"
    
    def calculate_accuracy(self):
        """Calculate and update accuracy rate."""
        if self.questions_attempted > 0:
            self.accuracy_rate = (self.questions_correct / self.questions_attempted) * 100
        else:
            self.accuracy_rate = 0.0
    
    def add_interaction(self, interaction_data: dict):
        """Add an interaction to this session."""
        self.questions_attempted += 1
        if interaction_data.get("correct", False):
            self.questions_correct += 1
        if interaction_data.get("hint_used", False):
            self.hints_used += 1
        
        # Recalculate accuracy
        self.calculate_accuracy()
    
    def complete_session(self):
        """Mark session as completed and update metrics."""
        self.status = "completed"
        self.ended_at = func.now()
        self.completion_percentage = 100.0
        
        # Calculate duration if not set
        if self.duration_minutes is None and self.ended_at and self.started_at:
            duration = (self.ended_at - self.started_at).total_seconds() / 60
            self.duration_minutes = round(duration, 2)


class SessionInteraction(Base):
    """
    Individual interactions within a learning session.
    
    Tracks each question, response, and interaction detail for
    fine-grained learning analytics and behavior analysis.
    """
    __tablename__ = "session_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=True)
    
    # Interaction details
    interaction_type = Column(String(50), nullable=False)  # question, hint, feedback, etc.
    sequence_number = Column(Integer, nullable=False)  # Order within session
    
    # Question/content data
    question_text = Column(Text, nullable=True)
    correct_answer = Column(Text, nullable=True)
    student_answer = Column(Text, nullable=True)
    answer_options = Column(JSON, nullable=True)  # For multiple choice
    
    # Response metrics
    is_correct = Column(Boolean, nullable=True)
    response_time_seconds = Column(Float, nullable=True)
    attempts_count = Column(Integer, default=1)
    hint_used = Column(Boolean, default=False)
    hint_content = Column(Text, nullable=True)
    
    # Difficulty and adaptation
    difficulty_level = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)  # Student's confidence
    perceived_difficulty = Column(Integer, nullable=True)  # Student's rating 1-5
    
    # AI tutor interaction
    ai_feedback_given = Column(Text, nullable=True)
    ai_explanation = Column(Text, nullable=True)
    ai_encouragement = Column(Text, nullable=True)
    
    # Behavioral indicators
    hesitation_time = Column(Float, nullable=True)  # Time before first response
    revision_count = Column(Integer, default=0)  # How many times answer was changed
    help_requested = Column(Boolean, default=False)
    
    # Learning analytics
    knowledge_component = Column(String(100), nullable=True)  # What skill/concept
    learning_objective_id = Column(Integer, ForeignKey("learning_objectives.id"), nullable=True)
    mastery_level_before = Column(Float, nullable=True)
    mastery_level_after = Column(Float, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    session = relationship("LearningSession", back_populates="interactions")
    content = relationship("Content", backref="interactions")
    learning_objective = relationship("LearningObjective", backref="interactions")
    
    def __repr__(self):
        return f"<SessionInteraction(id={self.id}, session_id={self.session_id}, type='{self.interaction_type}')>"
    
    def complete_interaction(self, is_correct: bool, response_time: float = None):
        """Complete the interaction with results."""
        self.is_correct = is_correct
        self.completed_at = func.now()
        if response_time:
            self.response_time_seconds = response_time
    
    def add_hint(self, hint_text: str):
        """Add hint usage to this interaction."""
        self.hint_used = True
        self.hint_content = hint_text
    
    def calculate_mastery_change(self):
        """Calculate change in mastery level from this interaction."""
        if self.mastery_level_before is not None and self.mastery_level_after is not None:
            return self.mastery_level_after - self.mastery_level_before
        return 0.0
