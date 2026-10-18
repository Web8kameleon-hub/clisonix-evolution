#!/usr/bin/env bash
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/opt/clisonix.com}"
STACK_NAME="${SWARM_STACK_NAME:-clisonix-next}"
NETWORK_NAME="${SWARM_NETWORK:-clisonix-swarm}"
VISION_MODEL="${CLXI_VISION_MODEL:-llava:7b}"
TEXT_MODEL="${CLX_TEXT_MODEL:-llama3.1:8b}"
OLLAMA_CONTAINER="${OLLAMA_CONTAINER:-clisonix-ollama}"
MIN_FREE_GB="${CLXI_MIN_FREE_GB:-8}"

cd "$DEPLOY_PATH"
COMMIT_SHA="$(git rev-parse --short=12 HEAD)"
AGENT_IMAGE="clisonix-clx-agent:deploy-${COMMIT_SHA}"
CLXI_IMAGE="clisonix-clx-i:deploy-${COMMIT_SHA}"
HYBRID_IMAGE="clisonix-clx-hybrid:deploy-${COMMIT_SHA}"
AI_GLOBAL_IMAGE="clisonix-ai-global-9999:deploy-${COMMIT_SHA}"

docker network inspect "$NETWORK_NAME" >/dev/null 2>&1 ||
  docker network create --driver overlay --attachable "$NETWORK_NAME"

docker inspect "$OLLAMA_CONTAINER" >/dev/null
[[ "$(docker inspect -f '{{.State.Running}}' "$OLLAMA_CONTAINER")" == "true" ]]
docker network connect --alias ollama --alias clisonix-ollama "$NETWORK_NAME" "$OLLAMA_CONTAINER" 2>/dev/null || true

ensure_model() {
  local model="$1"
  if ! docker exec "$OLLAMA_CONTAINER" ollama list |
    awk 'NR > 1 {print $1}' |
    grep -Eq "^(${model}|${model%%:*}(:|$))"; then
    free_gb="$(df -Pk "$DEPLOY_PATH" | awk 'NR==2 {print int($4/1024/1024)}')"
    if (( free_gb < MIN_FREE_GB )); then
      echo "Insufficient disk for required model: ${free_gb}GB free, ${MIN_FREE_GB}GB required"
      exit 1
    fi
    docker exec "$OLLAMA_CONTAINER" ollama pull "$model"
  fi

  docker exec "$OLLAMA_CONTAINER" ollama list |
    awk 'NR > 1 {print $1}' |
    grep -Eq "^(${model}|${model%%:*}(:|$))"
}

ensure_model "$TEXT_MODEL"
ensure_model "$VISION_MODEL"

docker build --build-arg HETZNER_DEPLOY=1 -f Dockerfile.clx-agent -t "$AGENT_IMAGE" .
docker build -f Dockerfile.clx-i -t "$CLXI_IMAGE" .
docker build --build-arg HETZNER_DEPLOY=1 -f Dockerfile.clx-hybrid -t "$HYBRID_IMAGE" .
docker build -f services/ai-global-9999/Dockerfile -t "$AI_GLOBAL_IMAGE" services/ai-global-9999

docker volume create clx_memory >/dev/null
docker volume create clx_i_data >/dev/null

upsert_service() {
  local service="$1"
  local image="$2"
  shift 2
  if docker service inspect "$service" >/dev/null 2>&1; then
    local args=("$@")
    local update_args=()
    local index
    for ((index = 0; index < ${#args[@]}; index++)); do
      if [[ "${args[$index]}" == "--mount-add" ]]; then
        ((index += 1))
        continue
      fi
      update_args+=("${args[$index]}")
    done
    docker service update --image "$image" --update-order start-first --update-parallelism 1 --update-failure-action rollback --update-monitor 180s --detach=false "${update_args[@]}" "$service"
  else
    local args=("$@")
    local create_args=()
    local index
    for ((index = 0; index < ${#args[@]}; index++)); do
      case "${args[$index]}" in
        --env-add) create_args+=("--env") ;;
        --mount-add) create_args+=("--mount") ;;
        *) create_args+=("${args[$index]}") ;;
      esac
    done
    docker service create --name "$service" --network "$NETWORK_NAME" --restart-condition any "${create_args[@]}" "$image"
  fi
}

upsert_service "${STACK_NAME}_clx-agent" "$AGENT_IMAGE"   --env-add PORT=7778   --env-add CLX_MEMORY_DIR=/data/.clx   --env-add CLX_MEMORY_PATH=/data/.clx/training-memory.json   --env-add CLX_AUTO_LEARN=true   --env-add CLX_DEFAULT_LANGUAGE=en   --mount-add type=volume,source=clx_memory,target=/data/.clx   --health-cmd 'curl -fsS http://localhost:7778/health >/dev/null'   --health-interval 30s --health-timeout 10s --health-retries 3

upsert_service "${STACK_NAME}_clx-i" "$CLXI_IMAGE"   --env-add PORT=8048   --env-add CLXI_OLLAMA_HOST=http://clisonix-ollama:11434   --env-add "CLXI_VISION_MODEL=${VISION_MODEL}"   --env-add CLXI_TIMEOUT_SECONDS=120   --env-add CLXI_SELFLEARNING_ENABLED=1   --env-add CLXI_MIRROR_FILE=/data/.clx_i/mirror_events.jsonl   --env-add CLXI_SELFLEARNING_FILE=/data/.clx_i/selflearning_events.jsonl   --mount-add type=volume,source=clx_i_data,target=/data/.clx_i   --health-cmd 'curl -fsS http://localhost:8048/health >/dev/null'   --health-interval 30s --health-timeout 10s --health-retries 3

upsert_service "${STACK_NAME}_clx-hybrid" "$HYBRID_IMAGE"   --env-add PORT=8058   --env-add CLX_HYBRID_API_URL=http://api:8000   --env-add CLX_HYBRID_OCEAN_URL=http://ocean-core:8030   --env-add CLX_HYBRID_CLX_AGENT_URL=http://${STACK_NAME}_clx-agent:7778   --env-add CLX_HYBRID_CLXI_URL=http://${STACK_NAME}_clx-i:8048   --env-add CLX_HYBRID_REQUIRE_NODEDB_FLUID=0   --health-cmd 'curl -fsS http://localhost:8058/health >/dev/null'   --health-interval 30s --health-timeout 10s --health-retries 3

upsert_service "${STACK_NAME}_ai-global-9999" "$AI_GLOBAL_IMAGE"   --env-add PORT=9999   --env-add OLLAMA_HOST=http://clisonix-ollama:11434   --env-add "MODEL=${TEXT_MODEL}"   --env-add REQUEST_TIMEOUT=180   --health-cmd 'curl -fsS http://localhost:9999/health >/dev/null'   --health-interval 30s --health-timeout 10s --health-retries 3

wait_healthy() {
  local service="$1"
  for attempt in $(seq 1 90); do
    container_id="$(docker service ps "$service" --filter desired-state=running --format '{{.ID}}' |
      head -n 1 |
      xargs -r docker inspect --format '{{.Status.ContainerStatus.ContainerID}}')"
    if [[ -n "$container_id" ]] &&
      [[ "$(docker inspect "$container_id" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}missing{{end}}')" == "healthy" ]]; then
      return 0
    fi
    sleep 4
  done
  docker service ps "$service" --no-trunc
  return 1
}

wait_healthy "${STACK_NAME}_clx-agent"
wait_healthy "${STACK_NAME}_clx-i"
wait_healthy "${STACK_NAME}_clx-hybrid"
wait_healthy "${STACK_NAME}_ai-global-9999"

docker run --rm --network "$NETWORK_NAME" -e "AI_GLOBAL_URL=http://${STACK_NAME}_ai-global-9999:9999" python:3.14-bookworm python - <<'PY'
docker run --rm --network "$NETWORK_NAME" -e "CLXI_HEALTH_URL=http://${STACK_NAME}_clx-i:8048/health" python:3.14-bookworm python - <<'PY'
import base64
import json
import os
import urllib.request

with urllib.request.urlopen(os.environ["CLXI_HEALTH_URL"], timeout=20) as response:
    health = json.load(response)
if health.get("status") != "healthy":
    raise SystemExit(f"CLX-I capability health failed: {health}")
if health.get("dependencies", {}).get("vision_model") != "ready":
    raise SystemExit(f"Vision model is not ready: {health}")

png = base64.b64encode(
    base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    )
).decode("ascii")
payload = json.dumps({
    "image_base64": png,
    "prompt": "Describe this image factually in one short sentence.",
    "stigma_level": 1,
    "mirror_level": 1,
}).encode("utf-8")
request = urllib.request.Request(
    "http://clx-i:8048/api/v1/icons/analyze",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=180) as response:
    result = json.load(response)
if not str(result.get("output") or "").strip():
    raise SystemExit(f"LLaVA inference returned no output: {result}")
print(json.dumps({
    "status": "ok",
    "model": result.get("model"),
    "output_chars": len(result["output"]),
}))

global_url = os.environ["AI_GLOBAL_URL"]
with urllib.request.urlopen(f"{global_url}/health", timeout=30) as response:
    global_health = json.load(response)
if global_health.get("status") != "healthy":
    raise SystemExit(f"AI Global health failed: {global_health}")
payload = json.dumps({
    "message": "Reply with one short factual sentence confirming that the model is active.",
    "language_hint": "English",
}).encode("utf-8")
request = urllib.request.Request(
    f"{global_url}/api/v1/chat",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(request, timeout=180) as response:
    global_result = json.load(response)
if not str(global_result.get("response") or "").strip():
    raise SystemExit(f"AI Global returned no model output: {global_result}")
print(json.dumps({
    "status": "ok",
    "service": global_result.get("service"),
    "model": global_result.get("model"),
    "output_chars": len(global_result["response"]),
}))
PY

echo "CLX, CLX-I, CLX hybrid, AI Global, Ollama text model and LLaVA rollout completed with real inference."
