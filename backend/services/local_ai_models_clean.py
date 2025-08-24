"""
Local AI Models Manager for Educational Content Generation.

Manages Ollama models: Llama 3 8B, Mistral 7B, and Qwen 3 8B.
Provides robust local inference with intelligent model selection.
"""

import subprocess
import logging
import asyncio
import json
import httpx
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class LocalAIManager:
    """Manages local Ollama AI models for educational content generation"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        
        # Only use these three specific models
        self.available_models = {
            "llama": "llama3:8b",        # Llama 3 8B
            "mistral": "mistral:7b",     # Mistral 7B  
            "qwen": "qwen3:8b"           # Qwen 3 8B
        }
        
        # Model specialization for different content types
        self.model_specialization = {
            "lesson": "llama",      # Llama excels at educational content
            "quiz": "mistral",      # Mistral good at structured questions
            "chat": "qwen",         # Qwen good at conversational responses
            "explanation": "llama", # Llama for detailed explanations
            "summary": "mistral",   # Mistral for concise summaries
            "general": "llama"      # Default to Llama
        }
        
    async def check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not accessible: {e}")
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get list of actually installed Ollama models"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    installed = [model["name"] for model in data.get("models", [])]
                    
                    # Filter to only our three target models
                    available = []
                    for key, model_name in self.available_models.items():
                        if any(model_name in inst for inst in installed):
                            available.append(key)
                    
                    logger.info(f"📋 Available Ollama models: {available}")
                    return available
                    
        except Exception as e:
            logger.warning(f"Failed to get Ollama models: {e}")
        
        return []
    
    async def generate_with_ollama(self, prompt: str, model: str = "llama", max_length: int = 512, temperature: float = 0.7) -> Optional[str]:
        """Generate content using specific Ollama model"""
        try:
            model_name = self.available_models.get(model, self.available_models["llama"])
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_length,
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            logger.info(f"🤖 Generating content with {model_name}")
            
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "").strip()
                    
                    if len(generated_text) > 20:
                        logger.info(f"✅ Successfully generated {len(generated_text)} chars with {model_name}")
                        return generated_text
                    else:
                        logger.warning(f"⚠️ Short response from {model_name}")
                        
        except Exception as e:
            logger.error(f"Ollama generation error with {model}: {e}")
        
        return None
    
    def generate_template_content(self, prompt: str, content_type: str) -> str:
        """Generate educational content using high-quality templates"""
        
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
        
        if content_type == "lesson":
            return f"""# Educational Lesson: {topic.title()}

## 📚 Introduction
Welcome to this comprehensive lesson on {topic}. This topic is fundamental for understanding key concepts and building practical skills in this subject area.

## 🎯 Learning Objectives
By the end of this lesson, you will be able to:
- Understand the core principles of {topic}
- Apply theoretical knowledge to practical situations
- Analyze real-world applications and examples
- Solve problems using {topic} concepts

## 🔑 Key Concepts

### 1. **Fundamental Principles**
The foundation of {topic} is built on essential principles that govern how this concept works in practice. Understanding these principles is crucial for mastering the subject.

### 2. **Practical Applications**
{topic.title()} has numerous real-world applications across various fields and industries. These applications demonstrate the importance and relevance of mastering this concept.

### 3. **Problem-Solving Strategies**
Effective approaches to solving problems involving {topic} include systematic analysis, step-by-step methodologies, and critical thinking skills.

## 💡 Examples and Case Studies

### Example 1: Basic Application
Here's how {topic} can be applied in a simple, everyday context to solve common problems and challenges.

### Example 2: Advanced Implementation  
More complex scenarios where {topic} principles are used to address sophisticated challenges and create innovative solutions.

## 🎓 Practice Exercises
1. **Basic Understanding**: Define key terms and explain fundamental concepts
2. **Application**: Apply {topic} principles to solve practice problems
3. **Analysis**: Evaluate different approaches and their effectiveness
4. **Synthesis**: Combine concepts to create comprehensive solutions

## 📝 Summary
{topic.title()} is an essential concept that provides valuable tools for understanding and solving problems in this field. Through systematic study and practice, you can develop proficiency and confidence in applying these principles.

## 🚀 Next Steps
Continue your learning journey by practicing with more complex examples, exploring advanced topics, and applying these concepts to real-world scenarios.
"""
        
        elif content_type == "quiz":
            return f"""# Quiz: {topic.title()}

## Question 1: Fundamental Understanding
**What is the most important principle underlying {topic}?**

A) Basic theoretical knowledge without practical application
B) Comprehensive understanding combining theory and practice
C) Memorization of facts and formulas only
D) Advanced techniques without foundational knowledge

**Correct Answer: B) Comprehensive understanding combining theory and practice**
**Explanation:** Effective mastery of {topic} requires both theoretical understanding and practical application skills.

## Question 2: Practical Application
**How would you best apply {topic} concepts in a real-world scenario?**

A) Use a systematic, step-by-step approach based on core principles
B) Rely solely on intuition and guesswork
C) Apply complex techniques without understanding basics
D) Avoid practical applications entirely

**Correct Answer: A) Use a systematic, step-by-step approach based on core principles**
**Explanation:** Systematic application of fundamental principles leads to more reliable and effective outcomes.

## Question 3: Problem-Solving Strategy
**When facing a challenging problem involving {topic}, what should be your first step?**

A) Immediately try advanced techniques
B) Skip the analysis and jump to solutions
C) Analyze the problem and identify relevant concepts
D) Avoid the problem if it seems difficult

**Correct Answer: C) Analyze the problem and identify relevant concepts**  
**Explanation:** Proper analysis and concept identification are essential first steps in effective problem-solving.

## Question 4: Learning Approach
**What is the best way to master {topic}?**

A) Memorize definitions without understanding
B) Practice regularly with increasing complexity
C) Study theory without any practical work
D) Focus only on advanced applications

**Correct Answer: B) Practice regularly with increasing complexity**
**Explanation:** Regular practice with progressively challenging problems builds strong understanding and skill.

## Question 5: Knowledge Application
**How can you demonstrate mastery of {topic}?**

A) Recite definitions perfectly
B) Solve complex problems and explain your reasoning
C) Use complicated terminology without understanding
D) Avoid challenging questions

**Correct Answer: B) Solve complex problems and explain your reasoning**
**Explanation:** True mastery is shown through problem-solving ability and clear explanation of reasoning processes.
"""
        
        elif content_type == "chat":
            return f"""I'm happy to help you learn about {topic}! 

{topic.title()} is an interesting and important subject. Here are some key points to get you started:

🔍 **What you should know:** Understanding {topic} involves grasping both the theoretical foundations and practical applications.

💡 **Why it matters:** This knowledge is valuable because it helps you solve real-world problems and think more systematically about complex challenges.

🎯 **How to approach it:** Start with the basics, practice regularly, and don't hesitate to ask questions when you need clarification.

What specific aspect of {topic} would you like to explore further? I'm here to guide your learning journey!"""

        else:
            return f"""## Understanding {topic.title()}

{topic.title()} is a valuable concept that combines theoretical knowledge with practical applications. Here's a comprehensive overview:

**Key Principles:**
- Foundation concepts that form the basis of understanding
- Systematic approaches to problem-solving
- Real-world applications and relevance

**Learning Approach:**
1. Start with fundamental concepts
2. Practice with examples and exercises  
3. Apply knowledge to solve practical problems
4. Reflect on learning and seek feedback

**Benefits of Mastering This Topic:**
- Enhanced problem-solving capabilities
- Better analytical thinking skills
- Practical tools for real-world challenges
- Foundation for advanced learning

This provides a solid starting point for your learning journey in {topic}!"""
    
    async def generate_content(self, prompt: str, content_type: str = "general", max_length: int = 512, temperature: float = 0.7, model_preference: str = None) -> str:
        """Generate educational content with intelligent model selection"""
        
        try:
            # Determine best model for content type
            if model_preference and model_preference in self.available_models:
                selected_model = model_preference
            else:
                selected_model = self.model_specialization.get(content_type, "llama")
            
            logger.info(f"🎯 Content type: {content_type}, Selected model: {selected_model}")
            
            # Check Ollama availability
            if await self.check_ollama_status():
                available_models = await self.get_available_models()
                
                # Try selected model first
                if selected_model in available_models:
                    result = await self.generate_with_ollama(prompt, selected_model, max_length, temperature)
                    if result:
                        return result
                
                # Try other available models as fallback
                for model in available_models:
                    if model != selected_model:
                        logger.info(f"🔄 Trying fallback model: {model}")
                        result = await self.generate_with_ollama(prompt, model, max_length, temperature)
                        if result:
                            return result
            
            # Final fallback to educational templates
            logger.info("📚 Using educational templates as final fallback")
            return self.generate_template_content(prompt, content_type)
            
        except Exception as e:
            logger.error(f"Error in generate_content: {e}")
            return self.generate_template_content(prompt, content_type)


# Global instance
local_ai_manager = LocalAIManager()
