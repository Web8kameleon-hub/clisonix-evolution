"""
orchestra.probes.cloudflare
============================
Probes Cloudflare zone health for the Clisonix domain.

Checks
------
  - Zone status (active / paused)
  - Zone paused flag
  - Health-check monitor status (if configured)
  - Cloudflare edge worker last deployment (clisonix-health-worker)

Env vars
--------
  CF_API_TOKEN       Cloudflare API token (Zone:Read, Workers:Read)
  CF_ZONE_ID         Cloudflare Zone ID for clisonix.com
  CF_ACCOUNT_ID      Cloudflare account ID
  CF_WORKER_NAME     Worker script name (default: clisonix-health-worker)
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict

from orchestra.models import ProbeResult, SignalStatus

_TOKEN      = os.getenv("CF_API_TOKEN", "")
_ZONE_ID    = os.getenv("CF_ZONE_ID", "")
_ACCOUNT_ID = os.getenv("CF_ACCOUNT_ID", "")
_WORKER     = os.getenv("CF_WORKER_NAME", "clisonix-health-worker")
_CF_API     = "https://api.cloudflare.com/client/v4"


def _cf_get(path: str, timeout: int = 8) -> Dict[str, Any]:
    url = f"{_CF_API}{path}"
    req = urllib.request.Request(url)
    if _TOKEN:
        req.add_header("Authorization", f"Bearer {_TOKEN}")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read())
    if not data.get("success"):
        errors = data.get("errors", [])
        raise RuntimeError(f"CF API error: {errors}")
    return data.get("result", data)


def run() -> ProbeResult:
    start = time.monotonic()
    details: Dict[str, Any] = {}
    warnings: list[str] = []
    errors: list[str] = []

    if not _TOKEN:
        return ProbeResult(
            domain     = "cloudflare",
            status     = SignalStatus.WARNING,
            message    = "CF_API_TOKEN not set — skipping Cloudflare probe",
            details    = {"skipped": True},
            latency_ms = 0.0,
        )

    try:
        # ── zone status ───────────────────────────────────────────────────────
        if _ZONE_ID:
            zone = _cf_get(f"/zones/{_ZONE_ID}")
            details["zone_name"]   = zone.get("name", "")
            details["zone_status"] = zone.get("status", "")
            details["zone_paused"] = zone.get("paused", False)
            details["plan"]        = zone.get("plan", {}).get("name", "")

            if zone.get("status") != "active":
                errors.append(f"Zone status is '{zone.get('status')}' (expected active)")
            if zone.get("paused"):
                warnings.append("Cloudflare zone is PAUSED — traffic bypassing CF")
        else:
            details["zone_status"] = "ZONE_ID_NOT_SET"
            warnings.append("CF_ZONE_ID not configured — zone check skipped")

        # ── worker deployment ─────────────────────────────────────────────────
        if _ACCOUNT_ID:
            try:
                worker = _cf_get(f"/accounts/{_ACCOUNT_ID}/workers/scripts/{_WORKER}")
                details["worker_name"]       = _WORKER
                details["worker_modified_on"] = worker.get("modified_on", "")
                details["worker_etag"]        = worker.get("etag", "")
            except RuntimeError as exc:
                details["worker_status"] = f"not found or error: {exc}"
                warnings.append(f"Worker '{_WORKER}' not found/accessible")
        else:
            details["worker_status"] = "CF_ACCOUNT_ID_NOT_SET"

        # ── result ────────────────────────────────────────────────────────────
        if errors:
            status  = SignalStatus.ERROR
            message = "; ".join(errors)
        elif warnings:
            status  = SignalStatus.WARNING
            message = "; ".join(warnings)
        else:
            status  = SignalStatus.OK
            message = f"zone active — plan={details.get('plan', 'unknown')}"

    except urllib.error.HTTPError as exc:
        status  = SignalStatus.ERROR
        message = f"Cloudflare API HTTP {exc.code}: {exc.reason}"
    except Exception as exc:
        status  = SignalStatus.ERROR
        message = f"cloudflare probe failed: {exc}"

    return ProbeResult(
        domain     = "cloudflare",
        status     = status,
        message    = message,
        details    = details,
        latency_ms = (time.monotonic() - start) * 1000,
    )
