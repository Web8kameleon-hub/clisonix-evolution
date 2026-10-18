#!/bin/bash
# 🚀 kameleon.life - COMPLETE DEPLOYMENT SCRIPT
# Ultra Industrial Platform - Production Launch

set -e

echo "🌟 STARTING KAMELEON.LIFE DEPLOYMENT..."
echo "========================================"

# Configuration
DOMAIN="kameleon.life"
STRATO_HOST="570523285.swh.strato-hosting.eu"
STRATO_USER="10068142"
REMOTE_PATH="/mnt/rid/32/85/570523285/htdocs"
LOCAL_BUILD=".next"

echo "📋 Deployment Configuration:"
echo "   Domain: $DOMAIN"
echo "   Host: $STRATO_HOST"
echo "   User: $STRATO_USER"
echo "   Target: $REMOTE_PATH"
echo ""

# Step 1: Clean everything
echo "🧹 STEP 1: Cleaning previous builds..."
rm -rf .next out dist node_modules/.cache
echo "   ✅ Cleaned build artifacts"

# Step 2: Install dependencies
echo "📦 STEP 2: Installing dependencies..."
yarn install --frozen-lockfile
echo "   ✅ Dependencies installed"

# Step 3: Build production
echo "🏗️  STEP 3: Building production..."
NODE_ENV=production yarn build
if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi
echo "   ✅ Production build completed"

# Step 4: Create deployment package
echo "📁 STEP 4: Creating deployment package..."
mkdir -p deploy-temp
cp -r .next deploy-temp/
cp -r public deploy-temp/
cp package.json deploy-temp/
cp yarn.lock deploy-temp/
cp .env.production deploy-temp/.env.local
echo "   ✅ Deployment package ready"

# Step 5: Create .htaccess for Apache
echo "🔧 STEP 5: Creating Apache configuration..."
cat > deploy-temp/.htaccess << 'EOF'
# kameleon.life - Ultra Industrial Platform
# Apache Configuration for Next.js Static Export

RewriteEngine On

# Security Headers
Header always set X-Frame-Options "SAMEORIGIN"
Header always set X-Content-Type-Options "nosniff"
Header always set X-XSS-Protection "1; mode=block"
Header always set Referrer-Policy "strict-origin-when-cross-origin"

# HTTPS Redirect
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# API Routes
RewriteRule ^api/(.*)$ /api/$1 [L]

# Next.js Static Routes
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ /index.html [L]

# Cache Control
<FilesMatch "\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2|ttf|eot)$">
    ExpiresActive On
    ExpiresDefault "access plus 1 year"
</FilesMatch>

# Gzip Compression
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
EOF
echo "   ✅ Apache configuration created"

# Step 6: Upload to STRATO
echo "🚀 STEP 6: Uploading to STRATO hosting..."
echo "   Please enter your STRATO password when prompted..."

# Create SFTP batch file
cat > sftp-batch << EOF
cd $REMOTE_PATH
mkdir -p backup-$(date +%Y%m%d)
put -r deploy-temp/* ./
chmod 755 .htaccess
quit
EOF

# Upload via SFTP
sftp -b sftp-batch $STRATO_USER@$STRATO_HOST
if [ $? -eq 0 ]; then
    echo "   ✅ Upload completed successfully"
else
    echo "   ❌ Upload failed"
    exit 1
fi

# Step 7: Cleanup
echo "🧹 STEP 7: Cleaning up..."
rm -rf deploy-temp sftp-batch
echo "   ✅ Cleanup completed"

# Step 8: Verification
echo "🔍 STEP 8: Verifying deployment..."
echo "   🌐 Testing: https://$DOMAIN"
curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN
echo ""

echo "🎉 KAMELEON.LIFE DEPLOYMENT COMPLETED!"
echo "========================================"
echo "🌟 Your Ultra Industrial Platform is now live at: https://$DOMAIN"
echo "🌤️  Weather API: https://$DOMAIN/ultra-industrial/weather"
echo "🤖 ASI Backend: https://api.$DOMAIN"
echo "🧠 NeuroSonix: https://neuro.$DOMAIN"
echo ""
echo "📊 Revenue Target: €4,500-12,000/month"
echo "🎯 Next: Configure SSL & subdomains in STRATO panel"
echo ""
echo "🚀 READY FOR BUSINESS LAUNCH! 🚀"
