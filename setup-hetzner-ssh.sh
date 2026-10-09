#!/bin/bash
# 🔑 Clisonix Hetzner SSH Setup Helper
# Automatizo gjenerimin e SSH keys dhe konfigurimin
# Përdorë: bash setup-hetzner-ssh.sh

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🔑 CLISONIX HETZNER SSH SETUP                                ║"
echo "║     Auto-generates SSH keys and configures access             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SSH_DIR="$HOME/.ssh"
HETZNER_KEY="$SSH_DIR/hetzner_deploy_key"
SSH_CONFIG="$SSH_DIR/config"
KEY_COMMENT="Clisonix Hetzner Deploy Key"

# ═══════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════
# STEP 1: Create SSH directory
# ═══════════════════════════════════════════════════════════════════════════

log_info "Checking SSH directory..."
if [ ! -d "$SSH_DIR" ]; then
    log_info "Creating SSH directory..."
    mkdir -p "$SSH_DIR"
    chmod 700 "$SSH_DIR"
    log_success "SSH directory created"
else
    log_success "SSH directory exists"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 2: Generate SSH key
# ═══════════════════════════════════════════════════════════════════════════

echo ""
log_info "SSH Key Generation"

if [ -f "$HETZNER_KEY" ]; then
    log_warning "SSH key already exists at: $HETZNER_KEY"
    read -p "Do you want to regenerate it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Skipping key generation"
        KEY_GENERATED=0
    else
        log_info "Backing up existing key..."
        cp "$HETZNER_KEY" "$HETZNER_KEY.backup.$(date +%Y%m%d_%H%M%S)"
        log_success "Backup created"
        KEY_GENERATED=1
    fi
else
    KEY_GENERATED=1
fi

if [ $KEY_GENERATED -eq 1 ]; then
    log_info "Generating SSH key (RSA 4096)..."
    ssh-keygen -t rsa -b 4096 -f "$HETZNER_KEY" -N "" -C "$KEY_COMMENT"

    # Fix permissions
    chmod 600 "$HETZNER_KEY"
    chmod 644 "$HETZNER_KEY.pub"

    log_success "SSH key generated successfully"
    echo "   Private key: $HETZNER_KEY"
    echo "   Public key:  $HETZNER_KEY.pub"
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 3: Display public key
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
log_info "Your Public Key (add to Hetzner console):"
echo "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
cat "$HETZNER_KEY.pub"
echo "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"

# Copy to clipboard (if available)
if command -v xclip &> /dev/null; then
    cat "$HETZNER_KEY.pub" | xclip -selection clipboard
    log_success "Public key copied to clipboard"
elif command -v pbcopy &> /dev/null; then
    cat "$HETZNER_KEY.pub" | pbcopy
    log_success "Public key copied to clipboard"
fi

echo ""
read -p "Press ENTER after adding the key to Hetzner console..."

# ═══════════════════════════════════════════════════════════════════════════
# STEP 4: Test SSH connection
# ═══════════════════════════════════════════════════════════════════════════

echo ""
log_info "Testing SSH connection..."
read -p "Enter Hetzner server IP (or press ENTER to skip): " HETZNER_IP

if [ -z "$HETZNER_IP" ]; then
    log_warning "Skipping connection test"
else
    log_info "Testing connection to $HETZNER_IP..."
    if ssh -i "$HETZNER_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@"$HETZNER_IP" "echo 'SSH connection OK'" &>/dev/null; then
        log_success "SSH connection successful!"
    else
        log_warning "SSH connection failed. Please verify:"
        echo "   1. Server IP is correct"
        echo "   2. SSH key is added to Hetzner console"
        echo "   3. Server has finished initializing (wait 2-3 minutes)"
        echo "   4. Firewall allows port 22"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════
# STEP 5: Update SSH config
# ═══════════════════════════════════════════════════════════════════════════

echo ""
log_info "Updating SSH config..."

if [ -f "$SSH_CONFIG" ]; then
    log_warning "SSH config already exists"
    read -p "Do you want to update it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$SSH_CONFIG" "$SSH_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
        log_success "Backup created: $SSH_CONFIG.backup"
    else
        log_info "Skipping SSH config update"
        exit 0
    fi
fi

# Create SSH config entry
cat >> "$SSH_CONFIG" << EOF

# ═══════════════════════════════════════════════════════════════════════════
# CLISONIX HETZNER SERVERS
# Added: $(date)
# ═══════════════════════════════════════════════════════════════════════════

Host hetzner-prod
    HostName 46.225.14.83
    User root
    Port 22
    IdentityFile $HETZNER_KEY
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    AddKeysToAgent yes
    ConnectTimeout 10
    ServerAliveInterval 60
    Compression yes

Host hetzner-new
    HostName $HETZNER_IP
    User root
    Port 22
    IdentityFile $HETZNER_KEY
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    AddKeysToAgent yes
    ConnectTimeout 10
    ServerAliveInterval 60
    Compression yes
EOF

chmod 600 "$SSH_CONFIG"
log_success "SSH config updated"

# ═══════════════════════════════════════════════════════════════════════════
# STEP 6: Add key to SSH agent
# ═══════════════════════════════════════════════════════════════════════════

echo ""
log_info "Adding key to SSH agent..."

if ssh-add "$HETZNER_KEY" 2>/dev/null; then
    log_success "Key added to SSH agent"
else
    log_warning "SSH agent not available"
    log_info "You can manually add it later with:"
    echo "   ssh-add $HETZNER_KEY"
fi

# ═══════════════════════════════════════════════════════════════════════════
# COMPLETION SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo "${GREEN}║  ✓ SSH SETUP COMPLETE                                         ║${NC}"
echo "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_success "SSH key generated: $HETZNER_KEY"
log_success "SSH config updated: $SSH_CONFIG"
log_success "Key added to SSH agent"

echo ""
echo "📝 Next steps:"
echo ""
echo "1. Add public key to Hetzner console:"
echo "   https://console.hetzner.com → SSH Keys"
echo ""
echo "2. Create new server with the SSH key selected"
echo ""
echo "3. Connect to server:"
echo "   ssh hetzner-prod     # Production server"
echo "   ssh hetzner-new      # New server (if IP was provided)"
echo ""
echo "4. Verify connection:"
echo "   ssh hetzner-prod 'docker ps'"
echo ""
echo "5. For more setup instructions, see:"
echo "   HETZNER_SSH_SETUP.md"
echo ""
