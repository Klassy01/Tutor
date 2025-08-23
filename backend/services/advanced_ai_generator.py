"""
Educational AI Content Generator using Qwen Coder, Llama 3, and Mistral models.
"""

import json
import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from backend.services.ai_models import ai_model_manager

logger = logging.getLogger(__name__)

class AdvancedAIGenerator:
    """Educational AI content generator using specialized models."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize the AI models."""
        if self.initialized:
            return
            
        try:
            await ai_model_manager.warmup_models()
            self.initialized = True
            logger.info("✅ Educational AI generator initialized successfully")
        except Exception as e:
            logger.warning(f"AI generator initialization had issues: {e}")
            self.initialized = True  # Continue with fallback
    
    async def generate_lesson_content(
        self, 
        subject: str, 
        topic: str, 
        difficulty: str = "intermediate"
    ) -> Dict[str, Any]:
        """Generate comprehensive lesson content using educational AI."""
        await self.initialize()
        
        # Create educational prompt for lesson generation
        prompt = f"""Create a comprehensive educational lesson about "{topic}" in {subject} for {difficulty} level students.

Structure the lesson with these sections:
1. **Introduction**: What students will learn and why it's important
2. **Key Concepts**: Break down the main ideas clearly
3. **Examples**: Real-world applications and concrete examples
4. **Practice**: Questions or exercises to check understanding
5. **Summary**: Recap the main points

Topic: {topic}
Subject: {subject}
Level: {difficulty}

Please create an engaging, well-structured lesson:"""

        try:
            # Generate content using educational AI
            content = await ai_model_manager.generate_content(
                prompt, 
                content_type="lesson"
            )
            
            # Structure the lesson data
            lesson = {
                "id": f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "subject": subject,
                "topic": topic,
                "difficulty_level": difficulty,
                "title": f"{topic} - {subject}",
                "content": content,
                "key_concepts": self._extract_key_concepts(content, topic),
                "duration_minutes": 25,
                "learning_objectives": [
                    f"Understand the core concepts of {topic}",
                    f"Apply {topic} principles to solve problems",
                    f"Analyze real-world applications of {topic}",
                    f"Develop critical thinking skills in {subject}"
                ],
                "created_at": datetime.now().isoformat(),
                "model_used": "educational_ai"
            }
            
            return lesson
            
        except Exception as e:
            logger.error(f"AI lesson generation failed: {e}")
            return self._create_fallback_lesson(subject, topic, difficulty)
    
    async def generate_quiz_questions(
        self,
        subject: str,
        topic: str,
        difficulty: str = "intermediate",
        num_questions: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate educational quiz questions using AI."""
        await self.initialize()
        
        questions = []
        
        for i in range(num_questions):
            # Create prompt for each question
            prompt = f"""Create a {difficulty} level multiple choice quiz question about "{topic}" in {subject}.

Requirements:
- Clear, specific question that tests understanding
- Four distinct answer choices (A, B, C, D)
- One clearly correct answer
- Brief explanation of why the answer is correct

Format your response exactly like this:
Question: [Your question here]
A) [First option]
B) [Second option]
C) [Third option]
D) [Fourth option]
Correct Answer: [Letter of correct answer]
Explanation: [Brief explanation why this is correct]

Topic: {topic}
Subject: {subject}
Level: {difficulty}

Create question {i+1}:"""

            try:
                response = await ai_model_manager.generate_content(
                    prompt, 
                    content_type="quiz"
                )
                
                question_data = self._parse_quiz_response(response, i+1, topic, subject)
                questions.append(question_data)
                
                # Small delay to avoid overwhelming the model
                await asyncio.sleep(0.3)
                
            except Exception as e:
                logger.error(f"Failed to generate question {i+1}: {e}")
                # Add fallback question
                questions.append(self._create_fallback_question(topic, subject, i+1, difficulty))
        
        return questions
    
    async def generate_chat_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        subject: str = "General"
    ) -> str:
        """Generate educational chat response."""
        await self.initialize()
        
        # Build context from conversation history
        context = ""
        if conversation_history:
            recent_messages = conversation_history[-3:]  # Last 3 exchanges
            for msg in recent_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context += f"{role.title()}: {content}\n"
        
        # Create educational chat prompt
        prompt = f"""You are a helpful AI tutor specializing in {subject}. Your role is to:
- Provide clear, accurate educational explanations
- Encourage learning and curiosity
- Break down complex concepts into understandable parts
- Give helpful examples and analogies
- Ask follow-up questions to check understanding

{context}
Student: {user_message}

As their AI tutor, provide a helpful, educational response:"""

        try:
            response = await ai_model_manager.generate_content(
                prompt,
                content_type="chat"
            )
            
            # Clean up the response
            response = response.strip()
            if not response:
                response = f"I'd be happy to help you learn about {subject}! Could you tell me more about what specific aspect you'd like to explore?"
            
            return response
            
        except Exception as e:
            logger.error(f"Chat response generation failed: {e}")
            return f"I'm here to help you learn about {subject}! What would you like to know more about?"
    
    def _extract_key_concepts(self, content: str, topic: str) -> List[str]:
        """Extract key learning concepts from lesson content."""
        concepts = []
        
        # Look for structured content indicators
        lines = content.lower().split('\n')
        for line in lines:
            line = line.strip()
            # Look for numbered lists, bullet points, or key terms
            if any(indicator in line for indicator in ['key', 'important', 'concept', 'principle', 'understand']):
                if any(prefix in line for prefix in ['1.', '2.', '3.', '-', '•', '*']):
                    # Clean up the line
                    clean_concept = line
                    for prefix in ['1.', '2.', '3.', '4.', '5.', '-', '•', '*', 'key', 'important']:
                        clean_concept = clean_concept.replace(prefix, '').strip()
                    if clean_concept and len(clean_concept) > 10:
                        concepts.append(clean_concept.capitalize())
        
        # Default concepts if none extracted
        if not concepts:
            concepts = [
                f"Understanding {topic}",
                f"Practical applications of {topic}",
                f"Key principles and methods",
                f"Problem-solving approaches",
                f"Real-world connections"
            ]
        
        return concepts[:5]  # Limit to 5 key concepts
    
    def _parse_quiz_response(self, response: str, question_num: int, topic: str, subject: str) -> Dict[str, Any]:
        """Parse AI-generated quiz question into structured format."""
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        question_text = ""
        options = []
        correct_answer = ""
        explanation = ""
        
        for line in lines:
            if line.startswith("Question:"):
                question_text = line.replace("Question:", "").strip()
            elif line.startswith(("A)", "B)", "C)", "D)")):
                option_text = line[2:].strip()  # Remove "A)" prefix
                options.append(option_text)
                # Check if this is marked as correct
                if "correct answer:" in response.lower():
                    correct_letter = line[0]
                    if f"correct answer: {correct_letter.lower()}" in response.lower() or f"correct: {correct_letter.lower()}" in response.lower():
                        correct_answer = option_text
            elif any(start in line.lower() for start in ["correct answer:", "correct:", "explanation:"]):
                if "explanation:" in line.lower():
                    explanation = line.split("explanation:")[-1].strip()
                elif not correct_answer and len(options) > 0:
                    # Try to identify correct answer
                    for opt in options:
                        if opt.lower() in line.lower():
                            correct_answer = opt
                            break
        
        # Fallback values if parsing failed
        if not question_text:
            question_text = f"What is an important concept related to {topic} in {subject}?"
        
        if not options:
            options = [
                f"Core principles of {topic}",
                "Unrelated concept",
                "Incorrect approach",
                "Random information"
            ]
        
        if not correct_answer and options:
            correct_answer = options[0]  # Default to first option
        
        if not explanation:
            explanation = f"This question tests understanding of key concepts in {topic}."
        
        return {
            "question_id": f"q_{question_num}",
            "question_text": question_text,
            "answer_options": options[:4],  # Ensure exactly 4 options
            "correct_answer": correct_answer,
            "explanation": explanation,
            "difficulty_level": 0.6,  # Medium difficulty
            "topic": topic,
            "subject": subject
        }
    
    def _create_fallback_lesson(self, subject: str, topic: str, difficulty: str) -> Dict[str, Any]:
        """Create a fallback lesson when AI generation fails."""
        content_templates = {
            "mathematics": f"""
            # Learning {topic} in Mathematics
            
            ## Introduction
            {topic} is a fundamental mathematical concept that builds the foundation for advanced problem-solving. Understanding this topic will enhance your analytical thinking and mathematical reasoning skills.
            
            ## Key Concepts
            • **Definition**: Understanding what {topic} means in mathematical context
            • **Applications**: How {topic} is used to solve real problems
            • **Methods**: Step-by-step approaches to working with {topic}
            • **Connections**: How {topic} relates to other mathematical concepts
            
            ## Practice Approach
            1. Start with basic definitions and examples
            2. Work through guided practice problems
            3. Apply concepts to real-world scenarios
            4. Check understanding with varied exercises
            
            ## Summary
            Mastering {topic} requires understanding both theory and practical application. Practice regularly and connect new knowledge to previously learned concepts.
            """,
            
            "science": f"""
            # Exploring {topic} in Science
            
            ## Introduction
            {topic} is an important scientific concept that helps us understand natural phenomena and scientific principles. This knowledge forms the basis for scientific inquiry and discovery.
            
            ## Scientific Understanding
            • **Observation**: What we can observe about {topic}
            • **Theory**: Scientific explanations behind {topic}
            • **Evidence**: How scientific evidence supports our understanding
            • **Applications**: Practical uses of {topic} in science and technology
            
            ## Investigation Methods
            1. Form hypotheses about {topic}
            2. Design experiments to test understanding
            3. Collect and analyze data
            4. Draw conclusions based on evidence
            
            ## Real-World Connections
            Understanding {topic} helps explain many phenomena we observe in everyday life and forms the foundation for technological advances.
            """
        }
        
        # Get appropriate template or use general template
        subject_key = subject.lower()
        if subject_key in content_templates:
            content = content_templates[subject_key]
        else:
            content = f"""
            # Understanding {topic} in {subject}
            
            ## Learning Objectives
            By studying {topic}, you will develop a comprehensive understanding of this important concept in {subject}.
            
            ## Core Concepts
            • Fundamental principles of {topic}
            • Key terminology and definitions
            • Practical applications and examples
            • Problem-solving strategies
            
            ## Study Approach
            1. Begin with basic concepts and build complexity gradually
            2. Practice with varied examples and scenarios
            3. Connect new learning to existing knowledge
            4. Apply concepts to real-world situations
            
            ## Assessment
            Test your understanding through practice questions, discussions, and practical applications of {topic} concepts.
            """
        
        return {
            "id": f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "subject": subject,
            "topic": topic,
            "difficulty_level": difficulty,
            "title": f"{topic} - {subject}",
            "content": content.strip(),
            "key_concepts": [
                f"Understanding {topic}",
                "Practical applications",
                "Problem-solving methods",
                "Real-world connections"
            ],
            "duration_minutes": 25,
            "learning_objectives": [
                f"Master fundamental concepts of {topic}",
                f"Apply {topic} knowledge to solve problems",
                f"Analyze {topic} in real-world contexts",
                f"Develop critical thinking skills"
            ],
            "created_at": datetime.now().isoformat(),
            "model_used": "educational_fallback"
        }
    
    def _create_fallback_question(self, topic: str, subject: str, question_num: int, difficulty: str) -> Dict[str, Any]:
        """Create a fallback quiz question."""
        question_templates = {
            "easy": [
                f"What is {topic}?",
                f"Which of the following describes {topic}?",
                f"What is the main purpose of {topic}?",
            ],
            "intermediate": [
                f"How is {topic} applied in {subject}?",
                f"What are the key characteristics of {topic}?",
                f"Which principle best explains {topic}?",
            ],
            "hard": [
                f"How does {topic} relate to advanced concepts in {subject}?",
                f"What would happen if you modified {topic} in a complex system?",
                f"How would you solve a complex problem involving {topic}?",
            ]
        }
        
        templates = question_templates.get(difficulty, question_templates["intermediate"])
        question_text = templates[question_num % len(templates)]
        
        return {
            "question_id": f"q_{question_num}",
            "question_text": question_text,
            "answer_options": [
                f"Comprehensive understanding and proper application of {topic}",
                "Basic memorization without understanding",
                "Avoiding complex aspects of the concept", 
                "Guessing without systematic approach"
            ],
            "correct_answer": f"Comprehensive understanding and proper application of {topic}",
            "explanation": f"Success with {topic} requires thorough understanding and practical application skills.",
            "difficulty_level": 0.5,
            "topic": topic,
            "subject": subject
        }
    
    async def generate_quiz(
        self,
        subject: str,
        topic: str,
        difficulty: str = "medium",
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """Generate a complete quiz with questions - compatibility method for quiz endpoint."""
        await self.initialize()
        
        try:
            # Generate questions using the existing method
            questions = await self.generate_quiz_questions(
                subject=subject,
                topic=topic,
                difficulty=difficulty,
                num_questions=num_questions
            )
            
            # Format as a complete quiz response
            quiz_data = {
                "quiz_id": f"quiz_{datetime.utcnow().timestamp()}",
                "title": f"{subject}: {topic} Quiz",
                "subject": subject,
                "topic": topic,
                "difficulty_level": difficulty,
                "num_questions": len(questions),
                "questions": questions,
                "time_limit_minutes": min(num_questions * 2, 30),  # 2 minutes per question, max 30
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"✅ Generated quiz with {len(questions)} questions for {subject}: {topic}")
            return quiz_data
            
        except Exception as e:
            logger.error(f"Quiz generation failed: {e}")
            # Return fallback quiz
            return {
                "quiz_id": f"fallback_quiz_{datetime.utcnow().timestamp()}",
                "title": f"{subject}: {topic} Quiz",
                "subject": subject,
                "topic": topic,
                "difficulty_level": difficulty,
                "num_questions": 1,
                "questions": [{
                    "id": "q_1",
                    "question": f"What is an important concept in {topic}?",
                    "options": ["Basic principle", "Advanced theory", "Practical application", "All of the above"],
                    "correct_answer": "All of the above",
                    "explanation": f"Understanding {topic} requires grasping multiple aspects including principles, theory, and applications."
                }],
                "time_limit_minutes": 10,
                "created_at": datetime.utcnow().isoformat()
            }


# Global instance
advanced_ai_generator = AdvancedAIGenerator()
