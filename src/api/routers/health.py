"""Health check and system status endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any

from ...retrieval import vector_store


router = APIRouter()


class HealthResponse(BaseModel):
    """Health response model."""
    status: str
    timestamp: str
    version: str


class DetailedHealthResponse(BaseModel):
    """Detailed health response model."""
    api: str
    qdrant: Dict[str, Any]
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for load balancer.
    
    Checks:
    - API is responsive
    - Returns 200 OK
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="0.1.0"
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse)
async def detailed_health():
    """Detailed system health including component status."""
    
    # Check Qdrant
    qdrant_status = {"status": "unknown"}
    try:
        info = vector_store.get_collection_info()
        qdrant_status = {
            "status": "healthy",
            "collection": info["name"],
            "documents": info["points_count"],
        }
    except Exception as e:
        qdrant_status = {
            "status": "unhealthy",
            "error": str(e),
        }
    
    return DetailedHealthResponse(
        api="healthy",
        qdrant=qdrant_status,
        timestamp=datetime.utcnow().isoformat(),
    )
