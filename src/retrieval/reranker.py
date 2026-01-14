"""
Cross-encoder reranking for improved retrieval precision.

Uses a cross-encoder model to rerank initial retrieval results
for higher accuracy.
"""

from typing import List, Dict, Any
from ..llm import bedrock_client


class CrossEncoderReranker:
    """
    Reranker using LLM-based relevance scoring.
    
    For MVP, uses Claude to score relevance. In production,
    could use specialized cross-encoder models like ms-marco-MiniLM.
    """
    
    def __init__(self, top_k: int = 5):
        """
        Initialize reranker.
        
        Args:
            top_k: Number of documents to return after reranking
        """
        self.top_k = top_k
    
    async def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = None,
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents using LLM-based relevance scoring.
        
        Args:
            query: Original search query
            documents: List of documents to rerank
            top_k: Number of results to return (default: self.top_k)
            
        Returns:
            Reranked documents with relevance scores
        """
        if not documents:
            return []
        
        if top_k is None:
            top_k = self.top_k
        
        # For small result sets, skip expensive reranking
        if len(documents) <= top_k:
            return documents
        
        # Build reranking prompt
        docs_text = "\n\n".join([
            f"[Document {i+1}]\n{doc.get('text', '')[:300]}"
            for i, doc in enumerate(documents[:10])  # Limit to top 10 for reranking
        ])
        
        rerank_prompt = f"""Given the user query, rank these documents by relevance.

Query: "{query}"

Documents:
{docs_text}

Return a JSON array of document numbers (1-{min(len(documents), 10)}) ordered by relevance, most relevant first.
Example: [3, 1, 5, 2, 4]

Return ONLY the JSON array, no other text."""

        try:
            result = await bedrock_client.generate(
                prompt=rerank_prompt,
                system_prompt="You are a relevance ranking expert. Return only a JSON array of numbers.",
                temperature=0.0,
            )
            
            # Parse ranking
            import json
            ranking = json.loads(result.strip())
            
            # Reorder documents based on ranking
            reranked = []
            for rank_idx in ranking[:top_k]:
                if 1 <= rank_idx <= len(documents):
                    doc = documents[rank_idx - 1].copy()
                    doc["rerank_position"] = len(reranked) + 1
                    reranked.append(doc)
            
            # Fill remaining spots if ranking was incomplete
            seen_ids = {doc.get("id") for doc in reranked}
            for doc in documents:
                if len(reranked) >= top_k:
                    break
                if doc.get("id") not in seen_ids:
                    reranked.append(doc)
            
            return reranked
            
        except Exception as e:
            # Fallback: return original order
            return documents[:top_k]
    
    async def score_relevance(
        self,
        query: str,
        document: str,
    ) -> float:
        """
        Score single document relevance (0-1).
        
        Args:
            query: User query
            document: Document text
            
        Returns:
            Relevance score between 0 and 1
        """
        score_prompt = f"""Rate the relevance of this document to the query on a scale of 0.0 to 1.0.

Query: "{query}"

Document:
{document[:500]}

Return ONLY a number between 0.0 and 1.0, nothing else."""

        try:
            result = await bedrock_client.generate(
                prompt=score_prompt,
                system_prompt="You are a relevance scoring expert. Return only a decimal number.",
                temperature=0.0,
            )
            
            score = float(result.strip())
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5  # Default neutral score


# Global reranker instance
reranker = CrossEncoderReranker()
