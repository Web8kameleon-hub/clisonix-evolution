#!/bin/bash
# 🚀 Kameleon.life Production Deployment Script
# Ultra Industrial Platform - STRATO Hosting

echo "🌟 Starting kameleon.life deployment..."

# Configuration
DOMAIN="kameleon.life"
REMOTE_HOST="570523285.swh.strato-hosting.eu"
REMOTE_USER="Master-ID"
REMOTE_PATH="/mnt/rid/32/85/570523285/htdocs"

# Step 1: Build Next.js for production
echo "📦 Building Next.js production..."
yarn build
if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Step 2: Create deployment package
echo "📋 Creating deployment package..."
mkdir -p deploy_temp
cp -r .next/ deploy_temp/
cp -r public/ deploy_temp/
cp package.json deploy_temp/
cp yarn.lock deploy_temp/

# Step 3: Create .htaccess for Next.js routing
echo "⚙️ Creating .htaccess..."
cat > deploy_temp/.htaccess << 'EOF'
RewriteEngine On

# Handle Next.js API routes
RewriteRule ^api/(.*)$ /api/$1 [L]

# Handle Next.js static files
RewriteRule ^_next/(.*)$ /_next/$1 [L]

# Handle dynamic routes - send everything to index.html
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.html [L]

# Security headers
Header always set X-Content-Type-Options nosniff
Header always set X-Frame-Options DENY
Header always set X-XSS-Protection "1; mode=block"

# Enable compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
</IfModule>

# Cache static resources
<IfModule mod_expires.c>
    ExpiresActive on
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/svg+xml "access plus 1 year"
</IfModule>
EOF

# Step 4: Create server-side configuration
echo "🔧 Creating server configuration..."
cat > deploy_temp/server.js << 'EOF'
const express = require('express');
const next = require('next');
const path = require('path');

const dev = process.env.NODE_ENV !== 'production';
const app = next({ dev, dir: '.' });
const handle = app.getRequestHandler();

const PORT = process.env.PORT || 3000;

app.prepare().then(() => {
  const server = express();
  
  // Serve static files
  server.use('/_next', express.static(path.join(__dirname, '.next')));
  server.use('/static', express.static(path.join(__dirname, 'public')));
  
  // Handle all other routes with Next.js
  server.get('*', (req, res) => {
    return handle(req, res);
  });
  
  server.listen(PORT, (err) => {
    if (err) throw err;
    console.log(`🚀 Kameleon.life ready on http://localhost:${PORT}`);
  });
});
EOF

# Step 5: Create package.json for production
echo "📄 Creating production package.json..."
cat > deploy_temp/package.json << 'EOF'
{
  "name": "kameleon-life-production",
  "version": "1.0.0",
  "description": "Ultra Industrial Platform - Kameleon.life",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "next dev",
    "build": "next build"
  },
  "dependencies": {
    "next": "^15.5.6",
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "express": "^4.18.2"
  }
}
EOF

# Step 6: Create environment configuration
echo "🔐 Creating environment config..."
cat > deploy_temp/.env.production << 'EOF'
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://kameleon.life
NEXT_PUBLIC_API_URL=https://api.kameleon.life
NEXT_PUBLIC_NEUROSONIX_URL=https://neuro.kameleon.life

# API Keys (update with actual values)
# OPENWEATHER_API_KEY=your_key_here
# NEWS_API_KEY=your_key_here
# ALPHA_VANTAGE_KEY=your_key_here
EOF

# Step 7: Create upload script
echo "📤 Creating upload script..."
cat > upload_to_strato.sh << 'EOF'
#!/bin/bash
echo "🚀 Uploading to kameleon.life..."

# Note: You'll need to install lftp for this to work
# sudo apt install lftp (Ubuntu/Debian)
# brew install lftp (macOS)

lftp -c "
set ftp:ssl-allow no
open -u Master-ID sftp://570523285.swh.strato-hosting.eu
cd /mnt/rid/32/85/570523285/htdocs
mirror -R deploy_temp/ ./
quit
"
EOF

chmod +x upload_to_strato.sh

# Step 8: Create deployment instructions
echo "📋 Creating deployment instructions..."
cat > KAMELEON_DEPLOYMENT_INSTRUCTIONS.md << 'EOF'
# 🚀 Kameleon.life Deployment Instructions

## Prerequisites
1. Change STRATO master password first
2. Install SFTP client (lftp recommended)
3. Have all API keys ready

## Automatic Deployment
```bash
./deploy-kameleon.sh
```

## Manual SFTP Upload
```bash
# Connect via SFTP
sftp Master-ID@570523285.swh.strato-hosting.eu

# Navigate to web directory
cd /mnt/rid/32/85/570523285/htdocs

# Upload files
put -r deploy_temp/* ./

# Set permissions
chmod 755 server.js
chmod 644 .htaccess
```

## Post-Deployment Setup
1. Configure MySQL database via STRATO panel
2. Enable SSL certificate for kameleon.life
3. Set up subdomains:
   - api.kameleon.life → Port 8080
   - neuro.kameleon.life → Port 8081
4. Test all services

## Monitoring
- Access logs: STRATO control panel
- Error logs: /logs directory
- Performance: Built-in analytics

## Business Launch
1. Test API collection system
2. Verify payment integration
3. Launch marketing campaign
4. Monitor revenue metrics

Target: €4,500-12,000/month with API services
EOF

echo "✅ Deployment configuration complete!"
echo "📁 Files created in deploy_temp/"
echo "🔧 Next steps:"
echo "   1. Change STRATO master password"
echo "   2. Run: ./upload_to_strato.sh"
echo "   3. Configure SSL and subdomains"
echo "   4. Launch kameleon.life! 🚀"
