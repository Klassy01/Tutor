#!/usr/bin/env python3
"""
Test the new Hugging Face access for Llama-3.1-8B
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_llama_access():
    """Test access to the approved Llama-3.1-8B model"""
    
    token = os.getenv('HUGGINGFACE_API_TOKEN', '')
    print(f"🔑 Using token: {token[:15]}..." if token else "❌ No token found")
    
    if not token:
        print("\n⚠️ Please set HUGGINGFACE_API_TOKEN in .env file")
        return
    
    # Test the exact model from your approval email
    models_to_test = [
        "meta-llama/Llama-3.1-8B",
        "meta-llama/Llama-3.1-8B-Instruct", 
        "meta-llama/Meta-Llama-3-8B-Instruct"
    ]
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    for model in models_to_test:
        print(f"\n🧪 Testing {model}...")
        
        payload = {
            "inputs": "Explain photosynthesis in simple terms:",
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7,
                "return_full_text": False
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{model}",
                    headers=headers,
                    json=payload
                )
                
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ SUCCESS! Access granted and working!")
                    print(f"Response: {result}")
                    return True
                elif response.status_code == 401:
                    print("❌ Token invalid or expired")
                elif response.status_code == 403:
                    print("⚠️ Access denied (may need to wait or request approval)")
                elif response.status_code == 404:
                    print("⚠️ Model not found or incorrect name")
                else:
                    print(f"⚠️ Error: {response.text}")
                    
        except Exception as e:
            print(f"❌ Connection error: {e}")
        
        await asyncio.sleep(2)  # Rate limiting
    
    return False

async def main():
    print("🚀 Testing New Hugging Face Access\n")
    
    success = await test_llama_access()
    
    if success:
        print("\n🎉 Ready to use Hugging Face API!")
        print("The backend will now use Llama-3.1-8B for content generation.")
    else:
        print("\n💡 Next steps:")
        print("1. Generate a fresh token at: https://huggingface.co/settings/tokens")
        print("2. Make sure it has 'Read' permissions")
        print("3. Update .env file with: HUGGINGFACE_API_TOKEN=your_new_token")
        print("4. The system will fallback to local models if needed")

if __name__ == "__main__":
    asyncio.run(main())
