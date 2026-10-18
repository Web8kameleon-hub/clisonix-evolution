# NDB Hybrid Enforcement Middleware (FastAPI)
# NO_FAKE: enforcement uses real NanoGrid NDB measurements and deterministic canary selection.

import hashlib
import json
import os
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ndb_shadow_sidecar import NDBRuntimeUnavailable, compute_ndb_scores
from ndb_advisory_middleware import recommend_policy

HYBRID_FILE = os.environ.get("NDB_HYBRID_EVENTS_FILE", "ndb_hybrid_events.jsonl")
ENFORCED_ROUTES = {route.strip() for route in os.environ.get("NDB_HYBRID_ENFORCED_ROUTES", "").split(",") if route.strip()}
CANARY_PERCENT = max(0, min(100, int(os.environ.get("NDB_HYBRID_CANARY_PERCENT", "0"))))

def _selected(correlation_id):
    bucket = int(hashlib.sha256(correlation_id.encode("utf-8")).hexdigest()[:8], 16) % 100
    return bucket < CANARY_PERCENT

class NDBHybridEnforcementMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if os.environ.get("NDB_HYBRID_ENFORCE_ENABLED", "0") != "1":
            return await call_next(request)
        correlation_id = str(uuid.uuid4())
        try:
            scores = compute_ndb_scores(request, await request.body())
        except NDBRuntimeUnavailable as exc:
            return Response(content=json.dumps({"error":"ndb_runtime_unavailable","detail":str(exc)}), status_code=503, media_type="application/json")
        enforce = request.url.path in ENFORCED_ROUTES and _selected(correlation_id)
        decision = recommend_policy(scores["ndb_score"], scores["tide"], scores["stigma_level"])
        if enforce and decision == "block":
            response = Response(content="Blocked by NDB Hybrid", status_code=403)
        elif enforce and decision == "throttle":
            response = Response(content="Throttled by NDB Hybrid", status_code=429)
        else:
            response = await call_next(request)
        event = {
            "timestamp": int(time.time()), "correlation_id": correlation_id,
            "endpoint": scores["endpoint"], "action": request.method,
            "ndb_score": scores["ndb_score"], "ndb_delta": scores["ndb_delta"],
            "tide": scores["tide"], "stigma_level": scores["stigma_level"],
            "node_id": scores["node_id"], "enforced": enforce, "decision": decision,
            "outcome": response.status_code, "source": "nanogrid-runtime",
        }
        with open(HYBRID_FILE, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return response
