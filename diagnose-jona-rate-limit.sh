#!/bin/bash
# JONA & ALBI Rate Limit Fix & Diagnostic
# Verifikat status aktual të rate limit-it
# Date: March 28, 2026

set -e

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║  🔍 JONA & ALBI Rate Limit Diagnostic                           ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# API Base URLs
JONA_API="http://localhost:7777"
MAIN_API="http://localhost:8000"
ALBI_EEG_API="http://localhost:6680"

# ═══════════════════════════════════════════════════════════════════════════
# FUNCTION: Test Rate Limit Status
# ═══════════════════════════════════════════════════════════════════════════

test_endpoint() {
    local endpoint=$1
    local name=$2
    local url="$MAIN_API$endpoint"

    echo -n "Testing $name... "

    for i in {1..5}; do
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url")

        if [ "$response" = "200" ] || [ "$response" = "201" ]; then
            echo -ne "✓ "
        elif [ "$response" = "429" ]; then
            echo -ne "${RED}⊗(429)${NC} "
        else
            echo -ne "?($response) "
        fi

        sleep 0.2
    done

    echo ""
}

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: Check API Health
# ═══════════════════════════════════════════════════════════════════════════

echo "${BLUE}[1] Checking API Health...${NC}"

if ! curl -s "$MAIN_API/api/health" > /dev/null 2>&1; then
    echo "${RED}✗ Main API not responding on port 8000${NC}"
    echo "  Start it with: docker-compose up -d clisonix-api"
    exit 1
fi

if ! curl -s "$JONA_API/health" > /dev/null 2>&1; then
    echo "${YELLOW}⚠ JONA API not fully responding (may be internal only)${NC}"
else
    echo "${GREEN}✓ JONA API healthy${NC}"
fi

if ! curl -s "http://localhost:6681/status" > /dev/null 2>&1; then
    echo "${YELLOW}⚠ ALBI EEG not responding (may be internal only)${NC}"
else
    echo "${GREEN}✓ ALBI EEG healthy${NC}"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: Test Rate Limit on Different Endpoints
# ═══════════════════════════════════════════════════════════════════════════

echo "${BLUE}[2] Testing Rate Limit Behavior...${NC}"
echo ""

echo "JONA endpoints (should be EXEMPT from rate limit):"
test_endpoint "/api/jona/status" "JONA Status"
test_endpoint "/api/jona/session" "JONA Session"
test_endpoint "/api/jona/audio/list" "JONA Audio List"

echo ""
echo "Health endpoints (should be EXEMPT from rate limit):"
test_endpoint "/api/health" "Health Check"
test_endpoint "/api/status" "Status"

echo ""
echo "Other endpoints (should have rate limit of 120/min):"
test_endpoint "/api/albi/eeg/status" "ALBI EEG Status"

echo ""

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: Check Rate Limit Configuration
# ═══════════════════════════════════════════════════════════════════════════

echo "${BLUE}[3] Rate Limit Configuration${NC}"

config_file="./apps/api/main.py"
if [ -f "$config_file" ]; then
    echo ""
    echo "Rate limit exempt paths (from $config_file):"
    grep -A 10 "RATE_LIMIT_EXEMPT_PATHS" "$config_file" | head -15
    echo ""

    echo "Rate limit value:"
    grep "limit = " "$config_file" | grep -v "endpoint"
else
    echo "${YELLOW}⚠ Config file not found${NC}"
fi

echo ""

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: Recommendations
# ═══════════════════════════════════════════════════════════════════════════

echo "${BLUE}[4] Recommendations${NC}"
echo ""

echo "✓ JONA Rate Limit Fix Applied:"
echo "  • JONA endpoints (/api/jona/*) - NO rate limit"
echo "  • Health endpoints - NO rate limit"
echo "  • Other endpoints - 120 requests/minute"
echo ""

echo "If you still see RATE_LIMIT errors:"
echo ""
echo "1. Restart API service:"
echo "   docker-compose restart clisonix-api"
echo ""
echo "2. Check if load-balancer has separate rate limit:"
echo "   grep -r 'rate' docker-compose.yml"
echo ""
echo "3. Check Nginx/proxy rate limit (if using):"
echo "   cat /etc/nginx/nginx.conf | grep limit"
echo ""
echo "4. Monitor logs during failures:"
echo "   docker logs -f clisonix-api | grep -i rate"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: Performance Test
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "${BLUE}[5] Performance Test (20 rapid requests to JONA)${NC}"
echo ""

success=0
rate_limit=0

for i in {1..20}; do
    response=$(curl -s -o /dev/null -w "%{http_code}" "$MAIN_API/api/jona/status")

    if [ "$response" = "200" ] || [ "$response" = "201" ]; then
        ((success++))
        echo -n "."
    elif [ "$response" = "429" ]; then
        ((rate_limit++))
        echo -n "R"  # Rate limited
    else
        echo -n "E"  # Error
    fi
done

echo ""
echo ""
echo "Results:"
echo "  Success: $success/20"
echo "  Rate limited: $rate_limit/20"

if [ $rate_limit -eq 0 ]; then
    echo "  ${GREEN}✓ JONA rate limit is working correctly!${NC}"
else
    echo "  ${RED}✗ JONA still hitting rate limit${NC}"
    echo ""
    echo "  Debugging steps:"
    echo "  1. Check if API is behind a proxy with its own rate limit"
    echo "  2. Verify main.py middleware is reloaded (restart API)"
    echo "  3. Check for other middleware applying rate limits"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "Diagnostic complete!"
echo "═══════════════════════════════════════════════════════════════════════"
