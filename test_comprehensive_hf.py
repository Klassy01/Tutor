#!/usr/bin/env python3
"""
Comprehensive Hugging Face API Test
Test different endpoints and model formats
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

HF_API_TOKEN = os.getenv('HUGGINGFACE_API_TOKEN', '')
print(f"Token: {HF_API_TOKEN[:15]}..." if HF_API_TOKEN else "No token found")

async def test_token_validity():
    """Test token with different endpoints"""
    print("🔍 Testing token validity with multiple endpoints...")
    
    endpoints = [
        ("https://huggingface.co/api/whoami", "User Info API"),
        ("https://api-inference.huggingface.co/", "Inference API Root"),
    ]
    
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    for url, desc in endpoints:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url, headers=headers)
                print(f"{desc}: {response.status_code} - {response.text[:100]}...")
        except Exception as e:
            print(f"{desc}: Error - {e}")

async def test_simple_models():
    """Test with very simple, definitely available models"""
    print("\n🧪 Testing with basic models...")
    
    # Try different model formats and simple models
    test_cases = [
        # Simple text classification (should work with any token)
        {
            "url": "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest",
            "payload": {"inputs": "I love this!"},
            "desc": "Sentiment Analysis"
        },
        # Text generation with very simple model
        {
            "url": "https://api-inference.huggingface.co/models/gpt2",
            "payload": {"inputs": "The weather today is", "parameters": {"max_new_tokens": 10}},
            "desc": "GPT-2 Generation"
        }
    ]
    
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    for test in test_cases:
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    test["url"],
                    headers=headers,
                    json=test["payload"]
                )
                print(f"{test['desc']}: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ SUCCESS! {test['desc']} works!")
                    result = response.json()
                    print(f"Response: {str(result)[:100]}...")
                elif response.status_code == 401:
                    print(f"❌ Authentication failed for {test['desc']}")
                else:
                    print(f"⚠️ {test['desc']} failed: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Error with {test['desc']}: {e}")
        
        await asyncio.sleep(1)

async def test_gated_models():
    """Test gated models with proper format"""
    print("\n🔐 Testing gated models...")
    
    gated_models = [
        "meta-llama/Llama-2-7b-chat-hf",
        "meta-llama/Meta-Llama-3-8B-Instruct",
        "meta-llama/Llama-3.1-8B",  # Exact model from approval email
        "meta-llama/Llama-3.1-8B-Instruct",  # Common variant
        "mistralai/Mistral-7B-Instruct-v0.1",
        "Qwen/Qwen2-7B-Instruct"
    ]
    
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    for model in gated_models:
        try:
            payload = {
                "inputs": "Hello, how are you?",
                "parameters": {"max_new_tokens": 20, "temperature": 0.7}
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json=payload
                )
                
                print(f"{model}: {response.status_code}")
                if response.status_code == 200:
                    print(f"✅ {model} accessible!")
                    result = response.json()
                    print(f"Response: {str(result)[:100]}...")
                elif response.status_code == 401:
                    print(f"❌ Authentication failed")
                elif response.status_code == 403:
                    print(f"⚠️ Access denied (need approval)")
                elif response.status_code == 404:
                    print(f"⚠️ Model not found")
                else:
                    print(f"⚠️ Error: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        await asyncio.sleep(1)

async def main():
    print("🚀 Comprehensive Hugging Face API Test\n")
    
    if not HF_API_TOKEN:
        print("❌ No token provided")
        return
    
    await test_token_validity()
    await test_simple_models()
    await test_gated_models()
    
    print("\n💡 Summary:")
    print("- If token is valid but models fail: Need Pro subscription or model approval")
    print("- If token is invalid: Check token permissions and expiration")
    print("- 404 errors: Model names might be incorrect or unavailable")

if __name__ == "__main__":
    asyncio.run(main())
