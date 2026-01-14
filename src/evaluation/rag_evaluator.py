"""
RAG Evaluation Suite using RAGAS and DeepEval metrics.

Provides metrics for achieving and validating 90% precision:
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Faithfulness
- Answer Relevancy
- Context Relevancy
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import asyncio


@dataclass
class EvaluationResult:
    """Container for evaluation metrics."""
    precision_at_k: float
    recall_at_k: float
    mrr: float
    faithfulness: float
    answer_relevancy: float
    context_relevancy: float
    overall_score: float
    details: Dict[str, Any]


class RAGEvaluator:
    """
    RAG evaluation framework inspired by RAGAS and DeepEval.
    
    Measures both retrieval and generation quality.
    """
    
    def __init__(self, llm=None):
        """
        Initialize evaluator.
        
        Args:
            llm: Optional LLM for LLM-as-judge metrics
        """
        self.llm = llm
    
    def precision_at_k(
        self,
        retrieved_ids: List[str],
        relevant_ids: List[str],
        k: int = 5,
    ) -> float:
        """
        Calculate Precision@K.
        
        Precision@K = (relevant docs in top-K) / K
        """
        if not retrieved_ids or k <= 0:
            return 0.0
        
        top_k = retrieved_ids[:k]
        relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_ids)
        
        return relevant_in_top_k / k
    
    def recall_at_k(
        self,
        retrieved_ids: List[str],
        relevant_ids: List[str],
        k: int = 5,
    ) -> float:
        """
        Calculate Recall@K.
        
        Recall@K = (relevant docs in top-K) / (total relevant docs)
        """
        if not relevant_ids:
            return 0.0
        
        top_k = retrieved_ids[:k]
        relevant_in_top_k = sum(1 for doc_id in top_k if doc_id in relevant_ids)
        
        return relevant_in_top_k / len(relevant_ids)
    
    def mean_reciprocal_rank(
        self,
        retrieved_ids: List[str],
        relevant_ids: List[str],
    ) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR).
        
        MRR = 1 / (position of first relevant doc)
        """
        for i, doc_id in enumerate(retrieved_ids):
            if doc_id in relevant_ids:
                return 1.0 / (i + 1)
        
        return 0.0
    
    async def faithfulness(
        self,
        answer: str,
        context: str,
    ) -> float:
        """
        Measure faithfulness: is the answer grounded in context?
        
        Uses LLM-as-judge to check if answer claims are supported.
        """
        from ..llm import bedrock_client
        
        prompt = f"""Evaluate if the answer is faithfully grounded in the context.

Context:
{context[:2000]}

Answer:
{answer}

Score from 0.0 (hallucinated) to 1.0 (fully grounded).
Consider:
- Are all claims in the answer supported by context?
- Does the answer make unsupported assertions?

Return ONLY a number between 0.0 and 1.0."""

        try:
            result = await bedrock_client.generate(
                prompt=prompt,
                system_prompt="You are a faithfulness evaluator. Return only a decimal number.",
                temperature=0.0,
            )
            
            score = float(result.strip())
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5
    
    async def answer_relevancy(
        self,
        query: str,
        answer: str,
    ) -> float:
        """
        Measure answer relevancy: does the answer address the query?
        """
        from ..llm import bedrock_client
        
        prompt = f"""Evaluate if the answer is relevant to the query.

Query: {query}

Answer:
{answer}

Score from 0.0 (irrelevant) to 1.0 (perfectly relevant).
Consider:
- Does the answer address the question asked?
- Is the answer complete and on-topic?

Return ONLY a number between 0.0 and 1.0."""

        try:
            result = await bedrock_client.generate(
                prompt=prompt,
                system_prompt="You are a relevancy evaluator. Return only a decimal number.",
                temperature=0.0,
            )
            
            score = float(result.strip())
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5
    
    async def context_relevancy(
        self,
        query: str,
        context: str,
    ) -> float:
        """
        Measure context relevancy: is the retrieved context useful?
        """
        from ..llm import bedrock_client
        
        prompt = f"""Evaluate if the context is relevant for answering the query.

Query: {query}

Context:
{context[:2000]}

Score from 0.0 (irrelevant) to 1.0 (highly relevant).
Consider:
- Does the context contain information needed to answer?
- Is the context focused on the query topic?

Return ONLY a number between 0.0 and 1.0."""

        try:
            result = await bedrock_client.generate(
                prompt=prompt,
                system_prompt="You are a context relevancy evaluator. Return only a decimal number.",
                temperature=0.0,
            )
            
            score = float(result.strip())
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5
    
    async def evaluate(
        self,
        query: str,
        answer: str,
        retrieved_docs: List[Dict[str, Any]],
        relevant_doc_ids: Optional[List[str]] = None,
        k: int = 5,
    ) -> EvaluationResult:
        """
        Run full evaluation suite.
        
        Args:
            query: User query
            answer: Generated answer
            retrieved_docs: Retrieved documents
            relevant_doc_ids: Ground truth relevant doc IDs (for P@K, R@K)
            k: K value for precision/recall
            
        Returns:
            EvaluationResult with all metrics
        """
        # Build context from retrieved docs
        context = "\n\n".join([
            doc.get("text", "")[:500] for doc in retrieved_docs[:k]
        ])
        
        # Retrieved doc IDs
        retrieved_ids = [doc.get("id", str(i)) for i, doc in enumerate(retrieved_docs)]
        
        # Calculate retrieval metrics if ground truth available
        if relevant_doc_ids:
            p_at_k = self.precision_at_k(retrieved_ids, relevant_doc_ids, k)
            r_at_k = self.recall_at_k(retrieved_ids, relevant_doc_ids, k)
            mrr = self.mean_reciprocal_rank(retrieved_ids, relevant_doc_ids)
        else:
            p_at_k = 0.0
            r_at_k = 0.0
            mrr = 0.0
        
        # Calculate LLM-based metrics concurrently
        faithfulness_score, answer_rel, context_rel = await asyncio.gather(
            self.faithfulness(answer, context),
            self.answer_relevancy(query, answer),
            self.context_relevancy(query, context),
        )
        
        # Calculate overall score
        # Weight: 40% faithfulness, 30% answer relevancy, 30% context relevancy
        overall = (
            0.4 * faithfulness_score +
            0.3 * answer_rel +
            0.3 * context_rel
        )
        
        return EvaluationResult(
            precision_at_k=p_at_k,
            recall_at_k=r_at_k,
            mrr=mrr,
            faithfulness=faithfulness_score,
            answer_relevancy=answer_rel,
            context_relevancy=context_rel,
            overall_score=overall,
            details={
                "k": k,
                "num_docs_retrieved": len(retrieved_docs),
                "context_length": len(context),
            },
        )
    
    async def batch_evaluate(
        self,
        test_cases: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Evaluate multiple test cases and aggregate metrics.
        
        Args:
            test_cases: List of {query, answer, retrieved_docs, relevant_ids}
            
        Returns:
            Aggregated metrics and individual results
        """
        results = []
        
        for case in test_cases:
            result = await self.evaluate(
                query=case["query"],
                answer=case["answer"],
                retrieved_docs=case["retrieved_docs"],
                relevant_doc_ids=case.get("relevant_ids"),
            )
            results.append(result)
        
        # Aggregate
        n = len(results)
        if n == 0:
            return {"error": "No test cases"}
        
        return {
            "num_cases": n,
            "avg_precision_at_k": sum(r.precision_at_k for r in results) / n,
            "avg_recall_at_k": sum(r.recall_at_k for r in results) / n,
            "avg_mrr": sum(r.mrr for r in results) / n,
            "avg_faithfulness": sum(r.faithfulness for r in results) / n,
            "avg_answer_relevancy": sum(r.answer_relevancy for r in results) / n,
            "avg_context_relevancy": sum(r.context_relevancy for r in results) / n,
            "avg_overall_score": sum(r.overall_score for r in results) / n,
            "individual_results": [
                {
                    "overall": r.overall_score,
                    "faithfulness": r.faithfulness,
                    "answer_relevancy": r.answer_relevancy,
                }
                for r in results
            ],
        }


# Global evaluator instance
rag_evaluator = RAGEvaluator()
