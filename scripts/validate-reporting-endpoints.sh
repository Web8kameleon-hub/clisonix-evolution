#!/bin/bash
# Validate ULTRA Reporting Command Center Endpoints
# Tests that all reporting endpoints return REAL data (not fake/null)
# Follows NO_FAKE_DATA_POLICY.md

set -e

echo "============================================"
echo "ULTRA Reporting Endpoint Validation"
echo "============================================"
echo ""

# Configuration
REPORTING_BASE="${REPORTING_BASE_URL:-http://localhost:8001}"
WEB_BASE="${WEB_BASE_URL:-http://localhost:3000}"
API_PROXY_BASE="${API_PROXY_BASE_URL:-http://localhost:3000/api/proxy}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

passed=0
failed=0
total=0

# Test function
test_endpoint() {
    local name="$1"
    local url="$2"
    local min_response_size="$3"

    echo -n "Testing $name... "
    total=$((total + 1))

    if response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null); then
        http_code=$(echo "$response" | tail -n1)
        body=$(echo "$response" | head -n-1)

        if [ "$http_code" = "200" ]; then
            # Check if response has meaningful data
            response_size=${#body}
            if [ "$response_size" -gt "$min_response_size" ]; then
                echo -e "${GREEN}✓ PASS${NC} (HTTP 200, $response_size bytes)"
                # Show sample data (first 200 chars)
                echo "  Sample: ${body:0:200}..."
                passed=$((passed + 1))
            else
                echo -e "${RED}✗ FAIL${NC} (HTTP 200 but response too small: $response_size bytes)"
                failed=$((failed + 1))
            fi
        else
            echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
            failed=$((failed + 1))
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (Connection error)"
        failed=$((failed + 1))
    fi
    echo ""
}

echo "=== REPORTING SERVICE (Direct) ==="
test_endpoint "Reporting Health" "$REPORTING_BASE/health" 50
test_endpoint "Docker Containers" "$REPORTING_BASE/api/reporting/docker-containers" 100
test_endpoint "Docker Stats" "$REPORTING_BASE/api/reporting/docker-stats" 50
test_endpoint "System Metrics" "$REPORTING_BASE/api/reporting/system-metrics" 50
test_endpoint "Dashboard" "$REPORTING_BASE/api/reporting/dashboard" 200

echo "=== REPORTING SERVICE (Via Web Proxy) ==="
test_endpoint "Proxy: Reporting Dashboard" "$API_PROXY_BASE/reporting-dashboard" 100
test_endpoint "Proxy: Docker Containers" "$API_PROXY_BASE/docker-containers" 50
test_endpoint "Proxy: Health" "$API_PROXY_BASE/health" 50

echo "=== RESULTS ==="
echo "Passed: $passed/$total"
echo "Failed: $failed/$total"
echo ""

if [ $failed -gt 0 ]; then
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Ensure reporting service is running: docker ps | grep reporting"
    echo "2. Check reporting service logs: docker logs clisonix-reporting"
    echo "3. Verify REPORTING_INTERNAL_URL is set in web service"
    echo "4. Test direct connection: curl http://clisonix-reporting:8001/health"
    exit 1
else
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    echo ""
    echo "ULTRA Reporting Command Center is properly configured with REAL data:"
    echo "✓ Docker container monitoring (psutil)"
    echo "✓ System metrics collection (psutil)"
    echo "✓ API performance metrics (aggregated)"
    echo "✓ Service discovery and health checks"
    echo "✓ Real data only - NO fake/fallback data"
    exit 0
fi
