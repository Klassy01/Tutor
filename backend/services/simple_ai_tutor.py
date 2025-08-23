"""
Simple AI Tutor Service without heavy dependencies.

This module provides AI tutoring capabilities using direct API calls.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
import json

from backend.core.config import settings
from backend.services.ai_models import (
    get_gemini_response,
    get_openai_response,
    get_huggingface_response
)

logger = logging.getLogger(__name__)


class SimpleAITutorService:
    """Simple AI Tutor Service with direct API integration."""
    
    def __init__(self):
        self.conversation_history: Dict[int, List[Dict[str, str]]] = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the AI tutor service."""
        if self.initialized:
            return
            
        logger.info("Initializing Simple AI Tutor Service...")
        
        # Test AI providers
        try:
            if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
                test_response = await get_gemini_response("Test", "Hello")
                logger.info("✅ Gemini AI provider initialized")
            elif settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
                test_response = await get_openai_response("Test", "Hello")
                logger.info("✅ OpenAI provider initialized")
        except Exception as e:
            logger.warning(f"AI provider test failed: {e}")
            
        self.initialized = True
        logger.info("Simple AI Tutor Service initialized successfully")
    
    def _get_conversation_history(self, student_id: int) -> List[Dict[str, str]]:
        """Get conversation history for a student."""
        if student_id not in self.conversation_history:
            self.conversation_history[student_id] = []
        return self.conversation_history[student_id]
    
    def _add_to_history(self, student_id: int, role: str, message: str):
        """Add message to conversation history."""
        history = self._get_conversation_history(student_id)
        history.append({
            "role": role,
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        # Keep only last 20 messages
        if len(history) > 20:
            history[:] = history[-20:]
    
    async def get_tutoring_response(
        self,
        student_id: int,
        message: str,
        subject: Optional[str] = None,
        difficulty_level: Optional[float] = None,
        learning_style: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get AI tutoring response for a student message."""
        try:
            if not self.initialized:
                await self.initialize()
            
            # Build context from conversation history
            history = self._get_conversation_history(student_id)
            context_messages = []
            
            # Add recent conversation history
            for msg in history[-5:]:  # Last 5 messages
                context_messages.append(f"{msg['role']}: {msg['content']}")
            
            # Build the prompt
            system_prompt = self._build_system_prompt(subject, difficulty_level, learning_style)
            
            # Create the full prompt
            context = "\n".join(context_messages) if context_messages else "No previous conversation."
            full_prompt = f"""
{system_prompt}

Previous conversation:
{context}

Student: {message}

AI Tutor:"""

            # Get response from AI provider
            ai_response = await self._get_ai_response(full_prompt)
            
            # Add to conversation history
            self._add_to_history(student_id, "student", message)
            self._add_to_history(student_id, "tutor", ai_response)
            
            return {
                "response": ai_response,
                "timestamp": datetime.utcnow().isoformat(),
                "student_id": student_id,
                "subject": subject,
                "difficulty_level": difficulty_level
            }
            
        except Exception as e:
            logger.error(f"Error getting tutoring response: {e}")
            return {
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _build_system_prompt(
        self,
        subject: Optional[str] = None,
        difficulty_level: Optional[float] = None,
        learning_style: Optional[str] = None
    ) -> str:
        """Build system prompt based on student preferences."""
        base_prompt = """You are an AI tutor that provides personalized, engaging, and educational responses. 
You should:
- Be encouraging and supportive
- Explain concepts clearly with examples
- Ask follow-up questions to check understanding
- Adapt your teaching style to the student's needs
- Provide step-by-step explanations for complex topics"""
        
        if subject:
            base_prompt += f"\n- Focus on {subject} topics and concepts"
            
        if difficulty_level is not None:
            level_desc = "beginner" if difficulty_level < 0.3 else "intermediate" if difficulty_level < 0.7 else "advanced"
            base_prompt += f"\n- Adjust explanations for {level_desc} level (difficulty: {difficulty_level})"
            
        if learning_style:
            base_prompt += f"\n- Adapt to {learning_style} learning style"
            
        return base_prompt
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from the configured AI provider."""
        try:
            if settings.AI_PROVIDER == "gemini":
                return await get_gemini_response("AI Tutor", prompt)
            elif settings.AI_PROVIDER == "openai":
                return await get_openai_response("AI Tutor", prompt)
            elif settings.AI_PROVIDER == "huggingface":
                return await get_huggingface_response(prompt)
            else:
                return "I'm sorry, no AI provider is configured."
        except Exception as e:
            logger.error(f"AI provider error: {e}")
            return "I'm having trouble connecting to my AI systems. Please try again in a moment."
    
    async def generate_quiz(
        self,
        subject: str,
        topic: str,
        difficulty_level: float = 0.5,
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """Generate a quiz for the given subject and topic."""
        try:
            if not self.initialized:
                await self.initialize()
            
            difficulty_desc = "beginner" if difficulty_level < 0.3 else "intermediate" if difficulty_level < 0.7 else "advanced"
            
            prompt = f"""Generate a {difficulty_desc} level quiz about {topic} in {subject} with {num_questions} multiple choice questions.

For each question, provide:
1. The question text
2. Four answer options (A, B, C, D)
3. The correct answer
4. A brief explanation

Format as JSON:
{{
    "quiz": [
        {{
            "question": "Question text?",
            "options": {{
                "A": "Option A",
                "B": "Option B", 
                "C": "Option C",
                "D": "Option D"
            }},
            "correct_answer": "A",
            "explanation": "Brief explanation"
        }}
    ]
}}"""

            response = await self._get_ai_response(prompt)
            
            # Try to parse JSON response
            try:
                quiz_data = json.loads(response)
                return quiz_data
            except json.JSONDecodeError:
                # Fallback: create a simple quiz
                return {
                    "quiz": [
                        {
                            "question": f"What is a key concept in {topic}?",
                            "options": {
                                "A": "Option A",
                                "B": "Option B",
                                "C": "Option C", 
                                "D": "Option D"
                            },
                            "correct_answer": "A",
                            "explanation": f"This is related to {topic} in {subject}."
                        }
                    ]
                }
                
        except Exception as e:
            logger.error(f"Error generating quiz: {e}")
            return {
                "error": "Failed to generate quiz",
                "quiz": []
            }
    
    async def get_learning_recommendations(
        self,
        student_id: int,
        current_subject: str,
        performance_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get personalized learning recommendations."""
        try:
            if not self.initialized:
                await self.initialize()
            
            prompt = f"""Based on a student's performance in {current_subject}, provide 3-5 personalized learning recommendations.

Student Performance Data:
{json.dumps(performance_data, indent=2)}

Provide recommendations as JSON:
{{
    "recommendations": [
        {{
            "title": "Recommendation title",
            "description": "Detailed description",
            "type": "practice|review|advance|concept",
            "priority": "high|medium|low",
            "estimated_time": "time in minutes"
        }}
    ]
}}"""

            response = await self._get_ai_response(prompt)
            
            try:
                recs = json.loads(response)
                return recs.get("recommendations", [])
            except json.JSONDecodeError:
                return [
                    {
                        "title": "Continue Practice",
                        "description": f"Keep practicing {current_subject} concepts",
                        "type": "practice",
                        "priority": "medium",
                        "estimated_time": "15-20 minutes"
                    }
                ]
                
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []


# Global instance
simple_tutor_service = SimpleAITutorService()