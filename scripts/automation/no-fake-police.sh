#!/bin/bash
# No Fake Police — No fake ever.
set -e

cd /opt/clisonix.com

echo "=========================================="
echo "NO FAKE POLICE"
echo "=========================================="
echo ""

FAIL=0

# 1. MOCK IN PRODUCTION
echo "=== 1. MOCK IN PRODUCTION ==="
MOCK=$(grep -rn "unittest.mock\|MagicMock\|AsyncMock\|@patch" \
    --include="*.py" \
    --exclude-dir=".venv" \
    --exclude-dir="node_modules" \
    --exclude-dir="__pycache__" \
    --exclude-dir="tests" \
    --exclude-dir="test" \
    . 2>/dev/null | grep -v "test_" | wc -l)
echo "Mock: $MOCK"
[ "$MOCK" -gt 0 ] && { echo "❌ FAIL"; FAIL=1; } || echo "✅ PASS"
echo ""

# 2. PLACEHOLDER
echo "=== 2. PLACEHOLDER ==="
PLACEHOLDER=$(grep -rn "placeholder\|PLACEHOLDER" \
    --include="*.py" \
    --exclude-dir=".venv" \
    --exclude-dir="node_modules" \
    --exclude-dir="__pycache__" \
    --exclude-dir="tests" \
    . 2>/dev/null | grep -v "no fake\|no_fake\|Never produce fake\|Do not output\|is_placeholder\|has_placeholder\|PLACEHOLDER_CONTENT" | wc -l)
echo "Placeholder: $PLACEHOLDER"
[ "$PLACEHOLDER" -gt 0 ] && { echo "❌ FAIL"; FAIL=1; } || echo "✅ PASS"
echo ""

# 3. TODO/FIXME
echo "=== 3. TODO/FIXME ==="
TODO=$(grep -rn "TODO\|FIXME" \
    --include="*.py" \
    --exclude-dir=".venv" \
    --exclude-dir="node_modules" \
    --exclude-dir="__pycache__" \
    . 2>/dev/null | grep -v "TODO_FIXME\|code_analyzer\|Contains TODO" | wc -l)
echo "TODO/FIXME: $TODO"
[ "$TODO" -gt 0 ] && echo "⚠️  WARN"
echo ""

# 4. HARDCODED STATUS
echo "=== 4. HARDCODED STATUS ==="
HARDCODED=$(grep -rn 'return {"status": "active"\|return {"status": "ok", "data":' \
    --include="*.py" \
    --exclude-dir=".venv" \
    --exclude-dir="node_modules" \
    --exclude-dir="__pycache__" \
    --exclude-dir="tests" \
    . 2>/dev/null | wc -l)
echo "Hardcoded: $HARDCODED"
[ "$HARDCODED" -gt 0 ] && { echo "❌ FAIL"; FAIL=1; } || echo "✅ PASS"
echo ""

# 5. SILENT FAIL
echo "=== 5. SILENT FAIL ==="
SILENT=$(grep -rn "except:.*pass\|except Exception:.*pass" \
    --include="*.py" \
    --exclude-dir=".venv" \
    --exclude-dir="node_modules" \
    --exclude-dir="__pycache__" \
    . 2>/dev/null | wc -l)
echo "Silent fail: $SILENT"
[ "$SILENT" -gt 0 ] && { echo "❌ FAIL"; FAIL=1; } || echo "✅ PASS"
echo ""

# 6. RETURN NONE
echo "=== 6. RETURN NONE ==="
NONE=$(grep -rn "return None$" \
    --include="*.py" \
    --exclude-dir=".venv" \
    --exclude-dir="node_modules" \
    --exclude-dir="__pycache__" \
    --exclude-dir="tests" \
    . 2>/dev/null | wc -l)
echo "Return None: $NONE"
[ "$NONE" -gt 0 ] && echo "⚠️  WARN"
echo ""

echo "=========================================="
if [ "$FAIL" -eq 1 ]; then
    echo "❌ NO FAKE POLICE: FAIL"
    exit 1
else
    echo "✅ NO FAKE POLICE: PASS"
fi
echo "=========================================="
