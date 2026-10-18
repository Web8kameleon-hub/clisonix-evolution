#!/usr/bin/env bash
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/opt/clisonix.com}"
STACK_NAME="${SWARM_STACK_NAME:-clisonix-next}"
NETWORK_NAME="${SWARM_NETWORK:-clisonix-swarm}"
SERVICE_NAME="${STACK_NAME}_ocean-core"

cd "$DEPLOY_PATH"
COMMIT_SHA="$(git rev-parse --short=12 HEAD)"
IMAGE_TAG="clisonix-ocean-core:deploy-${COMMIT_SHA}"

docker network inspect "$NETWORK_NAME" >/dev/null 2>&1 ||
  docker network create --driver overlay --attachable "$NETWORK_NAME"

docker service inspect "$SERVICE_NAME" >/dev/null
docker build --file ocean-core/Dockerfile --tag "$IMAGE_TAG" ocean-core

docker service update   --image "$IMAGE_TAG"   --update-order start-first   --update-parallelism 1   --update-failure-action rollback   --update-monitor 180s   --rollback-order start-first   --detach=false   "$SERVICE_NAME"

for attempt in $(seq 1 60); do
  container_id="$(
    docker service ps "$SERVICE_NAME"       --filter desired-state=running       --format '{{.ID}}' |
      head -n 1 |
      xargs -r docker inspect --format '{{.Status.ContainerStatus.ContainerID}}'
  )"
  if [[ -n "$container_id" ]] &&
    [[ "$(docker inspect "$container_id" --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}missing{{end}}')" == "healthy" ]]; then
    break
  fi
  if [[ "$attempt" -eq 60 ]]; then
    docker service ps "$SERVICE_NAME" --no-trunc
    exit 1
  fi
  sleep 4
done

docker run --rm -i --network "$NETWORK_NAME" python:3.14-bookworm python - <<'PY'
import json
import urllib.request

payload = json.dumps({
    "message": "Përgjigju vetëm me OCEAN_OK",
    "messages": [],
    "max_tokens": 32,
}).encode("utf-8")
request = urllib.request.Request(
    "http://ocean-core:8030/api/v1/chat/stream",
    data=payload,
    headers={
        "Accept": "text/event-stream",
        "Content-Type": "application/json",
    },
    method="POST",
)
with urllib.request.urlopen(request, timeout=120) as response:
    body = response.read().decode("utf-8", errors="replace")

usable = False
completed = False
for line in body.splitlines():
    if line.strip() == "event: error":
        raise SystemExit("Ocean smoke test emitted an SSE error")
    if not line.startswith("data: "):
        continue
    raw = line[6:].strip()
    if raw == "[DONE]":
        completed = True
        continue
    if not raw:
        continue
    try:
        event = json.loads(raw)
    except json.JSONDecodeError:
        if "[STREAM_ERROR:" in raw:
            raise SystemExit("Ocean smoke test emitted a model error")
        usable = usable or bool(raw)
        continue
    if not isinstance(event, dict) or event.get("error"):
        raise SystemExit("Ocean smoke test emitted an invalid/error event")
    for key in ("text", "chunk", "response", "content", "token", "printer_chunk"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            usable = True
            break

if not usable or not completed:
    raise SystemExit(f"Ocean smoke test produced no model text: {body[:2000]}")

print("Ocean model smoke test emitted usable text.")
PY

echo "Ocean Core Swarm rollout completed with model-output health gating."
