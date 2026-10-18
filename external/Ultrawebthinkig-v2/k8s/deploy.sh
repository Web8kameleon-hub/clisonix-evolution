#!/bin/bash
# EuroWeb AGI Platform - Production Deployment Script
# Deploy all Kubernetes resources for industrial production

set -e

echo "🚀 EuroWeb AGI Platform - Production Deployment"
echo "=============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed or not in PATH${NC}"
    exit 1
fi

# Check if we can connect to cluster
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${BLUE}Connected to cluster: $(kubectl config current-context)${NC}"

# Create namespace if it doesn't exist
echo -e "${YELLOW}Creating namespace...${NC}"
kubectl create namespace euroweb-production --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets (user must provide actual secret values)
echo -e "${YELLOW}Applying secrets and configuration...${NC}"
if [ -f "k8s/secrets.yaml" ]; then
    echo -e "${YELLOW}⚠️  Warning: Please ensure secrets.yaml contains actual base64-encoded values${NC}"
    read -p "Have you updated secrets.yaml with real values? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl apply -f k8s/secrets.yaml
        echo -e "${GREEN}✅ Secrets applied${NC}"
    else
        echo -e "${RED}❌ Skipping secrets - please update secrets.yaml first${NC}"
    fi
else
    echo -e "${RED}❌ secrets.yaml not found${NC}"
fi

# Apply services
echo -e "${YELLOW}Applying services...${NC}"
if [ -f "k8s/service.yaml" ]; then
    kubectl apply -f k8s/service.yaml
    echo -e "${GREEN}✅ Services applied${NC}"
else
    echo -e "${RED}❌ service.yaml not found${NC}"
fi

# Apply deployment
echo -e "${YELLOW}Applying deployment...${NC}"
if [ -f "k8s/production.yaml" ]; then
    kubectl apply -f k8s/production.yaml
    echo -e "${GREEN}✅ Deployment applied${NC}"
else
    echo -e "${RED}❌ production.yaml not found${NC}"
fi

# Apply autoscaler
echo -e "${YELLOW}Applying autoscaler...${NC}"
if [ -f "k8s/autoscaler.yaml" ]; then
    kubectl apply -f k8s/autoscaler.yaml
    echo -e "${GREEN}✅ Autoscaler applied${NC}"
else
    echo -e "${RED}❌ autoscaler.yaml not found${NC}"
fi

# Wait for deployment to be ready
echo -e "${YELLOW}Waiting for deployment to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s deployment/euroweb-deployment -n euroweb-production

# Get service info
echo -e "${BLUE}Service Information:${NC}"
kubectl get services -n euroweb-production

# Get pod status
echo -e "${BLUE}Pod Status:${NC}"
kubectl get pods -n euroweb-production

# Get HPA status
echo -e "${BLUE}Autoscaler Status:${NC}"
kubectl get hpa -n euroweb-production

# Get external IP (if LoadBalancer)
echo -e "${YELLOW}Getting external access information...${NC}"
EXTERNAL_IP=$(kubectl get service euroweb-service -n euroweb-production -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
if [ -n "$EXTERNAL_IP" ]; then
    echo -e "${GREEN}🌐 External access: http://$EXTERNAL_IP${NC}"
    echo -e "${GREEN}🌐 HTTPS access: https://$EXTERNAL_IP${NC}"
else
    echo -e "${YELLOW}⏳ External IP not yet assigned, check with: kubectl get svc -n euroweb-production${NC}"
fi

echo ""
echo -e "${GREEN}🎉 EuroWeb AGI Platform deployment complete!${NC}"
echo -e "${BLUE}Monitor with: kubectl get all -n euroweb-production${NC}"
echo -e "${BLUE}Logs: kubectl logs -f deployment/euroweb-deployment -n euroweb-production${NC}"
echo -e "${BLUE}Scale: kubectl scale deployment euroweb-deployment --replicas=5 -n euroweb-production${NC}"
