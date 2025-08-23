"""
Content models for learning materials and curriculum management.

Defines learning content, categories, objectives, and the structure
for adaptive content delivery in the AI tutoring system.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from backend.core.database import Base


class ContentType(enum.Enum):
    """Enumeration of content types."""
    LESSON = "lesson"
    EXERCISE = "exercise" 
    QUIZ = "quiz"
    VIDEO = "video"
    ARTICLE = "article"
    INTERACTIVE = "interactive"
    ASSESSMENT = "assessment"
    GAME = "game"


class DifficultyLevel(enum.Enum):
    """Enumeration of difficulty levels."""
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ContentCategory(Base):
    """
    Content categories for organizing learning materials.
    
    Hierarchical structure for subjects, topics, and subtopics
    to enable organized content delivery and navigation.
    """
    __tablename__ = "content_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Hierarchical structure
    parent_id = Column(Integer, ForeignKey("content_categories.id"), nullable=True)
    level = Column(Integer, default=0)  # 0=subject, 1=topic, 2=subtopic, etc.
    sort_order = Column(Integer, default=0)
    
    # Category metadata
    icon = Column(String(100), nullable=True)
    color_code = Column(String(7), nullable=True)  # Hex color
    is_active = Column(Boolean, default=True)
    
    # Learning analytics
    estimated_duration = Column(Integer, nullable=True)  # minutes
    prerequisite_categories = Column(JSON, nullable=True)  # List of category IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("ContentCategory", remote_side=[id], backref="children")
    contents = relationship("Content", back_populates="category")
    learning_objectives = relationship("LearningObjective", back_populates="category")
    
    def __repr__(self):
        return f"<ContentCategory(id={self.id}, name='{self.name}', level={self.level})>"
    
    def get_full_path(self) -> str:
        """Get full hierarchical path of the category."""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name


class LearningObjective(Base):
    """
    Learning objectives and goals for content and assessments.
    
    Defines specific learning outcomes that content aims to achieve
    for competency-based learning and progress tracking.
    """
    __tablename__ = "learning_objectives"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("content_categories.id"), nullable=False)
    
    # Objective details
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    learning_outcome = Column(Text, nullable=False)
    
    # Bloom's taxonomy level
    cognitive_level = Column(String(50), nullable=True)  # remember, understand, apply, etc.
    
    # Difficulty and prerequisites
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    prerequisite_objectives = Column(JSON, nullable=True)  # List of objective IDs
    
    # Assessment criteria
    mastery_threshold = Column(Float, default=0.8)  # 80% to consider mastered
    assessment_method = Column(String(100), nullable=True)
    
    # Metadata
    estimated_time = Column(Integer, nullable=True)  # minutes to master
    importance_weight = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("ContentCategory", back_populates="learning_objectives")
    contents = relationship("Content", secondary="content_objectives", back_populates="learning_objectives")
    
    def __repr__(self):
        return f"<LearningObjective(id={self.id}, title='{self.title}')>"


class Content(Base):
    """
    Learning content including lessons, exercises, and assessments.
    
    Core content entity with adaptive delivery parameters,
    difficulty levels, and engagement tracking capabilities.
    """
    __tablename__ = "contents"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("content_categories.id"), nullable=False)
    
    # Content identification
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    content_type = Column(Enum(ContentType), nullable=False)
    
    # Content data
    content_body = Column(Text, nullable=True)  # Main content (HTML, markdown, etc.)
    content_url = Column(String(500), nullable=True)  # External content URL
    content_metadata = Column(JSON, nullable=True)  # Additional content properties
    
    # Difficulty and adaptation
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    difficulty_score = Column(Float, nullable=True)  # 0.0 to 1.0
    adaptive_parameters = Column(JSON, nullable=True)  # Parameters for adaptation
    
    # Content structure
    prerequisites = Column(JSON, nullable=True)  # Required prior content IDs
    estimated_duration = Column(Integer, nullable=True)  # minutes
    sort_order = Column(Integer, default=0)
    
    # Assessment data (for quizzes/exercises)
    questions = Column(JSON, nullable=True)  # Question data structure
    correct_answers = Column(JSON, nullable=True)  # Answer keys
    scoring_rules = Column(JSON, nullable=True)  # How to score responses
    
    # AI tutor integration
    ai_prompts = Column(JSON, nullable=True)  # Prompts for AI interactions
    explanation_text = Column(Text, nullable=True)  # Explanations for AI to use
    hint_text = Column(Text, nullable=True)  # Hints for AI to provide
    
    # Engagement features
    gamification_elements = Column(JSON, nullable=True)  # Points, badges, etc.
    interactive_features = Column(JSON, nullable=True)  # Interactive elements
    
    # Analytics and tracking
    view_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    average_rating = Column(Float, nullable=True)
    engagement_score = Column(Float, nullable=True)
    
    # Content status
    is_published = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    category = relationship("ContentCategory", back_populates="contents")
    learning_objectives = relationship("LearningObjective", secondary="content_objectives", back_populates="contents")
    
    def __repr__(self):
        return f"<Content(id={self.id}, title='{self.title}', type='{self.content_type}')>"
    
    def increment_view(self):
        """Increment view count."""
        self.view_count += 1
    
    def increment_completion(self):
        """Increment completion count."""
        self.completion_count += 1
    
    def calculate_completion_rate(self) -> float:
        """Calculate completion rate."""
        if self.view_count > 0:
            return (self.completion_count / self.view_count) * 100
        return 0.0
    
    def is_accessible_for_difficulty(self, student_difficulty_level: float) -> bool:
        """Check if content is appropriate for student's difficulty level."""
        if not self.difficulty_score:
            return True
        
        # Allow content within ±0.2 of student's level
        return abs(self.difficulty_score - student_difficulty_level) <= 0.2
    
    def get_adaptive_version(self, student_level: float) -> dict:
        """Get adapted version of content for student level."""
        base_content = {
            "title": self.title,
            "description": self.description,
            "content_body": self.content_body,
            "questions": self.questions or []
        }
        
        # Apply adaptive parameters if available
        if self.adaptive_parameters:
            adaptations = self.adaptive_parameters
            
            # Adjust question difficulty
            if "question_filters" in adaptations:
                base_content["questions"] = self._filter_questions_by_difficulty(
                    base_content["questions"], student_level
                )
            
            # Adjust content complexity
            if "complexity_levels" in adaptations:
                base_content = self._adjust_content_complexity(base_content, student_level)
        
        return base_content
    
    def _filter_questions_by_difficulty(self, questions: list, student_level: float) -> list:
        """Filter questions based on student difficulty level."""
        if not questions:
            return []
        
        filtered = []
        for question in questions:
            q_difficulty = question.get("difficulty", 0.5)
            if abs(q_difficulty - student_level) <= 0.3:  # Within range
                filtered.append(question)
        
        return filtered or questions[:5]  # Fallback to first 5 if none match
    
    def _adjust_content_complexity(self, content: dict, student_level: float) -> dict:
        """Adjust content complexity based on student level."""
        # This is a simplified example - in practice, this could involve
        # more sophisticated NLP-based content adaptation
        if student_level < 0.3:  # Beginner
            content["hints_enabled"] = True
            content["detailed_explanations"] = True
        elif student_level > 0.7:  # Advanced
            content["hints_enabled"] = False
            content["challenge_mode"] = True
        
        return content


# Association table for many-to-many relationship between Content and LearningObjective
from sqlalchemy import Table
content_objectives = Table(
    'content_objectives',
    Base.metadata,
    Column('content_id', Integer, ForeignKey('contents.id'), primary_key=True),
    Column('objective_id', Integer, ForeignKey('learning_objectives.id'), primary_key=True)
)
