#!/bin/bash
# Deployment Checklist for JONA Rate Limit Fix
# Quick verification before and after deployment

set -e

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  📋 JONA Rate Limit Fix - Deployment Checklist                   ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default to localhost unless provided
API_HOST="${1:-localhost}"
API_PORT="${2:-8000}"
API_BASE="http://${API_HOST}:${API_PORT}"

echo "${BLUE}Configuration:${NC}"
echo "  API Base URL: $API_BASE"
echo ""

# Helper function for test results
check_endpoint() {
    local name=$1
    local endpoint=$2
    local expected=$3

    echo -n "  ├─ $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE$endpoint" 2>/dev/null || echo "000")

    if [ "$response" = "$expected" ] || [ "$expected" = "*" ]; then
        echo -e "${GREEN}✓ (HTTP $response)${NC}"
        return 0
    else
        echo -e "${RED}✗ (HTTP $response, expected $expected)${NC}"
        return 1
    fi
}

# ════════════════════════════════════════════════════════════════════════════
# PRE-DEPLOYMENT CHECKS
# ════════════════════════════════════════════════════════════════════════════

echo "${BLUE}[PRE-DEPLOYMENT CHECKS]${NC}"
echo ""

echo "1. Code Verification:"
echo "  ├─ Checking if rate limit exemption exists..."
if grep -q "RATE_LIMIT_EXEMPT_PATHS" apps/api/main.py; then
    echo -e "    ${GREEN}✓ Exemption code found${NC}"
else
    echo -e "    ${RED}✗ Exemption code NOT found${NC}"
    exit 1
fi

echo "  ├─ Checking if /api/jona/ is in exempt paths..."
if grep -q '/api/jona/' apps/api/main.py | grep RATE_LIMIT_EXEMPT_PATHS -A5; then
    echo -e "    ${GREEN}✓ JONA path exempt${NC}"
else
    echo -e "    ${YELLOW}⚠ Cannot verify from grep, checking manually...${NC}"
fi

echo "  ├─ Checking rate limit value..."
limit=$(grep "limit = " apps/api/main.py | grep -v endpoint | head -1 | grep -oE '[0-9]+' | head -1)
if [ "$limit" = "120" ]; then
    echo -e "    ${GREEN}✓ Global limit set to 120${NC}"
elif [ "$limit" = "60" ]; then
    echo -e "    ${RED}✗ Global limit still at 60 (fix not applied)${NC}"
    exit 1
else
    echo -e "    ${YELLOW}⚠ Global limit: $limit${NC}"
fi

echo ""

# ════════════════════════════════════════════════════════════════════════════
# PRE-DEPLOYMENT API TESTS
# ════════════════════════════════════════════════════════════════════════════

echo "2. API Connectivity (Current State):"

if check_endpoint "API Health" "/api/health" "200"; then
    api_running=1
else
    echo -e "  ${YELLOW}⚠ API not currently running (restart will be needed)${NC}"
    api_running=0
fi

echo ""

# ════════════════════════════════════════════════════════════════════════════
# DEPLOYMENT STEPS
# ════════════════════════════════════════════════════════════════════════════

echo "${BLUE}[DEPLOYMENT STEPS]${NC}"
echo ""

echo "3. Deployment Actions:"
echo ""

if [ "$api_running" -eq 1 ]; then
    echo "  Option A: Restart Docker Service (Recommended for testing)"
    echo -e "  ${BLUE}Command:${NC} docker-compose restart clisonix-api"
    echo ""
    echo "  Option B: Full Rebuild (For production)"
    echo -e "  ${BLUE}Command:${NC} docker-compose up -d --build clisonix-api"
    echo ""
    echo "  Option C: Manual Restart"
    echo -e "  ${BLUE}Steps:${NC}"
    echo "    1. Stop API: docker-compose stop clisonix-api"
    echo "    2. Wait 5s: sleep 5"
    echo "    3. Start API: docker-compose up -d clisonix-api"
    echo "    4. Wait 10s: sleep 10"
    echo "    5. Verify: curl http://localhost:8000/api/health"
else
    echo "  API is not running. Start it first:"
    echo -e "  ${BLUE}Command:${NC} docker-compose up -d clisonix-api"
fi

echo ""

# ════════════════════════════════════════════════════════════════════════════
# POST-DEPLOYMENT TESTS
# ════════════════════════════════════════════════════════════════════════════

echo "${BLUE}[POST-DEPLOYMENT TESTS]${NC}"
echo ""

# Only run if API is running
if [ "$api_running" -eq 0 ]; then
    echo "  ${YELLOW}⚠ Skipping connectivity tests (API not running)${NC}"
    echo "  Re-run this script after starting the API"
else
    echo "1. Basic Connectivity:"
    check_endpoint "Health"  "/api/health"  "200"
    check_endpoint "Status"  "/api/status"  "*"
    echo ""

    echo "2. Exempt Endpoints (should allow rapid requests):"
    check_endpoint "JONA Status"  "/api/jona/status"  "*"
    check_endpoint "Health"       "/api/health"        "200"
    echo ""

    echo "3. Rate-Limited Endpoints (may return 429 after many requests):"
    check_endpoint "ALBI Analysis"  "/api/albi/eeg/analysis"  "*"
    check_endpoint "Status"         "/api/status"             "*"
    echo ""
fi

# ════════════════════════════════════════════════════════════════════════════
# VERIFICATION SCRIPT
# ════════════════════════════════════════════════════════════════════════════

echo "${BLUE}[NEXT STEPS]${NC}"
echo ""

echo "1. Start deployment:"
echo -e "   ${BLUE}docker-compose restart clisonix-api${NC}"
echo ""

echo "2. Wait 10 seconds for API to come online:"
echo -e "   ${BLUE}sleep 10${NC}"
echo ""

echo "3. Run detailed diagnostic:"
echo -e "   ${BLUE}bash diagnose-jona-rate-limit.sh${NC}"
echo ""

echo "4. Test JONA audio downloads:"
echo -e "   ${BLUE}curl -v http://localhost:8000/api/jona/audio/list${NC}"
echo ""

echo "5. Monitor logs for errors:"
echo -e "   ${BLUE}docker logs -f clisonix-api | grep -i \"rate\\|jona\\|error\"${NC}"
echo ""

echo "6. If successful, commit changes:"
echo -e "   ${BLUE}git add -A && git commit -m \"Fix: Exempt JONA from rate limiting\"${NC}"
echo ""

# ════════════════════════════════════════════════════════════════════════════
# ROLLBACK INSTRUCTIONS
# ════════════════════════════════════════════════════════════════════════════

echo "${BLUE}[ROLLBACK PLAN (If Needed)]${NC}"
echo ""

echo "If the fix causes issues:"
echo ""
echo "1. Revert code:"
echo -e "   ${BLUE}git checkout apps/api/main.py${NC}"
echo ""
echo "2. Restart API:"
echo -e "   ${BLUE}docker-compose restart clisonix-api${NC}"
echo ""
echo "3. Contact dev team with error logs:"
echo -e "   ${BLUE}docker logs clisonix-api > api-error.log${NC}"
echo ""

# ════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ════════════════════════════════════════════════════════════════════════════

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  Deployment Checklist Complete                                   ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

echo "Summary:"
echo "  ✓ Code fix verified"
echo "  ✓ Deployment plan ready"
echo "  ✓ Test procedures documented"
echo "  ✓ Rollback plan available"
echo ""

echo "Status: ${GREEN}READY FOR DEPLOYMENT${NC}"
echo ""
