"""
Base agent interface defining common functionality for all agents.

All agents in the system inherit from this base class to ensure
consistent interfaces for orchestration and state management.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AgentInput(BaseModel):
    """Input schema for agent execution."""
    
    query: str
    context: Dict[str, Any] = {}
    conversation_history: List[Dict[str, str]] = []
    metadata: Dict[str, Any] = {}


class AgentOutput(BaseModel):
    """Output schema for agent execution."""
    
    result: Any
    metadata: Dict[str, Any] = {}
    next_agent: Optional[str] = None
    confidence_score: float = 1.0
    error: Optional[str] = None


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the multi-agent RAG system.
    
    Attributes:
        name: Unique identifier for the agent
        description: Human-readable description of agent's role
        level: Hierarchical level (1=Supervisor, 2=Coordinator, 3=Specialist)
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        level: int,
        **kwargs
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent identifier
            description: Agent role description
            level: Hierarchy level (1-3)
            **kwargs: Additional agent-specific configuration
        """
        self.name = name
        self.description = description
        self. = level
        self.config = kwargs
        
    @abstractmethod
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute the agent's core logic.
        
        Args:
            input_data: Structured input for the agent
            
        Returns:
            AgentOutput with results and metadata
        """
        pass
    
    async def pre_execute(self, input_data: AgentInput) -> AgentInput:
        """
        Hook for preprocessing before execution.
        
        Args:
            input_data: Raw input data
            
        Returns:
            Processed input data
        """
        return input_data
    
    async def post_execute(self, output: AgentOutput) -> AgentOutput:
        """
        Hook for postprocessing after execution.
        
        Args:
            output: Raw output from execute()
            
        Returns:
            Processed output
        """
        return output
    
    async def run(self, input_data: AgentInput) -> AgentOutput:
        """
        Full execution pipeline with pre/post hooks.
        
        Args:
            input_data: Agent input
            
        Returns:
            Agent output
        """
        try:
            # Preprocess
            processed_input = await self.pre_execute(input_data)
            
            # Execute
            output = await self.execute(processed_input)
            
            # Postprocess
            final_output = await self.post_execute(output)
            
            return final_output
            
        except Exception as e:
            return AgentOutput(
                result=None,
                error=str(e),
                metadata={"agent": self.name, "level": self.level}
            )
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', level={self.level})"
