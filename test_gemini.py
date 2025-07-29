#!/usr/bin/env python3
"""
Test script for Gemini API integration.
Run this to verify that your Gemini API key is working correctly.
"""
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai

async def test_gemini_integration():
    """Test the Gemini API integration."""
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        print("Please add your Gemini API key to the .env file")
        print("Get your API key from: https://aistudio.google.com/app/apikey")
        return False
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("🧪 Testing Gemini API connection...")
        
        # Test prompt
        test_prompt = """You are an expert AI tutor. 
        
Please respond to this student question: "Can you help me understand what photosynthesis is?"

Please provide a helpful, educational response that is appropriate for a high school student.
"""
        
        # Generate response
        response = await model.generate_content_async(
            test_prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=150,
                temperature=0.7,
            )
        )
        
        print("✅ Gemini API connection successful!")
        print("\n📝 Sample AI Tutor Response:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Gemini API: {e}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. API quota exceeded")
        print("3. Network connectivity issues")
        print("4. Service temporarily unavailable")
        return False

if __name__ == "__main__":
    print("🚀 AI Personal Tutor - Gemini Integration Test")
    print("=" * 50)
    
    success = asyncio.run(test_gemini_integration())
    
    if success:
        print("\n🎉 Gemini integration is working correctly!")
        print("You can now use the AI Personal Tutor with Gemini Flash API.")
    else:
        print("\n🔧 Please fix the issues above and try again.")
