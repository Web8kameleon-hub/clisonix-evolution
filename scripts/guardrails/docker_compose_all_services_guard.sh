#!/usr/bin/env bash
set -euo pipefail

# Strict guardrail: deployment fails unless ALL compose services are running.
# Usage:
#   bash scripts/guardrails/docker_compose_all_services_guard.sh [compose_file] [env_file]

COMPOSE_FILE="${1:-compose-hosting.yml}"
ENV_FILE="${2:-}"
LIST_FILE="scripts/guardrails/compose-hosting.services.txt"
COMPOSE_PROFILES="${COMPOSE_PROFILES:-}"
EXPECTED_SERVICES_COUNT="${EXPECTED_SERVICES_COUNT:-}"

profile_args=()
if [[ -n "$COMPOSE_PROFILES" ]]; then
  IFS=',' read -r -a _profiles <<< "$COMPOSE_PROFILES"
  for _profile in "${_profiles[@]}"; do
    _clean="$(echo "$_profile" | xargs)"
    [[ -n "$_clean" ]] && profile_args+=(--profile "$_clean")
  done
fi

resolve_compose() {
  if docker compose version >/dev/null 2>&1; then
    echo "docker compose"
    return
  fi
  if command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
    return
  fi
  echo "Docker Compose not found" >&2
  exit 1
}

compose_run() {
  local compose_bin="$1"
  shift
  if [[ -n "$ENV_FILE" && -f "$ENV_FILE" ]]; then
    $compose_bin --env-file "$ENV_FILE" "${profile_args[@]}" -f "$COMPOSE_FILE" "$@"
  else
    $compose_bin "${profile_args[@]}" -f "$COMPOSE_FILE" "$@"
  fi
}

if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "❌ Guardrail failed: compose file not found: $COMPOSE_FILE"
  exit 1
fi

compose_bin="$(resolve_compose)"

expected_file="$(mktemp)"
running_file="$(mktemp)"
list_file_tmp="$(mktemp)"
trap 'rm -f "$expected_file" "$running_file" "$list_file_tmp"' EXIT

compose_run "$compose_bin" config --services | sed '/^$/d' | sort -u > "$expected_file"
compose_run "$compose_bin" ps --services --status running | sed '/^$/d' | sort -u > "$running_file"

if [[ -f "$LIST_FILE" ]]; then
  sed '/^$/d' "$LIST_FILE" | sort -u > "$list_file_tmp"
  list_diff_missing="$(comm -23 "$list_file_tmp" "$expected_file" || true)"
  list_diff_extra="$(comm -13 "$list_file_tmp" "$expected_file" || true)"
  if [[ -n "$list_diff_missing" || -n "$list_diff_extra" ]]; then
    echo "❌ Guardrail failed: compose service set differs from canonical list"
    echo "   compose_file=$COMPOSE_FILE"
    echo "   canonical_list=$LIST_FILE"
    if [[ -n "$list_diff_missing" ]]; then
      echo "   listed_but_not_in_compose:"
      while IFS= read -r svc; do
        [[ -n "$svc" ]] && echo "   - $svc"
      done <<< "$list_diff_missing"
    fi
    if [[ -n "$list_diff_extra" ]]; then
      echo "   in_compose_but_not_listed:"
      while IFS= read -r svc; do
        [[ -n "$svc" ]] && echo "   - $svc"
      done <<< "$list_diff_extra"
    fi
    exit 1
  fi
fi

missing="$(comm -23 "$expected_file" "$running_file" || true)"

expected_count="$(wc -l < "$expected_file" | tr -d ' ')"
running_count="$(wc -l < "$running_file" | tr -d ' ')"

if [[ -n "$EXPECTED_SERVICES_COUNT" && "$expected_count" != "$EXPECTED_SERVICES_COUNT" ]]; then
  echo "❌ Guardrail failed: compose service count does not match required target"
  echo "   compose_file=$COMPOSE_FILE"
  echo "   required_count=$EXPECTED_SERVICES_COUNT"
  echo "   resolved_count=$expected_count"
  if [[ -n "$COMPOSE_PROFILES" ]]; then
    echo "   profiles=$COMPOSE_PROFILES"
  fi
  exit 1
fi

if [[ -n "$missing" ]]; then
  echo "❌ Guardrail failed: not all compose services are running"
  echo "   compose_file=$COMPOSE_FILE"
  echo "   expected_services=$expected_count"
  echo "   running_services=$running_count"
  echo "   missing_services:"
  while IFS= read -r svc; do
    [[ -n "$svc" ]] && echo "   - $svc"
  done <<< "$missing"
  exit 1
fi

echo "✅ Guardrail passed: all compose services are running ($running_count/$expected_count)"
