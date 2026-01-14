"""
Query Analyzer Agent (Level 2) - Intent understanding and entity extraction.

Responsibilities:
- Analyze query intent (factual Q&A, comparison, explanation, how-to)
- Extract named entities (classes, functions, modules, APIs)
- Determine query complexity (simple, multi-hop, requires synthesis)
- Identify time sensitivity
- Resolve pronoun references using conversation memory
- Detect ambiguity
"""

from typing import Any, Dict, List

from .base_agent import AgentInput, AgentOutput, BaseAgent


class QueryAnalyzerAgent(BaseAgent):
    """
    Level 2 agent that analyzes user intent and extracts query characteristics.
    """
    
    def __init__(self, llm=None, **kwargs):
        super().__init__(
            name="query_analyzer",
            description="Analyzes user intent and query characteristics",
            level=2,
            **kwargs
        )
        self.llm = llm
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Analyze query to extract intent, entities, and complexity.
        
        Uses Claude 4.5 Sonnet to understand query characteristics.
        
        Returns:
            AgentOutput with analysis results
        """
        from ..llm import bedrock_client
        
        analysis_prompt = f"""Analyze this user query and extract key characteristics.

User Query: "{input_data.query}"

Provide a JSON response with:
1. intent: Type of query (factual_qa, comparison, explanation, how_to, code_example)
2. entities: List of key entities/concepts mentioned (classes, functions, APIs, technical terms)
3. complexity: Query complexity (simple, moderate, multi_hop)
4. time_sensitive: Whether query asks about latest/recent/current information (true/false)
5. requires_code_examples: Whether user likely wants code examples (true/false)
6. ambiguity_score: How ambiguous the query is (0.0 to 1.0, where 1.0 is very ambiguous)

Return ONLY valid JSON, no other text."""

        try:
            result = await bedrock_client.generate(
                prompt=analysis_prompt,
                system_prompt="You are a query analysis expert. Respond only with valid JSON.",
                temperature=0.1,
            )
            
            # Parse JSON response
            import json
            analysis = json.loads(result)
            
            # Ensure all required fields exist
            analysis.setdefault("intent", "factual_qa")
            analysis.setdefault("entities", [])
            analysis.setdefault("complexity", "simple")
            analysis.setdefault("time_sensitive", False)
            analysis.setdefault("requires_code_examples", False)
            analysis.setdefault("ambiguity_score", 0.0)
            
        except Exception as e:
            # Fallback to simple analysis
            analysis = {
                "intent": "factual_qa",
                "entities": [],
                "complexity": "simple",
                "time_sensitive": False,
                "requires_code_examples": False,
                "ambiguity_score": 0.0,
                "error": str(e),
            }
        
        return AgentOutput(
            result=analysis,
            metadata={
                "agent": self.name,
                "query_length": len(input_data.query),
            },
            next_agent="router"
        )
