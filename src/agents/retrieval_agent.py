"""
Retrieval Agent (Level 3) - Vector search specialist.

Responsibilities:
- Execute vector similarity search on Qdrant
- Apply metadata filtering
- Implement hybrid search (dense + sparse BM25)
- Rerank results using cross-encoder
- Format retrieved chunks with metadata
"""

from typing import Any, Dict, List

from .base_agent import AgentInput, AgentOutput, BaseAgent


class RetrievalAgent(BaseAgent):
    """
    Level 3 specialist for vector database semantic search.
    
    Supports:
    - Vector-only search (default)
    - Hybrid search (vector + BM25)
    - Cross-encoder reranking
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="retrieval",
            description="Vector search specialist for semantic document retrieval",
            level=3,
            **kwargs
        )
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute retrieval pipeline:
        1. Hybrid search (vector + BM25) OR vector-only
        2. Apply metadata filters
        3. Rerank with cross-encoder
        4. Return top-k results
        
        Returns:
            Retrieved and ranked documents
        """
        from ..retrieval import vector_store, hybrid_retriever, reranker
        from ..config import settings
        
        query = input_data.query
        context = input_data.context
        
        # Get search parameters
        top_k = context.get("top_k", settings.retrieval_rerank_top_k)
        candidate_k = context.get("candidate_k", settings.retrieval_top_k)
        filter_dict = context.get("filter", None)
        use_hybrid = context.get("use_hybrid", True)
        use_reranking = context.get("use_reranking", True)
        strategies = context.get("strategies", ["vector"])
        
        retrieval_info = {"strategy": "vector"}
        
        try:
            # Step 1: Initial retrieval
            if use_hybrid and "vector" in strategies:
                # Hybrid search (vector + BM25)
                results = await hybrid_retriever.search(
                    query=query,
                    top_k=candidate_k,
                    filter_dict=filter_dict,
                )
                retrieval_info["strategy"] = "hybrid"
            else:
                # Vector-only search
                results = await vector_store.similarity_search(
                    query=query,
                    top_k=candidate_k,
                    filter_dict=filter_dict,
                )
            
            # Step 2: Filter by minimum similarity
            filtered_results = [
                result for result in results
                if result.get("score", 0) >= settings.retrieval_min_similarity
                or result.get("fused_score", 0) > 0
            ]
            
            # Step 3: Rerank with cross-encoder
            if use_reranking and len(filtered_results) > top_k:
                reranked_results = await reranker.rerank(
                    query=query,
                    documents=filtered_results,
                    top_k=top_k,
                )
                retrieval_info["reranked"] = True
            else:
                reranked_results = filtered_results[:top_k]
                retrieval_info["reranked"] = False
            
            # Step 4: Format documents
            retrieved_docs = []
            for result in reranked_results:
                retrieved_docs.append({
                    "id": result.get("id", ""),
                    "text": result.get("text", ""),
                    "score": result.get("fused_score", result.get("score", 0)),
                    "metadata": result.get("metadata", {}),
                    "source": result.get("source", "vector"),
                })
            
            # Calculate confidence
            if retrieved_docs:
                confidence = sum(doc["score"] for doc in retrieved_docs) / len(retrieved_docs)
            else:
                confidence = 0.0
            
        except Exception as e:
            retrieved_docs = []
            confidence = 0.0
            retrieval_info["error"] = str(e)
        
        return AgentOutput(
            result={
                "documents": retrieved_docs,
                "count": len(retrieved_docs),
                "average_score": confidence,
            },
            metadata={
                "agent": self.name,
                "retrieval_info": retrieval_info,
                "top_k": top_k,
                "candidates_evaluated": len(results) if 'results' in dir() else 0,
            },
            confidence_score=confidence
        )
