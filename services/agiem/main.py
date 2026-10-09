from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Clisonix AGIEM", version="1.0.0")

AGENTS: Dict[str, Dict[str, Any]] = {}


class AgentRegistration(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    role: str = Field(min_length=1, max_length=128)
    endpoint: str = Field(min_length=1, max_length=256)
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentHeartbeat(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    healthy: bool = True
    latency_ms: Optional[float] = Field(default=None, ge=0)
    metrics: Dict[str, Any] = Field(default_factory=dict)


@app.get("/health")
def health():
    return {"status": "healthy", "service": "agiem"}


@app.get("/status")
def status():
    healthy = sum(1 for row in AGENTS.values() if row.get("last_healthy") is True)
    return {
        "status": "operational",
        "service": "agiem",
        "registered_agents": len(AGENTS),
        "healthy_agents": healthy,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/agents/register")
def register_agent(payload: AgentRegistration):
    now = datetime.now(timezone.utc).isoformat()
    AGENTS[payload.agent_id] = {
        **payload.model_dump(),
        "registered_at": now,
        "last_seen": now,
        "last_healthy": True,
        "last_latency_ms": None,
    }
    return {"registered": True, "agent_id": payload.agent_id}


@app.post("/api/v1/agents/heartbeat")
def heartbeat(payload: AgentHeartbeat):
    if payload.agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail="agent not registered")

    AGENTS[payload.agent_id]["last_seen"] = datetime.now(timezone.utc).isoformat()
    AGENTS[payload.agent_id]["last_healthy"] = payload.healthy
    AGENTS[payload.agent_id]["last_latency_ms"] = payload.latency_ms
    AGENTS[payload.agent_id]["last_metrics"] = payload.metrics
    return {"accepted": True}


@app.get("/api/v1/agents")
def list_agents(healthy_only: bool = Query(default=False)):
    rows = list(AGENTS.values())
    if healthy_only:
        rows = [row for row in rows if row.get("last_healthy") is True]
    return {"count": len(rows), "agents": rows}


@app.delete("/api/v1/agents/{agent_id}")
def remove_agent(agent_id: str):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail="agent not found")
    del AGENTS[agent_id]
    return {"removed": True, "agent_id": agent_id}
