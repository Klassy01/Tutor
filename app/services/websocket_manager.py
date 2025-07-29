"""
WebSocket connection manager for real-time communication.

Manages WebSocket connections for the AI tutoring chat interface,
handling connection lifecycle, message routing, and real-time updates.
"""

from typing import Dict, List
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket connection manager for real-time AI tutoring.
    
    Handles multiple concurrent student connections, message broadcasting,
    and connection lifecycle management for the tutoring chat interface.
    """
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[int, WebSocket] = {}
        self.student_sessions: Dict[int, Dict] = {}
    
    async def connect(self, websocket: WebSocket, student_id: int):
        """
        Accept a new WebSocket connection for a student.
        
        Args:
            websocket: The WebSocket connection
            student_id: ID of the connecting student
        """
        await websocket.accept()
        self.active_connections[student_id] = websocket
        self.student_sessions[student_id] = {
            "connected_at": asyncio.get_event_loop().time(),
            "message_count": 0,
            "last_activity": asyncio.get_event_loop().time()
        }
        
        logger.info(f"Student {student_id} connected to tutor chat")
        
        # Send welcome message
        await self.send_personal_message(
            json.dumps({
                "type": "system",
                "content": "Welcome to your AI tutor! How can I help you learn today?",
                "timestamp": asyncio.get_event_loop().time()
            }),
            student_id
        )
    
    def disconnect(self, student_id: int):
        """
        Remove a student's WebSocket connection.
        
        Args:
            student_id: ID of the disconnecting student
        """
        if student_id in self.active_connections:
            del self.active_connections[student_id]
        
        if student_id in self.student_sessions:
            session_data = self.student_sessions[student_id]
            session_duration = asyncio.get_event_loop().time() - session_data["connected_at"]
            logger.info(
                f"Student {student_id} disconnected after {session_duration:.2f}s, "
                f"{session_data['message_count']} messages"
            )
            del self.student_sessions[student_id]
    
    async def send_personal_message(self, message: str, student_id: int):
        """
        Send a message to a specific student.
        
        Args:
            message: JSON string message to send
            student_id: ID of the target student
        """
        if student_id in self.active_connections:
            try:
                await self.active_connections[student_id].send_text(message)
                
                # Update session data
                if student_id in self.student_sessions:
                    self.student_sessions[student_id]["last_activity"] = asyncio.get_event_loop().time()
                    self.student_sessions[student_id]["message_count"] += 1
                
            except Exception as e:
                logger.error(f"Error sending message to student {student_id}: {e}")
                # Remove dead connection
                self.disconnect(student_id)
    
    async def broadcast_message(self, message: str):
        """
        Broadcast a message to all connected students.
        
        Args:
            message: JSON string message to broadcast
        """
        disconnected_students = []
        
        for student_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to student {student_id}: {e}")
                disconnected_students.append(student_id)
        
        # Clean up disconnected connections
        for student_id in disconnected_students:
            self.disconnect(student_id)
    
    async def send_typing_indicator(self, student_id: int, is_typing: bool = True):
        """
        Send typing indicator to a student.
        
        Args:
            student_id: ID of the target student
            is_typing: Whether the AI tutor is typing
        """
        message = json.dumps({
            "type": "typing_indicator",
            "is_typing": is_typing,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        await self.send_personal_message(message, student_id)
    
    async def send_system_notification(self, student_id: int, notification_type: str, content: str):
        """
        Send a system notification to a student.
        
        Args:
            student_id: ID of the target student
            notification_type: Type of notification (info, warning, success, error)
            content: Notification content
        """
        message = json.dumps({
            "type": "system_notification",
            "notification_type": notification_type,
            "content": content,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        await self.send_personal_message(message, student_id)
    
    async def send_progress_update(self, student_id: int, progress_data: Dict):
        """
        Send a progress update to a student.
        
        Args:
            student_id: ID of the target student
            progress_data: Progress information to send
        """
        message = json.dumps({
            "type": "progress_update",
            "data": progress_data,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        await self.send_personal_message(message, student_id)
    
    def get_connected_students(self) -> List[int]:
        """
        Get list of currently connected student IDs.
        
        Returns:
            List of connected student IDs
        """
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """
        Get the total number of active connections.
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)
    
    def get_student_session_info(self, student_id: int) -> Dict:
        """
        Get session information for a specific student.
        
        Args:
            student_id: ID of the student
            
        Returns:
            Session information dictionary
        """
        if student_id not in self.student_sessions:
            return {}
        
        session = self.student_sessions[student_id]
        current_time = asyncio.get_event_loop().time()
        
        return {
            "student_id": student_id,
            "connected_at": session["connected_at"],
            "session_duration": current_time - session["connected_at"],
            "message_count": session["message_count"],
            "last_activity": session["last_activity"],
            "idle_time": current_time - session["last_activity"],
            "is_active": (current_time - session["last_activity"]) < 300  # 5 minutes
        }
    
    async def cleanup_inactive_connections(self, timeout_seconds: int = 1800):
        """
        Clean up connections that have been inactive for too long.
        
        Args:
            timeout_seconds: Timeout in seconds (default 30 minutes)
        """
        current_time = asyncio.get_event_loop().time()
        inactive_students = []
        
        for student_id, session in self.student_sessions.items():
            if current_time - session["last_activity"] > timeout_seconds:
                inactive_students.append(student_id)
        
        for student_id in inactive_students:
            if student_id in self.active_connections:
                try:
                    await self.send_system_notification(
                        student_id,
                        "info",
                        "Session timed out due to inactivity. Please reconnect to continue."
                    )
                    await self.active_connections[student_id].close()
                except Exception:
                    pass  # Connection might already be closed
                
                self.disconnect(student_id)
        
        if inactive_students:
            logger.info(f"Cleaned up {len(inactive_students)} inactive connections")
    
    async def health_check(self):
        """
        Perform health check on all connections.
        
        Sends ping messages to verify connections are still alive.
        """
        disconnected_students = []
        
        for student_id, websocket in self.active_connections.items():
            try:
                # Send a ping message
                await websocket.ping()
            except Exception as e:
                logger.warning(f"Health check failed for student {student_id}: {e}")
                disconnected_students.append(student_id)
        
        # Clean up failed connections
        for student_id in disconnected_students:
            self.disconnect(student_id)
        
        return {
            "total_connections": len(self.active_connections),
            "healthy_connections": len(self.active_connections),
            "failed_connections": len(disconnected_students)
        }
