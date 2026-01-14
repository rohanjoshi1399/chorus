"""
Graph Query Agent (Level 3) - GraphRAG specialist for Neo4j.

Responsibilities:
- Translate natural language to Cypher queries
- Execute graph traversals (1-3 hops)
- Find entity relationships
- Perform community detection
- Combine graph results with vector search
"""

from typing import Any, Dict, List

from .base_agent import AgentInput, AgentOutput, BaseAgent


class GraphQueryAgent(BaseAgent):
    """
    Level 3 specialist for knowledge graph queries and multi-hop reasoning.
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            name="graph_query",
            description="GraphRAG specialist for entity relationships and multi-hop reasoning",
            level=3,
            **kwargs
        )
    
    async def execute(self, input_data: AgentInput) -> AgentOutput:
        """
        Execute graph query for entity relationships.
        
        Query patterns:
        - Local search: Entity + 1-hop neighbors
        - Path finding: Shortest path between entities
        - Multi-hop: Traverse relationships
        - Community: Related concept clusters
        
        Returns:
            Graph substructures and entity relationships
        """
        from ..graph import neo4j_client, cypher_generator
        from ..config import settings
        
        if not settings.graphrag_enabled:
            return AgentOutput(
                result={"entities": [], "relationships": [], "error": "GraphRAG not enabled"},
                metadata={"agent": self.name, "enabled": False},
                confidence_score=0.0
            )
        
        query = input_data.query
        context = input_data.context
        
        # Get entities from query analysis
        analysis = context.get("analysis", {})
        entities = analysis.get("entities", [])
        
        try:
            # Connect to Neo4j
            await neo4j_client.connect()
            
            graph_results = {
                "entities": [],
                "relationships": [],
                "paths": [],
            }
            
            # Strategy 1: If specific entities mentioned, do local search
            if entities:
                for entity_name in entities[:3]:  # Limit to top 3
                    # Search for the entity
                    found_nodes = await neo4j_client.search_nodes(
                        label="Class",  # Try Class first
                        search_term=entity_name,
                        limit=3
                    )
                    
                    if not found_nodes:
                        found_nodes = await neo4j_client.search_nodes(
                            label="Function",
                            search_term=entity_name,
                            limit=3
                        )
                    
                    for node in found_nodes:
                        graph_results["entities"].append(node)
                        
                        # Get neighbors
                        neighbors = await neo4j_client.get_neighbors(
                            node_id=node["id"],
                            limit=10
                        )
                        
                        for neighbor in neighbors:
                            graph_results["relationships"].append({
                                "from": node.get("name"),
                                "to": neighbor.get("name"),
                                "type": neighbor.get("rel_type"),
                            })
            
            # Strategy 2: If multiple entities, find paths
            if len(entities) >= 2:
                path = await neo4j_client.get_path(
                    from_name=entities[0],
                    to_name=entities[1],
                    max_hops=settings.graph_max_hop_depth
                )
                if path:
                    graph_results["paths"].append(path)
            
            # Strategy 3: Generate and execute custom Cypher
            if not graph_results["entities"] and not entities:
                # LLM-generated query
                cypher_result = await cypher_generator.generate_cypher(query)
                
                if "error" not in cypher_result:
                    try:
                        query_results = await neo4j_client.execute_query(
                            cypher_result["query"]
                        )
                        graph_results["custom_query"] = {
                            "cypher": cypher_result["query"],
                            "explanation": cypher_result.get("explanation", ""),
                            "results": query_results[:10],
                        }
                    except Exception:
                        pass
            
            # Calculate confidence based on results
            total_results = (
                len(graph_results["entities"]) +
                len(graph_results["relationships"]) +
                len(graph_results["paths"])
            )
            confidence = min(1.0, total_results / 10) if total_results > 0 else 0.0
            
        except Exception as e:
            graph_results = {
                "entities": [],
                "relationships": [],
                "paths": [],
                "error": str(e),
            }
            confidence = 0.0
        
        return AgentOutput(
            result=graph_results,
            metadata={
                "agent": self.name,
                "retrieval_strategy": "graph",
                "entities_queried": entities,
            },
            confidence_score=confidence
        )
