"""
Agent state management for LangGraph orchestration.

Defines the shared state that flows between agents in the 8-agent system.
"""

from typing import Dict, Any, List, Optional, TypedDict
from enum import Enum
from pydantic import BaseModel, Field


class QueryComplexity(str, Enum):
    """Query complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    MULTI_HOP = "multi_hop"


class QueryIntent(str, Enum):
    """Query intent types."""
    FACTUAL_QA = "factual_qa"
    COMPARISON = "comparison"
    EXPLANATION = "explanation"
    HOW_TO = "how_to"
    CODE_EXAMPLE = "code_example"


class RetrievalStrategy(str, Enum):
    """Available retrieval strategies."""
    VECTOR = "vector"
    GRAPH = "graph"
    WEB = "web"
    HYBRID = "hybrid"


class QueryAnalysis(BaseModel):
    """Output from Query Analyzer agent."""
    intent: QueryIntent = QueryIntent.FACTUAL_QA
    entities: List[str] = Field(default_factory=list)
    complexity: QueryComplexity = QueryComplexity.SIMPLE
    time_sensitive: bool = False
    requires_code_examples: bool = False
    ambiguity_score: float = 0.0


class RetrievedDocument(BaseModel):
    """A retrieved document with metadata."""
    id: str
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source: str = "vector"  # vector, graph, web


class ValidationResult(BaseModel):
    """Output from Validation agent."""
    validated_facts: List[str] = Field(default_factory=list)
    confidence_score: float = 1.0
    hallucination_detected: bool = False
    inconsistencies: List[str] = Field(default_factory=list)
    citation_accuracy: float = 1.0


class AgentState(TypedDict, total=False):
    """
    Shared state for LangGraph agent orchestration.
    
    This state flows through all agents and accumulates results
    from each step of the pipeline.
    """
    # Input
    query: str
    session_id: Optional[str]
    conversation_history: List[Dict[str, str]]
    
    # Query Analysis (from Query Analyzer)
    analysis: Optional[Dict[str, Any]]
    
    # Routing (from Router)
    strategies: List[str]
    
    # Retrieved content (from Retrieval agents)
    retrieved_documents: List[Dict[str, Any]]
    graph_results: Optional[Dict[str, Any]]
    web_results: Optional[Dict[str, Any]]
    
    # Validation (from Validator)
    validation: Optional[Dict[str, Any]]
    
    # Final output (from Synthesis)
    response: Optional[str]
    sources: List[Dict[str, Any]]
    
    # Metadata
    current_agent: str
    agent_trace: List[str]
    error: Optional[str]
    confidence: float


def create_initial_state(
    query: str,
    session_id: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None,
) -> AgentState:
    """
    Create initial agent state for a new query.
    
    Args:
        query: User query
        session_id: Optional session identifier
        conversation_history: Optional conversation history
        
    Returns:
        Initial AgentState
    """
    return AgentState(
        query=query,
        session_id=session_id,
        conversation_history=conversation_history or [],
        analysis=None,
        strategies=[],
        retrieved_documents=[],
        graph_results=None,
        web_results=None,
        validation=None,
        response=None,
        sources=[],
        current_agent="supervisor",
        agent_trace=["supervisor"],
        error=None,
        confidence=0.0,
    )
