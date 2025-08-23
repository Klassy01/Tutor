"""
Content management API endpoints.

Handles learning content delivery, content browsing, search,
and adaptive content recommendations for students.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.core.database import get_db
from backend.models.content import Content, ContentCategory, LearningObjective, ContentType, DifficultyLevel
from backend.models.student import Student
from backend.api.dependencies import get_current_student, get_optional_current_user, validate_content_access

router = APIRouter()


# Pydantic models
class ContentResponse(BaseModel):
    """Content response model."""
    id: int
    title: str
    description: Optional[str]
    content_type: str
    difficulty_level: str
    difficulty_score: Optional[float]
    estimated_duration: Optional[int]
    view_count: int
    completion_count: int
    average_rating: Optional[float]
    is_published: bool
    category_name: Optional[str]
    learning_objectives: List[str]
    
    class Config:
        from_attributes = True


class ContentCategoryResponse(BaseModel):
    """Content category response model."""
    id: int
    name: str
    description: Optional[str]
    level: int
    parent_id: Optional[int]
    icon: Optional[str]
    color_code: Optional[str]
    estimated_duration: Optional[int]
    content_count: int
    
    class Config:
        from_attributes = True


class ContentSearchResult(BaseModel):
    """Content search result model."""
    content: ContentResponse
    relevance_score: float
    match_reasons: List[str]
    recommended_for_student: bool


class LearningPathResponse(BaseModel):
    """Learning path response model."""
    path_id: str
    title: str
    description: str
    estimated_duration: int
    difficulty_progression: List[float]
    content_items: List[ContentResponse]
    learning_objectives: List[str]


@router.get("/categories", response_model=List[ContentCategoryResponse])
async def get_content_categories(
    level: Optional[int] = Query(None, description="Filter by category level"),
    parent_id: Optional[int] = Query(None, description="Filter by parent category"),
    db: Session = Depends(get_db)
):
    """
    Get content categories with optional filtering.
    
    Returns hierarchical content categories for browsing
    and organizing learning materials.
    """
    query = db.query(ContentCategory).filter(ContentCategory.is_active == True)
    
    if level is not None:
        query = query.filter(ContentCategory.level == level)
    
    if parent_id is not None:
        query = query.filter(ContentCategory.parent_id == parent_id)
    
    categories = query.order_by(ContentCategory.sort_order, ContentCategory.name).all()
    
    # Add content count for each category
    result = []
    for category in categories:
        content_count = db.query(Content).filter(
            Content.category_id == category.id,
            Content.is_published == True,
            Content.is_active == True
        ).count()
        
        category_data = ContentCategoryResponse.from_orm(category)
        category_data.content_count = content_count
        result.append(category_data)
    
    return result


@router.get("/browse", response_model=List[ContentResponse])
async def browse_content(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    content_type: Optional[ContentType] = Query(None, description="Filter by content type"),
    difficulty_level: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    current_student: Optional[Student] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Browse content with filtering and pagination.
    
    Returns paginated list of learning content with optional
    filtering by category, type, and difficulty level.
    """
    query = db.query(Content).filter(
        Content.is_published == True,
        Content.is_active == True
    )
    
    # Apply filters
    if category_id:
        query = query.filter(Content.category_id == category_id)
    
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    if difficulty_level:
        query = query.filter(Content.difficulty_level == difficulty_level)
    
    # Apply student-specific filtering if authenticated
    if current_student:
        # Filter by appropriate difficulty level
        difficulty_range = 0.2  # ±0.2 from student's level
        min_difficulty = max(0.0, current_student.current_difficulty_level - difficulty_range)
        max_difficulty = min(1.0, current_student.current_difficulty_level + difficulty_range)
        
        query = query.filter(
            and_(
                Content.difficulty_score >= min_difficulty,
                Content.difficulty_score <= max_difficulty
            )
        )
    
    # Order by relevance and popularity
    content_items = query.order_by(
        Content.average_rating.desc(),
        Content.view_count.desc()
    ).offset(offset).limit(limit).all()
    
    # Convert to response models
    result = []
    for content in content_items:
        content_data = ContentResponse(
            id=content.id,
            title=content.title,
            description=content.description,
            content_type=content.content_type.value,
            difficulty_level=content.difficulty_level.value,
            difficulty_score=content.difficulty_score,
            estimated_duration=content.estimated_duration,
            view_count=content.view_count,
            completion_count=content.completion_count,
            average_rating=content.average_rating,
            is_published=content.is_published,
            category_name=content.category.name if content.category else None,
            learning_objectives=[obj.title for obj in content.learning_objectives]
        )
        result.append(content_data)
    
    return result


@router.get("/search", response_model=List[ContentSearchResult])
async def search_content(
    query: str = Query(..., min_length=2, description="Search query"),
    category_id: Optional[int] = Query(None, description="Limit search to category"),
    content_type: Optional[ContentType] = Query(None, description="Limit search to content type"),
    limit: int = Query(20, le=50),
    current_student: Optional[Student] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
):
    """
    Search content with intelligent relevance scoring.
    
    Performs text search across content titles, descriptions,
    and learning objectives with relevance scoring.
    """
    # Base query
    base_query = db.query(Content).filter(
        Content.is_published == True,
        Content.is_active == True
    )
    
    # Apply filters
    if category_id:
        base_query = base_query.filter(Content.category_id == category_id)
    
    if content_type:
        base_query = base_query.filter(Content.content_type == content_type)
    
    # Search in title, description, and content body
    search_terms = query.lower().split()
    search_conditions = []
    
    for term in search_terms:
        term_conditions = [
            Content.title.ilike(f"%{term}%"),
            Content.description.ilike(f"%{term}%"),
            Content.content_body.ilike(f"%{term}%")
        ]
        search_conditions.append(or_(*term_conditions))
    
    # Combine all search conditions
    if search_conditions:
        base_query = base_query.filter(and_(*search_conditions))
    
    content_items = base_query.limit(limit * 2).all()  # Get more for scoring
    
    # Score and rank results
    scored_results = []
    for content in content_items:
        score, reasons = _calculate_relevance_score(content, query, search_terms)
        
        # Check if recommended for current student
        recommended = False
        if current_student:
            recommended = content.is_accessible_for_difficulty(
                current_student.current_difficulty_level
            )
        
        content_response = ContentResponse(
            id=content.id,
            title=content.title,
            description=content.description,
            content_type=content.content_type.value,
            difficulty_level=content.difficulty_level.value,
            difficulty_score=content.difficulty_score,
            estimated_duration=content.estimated_duration,
            view_count=content.view_count,
            completion_count=content.completion_count,
            average_rating=content.average_rating,
            is_published=content.is_published,
            category_name=content.category.name if content.category else None,
            learning_objectives=[obj.title for obj in content.learning_objectives]
        )
        
        scored_results.append(ContentSearchResult(
            content=content_response,
            relevance_score=score,
            match_reasons=reasons,
            recommended_for_student=recommended
        ))
    
    # Sort by relevance score and return top results
    scored_results.sort(key=lambda x: x.relevance_score, reverse=True)
    return scored_results[:limit]


@router.get("/recommendations", response_model=List[ContentResponse])
async def get_content_recommendations(
    recommendation_type: str = Query("adaptive", description="Type of recommendations"),
    limit: int = Query(10, le=20),
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get personalized content recommendations for student.
    
    Uses adaptive learning algorithms to recommend content
    based on student's learning history, preferences, and goals.
    """
    from backend.services.adaptive_learning import AdaptiveLearningEngine
    
    adaptive_engine = AdaptiveLearningEngine()
    
    # Get content recommendations based on type
    if recommendation_type == "adaptive":
        # Use adaptive learning engine
        recommendations = await adaptive_engine.generate_personalized_recommendations(
            current_student, db, recommendation_count=limit
        )
        
        # Filter for content recommendations
        content_recommendations = [
            rec for rec in recommendations if rec.get("type") == "content"
        ]
        
        # Get content objects
        content_ids = [rec["content_id"] for rec in content_recommendations]
        content_items = db.query(Content).filter(Content.id.in_(content_ids)).all()
        
    elif recommendation_type == "popular":
        # Popular content in student's difficulty range
        content_items = db.query(Content).filter(
            Content.is_published == True,
            Content.is_active == True,
            Content.difficulty_score.between(
                current_student.current_difficulty_level - 0.2,
                current_student.current_difficulty_level + 0.2
            )
        ).order_by(
            Content.view_count.desc(),
            Content.average_rating.desc()
        ).limit(limit).all()
        
    elif recommendation_type == "continue":
        # Content to continue learning from previous sessions
        from backend.models.learning_session import LearningSession
        from backend.models.progress import Progress
        
        # Get subjects from recent sessions
        recent_sessions = db.query(LearningSession).filter(
            LearningSession.student_id == current_student.id
        ).order_by(LearningSession.started_at.desc()).limit(5).all()
        
        recent_subjects = list(set(s.subject_area for s in recent_sessions if s.subject_area))
        
        if recent_subjects:
            # Find content in these subjects
            content_items = db.query(Content).join(Content.category).filter(
                ContentCategory.name.in_(recent_subjects),
                Content.is_published == True,
                Content.is_active == True
            ).limit(limit).all()
        else:
            content_items = []
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid recommendation type"
        )
    
    # Convert to response models
    result = []
    for content in content_items:
        content_data = ContentResponse(
            id=content.id,
            title=content.title,
            description=content.description,
            content_type=content.content_type.value,
            difficulty_level=content.difficulty_level.value,
            difficulty_score=content.difficulty_score,
            estimated_duration=content.estimated_duration,
            view_count=content.view_count,
            completion_count=content.completion_count,
            average_rating=content.average_rating,
            is_published=content.is_published,
            category_name=content.category.name if content.category else None,
            learning_objectives=[obj.title for obj in content.learning_objectives]
        )
        result.append(content_data)
    
    return result


@router.get("/{content_id}", response_model=Dict[str, Any])
async def get_content_details(
    content_id: int,
    current_student: Optional[Student] = Depends(get_optional_current_user),
    content: Content = Depends(validate_content_access),
    db: Session = Depends(get_db)
):
    """
    Get detailed content information with adaptive version.
    
    Returns content details and adapts the content based on
    the student's current difficulty level and preferences.
    """
    # Increment view count
    content.increment_view()
    db.commit()
    
    # Get adaptive version if student is authenticated
    if current_student:
        adaptive_content = content.get_adaptive_version(
            current_student.current_difficulty_level
        )
    else:
        adaptive_content = {
            "title": content.title,
            "description": content.description,
            "content_body": content.content_body,
            "questions": content.questions or []
        }
    
    # Get learning objectives
    learning_objectives = [
        {
            "id": obj.id,
            "title": obj.title,
            "description": obj.description,
            "cognitive_level": obj.cognitive_level,
            "mastery_threshold": obj.mastery_threshold
        }
        for obj in content.learning_objectives
    ]
    
    # Get related content
    related_content = db.query(Content).filter(
        Content.category_id == content.category_id,
        Content.id != content.id,
        Content.is_published == True,
        Content.is_active == True
    ).limit(5).all()
    
    return {
        "content": {
            "id": content.id,
            "title": content.title,
            "description": content.description,
            "content_type": content.content_type.value,
            "difficulty_level": content.difficulty_level.value,
            "difficulty_score": content.difficulty_score,
            "estimated_duration": content.estimated_duration,
            "category": {
                "id": content.category.id,
                "name": content.category.name,
                "description": content.category.description
            } if content.category else None,
            "metadata": content.content_metadata,
            "gamification": content.gamification_elements,
            "interactive_features": content.interactive_features
        },
        "adaptive_content": adaptive_content,
        "learning_objectives": learning_objectives,
        "related_content": [
            {
                "id": rc.id,
                "title": rc.title,
                "content_type": rc.content_type.value,
                "difficulty_level": rc.difficulty_level.value,
                "estimated_duration": rc.estimated_duration
            }
            for rc in related_content
        ],
        "student_context": {
            "recommended_difficulty": current_student.current_difficulty_level if current_student else None,
            "learning_style": current_student.learning_style if current_student else None,
            "is_appropriate": content.is_accessible_for_difficulty(
                current_student.current_difficulty_level
            ) if current_student else True
        }
    }


@router.post("/{content_id}/complete")
async def mark_content_complete(
    content_id: int,
    rating: Optional[int] = Query(None, ge=1, le=5, description="Content rating (1-5)"),
    time_spent: Optional[int] = Query(None, ge=0, description="Time spent in minutes"),
    current_student: Student = Depends(get_current_student),
    content: Content = Depends(validate_content_access),
    db: Session = Depends(get_db)
):
    """
    Mark content as completed by student.
    
    Records completion, updates progress tracking, and collects
    optional feedback for content improvement.
    """
    from backend.models.progress import Progress
    
    # Increment completion count
    content.increment_completion()
    
    # Update or create progress record
    progress = db.query(Progress).filter(
        Progress.student_id == current_student.id,
        Progress.content_id == content_id
    ).first()
    
    if not progress:
        progress = Progress(
            student_id=current_student.id,
            content_id=content_id,
            completion_percentage=100.0,
            status="completed"
        )
        db.add(progress)
    else:
        progress.completion_percentage = 100.0
        progress.status = "completed"
    
    # Add time spent if provided
    if time_spent:
        progress.time_spent_minutes += time_spent
        current_student.add_study_time(time_spent)
    
    # Award points for completion
    points_earned = 10  # Base points
    if content.difficulty_score:
        points_earned += int(content.difficulty_score * 20)  # Bonus for difficulty
    
    current_student.award_points(points_earned)
    
    # Update content rating if provided
    if rating:
        # Simple rating update (in practice, you'd want more sophisticated rating aggregation)
        if content.average_rating:
            # Weighted average with existing ratings
            total_ratings = content.view_count  # Assuming all viewers rate
            new_average = (
                (content.average_rating * (total_ratings - 1) + rating) / total_ratings
            )
            content.average_rating = new_average
        else:
            content.average_rating = float(rating)
    
    db.commit()
    
    return {
        "message": "Content marked as completed",
        "points_earned": points_earned,
        "total_points": current_student.points_earned,
        "completion_rate": content.calculate_completion_rate(),
        "progress_status": progress.status
    }


def _calculate_relevance_score(content: Content, query: str, search_terms: List[str]) -> tuple[float, List[str]]:
    """Calculate relevance score for search results."""
    score = 0.0
    reasons = []
    
    query_lower = query.lower()
    title_lower = (content.title or "").lower()
    desc_lower = (content.description or "").lower()
    
    # Title matches (highest weight)
    if query_lower in title_lower:
        score += 10.0
        reasons.append("Title match")
    
    # Individual term matches in title
    title_term_matches = sum(1 for term in search_terms if term in title_lower)
    score += title_term_matches * 5.0
    
    # Description matches
    if query_lower in desc_lower:
        score += 5.0
        reasons.append("Description match")
    
    # Individual term matches in description
    desc_term_matches = sum(1 for term in search_terms if term in desc_lower)
    score += desc_term_matches * 2.0
    
    # Learning objective matches
    for obj in content.learning_objectives:
        obj_title_lower = (obj.title or "").lower()
        if query_lower in obj_title_lower:
            score += 3.0
            reasons.append("Learning objective match")
    
    # Popularity boost
    if content.view_count > 100:
        score += 1.0
        reasons.append("Popular content")
    
    # Rating boost
    if content.average_rating and content.average_rating >= 4.0:
        score += 2.0
        reasons.append("Highly rated")
    
    return score, reasons
