"""
Query Rewriter Agent for iterative retrieval improvement.

Implements the query rewrite loop pattern from research:
- Grades retrieval results for relevance
- Rewrites queries when results are poor
- Supports multiple rewrite attempts with fallback
"""

from typing import Any, Dict, List, Optional
import json

from .base_agent import AgentInput, AgentOutput, BaseAgent


class QueryRewriterAgent(BaseAgent):
    """
    Specialized agent for query rewriting and result grading.
    
    Key capability for achieving 90% precision: when initial 
    retrieval fails, rewrite the query and retry.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="query_rewriter",
            description="Grades retrieval results and rewrites queries for better precision",
            level=2,
            **kwargs
        )
    
    async def grade_results(
        self,
        query: str,
        documents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Grade retrieval results for relevance.
        
        Returns:
            Dict with grade (pass/fail), score, and reasoning
        """
        from ..llm import bedrock_client
        
        if not documents:
            return {
                "grade": "fail",
                "score": 0.0,
                "reason": "No documents retrieved",
                "needs_rewrite": True,
            }
        
        # Build document context for grading
        docs_text = "\n\n".join([
            f"[Doc {i+1}] {doc.get('text', '')[:200]}"
            for i, doc in enumerate(documents[:5])
        ])
        
        grade_prompt = f"""Grade these retrieved documents for relevance to the query.

Query: "{query}"

Retrieved Documents:
{docs_text}

Evaluate:
1. Do the documents contain information to answer the query?
2. How relevant is the content (0.0-1.0)?
3. Should the query be rewritten for better results?

Return JSON:
{{
    "grade": "pass" or "fail",
    "relevance_score": 0.0-1.0,
    "reasoning": "brief explanation",
    "needs_rewrite": true/false
}}

Return ONLY valid JSON."""

        try:
            result = await bedrock_client.generate(
                prompt=grade_prompt,
                system_prompt="You are a relevance grading expert. Be strict - only 'pass' if documents clearly answer the query.",
                temperature=0.1,
            )
            
            grading = json.loads(result.strip())
            
            return {
                "grade": grading.get("grade", "fail"),
                "score": grading.get("relevance_score", 0.0),
                "reason": grading.get("reasoning", ""),
                "needs_rewrite": grading.get("needs_rewrite", True),
            }
            
        except Exception as e:
            # Fallback: use average retrieval score
            avg_score = sum(d.get("score", 0) for d in documents) / len(documents)
            return {
                "grade": "pass" if avg_score > 0.7 else "fail",
                "score": avg_score,
                "reason": "Fallback scoring based on retrieval scores",
                "needs_rewrite": avg_score < 0.7,
            }
    
    async def rewrite_query(
        self,
        original_query: str,
        failed_results_summary: str = "",
        attempt: int = 1,
    ) -> str:
        """
        Rewrite query to improve retrieval precision.
        
        Strategies:
        - Expand with synonyms
        - Add specificity
        - Decompose complex queries
        - Extract key terms
        """
        from ..llm import bedrock_client
        
        rewrite_prompt = f"""Rewrite this query to improve document retrieval.

Original Query: "{original_query}"
Attempt: {attempt}
{'Previous results were poor: ' + failed_results_summary if failed_results_summary else ''}

Strategies to apply:
- Add synonyms for key terms
- Make the query more specific
- If complex, focus on the core information need
- Remove ambiguous pronouns

Return ONLY the rewritten query, no explanation."""

        try:
            rewritten = await bedrock_client.generate(
                prompt=rewrite_prompt,
                system_prompt="You are a search query optimization expert. Return only the improved query.",
                temperature=0.3,
            )
            
            return rewritten.strip().strip('"')
            
        except Exception:
            return original_query
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute query rewriting if needed.
        
        Checks retrieval results and rewrites if below threshold.
        """
        query = input_data.query
        context = input_data.context
        
        documents = context.get("retrieved_documents", [])
        max_rewrites = context.get("max_rewrites", 2)
        current_attempt = context.get("rewrite_attempt", 0)
        
        # Grade current results
        grading = await self.grade_results(query, documents)
        
        result = {
            "original_query": query,
            "grading": grading,
            "rewritten_query": None,
            "should_retry": False,
        }
        
        # If results are good, no rewrite needed
        if grading["grade"] == "pass" and grading["score"] >= 0.7:
            result["should_retry"] = False
            return AgentOutput(
                result=result,
                metadata={"agent": self.name, "action": "pass"},
                confidence_score=grading["score"],
            )
        
        # If we haven't exceeded max rewrites, rewrite and retry
        if current_attempt < max_rewrites and grading["needs_rewrite"]:
            rewritten = await self.rewrite_query(
                original_query=query,
                failed_results_summary=grading["reason"],
                attempt=current_attempt + 1,
            )
            
            result["rewritten_query"] = rewritten
            result["should_retry"] = True
            
            return AgentOutput(
                result=result,
                metadata={
                    "agent": self.name,
                    "action": "rewrite",
                    "attempt": current_attempt + 1,
                },
                confidence_score=grading["score"],
            )
        
        # Max rewrites reached, proceed with what we have
        return AgentOutput(
            result=result,
            metadata={"agent": self.name, "action": "max_attempts_reached"},
            confidence_score=grading["score"],
        )


# Global query rewriter instance
query_rewriter = QueryRewriterAgent()
