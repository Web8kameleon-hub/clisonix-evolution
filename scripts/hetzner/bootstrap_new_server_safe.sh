#!/usr/bin/env bash
set -Eeuo pipefail

# Safe bootstrap for a fresh Hetzner Ubuntu server.
# Intentionally does NOT modify sshd_config or enable ufw.
# Usage:
#   bash scripts/hetzner/bootstrap_new_server_safe.sh [/root/Clisonix-cloud]

PROJECT_DIR="${1:-/root/Clisonix-cloud}"
BRANCH="${DEPLOY_BRANCH:-main}"

log() {
  printf '[SAFE_BOOTSTRAP] %s\n' "$*"
}

require_root() {
  if [ "$(id -u)" -ne 0 ]; then
    log "Run as root."
    exit 1
  fi
}

install_docker_ubuntu_noble() {
  log "Installing Docker (Ubuntu noble)"
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg lsb-release git

  install -m 0755 -d /etc/apt/keyrings
  if [ ! -f /etc/apt/keyrings/docker.gpg ]; then
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
  fi
  chmod a+r /etc/apt/keyrings/docker.gpg

  cat >/etc/apt/sources.list.d/docker.list <<'EOF'
deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu noble stable
EOF

  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable docker
  systemctl restart docker

  docker --version
  docker compose version
}

sync_repo() {
  log "Syncing repository to ${PROJECT_DIR}"
  if [ ! -d "${PROJECT_DIR}/.git" ]; then
    git clone https://github.com/Web8kameleon-hub/clisonix.com.git "${PROJECT_DIR}"
  fi

  cd "${PROJECT_DIR}"
  git fetch origin "${BRANCH}" --prune
  git checkout "${BRANCH}" 2>/dev/null || git checkout -b "${BRANCH}" "origin/${BRANCH}"
  git reset --hard "origin/${BRANCH}"

  log "Repository ready at $(pwd)"
  log "Commit: $(git rev-parse --short HEAD)"
}

show_next_steps() {
  log "Done. Next safe steps:"
  log "1) Add real env file (no placeholders): ${PROJECT_DIR}/.env"
  log "2) Start only required services first, example:"
  log "   cd ${PROJECT_DIR} && docker compose --env-file .env up -d api ocean-core"
  log "3) Verify health endpoints before adding traffic."
  log "4) Keep old server live until health checks pass (zero-downtime cutover)."
}

main() {
  require_root
  install_docker_ubuntu_noble
  sync_repo
  show_next_steps
}

main "$@"
