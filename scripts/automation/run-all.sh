#!/bin/bash
# Ekzekuton TË GJITHA automatikisht — No fake ever.
set -e

cd /opt/clisonix.com

echo "=========================================="
echo "CLISONIX AUTOMATION — TË GJITHA"
echo "=========================================="
echo ""

# 1. Changelog
echo "=== 1. CHANGELOG ==="
bash scripts/automation/changelog.sh
echo ""

# 2. Benchmarks
echo "=== 2. BENCHMARKS ==="
bash scripts/automation/benchmarks.sh
echo ""

# 3. Edge Cases
echo "=== 3. EDGE CASES ==="
bash scripts/automation/edge-cases.sh
echo ""

# 4. Test vs Test
echo "=== 4. TEST VS TEST ==="
bash scripts/automation/test-vs-test.sh
echo ""

# 5. Verify
echo "=== 5. VERIFY ==="
bash scripts/automation/verify.sh
echo ""

# 6. Commit
echo "=== 6. COMMIT ==="
bash scripts/automation/commit.sh
echo ""

# 7. Release
echo "=== 7. RELEASE ==="
bash scripts/automation/release.sh
echo ""

echo "=========================================="
echo "TË GJITHA U KRYEN"
echo "=========================================="
