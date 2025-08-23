"""
AI Tutor Service for intelligent tutoring interactions.

Provides AI-powered tutoring capabilities including question generation,
answer evaluation, personalized feedback, and adaptive content delivery.
"""

# Optional AI imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from typing import Dict, List, Any, Optional
import json
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.core.config import settings
from backend.models.student import Student
from backend.models.learning_session import LearningSession, SessionInteraction
from backend.models.content import Content, ContentType
from backend.models.progress import Progress


class AITutorService:
    """
    AI-powered tutoring service with personalized learning capabilities.
    
    Integrates with OpenAI GPT models to provide intelligent tutoring,
    adaptive questioning, and personalized feedback based on student
    learning patterns and performance history.
    """
    
    def __init__(self):
        """Initialize the AI tutor service with support for multiple providers."""
        self.ai_provider = settings.AI_PROVIDER.lower()
        
        if self.ai_provider == "openai":
            if settings.OPENAI_API_KEY:
                openai.api_key = settings.OPENAI_API_KEY
                self.model = settings.OPENAI_MODEL
            else:
                print("Warning: OpenAI API key not configured. AI features will be limited.")
        elif self.ai_provider == "gemini":
            if settings.GEMINI_API_KEY:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)
            else:
                print("Warning: Gemini API key not configured. AI features will be limited.")
        else:
            print(f"Warning: Unsupported AI provider '{self.ai_provider}'. AI features will be limited.")
        
        self.max_tokens = settings.MAX_TOKENS
        self.temperature = settings.TEMPERATURE
    
    async def generate_response(
        self,
        question: str,
        context: Optional[str] = None,
        student_context: Dict[str, Any] = None,
        subject_area: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an intelligent response to a student's question.
        
        Args:
            question: The student's question
            context: Additional context about the question
            student_context: Student's learning profile and history
            subject_area: The subject area of the question
            
        Returns:
            Dictionary containing response and metadata
        """
        # Build the prompt for the AI tutor
        prompt = self._build_tutor_prompt(
            question=question,
            context=context,
            student_context=student_context,
            subject_area=subject_area
        )
        
        try:
            if self.ai_provider == "openai" and settings.OPENAI_API_KEY:
                # Use OpenAI API
                response = await self._call_openai_api(prompt)
            elif self.ai_provider == "gemini" and settings.GEMINI_API_KEY:
                # Use Gemini API
                response = await self._call_gemini_api(prompt)
            else:
                # Fallback response for development
                response = self._generate_fallback_response(question, student_context)
            
            return self._parse_tutor_response(response)
            
        except Exception as e:
            print(f"Error generating AI response: {e}")
            return self._generate_error_response(question)
    
    async def generate_adaptive_questions(
        self,
        subject_area: str,
        topic: Optional[str] = None,
        difficulty_level: float = 0.5,
        question_count: int = 5,
        question_types: Optional[List[str]] = None,
        student_profile: Optional[Student] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate adaptive questions tailored to student's level.
        
        Args:
            subject_area: The subject area for questions
            topic: Specific topic within the subject
            difficulty_level: Difficulty level (0.0 to 1.0)
            question_count: Number of questions to generate
            question_types: Types of questions (multiple_choice, short_answer, etc.)
            student_profile: Student's learning profile
            
        Returns:
            List of generated questions with metadata
        """
        # Build prompt for question generation
        prompt = self._build_question_generation_prompt(
            subject_area=subject_area,
            topic=topic,
            difficulty_level=difficulty_level,
            question_count=question_count,
            question_types=question_types,
            student_profile=student_profile
        )
        
        try:
            if self.ai_provider == "openai" and settings.OPENAI_API_KEY:
                response = await self._call_openai_api(prompt)
                questions = self._parse_questions_response(response)
            elif self.ai_provider == "gemini" and settings.GEMINI_API_KEY:
                response = await self._call_gemini_api(prompt)
                questions = self._parse_questions_response(response)
            else:
                questions = self._generate_fallback_questions(
                    subject_area, topic, difficulty_level, question_count
                )
            
            return questions
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            return self._generate_fallback_questions(
                subject_area, topic, difficulty_level, question_count
            )
    
    async def evaluate_answer(
        self,
        question_id: str,
        student_answer: str,
        session_context: LearningSession,
        student_profile: Student
    ) -> Dict[str, Any]:
        """
        Evaluate a student's answer and provide feedback.
        
        Args:
            question_id: ID of the question being answered
            student_answer: The student's answer
            session_context: Current learning session context
            student_profile: Student's learning profile
            
        Returns:
            Evaluation results with feedback and explanations
        """
        # Get the original question from session data
        question_data = self._get_question_from_session(question_id, session_context)
        
        if not question_data:
            return {"is_correct": False, "explanation": "Question not found"}
        
        # Build evaluation prompt
        prompt = self._build_evaluation_prompt(
            question_data=question_data,
            student_answer=student_answer,
            student_profile=student_profile
        )
        
        try:
            if self.ai_provider == "openai" and settings.OPENAI_API_KEY:
                response = await self._call_openai_api(prompt)
                evaluation = self._parse_evaluation_response(response, question_data)
            elif self.ai_provider == "gemini" and settings.GEMINI_API_KEY:
                response = await self._call_gemini_api(prompt)
                evaluation = self._parse_evaluation_response(response, question_data)
            else:
                evaluation = self._generate_fallback_evaluation(
                    question_data, student_answer
                )
            
            return evaluation
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return self._generate_fallback_evaluation(question_data, student_answer)
    
    async def get_recent_performance(
        self, student_id: int, db: Session, days: int = 7
    ) -> Dict[str, Any]:
        """Get student's recent performance data."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        recent_sessions = db.query(LearningSession).filter(
            LearningSession.student_id == student_id,
            LearningSession.started_at >= cutoff_date
        ).all()
        
        if not recent_sessions:
            return {"average_accuracy": 0.0, "total_sessions": 0, "improvement_trend": "neutral"}
        
        # Calculate performance metrics
        total_accuracy = sum(s.accuracy_rate for s in recent_sessions if s.accuracy_rate)
        avg_accuracy = total_accuracy / len(recent_sessions) if recent_sessions else 0
        
        # Calculate improvement trend
        if len(recent_sessions) >= 3:
            recent_avg = sum(s.accuracy_rate for s in recent_sessions[-3:] if s.accuracy_rate) / 3
            earlier_avg = sum(s.accuracy_rate for s in recent_sessions[:-3] if s.accuracy_rate) / max(1, len(recent_sessions) - 3)
            
            if recent_avg > earlier_avg + 5:
                trend = "improving"
            elif recent_avg < earlier_avg - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "average_accuracy": avg_accuracy,
            "total_sessions": len(recent_sessions),
            "improvement_trend": trend,
            "last_session_date": recent_sessions[-1].started_at.isoformat() if recent_sessions else None
        }
    
    async def get_next_adaptive_question(
        self,
        session: LearningSession,
        student: Student,
        db: Session
    ) -> Optional[Dict[str, Any]]:
        """Get the next adaptive question for the session."""
        # This would implement logic to select the next best question
        # based on student performance and adaptive algorithms
        
        # For now, return a simple next question
        return {
            "id": f"q_{session.questions_attempted + 1}",
            "question": f"Next adaptive question for {session.subject_area}",
            "type": "multiple_choice",
            "options": ["A", "B", "C", "D"],
            "difficulty": session.difficulty_level_start
        }
    
    def _build_tutor_prompt(
        self,
        question: str,
        context: Optional[str],
        student_context: Dict[str, Any],
        subject_area: Optional[str]
    ) -> str:
        """Build a comprehensive prompt for the AI tutor."""
        prompt = f"""You are an expert AI tutor specializing in personalized education. 

Student Context:
- Current difficulty level: {student_context.get('current_difficulty', 0.5)}
- Learning style: {student_context.get('learning_style', 'mixed')}
- Recent performance: {student_context.get('recent_performance', {})}
- Subject interests: {student_context.get('subject_interests', [])}

Student Question: "{question}"
"""
        
        if context:
            prompt += f"\nAdditional Context: {context}"
        
        if subject_area:
            prompt += f"\nSubject Area: {subject_area}"
        
        prompt += """

Please provide a helpful, encouraging, and educational response that:
1. Directly addresses the student's question
2. Is appropriate for their difficulty level
3. Includes clear explanations and examples
4. Suggests follow-up questions or activities
5. Maintains an encouraging and supportive tone

Format your response as JSON with the following structure:
{
    "response": "Your main response here",
    "confidence_level": 0.9,
    "suggested_actions": ["action1", "action2"],
    "follow_up_questions": ["question1", "question2"],
    "learning_resources": [{"type": "video", "title": "Resource Title", "url": "URL"}]
}"""
        
        return prompt
    
    def _build_question_generation_prompt(
        self,
        subject_area: str,
        topic: Optional[str],
        difficulty_level: float,
        question_count: int,
        question_types: Optional[List[str]],
        student_profile: Optional[Student]
    ) -> str:
        """Build prompt for adaptive question generation."""
        difficulty_desc = self._get_difficulty_description(difficulty_level)
        
        prompt = f"""Generate {question_count} educational questions for:
Subject: {subject_area}
"""
        
        if topic:
            prompt += f"Topic: {topic}\n"
        
        prompt += f"Difficulty Level: {difficulty_desc} ({difficulty_level})\n"
        
        if question_types:
            prompt += f"Question Types: {', '.join(question_types)}\n"
        
        if student_profile:
            prompt += f"""
Student Profile:
- Learning Style: {student_profile.learning_style}
- Current Level: {student_profile.current_difficulty_level}
- Preferences: {student_profile.tutor_personality}
"""
        
        prompt += """
Generate questions that are:
1. Appropriate for the specified difficulty level
2. Educationally meaningful and engaging
3. Clear and well-structured
4. Include correct answers and explanations

Format as JSON array with this structure:
[
    {
        "id": "q1",
        "question": "Question text here",
        "type": "multiple_choice",
        "options": ["A", "B", "C", "D"],
        "correct_answer": "A",
        "explanation": "Why this is correct",
        "difficulty": 0.5,
        "topic": "specific topic",
        "learning_objective": "what this teaches"
    }
]"""
        
        return prompt
    
    def _build_evaluation_prompt(
        self,
        question_data: Dict[str, Any],
        student_answer: str,
        student_profile: Student
    ) -> str:
        """Build prompt for answer evaluation."""
        prompt = f"""Evaluate this student's answer:

Question: {question_data.get('question', '')}
Correct Answer: {question_data.get('correct_answer', '')}
Student Answer: {student_answer}

Student Profile:
- Learning Level: {student_profile.current_difficulty_level}
- Learning Style: {student_profile.learning_style}
- Feedback Preference: {student_profile.feedback_frequency}

Provide evaluation as JSON:
{{
    "is_correct": true/false,
    "explanation": "Detailed explanation for the student",
    "hints": ["hint1", "hint2"],
    "encouragement": "Encouraging message",
    "next_steps": "What to study next"
}}"""
        
        return prompt
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API with the given prompt."""
        try:
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert AI tutor."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            raise
    
    async def _call_gemini_api(self, prompt: str) -> str:
        """Call Google Gemini API with the given prompt."""
        try:
            system_instruction = "You are an expert AI tutor specializing in personalized education."
            full_prompt = f"{system_instruction}\n\n{prompt}"
            
            response = await self.gemini_model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            raise
    
    def _parse_tutor_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI tutor's response."""
        try:
            # Try to parse as JSON first
            return json.loads(response)
        except json.JSONDecodeError:
            # If not JSON, return the response in the expected format
            return {
                "response": response,
                "confidence_level": 0.7,
                "suggested_actions": [],
                "follow_up_questions": [],
                "learning_resources": []
            }
    
    def _parse_questions_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the questions response from AI."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return []
    
    def _parse_evaluation_response(self, response: str, question_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse the evaluation response from AI."""
        try:
            evaluation = json.loads(response)
            evaluation["question_text"] = question_data.get("question", "")
            return evaluation
        except json.JSONDecodeError:
            return {
                "is_correct": False,
                "explanation": "Unable to evaluate answer",
                "hints": [],
                "encouragement": "Keep trying!",
                "question_text": question_data.get("question", "")
            }
    
    def _generate_fallback_response(self, question: str, student_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response when AI is not available."""
        return {
            "response": f"Thank you for your question about '{question}'. I'm here to help you learn! Let me provide some guidance on this topic.",
            "confidence_level": 0.5,
            "suggested_actions": ["Review the relevant materials", "Try some practice exercises"],
            "follow_up_questions": ["Would you like to see some examples?", "Do you need clarification on any part?"],
            "learning_resources": []
        }
    
    def _generate_fallback_questions(
        self, subject_area: str, topic: Optional[str], difficulty_level: float, count: int
    ) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI is not available."""
        questions = []
        for i in range(count):
            questions.append({
                "id": f"fallback_q_{i+1}",
                "question": f"Sample {subject_area} question {i+1}" + (f" about {topic}" if topic else ""),
                "type": "multiple_choice",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Option A",
                "explanation": "This is a sample explanation.",
                "difficulty": difficulty_level,
                "topic": topic or subject_area,
                "learning_objective": f"Practice {subject_area} concepts"
            })
        return questions
    
    def _generate_fallback_evaluation(self, question_data: Dict[str, Any], student_answer: str) -> Dict[str, Any]:
        """Generate fallback evaluation when AI is not available."""
        correct_answer = question_data.get("correct_answer", "")
        is_correct = student_answer.lower().strip() == correct_answer.lower().strip()
        
        return {
            "is_correct": is_correct,
            "explanation": "Great job!" if is_correct else "Let's review this concept together.",
            "hints": ["Review the key concepts", "Think about the fundamental principles"],
            "encouragement": "You're doing well! Keep practicing.",
            "question_text": question_data.get("question", "")
        }
    
    def _generate_error_response(self, question: str) -> Dict[str, Any]:
        """Generate error response when something goes wrong."""
        return {
            "response": "I'm experiencing some technical difficulties. Please try again later.",
            "confidence_level": 0.0,
            "suggested_actions": ["Try rephrasing your question", "Contact support if the issue persists"],
            "follow_up_questions": [],
            "learning_resources": []
        }
    
    def _get_question_from_session(self, question_id: str, session: LearningSession) -> Optional[Dict[str, Any]]:
        """Retrieve question data from session context."""
        # This would normally query the session's stored questions
        # For now, return a mock question
        return {
            "id": question_id,
            "question": "Sample question for evaluation",
            "correct_answer": "Sample correct answer",
            "type": "short_answer"
        }
    
    def _get_difficulty_description(self, difficulty_level: float) -> str:
        """Convert difficulty level to description."""
        if difficulty_level < 0.2:
            return "Very Easy"
        elif difficulty_level < 0.4:
            return "Easy"
        elif difficulty_level < 0.6:
            return "Medium"
        elif difficulty_level < 0.8:
            return "Hard"
        else:
            return "Very Hard"
