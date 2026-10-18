# NDB Advisory Mode Middleware (FastAPI)
# NO_FAKE: consumes measurements from the real NanoGrid-backed shadow adapter.

import json
import os
import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from ndb_shadow_sidecar import NDBRuntimeUnavailable, compute_ndb_scores

ADVISORY_FILE = os.environ.get("NDB_ADVISORY_EVENTS_FILE", "ndb_advisory_events.jsonl")
NDB_BLOCK_THRESHOLD = float(os.environ.get("NDB_BLOCK_THRESHOLD", "0.80"))
NDB_THROTTLE_THRESHOLD = float(os.environ.get("NDB_THROTTLE_THRESHOLD", "0.65"))
NDB_MONITOR_THRESHOLD = float(os.environ.get("NDB_MONITOR_THRESHOLD", "0.40"))

def recommend_policy(ndb_score, tide, stigma_level):
    del tide
    if ndb_score >= NDB_BLOCK_THRESHOLD or stigma_level >= 3:
        return "block"
    if ndb_score >= NDB_THROTTLE_THRESHOLD:
        return "throttle"
    if ndb_score >= NDB_MONITOR_THRESHOLD:
        return "monitor"
    return "allow"

class NDBAdvisoryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if os.environ.get("NDB_ADVISORY_ENABLED", "0") != "1":
            return await call_next(request)
        correlation_id = str(uuid.uuid4())
        try:
            scores = compute_ndb_scores(request, await request.body())
        except NDBRuntimeUnavailable as exc:
            return Response(content=json.dumps({"error":"ndb_runtime_unavailable","detail":str(exc)}), status_code=503, media_type="application/json")
        recommendation = recommend_policy(scores["ndb_score"], scores["tide"], scores["stigma_level"])
        response: Response = await call_next(request)
        event = {
            "timestamp": int(time.time()), "correlation_id": correlation_id,
            "endpoint": scores["endpoint"], "action": request.method,
            "ndb_score": scores["ndb_score"], "ndb_delta": scores["ndb_delta"],
            "tide": scores["tide"], "stigma_level": scores["stigma_level"],
            "node_id": scores["node_id"], "recommendation": recommendation,
            "outcome": response.status_code, "source": "nanogrid-runtime",
        }
        with open(ADVISORY_FILE, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return response
