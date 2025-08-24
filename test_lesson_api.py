#!/usr/bin/env python3
"""
Test lesson generation with the fixed AI models
"""
import asyncio
import httpx
import json

async def test_lesson_generation():
    """Test lesson generation via the API"""
    
    # First login to get a token
    login_data = {
        "email": "david@example.com",
        "password": "password123"
    }
    
    async with httpx.AsyncClient(timeout=60) as client:
        # Login
        print("🔐 Logging in...")
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json=login_data
        )
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
            return
        
        token = login_response.json().get("access_token")
        print(f"✅ Login successful, got token")
        
        # Set auth headers
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test quiz generation (which was failing before)
        print("\n🧪 Testing quiz generation...")
        quiz_data = {
            "subject": "Python Programming",
            "topic": "Variables and Data Types",
            "num_questions": 3,
            "difficulty_level": "beginner"
        }
        
        quiz_response = await client.post(
            "http://localhost:8000/api/v1/quizzes/generate",
            headers=headers,
            json=quiz_data
        )
        
        print(f"Quiz Response Status: {quiz_response.status_code}")
        if quiz_response.status_code == 200:
            quiz_result = quiz_response.json()
            print(f"✅ Quiz generated successfully!")
            print(f"Questions: {len(quiz_result.get('questions', []))}")
            if quiz_result.get('questions'):
                print(f"First question: {quiz_result['questions'][0].get('question', '')[:100]}...")
        else:
            print(f"❌ Quiz generation failed: {quiz_response.text[:200]}...")
        
        # Test lesson generation
        print("\n📚 Testing lesson generation...")
        lesson_data = {
            "subject": "Python Programming", 
            "topic": "Functions and Methods",
            "difficulty_level": "intermediate"
        }
        
        lesson_response = await client.post(
            "http://localhost:8000/api/v1/lessons/generate",
            headers=headers,
            json=lesson_data
        )
        
        print(f"Lesson Response Status: {lesson_response.status_code}")
        if lesson_response.status_code == 200:
            lesson_result = lesson_response.json()
            print(f"✅ Lesson generated successfully!")
            print(f"Title: {lesson_result.get('title', 'N/A')}")
            content = lesson_result.get('content', '')
            print(f"Content length: {len(content)} characters")
            print(f"Content preview: {content[:150]}...")
        else:
            print(f"❌ Lesson generation failed: {lesson_response.text[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_lesson_generation())
