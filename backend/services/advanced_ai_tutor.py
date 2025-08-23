"""
Advanced AI Tutor Service with LangChain Integration.

This module provides sophisticated AI tutoring capabilities using LangChain
for orchestrating different AI models and tools.
"""

from typing import Dict, List, Optional, Any
from langchain_community.llms import HuggingFacePipeline
try:
    from langchain.chains import ConversationChain, LLMChain
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.prompts import PromptTemplate
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback when langchain has compatibility issues
    ConversationChain = None
    LLMChain = None
    ConversationBufferWindowMemory = None
    PromptTemplate = None
    BaseMessage = None
    HumanMessage = None
    AIMessage = None
    LANGCHAIN_AVAILABLE = False
import asyncio
from datetime import datetime
import json
import logging

from backend.core.config import settings
from backend.services.ai_models import (
    get_gemini_response,
    get_openai_response,
    get_huggingface_response
)
from backend.services.recommendation_engine import RecommendationEngine
from backend.models.learning_session import LearningSession
from backend.models.student import Student

logger = logging.getLogger(__name__)


class AdvancedAITutorService:
    """
    Advanced AI Tutor Service with adaptive learning capabilities.
    
    Uses LangChain to orchestrate multiple AI models and provide
    personalized tutoring experiences.
    """
    
    def __init__(self):
        # Initialize conversation memory with fallback
        self.memory = None
        if LANGCHAIN_AVAILABLE and ConversationBufferWindowMemory:
            try:
                self.memory = ConversationBufferWindowMemory(k=10)
            except Exception as e:
                logger.warning(f"Failed to initialize LangChain memory: {e}")
                self.memory = None
        
        if not self.memory:
            # Simple fallback memory implementation
            self.conversation_history: List[Dict[str, str]] = []
        self.recommendation_engine = RecommendationEngine()
        self.conversation_chains = {}
        self._initialize_chains()
    
    def _initialize_chains(self):
        """Initialize LangChain conversation chains for different purposes."""
        
        # Tutoring conversation chain
        tutor_template = """
        You are an advanced AI tutor specializing in personalized education. Your role is to:
        1. Provide clear, engaging explanations adapted to the student's level
        2. Ask thought-provoking questions to enhance understanding
        3. Offer encouragement and positive feedback
        4. Adapt your teaching style based on student responses
        5. Suggest relevant exercises and learning materials
        
        Student Level: {difficulty_level}
        Learning Style: {learning_style}
        Subject Focus: {subject}
        
        Previous conversation:
        {history}
        
        Student: {input}
        AI Tutor:"""
        
        self.tutor_prompt = PromptTemplate(
            input_variables=["difficulty_level", "learning_style", "subject", "history", "input"],
            template=tutor_template
        )
        
        # Quiz generation chain
        quiz_template = """
        Generate a multiple-choice quiz question for the following topic.
        Make it appropriate for the specified difficulty level.
        
        Topic: {topic}
        Difficulty Level: {difficulty_level} (0.0 = very easy, 1.0 = very hard)
        Number of Options: {num_options}
        
        Format your response as JSON:
        {{
            "question": "The question text",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "A",
            "explanation": "Detailed explanation of why this is correct"
        }}
        
        Quiz Question:"""
        
        self.quiz_prompt = PromptTemplate(
            input_variables=["topic", "difficulty_level", "num_options"],
            template=quiz_template
        )
        
        # Content summary chain
        summary_template = """
        Summarize the following educational content in a clear, concise manner.
        Highlight the key concepts and learning objectives.
        
        Content: {content}
        Target Audience Level: {difficulty_level}
        
        Summary:"""
        
        self.summary_prompt = PromptTemplate(
            input_variables=["content", "difficulty_level"],
            template=summary_template
        )
    
    async def get_tutor_response(
        self,
        message: str,
        student_id: int,
        session_id: Optional[int] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate an intelligent tutor response using LangChain.
        
        Args:
            message: Student's message
            student_id: Student ID for personalization
            session_id: Learning session ID
            context: Additional context for the conversation
            
        Returns:
            Dict containing the response and metadata
        """
        try:
            # Get student profile for personalization
            student_profile = await self._get_student_profile(student_id)
            
            # Prepare conversation context
            difficulty_level = student_profile.get("preferred_difficulty", 0.5)
            learning_style = student_profile.get("learning_style", "mixed")
            subject = context.get("subject", "General") if context else "General"
            
            # Get conversation history
            conversation_key = f"student_{student_id}"
            if conversation_key not in self.conversation_chains:
                self.conversation_chains[conversation_key] = []
            
            history = self._format_conversation_history(
                self.conversation_chains[conversation_key]
            )
            
            # Generate response using the configured AI provider
            response_text = await self._generate_ai_response(
                prompt=self.tutor_prompt.format(
                    difficulty_level=difficulty_level,
                    learning_style=learning_style,
                    subject=subject,
                    history=history,
                    input=message
                )
            )
            
            # Store conversation
            self.conversation_chains[conversation_key].append({
                "student": message,
                "tutor": response_text,
                "timestamp": datetime.utcnow()
            })
            
            # Keep only last 20 exchanges
            if len(self.conversation_chains[conversation_key]) > 20:
                self.conversation_chains[conversation_key] = self.conversation_chains[conversation_key][-20:]
            
            # Get recommendations
            recommendations = await self.recommendation_engine.get_content_recommendations(
                student_id, context={"message": message, "subject": subject}
            )
            
            return {
                "response": response_text,
                "confidence": 0.85,
                "recommendations": recommendations[:3],
                "follow_up_questions": await self._generate_follow_up_questions(message, subject),
                "difficulty_adjustment": await self._suggest_difficulty_adjustment(
                    message, difficulty_level
                ),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating tutor response: {e}")
            return {
                "response": "I apologize, but I'm having trouble processing your question right now. Could you please try again?",
                "confidence": 0.1,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def generate_quiz(
        self,
        topic: str,
        difficulty_level: float = 0.5,
        num_questions: int = 5,
        num_options: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Generate a quiz using AI.
        
        Args:
            topic: Quiz topic
            difficulty_level: Difficulty from 0.0 to 1.0
            num_questions: Number of questions to generate
            num_options: Number of multiple choice options
            
        Returns:
            List of quiz questions
        """
        try:
            quiz_questions = []
            
            for i in range(num_questions):
                # Generate question
                prompt = self.quiz_prompt.format(
                    topic=topic,
                    difficulty_level=difficulty_level,
                    num_options=num_options
                )
                
                response = await self._generate_ai_response(prompt)
                
                try:
                    # Try to parse JSON response
                    question_data = json.loads(response)
                    question_data["id"] = i + 1
                    question_data["topic"] = topic
                    question_data["difficulty"] = difficulty_level
                    quiz_questions.append(question_data)
                    
                except json.JSONDecodeError:
                    # Fallback for non-JSON responses
                    quiz_questions.append({
                        "id": i + 1,
                        "question": f"Question {i + 1}: {response[:100]}...",
                        "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
                        "correct_answer": "A",
                        "explanation": "AI-generated question",
                        "topic": topic,
                        "difficulty": difficulty_level
                    })
            
            return quiz_questions
            
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return []
    
    async def provide_feedback(
        self,
        student_answer: str,
        correct_answer: str,
        question: str,
        student_id: int
    ) -> Dict[str, Any]:
        """
        Provide intelligent feedback on student answers.
        
        Args:
            student_answer: The student's answer
            correct_answer: The correct answer
            question: The original question
            student_id: Student ID for personalization
            
        Returns:
            Detailed feedback dictionary
        """
        try:
            student_profile = await self._get_student_profile(student_id)
            
            feedback_prompt = f"""
            Provide constructive feedback for a student's answer.
            
            Question: {question}
            Correct Answer: {correct_answer}
            Student's Answer: {student_answer}
            Student Level: {student_profile.get('preferred_difficulty', 0.5)}
            
            Please provide:
            1. Whether the answer is correct or incorrect
            2. Detailed explanation
            3. Encouragement and guidance for improvement
            4. Related concepts to explore
            
            Feedback:"""
            
            feedback_text = await self._generate_ai_response(feedback_prompt)
            
            # Determine if answer is correct
            is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
            
            return {
                "is_correct": is_correct,
                "feedback": feedback_text,
                "confidence": 0.9 if is_correct else 0.7,
                "suggested_resources": await self.recommendation_engine.get_content_recommendations(
                    student_id, context={"question": question, "incorrect_answer": not is_correct}
                ),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error providing feedback: {e}")
            return {
                "is_correct": False,
                "feedback": "I'm having trouble analyzing your answer right now. Please try again.",
                "confidence": 0.1,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _generate_ai_response(self, prompt: str) -> str:
        """Generate AI response using the configured provider."""
        try:
            if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
                return await get_openai_response(prompt)
            elif settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
                return await get_gemini_response(prompt)
            elif settings.AI_PROVIDER == "huggingface":
                return await get_huggingface_response(prompt)
            else:
                return "AI service is not properly configured. Please check your settings."
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return "I'm experiencing technical difficulties. Please try again later."
    
    async def _get_student_profile(self, student_id: int) -> Dict[str, Any]:
        """Get student profile for personalization."""
        # This would typically query the database
        # For now, return default values
        return {
            "preferred_difficulty": 0.5,
            "learning_style": "visual",
            "tutor_personality": "encouraging"
        }
    
    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history for the prompt."""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for exchange in history[-5:]:  # Last 5 exchanges
            formatted.append(f"Student: {exchange['student']}")
            formatted.append(f"Tutor: {exchange['tutor']}")
        
        return "\n".join(formatted)
    
    async def _generate_follow_up_questions(self, message: str, subject: str) -> List[str]:
        """Generate follow-up questions to deepen learning."""
        try:
            prompt = f"""
            Based on this student message about {subject}: "{message}"
            
            Generate 2-3 follow-up questions that would help the student:
            1. Think deeper about the topic
            2. Connect concepts to real-world applications
            3. Test their understanding
            
            Format as a simple list:
            - Question 1
            - Question 2
            - Question 3
            """
            
            response = await self._generate_ai_response(prompt)
            # Parse the response and extract questions
            questions = [line.strip("- ").strip() for line in response.split("\n") if line.strip().startswith("-")]
            return questions[:3]
            
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {e}")
            return []
    
    async def _suggest_difficulty_adjustment(self, message: str, current_difficulty: float) -> Optional[Dict]:
        """Suggest difficulty level adjustments based on student interaction."""
        try:
            # Simple heuristic - can be made more sophisticated
            if "too easy" in message.lower() or "i know this" in message.lower():
                new_difficulty = min(1.0, current_difficulty + 0.1)
                return {
                    "suggested_difficulty": new_difficulty,
                    "reason": "Student indicates content is too easy"
                }
            elif "too hard" in message.lower() or "don't understand" in message.lower():
                new_difficulty = max(0.1, current_difficulty - 0.1)
                return {
                    "suggested_difficulty": new_difficulty,
                    "reason": "Student indicates content is too difficult"
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error suggesting difficulty adjustment: {e}")
            return None


# Global instance
advanced_tutor_service = AdvancedAITutorService()
