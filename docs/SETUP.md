# Multi-Agent RAG System - Setup Guide

## Prerequisites

- **Python**: 3.11 or higher
- **Docker**: 20.10+ with Docker Compose
- **AWS Account**: For Bedrock access
- **Memory**: 16GB RAM minimum
- **Disk Space**: 10GB for datasets and models

## Quick Setup (Local Development)

### 1. Clone and Setup Environment

```bash
# Clone repository
git clone <your-repo-url>
cd chorus

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Poetry
pip install poetry

# Install dependencies
poetry install
```

### 2. Configure Environment Variables

```bash
# Copy environment template
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# Edit .env and add your credentials:
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
# - NEO4J_PASSWORD
# (Optional) LANGCHAIN_API_KEY for tracing
```

### 3. Start Services

```bash
# Start Qdrant, Redis, and Neo4j
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f
```

### 4. Initialize Database

```bash
# TODO: Create setup script
# python scripts/setup_databases.py
```

### 5. Ingest Sample Documents

```bash
# TODO: Create ingestion script
# python scripts/ingest_documents.py --source data/docs
```

### 6. Start API Server

```bash
# Development mode with hot reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.api.main:app --workers 4 --host 0.0.0.0 --port 8000
```

### 7. Test the API

```bash
# Open browser
http://localhost:8000/docs  # Swagger UI

# Test health endpoint
curl http://localhost:8000/api/v1/health

# Test WebSocket (use examples/websocket_client.py)
python examples/websocket_client.py
```

## AWS Bedrock Setup

### 1. Enable Bedrock Models

1. Log into AWS Console
2. Navigate to Amazon Bedrock
3. Go to "Model access"
4. Request access to:
   - Claude 4.5 Sonnet
   - Titan Embeddings V2

### 2. Create IAM User

```bash
# Create IAM user with Bedrock permissions
# Attach policy: AmazonBedrockFullAccess

# Create access keys
# Add to .env file
```

## Neo4j Setup (Phase 4)

```bash
# Neo4j is included in docker-compose.yml

# Access Neo4j Browser
http://localhost:7474

# Login credentials (from .env):
# Username: neo4j
# Password: <your_neo4j_password_here>

# Run setup Cypher queries
# TODO: Create graph schema initialization script
```

## Qdrant Setup

```bash
# Qdrant runs in Docker (no additional setup needed)

# Access Qdrant dashboard
http://localhost:6333/dashboard

# Verify collection creation
# TODO: Collections are auto-created during ingestion
```

## Troubleshooting

### Docker Services Won't Start

```bash
# Check if ports are already in use
netstat -an | findstr "6333 6379 7474 7687"  # Windows
lsof -i :6333,6379,7474,7687                # macOS/Linux

# Stop conflicting services or change ports in docker-compose.yml
```

### AWS Bedrock 403 Errors

```bash
# Verify IAM permissions
aws bedrock list-foundation-models --region us-east-1

# Check model access in AWS Console
# Ensure Claude 4.5 Sonnet and Titan Embeddings are enabled
```

### Poetry Installation Issues

```bash
# Use pip fallback
pip install -r requirements.txt  # TODO: Generate requirements.txt
```

## Development Workflow

```bash
# Run tests
pytest tests/ -v --cov=src

# Run linting
ruff check src/
black src/ --check

# Format code
black src/
isort src/

# Type checking
mypy src/
```

## Next Steps

- [ ] Read [Architecture Documentation](ARCHITECTURE.md)
- [ ] Review [API Reference](API.md)
- [ ] Follow [DEPLOYMENT.md](DEPLOYMENT.md) for AWS EKS deployment
- [ ] Check [EVALUATION.md](EVALUATION.md) for benchmarking

## Support

For issues, please check:
1. [GitHub Issues](<your-repo-url>/issues)
2. [Documentation](docs/)
3. [Contributing Guide](CONTRIBUTING.md)
