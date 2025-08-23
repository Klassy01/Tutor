"""
AI Models Service for handling different AI providers.

Supports OpenAI, Google Gemini, and Hugging Face models with local model support.
Prioritizes local models to avoid API key requirements.
"""

from typing import Optional, Dict, Any, List
import asyncio
import httpx
import json
import logging
import os
from pathlib import Path

# Import with error handling
try:
    from transformers import (
        pipeline, 
        AutoTokenizer, 
        AutoModelForCausalLM,
        AutoModelForSequenceClassification,
        BloomForCausalLM,
        BloomTokenizerFast,
        GPT2LMHeadModel,
        GPT2Tokenizer,
        DistilBertTokenizer,
        DistilBertForSequenceClassification
    )
    import torch
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Transformers not fully available: {e}")
    TRANSFORMERS_AVAILABLE = False

from backend.core.config import settings

logger = logging.getLogger(__name__)

# Global model cache
_model_cache = {}
_embedding_model = None

# Default models that work well for educational content
DEFAULT_MODELS = {
    "conversational": [
        "microsoft/DialoGPT-medium",
        "microsoft/DialoGPT-small", 
        "distilgpt2",
        "gpt2"
    ],
    "text_generation": [
        "distilgpt2",
        "gpt2",
        "microsoft/DialoGPT-small"
    ],
    "classification": [
        "distilbert-base-uncased",
        "cardiffnlp/twitter-roberta-base-sentiment-latest"
    ],
    "embeddings": [
        "sentence-transformers/all-MiniLM-L6-v2",
        "sentence-transformers/paraphrase-MiniLM-L6-v2"
    ]
}


def get_cache_dir() -> str:
    """Get or create cache directory for models."""
    cache_dir = getattr(settings, 'HF_HOME', './models/huggingface_cache')
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    return cache_dir


async def load_local_model(model_name: str, task: str = "text-generation") -> Optional[Any]:
    """
    Load a Hugging Face model locally with fallback options.
    
    Args:
        model_name: Name of the model to load
        task: Task type (text-generation, conversational, etc.)
        
    Returns:
        Loaded model pipeline or None if failed
    """
    if not TRANSFORMERS_AVAILABLE:
        logger.warning("Transformers library not available")
        return None
    
    try:
        # Check cache first
        cache_key = f"{model_name}_{task}"
        if cache_key in _model_cache:
            return _model_cache[cache_key]
        
        logger.info(f"Loading local model: {model_name} for task: {task}")
        
        # Set cache directory
        cache_dir = get_cache_dir()
        os.environ['TRANSFORMERS_CACHE'] = cache_dir
        
        # Configure model loading parameters
        device = "cuda" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        
        # Try to load the model with various configurations
        try:
            # Primary attempt with full configuration
            model_pipeline = pipeline(
                task,
                model=model_name,
                tokenizer=model_name,
                torch_dtype=torch_dtype,
                device_map="auto" if torch.cuda.is_available() else None,
                cache_dir=cache_dir,
                trust_remote_code=True
            )
        except Exception as e1:
            logger.warning(f"Primary load failed: {e1}, trying simplified load...")
            # Simplified fallback
            try:
                model_pipeline = pipeline(
                    task,
                    model=model_name,
                    device=0 if torch.cuda.is_available() else -1,
                    cache_dir=cache_dir
                )
            except Exception as e2:
                logger.warning(f"Simplified load failed: {e2}, trying minimal config...")
                # Minimal configuration fallback
                model_pipeline = pipeline(task, model=model_name)
        
        # Cache the loaded model
        _model_cache[cache_key] = model_pipeline
        logger.info(f"✅ Successfully loaded model: {model_name}")
        return model_pipeline
        
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        
        # Try fallback models for the same task
        fallback_models = DEFAULT_MODELS.get(task, [])
        for fallback_model in fallback_models:
            if fallback_model != model_name:
                try:
                    logger.info(f"Trying fallback model: {fallback_model}")
                    return await load_local_model(fallback_model, task)
                except Exception as fallback_error:
                    logger.warning(f"Fallback {fallback_model} also failed: {fallback_error}")
                    continue
        
        return None


async def get_huggingface_response(
    prompt: str,
    model: str = None,
    max_tokens: int = None,
    temperature: float = None
) -> str:
    """
    Get response from Hugging Face model (local preferred, API fallback).
    """
    try:
        model_name = model or settings.HUGGINGFACE_MODEL
        max_length = max_tokens or settings.MAX_TOKENS
        temp = temperature or settings.TEMPERATURE
        
        # Try local model first
        generator = await load_local_model(model_name, "text-generation")
        
        if generator:
            try:
                # Generate response using local model
                result = generator(
                    prompt,
                    max_new_tokens=max_length,
                    temperature=temp,
                    do_sample=True,
                    pad_token_id=generator.tokenizer.eos_token_id,
                    truncation=True
                )
                
                # Extract generated text
                generated_text = result[0]['generated_text']
                response = generated_text[len(prompt):].strip()
                
                # Clean up response
                if not response:
                    response = "I understand your question. Let me help you with that topic."
                
                return response
                
            except Exception as local_error:
                logger.warning(f"Local model generation failed: {local_error}")
        
        # Fallback to API if available
        if settings.HUGGINGFACE_API_TOKEN:
            return await _get_huggingface_api_response(prompt, model_name, max_length, temp)
        
        # Final fallback response
        return "I'm ready to help you learn! Please ask me about any topic you'd like to explore."
        
    except Exception as e:
        logger.error(f"Hugging Face response error: {e}")
        return "I'm here to help with your learning journey. What would you like to study today?"


async def get_openai_response(
    prompt: str,
    model: str = None,
    max_tokens: int = None,
    temperature: float = None
) -> str:
    """
    Get response from OpenAI API.
    """
    try:
        if not settings.OPENAI_API_KEY:
            return "OpenAI API key not configured. Please add your API key to use OpenAI models."
        
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        
        response = await openai.ChatCompletion.acreate(
            model=model or settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens or settings.MAX_TOKENS,
            temperature=temperature or settings.TEMPERATURE,
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return f"OpenAI service temporarily unavailable. Error: {str(e)}"


async def get_gemini_response(
    prompt: str,
    model: str = None,
    max_tokens: int = None,
    temperature: float = None
) -> str:
    """
    Get response from Google Gemini API.
    """
    try:
        if not settings.GEMINI_API_KEY:
            return "Gemini API key not configured. Please add your API key to use Gemini models."
        
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        model_instance = genai.GenerativeModel(model or settings.GEMINI_MODEL)
        
        generation_config = {
            "temperature": temperature or settings.TEMPERATURE,
            "max_output_tokens": max_tokens or settings.MAX_TOKENS,
        }
        
        response = model_instance.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return f"Gemini service temporarily unavailable. Error: {str(e)}"


async def _get_huggingface_api_response(
    prompt: str,
    model: str,
    max_tokens: int,
    temperature: float
) -> str:
    """Get response from Hugging Face Inference API."""
    try:
        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                else:
                    return str(result)
            else:
                logger.error(f"Hugging Face API error: {response.status_code}")
                return "API temporarily unavailable"
                
    except Exception as e:
        logger.error(f"Hugging Face API error: {e}")
        return "Service temporarily unavailable"


async def get_embeddings(texts: List[str]) -> Optional[List[List[float]]]:
    """Get embeddings for texts using sentence transformers."""
    global _embedding_model
    
    try:
        if not TRANSFORMERS_AVAILABLE:
            return None
        
        if _embedding_model is None:
            model_name = getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            cache_dir = get_cache_dir()
            
            logger.info(f"Loading embedding model: {model_name}")
            _embedding_model = SentenceTransformer(model_name, cache_folder=cache_dir)
        
        embeddings = _embedding_model.encode(texts)
        return embeddings.tolist()
        
    except Exception as e:
        logger.error(f"Embedding generation error: {e}")
        return None


class AIModelManager:
    """Enhanced manager for AI models with local model priority."""
    
    def __init__(self):
        self.available_providers = []
        self._check_available_providers()
    
    def _check_available_providers(self):
        """Check which AI providers are available."""
        self.available_providers = []
        
        # Always add huggingface if transformers is available (no API key needed)
        if TRANSFORMERS_AVAILABLE:
            self.available_providers.append("huggingface")
        
        if settings.OPENAI_API_KEY:
            self.available_providers.append("openai")
        
        if settings.GEMINI_API_KEY:
            self.available_providers.append("gemini")
        
        logger.info(f"Available AI providers: {self.available_providers}")
    
    async def get_response(
        self,
        prompt: str,
        provider: str = None,
        model: str = None,
        **kwargs
    ) -> str:
        """
        Get AI response using the specified or best available provider.
        """
        # Use specified provider or fall back to configured default
        target_provider = provider or settings.AI_PROVIDER
        
        if target_provider not in self.available_providers:
            # Fall back to first available provider
            if self.available_providers:
                target_provider = self.available_providers[0]
                logger.warning(f"Requested provider {provider} not available, using {target_provider}")
            else:
                return "No AI providers are configured or available. Please check your configuration."
        
        try:
            if target_provider == "huggingface":
                return await get_huggingface_response(prompt, model, **kwargs)
            elif target_provider == "openai":
                return await get_openai_response(prompt, model, **kwargs)
            elif target_provider == "gemini":
                return await get_gemini_response(prompt, model, **kwargs)
            else:
                return f"Unsupported AI provider: {target_provider}"
                
        except Exception as e:
            logger.error(f"Error with provider {target_provider}: {e}")
            
            # Try fallback providers
            for fallback_provider in self.available_providers:
                if fallback_provider != target_provider:
                    try:
                        logger.info(f"Trying fallback provider: {fallback_provider}")
                        if fallback_provider == "huggingface":
                            return await get_huggingface_response(prompt, model, **kwargs)
                        elif fallback_provider == "openai":
                            return await get_openai_response(prompt, model, **kwargs)
                        elif fallback_provider == "gemini":
                            return await get_gemini_response(prompt, model, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback provider {fallback_provider} also failed: {fallback_error}")
                        continue
            
            return "I'm having trouble with my AI systems right now. Please try again in a moment."
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about available providers."""
        return {
            "available_providers": self.available_providers,
            "current_provider": settings.AI_PROVIDER,
            "models": {
                "openai": settings.OPENAI_MODEL,
                "gemini": settings.GEMINI_MODEL,
                "huggingface": settings.HUGGINGFACE_MODEL,
            },
            "transformers_available": TRANSFORMERS_AVAILABLE,
            "local_models_supported": TRANSFORMERS_AVAILABLE
        }
    
    async def warmup_models(self):
        """Pre-load commonly used models for better performance."""
        if TRANSFORMERS_AVAILABLE:
            logger.info("Warming up AI models...")
            try:
                # Pre-load the default model
                await load_local_model(settings.HUGGINGFACE_MODEL, "text-generation")
                
                # Pre-load embedding model
                await get_embeddings(["test"])
                
                logger.info("Model warmup completed")
            except Exception as e:
                logger.warning(f"Model warmup failed: {e}")


# Global instance
ai_model_manager = AIModelManager()
