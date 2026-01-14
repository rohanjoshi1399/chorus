"""
Cypher query generator using LLM.

Translates natural language queries to Neo4j Cypher queries.
"""

from typing import Optional, Dict, Any
import json

from ..llm import bedrock_client


class CypherGenerator:
    """
    LLM-based natural language to Cypher translation.
    """
    
    # Graph schema for context
    SCHEMA = """
    Node Types:
    - Module (name, description, version)
    - Class (name, description, methods, attributes)
    - Function (name, description, parameters, returns)
    - API (name, endpoint, method, description)
    - Concept (name, description, category)
    
    Relationship Types:
    - CONTAINS: (Module)-[:CONTAINS]->(Class|Function)
    - INHERITS: (Class)-[:INHERITS]->(Class)
    - CALLS: (Function)-[:CALLS]->(Function)
    - USES: (Entity)-[:USES]->(Entity)
    - IMPLEMENTS: (Class)-[:IMPLEMENTS]->(Concept)
    - RETURNS: (Function)-[:RETURNS]->(Class)
    - RELATED_TO: (Entity)-[:RELATED_TO]->(Entity)
    """
    
    async def generate_cypher(
        self,
        question: str,
        entities: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Generate Cypher query from natural language.
        
        Args:
            question: Natural language question
            entities: Optional list of known entities to reference
            
        Returns:
            Dict with 'query' (Cypher) and 'explanation'
        """
        entity_context = ""
        if entities:
            entity_context = f"\nKnown entities: {', '.join(entities[:10])}"
        
        prompt = f"""Generate a Neo4j Cypher query to answer this question.

Question: "{question}"

Graph Schema:
{self.SCHEMA}
{entity_context}

Return JSON with:
{{
    "query": "MATCH ... RETURN ...",
    "explanation": "What this query does",
    "return_fields": ["field1", "field2"]
}}

Rules:
- Use MATCH for finding nodes/relationships
- Use WHERE for filtering
- Limit results to 20 max
- Use toLower() for case-insensitive matching
- Return node properties, not entire nodes

Return ONLY valid JSON."""

        try:
            result = await bedrock_client.generate(
                prompt=prompt,
                system_prompt="You are a Neo4j Cypher expert. Generate accurate queries. Return only valid JSON.",
                temperature=0.1,
            )
            
            return json.loads(result.strip())
            
        except Exception as e:
            # Fallback: simple search query
            return {
                "query": f"MATCH (n) WHERE toLower(n.name) CONTAINS toLower('{question.split()[0]}') RETURN n LIMIT 10",
                "explanation": "Fallback search query",
                "error": str(e),
            }
    
    def generate_local_search(self, entity_name: str, entity_type: str = None) -> str:
        """
        Generate query for local entity search with neighbors.
        
        Args:
            entity_name: Entity to search for
            entity_type: Optional type filter
            
        Returns:
            Cypher query string
        """
        if entity_type:
            return f"""
            MATCH (n:{entity_type})-[r]-(neighbor)
            WHERE toLower(n.name) = toLower('{entity_name}')
            RETURN n, type(r) as relationship, neighbor
            LIMIT 20
            """
        else:
            return f"""
            MATCH (n)-[r]-(neighbor)
            WHERE toLower(n.name) = toLower('{entity_name}')
            RETURN n, labels(n) as type, type(r) as relationship, neighbor
            LIMIT 20
            """
    
    def generate_path_query(self, from_entity: str, to_entity: str, max_hops: int = 3) -> str:
        """
        Generate shortest path query between entities.
        """
        return f"""
        MATCH path = shortestPath((a)-[*1..{max_hops}]-(b))
        WHERE toLower(a.name) = toLower('{from_entity}')
          AND toLower(b.name) = toLower('{to_entity}')
        RETURN [node in nodes(path) | node.name] as path_nodes,
               [rel in relationships(path) | type(rel)] as path_rels,
               length(path) as hops
        LIMIT 5
        """
    
    def generate_community_query(self, entity_name: str, depth: int = 2) -> str:
        """
        Generate query to find related community of entities.
        """
        return f"""
        MATCH (start)-[*1..{depth}]-(related)
        WHERE toLower(start.name) = toLower('{entity_name}')
        WITH DISTINCT related
        RETURN labels(related)[0] as type, related.name as name, related.description as description
        LIMIT 30
        """


# Global Cypher generator
cypher_generator = CypherGenerator()
