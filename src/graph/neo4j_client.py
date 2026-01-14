"""
Neo4j client for GraphRAG knowledge graph.

Provides:
- Connection management
- Graph schema management
- Cypher query execution
- Entity and relationship operations
"""

from typing import List, Dict, Any, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver
import json

from ..config import settings


class Neo4jClient:
    """
    Async Neo4j client for knowledge graph operations.
    """
    
    def __init__(self):
        """Initialize Neo4j connection."""
        self._driver: Optional[AsyncDriver] = None
    
    async def connect(self) -> None:
        """Establish connection to Neo4j."""
        if self._driver is None:
            self._driver = AsyncGraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
            )
            # Verify connectivity
            await self._driver.verify_connectivity()
            print(f"✅ Connected to Neo4j at {settings.neo4j_uri}")
    
    async def close(self) -> None:
        """Close Neo4j connection."""
        if self._driver:
            await self._driver.close()
            self._driver = None
    
    async def _get_session(self):
        """Get an async session."""
        if self._driver is None:
            await self.connect()
        return self._driver.session()
    
    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        async with await self._get_session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records
    
    async def create_node(
        self,
        label: str,
        properties: Dict[str, Any],
    ) -> str:
        """
        Create a node in the graph.
        
        Args:
            label: Node label (e.g., 'Class', 'Function', 'Module')
            properties: Node properties
            
        Returns:
            Node ID
        """
        query = f"""
        CREATE (n:{label} $props)
        RETURN elementId(n) as id
        """
        result = await self.execute_query(query, {"props": properties})
        return result[0]["id"] if result else None
    
    async def create_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Create a relationship between two nodes.
        
        Args:
            from_id: Source node ID
            to_id: Target node ID
            rel_type: Relationship type (e.g., 'CONTAINS', 'CALLS', 'INHERITS')
            properties: Optional relationship properties
        """
        query = f"""
        MATCH (a), (b)
        WHERE elementId(a) = $from_id AND elementId(b) = $to_id
        CREATE (a)-[r:{rel_type} $props]->(b)
        """
        await self.execute_query(
            query,
            {"from_id": from_id, "to_id": to_id, "props": properties or {}}
        )
    
    async def find_node(
        self,
        label: str,
        name: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Find a node by label and name.
        
        Args:
            label: Node label
            name: Node name property
            
        Returns:
            Node data or None
        """
        query = f"""
        MATCH (n:{label} {{name: $name}})
        RETURN n, elementId(n) as id
        LIMIT 1
        """
        result = await self.execute_query(query, {"name": name})
        if result:
            return {"id": result[0]["id"], **dict(result[0]["n"])}
        return None
    
    async def get_neighbors(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Get neighboring nodes.
        
        Args:
            node_id: Node ID
            relationship_type: Optional filter by relationship type
            direction: 'in', 'out', or 'both'
            limit: Maximum neighbors to return
            
        Returns:
            List of neighbor nodes with relationship info
        """
        rel_pattern = f":{relationship_type}" if relationship_type else ""
        
        if direction == "out":
            query = f"""
            MATCH (a)-[r{rel_pattern}]->(b)
            WHERE elementId(a) = $node_id
            RETURN b, type(r) as rel_type, elementId(b) as id
            LIMIT $limit
            """
        elif direction == "in":
            query = f"""
            MATCH (a)<-[r{rel_pattern}]-(b)
            WHERE elementId(a) = $node_id
            RETURN b, type(r) as rel_type, elementId(b) as id
            LIMIT $limit
            """
        else:
            query = f"""
            MATCH (a)-[r{rel_pattern}]-(b)
            WHERE elementId(a) = $node_id
            RETURN b, type(r) as rel_type, elementId(b) as id
            LIMIT $limit
            """
        
        results = await self.execute_query(query, {"node_id": node_id, "limit": limit})
        return [
            {"id": r["id"], "rel_type": r["rel_type"], **dict(r["b"])}
            for r in results
        ]
    
    async def search_nodes(
        self,
        label: str,
        search_term: str,
        property_name: str = "name",
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search nodes by property using fuzzy matching.
        
        Args:
            label: Node label to search
            search_term: Search term
            property_name: Property to search
            limit: Max results
            
        Returns:
            Matching nodes
        """
        query = f"""
        MATCH (n:{label})
        WHERE toLower(n.{property_name}) CONTAINS toLower($term)
        RETURN n, elementId(n) as id
        LIMIT $limit
        """
        results = await self.execute_query(query, {"term": search_term, "limit": limit})
        return [{"id": r["id"], **dict(r["n"])} for r in results]
    
    async def get_path(
        self,
        from_name: str,
        to_name: str,
        max_hops: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Find shortest path between two entities.
        
        Args:
            from_name: Source entity name
            to_name: Target entity name
            max_hops: Maximum path length
            
        Returns:
            Path as list of nodes and relationships
        """
        query = f"""
        MATCH path = shortestPath((a)-[*1..{max_hops}]-(b))
        WHERE a.name = $from_name AND b.name = $to_name
        RETURN [node in nodes(path) | node.name] as nodes,
               [rel in relationships(path) | type(rel)] as relationships
        LIMIT 1
        """
        result = await self.execute_query(
            query,
            {"from_name": from_name, "to_name": to_name}
        )
        if result:
            return {
                "nodes": result[0]["nodes"],
                "relationships": result[0]["relationships"],
            }
        return None
    
    async def init_schema(self) -> None:
        """
        Initialize graph schema with indexes and constraints.
        """
        # Create indexes for common lookups
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (n:Module) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Class) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Function) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Concept) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:API) ON (n.name)",
        ]
        
        for idx in indexes:
            await self.execute_query(idx)
        
        print("✅ Neo4j schema initialized")


# Global Neo4j client
neo4j_client = Neo4jClient()
