"""
Demo API endpoints for testing frontend functionality.

Provides mock data and simplified endpoints for immediate functionality.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

from backend.core.database import get_db
from backend.services.ai_quiz_generator import ai_quiz_generator
from backend.services.enhanced_ai_tutor import enhanced_tutor_service

router = APIRouter()

# Mock data generators
def generate_mock_dashboard_data():
    """Generate mock dashboard data."""
    return {
        "student_info": {
            "name": "David",
            "current_level": 0.75,
            "knowledge_score": 0.68,
            "engagement_score": 0.82
        },
        "recent_activity": [
            {
                "session_id": 1,
                "subject": "Mathematics",
                "topic": "Algebra",
                "accuracy": 85.0,
                "duration": 45,
                "date": (datetime.now() - timedelta(days=1)).isoformat()
            },
            {
                "session_id": 2,
                "subject": "Science",
                "topic": "Physics",
                "accuracy": 92.0,
                "duration": 30,
                "date": (datetime.now() - timedelta(days=2)).isoformat()
            }
        ],
        "subject_progress": {
            "Mathematics": {
                "total": 10,
                "mastered": 7,
                "avg_mastery": 0.8,
                "completion_rate": 70
            },
            "Science": {
                "total": 8,
                "mastered": 6,
                "avg_mastery": 0.75,
                "completion_rate": 75
            }
        },
        "achievements": {
            "points_earned": 1250,
            "current_streak": 5,
            "badges": ["Quick Learner", "5-Day Streak"],
            "total_study_time": 480
        },
        "recommendations": [
            {"title": "Advanced Algebra", "type": "next_topic", "difficulty": 0.8},
            {"title": "Geometry Basics", "type": "related", "difficulty": 0.6}
        ],
        "quick_stats": {
            "sessions_this_week": 4,
            "average_accuracy": 88.5,
            "preferred_subjects": ["Mathematics", "Science"]
        }
    }

def generate_mock_progress_overview():
    """Generate mock progress overview data."""
    return {
        "summary": {
            "total_objectives": 24,
            "mastered_objectives": 15,
            "in_progress_objectives": 6,
            "not_started_objectives": 3,
            "overall_mastery_percentage": 68.0,
            "total_study_time": 480.0,
            "average_mastery_level": 0.68
        },
        "subject_progress": [
            {
                "subject_name": "Mathematics",
                "total_objectives": 8,
                "mastered_count": 6,
                "average_mastery": 0.80,
                "completion_percentage": 75.0,
                "study_time_minutes": 180,
                "last_activity": datetime.now().isoformat()
            },
            {
                "subject_name": "Science", 
                "total_objectives": 6,
                "mastered_count": 4,
                "average_mastery": 0.67,
                "completion_percentage": 67.0,
                "study_time_minutes": 120,
                "last_activity": (datetime.now() - timedelta(days=1)).isoformat()
            }
        ],
        "recent_achievements": [
            {
                "type": "streak",
                "title": "5-Day Learning Streak",
                "description": "Maintained consistent learning for 5 days!",
                "date": datetime.now().isoformat(),
                "points_earned": 50
            }
        ],
        "learning_patterns": {
            "patterns": {
                "preferred_study_time": "14:00",
                "average_session_duration": 35,
                "consistency_score": 0.85,
                "learning_velocity": 0.45
            },
            "insights": [
                "You're most productive in the afternoon!",
                "Your session length is optimal for retention."
            ]
        },
        "student_stats": {
            "current_streak": 5,
            "longest_streak": 12,
            "total_points": 1250,
            "sessions_completed": 32,
            "average_session_duration": 35
        }
    }

def generate_mock_learning_sessions():
    """Generate mock learning sessions data."""
    sessions = []
    for i in range(5):
        sessions.append({
            "id": i + 1,
            "session_type": random.choice(["practice", "quiz", "review"]),
            "subject_area": random.choice(["Mathematics", "Science", "History", "English"]),
            "topic": f"Topic {i + 1}",
            "status": random.choice(["completed", "active", "paused"]),
            "questions_attempted": random.randint(5, 15),
            "questions_correct": random.randint(3, 12),
            "accuracy_rate": random.uniform(60, 95),
            "difficulty_level_start": random.uniform(0.3, 0.8),
            "difficulty_level_end": random.uniform(0.4, 0.9),
            "duration_minutes": random.randint(15, 60),
            "engagement_score": random.uniform(0.6, 0.9),
            "hints_used": random.randint(0, 3),
            "completion_percentage": random.uniform(70, 100),
            "started_at": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
            "ended_at": (datetime.now() - timedelta(days=random.randint(0, 7), hours=1)).isoformat()
        })
    return sessions

@router.get("/dashboard")
async def get_demo_dashboard():
    """Get demo dashboard data for immediate functionality."""
    return generate_mock_dashboard_data()

@router.get("/progress/overview")
async def get_demo_progress_overview():
    """Get demo progress overview data."""
    return generate_mock_progress_overview()

@router.get("/learning/sessions")
async def get_demo_learning_sessions():
    """Get demo learning sessions data."""
    return generate_mock_learning_sessions()

@router.post("/learning/sessions")
async def create_demo_learning_session(session_data: Dict[str, Any]):
    """Create a demo learning session."""
    new_session = {
        "id": random.randint(100, 999),
        "session_type": session_data.get("session_type", "practice"),
        "subject_area": session_data.get("subject_area", "General"),
        "topic": session_data.get("topic", "Mixed Topics"),
        "status": "active",
        "questions_attempted": 0,
        "questions_correct": 0,
        "accuracy_rate": 0.0,
        "difficulty_level_start": 0.5,
        "difficulty_level_end": None,
        "duration_minutes": 0,
        "engagement_score": None,
        "hints_used": 0,
        "completion_percentage": 0,
        "started_at": datetime.now().isoformat(),
        "ended_at": None
    }
    return new_session

@router.get("/ai-tutor/suggestions")
async def get_ai_tutor_suggestions():
    """Get AI tutor suggestions."""
    return {
        "suggestions": [
            {
                "title": "Math Help",
                "description": "Get help with mathematical concepts",
                "prompt": "Can you help me understand quadratic equations?",
                "category": "Mathematics"
            },
            {
                "title": "Science Concepts",
                "description": "Explore scientific principles", 
                "prompt": "Explain photosynthesis in simple terms",
                "category": "Science"
            },
            {
                "title": "Study Techniques",
                "description": "Learn effective study methods",
                "prompt": "What are the best memorization techniques?",
                "category": "Study Skills"
            }
        ]
    }

@router.post("/ai-tutor/chat")
async def enhanced_ai_chat(message_data: Dict[str, Any]):
    """Enhanced AI chat endpoint using local AI models."""
    try:
        message = message_data.get("message", "")
        student_id = message_data.get("student_id", 1)  # Default demo student
        context = message_data.get("context", {})
        
        # Use the enhanced AI tutor service
        response = await enhanced_tutor_service.get_tutoring_response(
            student_id=student_id,
            message=message,
            context=context
        )
        
        return response
        
    except Exception as e:
        # Fallback to demo responses
        return await demo_ai_chat_fallback(message_data)

async def demo_ai_chat_fallback(message_data: Dict[str, Any]):
    """Fallback AI chat with demo responses."""
    message = message_data.get("message", "")
    
    # Generate contextual mock response (existing implementation)
    if "math" in message.lower() or "algebra" in message.lower():
        response_text = """Great question about mathematics! Let me help you understand this concept step by step:

🔢 **Key Mathematical Principles:**
1. **Identify the problem type** - What kind of equation or concept are we working with?
2. **Apply the right method** - Use the appropriate mathematical rules and formulas
3. **Work through examples** - Practice makes perfect!

For example, with quadratic equations like ax² + bx + c = 0, we can use:
- Factoring method
- Quadratic formula: x = (-b ± √(b²-4ac)) / 2a
- Completing the square

Would you like me to work through a specific example with you? 📝"""
    
    elif "science" in message.lower() or "physics" in message.lower() or "chemistry" in message.lower():
        response_text = """Excellent science question! Let me break this down scientifically:

🔬 **Scientific Method Approach:**
1. **Observe the phenomenon** - What do we see happening?
2. **Understand the principles** - What scientific laws apply?
3. **See the connections** - How does this relate to everyday life?

Science is all about understanding patterns in nature. Every concept builds on previous knowledge, creating a beautiful web of understanding!

What specific aspect of this topic interests you most? I can dive deeper into any area you'd like to explore! 🧪"""
    
    elif "study" in message.lower() or "learn" in message.lower():
        response_text = """Perfect question about effective learning! Here are some proven study techniques:

📚 **Evidence-Based Study Methods:**

**Active Learning Techniques:**
- **Spaced Repetition** - Review material at increasing intervals
- **Active Recall** - Test yourself without looking at notes
- **Feynman Technique** - Explain concepts in simple terms

**Organization Strategies:**
- Break complex topics into smaller chunks
- Create mind maps and visual connections
- Use the Pomodoro Technique (25-min focused sessions)

**Memory Enhancement:**
- Create meaningful associations and stories
- Use mnemonics for lists and sequences
- Practice retrieval rather than just re-reading

Which learning challenge would you like to tackle first? 🎯"""
    
    elif "quiz" in message.lower() or "test" in message.lower():
        response_text = """I'd love to create a personalized quiz for you! 🎯

**Quiz Options Available:**
- **Mathematics** - Algebra, geometry, calculus
- **Science** - Physics, chemistry, biology
- **History** - World history, specific time periods
- **Language** - Grammar, vocabulary, literature

**Difficulty Levels:**
- 🟢 Beginner - Build foundational understanding
- 🟡 Intermediate - Apply concepts and solve problems  
- 🔴 Advanced - Complex analysis and critical thinking

What subject and difficulty level would you prefer? I'll generate questions tailored to your learning goals! 

Just say something like "Create a math quiz" or "I want a science test" and I'll get started! 📝"""
    
    else:
        response_text = f"""Thanks for your question about "{message}"! Let me help you understand this better.

🎓 **Learning Approach:**
This is an interesting topic that connects to several key concepts. Let me break it down:

**Key Points to Consider:**
- Understanding the fundamentals is crucial
- Real-world applications help cement learning
- Practice and repetition build mastery

**Next Steps:**
- We can explore specific aspects in detail
- I can provide examples and practice problems
- We can connect this to other related topics

What specific aspect would you like to dive deeper into? I'm here to help you master this concept! 💡"""
    
    return {
        "response": response_text,
        "confidence": 0.85,
        "recommendations": [
            {"title": "Related Practice", "type": "exercise"},
            {"title": "Advanced Topics", "type": "next_level"}
        ],
        "follow_up_questions": [
            "Would you like to try a practice problem?",
            "Should we explore related concepts?",
            "Do you want me to explain this differently?"
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.post("/quiz/generate")
async def generate_ai_quiz(quiz_request: Dict[str, Any]):
    """Generate an AI-powered quiz using local models."""
    try:
        subject = quiz_request.get("subject", "General Knowledge")
        topic = quiz_request.get("topic", "Mixed Topics")
        difficulty = quiz_request.get("difficulty_level", "intermediate")
        num_questions = quiz_request.get("num_questions", 5)
        question_types = quiz_request.get("question_types", ["multiple_choice"])
        
        # Generate quiz using AI
        quiz = await ai_quiz_generator.generate_quiz(
            subject=subject,
            topic=topic,
            difficulty_level=difficulty,
            num_questions=num_questions,
            question_types=question_types
        )
        
        return {
            "success": True,
            "quiz": quiz,
            "message": f"Generated {len(quiz['questions'])} questions about {topic} in {subject}"
        }
        
    except Exception as e:
        # Return fallback quiz on error
        fallback_quiz = {
            "quiz_id": f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "subject": quiz_request.get("subject", "General Knowledge"),
            "topic": quiz_request.get("topic", "Mixed Topics"),
            "difficulty_level": quiz_request.get("difficulty_level", "intermediate"),
            "questions": [
                {
                    "id": 1,
                    "type": "multiple_choice",
                    "question": "What is the most effective way to learn new concepts?",
                    "options": {
                        "A": "Active practice and application",
                        "B": "Passive reading only",
                        "C": "Memorization without understanding",
                        "D": "Avoiding challenging material"
                    },
                    "correct_answer": "A",
                    "explanation": "Active practice and application help reinforce learning and improve retention.",
                    "points": 1
                }
            ],
            "total_questions": 1,
            "estimated_time": 2,
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "quiz": fallback_quiz,
            "message": "Generated fallback quiz (AI service temporarily unavailable)",
            "warning": f"AI generation error: {str(e)}"
        }

@router.post("/quiz/adaptive")
async def generate_adaptive_quiz(request_data: Dict[str, Any]):
    """Generate an adaptive quiz based on student performance."""
    try:
        student_performance = request_data.get("performance", {
            "average_score": 0.7,
            "weak_topics": ["problem solving", "advanced concepts"]
        })
        subject = request_data.get("subject", "Mathematics")
        topic = request_data.get("topic", "General")
        
        # Generate adaptive questions
        questions = await ai_quiz_generator.generate_adaptive_questions(
            student_performance=student_performance,
            subject=subject,
            topic=topic
        )
        
        return {
            "success": True,
            "questions": questions,
            "total_questions": len(questions),
            "message": f"Generated {len(questions)} adaptive questions",
            "performance_analysis": {
                "difficulty": ai_quiz_generator._determine_difficulty(student_performance),
                "weak_areas": ai_quiz_generator._identify_weak_areas(student_performance)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "questions": [],
            "message": "Failed to generate adaptive quiz"
        }

@router.post("/study-plan/generate")
async def generate_study_plan(plan_request: Dict[str, Any]):
    """Generate a personalized study plan using AI."""
    try:
        student_id = plan_request.get("student_id", 1)
        subject = plan_request.get("subject", "General Studies")
        goals = plan_request.get("goals", ["Improve understanding", "Practice regularly"])
        timeframe_days = plan_request.get("timeframe_days", 30)
        
        # Generate study plan using enhanced AI tutor
        study_plan = await enhanced_tutor_service.generate_study_plan(
            student_id=student_id,
            subject=subject,
            goals=goals,
            timeframe_days=timeframe_days
        )
        
        return study_plan
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "study_plan": "I'm having trouble creating your study plan right now. Try starting with basic concepts and gradually building complexity.",
            "message": "Failed to generate study plan"
        }

@router.get("/ai-models/status")
async def get_ai_models_status():
    """Get the status of available AI models and providers."""
    try:
        from backend.services.ai_models import ai_model_manager
        
        provider_info = ai_model_manager.get_provider_info()
        
        return {
            "status": "operational",
            "providers": provider_info,
            "capabilities": {
                "text_generation": True,
                "quiz_generation": True,
                "tutoring": True,
                "study_planning": True,
                "local_models": provider_info.get("transformers_available", False)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "capabilities": {
                "text_generation": False,
                "quiz_generation": False,
                "tutoring": False,
                "study_planning": False,
                "local_models": False
            },
            "timestamp": datetime.now().isoformat()
        }

@router.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Demo API endpoints are working!"
    }
