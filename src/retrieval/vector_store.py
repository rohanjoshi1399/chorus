"""
Qdrant vector store client.

Handles:
- Vector storage and retrieval
- Collection management
- Similarity search
- Metadata filtering
"""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams, PointStruct

from ..config import settings
from ..llm import bedrock_client


class VectorStore:
    """Qdrant vector database client."""
    
    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection
        self.embedding_dim = 1024  # Titan Embeddings V2 dimension
        
        # Create collection if it doesn't exist
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )
            print(f"✅ Created Qdrant collection: {self.collection_name}")
    
    async def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Add documents to vector store.
        
        Args:
            texts: Document texts to embed and store
            metadatas: Optional metadata for each document
            ids: Optional custom IDs for documents
            
        Returns:
            List of document IDs
        """
        # Generate embeddings
        embeddings = await bedrock_client.embed_documents(texts)
        
        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in texts]
        
        # Prepare metadata
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        # Create points
        points = []
        for idx, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
            payload = {
                "text": text,
                **metadata,
            }
            points.append(
                PointStruct(
                    id=ids[idx],
                    vector=embedding,
                    payload=payload,
                )
            )
        
        # Upload to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        
        return ids
    
    async def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of documents with scores
        """
        # Generate query embedding
        query_embedding = await bedrock_client.embed_text(query)
        
        # Build filter
        query_filter = None
        if filter_dict:
            conditions = [
                models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value),
                )
                for key, value in filter_dict.items()
            ]
            query_filter = models.Filter(must=conditions)
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter,
        )
        
        # Format results
        documents = []
        for result in results:
            documents.append({
                "id": result.id,
                "text": result.payload.get("text", ""),
                "score": result.score,
                "metadata": {
                    k: v for k, v in result.payload.items() if k != "text"
                },
            })
        
        return documents
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics."""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status,
        }


# Global vector store instance
vector_store = VectorStore()
