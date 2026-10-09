#!/usr/bin/env bash
set -euo pipefail

DEPLOY_PATH="${DEPLOY_PATH:-/root/Clisonix-cloud}"
SERVICES_CSV="${AUTO_DEPLOY_SERVICES:-web,api,ocean-core,ocean-core-multimodal,kloud-upstream-runtime,kloud-bridge,curiosity,user-management}"
COMPOSE_FILE="${AUTO_DEPLOY_COMPOSE_FILE:-docker-compose.75-services.yml}"
PREFERRED_ENV_FILE="${AUTO_DEPLOY_ENV_FILE:-}"

log() {
  printf '\n==> %s\n' "$1"
}

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

resolve_env_file() {
  local candidates=()

  if [[ -n "$PREFERRED_ENV_FILE" ]]; then
    candidates+=("$PREFERRED_ENV_FILE")
  fi

  candidates+=(
    ".env.autodeploy"
    ".env"
    ".env.production"
    ".env.unified"
  )

  local candidate
  for candidate in "${candidates[@]}"; do
    [[ -n "$candidate" ]] || continue
    if [[ -f "$candidate" ]]; then
      echo "$candidate"
      return
    fi
  done

  echo ""
}

compose_run() {
  local compose_bin="$1"
  local env_file="$2"
  shift 2

  if [[ -n "$env_file" ]]; then
    $compose_bin --env-file "$env_file" -f "$COMPOSE_FILE" "$@"
  else
    $compose_bin -f "$COMPOSE_FILE" "$@"
  fi
}

value_from_env_file() {
  local file="$1"
  local key="$2"
  [[ -n "$file" && -f "$file" ]] || return 0
  grep -E "^${key}=" "$file" | tail -1 | cut -d= -f2-
}

sync_origin_main() {
  log "Sync code to origin/main"
  git fetch origin main
  if [[ -n "$(git status --porcelain)" ]]; then
    local stash_msg="autostash-before-auto-deploy-$(date -u +%Y%m%dT%H%M%SZ)"
    echo "⚠️ Local changes detected on server, stashing as: $stash_msg"
    git stash push -u -m "$stash_msg" || true
  fi
  git checkout -B main origin/main
  git reset --hard origin/main
  git clean -fd
  echo "🔖 Commit: $(git rev-parse --short HEAD)"
}

build_web_image() {
  local env_file="$1"
  local image_tag="$2"
  local stripe_pub
  local stripe_table
  local adsense_id
  local auth_secret
  local nextauth_secret

  stripe_pub="$(value_from_env_file "$env_file" "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY")"
  stripe_table="$(value_from_env_file "$env_file" "NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID")"
  adsense_id="$(value_from_env_file "$env_file" "NEXT_PUBLIC_GOOGLE_ADSENSE_ID")"
  auth_secret="$(value_from_env_file "$env_file" "AUTH_SECRET")"
  nextauth_secret="$(value_from_env_file "$env_file" "NEXTAUTH_SECRET")"

  if [[ -z "$auth_secret" && -z "$nextauth_secret" ]]; then
    echo "❌ Missing AUTH_SECRET/NEXTAUTH_SECRET in env file: ${env_file:-none}"
    exit 1
  fi

  log "Build web image $image_tag"
  docker build \
    -f apps/web/Dockerfile \
    -t "$image_tag" \
    --build-arg "NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=${stripe_pub}" \
    --build-arg "NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID=${stripe_table}" \
    --build-arg "NEXT_PUBLIC_API_BASE=/api" \
    --build-arg "NEXT_PUBLIC_GOOGLE_ADSENSE_ID=${adsense_id}" \
    --build-arg "AUTH_SECRET=${auth_secret}" \
    --build-arg "NEXTAUTH_SECRET=${nextauth_secret}" \
    apps/web
}

deploy_web_direct() {
  local env_file="$1"
  local commit_sha="$2"
  local image_tag="clisonix-web:deploy-${commit_sha}"
  local candidate_name="clisonix-web-candidate-${commit_sha}"
  local env_tmp="/tmp/clisonix-web-env-${commit_sha}.list"
  local network_name="clisonix-net"

  build_web_image "$env_file" "$image_tag"

  log "Capture current web runtime environment"
  docker inspect clisonix-web --format '{{range .Config.Env}}{{println .}}{{end}}' > "$env_tmp"
  if docker inspect clisonix-web --format '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}' | grep -q .; then
    network_name="$(docker inspect clisonix-web --format '{{range $name, $_ := .NetworkSettings.Networks}}{{println $name}}{{end}}' | head -1)"
  fi

  log "Start web candidate container"
  docker rm -f "$candidate_name" >/dev/null 2>&1 || true
  docker run -d \
    --name "$candidate_name" \
    --restart unless-stopped \
    --network "$network_name" \
    --network-alias web-canary \
    --env-file "$env_tmp" \
    -v kitchen_jobs:/app/kitchen-jobs \
    -v kitchen_reports:/app/kitchen-reports \
    "$image_tag" >/dev/null

  log "Health-check web candidate"
  local ok="false"
  local attempt
  for attempt in 1 2 3 4 5 6 7 8; do
    if docker exec "$candidate_name" curl -fsS http://127.0.0.1:3000/api/health-check >/dev/null 2>&1; then
      ok="true"
      break
    fi
    sleep 3
  done

  if [[ "$ok" != "true" ]]; then
    echo "❌ Web candidate failed health-check"
    docker logs --tail=120 "$candidate_name" || true
    docker rm -f "$candidate_name" >/dev/null 2>&1 || true
    exit 1
  fi

  log "Swap web container"
  docker rm -f clisonix-web >/dev/null 2>&1 || true
  docker run -d \
    --name clisonix-web \
    --restart unless-stopped \
    --network "$network_name" \
    --network-alias web \
    --env-file "$env_tmp" \
    -p 3000:3000 \
    -v kitchen_jobs:/app/kitchen-jobs \
    -v kitchen_reports:/app/kitchen-reports \
    "$image_tag" >/dev/null

  local live_ok="false"
  for attempt in 1 2 3 4 5 6; do
    code="$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:3000/api/health-check || true)"
    if [[ "$code" == "200" ]]; then
      live_ok="true"
      break
    fi
    sleep 3
  done

  docker rm -f "$candidate_name" >/dev/null 2>&1 || true
  rm -f "$env_tmp"

  if [[ "$live_ok" != "true" ]]; then
    echo "❌ Live web health-check failed after swap"
    docker logs --tail=120 clisonix-web || true
    exit 1
  fi

  echo "✅ Web deployed via direct image swap"
}

check_http() {
  local name="$1"
  local url="$2"
  local ok="false"
  local attempt
  for attempt in 1 2 3 4 5 6; do
    code="$(curl -s -o /dev/null -w '%{http_code}' "$url" || true)"
    if [[ "$code" == "200" ]]; then
      ok="true"
      break
    fi
    sleep 4
  done

  if [[ "$ok" == "true" ]]; then
    echo "✅ $name healthy ($url)"
    return 0
  fi

  echo "❌ $name unhealthy ($url)"
  return 1
}

check_service_health() {
  local svc="$1"
  case "$svc" in
    web)
      check_http "web" "http://127.0.0.1:3000/api/health-check"
      ;;
    api)
      check_http "api" "http://127.0.0.1:8000/health"
      ;;
    ocean-core)
      check_http "ocean-core" "http://127.0.0.1:8030/health"
      ;;
    ocean-core-multimodal)
      check_http "ocean-core-multimodal" "http://127.0.0.1:8033/health"
      ;;
    kloud-upstream-runtime)
      check_http "kloud-upstream-runtime" "http://127.0.0.1:9080/health"
      ;;
    kloud-bridge)
      check_http "kloud-bridge" "http://127.0.0.1:8889/health"
      ;;
    curiosity)
      check_http "curiosity" "http://127.0.0.1:8011/health"
      ;;
    user-management)
      check_http "user-management" "http://127.0.0.1:8071/health"
      ;;
    *)
      echo "ℹ️ No HTTP health gate mapped for $svc"
      ;;
  esac
}

service_host_port() {
  local svc="$1"
  case "$svc" in
    web) echo "3000" ;;
    api) echo "8000" ;;
    ocean-core) echo "8030" ;;
    ocean-core-multimodal) echo "8033" ;;
    kloud-upstream-runtime) echo "9080" ;;
    kloud-bridge) echo "8889" ;;
    curiosity) echo "8011" ;;
    user-management) echo "8071" ;;
    *) echo "" ;;
  esac
}

ensure_service_port_available() {
  local svc="$1"
  local port
  port="$(service_host_port "$svc")"
  [[ -n "$port" ]] || return 0

  local expected_name="clisonix-${svc}"
  local conflict_lines
  conflict_lines="$(docker ps --filter "publish=${port}" --format '{{.ID}} {{.Names}}' || true)"

  if [[ -n "$conflict_lines" ]]; then
    local cid
    local cname
    while read -r cid cname; do
      [[ -n "${cid:-}" ]] || continue
      if [[ "$cname" == "$expected_name" ]]; then
        continue
      fi

      echo "⚠️ Port ${port} is occupied by ${cname} (${cid}); removing conflicting container"
      if ! docker rm -f "$cid" >/dev/null 2>&1; then
        echo "❌ Failed to remove conflicting container ${cname} (${cid}) on port ${port}"
        return 1
      fi
    done <<<"$conflict_lines"
  fi

  local remaining
  remaining="$(docker ps --filter "publish=${port}" --format '{{.Names}}' | grep -v "^${expected_name}$" || true)"
  if [[ -n "$remaining" ]]; then
    echo "❌ Port ${port} still occupied by container(s): ${remaining}"
    return 1
  fi

  if command -v ss >/dev/null 2>&1; then
    local docker_holder
    docker_holder="$(docker ps --filter "publish=${port}" --format '{{.Names}}' | head -1 || true)"
    if [[ -z "$docker_holder" ]] && ss -ltn "sport = :${port}" | tail -n +2 | grep -q .; then
      echo "❌ Port ${port} is occupied by a host process (not a Docker container); cannot restart ${svc}"
      ss -ltnp "sport = :${port}" || true
      return 1
    fi
  fi
}

main() {
  cd "$DEPLOY_PATH"

  local compose_bin
  compose_bin="$(resolve_compose)"
  local env_file
  env_file="$(resolve_env_file)"
  local commit_sha

  sync_origin_main
  commit_sha="$(git rev-parse --short HEAD)"

  if [[ -n "$env_file" ]]; then
    echo "🧩 Using env file: $env_file"
  else
    echo "⚠️ No explicit env file found; compose deploys may fail if services require secrets"
  fi

  local services=()
  read -r -a services <<<"${SERVICES_CSV//,/ }"

  if [[ "${#services[@]}" -eq 1 && "${services[0]}" == "web" ]]; then
    deploy_web_direct "$env_file" "$commit_sha"
    check_http "web" "http://127.0.0.1:3000/api/health-check"
    return
  fi

  log "Compose validation"
  compose_run "$compose_bin" "$env_file" config >/tmp/clisonix-compose-config.out

  log "Rebuild services: ${services[*]}"
  compose_run "$compose_bin" "$env_file" build "${services[@]}"

  log "Rolling restart services one-by-one: ${services[*]}"
  # Restart targets sequentially and gate each with health checks before continuing.
  # This reduces blast radius and avoids all-at-once restarts.
  local svc
  for svc in "${services[@]}"; do
    echo "🔄 Rolling service: ${svc}"
    ensure_service_port_available "$svc"
    compose_run "$compose_bin" "$env_file" up -d --no-deps --force-recreate "$svc"
    check_service_health "$svc" || {
      echo "🧯 Rolling deploy stopped at service: ${svc}"
      compose_run "$compose_bin" "$env_file" logs --tail=120 "$svc" || true
      exit 1
    }
  done

  log "Container status"
  compose_run "$compose_bin" "$env_file" ps "${services[@]}" || true

  echo "🎉 ALL GREEN"
}

main "$@"
