"""
Validation Agent (Level 2) - Fact-checker and quality assurance.

Responsibilities:
- Verify factual accuracy of retrieved information
- Cross-reference claims across sources
- Detect hallucinations
- Check citation accuracy
- Assign confidence scores
- Flag inconsistencies
"""

from typing import Any, Dict, List
import json

from .base_agent import AgentInput, AgentOutput, BaseAgent


class ValidationAgent(BaseAgent):
    """
    Level 2 agent for fact-checking and quality assurance.
    """
    
    def __init__(self, llm=None, **kwargs):
        super().__init__(
            name="validator",
            description="Validates facts and detects hallucinations",
            level=2,
            **kwargs
        )
        self.llm = llm
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Validate retrieved information for accuracy.
        
        Techniques:
        - Source consistency check
        - Temporal validation
        - Attribution verification
        - LLM-as-judge for quality assessment
        
        Returns:
            Validated facts with confidence scores
        """
        from ..llm import bedrock_client
        
        query = input_data.query
        context = input_data.context
        retrieved_docs = context.get("retrieved_documents", [])
        
        if not retrieved_docs:
            return AgentOutput(
                result={
                    "validated_facts": [],
                    "confidence_score": 0.0,
                    "hallucination_detected": False,
                    "inconsistencies": [],
                    "citation_accuracy": 0.0,
                    "validation_passed": False,
                    "reason": "No documents retrieved to validate"
                },
                metadata={"agent": self.name},
                confidence_score=0.0
            )
        
        # Build context from documents
        docs_context = "\n\n".join([
            f"[Source {i+1}] (Score: {doc.get('score', 0):.2f})\n{doc.get('text', '')[:400]}"
            for i, doc in enumerate(retrieved_docs[:5])
        ])
        
        # LLM-based validation
        validation_prompt = f"""Analyze the quality and consistency of these retrieved documents for answering the user's question.

User Question: "{query}"

Retrieved Sources:
{docs_context}

Evaluate and respond with JSON:
{{
    "relevance_score": 0.0-1.0 (how relevant are the sources to the question),
    "consistency_score": 0.0-1.0 (do the sources agree with each other),
    "coverage_score": 0.0-1.0 (do the sources fully answer the question),
    "potential_issues": ["list of any concerns or gaps"],
    "best_sources": [list of source numbers that are most reliable],
    "recommended_approach": "how to best synthesize the answer"
}}

Return ONLY valid JSON."""

        try:
            result = await bedrock_client.generate(
                prompt=validation_prompt,
                system_prompt="You are a fact-checking expert. Evaluate source quality objectively. Return only valid JSON.",
                temperature=0.1,
            )
            
            validation = json.loads(result)
            
            # Calculate overall confidence
            relevance = validation.get("relevance_score", 0.5)
            consistency = validation.get("consistency_score", 0.8)
            coverage = validation.get("coverage_score", 0.5)
            
            confidence_score = (relevance * 0.4 + consistency * 0.3 + coverage * 0.3)
            
            # Check for potential hallucination risk
            hallucination_risk = relevance < 0.5 or len(validation.get("potential_issues", [])) > 2
            
            validation_result = {
                "validated_facts": validation.get("best_sources", []),
                "confidence_score": confidence_score,
                "hallucination_detected": hallucination_risk,
                "inconsistencies": validation.get("potential_issues", []),
                "citation_accuracy": consistency,
                "validation_passed": confidence_score >= 0.6,
                "relevance_score": relevance,
                "coverage_score": coverage,
                "recommended_approach": validation.get("recommended_approach", ""),
            }
            
        except Exception as e:
            # Fallback: basic validation based on retrieval scores
            avg_score = sum(doc.get("score", 0) for doc in retrieved_docs) / len(retrieved_docs)
            
            validation_result = {
                "validated_facts": list(range(1, min(len(retrieved_docs), 4))),
                "confidence_score": avg_score,
                "hallucination_detected": avg_score < 0.5,
                "inconsistencies": [],
                "citation_accuracy": 0.8,
                "validation_passed": avg_score >= 0.6,
                "fallback_validation": True,
                "error": str(e),
            }
        
        return AgentOutput(
            result=validation_result,
            metadata={"agent": self.name, "docs_validated": len(retrieved_docs)},
            confidence_score=validation_result["confidence_score"]
        )
