"""
Dedicated Cross-Encoder Reranker using transformer models.

Research-backed reranking with specialized models:
- BGE-Reranker-Large (92-96% accuracy)
- Cohere Rerank 3 (API-based fallback)

Significantly faster and more accurate than LLM-based reranking.
"""

from typing import List, Dict, Any, Optional
import os


class BGECrossEncoderReranker:
    """
    Production cross-encoder reranker using BGE-Reranker.
    
    Uses sentence-transformers CrossEncoder for fast,
    accurate relevance scoring without LLM calls.
    """
    
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-large",
        max_length: int = 512,
        batch_size: int = 32,
    ):
        """
        Initialize cross-encoder reranker.
        
        Args:
            model_name: HuggingFace model name
            max_length: Max token length for encoding
            batch_size: Batch size for scoring
        """
        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size
        self._model = None
    
    def _load_model(self):
        """Lazy load the cross-encoder model."""
        if self._model is None:
            try:
                from sentence_transformers import CrossEncoder
                self._model = CrossEncoder(
                    self.model_name,
                    max_length=self.max_length,
                )
                print(f"✅ Loaded BGE cross-encoder: {self.model_name}")
            except ImportError:
                print("⚠️ sentence-transformers not installed, using fallback")
                self._model = "fallback"
    
    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents using cross-encoder scoring.
        
        Args:
            query: User query
            documents: Documents to rerank
            top_k: Number of top documents to return
            
        Returns:
            Reranked documents with cross-encoder scores
        """
        if not documents:
            return []
        
        self._load_model()
        
        if self._model == "fallback":
            # Use Cohere API or LLM fallback
            return await self._cohere_rerank(query, documents, top_k)
        
        # Prepare query-document pairs
        pairs = [
            (query, doc.get("text", "")[:self.max_length * 4])
            for doc in documents
        ]
        
        # Score all pairs
        scores = self._model.predict(pairs, batch_size=self.batch_size)
        
        # Add scores to documents
        scored_docs = []
        for doc, score in zip(documents, scores):
            doc_copy = doc.copy()
            doc_copy["cross_encoder_score"] = float(score)
            doc_copy["original_score"] = doc.get("score", 0)
            scored_docs.append(doc_copy)
        
        # Sort by cross-encoder score
        scored_docs.sort(key=lambda x: x["cross_encoder_score"], reverse=True)
        
        # Return top-k with updated scores
        result = scored_docs[:top_k]
        for i, doc in enumerate(result):
            doc["rerank_position"] = i + 1
            doc["score"] = doc["cross_encoder_score"]
        
        return result
    
    async def _cohere_rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int,
    ) -> List[Dict[str, Any]]:
        """
        Fallback to Cohere Rerank API.
        """
        cohere_api_key = os.getenv("COHERE_API_KEY")
        
        if not cohere_api_key:
            # Final fallback: return as-is
            return documents[:top_k]
        
        try:
            import cohere
            
            client = cohere.Client(cohere_api_key)
            
            # Prepare documents for Cohere
            doc_texts = [doc.get("text", "")[:4000] for doc in documents]
            
            response = client.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=doc_texts,
                top_n=top_k,
            )
            
            # Map results back
            result = []
            for ranking in response.results:
                doc = documents[ranking.index].copy()
                doc["cross_encoder_score"] = ranking.relevance_score
                doc["rerank_position"] = len(result) + 1
                doc["score"] = ranking.relevance_score
                result.append(doc)
            
            return result
            
        except Exception as e:
            print(f"Cohere rerank failed: {e}")
            return documents[:top_k]
    
    async def score_single(
        self,
        query: str,
        document: str,
    ) -> float:
        """
        Score a single query-document pair.
        
        Returns:
            Relevance score (higher = more relevant)
        """
        self._load_model()
        
        if self._model == "fallback":
            return 0.5
        
        score = self._model.predict([(query, document[:self.max_length * 4])])
        return float(score[0])


class HybridReranker:
    """
    Hybrid reranker combining multiple strategies.
    
    1. Initial retrieval scores
    2. Cross-encoder scores
    3. Optional diversity boost
    """
    
    def __init__(
        self,
        cross_encoder_weight: float = 0.7,
        retrieval_weight: float = 0.3,
    ):
        """
        Initialize hybrid reranker.
        
        Args:
            cross_encoder_weight: Weight for cross-encoder scores
            retrieval_weight: Weight for original retrieval scores
        """
        self.cross_encoder = BGECrossEncoderReranker()
        self.ce_weight = cross_encoder_weight
        self.ret_weight = retrieval_weight
    
    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Rerank with hybrid scoring.
        """
        if not documents:
            return []
        
        # Get cross-encoder reranked results
        reranked = await self.cross_encoder.rerank(
            query=query,
            documents=documents,
            top_k=len(documents),  # Rerank all, then take top-k
        )
        
        # Apply hybrid scoring
        for doc in reranked:
            ce_score = doc.get("cross_encoder_score", 0)
            ret_score = doc.get("original_score", 0)
            
            # Normalize scores to 0-1 range
            ce_norm = (ce_score + 10) / 20  # BGE scores are typically -10 to 10
            ce_norm = max(0, min(1, ce_norm))
            
            doc["hybrid_score"] = (
                self.ce_weight * ce_norm + 
                self.ret_weight * ret_score
            )
        
        # Sort by hybrid score
        reranked.sort(key=lambda x: x["hybrid_score"], reverse=True)
        
        return reranked[:top_k]


# Global reranker instances
bge_reranker = BGECrossEncoderReranker()
hybrid_reranker = HybridReranker()
