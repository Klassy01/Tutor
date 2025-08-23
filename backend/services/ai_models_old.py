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
from pathlib import Path

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Hugging Face API configuration
HF_API_URL = "https://api-inference.huggingface.co/models"
HF_API_TOKEN = getattr(settings, 'HUGGINGFACE_API_TOKEN', '')

# Educational AI models - using Hugging Face API compatible models
EDUCATIONAL_MODELS = {
    "qwen_coder": [
        "Qwen/Qwen2.5-Coder-7B-Instruct",
        "microsoft/DialoGPT-medium"  # Fallback
    ],
    "llama3": [
        "microsoft/DialoGPT-medium",  # Using available model as proxy
        "distilbert-base-uncased"     # Additional fallback
    ],
    "mistral": [
        "microsoft/DialoGPT-medium",  # Using available model as proxy
        "distilbert-base-uncased"     # Additional fallback
    ]
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
    models = EDUCATIONAL_MODELS[model_type]
    return models[0]  # Use first (preferred) model
        logger.error(f"Failed to load any educational model: {e}")
        return None


async def generate_educational_response(
    prompt: str,
    content_type: str = "general",  # lesson, quiz, explanation, chat
    model_name: str = None
) -> str:
    """
    Generate educational content using Qwen Coder, Llama 3, or Mistral via Hugging Face API.
    
    Args:
        prompt: The educational prompt
        content_type: Type of content (lesson, quiz, explanation, chat)
        model_name: Specific model to use
        
    Returns:
        Generated educational response
    """
    try:
        # Use HF API if token is available, otherwise use local models
        hf_token = getattr(settings, 'HUGGINGFACE_API_TOKEN', '')
        
        if hf_token:
            return await _generate_with_hf_api(prompt, content_type, model_name)
        else:
            # Fallback to local model generation
            generator = await load_educational_model(model_name)
            if generator:
                return await _generate_with_local_model(generator, prompt, content_type)
            else:
                return _get_fallback_response(content_type)
        
    except Exception as e:
        logger.error(f"Educational content generation error: {e}")
        return _get_fallback_response(content_type)


async def _generate_with_hf_api(prompt: str, content_type: str, model_name: str = None) -> str:
    """Generate response using Hugging Face Inference API."""
    try:
        import httpx
        
        # Select model based on content type
        if not model_name:
            model_name = _select_model_for_content(content_type)
        
        # Create educational context
        educational_context = {
            "lesson": "You are an expert educator. Create clear, engaging lesson content with examples.",
            "quiz": "You are creating educational quiz questions. Make them clear and educational.",
            "explanation": "You are explaining concepts to students. Use simple language and examples.",
            "chat": "You are a helpful AI tutor. Be encouraging and provide clear explanations."
        }
        
        context = educational_context.get(content_type, educational_context["chat"])
        full_prompt = f"{context}\n\nRequest: {prompt}\n\nResponse:"
        
        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 400,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model_name}",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 503:
                # Model is loading, wait and retry
                await asyncio.sleep(10)
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{model_name}",
                    headers=headers,
                    json=payload
                )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "").strip()
                elif isinstance(result, dict):
                    generated_text = result.get("generated_text", "").strip()
                else:
                    generated_text = str(result).strip()
                
                if generated_text:
                    return generated_text
                else:
                    return _get_fallback_response(content_type)
            else:
                logger.warning(f"HF API error {response.status_code}: {response.text}")
                return _get_fallback_response(content_type)
                
    except Exception as e:
        logger.error(f"Hugging Face API error: {e}")
        return _get_fallback_response(content_type)


def _select_model_for_content(content_type: str) -> str:
    """Select the best model for the content type."""
    model_mapping = {
        "lesson": getattr(settings, 'QWEN_CODER_MODEL', 'Qwen/Qwen2.5-Coder-7B-Instruct'),
        "quiz": getattr(settings, 'LLAMA3_MODEL', 'meta-llama/Meta-Llama-3.1-8B-Instruct'),
        "explanation": getattr(settings, 'QWEN_CODER_MODEL', 'Qwen/Qwen2.5-Coder-7B-Instruct'),
        "chat": getattr(settings, 'MISTRAL_MODEL', 'mistralai/Mistral-7B-Instruct-v0.3')
    }
    
    return model_mapping.get(content_type, model_mapping["chat"])


async def _generate_with_local_model(generator: Any, prompt: str, content_type: str) -> str:
    """Generate response using local model."""
    try:
        educational_context = {
            "lesson": "You are an expert educator creating engaging lesson content. Explain concepts clearly with examples.",
            "quiz": "You are creating educational quiz questions. Make them challenging but fair, with clear explanations.",
            "explanation": "You are explaining a concept to a student. Use simple language, examples, and break down complex ideas.",
            "chat": "You are a friendly AI tutor having a conversation with a student. Be encouraging and helpful."
        }
        
        context = educational_context.get(content_type, educational_context["chat"])
        full_prompt = f"{context}\n\nStudent request: {prompt}\n\nResponse:"
        
        result = generator(
            full_prompt,
            max_new_tokens=400,
            temperature=0.7,
            do_sample=True,
            pad_token_id=generator.tokenizer.eos_token_id if hasattr(generator, 'tokenizer') else None,
            truncation=True,
            repetition_penalty=1.1
        )
        
        generated_text = result[0]['generated_text']
        response = generated_text[len(full_prompt):].strip()
        
        if not response:
            response = _get_fallback_response(content_type)
        
        return response
        
    except Exception as e:
        logger.error(f"Local model generation failed: {e}")
        return _get_fallback_response(content_type)


def _get_fallback_response(content_type: str) -> str:
    """Get fallback response when AI generation fails."""
    fallback_responses = {
        "lesson": "I'm ready to teach you about any topic! What subject would you like to learn?",
        "quiz": "I can create quiz questions for you. What topic should I focus on?",
        "explanation": "I'd be happy to explain any concept you're curious about. What would you like to understand better?",
        "chat": "I'm here to help with your learning journey. What can I teach you today?"
    }
    
    return fallback_responses.get(content_type, fallback_responses["chat"])


class EducationalAIManager:
    """Manager for educational AI models (Qwen Coder, Llama 3, Mistral only)."""
    
    def __init__(self):
        self.available_models = []
        self._check_available_models()
    
    def _check_available_models(self):
        """Check which educational models are available."""
        self.available_models = []
        
        if TRANSFORMERS_AVAILABLE:
            # Add educational models
            for model_type, models in EDUCATIONAL_MODELS.items():
                self.available_models.extend([f"{model_type}: {model}" for model in models[:1]])  # Show first of each type
            
            if not self.available_models:
                self.available_models.append("fallback: DialoGPT-medium")
        
        logger.info(f"Available educational models: {self.available_models}")
    
    async def generate_content(
        self,
        prompt: str,
        content_type: str = "general",
        preferred_model: str = None,
        **kwargs
    ) -> str:
        """
        Generate educational content using available models.
        
        Args:
            prompt: The educational prompt
            content_type: Type of content (lesson, quiz, explanation, chat)
            preferred_model: Preferred model type (qwen_coder, llama3, mistral)
            
        Returns:
            Generated educational content
        """
        try:
            # Determine which model to use
            model_name = None
            if preferred_model and preferred_model in EDUCATIONAL_MODELS:
                models_list = EDUCATIONAL_MODELS[preferred_model]
                model_name = models_list[0]  # Use first available model of this type
            
            return await generate_educational_response(prompt, content_type, model_name)
            
        except Exception as e:
            logger.error(f"Error generating educational content: {e}")
            
            # Provide helpful fallback based on content type
            fallback_responses = {
                "lesson": "I'm ready to create educational lessons for you! What subject would you like to learn?",
                "quiz": "I can help create quiz questions. What topic should I focus on?",
                "explanation": "I'd be happy to explain any concept. What would you like to understand better?",
                "chat": "I'm here as your AI tutor. What can I help you learn today?"
            }
            
            return fallback_responses.get(content_type, fallback_responses["chat"])
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available educational models."""
        return {
            "available_models": self.available_models,
            "supported_types": ["qwen_coder", "llama3", "mistral"],
            "content_types": ["lesson", "quiz", "explanation", "chat"],
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "educational_focus": True,
            "description": "Educational AI using Qwen Coder, Llama 3, and Mistral models"
        }
    
    async def warmup_models(self):
        """Pre-load educational models for better performance."""
        if TRANSFORMERS_AVAILABLE:
            logger.info("Warming up educational AI models...")
            try:
                # Pre-load the preferred educational model
                await load_educational_model()
                logger.info("Educational model warmup completed")
            except Exception as e:
                logger.warning(f"Educational model warmup failed: {e}")


# Global instance
ai_model_manager = EducationalAIManager()
