"""
Configuration management using Pydantic Settings.

Loads configuration from environment variables and .env file.
"""

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # AWS Bedrock
    aws_region: str = "us-east-1"
    aws_access_key_id: str
    aws_secret_access_key: str
    bedrock_model: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    bedrock_embedding_model: str = "amazon.titan-embed-text-v2:0"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    
    # Qdrant Vector Database
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection: str = "documents"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    
    # Neo4j (Phase 4)
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_key: str = "dev-api-key-change-in-production"
    
    # WebSocket
    ws_max_connections: int = 1000
    ws_ping_interval: int = 30
    ws_message_queue_size: int = 100
    
    # Memory
    memory_buffer_size: int = 10
    memory_compression_threshold: int = 20
    
    # Retrieval
    retrieval_top_k: int = 50
    retrieval_rerank_top_k: int = 5
    retrieval_min_similarity: float = 0.7
    
    # GraphRAG (Phase 4)
    graphrag_enabled: bool = False
    graph_max_hop_depth: int = 3
    
    # Web Search (Phase 4)
    web_search_enabled: bool = False
    serpapi_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    
    # LangSmith Tracing
    langchain_tracing_v2: bool = False
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: Optional[str] = None
    langchain_project: str = "multi-agent-rag"
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Environment
    environment: str = "development"


# Global settings instance
settings = Settings()
