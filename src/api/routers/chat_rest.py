"""REST endpoints for chat history and management."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from ...services import orchestrator


router = APIRouter()


# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model."""
    query: str
    session_id: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    answer: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat query through the RAG system.
    
    Flow: Query Analyzer → Retrieval → Synthesis
    """
    try:
        response = await orchestrator.process_query(
            query=request.query,
            session_id=request.session_id,
            conversation_history=request.conversation_history or [],
        )
        return ChatResponse(**response)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )
