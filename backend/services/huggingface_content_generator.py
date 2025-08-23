"""
Hugging Face Content Generator Service

Uses Hugging Face models to generate educational lessons and quizzes.
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import random

# Import with error handling
try:
    from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Transformers not fully available: {e}")
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)

class HuggingFaceContentGenerator:
    """Content generator using Hugging Face models."""
    
    def __init__(self):
        self.text_generator = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize the content generator with Hugging Face models."""
        if self.initialized:
            return
            
        try:
            if TRANSFORMERS_AVAILABLE:
                logger.info("Initializing Hugging Face text generator...")
                # Use a lightweight model that works well for educational content
                self.text_generator = pipeline(
                    "text-generation",
                    model="distilgpt2",  # Lightweight and fast
                    max_length=200,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=50256
                )
                logger.info("Hugging Face model initialized successfully")
            else:
                logger.warning("Transformers not available, using fallback content generation")
                
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face model: {e}")
            self.initialized = True  # Mark as initialized to avoid retrying
    
    def _generate_text(self, prompt: str, max_length: int = 150) -> str:
        """Generate text using the Hugging Face model."""
        if not self.text_generator:
            return self._fallback_content(prompt)
            
        try:
            # Generate text
            result = self.text_generator(
                prompt,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                truncation=True
            )
            
            generated_text = result[0]['generated_text']
            # Remove the original prompt from the generated text
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
                
            return generated_text
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return self._fallback_content(prompt)
    
    def _fallback_content(self, topic: str) -> str:
        """Fallback content when AI model is not available."""
        fallback_content = {
            "mathematics": "Mathematics is the study of numbers, shapes, and patterns. It includes arithmetic, algebra, geometry, and calculus.",
            "science": "Science is the systematic study of the natural world through observation and experimentation.",
            "physics": "Physics is the branch of science that studies matter, energy, and the fundamental forces of nature.",
            "chemistry": "Chemistry is the study of atoms, molecules, and chemical reactions.",
            "biology": "Biology is the study of living organisms and life processes.",
            "history": "History is the study of past events and their impact on human civilization.",
            "literature": "Literature encompasses written works including novels, poems, and plays that express human experience.",
            "programming": "Programming is the process of creating instructions for computers to execute tasks.",
            "machine learning": "Machine learning is a subset of AI where computers learn patterns from data.",
            "artificial intelligence": "AI is the simulation of human intelligence in machines."
        }
        
        topic_lower = topic.lower()
        for key, content in fallback_content.items():
            if key in topic_lower:
                return content
                
        return f"This lesson covers important concepts related to {topic}. Understanding these fundamentals will help you build a strong foundation in this subject area."
    
    async def generate_lesson(
        self,
        subject: str,
        topic: str,
        difficulty_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """Generate a comprehensive lesson using Hugging Face models."""
        await self.initialize()
        
        # Create lesson prompt
        prompt = f"Explain {topic} in {subject} for {difficulty_level} level students:"
        
        # Generate lesson content
        lesson_content = self._generate_text(prompt, max_length=200)
        
        # Generate key concepts
        concepts_prompt = f"Key concepts in {topic}:"
        key_concepts = self._generate_text(concepts_prompt, max_length=100)
        
        # Create structured lesson
        lesson = {
            "id": f"lesson_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "subject": subject,
            "topic": topic,
            "difficulty_level": difficulty_level,
            "title": f"{topic} - {subject}",
            "content": lesson_content,
            "key_concepts": key_concepts.split('.') if key_concepts else [f"Understanding {topic}"],
            "duration_minutes": 15,
            "learning_objectives": [
                f"Understand the fundamentals of {topic}",
                f"Apply {topic} concepts to practical problems",
                f"Analyze the importance of {topic} in {subject}"
            ],
            "created_at": datetime.now().isoformat()
        }
        
        return lesson
    
    async def generate_quiz(
        self,
        subject: str,
        topic: str,
        difficulty_level: str = "intermediate",
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """Generate a quiz using Hugging Face models."""
        await self.initialize()
        
        questions = []
        
        # Generate questions using AI
        for i in range(num_questions):
            question_prompt = f"Create a {difficulty_level} level question about {topic} in {subject}:"
            question_text = self._generate_text(question_prompt, max_length=80)
            
            # Clean up the question
            if '?' not in question_text:
                question_text += "?"
            question_text = question_text.split('?')[0] + "?"
            
            # Generate options
            options_data = self._generate_quiz_options(topic, subject, difficulty_level)
            
            question = {
                "question_id": f"q_{i+1}",
                "question_text": question_text,
                "answer_options": options_data["options"],
                "correct_answer": options_data["correct"],
                "explanation": f"This question tests your understanding of {topic} concepts in {subject}.",
                "difficulty_level": 0.5 if difficulty_level == "intermediate" else (0.3 if difficulty_level == "beginner" else 0.8)
            }
            
            questions.append(question)
        
        quiz = {
            "quiz_id": f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "subject": subject,
            "topic": topic,
            "difficulty_level": difficulty_level,
            "questions": questions,
            "total_questions": len(questions),
            "estimated_time": len(questions) * 2,
            "created_at": datetime.now().isoformat()
        }
        
        return quiz
    
    def _generate_quiz_options(self, topic: str, subject: str, difficulty: str) -> Dict[str, Any]:
        """Generate quiz options based on topic."""
        # Topic-specific options
        topic_options = {
            "mathematics": {
                "algebra": ["x = 2", "x = 5", "x = -1", "x = 0"],
                "geometry": ["90 degrees", "180 degrees", "360 degrees", "45 degrees"],
                "calculus": ["dy/dx", "integral", "derivative", "limit"]
            },
            "science": {
                "physics": ["Force = Mass × Acceleration", "E = mc²", "P = F/A", "v = d/t"],
                "chemistry": ["H₂O", "CO₂", "NaCl", "CH₄"],
                "biology": ["Mitochondria", "Nucleus", "Cell membrane", "Cytoplasm"]
            },
            "programming": {
                "python": ["def function():", "class MyClass:", "import numpy", "print('Hello')"],
                "javascript": ["function() {}", "let variable = 5", "console.log()", "if (true) {}"]
            }
        }
        
        # Get subject-specific options
        subject_lower = subject.lower()
        topic_lower = topic.lower()
        
        options = ["Option A", "Option B", "Option C", "Option D"]
        
        if subject_lower in topic_options:
            for key, opts in topic_options[subject_lower].items():
                if key in topic_lower:
                    options = opts[:4]  # Take first 4 options
                    break
        
        # Ensure we have exactly 4 options
        while len(options) < 4:
            options.append(f"Additional option {len(options)}")
        
        return {
            "options": options,
            "correct": options[0]  # First option is correct
        }

# Global instance
hf_content_generator = HuggingFaceContentGenerator()
