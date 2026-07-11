#!/usr/bin/env bash
# 🔐 Pre-commit Hook - Prevents committing secrets
# Install: cp scripts/pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

echo "🔍 Running pre-commit security checks..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Patterns to block
PATTERNS=(
    'password.*=.*[^$]'
    'api[_-]?key.*=.*[^$]'
    'secret.*=.*[^$]'
    'token.*=.*[^$]'
    'AKIA[0-9A-Z]{16}'
    'sk_(test|live)_[0-9a-zA-Z]{24,}'
    'ghp_[0-9a-zA-Z]{36}'
    '[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}'
    '-----BEGIN\s+(RSA\s+)?PRIVATE KEY-----'
)

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    echo "✅ No files to check"
    exit 0
fi

# Check for secrets
FOUND_SECRETS=0

for FILE in $STAGED_FILES; do
    # Skip binary files
    if file "$FILE" | grep -q "binary"; then
        continue
    fi
    
    # Skip .gitignore and template files
    if [[ "$FILE" == ".gitignore" ]] || [[ "$FILE" == *.template ]] || [[ "$FILE" == *.example ]]; then
        continue
    fi
    
    # Check each pattern
    for PATTERN in "${PATTERNS[@]}"; do
        if grep -E -i "$PATTERN" "$FILE" > /dev/null 2>&1; then
            if [ $FOUND_SECRETS -eq 0 ]; then
                echo -e "${RED}❌ COMMIT BLOCKED: Potential secrets detected!${NC}\n"
            fi
            echo -e "${YELLOW}File: $FILE${NC}"
            grep -E -i -n --color=always "$PATTERN" "$FILE" || true
            echo ""
            FOUND_SECRETS=1
        fi
    done
done

# Check if .secrets or secrets/ are being committed
if echo "$STAGED_FILES" | grep -E '(^\.secrets$|^secrets/)' > /dev/null; then
    echo -e "${RED}❌ COMMIT BLOCKED: Attempting to commit secrets file!${NC}"
    echo -e "${YELLOW}Files:${NC}"
    echo "$STAGED_FILES" | grep -E '(^\.secrets$|^secrets/)'
    FOUND_SECRETS=1
fi

if [ $FOUND_SECRETS -eq 1 ]; then
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}COMMIT BLOCKED FOR SECURITY REASONS${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Please:"
    echo "  1. Remove hardcoded secrets from files"
    echo "  2. Use .secrets file or Docker secrets instead"
    echo "  3. Add sensitive files to .gitignore"
    echo ""
    echo "To bypass this check (NOT RECOMMENDED):"
    echo "  git commit --no-verify"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Pre-commit security check passed${NC}"
exit 0

