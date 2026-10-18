#!/usr/bin/env bash
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/opt/clisonix.com}"
COMPOSE_FILE="${SWARM_COMPOSE_FILE:-compose-hosting.yml}"
ENV_FILE="${SWARM_ENV_FILE:-.env.production}"
STACK_NAME="${SWARM_STACK_NAME:-clisonix-next}"
OVERLAY_NETWORK="${SWARM_NETWORK:-clisonix-swarm}"
SERVICES_CSV="${SWARM_SERVICES:-longo,web,api,jona,ocean-core,ocean-core-multimodal,kloud-upstream-runtime,kloud-bridge,curiosity,user-management}"
MIGRATE_LEGACY="${SWARM_MIGRATE_LEGACY:-false}"
HEALTH_ATTEMPTS="${SWARM_HEALTH_ATTEMPTS:-90}"

log() {
  printf '\n==> %s\n' "$1"
}

compose() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

wait_for_service() {
  local service_name="$1"
  local full_name="${STACK_NAME}_${service_name}"
  local attempt

  for attempt in $(seq 1 "$HEALTH_ATTEMPTS"); do
    local desired
    local running
    desired="$(docker service inspect "$full_name" --format '{{.Spec.Mode.Replicated.Replicas}}' 2>/dev/null || echo 0)"
    running="$(docker service ps "$full_name" --filter desired-state=running --format '{{.CurrentState}}' 2>/dev/null | grep -c '^Running' || true)"
    if [[ "$desired" -gt 0 && "$running" -eq "$desired" ]]; then
      local unhealthy="false"
      while read -r container_id; do
        [[ -n "$container_id" ]] || continue
        local health
        health="$(docker inspect "$container_id" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}missing{{end}}')"
        if [[ "$health" != "healthy" ]]; then
          unhealthy="true"
          break
        fi
      done < <(
        docker service ps "$full_name" \
          --filter desired-state=running \
          --format '{{.ID}}' |
          xargs -r docker inspect --format '{{.Status.ContainerStatus.ContainerID}}'
      )
      if [[ "$unhealthy" == "false" ]]; then
        echo "✅ $service_name is healthy in Swarm"
        return 0
      fi
    fi
    sleep 4
  done

  echo "❌ $service_name did not become healthy"
  docker service ps "$full_name" --no-trunc || true
  while read -r container_id; do
    [[ -n "$container_id" ]] || continue
    echo "--- logs: $container_id ---"
    docker logs --tail 100 "$container_id" 2>&1 || true
  done < <(
    docker service ps "$full_name" --no-trunc --format '{{.Status.ContainerStatus.ContainerID}}' |
      awk 'NF && !seen[$0]++'
  )
  return 1
}

main() {
  cd "$DEPLOY_PATH"
  export HETZNER_DEPLOY=1
  log "Enforcing production truth gate"
  bash scripts/guardrails/no_fake_fallback_gate.sh "$DEPLOY_PATH"
  python scripts/guardrails/repo_integrity_guard.py
  [[ -f "$ENV_FILE" ]] || {
    echo "Missing environment file: $ENV_FILE"
    exit 1
  }

  log "Validate required production secrets"
  if ! grep -Eq '^(AUTH_SECRET|NEXTAUTH_SECRET)=.+' "$ENV_FILE"; then
    echo "Missing AUTH_SECRET or NEXTAUTH_SECRET in $ENV_FILE"
    exit 1
  fi
  for key in MINIO_ROOT_USER MINIO_ROOT_PASSWORD; do
    if ! grep -Eq "^${key}=.+" "$ENV_FILE"; then
      echo "Missing required value in $ENV_FILE: $key"
      exit 1
    fi
  done
  if ! grep -Eq '^NEO4J_AUTH=.+' "$ENV_FILE" &&
    ! { grep -Eq '^NEO4J_USER=.+' "$ENV_FILE" && grep -Eq '^NEO4J_PASSWORD=.+' "$ENV_FILE"; }; then
    echo "Missing NEO4J_AUTH or NEO4J_USER/NEO4J_PASSWORD in $ENV_FILE"
    exit 1
  fi

  local services=()
  read -r -a services <<<"${SERVICES_CSV//,/ }"

  log "Validate and build selected service images"
  compose config -q
  compose build "${services[@]}"

  local work_dir
  work_dir="$(mktemp -d)"
  trap "rm -f '$work_dir/compose.json' '$work_dir/stack.json' '$work_dir/legacy.json'; rmdir '$work_dir' 2>/dev/null || true" EXIT
  compose config --format json >"$work_dir/compose.json"
  python3 scripts/render-swarm-stack.py \
    --input "$work_dir/compose.json" \
    --output "$work_dir/stack.json" \
    --mapping-output "$work_dir/legacy.json" \
    --services "$SERVICES_CSV" \
    --network "$OVERLAY_NETWORK"
  chmod 600 "$work_dir/compose.json" "$work_dir/stack.json"

  if [[ "$(docker info --format '{{.Swarm.LocalNodeState}}')" == "inactive" ]]; then
    log "Initialize single-node Swarm"
    docker swarm init --advertise-addr "$(hostname -I | awk '{print $1}')"
  fi

  docker network inspect "$OVERLAY_NETWORK" >/dev/null 2>&1 ||
    docker network create --driver overlay --attachable "$OVERLAY_NETWORK"

  log "Attach existing stateful dependencies to the private overlay"
  for dependency in redis ollama; do
    container="clisonix-${dependency}"
    if docker inspect "$container" >/dev/null 2>&1; then
      docker network connect --alias "$dependency" --alias "$container" "$OVERLAY_NETWORK" "$container" 2>/dev/null || true
    fi
  done
  if docker inspect clisonix-nginx >/dev/null 2>&1; then
    docker network connect "$OVERLAY_NETWORK" clisonix-nginx 2>/dev/null || true
  fi

  log "Deploy shadow stack with start-first rolling updates"
  docker stack deploy --resolve-image never -c "$work_dir/stack.json" "$STACK_NAME"

  for service in "${services[@]}"; do
    wait_for_service "$service"
  done

  if [[ "$MIGRATE_LEGACY" != "true" ]]; then
    echo "✅ Shadow stack is healthy. Legacy containers remain active."
    echo "Set SWARM_MIGRATE_LEGACY=true only after ingress validation."
    return
  fi

  log "Remove healthy legacy instances from service discovery"
  while IFS='|' read -r service container; do
    [[ -n "$container" ]] || continue
    if docker inspect "$container" >/dev/null 2>&1; then
      docker rm -f "$container"
      echo "✅ Migrated $service from $container"
    fi
  done < <(python3 - "$work_dir/legacy.json" <<'PY'
import json
import sys
for service, container in json.load(open(sys.argv[1], encoding="utf-8")).items():
    print(f"{service}|{container}")
PY
  )

  echo "🎉 Swarm migration complete"
}

main "$@"
