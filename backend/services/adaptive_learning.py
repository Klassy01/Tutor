"""
Adaptive Learning Engine for personalized learning optimization.

Implements sophisticated adaptive learning algorithms that adjust
difficulty, content selection, and pacing based on student performance,
engagement patterns, and learning preferences.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json

from backend.models.student import Student
from backend.models.learning_session import LearningSession, SessionInteraction
from backend.models.content import Content, LearningObjective
from backend.models.progress import Progress, ProgressTracker, EngagementMetrics
from backend.core.config import settings


class AdaptiveLearningEngine:
    """
    Advanced adaptive learning engine with machine learning capabilities.
    
    Implements multiple adaptive algorithms including:
    - Difficulty adjustment based on performance
    - Content recommendation using collaborative filtering
    - Spaced repetition for knowledge retention
    - Engagement-based pacing adjustments
    - Personalized learning path generation
    """
    
    def __init__(self):
        """Initialize the adaptive learning engine."""
        self.difficulty_adjustment_rate = settings.DIFFICULTY_ADJUSTMENT_RATE
        self.min_difficulty = settings.MIN_DIFFICULTY
        self.max_difficulty = settings.MAX_DIFFICULTY
        
        # Learning algorithm parameters
        self.mastery_threshold = 0.8
        self.engagement_weight = 0.3
        self.performance_weight = 0.7
        self.retention_factor = 0.1
    
    async def update_student_model(
        self,
        student: Student,
        interaction: SessionInteraction,
        db: Session
    ) -> Dict[str, Any]:
        """
        Update the student's learning model based on a new interaction.
        
        Args:
            student: The student whose model to update
            interaction: The latest learning interaction
            db: Database session
            
        Returns:
            Dictionary containing model updates and recommendations
        """
        # Update difficulty level
        difficulty_update = self._calculate_difficulty_adjustment(student, interaction)
        student.current_difficulty_level = max(
            self.min_difficulty,
            min(self.max_difficulty, student.current_difficulty_level + difficulty_update)
        )
        
        # Update knowledge level
        knowledge_update = self._calculate_knowledge_update(student, interaction)
        student.knowledge_level = max(0.0, min(1.0, student.knowledge_level + knowledge_update))
        
        # Update engagement score
        engagement_update = self._calculate_engagement_update(student, interaction)
        student.engagement_score = max(0.0, min(1.0, student.engagement_score + engagement_update))
        
        # Update progress records
        progress_updates = await self._update_progress_records(student, interaction, db)
        
        # Generate personalized recommendations
        recommendations = await self._generate_adaptive_recommendations(student, db)
        
        db.commit()
        
        return {
            "difficulty_adjustment": difficulty_update,
            "knowledge_update": knowledge_update,
            "engagement_update": engagement_update,
            "progress_updates": progress_updates,
            "recommendations": recommendations,
            "next_difficulty_level": student.current_difficulty_level
        }
    
    async def calculate_progress_update(
        self,
        student: Student,
        interaction: SessionInteraction,
        db: Session
    ) -> Dict[str, Any]:
        """Calculate detailed progress updates for the student."""
        # Get or create progress record
        progress = db.query(Progress).filter(
            Progress.student_id == student.id,
            Progress.learning_objective_id == interaction.learning_objective_id
        ).first()
        
        if not progress:
            progress = Progress(
                student_id=student.id,
                learning_objective_id=interaction.learning_objective_id,
                content_id=interaction.content_id
            )
            db.add(progress)
        
        # Calculate performance score for this interaction
        performance_score = self._calculate_performance_score(interaction)
        
        # Update progress
        time_spent = interaction.response_time_seconds or 0
        progress.update_progress(performance_score, time_spent / 60.0)  # Convert to minutes
        
        # Calculate mastery level change
        mastery_change = self._calculate_mastery_change(progress, performance_score)
        
        return {
            "mastery_level": progress.mastery_level,
            "mastery_change": mastery_change,
            "status": progress.status,
            "completion_percentage": progress.completion_percentage,
            "is_mastered": progress.is_mastered,
            "needs_review": progress.needs_review,
            "next_review_date": progress.next_review_date.isoformat() if progress.next_review_date else None
        }
    
    async def generate_session_summary(
        self,
        session: LearningSession,
        student: Student,
        db: Session
    ) -> Dict[str, Any]:
        """Generate a comprehensive session summary with insights."""
        # Calculate session metrics
        session_metrics = self._calculate_session_metrics(session)
        
        # Analyze learning patterns
        learning_patterns = await self._analyze_learning_patterns(student, session, db)
        
        # Generate recommendations
        recommendations = await self._generate_session_recommendations(
            session, student, learning_patterns, db
        )
        
        # Calculate knowledge gains
        knowledge_gained = self._estimate_knowledge_gains(session, student)
        
        return {
            "session_metrics": session_metrics,
            "learning_patterns": learning_patterns,
            "recommendations": recommendations,
            "knowledge_gained": knowledge_gained,
            "performance_analysis": {
                "strengths": learning_patterns.get("strengths", []),
                "areas_for_improvement": learning_patterns.get("weaknesses", []),
                "optimal_difficulty": self._calculate_optimal_difficulty(student, session)
            }
        }
    
    async def generate_personalized_recommendations(
        self,
        student: Student,
        db: Session,
        recommendation_count: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate personalized learning recommendations for the student."""
        # Get student's learning history
        learning_history = await self._get_learning_history(student, db)
        
        # Analyze knowledge gaps
        knowledge_gaps = await self._identify_knowledge_gaps(student, db)
        
        # Get content recommendations
        content_recommendations = await self._recommend_content(student, knowledge_gaps, db)
        
        # Generate activity recommendations
        activity_recommendations = await self._recommend_activities(student, learning_history, db)
        
        # Combine and prioritize recommendations
        all_recommendations = content_recommendations + activity_recommendations
        prioritized = self._prioritize_recommendations(all_recommendations, student)
        
        return prioritized[:recommendation_count]
    
    async def get_learning_objectives(
        self, subject_area: str, topic: Optional[str], db: Session
    ) -> List[LearningObjective]:
        """Get relevant learning objectives for a subject and topic."""
        query = db.query(LearningObjective).join(LearningObjective.category)
        
        if topic:
            # Filter by specific topic
            query = query.filter(LearningObjective.category.has(name=topic))
        else:
            # Filter by subject area (assuming it's a parent category)
            query = query.filter(
                LearningObjective.category.has(parent_id__in=
                    db.query(LearningObjective.category.id).filter(
                        LearningObjective.category.name == subject_area
                    ).subquery()
                )
            )
        
        return query.filter(LearningObjective.is_active == True).all()
    
    def _calculate_difficulty_adjustment(
        self, student: Student, interaction: SessionInteraction
    ) -> float:
        """Calculate how much to adjust the student's difficulty level."""
        performance_score = self._calculate_performance_score(interaction)
        current_difficulty = student.current_difficulty_level
        
        # Calculate base adjustment
        if performance_score > 0.8:
            # Increase difficulty for excellent performance
            base_adjustment = self.difficulty_adjustment_rate
        elif performance_score < 0.4:
            # Decrease difficulty for poor performance
            base_adjustment = -self.difficulty_adjustment_rate
        else:
            # No adjustment for moderate performance
            base_adjustment = 0.0
        
        # Modify based on response time (if available)
        if interaction.response_time_seconds:
            expected_time = 30.0  # 30 seconds expected per question
            time_factor = expected_time / interaction.response_time_seconds
            
            if time_factor > 1.5:  # Much faster than expected
                base_adjustment += 0.02
            elif time_factor < 0.5:  # Much slower than expected
                base_adjustment -= 0.02
        
        # Consider hint usage
        if interaction.hint_used:
            base_adjustment -= 0.01
        
        # Ensure adjustment doesn't exceed bounds
        new_difficulty = current_difficulty + base_adjustment
        if new_difficulty < self.min_difficulty:
            return self.min_difficulty - current_difficulty
        elif new_difficulty > self.max_difficulty:
            return self.max_difficulty - current_difficulty
        
        return base_adjustment
    
    def _calculate_knowledge_update(
        self, student: Student, interaction: SessionInteraction
    ) -> float:
        """Calculate knowledge level update based on interaction."""
        performance_score = self._calculate_performance_score(interaction)
        
        # Knowledge gain is proportional to performance and difficulty
        difficulty_factor = interaction.difficulty_level or student.current_difficulty_level
        knowledge_gain = performance_score * difficulty_factor * 0.05  # Small incremental gains
        
        return knowledge_gain
    
    def _calculate_engagement_update(
        self, student: Student, interaction: SessionInteraction
    ) -> float:
        """Calculate engagement score update based on interaction."""
        engagement_factors = []
        
        # Response time factor (not too fast, not too slow)
        if interaction.response_time_seconds:
            ideal_time = 30.0
            time_ratio = min(interaction.response_time_seconds / ideal_time, 2.0)
            time_engagement = 1.0 - abs(1.0 - time_ratio)
            engagement_factors.append(time_engagement)
        
        # Confidence factor
        if interaction.confidence_level:
            engagement_factors.append(interaction.confidence_level)
        
        # Hint usage (seeking help shows engagement)
        if interaction.hint_used:
            engagement_factors.append(0.8)  # Moderate positive engagement
        
        # Revision factor (thinking about answer)
        if interaction.revision_count > 0:
            engagement_factors.append(min(0.9, 0.6 + interaction.revision_count * 0.1))
        
        if engagement_factors:
            new_engagement = sum(engagement_factors) / len(engagement_factors)
            current_engagement = student.engagement_score
            
            # Smooth transition
            return (new_engagement - current_engagement) * 0.1
        
        return 0.0
    
    def _calculate_performance_score(self, interaction: SessionInteraction) -> float:
        """Calculate a comprehensive performance score for an interaction."""
        base_score = 1.0 if interaction.is_correct else 0.0
        
        # Adjust based on attempts (multiple attempts reduce score)
        if interaction.attempts_count > 1:
            attempt_penalty = (interaction.attempts_count - 1) * 0.1
            base_score = max(0.0, base_score - attempt_penalty)
        
        # Adjust based on hint usage
        if interaction.hint_used:
            base_score = max(0.0, base_score - 0.1)
        
        # Adjust based on response time (if reasonable)
        if interaction.response_time_seconds:
            expected_time = 30.0
            if interaction.response_time_seconds > expected_time * 3:
                # Very slow response
                base_score = max(0.0, base_score - 0.1)
        
        return base_score
    
    def _calculate_mastery_change(self, progress: Progress, performance_score: float) -> float:
        """Calculate the change in mastery level."""
        old_mastery = progress.mastery_level
        
        # Simulate the mastery update (this would be called after progress.update_progress)
        # This is a simplified version of the logic in Progress._update_mastery_level
        score_weight = 0.3
        consistency_weight = 0.7
        
        if progress.attempts_count > 1:
            consistency_component = min(1.0, (progress.average_score + performance_score) / 2)
        else:
            consistency_component = performance_score
        
        new_mastery = (performance_score * score_weight + consistency_component * consistency_weight)
        
        if old_mastery > 0:
            final_mastery = (old_mastery * 0.7 + new_mastery * 0.3)
        else:
            final_mastery = new_mastery
        
        return final_mastery - old_mastery
    
    async def _update_progress_records(
        self, student: Student, interaction: SessionInteraction, db: Session
    ) -> List[Dict[str, Any]]:
        """Update all relevant progress records."""
        updates = []
        
        # Update content progress if content_id is available
        if interaction.content_id:
            content_progress = db.query(Progress).filter(
                Progress.student_id == student.id,
                Progress.content_id == interaction.content_id
            ).first()
            
            if not content_progress:
                content_progress = Progress(
                    student_id=student.id,
                    content_id=interaction.content_id
                )
                db.add(content_progress)
            
            performance_score = self._calculate_performance_score(interaction)
            time_spent = (interaction.response_time_seconds or 0) / 60.0
            content_progress.update_progress(performance_score, time_spent)
            
            updates.append({
                "type": "content",
                "id": interaction.content_id,
                "mastery_level": content_progress.mastery_level,
                "status": content_progress.status
            })
        
        # Update learning objective progress
        if interaction.learning_objective_id:
            objective_progress = db.query(Progress).filter(
                Progress.student_id == student.id,
                Progress.learning_objective_id == interaction.learning_objective_id
            ).first()
            
            if not objective_progress:
                objective_progress = Progress(
                    student_id=student.id,
                    learning_objective_id=interaction.learning_objective_id
                )
                db.add(objective_progress)
            
            performance_score = self._calculate_performance_score(interaction)
            time_spent = (interaction.response_time_seconds or 0) / 60.0
            objective_progress.update_progress(performance_score, time_spent)
            
            updates.append({
                "type": "objective",
                "id": interaction.learning_objective_id,
                "mastery_level": objective_progress.mastery_level,
                "status": objective_progress.status
            })
        
        return updates
    
    async def _generate_adaptive_recommendations(
        self, student: Student, db: Session
    ) -> List[Dict[str, Any]]:
        """Generate adaptive recommendations based on student model updates."""
        recommendations = []
        
        # Difficulty-based recommendations
        if student.current_difficulty_level < 0.3:
            recommendations.append({
                "type": "difficulty",
                "message": "Consider reviewing fundamental concepts before advancing",
                "action": "review_basics"
            })
        elif student.current_difficulty_level > 0.8:
            recommendations.append({
                "type": "difficulty", 
                "message": "You're ready for more challenging material!",
                "action": "advance_difficulty"
            })
        
        # Engagement-based recommendations
        if student.engagement_score < 0.4:
            recommendations.append({
                "type": "engagement",
                "message": "Try shorter study sessions or different content types",
                "action": "adjust_pacing"
            })
        
        # Knowledge-based recommendations
        if student.knowledge_level > 0.7:
            recommendations.append({
                "type": "knowledge",
                "message": "Great progress! Consider exploring advanced topics",
                "action": "explore_advanced"
            })
        
        return recommendations
    
    def _calculate_session_metrics(self, session: LearningSession) -> Dict[str, Any]:
        """Calculate comprehensive session metrics."""
        return {
            "efficiency": session.accuracy_rate / max(1, session.questions_attempted) if session.questions_attempted else 0,
            "persistence": 1.0 - (session.hints_used / max(1, session.questions_attempted)),
            "improvement": session.difficulty_level_end - session.difficulty_level_start if session.difficulty_level_end else 0,
            "engagement_rating": session.engagement_score or 0.5,
            "time_efficiency": session.questions_attempted / max(1, session.duration_minutes or 1)
        }
    
    async def _analyze_learning_patterns(
        self, student: Student, session: LearningSession, db: Session
    ) -> Dict[str, Any]:
        """Analyze learning patterns from the session."""
        patterns = {
            "strengths": [],
            "weaknesses": [],
            "preferences": []
        }
        
        # Analyze accuracy patterns
        if session.accuracy_rate and session.accuracy_rate > 80:
            patterns["strengths"].append("High accuracy")
        elif session.accuracy_rate and session.accuracy_rate < 50:
            patterns["weaknesses"].append("Low accuracy - consider reviewing concepts")
        
        # Analyze pacing
        if session.duration_minutes and session.questions_attempted:
            avg_time_per_question = session.duration_minutes / session.questions_attempted
            if avg_time_per_question < 1:
                patterns["preferences"].append("Fast-paced learning")
            elif avg_time_per_question > 5:
                patterns["preferences"].append("Thoughtful, deliberate approach")
        
        # Analyze hint usage
        if session.hints_used == 0:
            patterns["strengths"].append("Independent problem solving")
        elif session.hints_used > session.questions_attempted / 2:
            patterns["preferences"].append("Benefits from guidance and hints")
        
        return patterns
    
    async def _generate_session_recommendations(
        self,
        session: LearningSession,
        student: Student,
        learning_patterns: Dict[str, Any],
        db: Session
    ) -> List[str]:
        """Generate specific recommendations based on session analysis."""
        recommendations = []
        
        # Performance-based recommendations
        if session.accuracy_rate and session.accuracy_rate < 60:
            recommendations.append("Review the fundamental concepts before continuing")
            recommendations.append("Consider working through additional practice problems")
        
        # Pacing recommendations
        if session.duration_minutes and session.duration_minutes < 10:
            recommendations.append("Consider taking more time to think through problems")
        elif session.duration_minutes and session.duration_minutes > 60:
            recommendations.append("Try shorter, more focused study sessions")
        
        # Engagement recommendations
        if session.engagement_score and session.engagement_score < 0.4:
            recommendations.append("Try different types of content to maintain interest")
            recommendations.append("Take breaks to maintain focus")
        
        return recommendations
    
    def _estimate_knowledge_gains(self, session: LearningSession, student: Student) -> float:
        """Estimate knowledge gained from the session."""
        if not session.accuracy_rate or not session.questions_attempted:
            return 0.0
        
        # Base knowledge gain from correct answers
        base_gain = (session.questions_correct / 100.0) * session.difficulty_level_start
        
        # Bonus for improvement during session
        if session.difficulty_level_end and session.difficulty_level_start:
            improvement_bonus = (session.difficulty_level_end - session.difficulty_level_start) * 0.5
            base_gain += improvement_bonus
        
        return min(0.1, base_gain)  # Cap at 10% knowledge gain per session
    
    def _calculate_optimal_difficulty(self, student: Student, session: LearningSession) -> float:
        """Calculate the optimal difficulty level for the student."""
        current_difficulty = student.current_difficulty_level
        
        # Adjust based on session performance
        if session.accuracy_rate:
            if session.accuracy_rate > 85:
                optimal = min(1.0, current_difficulty + 0.1)
            elif session.accuracy_rate < 50:
                optimal = max(0.1, current_difficulty - 0.1)
            else:
                optimal = current_difficulty
        else:
            optimal = current_difficulty
        
        return optimal
    
    async def _get_learning_history(self, student: Student, db: Session) -> Dict[str, Any]:
        """Get comprehensive learning history for the student."""
        # Get recent sessions
        recent_sessions = db.query(LearningSession).filter(
            LearningSession.student_id == student.id
        ).order_by(LearningSession.started_at.desc()).limit(10).all()
        
        # Calculate trends
        if len(recent_sessions) >= 3:
            recent_accuracy = [s.accuracy_rate for s in recent_sessions[:3] if s.accuracy_rate]
            earlier_accuracy = [s.accuracy_rate for s in recent_sessions[3:6] if s.accuracy_rate]
            
            if recent_accuracy and earlier_accuracy:
                trend = "improving" if np.mean(recent_accuracy) > np.mean(earlier_accuracy) else "stable"
            else:
                trend = "insufficient_data"
        else:
            trend = "insufficient_data"
        
        return {
            "total_sessions": len(recent_sessions),
            "performance_trend": trend,
            "favorite_subjects": self._identify_favorite_subjects(recent_sessions),
            "challenging_areas": self._identify_challenging_areas(recent_sessions)
        }
    
    async def _identify_knowledge_gaps(self, student: Student, db: Session) -> List[Dict[str, Any]]:
        """Identify knowledge gaps based on progress data."""
        # Get progress records with low mastery
        low_mastery_progress = db.query(Progress).filter(
            Progress.student_id == student.id,
            Progress.mastery_level < 0.6
        ).all()
        
        gaps = []
        for progress in low_mastery_progress:
            if progress.learning_objective:
                gaps.append({
                    "type": "objective",
                    "id": progress.learning_objective_id,
                    "title": progress.learning_objective.title,
                    "mastery_level": progress.mastery_level,
                    "priority": 1.0 - progress.mastery_level
                })
        
        # Sort by priority (lowest mastery first)
        gaps.sort(key=lambda x: x["priority"], reverse=True)
        
        return gaps
    
    async def _recommend_content(
        self, student: Student, knowledge_gaps: List[Dict[str, Any]], db: Session
    ) -> List[Dict[str, Any]]:
        """Recommend content based on knowledge gaps and student preferences."""
        recommendations = []
        
        for gap in knowledge_gaps[:3]:  # Top 3 gaps
            # Find content for this learning objective
            if gap["type"] == "objective":
                content_items = db.query(Content).join(
                    Content.learning_objectives
                ).filter(
                    LearningObjective.id == gap["id"],
                    Content.is_published == True,
                    Content.is_active == True
                ).all()
                
                for content in content_items:
                    if content.is_accessible_for_difficulty(student.current_difficulty_level):
                        recommendations.append({
                            "type": "content",
                            "content_id": content.id,
                            "title": content.title,
                            "content_type": content.content_type.value,
                            "priority": gap["priority"],
                            "reason": f"Addresses knowledge gap in {gap['title']}"
                        })
        
        return recommendations
    
    async def _recommend_activities(
        self, student: Student, learning_history: Dict[str, Any], db: Session
    ) -> List[Dict[str, Any]]:
        """Recommend learning activities based on student history and preferences."""
        recommendations = []
        
        # Recommend review sessions for spaced repetition
        recommendations.append({
            "type": "activity",
            "activity": "review_session",
            "title": "Review Previous Topics",
            "priority": 0.7,
            "reason": "Reinforce learning through spaced repetition"
        })
        
        # Recommend practice based on performance trend
        if learning_history.get("performance_trend") == "improving":
            recommendations.append({
                "type": "activity",
                "activity": "challenge_exercise",
                "title": "Challenge Exercise",
                "priority": 0.8,
                "reason": "You're improving! Ready for a challenge"
            })
        
        return recommendations
    
    def _prioritize_recommendations(
        self, recommendations: List[Dict[str, Any]], student: Student
    ) -> List[Dict[str, Any]]:
        """Prioritize recommendations based on student needs and preferences."""
        # Sort by priority score
        recommendations.sort(key=lambda x: x.get("priority", 0.5), reverse=True)
        
        # Apply student preference filters
        if student.learning_style == "visual":
            # Boost visual content
            for rec in recommendations:
                if rec.get("content_type") in ["video", "interactive"]:
                    rec["priority"] = rec.get("priority", 0.5) + 0.1
        
        # Re-sort after preference adjustments
        recommendations.sort(key=lambda x: x.get("priority", 0.5), reverse=True)
        
        return recommendations
    
    def _identify_favorite_subjects(self, sessions: List[LearningSession]) -> List[str]:
        """Identify subjects the student performs well in."""
        subject_performance = {}
        
        for session in sessions:
            if session.subject_area and session.accuracy_rate:
                if session.subject_area not in subject_performance:
                    subject_performance[session.subject_area] = []
                subject_performance[session.subject_area].append(session.accuracy_rate)
        
        # Calculate average performance per subject
        avg_performance = {}
        for subject, scores in subject_performance.items():
            avg_performance[subject] = np.mean(scores)
        
        # Return subjects sorted by performance
        sorted_subjects = sorted(avg_performance.items(), key=lambda x: x[1], reverse=True)
        return [subject for subject, _ in sorted_subjects[:3]]
    
    def _identify_challenging_areas(self, sessions: List[LearningSession]) -> List[str]:
        """Identify subjects the student finds challenging."""
        subject_performance = {}
        
        for session in sessions:
            if session.subject_area and session.accuracy_rate:
                if session.subject_area not in subject_performance:
                    subject_performance[session.subject_area] = []
                subject_performance[session.subject_area].append(session.accuracy_rate)
        
        # Calculate average performance per subject
        avg_performance = {}
        for subject, scores in subject_performance.items():
            avg_performance[subject] = np.mean(scores)
        
        # Return subjects with low performance
        challenging = [subject for subject, score in avg_performance.items() if score < 60]
        return challenging[:3]
