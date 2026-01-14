# Deployment Guide

## Overview

Deploy the Multi-Agent RAG system to AWS EKS using Terraform infrastructure as code.

---

## Prerequisites

- AWS CLI configured with appropriate permissions
- Terraform >= 1.0
- kubectl
- Docker

---

## Quick Deploy

```bash
# 1. Deploy infrastructure
cd infrastructure/terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan

# 2. Configure kubectl
aws eks update-kubeconfig --name multi-agent-rag --region us-east-1

# 3. Deploy application
./scripts/deploy.sh dev
```

---

## Environment Variables

```bash
# Required
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1

# Optional (for enhanced features)
NEO4J_URI=bolt://neo4j:7687
NEO4J_PASSWORD=your-password
TAVILY_API_KEY=your-key
COHERE_API_KEY=your-key
LANGCHAIN_API_KEY=your-key
```

---

## Terraform Resources

| Resource | Description |
|----------|-------------|
| VPC | 3 AZ, public/private subnets |
| EKS Cluster | Kubernetes 1.28 |
| Node Group | t3.medium/large (2-5 nodes) |
| ALB Controller | Ingress with WebSocket |
| EBS CSI | Persistent volumes |

---

## Kubernetes Resources

| Resource | Replicas | Purpose |
|----------|----------|---------|
| API Deployment | 2-10 (HPA) | FastAPI server |
| Qdrant StatefulSet | 1 | Vector store |
| Redis Deployment | 1 | Cache/memory |
| Ingress | 1 | ALB routing |

---

## Scaling

```bash
# Manual scale
kubectl scale deployment multi-agent-rag-api -n multi-agent-rag --replicas=5

# View HPA status
kubectl get hpa -n multi-agent-rag
```

---

## Monitoring

```bash
# Prometheus metrics
curl http://localhost:8000/metrics

# Pod logs
kubectl logs -f deployment/multi-agent-rag-api -n multi-agent-rag

# Dashboard
kubectl port-forward svc/grafana 3000:80 -n monitoring
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Pods not starting | Check secrets: `kubectl get secrets -n multi-agent-rag` |
| ALB not provisioning | Verify IAM role for AWS LB Controller |
| Memory OOM | Increase limits in deployment.yaml |
