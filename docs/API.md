# API Reference

## Base URL

```
http://localhost:8000/api/v1
```

## Endpoints

### Chat

#### POST /chat

Process a query through the RAG system.

**Request Body:**
```json
{
  "query": "What is retrieval-augmented generation?",
  "session_id": "optional-session-id",
  "conversation_history": []  // optional
}
```

**Response:**
```json
{
  "answer": "Retrieval-Augmented Generation (RAG)...",
  "sources": [
    {
      "id": "doc-id",
      "score": 0.95,
      "preview": "..."
    }
  ],
  "metadata": {
    "session_id": "...",
    "query_analysis": {
      "intent": "factual_qa",
      "complexity": "simple",
      "entities": ["RAG"]
    },
    "retrieval": {
      "documents_found": 5,
      "average_score": 0.87
    },
    "confidence": 0.92
  }
}
```

### Documents

#### POST /docs/upload

Upload documents for indexing.

**Request:**
- Content-Type: `multipart/form-data`
- Files: `.txt` or `.md` files

**Response:**
```json
{
  "uploaded": 2,
  "total_chunks": 15,
  "status": "completed",
  "document_ids": ["uuid1", "uuid2", ...]
}
```

#### GET /docs/search

Direct vector search (bypasses agents).

**Parameters:**
- `query` (string): Search query
- `top_k` (int): Number of results (default: 5)

**Response:**
```json
{
  "query": "...",
  "results": [
    {
      "id": "...",
      "text": "...",
      "score": 0.92,
      "metadata": {}
    }
  ]
}
```

### Health

#### GET /health

Basic health check.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-28T19:51:41Z",
  "version": "0.1.0"
}
```

#### GET /health/detailed

Detailed system health.

**Response:**
```json
{
  "api": "healthy",
  "qdrant": {
    "status": "healthy",
    "collection": "documents",
    "documents": 150
  },
  "timestamp": "2025-11-28T19:51:41Z"
}
```

## Usage Examples

### Python (requests)

```python
import requests

# Chat
response = requests.post(
    "http://localhost:8000/api/v1/chat",
    json={"query": "What is RAG?"}
)
print(response.json()["answer"])

# Upload document
with open("doc.txt", "rb") as f:
    requests.post(
        "http://localhost:8000/api/v1/docs/upload",
        files={"files": f}
    )
```

### cURL

```bash
# Chat
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?"}'

# Upload
curl -X POST http://localhost:8000/api/v1/docs/upload \
  -F "files=@document.txt"

# Health
curl http://localhost:8000/api/v1/health
```

## Error Responses

All endpoints return standard HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid input)
- `500`: Internal server error

Error format:
```json
{
  "detail": "Error message here"
}
```
