"""
AI Tutor Chat Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import logging
from datetime import datetime

from backend.api.dependencies import get_current_user, get_db
from backend.services.advanced_ai_generator import advanced_ai_generator
from backend.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory chat sessions (in production, use Redis or database)
chat_sessions = {}


@router.post("/start-session")
async def start_chat_session(
    session_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Start a new AI tutor chat session."""
    try:
        session_id = f"chat_{current_user.id}_{int(datetime.utcnow().timestamp())}"
        subject = session_data.get("subject", "General")
        learning_goal = session_data.get("learning_goal", "")
        
        # Initialize chat session
        chat_sessions[session_id] = {
            "user_id": current_user.id,
            "subject": subject,
            "learning_goal": learning_goal,
            "messages": [],
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        
        # Generate welcome message
        welcome_prompt = f"""You are an AI tutor specializing in {subject}. A student has just started a session with the learning goal: "{learning_goal}". 
        Welcome them warmly and ask how you can help them learn today. Be encouraging and professional."""
        
        welcome_response = await advanced_ai_generator.generate_chat_response(
            welcome_prompt,
            conversation_history=[],
            subject=subject
        )
        
        if welcome_response:
            welcome_message = {
                "role": "assistant",
                "content": welcome_response,
                "timestamp": datetime.utcnow().isoformat()
            }
            chat_sessions[session_id]["messages"].append(welcome_message)
        
        logger.info(f"Started chat session {session_id} for user {current_user.id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "welcome_message": welcome_response or f"Hello! I'm your AI tutor for {subject}. How can I help you learn today?",
            "subject": subject,
            "learning_goal": learning_goal
        }
        
    except Exception as e:
        logger.error(f"Error starting chat session for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start chat session"
        )


@router.post("/send-message")
async def send_message(
    message_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Send a message to the AI tutor and get response."""
    try:
        session_id = message_data.get("session_id")
        user_message = message_data.get("message", "").strip()
        
        if not session_id or session_id not in chat_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        session = chat_sessions[session_id]
        
        # Verify session belongs to user
        if session["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this chat session"
            )
        
        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Add user message to session
        user_msg = {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.utcnow().isoformat()
        }
        session["messages"].append(user_msg)
        session["last_activity"] = datetime.utcnow()
        
        # Generate AI response
        conversation_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in session["messages"][-10:]  # Last 10 messages for context
        ]
        
        ai_response = await advanced_ai_generator.generate_chat_response(
            user_message,
            conversation_history=conversation_history,
            subject=session["subject"]
        )
        
        if not ai_response:
            ai_response = "I apologize, but I'm having trouble processing your question right now. Could you please rephrase it or ask something else?"
        
        # Add AI response to session
        ai_msg = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        session["messages"].append(ai_msg)
        
        logger.info(f"Processed message in session {session_id} for user {current_user.id}")
        
        return {
            "success": True,
            "response": ai_response,
            "session_id": session_id,
            "message_count": len(session["messages"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )

@router.get("/session/{session_id}/history")
async def get_chat_history(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get chat history for a session."""
    try:
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        session = chat_sessions[session_id]
        
        # Verify session belongs to user
        if session["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this chat session"
            )
        
        return {
            "success": True,
            "session_id": session_id,
            "subject": session["subject"],
            "learning_goal": session["learning_goal"],
            "messages": session["messages"],
            "created_at": session["created_at"].isoformat(),
            "last_activity": session["last_activity"].isoformat(),
            "message_count": len(session["messages"])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching chat history for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat history"
        )

@router.get("/sessions")
async def get_user_chat_sessions(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get all chat sessions for the user."""
    try:
        user_sessions = []
        
        for session_id, session in chat_sessions.items():
            if session["user_id"] == current_user.id:
                # Get last message for preview
                last_message = session["messages"][-1] if session["messages"] else None
                
                user_sessions.append({
                    "session_id": session_id,
                    "subject": session["subject"],
                    "learning_goal": session["learning_goal"],
                    "created_at": session["created_at"].isoformat(),
                    "last_activity": session["last_activity"].isoformat(),
                    "message_count": len(session["messages"]),
                    "last_message_preview": last_message["content"][:100] + "..." if last_message and len(last_message["content"]) > 100 else (last_message["content"] if last_message else "")
                })
        
        # Sort by last activity (most recent first)
        user_sessions.sort(key=lambda x: x["last_activity"], reverse=True)
        
        return {
            "success": True,
            "sessions": user_sessions,
            "total_sessions": len(user_sessions)
        }
        
    except Exception as e:
        logger.error(f"Error fetching chat sessions for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chat sessions"
        )

@router.delete("/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a chat session."""
    try:
        if session_id not in chat_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        session = chat_sessions[session_id]
        
        # Verify session belongs to user
        if session["user_id"] != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this chat session"
            )
        
        del chat_sessions[session_id]
        logger.info(f"Deleted chat session {session_id} for user {current_user.id}")
        
        return {
            "success": True,
            "message": "Chat session deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )

@router.post("/ask-quick")
async def ask_quick_question(
    question_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Ask a quick question without starting a full session."""
    try:
        question = question_data.get("question", "").strip()
        subject = question_data.get("subject", "General")
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        # Generate response for quick question
        response = await advanced_ai_generator.generate_chat_response(
            question,
            conversation_history=[],
            subject=subject
        )
        
        if not response:
            response = "I apologize, but I'm having trouble answering your question right now. Please try rephrasing it or ask a different question."
        
        logger.info(f"Answered quick question for user {current_user.id}")
        
        return {
            "success": True,
            "question": question,
            "response": response,
            "subject": subject
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering quick question for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to answer question"
        )

@router.post("/explain-concept")
async def explain_concept(
    explanation_request: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed explanation of a concept."""
    try:
        concept = explanation_request.get("concept", "").strip()
        subject = explanation_request.get("subject", "General")
        level = explanation_request.get("level", "intermediate")
        
        if not concept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Concept to explain cannot be empty"
            )
        
        # Create detailed explanation prompt
        explanation_prompt = f"""Explain the concept "{concept}" in {subject} for a {level} level student. 
        Provide a clear, comprehensive explanation with:
        1. Definition and key points
        2. Real-world examples or applications
        3. Common misconceptions to avoid
        4. Related concepts they should know
        Make it educational but engaging."""
        
        explanation = await advanced_ai_generator.generate_chat_response(
            explanation_prompt,
            conversation_history=[],
            subject=subject
        )
        
        if not explanation:
            explanation = f"I'd be happy to explain {concept}, but I'm having trouble generating a detailed explanation right now. Could you ask me to explain a specific aspect of {concept}?"
        
        return {
            "success": True,
            "concept": concept,
            "subject": subject,
            "level": level,
            "explanation": explanation
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining concept for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to explain concept"
        )
