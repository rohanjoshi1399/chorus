"""
Hybrid search combining vector similarity with BM25 sparse retrieval.

Provides:
- Dense vector search (semantic)
- Sparse BM25 search (lexical)
- Score fusion with configurable weights
"""

from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi
import re

from ..config import settings
from ..llm import bedrock_client
from .vector_store import vector_store


class HybridRetriever:
    """
    Hybrid retriever combining dense vector search with sparse BM25.
    
    Uses Reciprocal Rank Fusion (RRF) to combine results.
    """
    
    def __init__(self, vector_weight: float = 0.7, bm25_weight: float = 0.3):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_weight: Weight for vector search results (0-1)
            bm25_weight: Weight for BM25 results (0-1)
        """
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.bm25_index = None
        self.corpus = []
        self.doc_ids = []
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25."""
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens
    
    async def build_bm25_index(self, documents: List[Dict[str, Any]]) -> None:
        """
        Build BM25 index from documents.
        
        Args:
            documents: List of documents with 'id' and 'text' fields
        """
        self.corpus = []
        self.doc_ids = []
        
        for doc in documents:
            self.corpus.append(self._tokenize(doc.get("text", "")))
            self.doc_ids.append(doc.get("id", ""))
        
        if self.corpus:
            self.bm25_index = BM25Okapi(self.corpus)
    
    def _bm25_search(self, query: str, top_k: int = 50) -> List[Dict[str, Any]]:
        """
        Perform BM25 search.
        
        Args:
            query: Search query
            top_k: Number of results
            
        Returns:
            List of documents with BM25 scores
        """
        if self.bm25_index is None:
            return []
        
        query_tokens = self._tokenize(query)
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "id": self.doc_ids[idx],
                    "score": float(scores[idx]),
                    "source": "bm25",
                })
        
        return results
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]],
        k: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        Combine results using Reciprocal Rank Fusion.
        
        RRF Score = sum(1 / (k + rank)) for each result list
        
        Args:
            vector_results: Vector search results
            bm25_results: BM25 search results
            k: RRF constant (default 60)
            
        Returns:
            Fused and re-ranked results
        """
        fused_scores = {}
        doc_data = {}
        
        # Add vector results
        for rank, doc in enumerate(vector_results):
            doc_id = doc["id"]
            rrf_score = self.vector_weight * (1 / (k + rank + 1))
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + rrf_score
            doc_data[doc_id] = doc
        
        # Add BM25 results
        for rank, doc in enumerate(bm25_results):
            doc_id = doc["id"]
            rrf_score = self.bm25_weight * (1 / (k + rank + 1))
            fused_scores[doc_id] = fused_scores.get(doc_id, 0) + rrf_score
            if doc_id not in doc_data:
                doc_data[doc_id] = doc
        
        # Sort by fused score
        sorted_ids = sorted(fused_scores.keys(), key=lambda x: fused_scores[x], reverse=True)
        
        results = []
        for doc_id in sorted_ids:
            doc = doc_data[doc_id].copy()
            doc["fused_score"] = fused_scores[doc_id]
            results.append(doc)
        
        return results
    
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search.
        
        Args:
            query: Search query
            top_k: Number of final results
            filter_dict: Optional metadata filters
            
        Returns:
            Hybrid search results
        """
        # Get more candidates for fusion
        candidate_k = min(top_k * 5, 50)
        
        # Vector search
        vector_results = await vector_store.similarity_search(
            query=query,
            top_k=candidate_k,
            filter_dict=filter_dict,
        )
        
        # BM25 search (if index exists)
        bm25_results = self._bm25_search(query, top_k=candidate_k)
        
        # Fuse results
        if bm25_results:
            fused_results = self._reciprocal_rank_fusion(vector_results, bm25_results)
        else:
            fused_results = vector_results
        
        return fused_results[:top_k]


# Global hybrid retriever instance
hybrid_retriever = HybridRetriever()
