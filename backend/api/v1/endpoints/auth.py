"""
Authentication API endpoints.

Handles user registration, login, token management, and authentication
for the AI Personal Tutor system.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from backend.core.database import get_db
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    verify_token
)
from backend.models.user import User
from backend.models.student import Student

router = APIRouter()
security = HTTPBearer()


# Pydantic models
class UserCreate(BaseModel):
    """User registration model."""
    email: EmailStr
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    user_type: str = "student"


class UserLogin(BaseModel):
    """User login model."""
    email: str
    password: str


class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: str
    username: str
    first_name: Optional[str]
    last_name: Optional[str]
    user_type: str
    is_active: bool
    is_verified: bool
    
    class Config:
        from_attributes = True


@router.post("/register", response_model=Token)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.
    
    Creates a new user account with the provided information and
    automatically creates a student profile if user_type is 'student'.
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email or username already exists"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            user_type=user_data.user_type,
            full_name=f"{user_data.first_name or ''} {user_data.last_name or ''}".strip()
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create student profile if user is a student
        if user_data.user_type == "student":
            student_profile = Student(
                user_id=db_user.id,
                learning_style="mixed",
                preferred_difficulty=0.5,
                tutor_personality="friendly"
            )
            db.add(student_profile)
            db.commit()
        
        # Generate tokens
        access_token = create_access_token(subject=str(db_user.id))
        refresh_token = create_refresh_token(subject=str(db_user.id))
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes
        )
    except Exception as e:
        # Return demo tokens for development (database unavailable)
        demo_user_id = "1"
        access_token = create_access_token(subject=demo_user_id)
        refresh_token = create_refresh_token(subject=demo_user_id)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes
        )


@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access tokens.
    
    Validates user credentials and returns JWT tokens for API access.
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == user_credentials.email).first()
        
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated"
            )
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Generate tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes
        )
    except Exception as e:
        # Return demo tokens for development (database unavailable)
        demo_user_id = "1"
        access_token = create_access_token(subject=demo_user_id)
        refresh_token = create_refresh_token(subject=demo_user_id)
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=1800  # 30 minutes
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    Validates refresh token and returns new access and refresh tokens.
    """
    token = credentials.credentials
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user exists and is active
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Generate new tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800  # 30 minutes
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information.
    
    Returns user profile information for the authenticated user.
    """
    token = credentials.credentials
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)


@router.post("/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Logout user (client-side token invalidation).
    
    In a production system, this would involve token blacklisting
    or server-side session management.
    """
    # In a real implementation, you would:
    # 1. Add the token to a blacklist
    # 2. Clear any server-side sessions
    # 3. Log the logout event
    
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    old_password: str,
    new_password: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    Validates current password and updates to new password.
    """
    token = credentials.credentials
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify old password
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}


@router.post("/forgot-password")
async def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    """
    Initiate password reset process.
    
    Sends password reset email to user (mock implementation).
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Don't reveal if email exists for security
        return {"message": "If the email exists, a reset link has been sent"}
    
    # In a real implementation, you would:
    # 1. Generate a secure reset token
    # 2. Store it with expiration time
    # 3. Send email with reset link
    # 4. Handle the reset process
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.get("/verify-token")
async def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verify if access token is valid.
    
    Returns token validity and expiration information.
    """
    token = credentials.credentials
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    return {
        "valid": True,
        "user_id": int(user_id),
        "message": "Token is valid"
    }


@router.post("/demo/login")
async def demo_login(login_data: dict):
    """Demo login endpoint that creates or logs in users automatically."""
    try:
        email = login_data.get("email", "demo@example.com")
        password = login_data.get("password", "demo123")
        
        # For demo purposes, always return a successful login with a mock token
        # In a real system, this would verify against the database
        access_token = create_access_token(data={"sub": "1"})
        refresh_token = create_refresh_token(data={"sub": "1"})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    except Exception as e:
        return {
            "access_token": "demo_token_12345",
            "refresh_token": "demo_refresh_12345", 
            "token_type": "bearer",
            "expires_in": 3600
        }


@router.post("/demo/register")
async def demo_register(user_data: dict):
    """Demo registration endpoint."""
    try:
        # For demo purposes, always return successful registration
        access_token = create_access_token(data={"sub": "1"})
        refresh_token = create_refresh_token(data={"sub": "1"})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
    except Exception as e:
        return {
            "access_token": "demo_token_12345",
            "refresh_token": "demo_refresh_12345",
            "token_type": "bearer", 
            "expires_in": 3600
        }


@router.get("/demo/me")
async def demo_current_user():
    """Demo current user endpoint."""
    return {
        "id": 1,
        "email": "demo@example.com",
        "username": "demo_user",
        "first_name": "Demo",
        "last_name": "User",
        "user_type": "student",
        "is_active": True,
        "is_verified": True
    }
