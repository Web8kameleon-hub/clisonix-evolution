#!/bin/bash

# Kameleon.life Deployment Script for Strato.de
# UltraWebThinking NeuroSonix Platform Deployment

echo "🦎 Starting Kameleon.life Deployment on Strato.de..."
echo "🚀 UltraWebThinking NeuroSonix Platform"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="kameleon.life"
PROJECT_DIR="/var/www/$DOMAIN"
BACKUP_DIR="/var/backups/$DOMAIN"
LOG_DIR="/var/log/kameleon"

echo -e "${BLUE}📋 Configuration:${NC}"
echo "   Domain: $DOMAIN"
echo "   Project Dir: $PROJECT_DIR"
echo "   Log Dir: $LOG_DIR"
echo ""

# Create directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
sudo mkdir -p $PROJECT_DIR
sudo mkdir -p $BACKUP_DIR
sudo mkdir -p $LOG_DIR
sudo mkdir -p /var/log/pm2

# Set permissions
echo -e "${YELLOW}🔐 Setting permissions...${NC}"
sudo chown -R www-data:www-data $PROJECT_DIR
sudo chown -R www-data:www-data $LOG_DIR
sudo chmod -R 755 $PROJECT_DIR

# Install Node.js (if not installed)
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Node.js...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install Python (if not installed)
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}🐍 Installing Python...${NC}"
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Install PM2 globally
if ! command -v pm2 &> /dev/null; then
    echo -e "${YELLOW}⚙️ Installing PM2...${NC}"
    sudo npm install -g pm2
fi

# Install Yarn globally
if ! command -v yarn &> /dev/null; then
    echo -e "${YELLOW}🧶 Installing Yarn...${NC}"
    sudo npm install -g yarn
fi

# Clone or update repository
if [ -d "$PROJECT_DIR/.git" ]; then
    echo -e "${YELLOW}🔄 Updating repository...${NC}"
    cd $PROJECT_DIR
    git pull origin master
else
    echo -e "${YELLOW}📥 Cloning repository...${NC}"
    git clone https://github.com/web8kameleon-hub/ultrawebthinking.git $PROJECT_DIR
    cd $PROJECT_DIR
fi

# Install dependencies
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
yarn install --production

# Build Next.js application
echo -e "${YELLOW}🏗️ Building Next.js application...${NC}"
yarn build

# Install Python dependencies
echo -e "${YELLOW}🐍 Installing Python dependencies...${NC}"
cd ultracom
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..

# Create environment files
echo -e "${YELLOW}⚙️ Creating environment files...${NC}"
cat > .env.production << EOF
NODE_ENV=production
DOMAIN=$DOMAIN
FRONTEND_URL=https://$DOMAIN
API_URL=https://api.$DOMAIN
NEURO_URL=https://neuro.$DOMAIN
EOF

# Copy ecosystem config
echo -e "${YELLOW}📄 Setting up PM2 ecosystem...${NC}"
cp ecosystem.config.js $PROJECT_DIR/

# Start services with PM2
echo -e "${YELLOW}🚀 Starting services...${NC}"
pm2 start ecosystem.config.js

# Setup PM2 startup
echo -e "${YELLOW}🔄 Setting up PM2 startup...${NC}"
pm2 startup
pm2 save

# Create Nginx configuration
echo -e "${YELLOW}🌐 Creating Nginx configuration...${NC}"
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://localhost:80;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}

server {
    listen 443 ssl http2;
    server_name api.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}

server {
    listen 443 ssl http2;
    server_name neuro.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8081;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Setup SSL with Certbot
echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN -d api.$DOMAIN -d neuro.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Create monitoring script
echo -e "${YELLOW}📊 Creating monitoring script...${NC}"
cat > /usr/local/bin/kameleon-monitor.sh << 'EOF'
#!/bin/bash
# Kameleon.life Monitoring Script

LOG_FILE="/var/log/kameleon/monitor.log"
date >> $LOG_FILE

# Check services
pm2 status >> $LOG_FILE

# Check disk space
df -h >> $LOG_FILE

# Check memory usage
free -h >> $LOG_FILE

# Check SSL certificate expiry
echo "SSL Certificate Status:" >> $LOG_FILE
sudo certbot certificates >> $LOG_FILE

# Restart services if needed
pm2 restart all --silent
EOF

chmod +x /usr/local/bin/kameleon-monitor.sh

# Setup cron job for monitoring
echo -e "${YELLOW}⏰ Setting up monitoring cron job...${NC}"
(crontab -l 2>/dev/null; echo "0 */6 * * * /usr/local/bin/kameleon-monitor.sh") | crontab -

# Final status check
echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}🌐 Service URLs:${NC}"
echo "   Main Site: https://$DOMAIN"
echo "   API Gateway: https://api.$DOMAIN"
echo "   NeuroSonix API: https://neuro.$DOMAIN"
echo ""
echo -e "${BLUE}📊 Status Commands:${NC}"
echo "   pm2 status"
echo "   pm2 logs"
echo "   pm2 monit"
echo ""
echo -e "${GREEN}🎉 Kameleon.life is now live!${NC}"
