"""
Advanced AI-Powered Educational Content Generator

Generates high-quality lessons and quizzes using local AI models only.
Uses Ollama (Llama 3, Mistral, Qwen) for privacy-first AI generation.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from backend.services.ai_models import ai_model_manager

logger = logging.getLogger(__name__)

class AdvancedAIGenerator:
    """Advanced AI generator using local models via Ollama only"""
    
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

            # Generate with local AI model
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
- Educational assessment and learning
- Problem-solving in various industries

## Step-by-Step Learning Process
1. **Understand the Basics**: Start with fundamental concepts and definitions
2. **Explore Examples**: Look at real-world applications and case studies
3. **Practice Application**: Work through problems and exercises
4. **Analyze Results**: Review outcomes and identify patterns
5. **Build Connections**: Link {topic} to other concepts in {subject}

## Key Takeaways
- {topic} is essential for understanding {subject}
- It provides a systematic approach to problem-solving
- Real-world applications demonstrate its practical value
- Mastery requires both theoretical knowledge and practical experience
- Continuous learning and practice lead to deeper understanding

## Next Steps
To continue learning about {topic}:
- Explore related concepts in {subject}
- Practice with real-world examples
- Connect with other learners and experts
- Apply knowledge in practical projects
- Stay updated with latest developments in the field"""

            return {
                "content": content,
                "generated_by": "template",
                "timestamp": datetime.now().isoformat(),
                "topic": topic,
                "subject": subject
            }

    async def generate_quiz_content(
        self,
        topic: str,
        subject: str,
        difficulty_level: str = "intermediate",
        num_questions: int = 5,
        quiz_type: str = "multiple_choice"
    ) -> Dict[str, Any]:
        """Generate quiz content using local AI models"""
        try:
            prompt = f"""Create a {difficulty_level} level quiz on '{topic}' in {subject}.

Requirements:
- Generate exactly {num_questions} questions
- Question type: {quiz_type}
- Difficulty: {difficulty_level}
- Include clear, educational questions
- Provide 4 multiple choice options per question
- Include correct answers and explanations
- Focus on understanding, not memorization

Format the response as JSON with this structure:
{{
    "questions": [
        {{
            "question": "Question text here",
            "type": "multiple_choice",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Explanation of why this answer is correct"
        }}
    ]
}}

Topic: {topic}
Subject: {subject}"""

            # Generate with local AI model
            content = await self.model_manager.generate_content(
                prompt=prompt,
                content_type="quiz",
                max_length=1500,
                temperature=0.7
            )
            
            if content and len(content.strip()) > 50:
                # Try to parse JSON response
                try:
                    import json
                    quiz_data = json.loads(content)
                    if "questions" in quiz_data and len(quiz_data["questions"]) > 0:
                        return {
                            "quiz_id": f"quiz_{datetime.now().timestamp()}",
                            "user_id": 1,  # Will be set by the endpoint
                            "subject": subject,
                            "topic": topic,
                            "difficulty_level": difficulty_level,
                            "num_questions": num_questions,
                            "quiz_type": quiz_type,
                            "questions": quiz_data["questions"],
                            "generated_by": "ai_model",
                            "timestamp": datetime.now().isoformat(),
                            "generated_at": "now",
                            "time_limit_minutes": num_questions * 2
                        }
                except json.JSONDecodeError:
                    logger.warning("Failed to parse AI-generated quiz JSON")
            
            raise Exception("Generated quiz content invalid")
                
        except Exception as e:
            logger.warning(f"AI quiz generation failed, using template: {e}")
            # Fallback template quiz
            questions = []
            for i in range(min(num_questions, 3)):  # Max 3 template questions
                questions.append({
                    "question": f"What is a key aspect of {topic} in {subject}?",
                    "type": "multiple_choice",
                    "options": [
                        f"Understanding {topic} fundamentals",
                        f"Memorizing {topic} definitions",
                        f"Ignoring {topic} applications",
                        f"Avoiding {topic} practice"
                    ],
                    "correct_answer": 0,
                    "explanation": f"Understanding {topic} fundamentals is essential for mastering this concept in {subject}."
                })
            
            return {
                "quiz_id": f"quiz_{datetime.now().timestamp()}",
                "user_id": 1,
                "subject": subject,
                "topic": topic,
                "difficulty_level": difficulty_level,
                "num_questions": len(questions),
                "quiz_type": quiz_type,
                "questions": questions,
                "generated_by": "template",
                "timestamp": datetime.now().isoformat(),
                "generated_at": "now",
                "time_limit_minutes": len(questions) * 2
            }

    async def generate_chat_response(
        self,
        message: str,
        subject: str = "General",
        conversation_history: Optional[List[Dict]] = None,
        max_tokens: int = 500
    ) -> str:
        """Generate a conversational response for the AI tutor chat"""
        try:
            # Use local models for chat generation
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

            # Generate with local AI model
            response = await self.model_manager.generate_content(
                prompt=prompt,
                content_type="chat",
                max_length=max_tokens,
                temperature=0.7
            )
            
            if response and len(response.strip()) > 20:
                return response.strip()
            else:
                raise Exception("Generated response too short")
                
        except Exception as e:
            logger.warning(f"AI chat generation failed, using template: {e}")
            # Fallback template response
            return f"""I'd be happy to help you with your question about {subject}! 

Your question: "{message}"

This is an interesting topic in {subject}. To give you the best answer, I'd recommend:
- Breaking down the question into smaller parts
- Looking at examples and real-world applications
- Practicing with related exercises
- Exploring how this connects to other concepts

Would you like me to explain any specific aspect in more detail, or do you have follow-up questions about {subject}?"""

    async def generate_explanation(
        self,
        concept: str,
        subject: str = "General",
        level: str = "intermediate"
    ) -> str:
        """Generate an explanation of a concept"""
        try:
            prompt = f"""Explain the concept of '{concept}' in {subject} at a {level} level.

Requirements:
- Provide a clear, educational explanation
- Use examples and analogies when helpful
- Structure the explanation logically
- Make it appropriate for {level} level understanding
- Include practical applications if relevant

Concept: {concept}
Subject: {subject}
Level: {level}"""

            # Generate with local AI model
            response = await self.model_manager.generate_content(
                prompt=prompt,
                content_type="explanation",
                max_length=800,
                temperature=0.7
            )
            
            if response and len(response.strip()) > 50:
                return response.strip()
            else:
                raise Exception("Generated explanation too short")
                
        except Exception as e:
            logger.warning(f"AI explanation generation failed, using template: {e}")
            # Fallback template explanation
            return f"""## Understanding {concept} in {subject}

{concept} is a fundamental concept in {subject} that helps us understand how systems work and interact. At a {level} level, we can think of {concept} as:

**Key Points:**
- {concept} represents important principles in {subject}
- It helps us analyze and solve problems systematically
- Understanding {concept} builds a foundation for more advanced topics
- Real-world applications demonstrate its practical value

**Why It Matters:**
{concept} is essential because it provides a framework for thinking about {subject} problems. By understanding {concept}, you can:
- Approach problems more systematically
- Make better predictions and decisions
- Connect different ideas in {subject}
- Apply knowledge in practical situations

**Next Steps:**
To deepen your understanding of {concept}:
- Practice with examples and exercises
- Explore how it relates to other concepts
- Look for real-world applications
- Ask questions and seek clarification when needed"""

# Create global instance
advanced_ai_generator = AdvancedAIGenerator()