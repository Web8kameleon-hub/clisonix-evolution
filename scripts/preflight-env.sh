#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-.env.production}"
SKIP_COMPOSE_VALIDATION="${SKIP_COMPOSE_VALIDATION:-0}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ ! -f "${ENV_FILE}" ]]; then
  if [[ -f "${REPO_ROOT}/${ENV_FILE}" ]]; then
    ENV_FILE="${REPO_ROOT}/${ENV_FILE}"
  else
    echo "[FAIL] Env file not found: ${ENV_FILE}" >&2
    echo "Create it from .env.production.template first." >&2
    exit 1
  fi
fi

required=(
  POSTGRES_PASSWORD
  MONGO_ROOT_PASSWORD
  NEO4J_PASSWORD
  MINIO_ROOT_PASSWORD
  GRAFANA_ADMIN_PASSWORD
  KITCHEN_RUN_API_KEY
)

placeholder_patterns=(
  "REPLACE_WITH_"
  "CHANGE_ME"
  "your-"
  "example"
  "admin123"
  "test123"
)

get_env_value() {
  local key="$1"
  local line
  line="$(grep -E "^${key}=" "${ENV_FILE}" | tail -n 1 || true)"
  if [[ -z "${line}" ]]; then
    echo ""
  else
    echo "${line#*=}"
  fi
}

missing=()
weak=()

for key in "${required[@]}"; do
  value="$(get_env_value "${key}")"
  if [[ -z "${value}" ]]; then
    missing+=("${key}")
    continue
  fi

  for p in "${placeholder_patterns[@]}"; do
    if [[ "${value}" == *"${p}"* ]]; then
      weak+=("${key}")
      break
    fi
  done
done

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "[FAIL] Missing required variables:" >&2
  for k in "${missing[@]}"; do
    echo "  - ${k}" >&2
  done
  exit 1
fi

if [[ ${#weak[@]} -gt 0 ]]; then
  echo "[FAIL] Placeholder or weak values detected:" >&2
  printf '%s\n' "${weak[@]}" | sort -u | sed 's/^/  - /' >&2
  exit 1
fi

echo "[OK] Required env variables are present and non-placeholder."

clisonix_env_file="$(get_env_value "CLISONIX_ENV_FILE")"
if [[ -n "${clisonix_env_file}" && "${clisonix_env_file}" != ".env.production" ]]; then
  echo "[WARN] CLISONIX_ENV_FILE in env file is '${clisonix_env_file}'. Expected '.env.production'."
fi

if [[ "${SKIP_COMPOSE_VALIDATION}" != "1" ]]; then
  pushd "${REPO_ROOT}" >/dev/null
  CLISONIX_ENV_FILE=.env.production docker compose --env-file "${ENV_FILE}" config >/dev/null
  popd >/dev/null
  echo "[OK] docker compose config validation passed."
fi

echo "Preflight env check passed."
