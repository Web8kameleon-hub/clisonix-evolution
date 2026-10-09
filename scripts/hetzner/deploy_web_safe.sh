#!/usr/bin/env bash
set -euo pipefail

# Zero-downtime web deploy for Hetzner host.
# 1) Build new image
# 2) Start canary container and wait healthy
# 3) Cut over traffic to new version
# 4) Remove old container

REPO_DIR="${REPO_DIR:-/root/Clisonix-cloud}"
BRANCH="${BRANCH:-main}"
REMOTE="${REMOTE:-origin}"
SERVICE="${SERVICE:-web}"
CONTAINER_NAME="${CONTAINER_NAME:-clisonix-web}"
NETWORK_NAME="${NETWORK_NAME:-clisonix-net}"
HEALTH_TIMEOUT_S="${HEALTH_TIMEOUT_S:-180}"

CANARY_NAME="${CONTAINER_NAME}-canary-$(date +%Y%m%d%H%M%S)"
ENV_FILE="/tmp/${CANARY_NAME}.env"
SMOKE_BODY="/tmp/deploy_smoke_body"

cleanup() {
  rm -f "${ENV_FILE}" "${SMOKE_BODY}" || true
}
trap cleanup EXIT

wait_healthy() {
  local container="$1"
  local timeout_s="$2"
  local start_ts now_ts elapsed health

  start_ts="$(date +%s)"
  while true; do
    health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${container}" 2>/dev/null || echo "missing")"
    if [[ "${health}" == "healthy" ]]; then
      return 0
    fi

    now_ts="$(date +%s)"
    elapsed="$((now_ts - start_ts))"
    if (( elapsed >= timeout_s )); then
      echo "ERROR: ${container} did not become healthy within ${timeout_s}s (last=${health})."
      docker ps --format '{{.Names}} {{.Status}}' | grep -E "${container}|${CONTAINER_NAME}|NAME" || true
      return 1
    fi

    sleep 2
  done
}

echo "[1/10] Repository: ${REPO_DIR}"
cd "${REPO_DIR}"

echo "[2/10] Pulling latest ${REMOTE}/${BRANCH}..."
git fetch "${REMOTE}"
git checkout "${BRANCH}"
git pull --ff-only "${REMOTE}" "${BRANCH}"

echo "[3/10] Ensuring old container exists: ${CONTAINER_NAME}"
docker inspect "${CONTAINER_NAME}" >/dev/null

echo "[4/10] Exporting runtime env from current container..."
docker inspect "${CONTAINER_NAME}" --format '{{range .Config.Env}}{{println .}}{{end}}' > "${ENV_FILE}"

echo "[5/10] Building new ${SERVICE} image..."
docker compose build "${SERVICE}"
NEW_IMAGE="$(docker compose images -q "${SERVICE}" | head -n 1 || true)"
if [[ -z "${NEW_IMAGE}" ]]; then
  NEW_IMAGE="$(docker image inspect --format '{{.ID}}' "clisonix-cloud-${SERVICE}:latest" 2>/dev/null || true)"
fi
if [[ -z "${NEW_IMAGE}" ]]; then
  NEW_IMAGE="clisonix-cloud-${SERVICE}:latest"
fi
if ! docker image inspect "${NEW_IMAGE}" >/dev/null 2>&1; then
  echo "ERROR: Failed to resolve built image for service ${SERVICE}."
  exit 1
fi
echo "Built image: ${NEW_IMAGE}"

echo "[6/10] Starting canary container ${CANARY_NAME} (no host port)..."
docker rm -f "${CANARY_NAME}" >/dev/null 2>&1 || true
docker run -d \
  --name "${CANARY_NAME}" \
  --restart unless-stopped \
  --network "${NETWORK_NAME}" \
  --network-alias "${CONTAINER_NAME}" \
  --network-alias web \
  --env-file "${ENV_FILE}" \
  -v kitchen_jobs:/app/kitchen-jobs \
  -v kitchen_reports:/app/kitchen-reports \
  "${NEW_IMAGE}" >/dev/null

echo "[7/10] Waiting for canary health=healthy..."
wait_healthy "${CANARY_NAME}" "${HEALTH_TIMEOUT_S}"

echo "[8/10] Removing old container ${CONTAINER_NAME} and promoting new version..."
docker rm -f "${CONTAINER_NAME}" >/dev/null

docker run -d \
  --name "${CONTAINER_NAME}" \
  --restart unless-stopped \
  --network "${NETWORK_NAME}" \
  --network-alias web \
  --env-file "${ENV_FILE}" \
  -v kitchen_jobs:/app/kitchen-jobs \
  -v kitchen_reports:/app/kitchen-reports \
  -p 3000:3000 \
  "${NEW_IMAGE}" >/dev/null

echo "[9/10] Waiting for promoted container health=healthy, then removing canary..."
wait_healthy "${CONTAINER_NAME}" "${HEALTH_TIMEOUT_S}"
docker rm -f "${CANARY_NAME}" >/dev/null 2>&1 || true

echo "[10/10] Running ingress smoke checks..."
for url in \
  "http://127.0.0.1:3000/modules" \
  "http://127.0.0.1:3000/robots.txt" \
  "http://127.0.0.1:3000/sitemap.xml" \
  "http://127.0.0.1:3000/api/proxy/kloud-bridge" \
  "http://127.0.0.1:3000/api/proxy/system-metrics"; do
  code="$(curl -sS -o "${SMOKE_BODY}" -w '%{http_code}' -m 20 "${url}" || true)"
  if [[ -z "${code}" ]]; then
    code="000"
  fi
  echo "${code} ${url}"
  if [[ "${code}" != "200" ]]; then
    echo "ERROR: Smoke check failed for ${url}"
    if [[ -f "${SMOKE_BODY}" ]]; then
      head -c 300 "${SMOKE_BODY}" || true
    fi
    echo
    exit 1
  fi
done

echo "Deploy successful (zero-downtime rollout)."
