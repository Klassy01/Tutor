"""
OpenAI API Service for Educational Content Generation.

Provides OpenAI GPT integration for high-quality educational content.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
import openai
from openai import AsyncOpenAI

from backend.core.config import settings

logger = logging.getLogger(__name__)


class OpenAIService:
    """OpenAI API service for educational content generation."""
    
    def __init__(self):
        self.client = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize OpenAI client."""
        if self.initialized:
            return
            
        try:
            # Get API key from environment or settings
            api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
            
            if not api_key or api_key == "your-openai-api-key-here":
                logger.warning("⚠️ OpenAI API key not configured. Using fallback templates.")
                return
                
            self.client = AsyncOpenAI(api_key=api_key)
            
            # Test the connection
            try:
                await self.client.models.list()
                logger.info("✅ OpenAI API connection successful")
                self.initialized = True
            except Exception as e:
                logger.error(f"❌ OpenAI API connection failed: {e}")
                self.client = None
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenAI service: {e}")
            self.client = None
    
    async def generate_content(
        self,
        prompt: str,
        content_type: str = "general",
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate content using OpenAI API."""
        
        if not self.initialized or not self.client:
            return await self._get_fallback_content(prompt, content_type)
        
        try:
            # Create educational prompt
            educational_prompt = self._create_educational_prompt(prompt, content_type)
            
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert AI tutor specializing in educational content. Provide clear, engaging, and helpful responses that promote learning."
                    },
                    {
                        "role": "user",
                        "content": educational_prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            content = response.choices[0].message.content
            logger.info(f"✅ Generated {content_type} content using OpenAI")
            return content.strip()
            
        except Exception as e:
            logger.error(f"❌ OpenAI generation failed: {e}")
            return await self._get_fallback_content(prompt, content_type)
    
    def _create_educational_prompt(self, prompt: str, content_type: str) -> str:
        """Create an educational-focused prompt."""
        
        if content_type == "chat":
            return f"""As an AI tutor, respond to this student's question in a helpful, educational manner:

{prompt}

Requirements:
- Be friendly and encouraging
- Provide clear explanations
- Use examples when helpful
- Keep the response focused and educational
- Encourage further learning"""
        
        elif content_type == "lesson":
            return f"""Create a comprehensive educational lesson based on this topic:

{prompt}

Include:
- Clear introduction and objectives
- Key concepts and definitions
- Step-by-step explanations
- Practical examples
- Real-world applications
- Summary and key takeaways"""
        
        elif content_type == "quiz":
            return f"""Generate educational quiz questions about this topic:

{prompt}

Create 3-5 questions with:
- Clear, specific questions
- Multiple choice options
- Correct answers
- Explanations for each answer
- Appropriate difficulty level"""
        
        else:
            return f"""Provide educational content about:

{prompt}

Make it informative, engaging, and suitable for learning."""
    
    async def _get_fallback_content(self, prompt: str, content_type: str) -> str:
        """Get fallback content when OpenAI is not available."""
        
        # Extract topic from prompt
        topic = prompt.lower()
        if "generate" in topic:
            topic = topic.split("generate")[-1].strip()
        if "about" in topic:
            topic = topic.split("about")[-1].strip()
        if "lesson" in topic:
            topic = topic.replace("lesson", "").strip()
        if "quiz" in topic:
            topic = topic.replace("quiz", "").strip()
        topic = topic.strip('"').strip("'").strip()
        
        if content_type == "chat":
            return f"""I understand you're asking about **{topic}**! 🎓

This is a fascinating and important topic that has many practical applications. Let me help you explore this concept:

## 🔍 **What You Should Know:**
- **{topic.title()}** involves key principles that are fundamental to understanding this field
- It has practical applications in many real-world scenarios
- Mastering this concept requires both theoretical knowledge and hands-on practice

## 📚 **Learning Approach:**
1. **Start with the basics** - Build a solid foundation with core concepts
2. **Practice regularly** - Apply what you learn through exercises and examples  
3. **Connect ideas** - Link new knowledge to what you already know
4. **Ask questions** - Curiosity drives deeper understanding

## 💡 **Why This Matters:**
Understanding {topic} will help you:
- Solve complex problems more effectively
- Think critically and analytically
- Apply knowledge in practical situations
- Build confidence in this subject area

## 🎯 **Next Steps:**
Would you like me to explain any specific aspect of {topic} in more detail? I can help you with:
- Core concepts and definitions
- Step-by-step problem-solving approaches
- Real-world examples and applications
- Practice exercises and challenges

What specific part of {topic} would you like to explore further? I'm here to help make this topic clear and engaging for you! 🚀"""
        
        else:
            return f"""## Understanding {topic.title()} 📖

Thank you for your interest in learning about **{topic}**. This is an important concept that deserves careful attention and study.

### 🔍 **Overview**
{topic.title()} encompasses several key ideas and principles that are essential for building a comprehensive understanding of this subject area. The concepts involved are both theoretically significant and practically applicable.

### 📋 **Key Areas to Explore:**
- **Fundamental principles** that form the foundation
- **Practical applications** in real-world contexts  
- **Problem-solving approaches** using these concepts
- **Connections** to related topics and fields

### 🎯 **Learning Strategy:**
1. **Build understanding gradually** - Start with basics and progress to advanced topics
2. **Practice actively** - Engage with examples and exercises
3. **Make connections** - Link new concepts to existing knowledge
4. **Apply knowledge** - Use what you learn in practical situations

### 💡 **Why This Matters:**
Developing expertise in {topic} will enhance your analytical thinking, problem-solving abilities, and practical skills in this field.

I hope this introduction helps! Please feel free to ask specific questions about any aspect of {topic} that interests you. I'm here to support your learning journey! 🚀"""


# Global OpenAI service instance
openai_service = OpenAIService()
