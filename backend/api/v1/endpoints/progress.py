"""
Progress tracking API endpoints.

Handles student progress monitoring, mastery tracking,
and learning analytics for the AI tutoring system.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from backend.core.database import get_db
from backend.models.student import Student
from backend.models.progress import Progress, ProgressTracker, EngagementMetrics
from backend.models.content import LearningObjective
from backend.api.dependencies import get_current_student

router = APIRouter()


# Pydantic models
class ProgressResponse(BaseModel):
    """Progress response model."""
    id: int
    content_id: Optional[int]
    learning_objective_id: Optional[int]
    mastery_level: float
    completion_percentage: float
    attempts_count: int
    best_score: Optional[float]
    average_score: Optional[float]
    time_spent_minutes: float
    status: str
    is_mastered: bool
    needs_review: bool
    next_review_date: Optional[datetime]
    
    class Config:
        from_attributes = True


class ProgressSummary(BaseModel):
    """Progress summary model."""
    total_objectives: int
    mastered_objectives: int
    in_progress_objectives: int
    not_started_objectives: int
    overall_mastery_percentage: float
    total_study_time: float
    average_mastery_level: float


class SubjectProgress(BaseModel):
    """Subject-specific progress model."""
    subject_name: str
    total_objectives: int
    mastered_count: int
    average_mastery: float
    completion_percentage: float
    study_time_minutes: float
    last_activity: Optional[datetime]


class EngagementResponse(BaseModel):
    """Engagement metrics response model."""
    id: int
    session_duration: Optional[float]
    focus_score: Optional[float]
    engagement_score: Optional[float]
    help_requests: int
    hint_usage_rate: Optional[float]
    confidence_level: Optional[float]
    motivation_score: Optional[float]
    measurement_date: datetime
    
    class Config:
        from_attributes = True


@router.get("/overview")
async def get_progress_overview(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive progress overview for the student.
    
    Returns high-level progress metrics, mastery statistics,
    and learning achievement summaries.
    """
    # Get all progress records
    progress_records = db.query(Progress).filter(
        Progress.student_id == current_student.id
    ).all()
    
    # Calculate summary statistics
    total_objectives = len(progress_records)
    mastered = len([p for p in progress_records if p.is_mastered])
    in_progress = len([p for p in progress_records if p.status == "in_progress"])
    not_started = len([p for p in progress_records if p.status == "not_started"])
    
    overall_mastery = sum(p.mastery_level for p in progress_records) / max(1, total_objectives)
    total_study_time = sum(p.time_spent_minutes for p in progress_records)
    
    # Get subject-wise progress
    subject_progress = _calculate_subject_progress(progress_records, db)
    
    # Get recent achievements
    recent_achievements = _get_recent_achievements(current_student, db)
    
    # Get learning streaks and patterns
    learning_patterns = _analyze_learning_patterns(current_student, db)
    
    return {
        "summary": ProgressSummary(
            total_objectives=total_objectives,
            mastered_objectives=mastered,
            in_progress_objectives=in_progress,
            not_started_objectives=not_started,
            overall_mastery_percentage=overall_mastery * 100,
            total_study_time=total_study_time,
            average_mastery_level=overall_mastery
        ),
        "subject_progress": subject_progress,
        "recent_achievements": recent_achievements,
        "learning_patterns": learning_patterns,
        "student_stats": {
            "current_streak": current_student.current_streak,
            "longest_streak": current_student.longest_streak,
            "total_points": current_student.points_earned,
            "sessions_completed": current_student.sessions_completed,
            "average_session_duration": current_student.average_session_duration
        }
    }


@router.get("/detailed", response_model=List[ProgressResponse])
async def get_detailed_progress(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    status: Optional[str] = Query(None, description="Filter by progress status"),
    mastery_threshold: Optional[float] = Query(None, ge=0.0, le=1.0, description="Filter by mastery level"),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get detailed progress records with filtering options.
    
    Returns comprehensive list of progress records with optional
    filtering by subject, status, and mastery level.
    """
    query = db.query(Progress).filter(Progress.student_id == current_student.id)
    
    if status:
        query = query.filter(Progress.status == status)
    
    if mastery_threshold is not None:
        query = query.filter(Progress.mastery_level >= mastery_threshold)
    
    if subject:
        # Filter by subject through learning objectives
        query = query.join(LearningObjective).join(LearningObjective.category).filter(
            LearningObjective.category.name.ilike(f"%{subject}%")
        )
    
    progress_records = query.order_by(
        Progress.updated_at.desc()
    ).offset(offset).limit(limit).all()
    
    return [ProgressResponse.from_orm(progress) for progress in progress_records]


@router.get("/subjects")
async def get_subject_progress(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get progress breakdown by subject areas.
    
    Returns progress metrics organized by subject areas
    with mastery levels and completion rates.
    """
    # Get progress records with learning objectives
    progress_records = db.query(Progress).filter(
        Progress.student_id == current_student.id,
        Progress.learning_objective_id.isnot(None)
    ).join(LearningObjective).join(LearningObjective.category).all()
    
    subject_progress = _calculate_subject_progress(progress_records, db)
    
    return {
        "subjects": subject_progress,
        "total_subjects": len(subject_progress),
        "subjects_mastered": len([s for s in subject_progress if s.completion_percentage >= 80]),
        "overall_progress": sum(s.completion_percentage for s in subject_progress) / max(1, len(subject_progress))
    }


@router.get("/mastery-map")
async def get_mastery_map(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get visual mastery map showing skill progression.
    
    Returns hierarchical mastery data suitable for creating
    visual progress maps and skill trees.
    """
    from backend.models.content import ContentCategory
    
    # Get all categories with progress data
    categories = db.query(ContentCategory).filter(
        ContentCategory.is_active == True
    ).order_by(ContentCategory.level, ContentCategory.sort_order).all()
    
    mastery_map = {}
    
    for category in categories:
        # Get progress for this category
        progress_in_category = db.query(Progress).filter(
            Progress.student_id == current_student.id
        ).join(LearningObjective).filter(
            LearningObjective.category_id == category.id
        ).all()
        
        if progress_in_category:
            avg_mastery = sum(p.mastery_level for p in progress_in_category) / len(progress_in_category)
            mastered_count = len([p for p in progress_in_category if p.is_mastered])
            
            mastery_map[category.name] = {
                "category_id": category.id,
                "level": category.level,
                "parent_id": category.parent_id,
                "mastery_level": avg_mastery,
                "total_objectives": len(progress_in_category),
                "mastered_objectives": mastered_count,
                "completion_percentage": (mastered_count / len(progress_in_category)) * 100,
                "icon": category.icon,
                "color_code": category.color_code
            }
    
    return {
        "mastery_map": mastery_map,
        "hierarchy": _build_category_hierarchy(categories),
        "overall_stats": {
            "categories_started": len(mastery_map),
            "categories_mastered": len([m for m in mastery_map.values() if m["completion_percentage"] >= 80]),
            "average_mastery": sum(m["mastery_level"] for m in mastery_map.values()) / max(1, len(mastery_map))
        }
    }


@router.get("/learning-path")
async def get_recommended_learning_path(
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get recommended learning path based on current progress.
    
    Uses adaptive algorithms to suggest optimal learning sequence
    based on prerequisites, mastery levels, and learning goals.
    """
    from backend.services.adaptive_learning import AdaptiveLearningEngine
    
    adaptive_engine = AdaptiveLearningEngine()
    
    # Get knowledge gaps
    knowledge_gaps = await adaptive_engine._identify_knowledge_gaps(current_student, db)
    
    # Get learning objectives that need attention
    objectives_to_review = db.query(Progress).filter(
        Progress.student_id == current_student.id,
        Progress.needs_review == True
    ).all()
    
    # Get next objectives to tackle
    not_started_objectives = db.query(LearningObjective).filter(
        ~LearningObjective.id.in_(
            db.query(Progress.learning_objective_id).filter(
                Progress.student_id == current_student.id,
                Progress.learning_objective_id.isnot(None)
            )
        ),
        LearningObjective.is_active == True
    ).limit(10).all()
    
    learning_path = {
        "immediate_priorities": [
            {
                "type": "review",
                "objective_id": progress.learning_objective_id,
                "title": progress.learning_objective.title if progress.learning_objective else "Unknown",
                "reason": "Needs review to maintain mastery",
                "priority": "high",
                "estimated_time": 15
            }
            for progress in objectives_to_review[:3]
        ],
        "knowledge_gaps": [
            {
                "type": "gap_filling",
                "objective_id": gap.get("id"),
                "title": gap.get("title", "Unknown"),
                "mastery_level": gap.get("mastery_level", 0),
                "priority": "medium",
                "estimated_time": 30
            }
            for gap in knowledge_gaps[:3]
        ],
        "new_learning": [
            {
                "type": "new_objective",
                "objective_id": obj.id,
                "title": obj.title,
                "description": obj.description,
                "difficulty": obj.difficulty_level.value if obj.difficulty_level else "medium",
                "priority": "low",
                "estimated_time": obj.estimated_time or 45
            }
            for obj in not_started_objectives[:5]
        ]
    }
    
    return learning_path


@router.get("/engagement-metrics", response_model=List[EngagementResponse])
async def get_engagement_metrics(
    days: int = Query(30, ge=1, le=90, description="Number of days to retrieve"),
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get engagement metrics for the specified time period.
    
    Returns detailed engagement analytics including focus scores,
    motivation levels, and learning behavior patterns.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    engagement_records = db.query(EngagementMetrics).filter(
        EngagementMetrics.student_id == current_student.id,
        EngagementMetrics.measurement_date >= cutoff_date
    ).order_by(EngagementMetrics.measurement_date.desc()).all()
    
    return [EngagementResponse.from_orm(record) for record in engagement_records]


@router.get("/analytics")
async def get_progress_analytics(
    period: str = Query("week", regex="^(week|month|quarter|year)$"),
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive progress analytics for specified time period.
    
    Returns detailed analytics including trends, patterns,
    and performance insights over the specified period.
    """
    # Calculate date range
    now = datetime.utcnow()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "quarter":
        start_date = now - timedelta(days=90)
    else:  # year
        start_date = now - timedelta(days=365)
    
    # Get progress tracker records
    tracker_records = db.query(ProgressTracker).filter(
        ProgressTracker.student_id == current_student.id,
        ProgressTracker.period_start >= start_date
    ).all()
    
    # Calculate analytics
    analytics = {
        "period": period,
        "date_range": {
            "start": start_date.isoformat(),
            "end": now.isoformat()
        },
        "summary_metrics": _calculate_period_metrics(tracker_records),
        "trends": _analyze_progress_trends(tracker_records),
        "performance_patterns": _analyze_performance_patterns(current_student, db, start_date),
        "achievements_unlocked": _get_period_achievements(current_student, db, start_date),
        "recommendations": _generate_progress_recommendations(current_student, tracker_records)
    }
    
    return analytics


@router.post("/goals")
async def set_progress_goals(
    goals: Dict[str, Any],
    current_student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """
    Set progress goals for the student.
    
    Allows students to set specific learning goals and targets
    for progress tracking and motivation.
    """
    # Store goals in student profile or separate goals table
    # For now, we'll store in the student's academic_goals field
    current_student.academic_goals = str(goals)  # In practice, you'd have a separate goals model
    db.commit()
    
    return {
        "message": "Progress goals set successfully",
        "goals": goals,
        "target_date": goals.get("target_date"),
        "reminders_enabled": goals.get("reminders_enabled", True)
    }


def _calculate_subject_progress(progress_records: List[Progress], db: Session) -> List[SubjectProgress]:
    """Calculate progress statistics by subject."""
    from backend.models.content import ContentCategory
    
    subject_data = {}
    
    for progress in progress_records:
        if not progress.learning_objective or not progress.learning_objective.category:
            continue
        
        subject_name = progress.learning_objective.category.name
        
        if subject_name not in subject_data:
            subject_data[subject_name] = {
                "progress_records": [],
                "total_time": 0,
                "last_activity": None
            }
        
        subject_data[subject_name]["progress_records"].append(progress)
        subject_data[subject_name]["total_time"] += progress.time_spent_minutes
        
        if progress.last_attempt:
            if not subject_data[subject_name]["last_activity"] or progress.last_attempt > subject_data[subject_name]["last_activity"]:
                subject_data[subject_name]["last_activity"] = progress.last_attempt
    
    # Convert to SubjectProgress objects
    subject_progress = []
    for subject_name, data in subject_data.items():
        records = data["progress_records"]
        mastered_count = len([p for p in records if p.is_mastered])
        avg_mastery = sum(p.mastery_level for p in records) / len(records)
        
        subject_progress.append(SubjectProgress(
            subject_name=subject_name,
            total_objectives=len(records),
            mastered_count=mastered_count,
            average_mastery=avg_mastery,
            completion_percentage=(mastered_count / len(records)) * 100,
            study_time_minutes=data["total_time"],
            last_activity=data["last_activity"]
        ))
    
    return subject_progress


def _get_recent_achievements(student: Student, db: Session) -> List[Dict[str, Any]]:
    """Get recent achievements and milestones."""
    achievements = []
    
    # Check for recent milestones
    if student.sessions_completed > 0 and student.sessions_completed % 10 == 0:
        achievements.append({
            "type": "milestone",
            "title": f"{student.sessions_completed} Sessions Completed",
            "description": "Congratulations on your learning consistency!",
            "date": datetime.utcnow().isoformat(),
            "points_earned": 50
        })
    
    # Check for streak achievements
    if student.current_streak >= 7:
        achievements.append({
            "type": "streak",
            "title": f"{student.current_streak} Day Streak",
            "description": "Amazing dedication to learning!",
            "date": datetime.utcnow().isoformat(),
            "points_earned": student.current_streak * 5
        })
    
    return achievements


def _analyze_learning_patterns(student: Student, db: Session) -> Dict[str, Any]:
    """Analyze learning patterns and habits."""
    from backend.models.learning_session import LearningSession
    
    # Get recent sessions
    recent_sessions = db.query(LearningSession).filter(
        LearningSession.student_id == student.id
    ).order_by(LearningSession.started_at.desc()).limit(20).all()
    
    if not recent_sessions:
        return {"patterns": [], "insights": []}
    
    # Analyze session timing patterns
    session_hours = [session.started_at.hour for session in recent_sessions]
    most_active_hour = max(set(session_hours), key=session_hours.count) if session_hours else 12
    
    # Analyze session duration patterns
    durations = [s.duration_minutes for s in recent_sessions if s.duration_minutes]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    patterns = {
        "preferred_study_time": f"{most_active_hour:02d}:00",
        "average_session_duration": avg_duration,
        "consistency_score": min(1.0, len(recent_sessions) / 20),
        "learning_velocity": student.knowledge_level / max(1, student.sessions_completed)
    }
    
    insights = []
    if most_active_hour < 12:
        insights.append("You're a morning learner! Your brain is most active in the AM.")
    elif most_active_hour > 18:
        insights.append("You prefer evening study sessions. Make sure you're well-rested!")
    
    if avg_duration > 45:
        insights.append("You prefer longer, deep study sessions. Remember to take breaks!")
    elif avg_duration < 15:
        insights.append("You like quick learning bursts. Try gradually increasing session length.")
    
    return {"patterns": patterns, "insights": insights}


def _build_category_hierarchy(categories: List) -> Dict[str, Any]:
    """Build hierarchical structure of categories."""
    # This would build a tree structure of categories
    # For now, return a simple structure
    return {
        "root_categories": [cat.name for cat in categories if cat.level == 0],
        "total_levels": max(cat.level for cat in categories) + 1 if categories else 0
    }


def _calculate_period_metrics(tracker_records: List[ProgressTracker]) -> Dict[str, Any]:
    """Calculate metrics for a specific time period."""
    if not tracker_records:
        return {"total_study_time": 0, "sessions_completed": 0, "objectives_mastered": 0}
    
    return {
        "total_study_time": sum(record.total_study_time for record in tracker_records),
        "sessions_completed": sum(record.sessions_completed for record in tracker_records),
        "objectives_mastered": sum(record.objectives_mastered for record in tracker_records),
        "average_accuracy": sum(
            record.average_accuracy for record in tracker_records if record.average_accuracy
        ) / len([r for r in tracker_records if r.average_accuracy]) if tracker_records else 0
    }


def _analyze_progress_trends(tracker_records: List[ProgressTracker]) -> Dict[str, Any]:
    """Analyze progress trends over time."""
    if len(tracker_records) < 2:
        return {"trend": "insufficient_data"}
    
    # Sort by date
    sorted_records = sorted(tracker_records, key=lambda x: x.period_start)
    
    # Calculate trend
    recent_performance = sorted_records[-3:] if len(sorted_records) >= 3 else sorted_records
    earlier_performance = sorted_records[:-3] if len(sorted_records) >= 6 else []
    
    if earlier_performance:
        recent_avg = sum(r.average_accuracy or 0 for r in recent_performance) / len(recent_performance)
        earlier_avg = sum(r.average_accuracy or 0 for r in earlier_performance) / len(earlier_performance)
        
        if recent_avg > earlier_avg + 5:
            trend = "improving"
        elif recent_avg < earlier_avg - 5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {"trend": trend, "data_points": len(tracker_records)}


def _analyze_performance_patterns(student: Student, db: Session, start_date: datetime) -> Dict[str, Any]:
    """Analyze performance patterns for the period."""
    from backend.models.learning_session import LearningSession
    
    sessions = db.query(LearningSession).filter(
        LearningSession.student_id == student.id,
        LearningSession.started_at >= start_date
    ).all()
    
    if not sessions:
        return {"patterns": []}
    
    patterns = []
    
    # Accuracy pattern
    accuracies = [s.accuracy_rate for s in sessions if s.accuracy_rate]
    if accuracies:
        avg_accuracy = sum(accuracies) / len(accuracies)
        if avg_accuracy > 80:
            patterns.append("High accuracy - you're mastering the material well!")
        elif avg_accuracy < 60:
            patterns.append("Consider reviewing fundamentals to improve accuracy")
    
    return {"patterns": patterns}


def _get_period_achievements(student: Student, db: Session, start_date: datetime) -> List[Dict[str, Any]]:
    """Get achievements unlocked during the period."""
    # This would query an achievements table
    # For now, return mock achievements
    return [
        {
            "title": "Consistent Learner",
            "description": "Completed learning sessions for 7 consecutive days",
            "unlocked_date": datetime.utcnow().isoformat(),
            "points_awarded": 100
        }
    ]


def _generate_progress_recommendations(student: Student, tracker_records: List[ProgressTracker]) -> List[str]:
    """Generate recommendations based on progress analysis."""
    recommendations = []
    
    if not tracker_records:
        recommendations.append("Start learning regularly to build momentum")
        return recommendations
    
    # Analyze recent performance
    recent_record = max(tracker_records, key=lambda x: x.period_start)
    
    if recent_record.average_accuracy and recent_record.average_accuracy < 60:
        recommendations.append("Focus on reviewing basic concepts to improve accuracy")
    
    if recent_record.sessions_completed < 5:
        recommendations.append("Try to increase your learning frequency for better retention")
    
    if recent_record.total_study_time < 120:  # Less than 2 hours
        recommendations.append("Consider longer study sessions for deeper learning")
    
    return recommendations
