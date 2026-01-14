# Multi-Agent RAG System Architecture

> Comprehensive technical architecture documentation for the 8-agent hierarchical RAG system.

## Table of Contents

1. [System Overview](#system-overview)
2. [Agent Architecture](#agent-architecture)
3. [Data Flow](#data-flow)
4. [Database Schemas](#database-schemas)
5. [Retrieval Pipeline](#retrieval-pipeline)
6. [Deployment Architecture](#deployment-architecture)
7. [API Design](#api-design)

---

## System Overview

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web UI]
        WS[WebSocket Client]
        REST[REST Client]
    end
    
    subgraph "API Layer"
        ALB[AWS ALB]
        API[FastAPI Server]
        WSH[WebSocket Handler]
    end
    
    subgraph "Agent Layer"
        ORCH[Supervisor Orchestrator]
        L2[Level 2 Agents]
        L3[Level 3 Agents]
    end
    
    subgraph "Data Layer"
        QDRANT[(Qdrant)]
        NEO4J[(Neo4j)]
        REDIS[(Redis)]
    end
    
    subgraph "External"
        BEDROCK[AWS Bedrock]
        TAVILY[Tavily API]
        COHERE[Cohere Rerank]
    end
    
    WEB & WS & REST --> ALB
    ALB --> API & WSH
    API & WSH --> ORCH
    ORCH --> L2 --> L3
    L3 --> QDRANT & NEO4J
    ORCH --> REDIS
    L2 & L3 --> BEDROCK
    L3 --> TAVILY
    L3 --> COHERE
```

### Technology Matrix

| Component | Technology | Purpose |
|-----------|------------|---------|
| LLM | Claude 4.5 Sonnet (Bedrock) | Generation, analysis |
| Embeddings | Titan Embeddings V2 | Dense vectors |
| Orchestration | LangGraph StateGraph | Agent workflow |
| Vector Store | Qdrant | Semantic search |
| Graph Store | Neo4j | Entity relationships |
| Cache/Memory | Redis | Session state |
| API | FastAPI | REST + WebSocket |
| Reranking | BGE-Reranker-Large | Cross-encoder scoring |

---

## Agent Architecture

### Hierarchical Agent System

```mermaid
graph TD
    subgraph "Level 1 - Orchestration"
        SUP[Supervisor<br/>LangGraph StateGraph]
    end
    
    subgraph "Level 2 - Analysis & Processing"
        QA[Query Analyzer<br/>Intent + Entities]
        RT[Router<br/>Strategy Selection]
        QRW[Query Rewriter<br/>Result Grading]
        VAL[Validator<br/>Fact Checking]
        SYN[Synthesis<br/>Response Gen]
    end
    
    subgraph "Level 3 - Specialists"
        RET[Retrieval Agent<br/>Hybrid Search]
        GQ[Graph Query<br/>Neo4j Cypher]
        WS[Web Search<br/>Tavily/SerpAPI]
    end
    
    SUP --> QA --> RT
    RT --> RET & GQ & WS
    RET & GQ & WS --> QRW
    QRW --> |rewrite| RET
    QRW --> |continue| VAL
    VAL --> SYN
```

### Agent Specifications

#### Level 1: Supervisor Orchestrator

```python
# LangGraph Workflow Definition
workflow = StateGraph(AgentState)
workflow.add_node("supervisor", _supervisor_node)
workflow.add_node("query_analyzer", _query_analyzer_node)
workflow.add_node("router", _router_node)
workflow.add_node("multi_retrieval", _multi_retrieval_node)
workflow.add_node("grade_results", _grade_results_node)
workflow.add_node("rewrite_query", _rewrite_query_node)
workflow.add_node("validator", _validator_node)
workflow.add_node("synthesis", _synthesis_node)

# Conditional edges for query rewrite loop
workflow.add_conditional_edges(
    "grade_results",
    _should_rewrite,
    {"rewrite": "rewrite_query", "continue": "validator"}
)
```

#### Level 2: Query Analyzer

| Output Field | Type | Description |
|--------------|------|-------------|
| intent | string | factual_qa, comparison, explanation, etc. |
| entities | list[str] | Extracted technical terms |
| complexity | string | simple, moderate, multi_hop |
| time_sensitive | bool | Requires current information |
| requires_code | bool | Code examples needed |

#### Level 2: Router Agent

**Routing Decision Tree:**

```
IF entities > 1 AND complexity in (moderate, multi_hop):
    strategies = [graph, vector]
ELIF time_sensitive:
    strategies = [web, vector]
ELIF requires_code:
    strategies = [vector]
ELIF complexity == multi_hop:
    strategies = [vector, graph]
ELSE:
    strategies = [vector]
```

#### Level 2: Query Rewriter

**Query Rewrite Loop (Max 2 attempts):**

```mermaid
flowchart LR
    A[Retrieve Docs] --> B{Grade Results}
    B -->|score < 0.7| C[Rewrite Query]
    C --> A
    B -->|score >= 0.7| D[Continue to Validator]
    B -->|max attempts| D
```

---

## Data Flow

### Query Processing Pipeline

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI
    participant SUP as Supervisor
    participant QA as Query Analyzer
    participant RT as Router
    participant RET as Retrieval
    participant GRD as Grader
    participant VAL as Validator
    participant SYN as Synthesis
    
    U->>API: POST /chat or WebSocket
    API->>SUP: process_query()
    SUP->>QA: Analyze intent
    QA-->>SUP: {intent, entities, complexity}
    SUP->>RT: Route strategies
    RT-->>SUP: [vector, graph, web]
    
    par Parallel Retrieval
        SUP->>RET: Vector search
        SUP->>RET: Graph query
        SUP->>RET: Web search
    end
    
    RET-->>SUP: Documents
    SUP->>GRD: Grade relevance
    
    alt Poor Results
        GRD-->>SUP: Rewrite needed
        SUP->>RET: Retry with new query
    end
    
    GRD-->>SUP: Results OK
    SUP->>VAL: Validate facts
    VAL-->>SUP: Validation report
    SUP->>SYN: Generate response
    SYN-->>SUP: Answer + Sources
    SUP-->>API: Response
    API-->>U: JSON/WebSocket
```

### Agent State Schema

```python
class AgentState(TypedDict):
    # Core
    query: str
    original_query: str
    session_id: Optional[str]
    
    # Analysis
    analysis: Dict[str, Any]  # Query analyzer output
    strategies: List[str]     # Router decisions
    
    # Retrieval
    retrieved_documents: List[Dict]
    graph_results: Optional[Dict]
    web_results: Optional[Dict]
    
    # Quality Loop
    grading: Dict[str, Any]
    rewrite_count: int
    rewritten_query: Optional[str]
    
    # Validation
    validation: Dict[str, Any]
    confidence: float
    
    # Output
    response: str
    sources: List[Dict]
    agent_trace: List[str]
```

---

## Database Schemas

### Qdrant Vector Store

```yaml
Collection: documents
  Vectors:
    size: 1024  # Titan Embeddings V2
    distance: Cosine
    
  Payload Schema:
    - id: string (UUID)
    - text: string (chunk content)
    - doc_id: string (parent document)
    - chunk_index: int
    - cohesion_score: float (semantic chunker)
    - source_type: string (vector|graph|web)
    
  Indexes:
    - doc_id (keyword)
    - source_type (keyword)
    
  HNSW Config:
    m: 16
    ef_construct: 128
```

### Neo4j Graph Schema

```mermaid
erDiagram
    Module ||--o{ Class : CONTAINS
    Module ||--o{ Function : CONTAINS
    Class ||--o{ Function : CONTAINS
    Class ||--o{ Class : INHERITS
    Function ||--o{ Function : CALLS
    Function ||--o{ Class : RETURNS
    Class ||--o{ Concept : IMPLEMENTS
    Entity ||--o{ Entity : RELATED_TO
    Entity ||--o{ Entity : USES
    
    Module {
        string name PK
        string description
        string version
    }
    
    Class {
        string name PK
        string description
        string[] methods
        string[] attributes
    }
    
    Function {
        string name PK
        string description
        string[] parameters
        string returns
    }
    
    Concept {
        string name PK
        string description
        string category
    }
    
    API {
        string name PK
        string endpoint
        string method
        string description
    }
```

**Neo4j Indexes:**
```cypher
CREATE INDEX FOR (n:Module) ON (n.name);
CREATE INDEX FOR (n:Class) ON (n.name);
CREATE INDEX FOR (n:Function) ON (n.name);
CREATE INDEX FOR (n:Concept) ON (n.name);
CREATE INDEX FOR (n:API) ON (n.name);
```

### Redis Memory Schema

```yaml
Keys:
  conversation:{session_id}:
    type: LIST
    ttl: 86400 (24h)
    format: JSON messages
    
  Message Format:
    - role: string (user|assistant)
    - content: string
    - timestamp: ISO8601
    - metadata: object
    
Commands:
  - RPUSH: Add message
  - LRANGE: Get history
  - LTRIM: Limit to N messages
  - EXPIRE: Set TTL
```

---

## Retrieval Pipeline

### Hybrid Search Architecture

```mermaid
flowchart TB
    Q[Query] --> EMB[Titan Embeddings]
    Q --> TOK[BM25 Tokenizer]
    
    EMB --> VS[Vector Search<br/>Qdrant]
    TOK --> BM[BM25 Search<br/>In-Memory]
    
    VS --> RRF[Reciprocal Rank Fusion]
    BM --> RRF
    
    RRF --> CAND[Candidates<br/>Top 50]
    
    CAND --> BGE[BGE Cross-Encoder]
    BGE --> TOP[Final Top 5]
```

### Semantic Chunking (Max-Min Algorithm)

```python
# 1. Embed all sentences
embeddings = await embed_sentences(sentences)

# 2. Cluster by similarity
for sentence in sentences[1:]:
    max_sim = max(cos_sim(sentence, chunk) for chunk in current_chunk)
    
    if max_sim >= threshold and len(chunk) < max_size:
        # Merge into current chunk
        current_chunk.append(sentence)
    else:
        # Start new chunk
        chunks.append(current_chunk)
        current_chunk = [sentence]

# 3. Calculate cohesion scores
for chunk in chunks:
    chunk.cohesion = mean(pairwise_similarities(chunk))
```

### Reranking Strategy

| Stage | Model | Candidates | Output |
|-------|-------|------------|--------|
| 1. Initial | Bi-encoder | All docs | Top 50 |
| 2. Rerank | BGE Cross-encoder | Top 50 | Top 5 |
| 3. Fallback | Cohere API | (if BGE fails) | Top 5 |

---

## Deployment Architecture

### AWS EKS Topology

```mermaid
graph TB
    subgraph "VPC (10.0.0.0/16)"
        subgraph "Public Subnets"
            ALB[Application LB]
            NAT[NAT Gateway]
        end
        
        subgraph "Private Subnets"
            subgraph "EKS Cluster"
                API1[API Pod 1]
                API2[API Pod 2]
                QDRANT[Qdrant StatefulSet]
                REDIS[Redis Pod]
            end
        end
    end
    
    BEDROCK[AWS Bedrock] -.-> API1 & API2
    NEO4J[Neo4j Aura] -.-> API1 & API2
    
    USERS[Users] --> ALB
    ALB --> API1 & API2
    API1 & API2 --> QDRANT & REDIS
    API1 & API2 --> NAT --> BEDROCK & NEO4J
```

### Kubernetes Resources

| Resource | Replicas | CPU | Memory |
|----------|----------|-----|--------|
| API Deployment | 2-10 (HPA) | 250m-1000m | 512Mi-2Gi |
| Qdrant StatefulSet | 1 | 500m-2000m | 1Gi-4Gi |
| Redis Deployment | 1 | 100m-500m | 256Mi-1Gi |

### Horizontal Pod Autoscaler

```yaml
metrics:
  - cpu: 70% target
  - memory: 80% target
behavior:
  scaleUp:
    stabilizationWindow: 60s
    maxPods: 2 per 60s
  scaleDown:
    stabilizationWindow: 300s
    maxPods: 1 per 120s
```

---

## API Design

### REST Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Synchronous query |
| POST | `/api/v1/docs/upload` | Document ingestion |
| GET | `/api/v1/docs/search` | Direct vector search |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/health/detailed` | Component status |

### WebSocket Protocol

```json
// Client → Server
{"type": "chat.message", "session_id": "...", "message": "..."}

// Server → Client (progress)
{"type": "agent.thinking", "agent": "query_analyzer", "message": "..."}
{"type": "retrieval.progress", "count": 5}

// Server → Client (response)
{
  "type": "message.complete",
  "answer": "...",
  "sources": [...],
  "metadata": {
    "agent_trace": ["supervisor", "query_analyzer", ...],
    "confidence": 0.92
  }
}
```

---

## Evaluation Metrics

### RAG Quality Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Precision@K | relevant_in_topK / K | ≥ 0.90 |
| Recall@K | relevant_in_topK / total_relevant | ≥ 0.85 |
| MRR | 1 / first_relevant_rank | ≥ 0.80 |
| Faithfulness | LLM-judge grounding score | ≥ 0.95 |
| Answer Relevancy | LLM-judge query match | ≥ 0.90 |

### Evaluation Pipeline

```python
result = await rag_evaluator.evaluate(
    query="How does LangGraph handle state?",
    answer=generated_answer,
    retrieved_docs=docs,
    relevant_doc_ids=ground_truth_ids,
)

# Returns: precision@5, recall@10, mrr, faithfulness, answer_relevancy
```

---

## Security Considerations

1. **API Authentication**: JWT tokens via AWS Cognito
2. **Secrets Management**: Kubernetes Secrets + AWS Secrets Manager
3. **Network Policy**: Ingress/Egress rules per namespace
4. **RBAC**: Qdrant metadata filtering for multi-tenancy
5. **Data Encryption**: TLS in transit, EBS encryption at rest
