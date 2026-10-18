#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# CLISONIX CLOUD - HETZNER CPX62 DEPLOYMENT GUIDE
# ═══════════════════════════════════════════════════════════════════════════════
#
# Server: cpx62 (Helsinki, Finland)
# IP: 46.62.210.251
# IPv6: 2a01:4f9:c014:5603::/64
# Resources: 16 vCPU, 32 GB RAM, 640 GB SSD
# Total Microservices: 75 (docker-compose.75-services.yml) + others
#
# Created: May 28, 2026
# ═══════════════════════════════════════════════════════════════════════════════

set -e

SERVER_IP="46.62.210.251"
SERVER_NAME="cpx62-hel1-2"
DEPLOY_DIR="/opt/clisonix"
USER="root"
REGION="helsinki"

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║              CLISONIX CLOUD - HETZNER DEPLOYMENT SETUP                  ║"
echo "║                                                                           ║"
echo "║  Server: $SERVER_NAME                                             ║"
echo "║  IP: $SERVER_IP                                                   ║"
echo "║  Region: $REGION                                                   ║"
echo "║  Status: READY TO DEPLOY                                                 ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

# Step 1: System Preparation
echo ""
echo "STEP 1: SYSTEM PREPARATION"
echo "═════════════════════════════════════════════════════════════════════════════"

# Update system
apt-get update && apt-get upgrade -y

# Install prerequisites
apt-get install -y \
  curl \
  wget \
  git \
  vim \
  net-tools \
  htop \
  jq \
  unzip \
  python3 \
  python3-pip

echo "✓ System packages installed"

# Step 2: Docker Installation
echo ""
echo "STEP 2: DOCKER & DOCKER-COMPOSE INSTALLATION"
echo "═════════════════════════════════════════════════════════════════════════════"

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose v2
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
echo "✓ Docker & Docker-Compose installed"

# Step 3: Repository Setup
echo ""
echo "STEP 3: REPOSITORY SETUP"
echo "═════════════════════════════════════════════════════════════════════════════"

mkdir -p $DEPLOY_DIR
cd $DEPLOY_DIR

echo "Cloning Clisonix Cloud repository..."
git clone https://github.com/Web8kameleon-hub/clisonix.com.git .

echo "✓ Repository cloned"

# Step 4: Network Setup
echo ""
echo "STEP 4: DOCKER NETWORK SETUP"
echo "═════════════════════════════════════════════════════════════════════════════"

# Create custom network
docker network create clisonix-net 2>/dev/null || true

echo "✓ Docker network 'clisonix-net' created"

# Step 5: Environment Configuration
echo ""
echo "STEP 5: ENVIRONMENT CONFIGURATION"
echo "═════════════════════════════════════════════════════════════════════════════"

# Create .env file for Hetzner deployment
cat > .env.hetzner << 'EOF'
# ═════════════════════════════════════════════════════════════════════════════
# CLISONIX CLOUD - HETZNER ENVIRONMENT CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════════

# Deployment Settings
HETZNER_DEPLOY=1
DEPLOYMENT_REGION=helsinki
DEPLOYMENT_ENV=production
SERVER_IP=46.62.210.251

# Database Configuration
POSTGRES_USER=clisonix
POSTGRES_PASSWORD=clisonix_secure_hetzner_2026
POSTGRES_DB=clisonixdb
DATABASE_URL=postgresql://clisonix:clisonix_secure_hetzner_2026@postgres:5432/clisonixdb

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Neo4j Configuration
NEO4J_PASSWORD=neo4j_secure_hetzner_2026

# MinIO Configuration
MINIO_ROOT_USER=clisonix
MINIO_ROOT_PASSWORD=minio_secure_hetzner_2026

# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODEL=llama3.1:8b

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=8

# Ocean Core Configuration
OCEAN_PORT=8030
OCEAN_MULTIMODAL_PORT=8033

# Stripe Configuration (Replace with actual keys)
STRIPE_SECRET_KEY=sk_live_your_key_here
STRIPE_PUBLISHABLE_KEY=pk_live_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=Web8kameleon-hub/clisonix-blog

# Clerk Configuration
CLERK_WEBHOOK_SECRET=your_clerk_secret_here

# Application Settings
PYTHONUNBUFFERED=1
PYTHONIOENCODING=UTF-8
LANG=C.UTF-8

# Memory Limits
MEMORY_LIMIT=2G
SWAP_MEMORY=1G

# Logging
LOG_LEVEL=INFO
DOCKER_LOG_LEVEL=info

# Networking
NGINX_PORT=80
NGINX_HTTPS_PORT=443
INTERNAL_NETWORK=clisonix-net
EOF

echo "✓ Environment file created (.env.hetzner)"

# Step 6: Resource Configuration
echo ""
echo "STEP 6: SYSTEM RESOURCE OPTIMIZATION"
echo "═════════════════════════════════════════════════════════════════════════════"

# Increase file descriptors
cat >> /etc/security/limits.conf << EOF
* soft nofile 65535
* hard nofile 65535
* soft nproc 32768
* hard nproc 32768
EOF

# Kernel tuning for Docker
cat >> /etc/sysctl.conf << EOF
vm.max_map_count=262144
net.ipv4.ip_forward=1
net.bridge.bridge-nf-call-iptables=1
EOF

sysctl -p > /dev/null
echo "✓ System resources optimized"

# Step 7: Docker Compose Pre-check
echo ""
echo "STEP 7: DEPLOYMENT READINESS CHECK"
echo "═════════════════════════════════════════════════════════════════════════════"

echo "Checking required files..."
required_files=(
  "docker-compose.75-services.yml"
  "docker-compose.yml"
  "nginx.production.conf"
)

for file in "${required_files[@]}"; do
  if test -f "$file"; then
    echo "  ✓ $file"
  else
    echo "  ✗ $file - MISSING!"
  fi
done

# Step 8: Deployment Notice
echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                         DEPLOYMENT READY                                  ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

echo ""
echo "NEXT STEPS:"
echo "═════════════════════════════════════════════════════════════════════════════"
echo ""
echo "1. UPDATE SECRETS in .env.hetzner:"
echo "   - POSTGRES_PASSWORD"
echo "   - STRIPE_SECRET_KEY"
echo "   - GITHUB_TOKEN"
echo "   - CLERK_WEBHOOK_SECRET"
echo ""
echo "2. START SERVICES:"
echo ""
echo "   # Start all 75 microservices:"
echo "   docker-compose -f docker-compose.75-services.yml --env-file .env.hetzner up -d"
echo ""
echo "   # Or start core services only:"
echo "   docker-compose -f docker-compose.yml --env-file .env.hetzner up -d"
echo ""
echo "3. VERIFY DEPLOYMENT:"
echo "   docker-compose -f docker-compose.75-services.yml ps"
echo ""
echo "4. CHECK LOGS:"
echo "   docker logs clisonix-api"
echo "   docker logs clisonix-ocean-core"
echo "   docker logs clisonix-ollama"
echo ""
echo "5. ACCESS SERVICES:"
echo "   API              → http://46.62.210.251:8000"
echo "   Web Frontend     → http://46.62.210.251:3000"
echo "   Ocean Core       → http://46.62.210.251:8030"
echo "   Ollama           → http://46.62.210.251:11434"
echo "   Grafana          → http://46.62.210.251:3001"
echo "   Prometheus       → http://46.62.210.251:9090"
echo ""
echo "6. SETUP FLOATING IP (Optional):"
echo "   - Via Hetzner Cloud Console: Add Floating IP 46.62.210.251"
echo "   - Configure reverse DNS and DNSSEC"
echo "   - Update firewall rules if needed"
echo ""
echo "═════════════════════════════════════════════════════════════════════════════"

echo ""
echo "✓ Deployment preparation complete!"
echo "✓ All systems ready for Clisonix Cloud deployment"
echo ""

