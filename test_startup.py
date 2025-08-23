#!/usr/bin/env python3
"""
Simple startup test for the AI Tutor backend.
"""

print("🚀 AI-Powered Personal Tutor - Startup Test")
print("=" * 50)

# Test 1: Basic imports
try:
    import os
    import sys
    print("✅ Python standard library imports working")
except Exception as e:
    print(f"❌ Standard library import failed: {e}")
    sys.exit(1)

# Test 2: Check environment file
try:
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found, using defaults")
except Exception as e:
    print(f"❌ Environment check failed: {e}")

# Test 3: Pydantic imports
try:
    from pydantic import BaseModel
    from pydantic_settings import BaseSettings
    print("✅ Pydantic imports working")
except Exception as e:
    print(f"❌ Pydantic import failed: {e}")
    print("Please install: pip install pydantic pydantic-settings")

# Test 4: FastAPI imports
try:
    from fastapi import FastAPI
    print("✅ FastAPI imports working")
except Exception as e:
    print(f"❌ FastAPI import failed: {e}")
    print("Please install: pip install fastapi")

# Test 5: Configuration
try:
    from backend.core.config import Settings
    settings = Settings()
    print(f"✅ Configuration loaded: {settings.APP_NAME}")
except Exception as e:
    print(f"❌ Configuration failed: {e}")

# Test 6: Database configuration
try:
    from sqlalchemy import create_engine
    print("✅ SQLAlchemy imports working")
except Exception as e:
    print(f"❌ SQLAlchemy import failed: {e}")

print("\n🎯 Startup test completed!")
print("If all tests passed, you can start the server with:")
print("uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload")
