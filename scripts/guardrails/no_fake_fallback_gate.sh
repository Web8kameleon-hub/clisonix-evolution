#!/usr/bin/env bash
set -euo pipefail

# Enforces no-fake/no-demo/no-synthetic fallbacks for critical runtime routes.
# This guard intentionally checks only high-risk files to keep false positives low.

REPO_DIR="${1:-$(pwd)}"
cd "${REPO_DIR}"

fail() {
  echo "[NO-FAKE-GATE] ERROR: $1"
  exit 1
}

check_absent() {
  local file="$1"
  local pattern="$2"
  local message="$3"

  if grep -nE "$pattern" "$file" >/tmp/no_fake_gate_hit 2>/dev/null; then
    echo "[NO-FAKE-GATE] Violation in ${file}:"
    cat /tmp/no_fake_gate_hit
    fail "$message"
  fi
}

critical_files=(
  "apps/web/app/api/proxy/kloud-bridge/route.ts"
  "apps/web/app/api/proxy/user-data-sources/route.ts"
  "apps/web/app/api/proxy/user-summary/route.ts"
  "apps/web/app/api/proxy/user-metrics/route.ts"
  "apps/web/app/api/mymirror/data-sources/route.ts"
  "apps/web/app/api/service-discovery/route.ts"
  "apps/web/app/api/openmind/route.ts"
  "apps/web/app/api/_lib/upstream.ts"
)

for file in "${critical_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    fail "Missing critical file: ${file}"
  fi
done

# No demo identity fallbacks in production proxies.
check_absent "apps/web/app/api/proxy/user-data-sources/route.ts" "demo-user|anonymous-user" "Identity fallback detected in user-data-sources proxy"
check_absent "apps/web/app/api/proxy/user-summary/route.ts" "demo-user|anonymous-user" "Identity fallback detected in user-summary proxy"
check_absent "apps/web/app/api/proxy/user-metrics/route.ts" "demo-user|anonymous-user" "Identity fallback detected in user-metrics proxy"
check_absent "apps/web/app/api/mymirror/data-sources/route.ts" "demo-user|anonymous-user" "Identity fallback detected in mymirror data-sources route"
check_absent "apps/web/app/api/_lib/upstream.ts" "demo-user" "Demo identity detected in upstream helper"

# No synthetic activity math fallback in kloud-bridge.
check_absent "apps/web/app/api/proxy/kloud-bridge/route.ts" "activeSources\s*\*\s*runningContainers" "Synthetic kloud activity fallback detected"

# No explicit mock/fake placeholder function naming in critical runtime routes.
check_absent "apps/web/app/api/proxy/kloud-bridge/route.ts" "\b(mock|fake|placeholder)_[A-Za-z0-9_]*\b" "Mock/fake placeholder function detected"
check_absent "apps/web/app/api/proxy/user-data-sources/route.ts" "\b(mock|fake|placeholder)_[A-Za-z0-9_]*\b" "Mock/fake placeholder function detected"
check_absent "apps/web/app/api/proxy/user-summary/route.ts" "\b(mock|fake|placeholder)_[A-Za-z0-9_]*\b" "Mock/fake placeholder function detected"

# Block degraded fallback snapshots in strict discovery and openmind routes.
check_absent "apps/web/app/api/service-discovery/route.ts" "apiDegraded\(|fallbackServices" "Service discovery degraded fallback detected"
check_absent "apps/web/app/api/openmind/route.ts" "OPENMIND_FALLBACK|getCandidates\(" "OpenMind fallback chain detected"

echo "[NO-FAKE-GATE] PASS"
