# Resonance-First Default Middleware (FastAPI)
# NO_FAKE: primary policy consumes real NanoGrid NDB measurements and fails closed if unavailable.

import json
import os
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ndb_shadow_sidecar import NDBRuntimeUnavailable, compute_ndb_scores
from ndb_advisory_middleware import recommend_policy

RESONANCE_FILE = os.environ.get("NDB_RESONANCE_EVENTS_FILE", "ndb_resonance_events.jsonl")
PRIMARY_ROUTES = {route.strip() for route in os.environ.get("NDB_RESONANCE_PRIMARY_ROUTES", "").split(",") if route.strip()}

class NDBResonanceDefaultMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if os.environ.get("NDB_RESONANCE_DEFAULT_ENABLED", "0") != "1":
            return await call_next(request)
        correlation_id = str(uuid.uuid4())
        try:
            scores = compute_ndb_scores(request, await request.body())
        except NDBRuntimeUnavailable as exc:
            return Response(content=json.dumps({"error":"ndb_runtime_unavailable","detail":str(exc)}), status_code=503, media_type="application/json")
        is_primary = request.url.path in PRIMARY_ROUTES
        decision = recommend_policy(scores["ndb_score"], scores["tide"], scores["stigma_level"])
        if is_primary and decision == "block":
            response = Response(content="Blocked by Resonance Policy", status_code=403)
        elif is_primary and decision == "throttle":
            response = Response(content="Throttled by Resonance Policy", status_code=429)
        else:
            response = await call_next(request)
        event = {
            "timestamp": int(time.time()), "correlation_id": correlation_id,
            "endpoint": scores["endpoint"], "action": request.method,
            "ndb_score": scores["ndb_score"], "ndb_delta": scores["ndb_delta"],
            "tide": scores["tide"], "stigma_level": scores["stigma_level"],
            "node_id": scores["node_id"], "primary": is_primary, "decision": decision,
            "outcome": response.status_code, "source": "nanogrid-runtime",
        }
        with open(RESONANCE_FILE, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return response
