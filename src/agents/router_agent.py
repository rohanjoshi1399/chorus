"""
Router Agent (Level 2) - Intelligent strategy selection for retrieval.

Responsibilities:
- Route based on Query Analyzer output
- Support multiple simultaneous strategies (hybrid retrieval)
- Determine confidence thresholds
- Coordinate parallel retrieval from multiple sources
- Implement fallback logic (vector → graph → web)
"""

from typing import Any, Dict, List

from .base_agent import AgentInput, AgentOutput, BaseAgent
from ..config import settings


class RouterAgent(BaseAgent):
    """
    Level 2 agent that routes queries to appropriate Level 3 retrieval specialists.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="router",
            description="Routes queries to appropriate retrieval strategies",
            level=2,
            **kwargs
        )
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Determine which retrieval strategies to use based on query analysis.
        
        Routing Logic:
        - Entities with relationships → graph + vector
        - Time-sensitive → web + vector
        - Code examples → vector (code in docs)
        - Default → vector only
        
        Returns:
            List of strategies and routing metadata
        """
        analysis = input_data.context.get("analysis", {})
        entities = analysis.get("entities", [])
        intent = analysis.get("intent", "factual_qa")
        time_sensitive = analysis.get("time_sensitive", False)
        complexity = analysis.get("complexity", "simple")
        requires_code = analysis.get("requires_code_examples", False)
        
        strategies = []
        routing_reason = []
        
        # Decision tree for strategy selection
        if len(entities) > 1 and complexity in ["moderate", "multi_hop"]:
            # Multiple entities with relationships → use GraphRAG
            if settings.graphrag_enabled:
                strategies.append("graph")
                routing_reason.append("Multiple entities detected, using graph for relationships")
            strategies.append("vector")
            routing_reason.append("Vector search for semantic matching")
            
        elif time_sensitive:
            # Time-sensitive → prioritize web search
            if settings.web_search_enabled:
                strategies.append("web")
                routing_reason.append("Time-sensitive query, using web search")
            strategies.append("vector")
            routing_reason.append("Vector search as fallback")
            
        elif requires_code:
            # Code examples → vector search (code is in indexed docs)
            strategies.append("vector")
            routing_reason.append("Code example needed, searching documentation")
            
        elif complexity == "multi_hop":
            # Complex queries → hybrid search
            strategies.append("vector")
            if settings.graphrag_enabled:
                strategies.append("graph")
                routing_reason.append("Multi-hop query, using hybrid vector + graph")
            else:
                routing_reason.append("Multi-hop query, using enhanced vector search")
                
        else:
            # Default: vector search
            strategies.append("vector")
            routing_reason.append("Standard vector search")
        
        # Ensure at least vector search is always included
        if "vector" not in strategies:
            strategies.append("vector")
        
        return AgentOutput(
            result={
                "strategies": strategies,
                "routing_reasons": routing_reason,
                "primary_strategy": strategies[0],
                "fallback_enabled": len(strategies) > 1,
            },
            metadata={
                "agent": self.name,
                "routing_decision": strategies,
                "query_complexity": complexity,
                "entities_count": len(entities),
            },
            next_agent="retrieval"
        )
