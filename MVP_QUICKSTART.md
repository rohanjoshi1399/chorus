# MVP Quick Start Guide

## 🚀 Getting Started

###  1. Install Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install with Poetry
poetry install

# OR with pip
pip install langchain langchain-aws langchain-community langgraph boto3 qdrant-client fastapi uvicorn redis pydantic-settings python-dotenv
```

### 2. Configure Environment

Create `.env` file from template and add your AWS credentials:

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux
```

Edit `.env`:
```
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
NEO4J_PASSWORD=your_password_here
```

### 3. Start Services

```bash
docker-compose up -d

# Verify services
docker-compose ps
```

### 4. Ingest Sample Documents

Create some sample documents in a local folder (e.g., `./my_docs/`) then:

```bash
python -m scripts.ingest_documents ./my_docs
```

### 5. Test the MVP

```bash
python examples/simple_chat.py "What is retrieval-augmented generation?"
```

## 📋 Sample Document

Create `my_docs/rag_basics.md`:

```markdown
# Retrieval-Augmented Generation (RAG)

RAG combines information retrieval with LLM generation. Key components:
- Vector Database for embeddings
- Retriever for finding relevant documents
- Generator (LLM) for producing responses

Benefits include factual accuracy, up-to-date information, and reduced hallucinations.
```

## 🎯 What's Working (MVP - Phase 1)

✅ **3-Agent System**:
- Query Analyzer (Claude-powered intent analysis)
- Retrieval Agent (Qdrant vector search)
- Synthesis Agent (LLM response generation)

✅ **Core Infrastructure**:
- AWS Bedrock (Claude 4.5 Sonnet + Titan Embeddings)
- Qdrant Vector Database
- Configuration management
- Document ingestion pipeline

✅ **Example Usage**:
- Simple chat interface
- Document ingestion script

## 🔄 Next Steps

**Phase 2** - Full 8-agent system:
- Router Agent for strategy selection
- Validation Agent for fact-checking
- Add GraphRAG (Neo4j)
- Add Web Search Agent

**Phase 3** - Production:
- WebSocket streaming
- REST API endpoints
- AWS EKS deployment

## 🐛 Troubleshooting

**"No documents found" error**:
- Make sure you've run `scripts/ingest_documents.py`
- Verify Qdrant is running: `docker-compose ps`

**AWS Bedrock errors**:
- Check AWS credentials in `.env`
- Ensure Claude 4.5 Sonnet access is enabled in AWS Console

**Import errors**:
- Ensure you're in the project root directory
- Check virtual environment is activated

## 📚 Files Created

```
src/
├── config.py                    # Configuration management
├── llm/
│   ├── bedrock_client.py       # AWS Bedrock integration
├── retrieval/
│   └── vector_store.py         # Qdrant vector database
├── agents/
│   ├── base_agent.py           # Base agent class
│   ├── query_analyzer.py       # Query analysis with Claude
│   ├── retrieval_agent.py      # Vector search
│   └── synthesis_agent.py      # Response generation

scripts/
└── ingest_documents.py         # Document ingestion

examples/
└── simple_chat.py              # Simple chat demo
```

## 🎉 Success!

You now have a working MVP multi-agent RAG system with:
- LLM-powered query analysis
- Semantic vector search
- Context-aware response generation

Ready to move to Phase 2? See [implementation_plan.md](../implementation_plan.md)
