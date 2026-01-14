#!/bin/bash
# EKS Deployment Script
# Usage: ./deploy.sh <environment>

set -euo pipefail

ENVIRONMENT=${1:-dev}
AWS_REGION=${AWS_REGION:-us-east-1}
CLUSTER_NAME="multi-agent-rag"
NAMESPACE="multi-agent-rag"

echo "🚀 Deploying Multi-Agent RAG to $ENVIRONMENT environment"

# Check prerequisites
command -v kubectl >/dev/null 2>&1 || { echo "kubectl required but not installed."; exit 1; }
command -v aws >/dev/null 2>&1 || { echo "AWS CLI required but not installed."; exit 1; }

# Update kubeconfig
echo "📋 Configuring kubectl..."
aws eks update-kubeconfig --name "$CLUSTER_NAME" --region "$AWS_REGION"

# Verify cluster connection
kubectl cluster-info

# Create namespace if not exists
echo "📁 Creating namespace..."
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Apply data services
echo "💾 Deploying data services (Qdrant, Redis)..."
kubectl apply -f infrastructure/kubernetes/data-services.yaml

# Wait for data services
echo "⏳ Waiting for data services..."
kubectl wait --for=condition=ready pod -l app=qdrant -n "$NAMESPACE" --timeout=120s || true
kubectl wait --for=condition=ready pod -l app=redis -n "$NAMESPACE" --timeout=120s || true

# Apply secrets and config (assumes secrets.yaml has been customized)
echo "🔐 Applying secrets and configuration..."
kubectl apply -f infrastructure/kubernetes/secrets.yaml

# Deploy application
echo "🎯 Deploying API application..."
kubectl apply -f infrastructure/kubernetes/deployment.yaml

# Apply autoscaling
echo "📈 Configuring autoscaling..."
kubectl apply -f infrastructure/kubernetes/autoscaling.yaml

# Apply ingress
echo "🌐 Configuring ingress..."
kubectl apply -f infrastructure/kubernetes/ingress.yaml

# Apply monitoring (if Prometheus operator is installed)
if kubectl get crd servicemonitors.monitoring.coreos.com >/dev/null 2>&1; then
    echo "📊 Configuring monitoring..."
    kubectl apply -f infrastructure/kubernetes/monitoring.yaml
fi

# Wait for deployment
echo "⏳ Waiting for deployment rollout..."
kubectl rollout status deployment/multi-agent-rag-api -n "$NAMESPACE" --timeout=300s

# Show status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Pod Status:"
kubectl get pods -n "$NAMESPACE"
echo ""
echo "🌐 Ingress:"
kubectl get ingress -n "$NAMESPACE"
echo ""
echo "🔗 Load Balancer URL:"
kubectl get ingress -n "$NAMESPACE" -o jsonpath='{.items[0].status.loadBalancer.ingress[0].hostname}'
echo ""
