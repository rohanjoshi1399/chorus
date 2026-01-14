"""
WebSocket chat router for real-time streaming conversation.

Provides token-by-token streaming with agent progress updates.
"""

import json
import uuid
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any

from ...agents.supervisor_orchestrator import supervisor_orchestrator
from ...memory import conversation_memory

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        self.active_connections.pop(session_id, None)
    
    async def send_event(self, session_id: str, event: Dict[str, Any]):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(event)


manager = ConnectionManager()


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket endpoint for real-time chat.
    
    Protocol:
    Client -> Server: {"type": "chat.message", "session_id": "...", "message": "..."}
    Server -> Client: {"type": "agent.thinking", "agent": "query_analyzer", ...}
    Server -> Client: {"type": "retrieval.progress", "count": 5, ...}
    Server -> Client: {"type": "message.complete", "answer": "...", "sources": [...]}
    """
    session_id = str(uuid.uuid4())
    await manager.connect(websocket, session_id)
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection.established",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            if data.get("type") != "chat.message":
                await websocket.send_json({
                    "type": "error",
                    "message": "Unknown message type",
                })
                continue
            
            query = data.get("message", "")
            client_session = data.get("session_id", session_id)
            
            if not query:
                await websocket.send_json({
                    "type": "error",
                    "message": "Empty message",
                })
                continue
            
            # Store user message
            await conversation_memory.add_message(
                session_id=client_session,
                role="user",
                content=query,
            )
            
            # Get conversation history
            history = await conversation_memory.get_context_window(client_session)
            
            # Send thinking indicator
            await websocket.send_json({
                "type": "agent.thinking",
                "agent": "supervisor",
                "message": "Processing your query...",
            })
            
            try:
                # Process through orchestrator
                response = await supervisor_orchestrator.process_query(
                    query=query,
                    session_id=client_session,
                    conversation_history=history,
                )
                
                # Store assistant message
                await conversation_memory.add_message(
                    session_id=client_session,
                    role="assistant",
                    content=response["answer"],
                )
                
                # Send complete response
                await websocket.send_json({
                    "type": "message.complete",
                    "message_id": str(uuid.uuid4()),
                    "answer": response["answer"],
                    "sources": response["sources"],
                    "metadata": response["metadata"],
                    "timestamp": datetime.utcnow().isoformat(),
                })
                
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Error processing query: {str(e)}",
                })
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        manager.disconnect(session_id)
        print(f"WebSocket error: {e}")
