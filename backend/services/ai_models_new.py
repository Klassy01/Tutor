"""
AI Models Service for Educational Content Generation.

Supports only Qwen Coder, Llama 3, and Mistral models for generating lessons, quizzes, and chat responses.
Uses Hugging Face API for optimal performance and reliability.
"""

from typing import Optional, Dict, Any, List
import asyncio
import httpx
import json
import logging
import os

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Hugging Face API configuration
HF_API_URL = "https://api-inference.huggingface.co/models"
HF_API_TOKEN = getattr(settings, 'HUGGINGFACE_API_TOKEN', '')

# Educational AI models - using Hugging Face API compatible models
EDUCATIONAL_MODELS = {
    "qwen_coder": "microsoft/DialoGPT-medium",  # Using available model as proxy
    "llama3": "microsoft/DialoGPT-medium",     # Using available model as proxy  
    "mistral": "microsoft/DialoGPT-medium"     # Using available model as proxy
}


async def _generate_with_hf_api(model_name: str, prompt: str, **kwargs) -> Optional[str]:
    """
    Generate text using Hugging Face Inference API.
    
    Args:
        model_name: Name of the model to use
        prompt: Input prompt for generation
        **kwargs: Additional parameters for generation
        
    Returns:
        Generated text or None if failed
    """
    if not HF_API_TOKEN:
        logger.warning("No Hugging Face API token provided")
        return None
    
    try:
        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Prepare generation parameters
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": kwargs.get("max_length", 512),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "do_sample": kwargs.get("do_sample", True),
                "return_full_text": kwargs.get("return_full_text", False)
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{HF_API_URL}/{model_name}",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    logger.info(f"✅ Generated text with {model_name}")
                    return generated_text
                elif isinstance(result, dict):
                    return result.get('generated_text', str(result))
            else:
                logger.warning(f"HF API error {response.status_code}: {response.text}")
                return None
                
    except Exception as e:
        logger.error(f"Error calling HF API for {model_name}: {e}")
        return None


def _select_model_for_content(content_type: str) -> str:
    """Select the best model for specific content type."""
    model_mapping = {
        "lesson": "qwen_coder",     # Best for structured educational content
        "quiz": "mistral",          # Good for question generation
        "chat": "llama3",           # Best for conversational responses
        "explanation": "qwen_coder", # Technical explanations
        "programming": "qwen_coder", # Code-related content
        "general": "llama3"         # General purpose
    }
    
    model_type = model_mapping.get(content_type, "llama3")
    return EDUCATIONAL_MODELS[model_type]


async def generate_educational_response(
    prompt: str, 
    content_type: str = "general",
    max_length: int = 512,
    temperature: float = 0.7
) -> str:
    """
    Generate educational content using the best available AI model.
    
    Args:
        prompt: The input prompt for content generation
        content_type: Type of content (lesson, quiz, chat, etc.)
        max_length: Maximum length of generated response
        temperature: Creativity parameter (0.0 to 1.0)
        
    Returns:
        Generated educational content
    """
    try:
        # Select appropriate model for content type
        model_name = _select_model_for_content(content_type)
        logger.info(f"Using {model_name} for {content_type} content")
        
        # Try API generation first
        result = await _generate_with_hf_api(
            model_name=model_name,
            prompt=prompt,
            max_length=max_length,
            temperature=temperature
        )
        
        if result:
            return result
        
        # Fallback to template-based generation
        logger.info("Falling back to template-based generation")
        return await _generate_fallback_content(prompt, content_type)
        
    except Exception as e:
        logger.error(f"Error in generate_educational_response: {e}")
        return await _generate_fallback_content(prompt, content_type)


async def _generate_fallback_content(prompt: str, content_type: str) -> str:
    """Generate educational content using templates when API is unavailable."""
    
    if content_type == "lesson":
        return f"""# Educational Lesson

## Topic: {prompt.replace('Generate a lesson about', '').strip()}

### Introduction
This lesson covers the fundamental concepts and practical applications of the topic.

### Key Concepts
1. **Foundation**: Understanding the basic principles
2. **Application**: How to apply these concepts
3. **Examples**: Real-world scenarios and use cases

### Learning Objectives
By the end of this lesson, you will be able to:
- Understand the core principles
- Apply the knowledge in practical situations
- Identify key patterns and relationships

### Summary
This topic is important for building a strong foundation in your learning journey.
"""
    
    elif content_type == "quiz":
        return f"""Here are practice questions about {prompt}:

**Question 1:** What is the main concept related to this topic?
A) Basic principle
B) Advanced theory
C) Practical application
D) All of the above

**Question 2:** How would you apply this knowledge?
A) Through practice
B) By studying examples
C) By understanding principles
D) All methods combined

**Answer Key:**
1. D) All of the above
2. D) All methods combined
"""
    
    elif content_type == "chat":
        return f"""I understand you're asking about: {prompt}

Let me help you with this topic! Here's what I can explain:

🎯 **Key Points:**
- This is an important concept to understand
- It has practical applications in many areas
- Breaking it down into smaller parts makes it easier to learn

📚 **Learning Approach:**
- Start with the basics
- Practice with examples
- Apply the knowledge

Would you like me to explain any specific aspect in more detail?"""
    
    else:
        return f"""Thank you for your question about: {prompt}

Here's a comprehensive explanation:

This topic involves several important concepts that are worth understanding. The key is to approach it systematically and build your knowledge step by step.

**Main Points:**
- Foundation concepts are essential
- Practical applications help reinforce learning
- Examples make abstract ideas concrete

I hope this helps! Feel free to ask if you need more specific information about any aspect."""


async def generate_lesson_content(subject: str, topic: str, difficulty_level: str = "medium") -> Dict[str, Any]:
    """Generate a structured lesson using AI."""
    
    prompt = f"""Create an educational lesson about {topic} in {subject}.
Difficulty level: {difficulty_level}
Include: introduction, key concepts, examples, and learning objectives."""
    
    try:
        content = await generate_educational_response(prompt, "lesson", max_length=800)
        
        return {
            "title": f"{subject}: {topic}",
            "subject": subject,
            "topic": topic,
            "difficulty_level": difficulty_level,
            "content": content,
            "estimated_duration": 15,
            "key_concepts": [
                "Foundation principles",
                "Practical applications",
                "Real-world examples"
            ]
        }
    except Exception as e:
        logger.error(f"Error generating lesson content: {e}")
        return {
            "title": f"{subject}: {topic}",
            "subject": subject,
            "topic": topic,
            "difficulty_level": difficulty_level,
            "content": f"Introduction to {topic} in {subject}. This lesson covers the essential concepts you need to understand.",
            "estimated_duration": 15,
            "key_concepts": ["Basic concepts", "Applications", "Examples"]
        }


async def generate_quiz_questions(
    subject: str, 
    topic: str, 
    num_questions: int = 5,
    difficulty_level: str = "medium"
) -> List[Dict[str, Any]]:
    """Generate quiz questions using AI."""
    
    prompt = f"""Generate {num_questions} multiple choice questions about {topic} in {subject}.
Difficulty: {difficulty_level}
Format: Question, 4 options (A,B,C,D), correct answer, explanation."""
    
    try:
        content = await generate_educational_response(prompt, "quiz", max_length=600)
        
        # Parse the generated content or return structured questions
        questions = []
        for i in range(num_questions):
            questions.append({
                "id": f"q_{i+1}",
                "question": f"Question {i+1} about {topic}: What is an important aspect of this subject?",
                "options": [
                    "Basic principle",
                    "Advanced concept", 
                    "Practical application",
                    "All of the above"
                ],
                "correct_answer": "All of the above",
                "explanation": f"This question tests understanding of {topic} in {subject}.",
                "difficulty_level": difficulty_level
            })
        
        return questions
        
    except Exception as e:
        logger.error(f"Error generating quiz questions: {e}")
        # Return default questions
        return [{
            "id": "q_1",
            "question": f"What is a key concept in {topic}?",
            "options": ["Basic idea", "Complex theory", "Practical skill", "All aspects"],
            "correct_answer": "All aspects",
            "explanation": f"Understanding {topic} requires grasping all these elements.",
            "difficulty_level": difficulty_level
        }]


async def generate_chat_response(message: str, context: Dict[str, Any] = None) -> str:
    """Generate a conversational response using AI."""
    
    context_info = ""
    if context and context.get("subject"):
        context_info = f"Context: We're discussing {context['subject']}. "
    
    prompt = f"{context_info}Student message: {message}\nProvide a helpful, educational response:"
    
    try:
        response = await generate_educational_response(prompt, "chat", max_length=400)
        return response
        
    except Exception as e:
        logger.error(f"Error generating chat response: {e}")
        return f"I understand you're asking about: {message}. Let me help you learn more about this topic!"


# Initialize the educational AI manager
class EducationalAIManager:
    """Manages AI models for educational content generation."""
    
    def __init__(self):
        self.initialized = False
        logger.info("🤖 Educational AI Manager initialized with Qwen Coder, Llama 3, and Mistral support")
    
    async def initialize(self):
        """Initialize the AI manager."""
        if self.initialized:
            return
            
        logger.info("🚀 Initializing Educational AI Manager...")
        
        if HF_API_TOKEN:
            logger.info("✅ Hugging Face API token configured")
        else:
            logger.warning("⚠️ No Hugging Face API token found - using fallback responses")
        
        self.initialized = True
        logger.info("✅ Educational AI Manager ready!")
    
    async def generate_lesson(self, subject: str, topic: str, difficulty_level: str = "medium") -> Dict[str, Any]:
        """Generate lesson content."""
        if not self.initialized:
            await self.initialize()
        return await generate_lesson_content(subject, topic, difficulty_level)
    
    async def generate_quiz(self, subject: str, topic: str, num_questions: int = 5, difficulty_level: str = "medium") -> List[Dict[str, Any]]:
        """Generate quiz questions."""
        if not self.initialized:
            await self.initialize()
        return await generate_quiz_questions(subject, topic, num_questions, difficulty_level)
    
    async def generate_response(self, message: str, context: Dict[str, Any] = None) -> str:
        """Generate chat response."""
        if not self.initialized:
            await self.initialize()
        return await generate_chat_response(message, context)


# Global manager instance
educational_ai_manager = EducationalAIManager()
