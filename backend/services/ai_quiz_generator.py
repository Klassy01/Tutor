"""
Enhanced AI Quiz Generator Service

Generates educational quizzes using local AI models without requiring API keys.
"""

import json
import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from backend.services.ai_models import ai_model_manager

logger = logging.getLogger(__name__)


class AIQuizGenerator:
    """Enhanced quiz generator using local AI models."""
    
    def __init__(self):
        self.initialized = False
    
    async def initialize(self):
        """Initialize the quiz generator."""
        if not self.initialized:
            logger.info("Initializing AI Quiz Generator...")
            # Warm up the AI models
            await ai_model_manager.warmup_models()
            self.initialized = True
    
    async def generate_quiz(
        self,
        subject: str,
        topic: str,
        difficulty_level: str = "intermediate",
        num_questions: int = 5,
        question_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive quiz for the given parameters.
        
        Args:
            subject: The subject area (e.g., "Mathematics", "Science", "History")
            topic: Specific topic within the subject
            difficulty_level: "beginner", "intermediate", or "advanced"
            num_questions: Number of questions to generate
            question_types: Types of questions ["multiple_choice", "true_false", "fill_blank"]
        
        Returns:
            Dictionary containing the quiz data
        """
        if not self.initialized:
            await self.initialize()
        
        if question_types is None:
            question_types = ["multiple_choice"]
        
        try:
            quiz_data = {
                "quiz_id": f"quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "subject": subject,
                "topic": topic,
                "difficulty_level": difficulty_level,
                "created_at": datetime.now().isoformat(),
                "questions": []
            }
            
            for i in range(num_questions):
                question_type = question_types[i % len(question_types)]
                question = await self._generate_question(
                    subject, topic, difficulty_level, question_type, i + 1
                )
                if question:
                    quiz_data["questions"].append(question)
            
            # Add quiz metadata
            quiz_data["total_questions"] = len(quiz_data["questions"])
            quiz_data["estimated_time"] = len(quiz_data["questions"]) * 2  # 2 minutes per question
            
            return quiz_data
            
        except Exception as e:
            logger.error(f"Quiz generation error: {e}")
            return self._create_fallback_quiz(subject, topic, difficulty_level, num_questions)
    
    async def _generate_question(
        self,
        subject: str,
        topic: str,
        difficulty_level: str,
        question_type: str,
        question_number: int
    ) -> Optional[Dict[str, Any]]:
        """Generate a single question."""
        try:
            if question_type == "multiple_choice":
                return await self._generate_multiple_choice(subject, topic, difficulty_level, question_number)
            elif question_type == "true_false":
                return await self._generate_true_false(subject, topic, difficulty_level, question_number)
            elif question_type == "fill_blank":
                return await self._generate_fill_blank(subject, topic, difficulty_level, question_number)
            else:
                return await self._generate_multiple_choice(subject, topic, difficulty_level, question_number)
        except Exception as e:
            logger.error(f"Question generation error: {e}")
            return None
    
    async def _generate_multiple_choice(
        self,
        subject: str,
        topic: str,
        difficulty_level: str,
        question_number: int
    ) -> Dict[str, Any]:
        """Generate a multiple choice question."""
        prompt = f"""Create a {difficulty_level} level multiple choice question about {topic} in {subject}.

Requirements:
- Clear, educational question
- 4 options labeled A, B, C, D
- Only one correct answer
- Brief explanation for the correct answer
- Appropriate for {difficulty_level} level students

Format your response as:
Question: [Your question here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct Answer: [A, B, C, or D]
Explanation: [Brief explanation]

Generate the question now:"""

        response = await ai_model_manager.get_response(prompt)
        
        # Parse the AI response
        return self._parse_multiple_choice_response(response, question_number)
    
    async def _generate_true_false(
        self,
        subject: str,
        topic: str,
        difficulty_level: str,
        question_number: int
    ) -> Dict[str, Any]:
        """Generate a true/false question."""
        prompt = f"""Create a {difficulty_level} level true/false question about {topic} in {subject}.

Requirements:
- Clear statement that is either true or false
- Educational and factual
- Appropriate for {difficulty_level} level students
- Brief explanation

Format:
Statement: [Your statement here]
Answer: [True or False]
Explanation: [Brief explanation]

Generate the question now:"""

        response = await ai_model_manager.get_response(prompt)
        
        return self._parse_true_false_response(response, question_number)
    
    async def _generate_fill_blank(
        self,
        subject: str,
        topic: str,
        difficulty_level: str,
        question_number: int
    ) -> Dict[str, Any]:
        """Generate a fill-in-the-blank question."""
        prompt = f"""Create a {difficulty_level} level fill-in-the-blank question about {topic} in {subject}.

Requirements:
- Sentence with one important word/phrase missing
- The missing word should be key to understanding the concept
- Provide the correct answer
- Brief explanation
- Use _____ for the blank

Format:
Question: [Sentence with _____ for the blank]
Answer: [Correct word/phrase]
Explanation: [Brief explanation]

Generate the question now:"""

        response = await ai_model_manager.get_response(prompt)
        
        return self._parse_fill_blank_response(response, question_number)
    
    def _parse_multiple_choice_response(self, response: str, question_number: int) -> Dict[str, Any]:
        """Parse AI response for multiple choice questions."""
        try:
            lines = response.strip().split('\n')
            question_text = ""
            options = {}
            correct_answer = ""
            explanation = ""
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith("Question:"):
                    question_text = line.replace("Question:", "").strip()
                elif line.startswith(("A)", "A.", "A:")):
                    options["A"] = re.sub(r'^A[)\.:]', '', line).strip()
                elif line.startswith(("B)", "B.", "B:")):
                    options["B"] = re.sub(r'^B[)\.:]', '', line).strip()
                elif line.startswith(("C)", "C.", "C:")):
                    options["C"] = re.sub(r'^C[)\.:]', '', line).strip()
                elif line.startswith(("D)", "D.", "D:")):
                    options["D"] = re.sub(r'^D[)\.:]', '', line).strip()
                elif line.startswith("Correct Answer:"):
                    correct_answer = line.replace("Correct Answer:", "").strip().upper()
                elif line.startswith("Explanation:"):
                    explanation = line.replace("Explanation:", "").strip()
            
            # Fallback parsing if primary parsing fails
            if not question_text or not options:
                return self._create_fallback_multiple_choice(question_number)
            
            return {
                "id": question_number,
                "type": "multiple_choice",
                "question": question_text,
                "options": options,
                "correct_answer": correct_answer if correct_answer in options else "A",
                "explanation": explanation or f"This question tests knowledge of the topic.",
                "points": 1
            }
            
        except Exception as e:
            logger.error(f"Parsing error: {e}")
            return self._create_fallback_multiple_choice(question_number)
    
    def _parse_true_false_response(self, response: str, question_number: int) -> Dict[str, Any]:
        """Parse AI response for true/false questions."""
        try:
            lines = response.strip().split('\n')
            statement = ""
            answer = ""
            explanation = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("Statement:"):
                    statement = line.replace("Statement:", "").strip()
                elif line.startswith("Answer:"):
                    answer = line.replace("Answer:", "").strip().lower()
                elif line.startswith("Explanation:"):
                    explanation = line.replace("Explanation:", "").strip()
            
            if not statement:
                return self._create_fallback_true_false(question_number)
            
            is_true = "true" in answer
            
            return {
                "id": question_number,
                "type": "true_false",
                "question": statement,
                "correct_answer": is_true,
                "explanation": explanation or "This statement tests understanding of key concepts.",
                "points": 1
            }
            
        except Exception as e:
            logger.error(f"True/false parsing error: {e}")
            return self._create_fallback_true_false(question_number)
    
    def _parse_fill_blank_response(self, response: str, question_number: int) -> Dict[str, Any]:
        """Parse AI response for fill-in-the-blank questions."""
        try:
            lines = response.strip().split('\n')
            question_text = ""
            answer = ""
            explanation = ""
            
            for line in lines:
                line = line.strip()
                if line.startswith("Question:"):
                    question_text = line.replace("Question:", "").strip()
                elif line.startswith("Answer:"):
                    answer = line.replace("Answer:", "").strip()
                elif line.startswith("Explanation:"):
                    explanation = line.replace("Explanation:", "").strip()
            
            if not question_text or not answer:
                return self._create_fallback_fill_blank(question_number)
            
            return {
                "id": question_number,
                "type": "fill_blank",
                "question": question_text,
                "correct_answer": answer,
                "explanation": explanation or "This tests knowledge of key terms and concepts.",
                "points": 1
            }
            
        except Exception as e:
            logger.error(f"Fill blank parsing error: {e}")
            return self._create_fallback_fill_blank(question_number)
    
    def _create_fallback_quiz(self, subject: str, topic: str, difficulty_level: str, num_questions: int) -> Dict[str, Any]:
        """Create a fallback quiz when AI generation fails."""
        questions = []
        
        for i in range(num_questions):
            questions.append({
                "id": i + 1,
                "type": "multiple_choice",
                "question": f"What is an important concept to understand about {topic} in {subject}?",
                "options": {
                    "A": f"Basic principles of {topic}",
                    "B": f"Advanced applications of {topic}",
                    "C": f"Historical context of {topic}",
                    "D": f"Future developments in {topic}"
                },
                "correct_answer": "A",
                "explanation": f"Understanding basic principles is fundamental to learning {topic}.",
                "points": 1
            })
        
        return {
            "quiz_id": f"fallback_quiz_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "subject": subject,
            "topic": topic,
            "difficulty_level": difficulty_level,
            "questions": questions,
            "total_questions": len(questions),
            "estimated_time": len(questions) * 2,
            "created_at": datetime.now().isoformat()
        }
    
    def _create_fallback_multiple_choice(self, question_number: int) -> Dict[str, Any]:
        """Create a fallback multiple choice question."""
        return {
            "id": question_number,
            "type": "multiple_choice",
            "question": "Which of the following is a key learning concept?",
            "options": {
                "A": "Understanding fundamental principles",
                "B": "Memorizing facts only",
                "C": "Avoiding practice",
                "D": "Learning in isolation"
            },
            "correct_answer": "A",
            "explanation": "Understanding fundamental principles is essential for effective learning.",
            "points": 1
        }
    
    def _create_fallback_true_false(self, question_number: int) -> Dict[str, Any]:
        """Create a fallback true/false question."""
        return {
            "id": question_number,
            "type": "true_false",
            "question": "Active learning is more effective than passive learning.",
            "correct_answer": True,
            "explanation": "Active learning engages students and improves retention and understanding.",
            "points": 1
        }
    
    def _create_fallback_fill_blank(self, question_number: int) -> Dict[str, Any]:
        """Create a fallback fill-in-the-blank question."""
        return {
            "id": question_number,
            "type": "fill_blank",
            "question": "Effective learning requires _____ and practice.",
            "correct_answer": "understanding",
            "explanation": "Understanding concepts deeply is crucial for effective learning.",
            "points": 1
        }
    
    async def generate_adaptive_questions(
        self,
        student_performance: Dict[str, Any],
        subject: str,
        topic: str
    ) -> List[Dict[str, Any]]:
        """Generate adaptive questions based on student performance."""
        try:
            difficulty = self._determine_difficulty(student_performance)
            weak_areas = self._identify_weak_areas(student_performance)
            
            questions = []
            
            # Generate questions focusing on weak areas
            for area in weak_areas[:3]:  # Focus on top 3 weak areas
                question = await self._generate_question(
                    subject, area, difficulty, "multiple_choice", len(questions) + 1
                )
                if question:
                    questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Adaptive question generation error: {e}")
            return []
    
    def _determine_difficulty(self, performance: Dict[str, Any]) -> str:
        """Determine appropriate difficulty based on performance."""
        avg_score = performance.get("average_score", 0.5)
        
        if avg_score < 0.4:
            return "beginner"
        elif avg_score < 0.7:
            return "intermediate"
        else:
            return "advanced"
    
    def _identify_weak_areas(self, performance: Dict[str, Any]) -> List[str]:
        """Identify areas where student needs improvement."""
        weak_areas = performance.get("weak_topics", [])
        return weak_areas if weak_areas else ["fundamental concepts", "problem solving", "application"]


# Global instance
ai_quiz_generator = AIQuizGenerator()
