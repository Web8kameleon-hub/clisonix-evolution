#!/bin/bash

# =============================================================================
# CLISONIX CLOUD - AVIATION WEATHER SERVICE DEPLOYMENT
# =============================================================================
# Deploys ONLY the aviation-weather container to Hetzner server
# Usage: ./deploy-aviation-weather.sh

set -e

HETZNER_IP="46.225.14.83"
DEPLOY_PATH="/root/Clisonix-cloud"
SERVICE_NAME="aviation"
CONTAINER_NAME="clisonix-aviation"

echo "🛫 Aviation Weather Deployment Script"
echo "========================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if SSH key is available
if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${RED}❌ SSH key not found at ~/.ssh/id_rsa${NC}"
    exit 1
fi

echo -e "${YELLOW}📡 Connecting to Hetzner server...${NC}"
echo "   IP: $HETZNER_IP"
echo "   Service: $SERVICE_NAME"
echo ""

# Connect via SSH and deploy
ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 root@$HETZNER_IP << ENDSSH
    set -e
    
    echo -e "${YELLOW}📥 Pulling latest code from GitHub...${NC}"
    cd $DEPLOY_PATH
    git pull origin main --quiet
    
    echo -e "${YELLOW}🔨 Building aviation-weather image...${NC}"
    docker-compose build --no-cache $SERVICE_NAME
    
    echo -e "${YELLOW}🛑 Stopping existing container...${NC}"
    docker-compose down $SERVICE_NAME || true
    
    echo -e "${YELLOW}▶️  Starting new container...${NC}"
    docker-compose up -d $SERVICE_NAME
    
    echo -e "${YELLOW}⏳ Waiting for service to be healthy...${NC}"
    sleep 5
    
    echo -e "${YELLOW}📊 Container Status:${NC}"
    docker ps --format 'table {{.Names}}\t{{.Status}}' | grep $CONTAINER_NAME
    
    echo ""
    echo -e "${YELLOW}🔍 Testing aviation-weather endpoints...${NC}"
    
    # Test health endpoint
    HEALTH=$(curl -s http://localhost:8080/health | grep -o 'healthy')
    if [ "$HEALTH" = "healthy" ]; then
        echo -e "${GREEN}✅ /health endpoint: OK${NC}"
    else
        echo -e "${RED}❌ /health endpoint: FAILED${NC}"
    fi
    
    # Test status endpoint
    STATUS=$(curl -s http://localhost:8080/status | grep -o 'operational')
    if [ "$STATUS" = "operational" ]; then
        echo -e "${GREEN}✅ /status endpoint: OK${NC}"
    else
        echo -e "${RED}❌ /status endpoint: FAILED${NC}"
    fi
    
    # Test API root
    API_TEST=$(curl -s http://localhost:8080/ | grep -o 'Aviation Weather API')
    if [ "$API_TEST" = "Aviation Weather API" ]; then
        echo -e "${GREEN}✅ API root endpoint: OK${NC}"
    else
        echo -e "${RED}❌ API root endpoint: FAILED${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
    echo ""
    echo "📚 Available endpoints:"
    echo "   - Health: http://api.clisonix.com:8080/health"
    echo "   - Status: http://api.clisonix.com:8080/status"
    echo "   - METAR: http://api.clisonix.com:8080/metar/{ICAO}"
    echo "   - TAF: http://api.clisonix.com:8080/taf/{ICAO}"
    echo "   - Search: http://api.clisonix.com:8080/airports/search?query=tirana"
    
ENDSSH

echo ""
echo -e "${GREEN}🎉 Aviation Weather Service deployed successfully!${NC}"
echo ""
