"""
Progress tracking and engagement analytics models.

Defines comprehensive progress tracking, learning analytics,
and student engagement measurement for the AI tutoring system.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from backend.core.database import Base


class Progress(Base):
    """
    Student progress tracking for learning objectives and content.
    
    Tracks mastery levels, completion status, and learning progression
    across different subjects and skills for adaptive learning.
    """
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=True)
    learning_objective_id = Column(Integer, ForeignKey("learning_objectives.id"), nullable=True)
    
    # Progress metrics
    mastery_level = Column(Float, default=0.0)  # 0.0 to 1.0
    completion_percentage = Column(Float, default=0.0)  # 0.0 to 100.0
    attempts_count = Column(Integer, default=0)
    
    # Performance tracking
    best_score = Column(Float, nullable=True)
    last_score = Column(Float, nullable=True)
    average_score = Column(Float, nullable=True)
    time_spent_minutes = Column(Float, default=0.0)
    
    # Learning analytics
    learning_velocity = Column(Float, nullable=True)  # Rate of learning
    retention_score = Column(Float, nullable=True)  # How well knowledge is retained
    difficulty_progression = Column(JSON, nullable=True)  # Difficulty level over time
    
    # Status tracking
    status = Column(String(20), default="not_started")  # not_started, in_progress, completed, mastered
    is_mastered = Column(Boolean, default=False)
    needs_review = Column(Boolean, default=False)
    
    # Adaptive learning data
    recommended_difficulty = Column(Float, nullable=True)
    next_review_date = Column(DateTime, nullable=True)
    spaced_repetition_interval = Column(Integer, default=1)  # days
    
    # Timestamps
    first_attempt = Column(DateTime(timezone=True), nullable=True)
    last_attempt = Column(DateTime(timezone=True), nullable=True)
    mastered_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="progress_records")
    content = relationship("Content")
    learning_objective = relationship("LearningObjective")
    
    def __repr__(self):
        return f"<Progress(id={self.id}, student_id={self.student_id}, mastery={self.mastery_level})>"
    
    def update_progress(self, score: float, time_spent: float):
        """Update progress with new attempt data."""
        self.attempts_count += 1
        self.time_spent_minutes += time_spent
        self.last_score = score
        self.last_attempt = datetime.utcnow()
        
        # Update best score
        if self.best_score is None or score > self.best_score:
            self.best_score = score
        
        # Update average score
        if self.average_score is None:
            self.average_score = score
        else:
            self.average_score = (self.average_score * (self.attempts_count - 1) + score) / self.attempts_count
        
        # Update mastery level based on performance
        self._update_mastery_level(score)
        
        # Set first attempt if this is the first
        if self.first_attempt is None:
            self.first_attempt = self.last_attempt
        
        # Update status
        self._update_status()
    
    def _update_mastery_level(self, score: float):
        """Update mastery level using spaced repetition and performance."""
        # Simple mastery calculation - can be enhanced with more sophisticated algorithms
        score_weight = 0.3
        consistency_weight = 0.7
        
        # Score component
        score_component = score
        
        # Consistency component (based on recent performance)
        if self.attempts_count > 1:
            consistency_component = min(1.0, (self.average_score + score) / 2)
        else:
            consistency_component = score
        
        # Calculate new mastery level
        new_mastery = (score_component * score_weight + 
                      consistency_component * consistency_weight)
        
        # Smooth the transition
        if self.mastery_level > 0:
            self.mastery_level = (self.mastery_level * 0.7 + new_mastery * 0.3)
        else:
            self.mastery_level = new_mastery
        
        # Ensure bounds
        self.mastery_level = max(0.0, min(1.0, self.mastery_level))
    
    def _update_status(self):
        """Update progress status based on current metrics."""
        if self.mastery_level >= 0.9:
            self.status = "mastered"
            self.is_mastered = True
            if self.mastered_at is None:
                self.mastered_at = datetime.utcnow()
        elif self.mastery_level >= 0.7:
            self.status = "completed"
        elif self.attempts_count > 0:
            self.status = "in_progress"
        else:
            self.status = "not_started"
    
    def calculate_next_review(self):
        """Calculate next review date using spaced repetition."""
        if self.is_mastered:
            # Use spaced repetition algorithm
            base_interval = self.spaced_repetition_interval
            
            if self.last_score and self.last_score >= 0.8:
                # Increase interval for good performance
                self.spaced_repetition_interval = min(30, base_interval * 2)
            else:
                # Reset interval for poor performance
                self.spaced_repetition_interval = max(1, base_interval // 2)
            
            self.next_review_date = datetime.utcnow() + timedelta(days=self.spaced_repetition_interval)
        else:
            # More frequent review for non-mastered content
            self.next_review_date = datetime.utcnow() + timedelta(days=1)


class ProgressTracker(Base):
    """
    Aggregate progress tracking across subjects and time periods.
    
    Provides high-level analytics and progress summaries for
    dashboard views and learning analytics.
    """
    __tablename__ = "progress_trackers"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Time period tracking
    tracking_period = Column(String(20), nullable=False)  # daily, weekly, monthly
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    
    # Aggregate metrics
    total_study_time = Column(Float, default=0.0)  # minutes
    sessions_completed = Column(Integer, default=0)
    content_items_completed = Column(Integer, default=0)
    objectives_mastered = Column(Integer, default=0)
    
    # Performance metrics
    average_accuracy = Column(Float, nullable=True)
    improvement_rate = Column(Float, nullable=True)  # Rate of improvement
    consistency_score = Column(Float, nullable=True)  # How consistent the learning is
    
    # Subject-specific tracking
    subject_progress = Column(JSON, nullable=True)  # Progress by subject
    skill_improvements = Column(JSON, nullable=True)  # Skill-level improvements
    
    # Goal tracking
    goals_set = Column(Integer, default=0)
    goals_achieved = Column(Integer, default=0)
    streak_count = Column(Integer, default=0)
    
    # Engagement metrics
    engagement_score = Column(Float, nullable=True)
    participation_rate = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    student = relationship("Student")
    
    def __repr__(self):
        return f"<ProgressTracker(id={self.id}, student_id={self.student_id}, period='{self.tracking_period}')>"


class EngagementMetrics(Base):
    """
    Detailed engagement and behavioral analytics.
    
    Tracks student engagement patterns, attention levels,
    and behavioral indicators for personalized learning optimization.
    """
    __tablename__ = "engagement_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("learning_sessions.id"), nullable=True)
    
    # Time-based engagement
    session_duration = Column(Float, nullable=True)  # minutes
    active_time_percentage = Column(Float, nullable=True)  # % of session actively engaged
    idle_time_total = Column(Float, default=0.0)  # minutes of idle time
    
    # Interaction patterns
    click_frequency = Column(Float, nullable=True)  # clicks per minute
    scroll_behavior = Column(JSON, nullable=True)  # Scrolling patterns
    navigation_patterns = Column(JSON, nullable=True)  # How student navigates
    
    # Attention indicators
    focus_score = Column(Float, nullable=True)  # 0.0 to 1.0
    distraction_events = Column(Integer, default=0)  # Tab switches, etc.
    attention_span = Column(Float, nullable=True)  # Estimated attention span
    
    # Response patterns
    response_time_variance = Column(Float, nullable=True)  # Consistency of response times
    hesitation_frequency = Column(Float, nullable=True)  # How often student hesitates
    revision_frequency = Column(Float, nullable=True)  # How often answers are changed
    
    # Emotional indicators
    frustration_indicators = Column(Integer, default=0)  # Signs of frustration
    confidence_level = Column(Float, nullable=True)  # Self-reported or inferred
    motivation_score = Column(Float, nullable=True)  # Inferred motivation level
    
    # Help-seeking behavior
    help_requests = Column(Integer, default=0)
    hint_usage_rate = Column(Float, nullable=True)  # % of available hints used
    external_resource_access = Column(Integer, default=0)
    
    # Social engagement (if applicable)
    peer_interaction_count = Column(Integer, default=0)
    collaboration_score = Column(Float, nullable=True)
    discussion_participation = Column(Float, nullable=True)
    
    # Gamification engagement
    achievement_reactions = Column(JSON, nullable=True)  # Reactions to achievements
    challenge_acceptance_rate = Column(Float, nullable=True)
    competition_engagement = Column(Float, nullable=True)
    
    # Predictive indicators
    dropout_risk_score = Column(Float, nullable=True)  # Risk of dropping out
    engagement_trend = Column(String(20), nullable=True)  # increasing, stable, decreasing
    
    # Timestamps
    measurement_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="engagement_metrics")
    session = relationship("LearningSession")
    
    def __repr__(self):
        return f"<EngagementMetrics(id={self.id}, student_id={self.student_id}, focus={self.focus_score})>"
    
    def calculate_overall_engagement(self) -> float:
        """Calculate overall engagement score from component metrics."""
        metrics = []
        
        if self.focus_score is not None:
            metrics.append(self.focus_score)
        
        if self.active_time_percentage is not None:
            metrics.append(self.active_time_percentage / 100)
        
        if self.motivation_score is not None:
            metrics.append(self.motivation_score)
        
        if self.confidence_level is not None:
            metrics.append(self.confidence_level)
        
        if metrics:
            return sum(metrics) / len(metrics)
        return 0.5  # Default neutral engagement
    
    def identify_engagement_patterns(self) -> dict:
        """Identify key engagement patterns and recommendations."""
        patterns = {
            "strengths": [],
            "concerns": [],
            "recommendations": []
        }
        
        # Analyze focus and attention
        if self.focus_score and self.focus_score > 0.8:
            patterns["strengths"].append("High focus and attention")
        elif self.focus_score and self.focus_score < 0.4:
            patterns["concerns"].append("Low focus levels")
            patterns["recommendations"].append("Consider shorter session durations")
        
        # Analyze help-seeking behavior
        if self.help_requests > 3:
            patterns["concerns"].append("Frequent help requests - content may be too difficult")
            patterns["recommendations"].append("Adjust difficulty level or provide more scaffolding")
        
        # Analyze frustration indicators
        if self.frustration_indicators > 2:
            patterns["concerns"].append("Signs of frustration detected")
            patterns["recommendations"].append("Provide encouragement and adjust pacing")
        
        return patterns


class Achievement(Base):
    """
    Student achievements and badges system.
    
    Tracks earned achievements, badges, and milestones
    for gamification and motivation enhancement.
    """
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    
    # Achievement details
    achievement_type = Column(String(50), nullable=False)  # badge, milestone, streak, etc.
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)  # academic, engagement, consistency
    
    # Achievement data
    criteria = Column(JSON, nullable=True)  # What was needed to earn this
    progress_data = Column(JSON, nullable=True)  # Progress toward earning
    reward_points = Column(Integer, default=0)
    
    # Status
    is_earned = Column(Boolean, default=False)
    earned_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", backref="achievements")
    
    def __repr__(self):
        return f"<Achievement(id={self.id}, student_id={self.student_id}, name='{self.name}')>"
    
    def earn_achievement(self):
        """Mark achievement as earned."""
        self.is_earned = True
        self.earned_at = func.now()
