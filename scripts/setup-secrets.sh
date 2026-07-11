#!/bin/bash
# 🔐 Setup Docker Secrets (Linux/Mac)
# Creates secret files from .secrets file

set -e

echo -e "\n🔐 Docker Secrets Setup Script"
echo "================================"

# Check if .secrets file exists
if [ ! -f ".secrets" ]; then
    echo -e "\n❌ Error: .secrets file not found!"
    echo -e "\nPlease create .secrets file first:"
    echo "  1. Copy .secrets.template to .secrets"
    echo "  2. Fill in all secret values"
    echo "  3. Run this script again\n"
    exit 1
fi

# Create secrets directory
mkdir -p secrets
echo "✓ Created secrets/ directory"

# Load .secrets file
echo -e "\n📖 Reading .secrets file..."
source .secrets

# Required secrets
declare -A SECRETS=(
    ["postgres_password"]="$POSTGRES_PASSWORD"
    ["redis_password"]="$REDIS_PASSWORD"
    ["minio_root_password"]="$MINIO_ROOT_PASSWORD"
    ["elasticsearch_password"]="$ELASTICSEARCH_PASSWORD"
    ["grafana_admin_password"]="$GF_SECURITY_ADMIN_PASSWORD"
    ["jwt_secret_key"]="$JWT_SECRET_KEY"
    ["stripe_secret_key"]="$STRIPE_SECRET_KEY"
    ["sepa_iban"]="$SEPA_IBAN"
)

echo "✓ Found ${#SECRETS[@]} secrets"

# Create secret files
echo -e "\n📝 Creating secret files...\n"

created=0
errors=0

for secret_name in "${!SECRETS[@]}"; do
    value="${SECRETS[$secret_name]}"
    file_path="secrets/${secret_name}.txt"
    
    if [ -z "$value" ]; then
        echo "  ❌ Missing: $secret_name"
        ((errors++))
    else
        echo -n "$value" > "$file_path"
        chmod 600 "$file_path"
        echo "  ✓ Created: $secret_name"
        ((created++))
    fi
done

echo -e "\n================================"
echo "✓ Created: $created"
echo "❌ Errors: $errors"

if [ $errors -gt 0 ]; then
    echo -e "\n⚠️  Some secrets are missing. Please add them to .secrets file.\n"
    exit 1
fi

echo -e "\n✅ All secrets configured successfully!\n"
echo "Next steps:"
echo "  1. Verify secrets/ directory is in .gitignore"
echo "  2. Run: docker-compose -f docker-compose.secrets.yml up -d\n"

