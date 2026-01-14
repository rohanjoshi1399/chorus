"""
Web Search Agent (Level 3) - Real-time information specialist.

Responsibilities:
- Execute web searches for time-sensitive queries
- Scrape and parse search result content
- Filter low-quality sources
- Extract relevant snippets
- Cache results
"""

from typing import Any, Dict, List, Optional
import json

from .base_agent import AgentInput, AgentOutput, BaseAgent


class WebSearchAgent(BaseAgent):
    """
    Level 3 specialist for real-time web information retrieval.
    
    Supports:
    - Tavily Search API (recommended for RAG)
    - SerpAPI (Google search)
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="web_search",
            description="Real-time web search specialist",
            level=3,
            **kwargs
        )
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute web search and extract relevant information.
        
        Activation conditions:
        - Time-sensitive queries ("latest", "recent", "current")
        - Low vector DB relevance (< 0.7)
        - Explicit web search request
        
        Returns:
            Web search results with credibility scores
        """
        from ..config import settings
        
        if not settings.web_search_enabled:
            return AgentOutput(
                result={"results": [], "error": "Web search not enabled"},
                metadata={"agent": self.name, "enabled": False},
                confidence_score=0.0
            )
        
        query = input_data.query
        context = input_data.context
        
        # Determine which API to use
        results = []
        search_api = "none"
        
        try:
            if settings.tavily_api_key:
                results = await self._tavily_search(query, settings.tavily_api_key)
                search_api = "tavily"
            elif settings.serpapi_api_key:
                results = await self._serpapi_search(query, settings.serpapi_api_key)
                search_api = "serpapi"
            else:
                return AgentOutput(
                    result={"results": [], "error": "No web search API configured"},
                    metadata={"agent": self.name},
                    confidence_score=0.0
                )
            
            # Filter and score results
            scored_results = self._score_credibility(results)
            
            # Calculate confidence
            if scored_results:
                avg_credibility = sum(r.get("credibility", 0.5) for r in scored_results) / len(scored_results)
                confidence = min(1.0, avg_credibility)
            else:
                confidence = 0.0
            
        except Exception as e:
            scored_results = []
            confidence = 0.0
            search_api = "error"
        
        return AgentOutput(
            result={
                "results": scored_results,
                "query": query,
                "api_used": search_api,
            },
            metadata={
                "agent": self.name,
                "retrieval_strategy": "web",
                "result_count": len(scored_results),
            },
            confidence_score=confidence
        )
    
    async def _tavily_search(self, query: str, api_key: str) -> List[Dict[str, Any]]:
        """
        Search using Tavily API (optimized for RAG).
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": api_key,
                    "query": query,
                    "search_depth": "advanced",
                    "include_answer": True,
                    "include_raw_content": False,
                    "max_results": 5,
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                data = response.json()
                
                results = []
                
                # Add Tavily's synthesized answer if available
                if data.get("answer"):
                    results.append({
                        "title": "Tavily Summary",
                        "content": data["answer"],
                        "url": "tavily://summary",
                        "source": "tavily_answer",
                    })
                
                # Add individual results
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "content": item.get("content", ""),
                        "url": item.get("url", ""),
                        "source": "web",
                        "score": item.get("score", 0.5),
                    })
                
                return results
            
            return []
    
    async def _serpapi_search(self, query: str, api_key: str) -> List[Dict[str, Any]]:
        """
        Search using SerpAPI (Google).
        """
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://serpapi.com/search",
                params={
                    "api_key": api_key,
                    "q": query,
                    "engine": "google",
                    "num": 5,
                },
                timeout=30.0,
            )
            
            if response.status_code == 200:
                data = response.json()
                
                results = []
                for item in data.get("organic_results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "content": item.get("snippet", ""),
                        "url": item.get("link", ""),
                        "source": "google",
                        "position": item.get("position", 0),
                    })
                
                return results
            
            return []
    
    def _score_credibility(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Score result credibility based on source.
        """
        # High credibility domains
        HIGH_CREDIBILITY = [
            "docs.python.org",
            "aws.amazon.com",
            "langchain.com",
            "microsoft.com",
            "github.com",
            "stackoverflow.com",
            "developer.mozilla.org",
        ]
        
        MEDIUM_CREDIBILITY = [
            "medium.com",
            "dev.to",
            "towardsdatascience.com",
            "realpython.com",
        ]
        
        for result in results:
            url = result.get("url", "").lower()
            
            if any(domain in url for domain in HIGH_CREDIBILITY):
                result["credibility"] = 0.9
            elif any(domain in url for domain in MEDIUM_CREDIBILITY):
                result["credibility"] = 0.7
            elif result.get("source") == "tavily_answer":
                result["credibility"] = 0.85
            else:
                result["credibility"] = 0.5
        
        # Sort by credibility
        return sorted(results, key=lambda x: x.get("credibility", 0), reverse=True)
