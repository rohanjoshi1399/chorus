"""
RAG Orchestrator service.

Provides the full 8-agent LangGraph orchestrator for Phase 2.
"""

from typing import Dict, Any, List, Optional

from ..agents.supervisor_orchestrator import SupervisorOrchestrator, supervisor_orchestrator


# Re-export the LangGraph-based orchestrator as the main orchestrator
orchestrator = supervisor_orchestrator
