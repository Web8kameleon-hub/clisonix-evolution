from collections import Counter, deque
from datetime import datetime, timezone
from typing import Any, Deque, Dict, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Clisonix Agent Telemetry", version="1.0.0")

MAX_EVENTS = 10000
EVENTS: Deque[Dict[str, Any]] = deque(maxlen=MAX_EVENTS)


class TelemetryEvent(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    event_type: str = Field(min_length=1, max_length=128)
    service: Optional[str] = Field(default=None, max_length=128)
    trace_id: Optional[str] = Field(default=None, max_length=128)
    latency_ms: Optional[float] = Field(default=None, ge=0)
    success: Optional[bool] = True
    payload: Dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "agent-telemetry"}


@app.get("/status")
def status():
    return {
        "status": "operational",
        "service": "agent-telemetry",
        "events_buffered": len(EVENTS),
        "max_events": MAX_EVENTS,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/telemetry/events")
def ingest_event(event: TelemetryEvent):
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **event.model_dump(),
    }
    EVENTS.append(record)
    return {"accepted": True, "buffered": len(EVENTS)}


@app.get("/api/v1/telemetry/events")
def list_events(limit: int = Query(default=100, ge=1, le=1000), agent_id: Optional[str] = None):
    rows = list(EVENTS)
    if agent_id:
        rows = [row for row in rows if row.get("agent_id") == agent_id]
    return {"count": min(len(rows), limit), "events": rows[-limit:]}


@app.get("/api/v1/telemetry/metrics")
def metrics():
    if not EVENTS:
        return {
            "events": 0,
            "success_rate": 0.0,
            "event_types": {},
            "agents": {},
            "avg_latency_ms": 0.0,
        }

    event_types = Counter(event.get("event_type", "unknown") for event in EVENTS)
    agents = Counter(event.get("agent_id", "unknown") for event in EVENTS)

    total = len(EVENTS)
    success = sum(1 for event in EVENTS if event.get("success") is True)
    latencies = [float(event["latency_ms"]) for event in EVENTS if event.get("latency_ms") is not None]

    return {
        "events": total,
        "success_rate": round((success / total) * 100.0, 2),
        "event_types": dict(event_types),
        "agents": dict(agents),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0.0,
    }


@app.delete("/api/v1/telemetry/events")
def clear_events(confirm: bool = Query(default=False)):
    if not confirm:
        raise HTTPException(status_code=400, detail="Set confirm=true to clear telemetry buffer")
    EVENTS.clear()
    return {"cleared": True}
