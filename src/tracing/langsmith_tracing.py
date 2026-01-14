"""
LangSmith tracing integration for observability.

Provides:
- Automatic tracing of LLM calls
- Agent execution tracing
- Custom run metadata
"""

import os
from typing import Optional, Dict, Any
from functools import wraps
from contextlib import asynccontextmanager

from ..config import settings


def setup_langsmith():
    """
    Configure LangSmith tracing from environment.
    
    Call this at application startup to enable tracing.
    """
    if settings.langchain_tracing_v2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = settings.langchain_endpoint
        
        if settings.langchain_api_key:
            os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        
        print(f"✅ LangSmith tracing enabled for project: {settings.langchain_project}")
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"


@asynccontextmanager
async def trace_agent(
    agent_name: str,
    run_type: str = "chain",
    metadata: Optional[Dict[str, Any]] = None,
):
    """
    Context manager for tracing agent execution.
    
    Usage:
        async with trace_agent("query_analyzer", metadata={"query": query}):
            result = await agent.run(input)
    
    Args:
        agent_name: Name of the agent being traced
        run_type: Type of run (chain, llm, tool)
        metadata: Additional metadata for the trace
    """
    try:
        from langsmith import traceable
        from langsmith.run_helpers import get_current_run_tree
        
        # Add metadata to current trace if available
        run_tree = get_current_run_tree()
        if run_tree and metadata:
            run_tree.add_metadata(metadata)
        
        yield
        
    except ImportError:
        # LangSmith not installed, skip tracing
        yield
    except Exception:
        # Tracing error, don't fail the agent
        yield


def trace_llm_call(func):
    """
    Decorator to trace LLM calls.
    
    Usage:
        @trace_llm_call
        async def generate(self, prompt: str) -> str:
            ...
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            from langsmith import traceable
            
            # Wrap with traceable if available
            traced_func = traceable(run_type="llm", name=func.__name__)(func)
            return await traced_func(*args, **kwargs)
            
        except ImportError:
            return await func(*args, **kwargs)
    
    return wrapper


class TracingCallbackHandler:
    """
    Callback handler for LangChain tracing events.
    
    Captures detailed execution metrics for analysis.
    """
    
    def __init__(self):
        self.runs = []
    
    def on_llm_start(self, serialized: Dict, prompts: list, **kwargs):
        """Called when LLM starts."""
        self.runs.append({
            "type": "llm_start",
            "model": serialized.get("name", "unknown"),
            "prompts": len(prompts),
        })
    
    def on_llm_end(self, response, **kwargs):
        """Called when LLM ends."""
        self.runs.append({
            "type": "llm_end",
            "tokens": getattr(response, "llm_output", {}).get("token_usage", {}),
        })
    
    def on_chain_start(self, serialized: Dict, inputs: Dict, **kwargs):
        """Called when chain starts."""
        self.runs.append({
            "type": "chain_start",
            "name": serialized.get("name", "unknown"),
        })
    
    def on_chain_end(self, outputs: Dict, **kwargs):
        """Called when chain ends."""
        self.runs.append({
            "type": "chain_end",
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        llm_calls = len([r for r in self.runs if r["type"] == "llm_start"])
        chain_calls = len([r for r in self.runs if r["type"] == "chain_start"])
        
        return {
            "total_runs": len(self.runs),
            "llm_calls": llm_calls,
            "chain_calls": chain_calls,
        }
