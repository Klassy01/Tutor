#!/usr/bin/env python3
"""
Test script to verify AI models service is working after fixes.
"""
import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append('/home/klassy/Downloads/Learning-Tutor')

from backend.services.ai_models import educational_ai_manager

async def test_ai_service():
    """Test the AI models service functionality."""
    print("🧪 Testing AI Models Service...")
    
    try:
        # Test initialization
        print("1. Testing initialization...")
        await educational_ai_manager.initialize()
        print("   ✅ Initialization successful")
        
        # Test warmup_models (compatibility method)
        print("2. Testing warmup_models...")
        await educational_ai_manager.warmup_models()
        print("   ✅ Warmup successful")
        
        # Test generate_content (compatibility method)
        print("3. Testing generate_content...")
        response = await educational_ai_manager.generate_content(
            "Explain what 2+2 equals", 
            content_type="chat"
        )
        print(f"   ✅ Content generation successful: {response[:100]}...")
        
        # Test generate_response
        print("4. Testing generate_response...")
        chat_response = await educational_ai_manager.generate_response(
            "What is mathematics?",
            context={"subject": "Mathematics"}
        )
        print(f"   ✅ Chat response successful: {chat_response[:100]}...")
        
        # Test lesson generation
        print("5. Testing lesson generation...")
        lesson = await educational_ai_manager.generate_lesson(
            "Mathematics",
            "Basic Arithmetic"
        )
        print(f"   ✅ Lesson generation successful: {lesson['title']}")
        
        # Test quiz generation
        print("6. Testing quiz generation...")
        quiz = await educational_ai_manager.generate_quiz(
            "Mathematics",
            "Addition",
            num_questions=2
        )
        print(f"   ✅ Quiz generation successful: {len(quiz)} questions")
        
        print("\n🎉 All AI service tests passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_ai_service())
    sys.exit(0 if success else 1)
