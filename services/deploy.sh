#!/bin/bash
# =============================================================================
# CLISONIX MICROSERVICES DEPLOYMENT SCRIPT
# =============================================================================
# Përdorimi: ./deploy.sh [all|core|reporting|excel]
# =============================================================================

set -e

SERVICE=${1:-all}
NETWORK="clisonix-services"

echo "🚀 Clisonix Microservices Deployment"
echo "======================================"

# Krijo network nëse nuk ekziston
docker network create $NETWORK 2>/dev/null || true

deploy_core() {
    echo "📦 Deploying Core API..."
    cd core
    docker build -t clisonix-core:latest .
    docker stop clisonix-core 2>/dev/null || true
    docker rm clisonix-core 2>/dev/null || true
    docker run -d \
        --name clisonix-core \
        --network $NETWORK \
        --network root_clisonix \
        -p 8000:8000 \
        --restart unless-stopped \
        clisonix-core:latest
    cd ..
    echo "✅ Core API deployed on port 8000"
}

deploy_reporting() {
    echo "📊 Deploying Reporting Service..."
    cd reporting
    docker build -t clisonix-reporting:latest .
    docker stop clisonix-reporting 2>/dev/null || true
    docker rm clisonix-reporting 2>/dev/null || true
    docker run -d \
        --name clisonix-reporting \
        --network $NETWORK \
        --network root_clisonix \
        -p 8001:8001 \
        -e CORE_API_URL=http://clisonix-core:8000 \
        --restart unless-stopped \
        clisonix-reporting:latest
    cd ..
    echo "✅ Reporting Service deployed on port 8001"
}

deploy_excel() {
    echo "📗 Deploying Excel Service..."
    cd excel
    docker build -t clisonix-excel:latest .
    docker stop clisonix-excel 2>/dev/null || true
    docker rm clisonix-excel 2>/dev/null || true
    docker run -d \
        --name clisonix-excel \
        --network $NETWORK \
        --network root_clisonix \
        -p 8002:8002 \
        -e CORE_API_URL=http://clisonix-core:8000 \
        --restart unless-stopped \
        clisonix-excel:latest
    cd ..
    echo "✅ Excel Service deployed on port 8002"
}

case $SERVICE in
    core)
        deploy_core
        ;;
    reporting)
        deploy_reporting
        ;;
    excel)
        deploy_excel
        ;;
    all)
        deploy_core
        sleep 3
        deploy_reporting
        deploy_excel
        ;;
    *)
        echo "Usage: ./deploy.sh [all|core|reporting|excel]"
        exit 1
        ;;
esac

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Services Status:"
docker ps --filter "name=clisonix-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
