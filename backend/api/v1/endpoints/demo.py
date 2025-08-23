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
from backend.services.huggingface_content_generator import hf_content_generator

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
    """Generate comprehensive learning sessions with lessons and quizzes."""
    
    # Educational topics with detailed content
    topics = [
        {
            "subject_area": "Mathematics", 
            "topic": "Algebra - Linear Equations", 
            "session_type": "lesson",
            "lesson_content": {
                "title": "Understanding Linear Equations",
                "introduction": "Linear equations are fundamental in algebra and represent straight lines when graphed.",
                "key_concepts": [
                    "An equation with variables to the first power",
                    "Form: ax + b = c where a ≠ 0",
                    "Solution represents x-intercept"
                ],
                "examples": [
                    {"equation": "2x + 5 = 11", "solution": "x = 3", "steps": ["Subtract 5: 2x = 6", "Divide by 2: x = 3"]},
                    {"equation": "3x - 7 = 14", "solution": "x = 7", "steps": ["Add 7: 3x = 21", "Divide by 3: x = 7"]}
                ]
            },
            "quiz_questions": [
                {
                    "id": 1,
                    "question": "Solve for x: 2x + 8 = 16",
                    "options": ["x = 2", "x = 4", "x = 6", "x = 8"],
                    "correct_answer": "x = 4",
                    "explanation": "Subtract 8 from both sides: 2x = 8, then divide by 2: x = 4"
                },
                {
                    "id": 2,
                    "question": "What is the solution to 5x - 10 = 25?",
                    "options": ["x = 5", "x = 7", "x = 9", "x = 11"],
                    "correct_answer": "x = 7",
                    "explanation": "Add 10 to both sides: 5x = 35, then divide by 5: x = 7"
                }
            ]
        },
        {
            "subject_area": "Science", 
            "topic": "Physics - Newton's Laws", 
            "session_type": "lesson",
            "lesson_content": {
                "title": "Newton's Three Laws of Motion",
                "introduction": "Isaac Newton's laws describe the relationship between forces and motion.",
                "key_concepts": [
                    "First Law: Object at rest stays at rest unless acted upon by force",
                    "Second Law: Force equals mass times acceleration (F = ma)",
                    "Third Law: For every action, there's an equal and opposite reaction"
                ],
                "examples": [
                    {"law": "First Law", "example": "A book on a table remains stationary"},
                    {"law": "Second Law", "example": "Pushing a cart - more force means more acceleration"},
                    {"law": "Third Law", "example": "Walking - you push ground back, ground pushes you forward"}
                ]
            },
            "quiz_questions": [
                {
                    "id": 1,
                    "question": "Which law explains why a passenger jerks forward when a car suddenly stops?",
                    "options": ["Newton's First Law (Inertia)", "Newton's Second Law (F=ma)", "Newton's Third Law (Action-Reaction)", "Law of Gravitation"],
                    "correct_answer": "Newton's First Law (Inertia)",
                    "explanation": "The passenger continues moving forward due to inertia - objects in motion stay in motion unless acted upon by force."
                },
                {
                    "id": 2,
                    "question": "If you apply twice the force to an object of the same mass, what happens to acceleration?",
                    "options": ["Stays the same", "Doubles", "Halves", "Quadruples"],
                    "correct_answer": "Doubles",
                    "explanation": "From F = ma, if force doubles and mass stays constant, acceleration must double."
                }
            ]
        },
        {
            "subject_area": "History", 
            "topic": "American Revolution - Causes", 
            "session_type": "lesson",
            "lesson_content": {
                "title": "Causes of the American Revolution",
                "introduction": "Multiple factors led to the American colonies seeking independence from Britain.",
                "key_concepts": [
                    "Taxation without representation in Parliament",
                    "British laws restricting colonial trade and movement",
                    "Growing sense of American identity and self-governance"
                ],
                "examples": [
                    {"event": "Boston Tea Party (1773)", "significance": "Protest against Tea Act and British taxation"},
                    {"event": "Stamp Act (1765)", "significance": "First direct tax on colonists, sparked organized resistance"},
                    {"event": "Boston Massacre (1770)", "significance": "Increased anti-British sentiment"}
                ]
            },
            "quiz_questions": [
                {
                    "id": 1,
                    "question": "What was the main colonial complaint about British taxation?",
                    "options": ["Taxes were too high", "No representation in Parliament", "Taxes were paid in gold", "Taxes helped Britain's enemies"],
                    "correct_answer": "No representation in Parliament",
                    "explanation": "Colonists objected to 'taxation without representation' - being taxed by a Parliament where they had no voice."
                },
                {
                    "id": 2,
                    "question": "The Boston Tea Party was a response to which British act?",
                    "options": ["Stamp Act", "Sugar Act", "Tea Act", "Intolerable Acts"],
                    "correct_answer": "Tea Act",
                    "explanation": "The Tea Act gave the British East India Company a monopoly on tea sales, prompting the Boston Tea Party protest."
                }
            ]
        },
        {
            "subject_area": "Computer Science", 
            "topic": "Algorithms - Sorting", 
            "session_type": "lesson",
            "lesson_content": {
                "title": "Introduction to Sorting Algorithms",
                "introduction": "Sorting algorithms organize data in a specific order, essential for efficient searching and data processing.",
                "key_concepts": [
                    "Bubble Sort: Compare adjacent elements and swap if needed",
                    "Selection Sort: Find minimum element and place at beginning",
                    "Time complexity measures algorithm efficiency"
                ],
                "examples": [
                    {"algorithm": "Bubble Sort", "example": "[3,1,4,2] → [1,2,3,4] through pairwise swaps"},
                    {"algorithm": "Selection Sort", "example": "Find smallest (1), then next smallest (2), etc."}
                ]
            },
            "quiz_questions": [
                {
                    "id": 1,
                    "question": "What is the time complexity of Bubble Sort in the worst case?",
                    "options": ["O(n)", "O(n log n)", "O(n²)", "O(2^n)"],
                    "correct_answer": "O(n²)",
                    "explanation": "Bubble sort compares each element with every other element, resulting in n² comparisons in worst case."
                },
                {
                    "id": 2,
                    "question": "Which sorting algorithm repeatedly finds the minimum element?",
                    "options": ["Bubble Sort", "Selection Sort", "Quick Sort", "Merge Sort"],
                    "correct_answer": "Selection Sort",
                    "explanation": "Selection sort works by repeatedly selecting the minimum element and placing it in the correct position."
                }
            ]
        }
    ]
    
    sessions = []
    for i, topic in enumerate(topics):
        # Create lesson session
        lesson_session = {
            "id": f"lesson_{i + 1}",
            "session_type": "lesson",
            "subject_area": topic["subject_area"],
            "topic": topic["topic"],
            "status": "available",
            "content": topic["lesson_content"],
            "duration_estimate": random.randint(15, 30),
            "difficulty_level": random.uniform(0.4, 0.8),
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        }
        sessions.append(lesson_session)
        
        # Create corresponding quiz session
        quiz_session = {
            "id": f"quiz_{i + 1}",
            "session_type": "quiz", 
            "subject_area": topic["subject_area"],
            "topic": topic["topic"],
            "status": "available",
            "questions": topic["quiz_questions"],
            "total_questions": len(topic["quiz_questions"]),
            "time_limit_minutes": 10,
            "difficulty_level": random.uniform(0.5, 0.9),
            "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        }
        sessions.append(quiz_session)
    
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
        
        # Generate quiz using Hugging Face model
        quiz = await hf_content_generator.generate_quiz(
            subject=subject,
            topic=topic,
            difficulty_level=difficulty,
            num_questions=num_questions
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

# Demo Quiz Attempt endpoints (no authentication required)
demo_quiz_attempts = {}
demo_attempt_id_counter = 1

@router.post("/quiz/quiz-attempts")
async def create_demo_quiz_attempt(quiz_data: Dict[str, Any]):
    """Create a demo quiz attempt without authentication."""
    global demo_attempt_id_counter
    
    attempt_id = demo_attempt_id_counter
    demo_attempt_id_counter += 1
    
    attempt = {
        "id": attempt_id,
        "quiz_title": quiz_data.get("quiz_title", "Demo Quiz"),
        "subject_area": quiz_data.get("subject_area"),
        "topic": quiz_data.get("topic"),
        "difficulty_level": quiz_data.get("difficulty_level", 0.5),
        "total_questions": len(quiz_data.get("questions", [])),
        "correct_answers": 0,
        "incorrect_answers": 0,
        "skipped_questions": 0,
        "accuracy_percentage": 0.0,
        "completion_percentage": 0.0,
        "status": "in_progress",
        "final_score": None,
        "grade": None,
        "started_at": datetime.now().isoformat(),
        "completed_at": None,
        "questions": quiz_data.get("questions", []),
        "answers": {}
    }
    
    demo_quiz_attempts[attempt_id] = attempt
    
    return attempt

@router.get("/quiz/quiz-attempts")
async def get_demo_quiz_attempts():
    """Get all demo quiz attempts."""
    return list(demo_quiz_attempts.values())

@router.get("/quiz/quiz-attempts/{attempt_id}")
async def get_demo_quiz_attempt(attempt_id: int):
    """Get a specific demo quiz attempt."""
    if attempt_id not in demo_quiz_attempts:
        return {"error": "Quiz attempt not found"}
    
    return demo_quiz_attempts[attempt_id]

@router.post("/quiz/quiz-attempts/{attempt_id}/submit-answer")
async def submit_demo_quiz_answer(attempt_id: int, answer_data: Dict[str, Any]):
    """Submit an answer for a demo quiz attempt."""
    if attempt_id not in demo_quiz_attempts:
        return {"error": "Quiz attempt not found"}
    
    attempt = demo_quiz_attempts[attempt_id]
    question_id = answer_data.get("question_id")
    student_answer = answer_data.get("student_answer")
    
    # Find the question
    question = None
    for q in attempt["questions"]:
        if q.get("question_id") == question_id:
            question = q
            break
    
    if not question:
        return {"error": "Question not found"}
    
    # Check if answer is correct
    correct_answer = question.get("correct_answer")
    is_correct = student_answer == correct_answer
    
    # Store the answer
    attempt["answers"][question_id] = {
        "student_answer": student_answer,
        "is_correct": is_correct,
        "response_time_seconds": answer_data.get("response_time_seconds")
    }
    
    # Update statistics
    if question_id not in [a["question_id"] for a in attempt["answers"].values() if "question_id" in a]:
        if is_correct:
            attempt["correct_answers"] += 1
        else:
            attempt["incorrect_answers"] += 1
    
    # Update completion percentage
    answered_questions = len(attempt["answers"])
    attempt["completion_percentage"] = (answered_questions / attempt["total_questions"]) * 100
    
    # Update accuracy percentage
    if answered_questions > 0:
        attempt["accuracy_percentage"] = (attempt["correct_answers"] / answered_questions) * 100
    
    # Check if quiz is complete
    quiz_completed = answered_questions >= attempt["total_questions"]
    if quiz_completed:
        attempt["status"] = "completed"
        attempt["completed_at"] = datetime.now().isoformat()
        attempt["final_score"] = attempt["accuracy_percentage"]
        
        # Assign grade based on score
        if attempt["final_score"] >= 90:
            attempt["grade"] = "A"
        elif attempt["final_score"] >= 80:
            attempt["grade"] = "B"
        elif attempt["final_score"] >= 70:
            attempt["grade"] = "C"
        elif attempt["final_score"] >= 60:
            attempt["grade"] = "D"
        else:
            attempt["grade"] = "F"
    
    return {
        "is_correct": is_correct,
        "correct_answer": correct_answer,
        "explanation": question.get("explanation"),
        "quiz_completed": quiz_completed,
        "final_score": attempt["final_score"] if quiz_completed else None
    }

@router.post("/quiz/quiz-attempts/{attempt_id}/complete")
async def complete_demo_quiz_attempt(attempt_id: int):
    """Mark a demo quiz attempt as completed."""
    if attempt_id not in demo_quiz_attempts:
        return {"error": "Quiz attempt not found"}
    
    attempt = demo_quiz_attempts[attempt_id]
    attempt["status"] = "completed"
    attempt["completed_at"] = datetime.now().isoformat()
    
    # Calculate final score
    answered_questions = len(attempt["answers"])
    if answered_questions > 0:
        attempt["final_score"] = attempt["accuracy_percentage"]
    else:
        attempt["final_score"] = 0
    
    # Assign grade
    if attempt["final_score"] >= 90:
        attempt["grade"] = "A"
    elif attempt["final_score"] >= 80:
        attempt["grade"] = "B"
    elif attempt["final_score"] >= 70:
        attempt["grade"] = "C"
    elif attempt["final_score"] >= 60:
        attempt["grade"] = "D"
    else:
        attempt["grade"] = "F"
    
    passed = attempt["final_score"] >= 60
    
    return {
        "message": "Quiz completed successfully",
        "final_score": attempt["final_score"],
        "grade": attempt["grade"],
        "passed": passed
    }

@router.get("/quiz/quiz-attempts/{attempt_id}/results")
async def get_demo_quiz_results(attempt_id: int):
    """Get detailed results for a demo quiz attempt."""
    if attempt_id not in demo_quiz_attempts:
        return {"error": "Quiz attempt not found"}
    
    attempt = demo_quiz_attempts[attempt_id]
    
    questions_and_answers = []
    for i, question in enumerate(attempt["questions"]):
        question_id = question.get("question_id")
        answer_info = attempt["answers"].get(question_id, {})
        
        questions_and_answers.append({
            "question_number": i + 1,
            "question_text": question.get("question_text"),
            "answer_options": question.get("answer_options"),
            "correct_answer": question.get("correct_answer"),
            "student_answer": answer_info.get("student_answer"),
            "is_correct": answer_info.get("is_correct", False),
            "explanation": question.get("explanation"),
            "response_time_seconds": answer_info.get("response_time_seconds")
        })
    
    return {
        "quiz_attempt": attempt,
        "questions_and_answers": questions_and_answers
    }

@router.post("/learning/generate-lesson")
async def generate_ai_lesson(lesson_request: Dict[str, Any]):
    """Generate an AI-powered lesson using Hugging Face models."""
    try:
        subject = lesson_request.get("subject", "General Knowledge")
        topic = lesson_request.get("topic", "Mixed Topics")
        difficulty = lesson_request.get("difficulty_level", "intermediate")
        
        # Generate lesson using Hugging Face model
        lesson = await hf_content_generator.generate_lesson(
            subject=subject,
            topic=topic,
            difficulty_level=difficulty
        )
        
        return {
            "success": True,
            "lesson": lesson,
            "message": f"Generated AI lesson about {topic} in {subject}"
        }
        
    except Exception as e:
        logger.error(f"Error generating lesson: {e}")
        # Fallback lesson
        fallback_lesson = {
            "id": f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "subject": lesson_request.get("subject", "General Knowledge"),
            "topic": lesson_request.get("topic", "Mixed Topics"),
            "difficulty_level": lesson_request.get("difficulty_level", "intermediate"),
            "title": f"{lesson_request.get('topic', 'Mixed Topics')} - {lesson_request.get('subject', 'General Knowledge')}",
            "content": f"This comprehensive lesson covers the fundamental concepts of {lesson_request.get('topic', 'Mixed Topics')}. You'll learn key principles, practical applications, and develop a solid understanding of the subject matter.",
            "key_concepts": [
                f"Understanding {lesson_request.get('topic', 'Mixed Topics')}",
                "Practical applications",
                "Problem-solving techniques",
                "Real-world examples"
            ],
            "duration_minutes": 15,
            "learning_objectives": [
                f"Master the basics of {lesson_request.get('topic', 'Mixed Topics')}",
                "Apply concepts to solve problems",
                "Analyze and evaluate different approaches"
            ],
            "created_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "lesson": fallback_lesson,
            "message": f"Generated lesson about {lesson_request.get('topic', 'Mixed Topics')}"
        }
