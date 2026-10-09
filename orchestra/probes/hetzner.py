"""
orchestra.probes.hetzner
========================
Probes all critical Clisonix services running on the Hetzner VPS.

Service registry is driven by env var ORCHESTRA_HETZNER_IP (default 46.225.14.83).
Reads ORCHESTRA_HETZNER_SERVICES JSON override for custom service list.

Default services (match slo-sli-gate.yml matrix)
-------------------------------------------------
  api          :8000/health
  ocean-core   :8030/health
  excel        :8002/health
  translation  :8036/health
  ollama       :11434  (no /health path — checks HTTP 200)
  openmind     :9999/health   (allow_failure=True — WARNING not ERROR)
  newsroom     :9800/health
  blog_pub     :8041/health
  albi         :6680/health
  alba         :5555/health
  jona         :7777/health
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple

from orchestra.models import ProbeResult, SignalStatus

_IP = os.getenv("ORCHESTRA_HETZNER_IP", "46.225.14.83")
_TIMEOUT = int(os.getenv("ORCHESTRA_HETZNER_TIMEOUT", "8"))

# (name, port, path, allow_failure)
_DEFAULT_SERVICES: List[Tuple[str, int, str, bool]] = [
    ("api",         8000,  "/health", False),
    ("ocean-core",  8030,  "/health", False),
    ("excel",       8002,  "/health", False),
    ("translation", 8036,  "/health", False),
    ("ollama",      11434, "/",       False),
    ("openmind",    9999,  "/health", True),   # allow_failure
    ("newsroom",    9800,  "/health", False),
    ("blog_pub",    8041,  "/health", True),   # allow_failure if not deployed
    ("albi",        6680,  "/health", True),
    ("alba",        5555,  "/health", True),
    ("jona",        7777,  "/health", True),
]


def _probe_one(name: str, port: int, path: str, allow_failure: bool) -> Dict[str, Any]:
    url = f"http://{_IP}:{port}{path}"
    start = time.monotonic()
    http_code = 0
    error_msg = None
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            http_code = r.getcode()
    except urllib.error.HTTPError as e:
        http_code = e.code
    except Exception as exc:
        error_msg = str(exc)

    latency = (time.monotonic() - start) * 1000
    ok = (http_code >= 200 and http_code < 500) and not error_msg

    return {
        "name":          name,
        "url":           url,
        "http_code":     http_code,
        "latency_ms":    round(latency, 2),
        "ok":            ok,
        "allow_failure": allow_failure,
        "error":         error_msg,
    }


def run() -> ProbeResult:
    start = time.monotonic()
    services = _DEFAULT_SERVICES

    # allow JSON override from env
    override = os.getenv("ORCHESTRA_HETZNER_SERVICES")
    if override:
        try:
            services = [tuple(s) for s in json.loads(override)]  # type: ignore
        except Exception:
            pass

    results: List[Dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=len(services)) as pool:
        futures = {
            pool.submit(_probe_one, name, port, path, af): name
            for name, port, path, af in services
        }
        for fut in as_completed(futures):
            results.append(fut.result())

    results.sort(key=lambda r: r["name"])

    hard_failures = [r for r in results if not r["ok"] and not r["allow_failure"]]
    soft_failures = [r for r in results if not r["ok"] and r["allow_failure"]]

    if hard_failures:
        status  = SignalStatus.ERROR
        message = "DOWN: " + ", ".join(r["name"] for r in hard_failures)
    elif soft_failures:
        status  = SignalStatus.WARNING
        message = "soft-down: " + ", ".join(r["name"] for r in soft_failures)
    else:
        ok_count = sum(1 for r in results if r["ok"])
        status  = SignalStatus.OK
        message = f"all {ok_count}/{len(results)} services healthy"

    return ProbeResult(
        domain     = "hetzner",
        status     = status,
        message    = message,
        details    = {
            "ip":       _IP,
            "services": results,
            "hard_failures": [r["name"] for r in hard_failures],
            "soft_failures": [r["name"] for r in soft_failures],
        },
        latency_ms = (time.monotonic() - start) * 1000,
    )
