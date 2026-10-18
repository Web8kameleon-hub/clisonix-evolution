# NDB Shadow Evaluator Sidecar (FastAPI Middleware)
# NO_FAKE: reads NDB/Stigma/Tide from the real NanoGrid runtime.

import json
import os
import time
import uuid
import urllib.error
import urllib.request

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

EVENTS_FILE = os.environ.get("NDB_SHADOW_EVENTS_FILE", "ndb_shadow_events.jsonl")
NANOGRID_URL = os.environ.get("NANOGRID_URL", "http://127.0.0.1:8033").rstrip("/")
NANOGRID_STATUS_URL = os.environ.get(
    "NANOGRID_STATUS_URL", f"{NANOGRID_URL}/status?stigma_level=2"
)
NANOGRID_TIMEOUT_SECONDS = float(os.environ.get("NANOGRID_TIMEOUT_SECONDS", "2.0"))


class NDBRuntimeUnavailable(RuntimeError):
    pass


def _read_nanogrid_status():
    try:
        with urllib.request.urlopen(NANOGRID_STATUS_URL, timeout=NANOGRID_TIMEOUT_SECONDS) as response:
            if response.status != 200:
                raise NDBRuntimeUnavailable(f"NanoGrid status HTTP {response.status}")
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        raise NDBRuntimeUnavailable(f"NanoGrid runtime unavailable: {exc}") from exc

    required = ("ndb_score", "ndb_delta", "tide")
    missing = [key for key in required if key not in payload]
    if missing:
        raise NDBRuntimeUnavailable(
            "NanoGrid status missing required fields: " + ", ".join(missing)
        )
    return payload


def compute_ndb_scores(request: Request, body: bytes):
    # body is accepted for middleware compatibility; it is never used to invent a score.
    del body
    status = _read_nanogrid_status()
    stigma_raw = request.headers.get("X-Stigma-Level", "2")
    try:
        stigma_level = max(1, min(3, int(stigma_raw)))
    except ValueError:
        stigma_level = 2
    return {
        "ndb_score": float(status["ndb_score"]),
        "ndb_delta": float(status["ndb_delta"]),
        "tide": str(status["tide"]),
        "stigma_level": stigma_level,
        "node_id": status.get("node_id"),
        "endpoint": request.url.path,
    }


class NDBShadowMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if os.environ.get("NDB_SHADOW_ENABLED", "0") != "1":
            return await call_next(request)

        correlation_id = str(uuid.uuid4())
        body = await request.body()
        try:
            scores = compute_ndb_scores(request, body)
        except NDBRuntimeUnavailable as exc:
            return Response(
                content=json.dumps({"error": "ndb_runtime_unavailable", "detail": str(exc)}),
                status_code=503,
                media_type="application/json",
            )

        response: Response = await call_next(request)
        event = {
            "timestamp": int(time.time()),
            "correlation_id": correlation_id,
            "endpoint": scores["endpoint"],
            "action": request.method,
            "ndb_score": scores["ndb_score"],
            "ndb_delta": scores["ndb_delta"],
            "tide": scores["tide"],
            "stigma_level": scores["stigma_level"],
            "node_id": scores["node_id"],
            "outcome": response.status_code,
            "source": "nanogrid-runtime",
        }
        with open(EVENTS_FILE, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return response
