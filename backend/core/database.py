"""
Database configuration and session management.

Provides SQLAlchemy engine, session management, and database
utilities for the AI Personal Tutor system.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import asyncio

from backend.core.config import settings


# Create SQLAlchemy engine for SQLite
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=settings.DATABASE_ECHO
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for Alembic migrations
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Create database session dependency.
    
    Yields a SQLAlchemy session that can be used for database operations.
    Automatically closes the session when done.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


async def create_tables():
    """Create all database tables."""
    # Import all models to ensure they're registered
    from backend.models import (
        user, student, learning_session, content, progress, user_analytics
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    drop_tables()
    asyncio.run(create_tables())
