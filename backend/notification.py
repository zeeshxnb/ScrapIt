"""
Notification System for Email Tasks
Handles task completion notifications and updates
"""
import os
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, List, Set
from datetime import datetime
import json
import asyncio

from database import get_db
from models import User, Task
from auth import get_current_user, verify_jwt_token

router = APIRouter()

# Store active websocket connections
class ConnectionManager:
    def __init__(self):
        # Map of user_id -> set of websocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_notification(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            # Convert message to JSON string
            json_message = json.dumps(message)
            
            # Send to all connections for this user
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json_message)
                except Exception:
                    disconnected.add(connection)
            
            # Clean up any disconnected websockets
            for conn in disconnected:
                self.active_connections[user_id].discard(conn)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

manager = ConnectionManager()

async def notify_task_update(task: Task):
    """Send a notification about a task update"""
    if not task:
        return
        
    message = {
        "type": "task_update",
        "task_id": task.id,
        "status": task.status,
        "description": task.description,
        "progress": task.progress,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_notification(task.user_id, message)

async def notify_task_completion(task: Task):
    """Send a notification about a completed task"""
    if not task:
        return
        
    message = {
        "type": "task_completed",
        "task_id": task.id,
        "description": task.description,
        "result": task.result,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_notification(task.user_id, message)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """WebSocket endpoint for real-time notifications"""
    # Verify token
    user_id = verify_jwt_token(token)
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token")
        return
        
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return
    
    # Accept connection
    await manager.connect(websocket, user_id)
    
    try:
        # Send initial connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for any message (heartbeat or commands)
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                
                # Handle heartbeat
                if message.get("type") == "heartbeat":
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat_response",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
            except json.JSONDecodeError:
                pass
                
            # Sleep to prevent tight loop
            await asyncio.sleep(0.1)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)

@router.get("/tasks/{task_id}/notifications")
async def get_task_notifications(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for a specific task"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Return task status as a notification
    return {
        "notifications": [
            {
                "type": "task_status",
                "task_id": task.id,
                "status": task.status,
                "description": task.description,
                "progress": task.progress,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }

@router.post("/tasks/{task_id}/notify")
async def send_task_notification(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually send a notification for a task (for testing)"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == current_user.id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Send notification
    await notify_task_update(task)
    
    return {"message": "Notification sent"}

# Export router
notification_router = router
