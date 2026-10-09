"""
orchestra.probes.clients
=========================
Reads active API-key clients telemetry from the Clisonix API service.

Checks
------
  - /api/keys/summary   → total keys, active keys, revoked keys
  - /api/usage/summary  → requests last 24h, top consumers
  - Stale client gate   → clients with 0 requests in CLIENTS_STALE_DAYS
  - Suspicious gate     → clients exceeding CLIENTS_MAX_RPM (per minute)

Env vars
--------
  CLISONIX_API_URL        base URL  (default: http://localhost:8000)
  CLISONIX_INTERNAL_KEY   internal API key for /api/keys/summary access
  CLIENTS_STALE_DAYS      int (default: 30)
  CLIENTS_MAX_RPM         int (default: 600)
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from orchestra.models import ProbeResult, SignalStatus

_API_URL     = os.getenv("CLISONIX_API_URL", "http://localhost:8000")
_INT_KEY     = os.getenv("CLISONIX_INTERNAL_KEY", "")
_STALE_DAYS  = int(os.getenv("CLIENTS_STALE_DAYS", "30"))
_MAX_RPM     = int(os.getenv("CLIENTS_MAX_RPM", "600"))


def _get(path: str, timeout: int = 6) -> Optional[Dict[str, Any]]:
    url = f"{_API_URL}{path}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    if _INT_KEY:
        req.add_header("X-API-Key", _INT_KEY)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403, 404):
            return {"_http_error": exc.code, "_reason": exc.reason}
        raise
    except Exception:
        return None


def run() -> ProbeResult:
    start = time.monotonic()
    details: Dict[str, Any] = {"api_url": _API_URL}
    warnings: list[str] = []
    errors:   list[str] = []

    # ── /health reachability ──────────────────────────────────────────────────
    health = _get("/health", timeout=4)
    if health is None:
        return ProbeResult(
            domain     = "clients",
            status     = SignalStatus.ERROR,
            message    = f"Clisonix API unreachable at {_API_URL}",
            details    = details,
            latency_ms = (time.monotonic() - start) * 1000,
        )
    details["api_health"] = health

    try:
        # ── API key summary ───────────────────────────────────────────────────
        keys_data = _get("/api/v1/keys/summary") or _get("/api/keys/summary") or {}
        if "_http_error" in keys_data:
            details["keys_probe"] = f"HTTP {keys_data['_http_error']} — no key access"
            warnings.append("API-key summary endpoint requires elevated token")
        else:
            total_keys   = keys_data.get("total",   keys_data.get("count", "n/a"))
            active_keys  = keys_data.get("active",  "n/a")
            revoked_keys = keys_data.get("revoked", "n/a")
            details["total_keys"]   = total_keys
            details["active_keys"]  = active_keys
            details["revoked_keys"] = revoked_keys

            if isinstance(revoked_keys, int) and isinstance(total_keys, int):
                revoke_pct = revoked_keys / max(total_keys, 1) * 100
                if revoke_pct > 20:
                    warnings.append(f"High revocation rate: {revoke_pct:.1f}% of keys revoked")

        # ── usage summary ─────────────────────────────────────────────────────
        usage_data = _get("/api/v1/usage/summary") or _get("/api/usage/summary") or {}
        if "_http_error" not in usage_data and usage_data:
            requests_24h = usage_data.get("requests_24h", usage_data.get("total_requests", "n/a"))
            top_clients: List[Dict] = usage_data.get("top_clients", [])
            details["requests_24h"] = requests_24h
            details["top_clients"]  = top_clients[:5]

            # suspicious RPM check
            for client in top_clients:
                rpm = client.get("rpm", 0)
                if rpm and rpm > _MAX_RPM:
                    warnings.append(
                        f"Client '{client.get('key_id','?')}' at {rpm} RPM > {_MAX_RPM} threshold"
                    )
        else:
            details["usage_data"] = "not available"

        # ── stale clients (if data available) ────────────────────────────────
        stale_data = _get(f"/api/v1/keys/stale?days={_STALE_DAYS}") or {}
        stale_count = stale_data.get("count", stale_data.get("stale_count", None))
        if stale_count is not None:
            details["stale_clients"] = stale_count
            if isinstance(stale_count, int) and stale_count > 0:
                warnings.append(f"{stale_count} client(s) stale for > {_STALE_DAYS} days")

        # ── result ────────────────────────────────────────────────────────────
        if errors:
            status  = SignalStatus.ERROR
            message = "; ".join(errors)
        elif warnings:
            status  = SignalStatus.WARNING
            message = "; ".join(warnings)
        else:
            status  = SignalStatus.OK
            active  = details.get("active_keys", "?")
            req24   = details.get("requests_24h", "?")
            message = f"clients ok — {active} active keys, {req24} req/24h"

    except Exception as exc:
        status  = SignalStatus.ERROR
        message = f"clients probe failed: {exc}"

    return ProbeResult(
        domain     = "clients",
        status     = status,
        message    = message,
        details    = details,
        latency_ms = (time.monotonic() - start) * 1000,
    )
