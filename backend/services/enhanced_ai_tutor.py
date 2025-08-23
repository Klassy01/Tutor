"""
Enhanced AI Tutor Service with Advanced Features

Provides comprehensive AI tutoring capabilities using local models.
"""

import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

from backend.services.ai_models import ai_model_manager
from backend.services.ai_quiz_generator import ai_quiz_generator
from backend.core.config import settings

logger = logging.getLogger(__name__)


class EnhancedAITutorService:
    """Enhanced AI Tutor Service with advanced learning capabilities."""
    
    def __init__(self):
        self.conversation_histories: Dict[int, List[Dict[str, Any]]] = {}
        self.student_profiles: Dict[int, Dict[str, Any]] = {}
        self.learning_analytics: Dict[int, Dict[str, Any]] = {}
        self.initialized = False
        
    async def initialize(self):
        """Initialize the enhanced AI tutor service."""
        if self.initialized:
            return
            
        logger.info("Initializing Enhanced AI Tutor Service...")
        
        # Initialize AI models
        await ai_model_manager.warmup_models()
        
        # Initialize quiz generator
        await ai_quiz_generator.initialize()
        
        self.initialized = True
        logger.info("✅ Enhanced AI Tutor Service initialized successfully")
    
    async def get_tutoring_response(
        self,
        student_id: int,
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive AI tutoring response.
        
        Args:
            student_id: ID of the student
            message: Student's message/question
            context: Additional context (subject, topic, etc.)
        
        Returns:
            Comprehensive response with tutoring content, recommendations, etc.
        """
        try:
            if not self.initialized:
                await self.initialize()
            
            # Get or create student profile
            student_profile = self._get_student_profile(student_id)
            
            # Get conversation history
            conversation_history = self._get_conversation_history(student_id)
            
            # Analyze the message for learning intent
            intent_analysis = await self._analyze_learning_intent(message, context)
            
            # Generate contextual response
            response = await self._generate_contextual_response(
                message=message,
                student_profile=student_profile,
                conversation_history=conversation_history,
                intent_analysis=intent_analysis,
                context=context
            )
            
            # Generate recommendations
            recommendations = await self._generate_learning_recommendations(
                student_id=student_id,
                current_topic=intent_analysis.get("subject"),
                response_content=response
            )
            
            # Update conversation history
            self._add_to_conversation_history(
                student_id=student_id,
                role="student",
                content=message,
                metadata={"intent": intent_analysis, "context": context}
            )
            
            self._add_to_conversation_history(
                student_id=student_id,
                role="tutor",
                content=response,
                metadata={"recommendations": recommendations}
            )
            
            # Update learning analytics
            await self._update_learning_analytics(student_id, intent_analysis, response)
            
            return {
                "response": response,
                "intent_analysis": intent_analysis,
                "recommendations": recommendations,
                "follow_up_questions": self._generate_follow_up_questions(intent_analysis),
                "confidence": 0.85,
                "learning_insights": self._generate_learning_insights(student_profile),
                "timestamp": datetime.now().isoformat(),
                "student_id": student_id
            }
            
        except Exception as e:
            logger.error(f"Error in tutoring response: {e}")
            return self._create_fallback_response(message, student_id)
    
    async def _analyze_learning_intent(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze the learning intent behind a student's message."""
        
        # Keywords analysis
        keywords = {
            "mathematics": ["math", "algebra", "geometry", "calculus", "equation", "formula", "number"],
            "science": ["physics", "chemistry", "biology", "experiment", "molecule", "force", "energy"],
            "history": ["history", "ancient", "war", "civilization", "empire", "timeline", "historical"],
            "english": ["grammar", "writing", "literature", "essay", "poem", "story", "language"],
            "computer_science": ["programming", "code", "algorithm", "data", "computer", "software"],
            "help_request": ["help", "explain", "understand", "confused", "don't know", "how to"],
            "quiz_request": ["quiz", "test", "practice", "questions", "exam", "assessment"],
            "concept_explanation": ["what is", "how does", "why", "define", "meaning", "concept"]
        }
        
        detected_subjects = []
        detected_intents = []
        
        message_lower = message.lower()
        
        for subject, terms in keywords.items():
            if any(term in message_lower for term in terms):
                if subject in ["mathematics", "science", "history", "english", "computer_science"]:
                    detected_subjects.append(subject)
                else:
                    detected_intents.append(subject)
        
        # Determine primary subject
        primary_subject = detected_subjects[0] if detected_subjects else context.get("subject", "general")
        
        # Determine learning intent
        if "quiz_request" in detected_intents:
            intent_type = "quiz_generation"
        elif "concept_explanation" in detected_intents:
            intent_type = "concept_explanation"
        elif "help_request" in detected_intents:
            intent_type = "help_request"
        else:
            intent_type = "general_learning"
        
        # Extract topic if mentioned
        topic = context.get("topic", "general concepts")
        
        return {
            "intent_type": intent_type,
            "subject": primary_subject,
            "topic": topic,
            "detected_subjects": detected_subjects,
            "detected_intents": detected_intents,
            "complexity_level": self._estimate_complexity_level(message),
            "question_type": self._classify_question_type(message)
        }
    
    async def _generate_contextual_response(
        self,
        message: str,
        student_profile: Dict[str, Any],
        conversation_history: List[Dict[str, Any]],
        intent_analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Generate a contextual AI response based on comprehensive analysis."""
        
        # Build comprehensive prompt
        system_prompt = self._build_advanced_system_prompt(student_profile, intent_analysis)
        
        # Add conversation context
        conversation_context = self._build_conversation_context(conversation_history[-3:])
        
        # Create the full prompt
        full_prompt = f"""{system_prompt}

Previous conversation context:
{conversation_context}

Student's current question/message: "{message}"

Please provide a helpful, educational response that:
1. Directly addresses the student's question
2. Explains concepts clearly with examples
3. Adapts to the student's learning level
4. Encourages further learning
5. Uses engaging and supportive language

AI Tutor Response:"""

        # Get response from AI model - using enhanced educational AI
        response = await self._generate_educational_response(full_prompt, intent_analysis, message)
        
        # Clean and enhance the response
        return self._enhance_response(response, intent_analysis)

    async def _generate_educational_response(self, full_prompt: str, intent_analysis: Dict[str, Any], original_message: str) -> str:
        """Generate educational response with better AI handling."""
        try:
            # Try AI model first
            response = await ai_model_manager.get_response(full_prompt)
            
            # If AI model fails or gives poor response, use enhanced rule-based system
            if not response or len(response.strip()) < 20 or "error" in response.lower():
                response = self._generate_comprehensive_educational_response(original_message, intent_analysis)
                
            return response
        except Exception as e:
            logger.warning(f"AI model failed, using educational fallback: {e}")
            return self._generate_comprehensive_educational_response(original_message, intent_analysis)
    
    def _generate_comprehensive_educational_response(self, message: str, intent_analysis: Dict[str, Any]) -> str:
        """Generate comprehensive educational responses based on topics."""
        message_lower = message.lower()
        subject = intent_analysis.get("subject", "general")
        
        # Mathematics responses
        if "math" in subject or any(word in message_lower for word in ['algebra', 'equation', 'solve', 'calculate', 'math', 'number']):
            return """🔢 **Mathematics Help**

Great question! Let me help you understand this step by step.

**Problem-Solving Approach:**
1️⃣ **Understand the Problem**
   - Read carefully and identify what's given
   - Determine what you need to find
   - Look for key mathematical relationships

2️⃣ **Plan Your Strategy**
   - Choose the right mathematical tools
   - Break complex problems into smaller steps
   - Consider multiple solution methods

3️⃣ **Execute and Check**
   - Work through your solution systematically
   - Double-check your calculations
   - Verify your answer makes sense

**Key Tips:**
• Draw diagrams when possible
• Show all your work clearly  
• Practice similar problems for mastery
• Don't hesitate to try different approaches

Would you like me to help you work through a specific math problem? Share the details and I'll guide you step by step! 📐✨"""

        # Science responses  
        elif "science" in subject or any(word in message_lower for word in ['physics', 'chemistry', 'biology', 'experiment', 'theory']):
            return """🔬 **Science Exploration**

Excellent question! Science is all about understanding how our world works.

**Scientific Thinking Process:**
1️⃣ **Observe & Question**
   - Notice patterns in the natural world
   - Ask "why" and "how" questions
   - Form educated guesses (hypotheses)

2️⃣ **Investigate & Experiment**
   - Design tests to check your ideas
   - Collect and analyze data
   - Look for cause-and-effect relationships

3️⃣ **Conclude & Apply**
   - Draw conclusions from evidence
   - Connect concepts to real-world examples
   - Use knowledge to solve problems

**Study Strategies:**
• Use visual aids and diagrams
• Connect concepts to everyday experiences  
• Practice explaining ideas in your own words
• Look for patterns and relationships

What specific science topic would you like to explore? I can help you understand concepts, work through problems, or design experiments! 🧪⚗️"""

        # Programming/Computer Science
        elif any(word in message_lower for word in ['code', 'programming', 'python', 'javascript', 'algorithm', 'computer']):
            return """💻 **Programming & Computer Science**

Great question about programming! Let's break this down logically.

**Programming Problem-Solving:**
1️⃣ **Understand the Problem**
   - Read requirements carefully
   - Identify inputs and expected outputs
   - Break complex problems into smaller parts

2️⃣ **Design Your Solution**
   - Write pseudocode or flowcharts
   - Choose appropriate data structures
   - Plan your algorithm step by step

3️⃣ **Code & Test**
   - Write clean, readable code
   - Test with different inputs
   - Debug systematically

**Key Programming Concepts:**
• **Variables**: Store and manipulate data
• **Functions**: Reusable code blocks
• **Loops**: Repeat actions efficiently  
• **Conditionals**: Make decisions in code

**Best Practices:**
• Write clear, commented code
• Test thoroughly with edge cases
• Learn from others' code
• Practice regularly with projects

What programming concept or problem would you like help with? Share your code or describe what you're trying to build! 🚀👨‍💻"""

        # History responses
        elif "history" in subject or any(word in message_lower for word in ['history', 'historical', 'past', 'ancient', 'war', 'civilization']):
            return """🏛️ **Historical Understanding**

Fascinating historical question! Understanding the past helps us make sense of the present.

**Historical Analysis Framework:**
1️⃣ **Context Matters**
   - When and where did events occur?
   - What were the social, economic, political conditions?
   - Who were the key people involved?

2️⃣ **Cause and Effect**
   - What led to these events?
   - How did different factors interact?
   - What were the short and long-term consequences?

3️⃣ **Multiple Perspectives**
   - How did different groups experience events?
   - What sources tell us about the past?
   - How do we separate fact from interpretation?

**Study Strategies:**
• Create timelines to visualize sequences
• Use maps to understand geographic context
• Compare and contrast different periods
• Connect historical events to modern issues

**Critical Questions to Ask:**
• Why did this happen at this time?
• How did this affect different groups of people?
• What can we learn from this for today?

What historical period or event interests you? I'd love to help you explore the fascinating stories from our past! 📚🗺️"""

        # General study help
        elif any(word in message_lower for word in ['study', 'learn', 'exam', 'test', 'homework', 'assignment']):
            return """📚 **Effective Learning Strategies**

Great that you're focused on learning! Let me share proven study techniques.

**The Study Success Formula:**
1️⃣ **Active Learning Methods**
   • **Retrieval Practice**: Test yourself without notes
   • **Spaced Repetition**: Review material at increasing intervals  
   • **Elaboration**: Explain concepts in your own words
   • **Interleaving**: Mix different types of problems/topics

2️⃣ **Effective Study Habits**
   • Create a dedicated study environment
   • Use the Pomodoro Technique (25-min focused sessions)
   • Take regular breaks to maintain concentration
   • Stay hydrated and get adequate sleep

3️⃣ **Memory Enhancement**
   • Create visual mind maps
   • Use mnemonics and acronyms
   • Connect new information to what you already know
   • Teach concepts to someone else

**Subject-Specific Tips:**
• **Math/Science**: Practice problems regularly, understand concepts before memorizing
• **Languages**: Immerse yourself, practice speaking, use flashcards
• **History/Literature**: Create stories and connections, discuss with others

What subject are you studying for? I can provide more targeted strategies! 🎯✨"""

        # Default comprehensive response
        else:
            return f"""🌟 **Learning Together**

Thank you for your question: "{message}"

I'm here to help you learn and understand complex topics! As your AI tutor, I can assist with:

**📖 Academic Subjects:**
• Mathematics - from basic arithmetic to advanced calculus
• Sciences - physics, chemistry, biology, and more
• Programming - algorithms, coding, computer science
• History - understanding events, causes, and effects
• Languages - grammar, writing, communication skills

**🎯 Learning Support:**
• Breaking down complex problems into manageable steps
• Providing clear explanations with examples
• Creating practice questions and exercises
• Offering study strategies and techniques
• Giving personalized feedback and guidance

**💡 How I Can Help You Best:**
• Be specific about what you're studying
• Share any problems you're stuck on  
• Tell me your learning goals and challenges
• Ask for examples or practice problems

**Let's make learning engaging and effective!**

What specific topic would you like to explore today? I'm excited to help you discover new knowledge and build your understanding! 🚀📚"""
        
        # Clean and enhance the response
        return self._enhance_response(response, intent_analysis)
    
    def _build_advanced_system_prompt(
        self, 
        student_profile: Dict[str, Any], 
        intent_analysis: Dict[str, Any]
    ) -> str:
        """Build an advanced system prompt based on student profile and intent."""
        
        base_prompt = """You are an advanced AI tutor with expertise in personalized education. You provide:

✨ **Core Capabilities:**
- Clear, step-by-step explanations
- Adaptive difficulty based on student level
- Engaging examples and real-world connections
- Encouraging and supportive guidance
- Interactive learning approaches"""

        # Add subject-specific guidance
        subject = intent_analysis.get("subject", "general")
        if subject == "mathematics":
            base_prompt += """

🔢 **Mathematics Focus:**
- Break complex problems into smaller steps
- Show multiple solution methods when appropriate
- Use visual representations and analogies
- Connect math to real-world applications
- Encourage problem-solving strategies"""

        elif subject == "science":
            base_prompt += """

🔬 **Science Focus:**
- Explain scientific phenomena with clear mechanisms
- Use experiments and observations as examples
- Connect concepts to everyday experiences
- Encourage scientific thinking and questioning
- Show relationships between different scientific areas"""

        elif subject == "history":
            base_prompt += """

📚 **History Focus:**
- Provide context and background information
- Show cause-and-effect relationships
- Connect historical events to present day
- Use stories and narratives to engage
- Encourage critical thinking about sources"""

        # Add learning style adaptations
        learning_style = student_profile.get("learning_style", "mixed")
        base_prompt += f"""

🎯 **Learning Style Adaptation:** Adapted for {learning_style} learning style"""

        # Add difficulty level guidance
        difficulty = student_profile.get("difficulty_level", 0.5)
        if difficulty < 0.3:
            base_prompt += "\n- Use simple language and basic concepts\n- Provide more detailed explanations\n- Use lots of examples and analogies"
        elif difficulty > 0.7:
            base_prompt += "\n- Use advanced terminology appropriately\n- Provide in-depth analysis\n- Challenge with complex connections"
        else:
            base_prompt += "\n- Balance simplicity with depth\n- Gradually introduce complexity\n- Build on fundamental concepts"

        return base_prompt
    
    def _build_conversation_context(self, recent_messages: List[Dict[str, Any]]) -> str:
        """Build conversation context from recent messages."""
        context_lines = []
        for msg in recent_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:200]  # Limit length
            context_lines.append(f"{role.title()}: {content}")
        
        return "\n".join(context_lines) if context_lines else "No previous conversation."
    
    def _enhance_response(self, response: str, intent_analysis: Dict[str, Any]) -> str:
        """Enhance the AI response with formatting and educational elements."""
        
        # Clean up the response
        cleaned_response = response.strip()
        
        # Add subject-specific emojis and formatting
        subject = intent_analysis.get("subject", "general")
        intent_type = intent_analysis.get("intent_type", "general_learning")
        
        if intent_type == "quiz_generation":
            cleaned_response += "\n\n💡 **Tip:** Practice quizzes are a great way to test your understanding!"
        
        elif intent_type == "concept_explanation":
            cleaned_response += "\n\n🎯 **Remember:** Understanding concepts deeply is more valuable than memorization!"
        
        # Ensure response is educational and encouraging
        if len(cleaned_response) < 50:
            cleaned_response += " I'm here to help you learn and understand these concepts better!"
        
        return cleaned_response
    
    async def _generate_learning_recommendations(
        self,
        student_id: int,
        current_topic: Optional[str],
        response_content: str
    ) -> List[Dict[str, Any]]:
        """Generate personalized learning recommendations."""
        
        student_profile = self._get_student_profile(student_id)
        analytics = self.learning_analytics.get(student_id, {})
        
        recommendations = []
        
        # Practice recommendation
        recommendations.append({
            "title": "Practice Problems",
            "description": f"Try some practice problems to reinforce your understanding",
            "type": "practice",
            "priority": "high",
            "estimated_time": "15-20 minutes"
        })
        
        # Quiz recommendation
        if current_topic and current_topic != "general":
            recommendations.append({
                "title": f"Quiz on {current_topic.title()}",
                "description": f"Test your knowledge with a personalized quiz",
                "type": "assessment",
                "priority": "medium",
                "estimated_time": "10-15 minutes"
            })
        
        # Advanced topics recommendation
        difficulty_level = student_profile.get("difficulty_level", 0.5)
        if difficulty_level > 0.6:
            recommendations.append({
                "title": "Advanced Concepts",
                "description": "Explore more challenging aspects of this topic",
                "type": "advanced",
                "priority": "low",
                "estimated_time": "20-30 minutes"
            })
        
        return recommendations
    
    def _generate_follow_up_questions(self, intent_analysis: Dict[str, Any]) -> List[str]:
        """Generate contextual follow-up questions."""
        
        subject = intent_analysis.get("subject", "general")
        intent_type = intent_analysis.get("intent_type", "general_learning")
        
        base_questions = [
            "Would you like me to explain this in a different way?",
            "Do you have any specific questions about this topic?",
            "Should we try a practice problem together?"
        ]
        
        if intent_type == "concept_explanation":
            base_questions.extend([
                "Would you like to see some real-world examples?",
                "Should we explore how this connects to other concepts?"
            ])
        
        elif intent_type == "quiz_generation":
            base_questions.extend([
                "What difficulty level would you prefer?",
                "Which specific topics should I focus on?"
            ])
        
        if subject == "mathematics":
            base_questions.append("Would you like to work through a step-by-step example?")
        elif subject == "science":
            base_questions.append("Should we explore the scientific principles behind this?")
        
        return base_questions[:4]  # Limit to 4 questions
    
    def _generate_learning_insights(self, student_profile: Dict[str, Any]) -> List[str]:
        """Generate personalized learning insights."""
        
        insights = []
        
        difficulty_level = student_profile.get("difficulty_level", 0.5)
        learning_style = student_profile.get("learning_style", "mixed")
        
        if difficulty_level < 0.4:
            insights.append("Focus on building strong fundamentals before moving to advanced topics")
        elif difficulty_level > 0.7:
            insights.append("You're ready for challenging problems and advanced concepts")
        
        if learning_style == "visual":
            insights.append("Try using diagrams and visual aids to enhance your learning")
        elif learning_style == "hands_on":
            insights.append("Practice problems and interactive exercises work best for you")
        
        # Add general learning tips
        insights.append("Regular practice and review help strengthen long-term retention")
        
        return insights
    
    def _get_student_profile(self, student_id: int) -> Dict[str, Any]:
        """Get or create student profile."""
        if student_id not in self.student_profiles:
            self.student_profiles[student_id] = {
                "difficulty_level": 0.5,
                "learning_style": "mixed",
                "preferred_subjects": [],
                "weak_areas": [],
                "strong_areas": [],
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
        
        return self.student_profiles[student_id]
    
    def _get_conversation_history(self, student_id: int) -> List[Dict[str, Any]]:
        """Get conversation history for a student."""
        if student_id not in self.conversation_histories:
            self.conversation_histories[student_id] = []
        return self.conversation_histories[student_id]
    
    def _add_to_conversation_history(
        self, 
        student_id: int, 
        role: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add message to conversation history."""
        history = self._get_conversation_history(student_id)
        history.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 50 messages
        if len(history) > 50:
            history[:] = history[-50:]
    
    async def _update_learning_analytics(
        self, 
        student_id: int, 
        intent_analysis: Dict[str, Any], 
        response: str
    ):
        """Update learning analytics for the student."""
        if student_id not in self.learning_analytics:
            self.learning_analytics[student_id] = {
                "total_interactions": 0,
                "subjects_explored": set(),
                "topics_covered": set(),
                "question_types": {},
                "session_start": datetime.now().isoformat()
            }
        
        analytics = self.learning_analytics[student_id]
        analytics["total_interactions"] += 1
        analytics["subjects_explored"].add(intent_analysis.get("subject", "general"))
        analytics["topics_covered"].add(intent_analysis.get("topic", "general"))
        
        intent_type = intent_analysis.get("intent_type", "general_learning")
        analytics["question_types"][intent_type] = analytics["question_types"].get(intent_type, 0) + 1
        
        analytics["last_interaction"] = datetime.now().isoformat()
    
    def _estimate_complexity_level(self, message: str) -> str:
        """Estimate the complexity level of a student's message."""
        message_lower = message.lower()
        
        advanced_indicators = ["advanced", "complex", "detailed", "in-depth", "sophisticated"]
        basic_indicators = ["basic", "simple", "easy", "beginner", "start"]
        
        if any(indicator in message_lower for indicator in advanced_indicators):
            return "advanced"
        elif any(indicator in message_lower for indicator in basic_indicators):
            return "basic"
        else:
            return "intermediate"
    
    def _classify_question_type(self, message: str) -> str:
        """Classify the type of question being asked."""
        message_lower = message.lower()
        
        if message_lower.startswith(("what", "define", "meaning")):
            return "definition"
        elif message_lower.startswith(("how", "explain", "show me")):
            return "explanation"
        elif message_lower.startswith(("why", "reason", "because")):
            return "reasoning"
        elif any(word in message_lower for word in ["solve", "calculate", "find"]):
            return "problem_solving"
        elif any(word in message_lower for word in ["quiz", "test", "practice"]):
            return "assessment"
        else:
            return "general_inquiry"
    
    def _create_fallback_response(self, message: str, student_id: int) -> Dict[str, Any]:
        """Create a fallback response when AI processing fails."""
        return {
            "response": f"I understand you're asking about: '{message}'. While I'm having some technical difficulties, I'm still here to help you learn! Could you try rephrasing your question, or let me know what specific topic you'd like to explore?",
            "intent_analysis": {"intent_type": "general_learning", "subject": "general"},
            "recommendations": [
                {"title": "Try Again", "description": "Rephrase your question", "type": "retry"}
            ],
            "follow_up_questions": [
                "What subject are you working on?",
                "What specific concept would you like help with?",
                "Would you prefer a different type of explanation?"
            ],
            "confidence": 0.5,
            "learning_insights": ["I'm here to support your learning journey!"],
            "timestamp": datetime.now().isoformat(),
            "student_id": student_id,
            "error": "Fallback response due to processing error"
        }
    
    async def generate_study_plan(
        self, 
        student_id: int, 
        subject: str, 
        goals: List[str],
        timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """Generate a personalized study plan."""
        try:
            student_profile = self._get_student_profile(student_id)
            
            # Generate study plan using AI
            prompt = f"""Create a personalized {timeframe_days}-day study plan for {subject}.

Student Profile:
- Difficulty Level: {student_profile.get('difficulty_level', 0.5)}
- Learning Style: {student_profile.get('learning_style', 'mixed')}
- Goals: {', '.join(goals)}

Create a structured plan with:
1. Weekly breakdown
2. Daily topics and activities
3. Practice exercises
4. Review sessions
5. Milestones and assessments

Format as a clear, actionable study schedule."""

            response = await ai_model_manager.get_response(prompt)
            
            return {
                "study_plan": response,
                "subject": subject,
                "duration_days": timeframe_days,
                "goals": goals,
                "student_profile": student_profile,
                "created_at": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Study plan generation error: {e}")
            return {
                "study_plan": "I'm having trouble generating your study plan right now, but I recommend starting with fundamental concepts and gradually building complexity.",
                "error": str(e),
                "success": False
            }


# Global instance
enhanced_tutor_service = EnhancedAITutorService()
