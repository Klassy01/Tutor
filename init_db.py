#!/usr/bin/env python3
"""
Database initialization script for AI-Powered Personal Tutor.

This script creates all necessary database tables and initializes
the system with default data.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.core.config import settings
from backend.core.database import Base
from backend.models.user import User
from backend.models.student import Student
from backend.models.content import Content, ContentCategory
from backend.models.learning_session import LearningSession, SessionInteraction
from backend.models.progress import Progress, Achievement
from backend.core.security import get_password_hash

# Import all models to ensure they're registered
from backend.models import *

def create_database_tables():
    """Create all database tables."""
    print("Creating database tables...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        try:
            # Check if we need to seed initial data
            existing_categories = session.query(ContentCategory).count()
            if existing_categories == 0:
                print("Seeding initial data...")
                seed_initial_data(session)
                
        except Exception as e:
            print(f"⚠️  Error seeding data: {e}")
            session.rollback()
        finally:
            session.close()
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False
    
    return True

def seed_initial_data(session):
    """Seed the database with initial data."""
    
    # Create default content categories
    categories = [
        {"name": "Mathematics", "description": "Mathematical concepts and problem solving"},
        {"name": "Science", "description": "Scientific principles and applications"},
        {"name": "Language Arts", "description": "Reading, writing, and communication skills"},
        {"name": "History", "description": "Historical events and cultural studies"},
        {"name": "Programming", "description": "Computer programming and software development"},
        {"name": "Art", "description": "Creative arts and design principles"},
    ]
    
    for cat_data in categories:
        category = ContentCategory(
            name=cat_data["name"],
            description=cat_data["description"]
        )
        session.add(category)
    
    # Create sample content
    sample_contents = [
        {
            "title": "Introduction to Algebra",
            "description": "Basic algebraic concepts and linear equations",
            "content_type": "lesson",
            "difficulty_level": 0.3,
            "category": "Mathematics"
        },
        {
            "title": "Python Basics",
            "description": "Introduction to Python programming language",
            "content_type": "tutorial",
            "difficulty_level": 0.2,
            "category": "Programming"
        },
        {
            "title": "World War II Overview",
            "description": "Major events and impact of World War II",
            "content_type": "lesson",
            "difficulty_level": 0.4,
            "category": "History"
        }
    ]
    
    # We'll add content after categories are committed
    session.commit()
    
    # Now add content with proper category references
    math_category = session.query(ContentCategory).filter_by(name="Mathematics").first()
    programming_category = session.query(ContentCategory).filter_by(name="Programming").first()
    history_category = session.query(ContentCategory).filter_by(name="History").first()
    
    contents = [
        Content(
            title="Introduction to Algebra",
            description="Basic algebraic concepts and linear equations",
            content="# Introduction to Algebra\n\nAlgebra is a branch of mathematics dealing with symbols and the rules for manipulating those symbols...",
            content_type="lesson",
            difficulty_level=0.3,
            category_id=math_category.id if math_category else None,
            estimated_duration=30,
            is_published=True
        ),
        Content(
            title="Python Basics",
            description="Introduction to Python programming language",
            content="# Python Programming Basics\n\nPython is a high-level programming language known for its simplicity...",
            content_type="tutorial",
            difficulty_level=0.2,
            category_id=programming_category.id if programming_category else None,
            estimated_duration=45,
            is_published=True
        ),
        Content(
            title="World War II Overview",
            description="Major events and impact of World War II",
            content="# World War II: A Historical Overview\n\nWorld War II was a global conflict that lasted from 1939 to 1945...",
            content_type="lesson",
            difficulty_level=0.4,
            category_id=history_category.id if history_category else None,
            estimated_duration=25,
            is_published=True
        )
    ]
    
    for content in contents:
        session.add(content)
    
    # Create a demo admin user
    admin_user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        first_name="System",
        last_name="Administrator",
        full_name="System Administrator",
        user_type="admin",
        is_active=True,
        is_verified=True,
        is_superuser=True
    )
    session.add(admin_user)
    
    # Create a demo student user
    demo_student = User(
        email="student@example.com",
        username="student",
        hashed_password=get_password_hash("student123"),
        first_name="Demo",
        last_name="Student",
        full_name="Demo Student",
        user_type="student",
        is_active=True,
        is_verified=True
    )
    session.add(demo_student)
    
    session.commit()
    
    # Create student profile for demo student
    student_profile = Student(
        user_id=demo_student.id,
        learning_style="visual",
        preferred_difficulty=0.4,
        tutor_personality="encouraging"
    )
    session.add(student_profile)
    
    session.commit()
    print("✅ Initial data seeded successfully!")

def main():
    """Main initialization function."""
    print("🚀 Initializing AI-Powered Personal Tutor Database...")
    print(f"Database URL: {settings.DATABASE_URL}")
    
    if create_database_tables():
        print("🎉 Database initialization completed successfully!")
        print("\nDemo Accounts Created:")
        print("👨‍💻 Admin: admin@example.com / admin123")
        print("🎓 Student: student@example.com / student123")
        return True
    else:
        print("❌ Database initialization failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
