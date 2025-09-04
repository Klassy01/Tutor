"""
Advanced AI-Powered Educational Content Generator

Generates high-quality lessons and quizzes using local AI models.
Uses Ollama (Llama 3, Mistral, Qwen) for privacy-first AI generation.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from backend.services.ai_models import ai_model_manager
from backend.services.openai_service import openai_service

logger = logging.getLogger(__name__)

class AdvancedAIGenerator:
    """Advanced AI generator using local models via Ollama"""
    
    def __init__(self):
        self.model_manager = ai_model_manager
        
    async def generate_lesson_content(
        self, 
        topic: str, 
        subject: str,
        difficulty_level: str = "intermediate",
        learning_style: str = "visual",
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """Generate comprehensive lesson content using local AI models"""
        try:
            # Create detailed prompt for lesson generation
            prompt = f"""Create a comprehensive lesson on '{topic}' in {subject}.

Requirements:
- Target difficulty: {difficulty_level}
- Learning style: {learning_style}  
- Duration: {duration_minutes} minutes
- Include clear explanations with examples
- Add practical applications and real-world context
- Structure with headings and bullet points
- Focus on understanding, not memorization

Generate a well-structured lesson covering:
1. Introduction and importance
2. Key concepts and definitions
3. Step-by-step explanations
4. Practical examples
5. Real-world applications
6. Summary and key takeaways

Topic: {topic}
Subject: {subject}"""

            # Try to generate with AI model
            content = await self.model_manager.generate_content(
                prompt=prompt,
                content_type="lesson",
                max_length=2000,
                temperature=0.7
            )
            
            if content and len(content.strip()) > 100:
                return {
                    "content": content.strip(),
                    "generated_by": "ai_model",
                    "timestamp": datetime.now().isoformat(),
                    "topic": topic,
                    "subject": subject
                }
            else:
                raise Exception("Generated content too short")
                
        except Exception as e:
            logger.warning(f"AI generation failed, using enhanced template: {e}")
            # Enhanced fallback template
            content = f"""## What is {topic}?
{topic} is a fundamental concept in {subject} that plays a crucial role in understanding how systems work and interact. It represents key principles that help us analyze, predict, and solve problems in this field.

## Why is {topic} Important?
In {subject}, {topic} serves as a foundation for:
- Analyzing data and identifying patterns
- Making informed predictions and decisions  
- Understanding cause-and-effect relationships
- Solving complex problems systematically
- Building more advanced knowledge

## Key Concepts
- **Definition**: Clear understanding of what {topic} means and includes
- **Core Principles**: Fundamental rules and properties of {topic}
- **Applications**: How {topic} is used in real scenarios and problem-solving
- **Methods**: Different approaches and techniques for working with {topic}
- **Analysis**: Ways to interpret, evaluate, and apply {topic} knowledge

## Real-World Applications
{topic} appears in many practical areas including:
- Business analytics and decision-making
- Scientific research and discovery
- Technology development and innovation
- Problem-solving in professional settings
- Daily life situations and personal decisions

## Learning Activities
To master {topic}, consider these approaches:
1. **Study the fundamentals** - Start with basic definitions and principles
2. **Practice with examples** - Work through real-world scenarios
3. **Apply knowledge** - Use {topic} concepts in practical projects
4. **Connect concepts** - Link {topic} to other areas in {subject}
5. **Test understanding** - Complete exercises and assessments

## Summary
{topic} is essential for success in {subject}. By understanding its core principles, applications, and methods, you can develop strong analytical skills and solve complex problems effectively. Remember to practice regularly and connect concepts to real-world situations for deeper learning."""

            return {
                "content": content.strip(),
                "generated_by": "template",
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "subject": subject
            }

    async def generate_quiz(
        self, 
        topic: str, 
        subject: str,
        num_questions: int = 5,
        difficulty_level: str = "intermediate",
        question_types: List[str] = None
    ) -> Dict[str, Any]:
        """Generate quiz questions using local AI models"""
        
        if question_types is None:
            question_types = ["multiple_choice", "true_false"]
            
        try:
            # Create detailed prompt for quiz generation
            prompt = f"""Generate {num_questions} quiz questions about '{topic}' in {subject}.

Requirements:
- Difficulty: {difficulty_level}
- Question types: {', '.join(question_types)}
- Focus on understanding and application
- Include clear explanations for answers
- Make questions practical and relevant

For each question, provide:
1. Clear, specific question text
2. Answer options (for multiple choice)
3. Correct answer
4. Detailed explanation

IMPORTANT: Respond ONLY with valid JSON. No explanations, no markdown, no extra text.

Required JSON format:
{{
  "questions": [
    {{
      "question": "Question text here",
      "type": "multiple_choice",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": 0,
      "explanation": "Explanation of why this is correct"
    }}
  ]
}}

Topic: {topic}
Subject: {subject}

Respond with ONLY the JSON object:"""

            # Try to generate with AI model
            response = await self.model_manager.generate_content(
                prompt=prompt,
                content_type="quiz",
                max_length=1500,
                temperature=0.6
            )
            
            if response and len(response.strip()) > 50:
                # Try to parse JSON response with improved error handling
                import json
                import re
                try:
                    # Clean the response - remove any markdown formatting
                    cleaned_response = response.strip()
                    if cleaned_response.startswith('```json'):
                        cleaned_response = cleaned_response[7:]
                    if cleaned_response.endswith('```'):
                        cleaned_response = cleaned_response[:-3]
                    cleaned_response = cleaned_response.strip()
                    
                    # Try to extract JSON from the response if it's embedded in text
                    json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if json_match:
                        cleaned_response = json_match.group(0)
                    
                    quiz_data = json.loads(cleaned_response)
                    if "questions" in quiz_data and len(quiz_data["questions"]) > 0:
                        logger.info("✅ Successfully parsed AI-generated quiz JSON")
                        return {
                            "questions": quiz_data["questions"],
                            "generated_by": "ai_model",
                            "timestamp": datetime.now().isoformat(),
                            "topic": topic,
                            "subject": subject
                        }
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse AI-generated quiz JSON: {e}")
                    logger.debug(f"Raw response: {response[:200]}...")
                except Exception as e:
                    logger.warning(f"Error processing AI response: {e}")
                    
            raise Exception("AI quiz generation failed or invalid format")
            
        except Exception as e:
            logger.warning(f"AI quiz generation failed, using template: {e}")
            
            # Fallback quiz template
            fallback_quiz = [
                {
                    "question": f"What is the primary focus of {topic}?",
                    "type": "multiple_choice",
                    "options": [
                        "Understanding basic concepts and applications",
                        "Memorizing complex formulas only", 
                        "Learning unrelated facts",
                        "Avoiding practical examples"
                    ],
                    "correct_answer": 0,
                    "explanation": f"{topic} focuses on building understanding through concepts and real-world applications."
                },
                {
                    "question": f"Which approach best describes effective learning of {topic}?",
                    "type": "multiple_choice", 
                    "options": [
                        "Rote memorization without context",
                        "Connecting concepts to practical applications",
                        "Ignoring foundational principles",
                        "Learning in isolation from other topics"
                    ],
                    "correct_answer": 1,
                    "explanation": f"Effective learning of {topic} involves connecting concepts to practical applications."
                },
                {
                    "question": f"True or False: {topic} has real-world applications beyond academic study.",
                    "type": "true_false",
                    "correct_answer": True,
                    "explanation": f"{topic} has numerous practical applications in professional and daily life contexts."
                }
            ]
            
            # Limit to requested number of questions
            questions = fallback_quiz[:num_questions]
            
            return {
                "questions": questions,
                "generated_by": "template",
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "subject": subject
            }

    async def generate_adaptive_content(
        self,
        topic: str,
        subject: str,
        student_performance: Dict[str, Any],
        learning_objectives: List[str] = None
    ) -> Dict[str, Any]:
        """Generate adaptive content based on student performance"""
        
        # Determine content difficulty based on performance
        avg_score = student_performance.get("average_score", 0.5)
        
        if avg_score >= 0.8:
            difficulty = "advanced"
        elif avg_score >= 0.6:
            difficulty = "intermediate"  
        else:
            difficulty = "beginner"
            
        # Generate lesson content
        lesson_content = await self.generate_lesson_content(
            topic=topic,
            subject=subject,
            difficulty_level=difficulty
        )
        
        # Generate appropriate quiz
        quiz_content = await self.generate_quiz(
            topic=topic,
            subject=subject,
            difficulty_level=difficulty,
            num_questions=5
        )
        
        return {
            "lesson": lesson_content,
            "quiz": quiz_content,
            "difficulty_level": difficulty,
            "adapted_for": student_performance,
            "timestamp": datetime.now().isoformat()
        }

    async def generate_explanation(
        self,
        question: str,
        context: str,
        detail_level: str = "medium"
    ) -> str:
        """Generate detailed explanations for questions or concepts"""
        try:
            prompt = f"""Provide a clear, {detail_level}-detail explanation for this question:

Question: {question}
Context: {context}

Requirements:
- Clear and understandable language
- Step-by-step reasoning if applicable
- Examples when helpful
- Connections to broader concepts
- Practical relevance

Explanation:"""

            explanation = await self.model_manager.generate_content(
                prompt=prompt,
                content_type="explanation",
                max_length=800,
                temperature=0.5
            )
            
            if explanation and len(explanation.strip()) > 20:
                return explanation.strip()
            else:
                raise Exception("Generated explanation too short")
                
        except Exception as e:
            logger.warning(f"AI explanation generation failed: {e}")
            return f"""This question relates to {context} and requires understanding of key concepts and their applications.

To approach this effectively:
1. Identify the main concept being asked about
2. Consider how it connects to the broader topic
3. Think about practical applications and examples
4. Apply logical reasoning to reach the answer

For more detailed explanations, consider reviewing the lesson material and practicing with similar examples."""

    async def generate_chat_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        subject: str = "General",
        max_tokens: int = 500
    ) -> str:
        """Generate a conversational response for the AI tutor chat"""
        try:
            # Try OpenAI first if available
            await openai_service.initialize()
            if openai_service.initialized:
                # Build context from conversation history
                context = ""
                if conversation_history:
                    context = "Previous conversation:\n"
                    for msg in conversation_history[-3:]:  # Last 3 messages for context
                        role = "Student" if msg["role"] == "user" else "Tutor"
                        context += f"{role}: {msg['content']}\n"
                
                prompt = f"""You are an AI tutor specializing in {subject}. Please respond to this student's question in a helpful, educational manner:

Student Question: {message}
{context}

Requirements:
- Be friendly and encouraging
- Provide clear, educational explanations
- Use examples when helpful
- Keep the response focused and concise
- Encourage further learning
- Stay focused on {subject} topics

Response:"""

                response = await openai_service.generate_content(
                    prompt=prompt,
                    content_type="chat",
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                
                if response and len(response.strip()) > 10:
                    logger.info("✅ Generated response using OpenAI")
                    return response.strip()
            
            # Fallback to local AI models
            # Build context from conversation history
            context = ""
            if conversation_history:
                context = "Previous conversation:\n"
                for msg in conversation_history[-3:]:  # Last 3 messages for context
                    role = "Student" if msg["role"] == "user" else "Tutor"
                    context += f"{role}: {msg['content']}\n"
            
            prompt = f"""You are an AI tutor specializing in {subject}. Please respond to this student's question in a helpful, educational manner:

Student Question: {message}
{context}

Requirements:
- Be friendly and encouraging
- Provide clear, educational explanations
- Use examples when helpful
- Keep the response focused and concise
- Encourage further learning
- Stay focused on {subject} topics

Response:"""

            response = await self.model_manager.generate_content(
                prompt=prompt,
                content_type="chat",
                max_length=max_tokens,
                temperature=0.7
            )
            
            if response and len(response.strip()) > 10:
                logger.info("✅ Generated response using local AI models")
                return response.strip()
            else:
                raise Exception("Generated response too short")
                
        except Exception as e:
            logger.warning(f"AI chat response generation failed: {e}")
            return f"""Thank you for your question about {subject}! I understand you're asking: "{message}"

While I work on generating a detailed response, here are some key points to consider:

1. **Break down the topic**: Think about the main concepts involved in {subject}
2. **Look for connections**: How does this relate to what you've already learned?  
3. **Practice examples**: Try working through similar problems or scenarios
4. **Ask follow-up questions**: What specific aspects of {subject} would you like to explore further?

I'm here to help guide your learning journey in {subject}. Feel free to ask more specific questions or request examples!"""

# Create global instance
advanced_ai_generator = AdvancedAIGenerator()
