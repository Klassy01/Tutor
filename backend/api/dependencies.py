"""
API dependencies for authentication and authorization.

Provides reusable dependency functions for FastAPI endpoints
to handle authentication, user retrieval, and permissions.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from backend.core.database import get_db
from backend.core.security import verify_token
from backend.models.user import User
from backend.models.student import Student

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user.
    
    Validates JWT token and returns the authenticated user object.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User object for authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is deactivated"
        )
    
    return user


async def get_current_student(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Student:
    """
    Get current authenticated student.
    
    Validates that the current user is a student and returns
    their student profile.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Student object for authenticated student
        
    Raises:
        HTTPException: If user is not a student or profile not found
    """
    if not current_user.is_student():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to students only"
        )
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return student


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Ensures the user account is active and verified.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is inactive or unverified
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current superuser.
    
    Validates that the current user has superuser privileges.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Superuser object
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser access required"
        )
    
    return current_user


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.
    
    For endpoints that work with or without authentication.
    
    Args:
        credentials: Optional HTTP Bearer token credentials
        db: Database session
        
    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_id = verify_token(token)
        
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            return None
        
        return user
    except Exception:
        return None


def require_permission(permission: str):
    """
    Dependency factory for permission-based access control.
    
    Args:
        permission: Required permission string
        
    Returns:
        Dependency function that checks permission
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        # Simple role-based permissions
        user_permissions = {
            "student": ["read_own_data", "update_own_profile", "submit_answers"],
            "teacher": ["read_student_data", "create_content", "view_analytics"],
            "admin": ["read_all_data", "manage_users", "system_admin"]
        }
        
        user_role_permissions = user_permissions.get(current_user.user_type, [])
        
        if permission not in user_role_permissions and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return current_user
    
    return permission_checker


async def validate_student_access(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Student:
    """
    Validate that current user can access specific student data.
    
    Students can only access their own data, teachers and admins
    can access student data based on their permissions.
    
    Args:
        student_id: ID of the student to access
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Student object if access is allowed
        
    Raises:
        HTTPException: If access is not allowed
    """
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Students can only access their own data
    if current_user.is_student():
        user_student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not user_student or user_student.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only access your own student data"
            )
    
    # Teachers and admins have broader access (implement specific logic as needed)
    elif current_user.is_teacher() or current_user.is_admin() or current_user.is_superuser:
        # In a real system, you might check class assignments, school permissions, etc.
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access student data"
        )
    
    return student


async def validate_content_access(
    content_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate that current user can access specific content.
    
    Args:
        content_id: ID of the content to access
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Content object if access is allowed
        
    Raises:
        HTTPException: If access is not allowed
    """
    from backend.models.content import Content
    
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if content is published and active
    if not content.is_published or not content.is_active:
        if not (current_user.is_teacher() or current_user.is_admin() or current_user.is_superuser):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Content is not available"
            )
    
    # Additional access control logic can be added here
    # For example, subscription-based access, prerequisite checks, etc.
    
    return content


class RateLimitChecker:
    """Rate limiting dependency for API endpoints."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts = {}
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        """
        Check rate limit for current user.
        
        Args:
            current_user: Current authenticated user
            
        Raises:
            HTTPException: If rate limit exceeded
        """
        import time
        
        now = time.time()
        user_id = current_user.id
        
        # Clean old entries
        if user_id in self.request_counts:
            self.request_counts[user_id] = [
                timestamp for timestamp in self.request_counts[user_id]
                if now - timestamp < self.window_seconds
            ]
        else:
            self.request_counts[user_id] = []
        
        # Check limit
        if len(self.request_counts[user_id]) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )
        
        # Add current request
        self.request_counts[user_id].append(now)
        
        return current_user


# Create rate limit instances for different endpoints
ai_tutor_rate_limit = RateLimitChecker(max_requests=50, window_seconds=3600)  # 50 requests per hour
general_rate_limit = RateLimitChecker(max_requests=200, window_seconds=3600)  # 200 requests per hour
