#!/bin/bash

# ResoftAI Kubernetes Deployment Script
# Usage: ./deploy-k8s.sh [namespace]

set -e

NAMESPACE=${1:-resoftai}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    log_error "kubectl is not installed or not in PATH"
    exit 1
fi

# Check if we're connected to a cluster
if ! kubectl cluster-info &> /dev/null; then
    log_error "Not connected to a Kubernetes cluster"
    exit 1
fi

log_info "Deploying ResoftAI to Kubernetes namespace: $NAMESPACE"

# Create namespace
log_info "Creating namespace..."
kubectl apply -f kubernetes/namespace.yaml

# Create secrets
log_info "Creating secrets..."
kubectl apply -f kubernetes/secrets.yaml

# Deploy PostgreSQL
log_info "Deploying PostgreSQL..."
kubectl apply -f kubernetes/postgres.yaml

# Wait for PostgreSQL to be ready
log_info "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s

# Build and push Docker images (this would typically be done in CI/CD)
log_info "Note: Docker images should be built and pushed to a registry"
log_info "For local testing, you can build images and load them into kind/minikube"

# Deploy backend
log_info "Deploying backend..."
kubectl apply -f kubernetes/backend.yaml

# Deploy frontend
log_info "Deploying frontend..."
kubectl apply -f kubernetes/frontend.yaml

# Deploy ingress (optional)
log_info "Deploying ingress..."
kubectl apply -f kubernetes/ingress.yaml

# Wait for all pods to be ready
log_info "Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n $NAMESPACE --timeout=300s

# Display deployment information
log_success "ResoftAI Kubernetes deployment completed!"
log_info ""
log_info "Services:"
log_info "  Frontend: $(kubectl get svc frontend -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
log_info "  Backend API: $(kubectl get svc backend -n $NAMESPACE -o jsonpath='{.spec.clusterIP}'):8000"
log_info ""
log_info "Pods:"
kubectl get pods -n $NAMESPACE
log_info ""
log_info "Services:"
kubectl get svc -n $NAMESPACE
log_info ""
log_info "To access the application:"
log_info "  1. Update your /etc/hosts or DNS to point to the frontend service IP"
log_info "  2. Access the application at the configured hostname"
log_info ""
log_info "Management Commands:"
log_info "  View logs: kubectl logs -f deployment/backend -n $NAMESPACE"
log_info "  Scale backend: kubectl scale deployment/backend --replicas=3 -n $NAMESPACE"
log_info "  Delete deployment: kubectl delete -f kubernetes/ -n $NAMESPACE"

log_success "Kubernetes deployment script completed successfully!"