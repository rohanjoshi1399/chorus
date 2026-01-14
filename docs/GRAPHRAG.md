# GraphRAG Guide

## Overview

GraphRAG integration using Neo4j for knowledge graph-based retrieval with multi-hop reasoning.

---

## Entity Types

| Entity | Description | Properties |
|--------|-------------|------------|
| Module | Python module/package | name, description, version |
| Class | Python class | name, description, methods, attributes |
| Function | Function/method | name, description, parameters, returns |
| Concept | Technical concept | name, description, category |
| API | REST/SDK endpoint | name, endpoint, method, description |

---

## Relationships

| Relationship | From | To | Description |
|--------------|------|-----|-------------|
| CONTAINS | Module | Class/Function | Ownership |
| INHERITS | Class | Class | Inheritance |
| CALLS | Function | Function | Invocation |
| RETURNS | Function | Class | Return type |
| USES | Entity | Entity | Dependency |
| IMPLEMENTS | Class | Concept | Pattern usage |

---

## Schema Setup

```cypher
// Create indexes
CREATE INDEX FOR (n:Module) ON (n.name);
CREATE INDEX FOR (n:Class) ON (n.name);
CREATE INDEX FOR (n:Function) ON (n.name);
CREATE INDEX FOR (n:Concept) ON (n.name);
CREATE INDEX FOR (n:API) ON (n.name);

// Create constraints
CREATE CONSTRAINT FOR (n:Module) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT FOR (n:Class) REQUIRE n.name IS UNIQUE;
```

---

## Query Patterns

### Local Search
```cypher
MATCH (e:Entity)
WHERE toLower(e.name) CONTAINS toLower($query)
RETURN e LIMIT 10
```

### Path Finding
```cypher
MATCH path = shortestPath((a:Entity)-[*..5]-(b:Entity))
WHERE a.name = $entity1 AND b.name = $entity2
RETURN path
```

### Community Detection
```cypher
MATCH (e:Entity)-[r]-(related:Entity)
WHERE e.name = $entity
RETURN e, r, related
```

---

## Entity Extraction

The system extracts entities using:
1. **LLM-based extraction**: Structured prompts for entity identification
2. **Regex patterns**: Code-specific patterns for classes, functions, imports

```python
# Example extraction
entities = await entity_extractor.extract(document_text)
# Returns: [Entity(type="Class", name="StateGraph", ...)]
```

---

## Usage in Queries

When a query involves:
- Multiple related concepts → Graph traversal
- "How does X relate to Y" → Path finding
- Technical dependencies → Relationship queries

The Router agent determines when to invoke GraphRAG based on query complexity.
