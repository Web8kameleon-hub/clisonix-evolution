#!/bin/bash
# ═════════════════════════════════════════════════════════════
# CLISONIX PRODUCTION DEPLOYMENT SETUP
# ═════════════════════════════════════════════════════════════

cd /opt/clisonix-cloud

echo "🔐 Step 1: Generating secure passwords..."

# Generate strong passwords (32+ chars)
DB_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
REDIS_PASS=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
JWT_SECRET=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-64)

echo "✅ Generated secure credentials:"
echo "   DB_PASSWORD: ${DB_PASS:0:10}..."
echo "   REDIS_PASSWORD: ${REDIS_PASS:0:10}..."
echo "   JWT_SECRET: ${JWT_SECRET:0:10}..."

# Backup current .env.production
cp .env.production .env.production.bak.$(date +%s)
echo "✅ Backed up to .env.production.bak.*"

# Update .env.production with actual passwords
echo ""
echo "🔧 Step 2: Updating .env.production..."

# Use sed to replace placeholders
sed -i "s|CHANGE_ME_TO_STRONG_PASSWORD_32_CHARS_MIN|${DB_PASS}|g" .env.production
sed -i "s|CHANGE_ME_TO_STRONG_REDIS_PASSWORD_32_CHARS_MIN|${REDIS_PASS}|g" .env.production

# Update DATABASE_URL and REDIS_URL
sed -i "s|postgresql://clisonix:CHANGE_ME.*@postgres|postgresql://clisonix:${DB_PASS}@postgres|g" .env.production
sed -i "s|redis://:CHANGE_ME.*@redis|redis://:${REDIS_PASS}@redis|g" .env.production

# Add JWT_SECRET
echo "" >> .env.production
echo "JWT_SECRET=${JWT_SECRET}" >> .env.production

echo "✅ .env.production updated!"
chmod 600 .env.production

echo ""
echo "📋 Step 3: Verification - Current Production Variables:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat .env.production | grep -E '^(DB_USER|DB_NAME|ENVIRONMENT|DEBUG|LOG_LEVEL)=' | head -5
echo ""
echo "DB_PASSWORD: $(cat .env.production | grep '^DB_PASSWORD=' | cut -d= -f2 | head -c 10)..."
echo "REDIS_PASSWORD: $(cat .env.production | grep '^REDIS_PASSWORD=' | cut -d= -f2 | head -c 10)..."

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Step 2.5: Validate docker-compose syntax..."
docker-compose -f docker-compose.production.yml config > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ docker-compose.production.yml is VALID"
else
    echo "❌ Invalid docker-compose syntax!"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ALL SETUP COMPLETE - Ready to deploy!"
echo ""
echo "Next steps:"
echo "  1. docker-compose -f docker-compose.production.yml up -d postgres redis"
echo "  2. sleep 20 && docker-compose -f docker-compose.production.yml up -d"
echo "  3. Monitor: docker-compose -f docker-compose.production.yml logs -f"

