"""
FastAPI main application with WebSocket support.

Provides:
- WebSocket chat interface (ws://api/v1/chat)
- REST endpoints for management
- Health checks
- Prometheus metrics
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from .routers import chat_websocket, chat_rest, docs, health
from .websocket.connection_manager import ConnectionManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup/shutdown events."""
    # Startup
    print("🚀 Starting Multi-Agent RAG API...")
    
    # TODO: Initialize services (Qdrant, Redis, Neo4j clients)
    # TODO: Load agents
    # TODO: Initialize WebSocket connection manager
    
    yield
    
    # Shutdown
    print("🛑 Shutting down gracefully...")
    # TODO: Close connections


# Create FastAPI app
app = FastAPI(
    title="Multi-Agent RAG API",
    description="8-agent hierarchical RAG system with GraphRAG and WebSocket streaming",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_websocket.router, prefix="/api/v1", tags=["WebSocket Chat"])
app.include_router(chat_rest.router, prefix="/api/v1", tags=["Chat Management"])
app.include_router(docs.router, prefix="/api/v1", tags=["Documents"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Multi-Agent RAG API",
       "version": "0.1.0",
        "docs": "/docs",
        "websocket": "ws://localhost:8000/api/v1/chat"
    }
