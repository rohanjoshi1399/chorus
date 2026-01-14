"""
Enhanced Supervisor Agent (Level 1) with LangGraph orchestration.

Implements the full 8-agent hierarchical system with query rewrite loop:
- Level 1: Supervisor (this agent)
- Level 2: Query Analyzer, Router, Query Rewriter, Validator, Synthesis
- Level 3: Retrieval, Graph Query, Web Search

Key enhancement: Iterative retrieval with query rewriting for 90% precision.
"""

import asyncio
from typing import Any, Dict, Literal
from langgraph.graph import StateGraph, END

from .agent_state import AgentState, create_initial_state
from .query_analyzer import QueryAnalyzerAgent
from .router_agent import RouterAgent
from .query_rewriter import QueryRewriterAgent
from .retrieval_agent import RetrievalAgent
from .graph_query_agent import GraphQueryAgent
from .web_search_agent import WebSearchAgent
from .validation_agent import ValidationAgent
from .synthesis_agent import SynthesisAgent


class SupervisorOrchestrator:
    """
    Level 1 orchestrator using LangGraph for multi-agent coordination.
    
    Enhanced with query rewrite loop for 90% precision target:
    Supervisor → Query Analyzer → Router → Retrieval → Grade → [Rewrite?] → Validator → Synthesis
    """
    
    MAX_REWRITE_ATTEMPTS = 2
    
    def __init__(self):
        """Initialize all agents and build workflow."""
        # Level 2 agents
        self.query_analyzer = QueryAnalyzerAgent()
        self.router = RouterAgent()
        self.query_rewriter = QueryRewriterAgent()
        self.validator = ValidationAgent()
        self.synthesizer = SynthesisAgent()
        
        # Level 3 agents
        self.retrieval_agent = RetrievalAgent()
        self.graph_agent = GraphQueryAgent()
        self.web_agent = WebSearchAgent()
        
        # Build LangGraph workflow
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph state machine with query rewrite loop.
        
        Flow:
        supervisor → query_analyzer → router → multi_retrieval → 
        grade_results → [rewrite & retry OR continue] → validator → synthesis → END
        """
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("query_analyzer", self._query_analyzer_node)
        workflow.add_node("router", self._router_node)
        workflow.add_node("multi_retrieval", self._multi_retrieval_node)
        workflow.add_node("grade_results", self._grade_results_node)
        workflow.add_node("rewrite_query", self._rewrite_query_node)
        workflow.add_node("validator", self._validator_node)
        workflow.add_node("synthesis", self._synthesis_node)
        
        # Define edges
        workflow.set_entry_point("supervisor")
        workflow.add_edge("supervisor", "query_analyzer")
        workflow.add_edge("query_analyzer", "router")
        workflow.add_conditional_edges(
            "router",
            self._route_to_retrieval,
            {
                "multi_retrieval": "multi_retrieval",
                "synthesis": "synthesis",
            }
        )
        workflow.add_edge("multi_retrieval", "grade_results")
        
        # Conditional: rewrite or continue
        workflow.add_conditional_edges(
            "grade_results",
            self._should_rewrite,
            {
                "rewrite": "rewrite_query",
                "continue": "validator",
            }
        )
        
        # After rewrite, go back to retrieval
        workflow.add_edge("rewrite_query", "multi_retrieval")
        
        workflow.add_edge("validator", "synthesis")
        workflow.add_edge("synthesis", END)
        
        return workflow.compile()
    
    async def _supervisor_node(self, state: AgentState) -> AgentState:
        """Initialize orchestration."""
        state["current_agent"] = "supervisor"
        state["agent_trace"] = ["supervisor"]
        state["rewrite_count"] = 0
        return state
    
    async def _query_analyzer_node(self, state: AgentState) -> AgentState:
        """Analyze user intent."""
        from .base_agent import AgentInput
        
        state["current_agent"] = "query_analyzer"
        state["agent_trace"].append("query_analyzer")
        
        input_data = AgentInput(
            query=state["query"],
            conversation_history=state.get("conversation_history", []),
        )
        
        output = await self.query_analyzer.run(input_data)
        state["analysis"] = output.result
        
        # Store original query for potential rewriting
        state["original_query"] = state["query"]
        
        return state
    
    async def _router_node(self, state: AgentState) -> AgentState:
        """Determine retrieval strategies."""
        from .base_agent import AgentInput
        
        state["current_agent"] = "router"
        state["agent_trace"].append("router")
        
        input_data = AgentInput(
            query=state["query"],
            context={"analysis": state.get("analysis", {})},
        )
        
        output = await self.router.run(input_data)
        state["strategies"] = output.result.get("strategies", ["vector"])
        
        return state
    
    def _route_to_retrieval(self, state: AgentState) -> Literal["multi_retrieval", "synthesis"]:
        """Skip retrieval for greetings."""
        analysis = state.get("analysis", {})
        intent = analysis.get("intent", "factual_qa")
        
        if intent == "greeting" or state.get("query", "").lower() in ["hi", "hello", "hey"]:
            return "synthesis"
        
        return "multi_retrieval"
    
    async def _multi_retrieval_node(self, state: AgentState) -> AgentState:
        """Execute parallel retrieval strategies."""
        from .base_agent import AgentInput
        
        state["current_agent"] = "multi_retrieval"
        state["agent_trace"].append("multi_retrieval")
        
        strategies = state.get("strategies", ["vector"])
        current_query = state.get("query", state.get("original_query", ""))
        
        # Build async tasks
        tasks = []
        task_names = []
        
        # Vector retrieval (always)
        vector_input = AgentInput(
            query=current_query,
            context={
                "strategies": strategies,
                "analysis": state.get("analysis", {}),
                "top_k": 10,
            },
        )
        tasks.append(self.retrieval_agent.run(vector_input))
        task_names.append("vector")
        
        # Graph retrieval
        if "graph" in strategies:
            graph_input = AgentInput(
                query=current_query,
                context={"analysis": state.get("analysis", {})},
            )
            tasks.append(self.graph_agent.run(graph_input))
            task_names.append("graph")
        
        # Web retrieval
        if "web" in strategies:
            web_input = AgentInput(
                query=current_query,
                context={"analysis": state.get("analysis", {})},
            )
            tasks.append(self.web_agent.run(web_input))
            task_names.append("web")
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        all_documents = []
        
        for name, result in zip(task_names, results):
            if isinstance(result, Exception):
                continue
            
            if name == "vector":
                docs = result.result.get("documents", [])
                for doc in docs:
                    doc["source_type"] = "vector"
                all_documents.extend(docs)
                
            elif name == "graph":
                state["graph_results"] = result.result
                for entity in result.result.get("entities", []):
                    all_documents.append({
                        "id": entity.get("id", ""),
                        "text": f"{entity.get('name', '')}: {entity.get('description', '')}",
                        "score": 0.8,
                        "metadata": entity,
                        "source_type": "graph",
                    })
                    
            elif name == "web":
                state["web_results"] = result.result
                for web_result in result.result.get("results", []):
                    all_documents.append({
                        "id": web_result.get("url", ""),
                        "text": f"{web_result.get('title', '')}\n{web_result.get('content', '')}",
                        "score": web_result.get("credibility", 0.5),
                        "metadata": {"url": web_result.get("url", "")},
                        "source_type": "web",
                    })
        
        # Sort by score
        all_documents.sort(key=lambda x: x.get("score", 0), reverse=True)
        state["retrieved_documents"] = all_documents[:15]
        
        return state
    
    async def _grade_results_node(self, state: AgentState) -> AgentState:
        """Grade retrieval results for relevance."""
        from .base_agent import AgentInput
        
        state["current_agent"] = "grade_results"
        state["agent_trace"].append("grade_results")
        
        input_data = AgentInput(
            query=state.get("query", ""),
            context={
                "retrieved_documents": state.get("retrieved_documents", []),
                "rewrite_attempt": state.get("rewrite_count", 0),
                "max_rewrites": self.MAX_REWRITE_ATTEMPTS,
            },
        )
        
        output = await self.query_rewriter.run(input_data)
        
        state["grading"] = output.result.get("grading", {})
        state["should_rewrite"] = output.result.get("should_retry", False)
        state["rewritten_query"] = output.result.get("rewritten_query")
        
        return state
    
    def _should_rewrite(self, state: AgentState) -> Literal["rewrite", "continue"]:
        """Decide whether to rewrite query and retry."""
        should_rewrite = state.get("should_rewrite", False)
        rewrite_count = state.get("rewrite_count", 0)
        
        if should_rewrite and rewrite_count < self.MAX_REWRITE_ATTEMPTS:
            return "rewrite"
        
        return "continue"
    
    async def _rewrite_query_node(self, state: AgentState) -> AgentState:
        """Update query with rewritten version."""
        state["current_agent"] = "rewrite_query"
        state["agent_trace"].append("rewrite_query")
        
        rewritten = state.get("rewritten_query")
        if rewritten:
            state["query"] = rewritten
        
        state["rewrite_count"] = state.get("rewrite_count", 0) + 1
        
        return state
    
    async def _validator_node(self, state: AgentState) -> AgentState:
        """Validate retrieved information."""
        from .base_agent import AgentInput
        
        state["current_agent"] = "validator"
        state["agent_trace"].append("validator")
        
        input_data = AgentInput(
            query=state.get("original_query", state["query"]),
            context={
                "retrieved_documents": state.get("retrieved_documents", []),
            },
        )
        
        output = await self.validator.run(input_data)
        state["validation"] = output.result
        state["confidence"] = output.confidence_score
        
        return state
    
    async def _synthesis_node(self, state: AgentState) -> AgentState:
        """Generate final response."""
        from .base_agent import AgentInput
        
        state["current_agent"] = "synthesis"
        state["agent_trace"].append("synthesis")
        
        input_data = AgentInput(
            query=state.get("original_query", state["query"]),
            context={
                "retrieved_documents": state.get("retrieved_documents", []),
                "validation": state.get("validation", {}),
                "graph_results": state.get("graph_results", {}),
                "web_results": state.get("web_results", {}),
            },
        )
        
        output = await self.synthesizer.run(input_data)
        state["response"] = output.result.get("answer", "")
        state["sources"] = output.result.get("sources", [])
        state["confidence"] = output.confidence_score
        
        return state
    
    async def process_query(
        self,
        query: str,
        session_id: str = None,
        conversation_history: list = None,
    ) -> Dict[str, Any]:
        """Process a query through the full agent pipeline."""
        initial_state = create_initial_state(
            query=query,
            session_id=session_id,
            conversation_history=conversation_history or [],
        )
        
        final_state = await self.workflow.ainvoke(initial_state)
        
        return {
            "answer": final_state.get("response", ""),
            "sources": final_state.get("sources", []),
            "metadata": {
                "session_id": session_id,
                "original_query": final_state.get("original_query", query),
                "final_query": final_state.get("query", query),
                "rewrites": final_state.get("rewrite_count", 0),
                "query_analysis": final_state.get("analysis", {}),
                "strategies_used": final_state.get("strategies", []),
                "documents_retrieved": len(final_state.get("retrieved_documents", [])),
                "grading": final_state.get("grading", {}),
                "graph_results": final_state.get("graph_results"),
                "web_results": final_state.get("web_results"),
                "validation": final_state.get("validation", {}),
                "confidence": final_state.get("confidence", 0.0),
                "agent_trace": final_state.get("agent_trace", []),
            },
        }


# Global orchestrator instance
supervisor_orchestrator = SupervisorOrchestrator()
