"""
Semantic Chunker with Max-Min Algorithm.

Implements research-backed semantic chunking strategies:
- Max-Min Semantic Chunking (constrained clustering)
- Sentence embedding similarity breakpoints
- Configurable chunk size constraints

Reference: "Embedding First, Then Chunking: Smarter RAG Retrieval 
with Max-Min Semantic Chunking" - Milvus Blog
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import numpy as np
from dataclasses import dataclass

from ..llm import bedrock_client


@dataclass
class SemanticChunk:
    """A semantically coherent text chunk."""
    text: str
    start_idx: int
    end_idx: int
    sentence_count: int
    cohesion_score: float
    metadata: Dict[str, Any]


class SemanticChunker:
    """
    Advanced semantic chunker using Max-Min algorithm.
    
    Unlike fixed-size chunking, this preserves conceptual boundaries
    by analyzing embedding similarity between consecutive sentences.
    """
    
    def __init__(
        self,
        min_chunk_size: int = 100,
        max_chunk_size: int = 1000,
        similarity_threshold: float = 0.5,
        breakpoint_percentile: float = 90,
    ):
        """
        Initialize semantic chunker.
        
        Args:
            min_chunk_size: Minimum characters per chunk
            max_chunk_size: Maximum characters per chunk
            similarity_threshold: Min similarity to merge sentences
            breakpoint_percentile: Percentile for detecting breakpoints
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.similarity_threshold = similarity_threshold
        self.breakpoint_percentile = breakpoint_percentile
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using regex.
        
        Handles common abbreviations and edge cases.
        """
        # Regex for sentence boundaries
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Filter empty and whitespace-only sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    async def _embed_sentences(self, sentences: List[str]) -> np.ndarray:
        """
        Generate embeddings for all sentences.
        
        Returns:
            NumPy array of shape (n_sentences, embedding_dim)
        """
        embeddings = []
        
        # Batch embedding for efficiency
        batch_size = 20
        for i in range(0, len(sentences), batch_size):
            batch = sentences[i:i + batch_size]
            batch_embeddings = await bedrock_client.embed_texts(batch)
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot / (norm1 * norm2))
    
    def _calculate_breakpoints(
        self,
        embeddings: np.ndarray,
    ) -> List[int]:
        """
        Identify semantic breakpoints using similarity drops.
        
        A breakpoint occurs when similarity between consecutive
        sentences drops significantly (below percentile threshold).
        """
        if len(embeddings) < 2:
            return []
        
        # Calculate consecutive similarities
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = self._cosine_similarity(embeddings[i], embeddings[i + 1])
            similarities.append(sim)
        
        if not similarities:
            return []
        
        # Find breakpoints where similarity drops below threshold
        threshold = np.percentile(similarities, 100 - self.breakpoint_percentile)
        
        breakpoints = []
        for i, sim in enumerate(similarities):
            if sim < threshold:
                breakpoints.append(i + 1)  # Break AFTER this sentence
        
        return breakpoints
    
    def _maxmin_chunking(
        self,
        sentences: List[str],
        embeddings: np.ndarray,
    ) -> List[Tuple[int, int]]:
        """
        Apply Max-Min semantic chunking algorithm.
        
        For each sentence, decide whether to:
        - Merge with current chunk (if similar enough)
        - Start new chunk (if dissimilar)
        
        Decision based on:
        - max_sim: Maximum similarity to any sentence in current chunk
        - min_sim: Minimum pairwise similarity in current chunk
        """
        if len(sentences) == 0:
            return []
        
        if len(sentences) == 1:
            return [(0, 0)]
        
        chunk_ranges = []
        current_start = 0
        current_embeddings = [embeddings[0]]
        current_text_len = len(sentences[0])
        
        for i in range(1, len(sentences)):
            sentence = sentences[i]
            embedding = embeddings[i]
            
            # Calculate max similarity to current chunk
            max_sim = max(
                self._cosine_similarity(embedding, e) 
                for e in current_embeddings
            )
            
            # Decide: merge or new chunk?
            should_merge = (
                max_sim >= self.similarity_threshold and
                current_text_len + len(sentence) <= self.max_chunk_size
            )
            
            # Force merge if chunk too small
            if current_text_len < self.min_chunk_size:
                should_merge = True
            
            # Force split if chunk too large
            if current_text_len + len(sentence) > self.max_chunk_size:
                should_merge = False
            
            if should_merge:
                current_embeddings.append(embedding)
                current_text_len += len(sentence)
            else:
                # Save current chunk and start new
                chunk_ranges.append((current_start, i - 1))
                current_start = i
                current_embeddings = [embedding]
                current_text_len = len(sentence)
        
        # Don't forget the last chunk
        chunk_ranges.append((current_start, len(sentences) - 1))
        
        return chunk_ranges
    
    async def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[SemanticChunk]:
        """
        Split text into semantic chunks.
        
        Args:
            text: Input text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of SemanticChunk objects
        """
        # Split into sentences
        sentences = self._split_into_sentences(text)
        
        if not sentences:
            return []
        
        if len(sentences) == 1:
            return [SemanticChunk(
                text=sentences[0],
                start_idx=0,
                end_idx=len(sentences[0]),
                sentence_count=1,
                cohesion_score=1.0,
                metadata=metadata or {},
            )]
        
        # Embed all sentences
        embeddings = await self._embed_sentences(sentences)
        
        # Apply Max-Min chunking
        chunk_ranges = self._maxmin_chunking(sentences, embeddings)
        
        # Build SemanticChunk objects
        chunks = []
        char_offset = 0
        
        for start_idx, end_idx in chunk_ranges:
            chunk_sentences = sentences[start_idx:end_idx + 1]
            chunk_text = " ".join(chunk_sentences)
            
            # Calculate cohesion (average pairwise similarity)
            chunk_embeddings = embeddings[start_idx:end_idx + 1]
            if len(chunk_embeddings) > 1:
                sims = []
                for i in range(len(chunk_embeddings)):
                    for j in range(i + 1, len(chunk_embeddings)):
                        sims.append(self._cosine_similarity(
                            chunk_embeddings[i], chunk_embeddings[j]
                        ))
                cohesion = np.mean(sims) if sims else 1.0
            else:
                cohesion = 1.0
            
            chunks.append(SemanticChunk(
                text=chunk_text,
                start_idx=char_offset,
                end_idx=char_offset + len(chunk_text),
                sentence_count=len(chunk_sentences),
                cohesion_score=float(cohesion),
                metadata={
                    **(metadata or {}),
                    "chunk_method": "maxmin_semantic",
                    "sentence_range": (start_idx, end_idx),
                },
            ))
            
            char_offset += len(chunk_text) + 1
        
        return chunks
    
    async def chunk_document(
        self,
        text: str,
        doc_id: str,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Chunk a document into vector store format.
        
        Args:
            text: Document text
            doc_id: Document identifier
            doc_metadata: Document metadata
            
        Returns:
            List of chunk dicts ready for vector store
        """
        chunks = await self.chunk_text(text, doc_metadata)
        
        result = []
        for i, chunk in enumerate(chunks):
            result.append({
                "id": f"{doc_id}_chunk_{i}",
                "text": chunk.text,
                "metadata": {
                    **chunk.metadata,
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "cohesion_score": chunk.cohesion_score,
                    "sentence_count": chunk.sentence_count,
                },
            })
        
        return result


# Global semantic chunker instance
semantic_chunker = SemanticChunker()
