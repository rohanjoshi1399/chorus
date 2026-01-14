"""
Entity extraction from documents for knowledge graph.

Extracts:
- Modules, Classes, Functions, APIs
- Concepts and technical terms
- Relationships between entities
"""

from typing import List, Dict, Any, Tuple
import json
import re

from ..llm import bedrock_client


class EntityExtractor:
    """
    LLM-based entity extraction for building knowledge graphs.
    """
    
    # Entity types to extract
    ENTITY_TYPES = [
        "Module",     # Python modules, packages
        "Class",      # Classes and types
        "Function",   # Functions and methods
        "API",        # API endpoints, services
        "Concept",    # Technical concepts
    ]
    
    # Relationship types
    RELATIONSHIP_TYPES = [
        "CONTAINS",   # Module contains class
        "INHERITS",   # Class inherits from class
        "CALLS",      # Function calls function
        "USES",       # Entity uses another entity
        "IMPLEMENTS", # Implements interface/protocol
        "RETURNS",    # Function returns type
        "RELATED_TO", # General relationship
    ]
    
    async def extract_entities(
        self,
        text: str,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract entities from document text.
        
        Args:
            text: Document text
            doc_metadata: Optional document metadata
            
        Returns:
            List of extracted entities
        """
        extraction_prompt = f"""Extract technical entities from this documentation.

Text:
{text[:2000]}

Extract entities of these types: Module, Class, Function, API, Concept

Return a JSON array of entities:
[
  {{"type": "Class", "name": "EntityName", "description": "brief description"}},
  ...
]

Return ONLY the JSON array."""

        try:
            result = await bedrock_client.generate(
                prompt=extraction_prompt,
                system_prompt="You are a technical documentation parser. Extract entities accurately. Return only valid JSON.",
                temperature=0.1,
            )
            
            entities = json.loads(result.strip())
            
            # Add source metadata
            for entity in entities:
                entity["source"] = doc_metadata.get("filename", "unknown") if doc_metadata else "unknown"
            
            return entities
            
        except Exception as e:
            return []
    
    async def extract_relationships(
        self,
        text: str,
        entities: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Extract relationships between entities.
        
        Args:
            text: Document text
            entities: Previously extracted entities
            
        Returns:
            List of relationships
        """
        entity_names = [e["name"] for e in entities[:20]]  # Limit for prompt
        
        if len(entity_names) < 2:
            return []
        
        relationship_prompt = f"""Given these entities from technical documentation, identify relationships between them.

Entities: {', '.join(entity_names)}

Text context:
{text[:1500]}

Relationship types: CONTAINS, INHERITS, CALLS, USES, IMPLEMENTS, RETURNS, RELATED_TO

Return a JSON array of relationships:
[
  {{"from": "EntityA", "to": "EntityB", "type": "CALLS"}},
  ...
]

Return ONLY the JSON array."""

        try:
            result = await bedrock_client.generate(
                prompt=relationship_prompt,
                system_prompt="You are a code relationship analyzer. Return only valid JSON.",
                temperature=0.1,
            )
            
            relationships = json.loads(result.strip())
            return relationships
            
        except Exception as e:
            return []
    
    def extract_code_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Rule-based extraction of code entities using regex.
        
        Faster than LLM for common patterns.
        
        Args:
            text: Code or documentation text
            
        Returns:
            Extracted entities
        """
        entities = []
        
        # Python class patterns
        class_pattern = r'class\s+(\w+)(?:\(([^)]*)\))?:'
        for match in re.finditer(class_pattern, text):
            entities.append({
                "type": "Class",
                "name": match.group(1),
                "inherits": match.group(2) if match.group(2) else None,
            })
        
        # Python function patterns
        func_pattern = r'(?:async\s+)?def\s+(\w+)\s*\([^)]*\)'
        for match in re.finditer(func_pattern, text):
            name = match.group(1)
            if not name.startswith('_'):  # Skip private methods
                entities.append({
                    "type": "Function",
                    "name": name,
                })
        
        # Import patterns for modules
        import_pattern = r'(?:from|import)\s+([\w.]+)'
        for match in re.finditer(import_pattern, text):
            module = match.group(1).split('.')[0]
            if module not in [e["name"] for e in entities]:
                entities.append({
                    "type": "Module",
                    "name": module,
                })
        
        return entities


# Type hint for optional import
from typing import Optional

# Global entity extractor
entity_extractor = EntityExtractor()
