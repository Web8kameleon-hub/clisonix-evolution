#!/usr/bin/env bash
set -Eeuo pipefail

MODEL_TAG="${1:-}"
RESTART_OPENMIND="${2:-false}"

if [[ -z "${MODEL_TAG}" ]]; then
  echo "Usage: $0 <model-tag> [restart-openmind:true|false]"
  echo "Example: $0 clisonix-ocean:v2 true"
  exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "❌ ollama CLI not found"
  exit 1
fi

if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  echo "❌ docker compose not found"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

ENV_FILE="${ROOT_DIR}/.env"
[[ -f "${ENV_FILE}" ]] || touch "${ENV_FILE}"

echo "==> Ollama version"
ollama --version || true

echo "==> Installed models"
ollama list

if ! ollama list | awk 'NR>1 {print $1}' | grep -Fxq "${MODEL_TAG}"; then
  echo "❌ Model not found: ${MODEL_TAG}"
  echo "   Import first (Modelfile + ollama create) or pull from registry"
  exit 1
fi

backup_file="${ENV_FILE}.bak.$(date +%Y%m%d_%H%M%S)"
cp "${ENV_FILE}" "${backup_file}"
echo "==> Backed up .env to ${backup_file}"

upsert_env() {
  local key="$1"
  local value="$2"
  if grep -qE "^${key}=" "${ENV_FILE}"; then
    sed -i "s#^${key}=.*#${key}=${value}#" "${ENV_FILE}"
  else
    printf "%s=%s\n" "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

upsert_env "MODEL" "${MODEL_TAG}"
upsert_env "OPENMIND_MODEL" "${MODEL_TAG}"

echo "==> Pinned env vars"
grep -E '^(MODEL|OPENMIND_MODEL)=' "${ENV_FILE}" || true

echo "==> Preload model"
curl -sS "http://localhost:11434/api/generate" \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"${MODEL_TAG}\",\"prompt\":\"\",\"stream\":false}" \
  >/dev/null

echo "==> Rebuild/restart ocean-core only"
${COMPOSE_CMD} up -d --build ocean-core

if [[ "${RESTART_OPENMIND}" == "true" ]]; then
  echo "==> Restarting openmind"
  ${COMPOSE_CMD} up -d --build openmind || ${COMPOSE_CMD} up -d openmind || true
fi

echo "==> Smoke checks"
curl -fsS "http://localhost:8030/health" && echo
curl -fsS "http://localhost:8030/api/v1/status" && echo
curl -fsS "http://localhost:9999/status" && echo || true

echo "✅ Completed safely with MODEL=${MODEL_TAG}"