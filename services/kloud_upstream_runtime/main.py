import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

SERVICE_NAME = "kloud-upstream-runtime"
SERVICE_VERSION = "0.1.0"
PORT = int(os.getenv("PORT", "9080"))
STATE_PATH = Path(os.getenv("KLOUD_RUNTIME_STATE_PATH", "/app/data/runtime-state.json"))
RUNTIME_NODE_ID = os.getenv("KLOUD_RUNTIME_NODE_ID", "aiagi-node-01").strip() or "aiagi-node-01"
RUNTIME_ROLE = os.getenv("KLOUD_RUNTIME_ROLE", "coordinator").strip() or "coordinator"
RUNTIME_REGION = os.getenv("KLOUD_RUNTIME_REGION", "eu-central").strip() or "eu-central"
RUNTIME_PUBLIC_BASE_URL = os.getenv("KLOUD_RUNTIME_PUBLIC_BASE_URL", "https://aiagi.io").strip().rstrip("/")
START_TIME = time.time()
_STATE_LOCK = RLock()

app = FastAPI(title="Kloud Upstream Runtime", version=SERVICE_VERSION)


class RegisterNodeRequest(BaseModel):
    node_id: str = Field(..., min_length=2, max_length=80)
    role: str = Field(default="worker", min_length=2, max_length=80)
    region: str = Field(default="global", min_length=2, max_length=80)
    capabilities: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HeartbeatRequest(BaseModel):
    node_id: str = Field(..., min_length=2, max_length=80)
    status: str = Field(default="online", min_length=2, max_length=40)
    latency_ms: Optional[float] = Field(default=None, ge=0)
    load: Optional[float] = Field(default=None, ge=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SubmitRequest(BaseModel):
    source: str = Field(default="kloud-bridge", min_length=2, max_length=120)
    ops: List[str] = Field(default_factory=list)
    payload: Any = None
    tags: List[str] = Field(default_factory=list)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_state_parent() -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _default_state() -> Dict[str, Any]:
    created_at = _now_iso()
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "created_at": created_at,
        "updated_at": created_at,
        "nodes": {},
        "submissions": [],
    }


def _bootstrap_runtime_node(state: Dict[str, Any]) -> Dict[str, Any]:
    nodes = state.setdefault("nodes", {})
    existing = nodes.get(RUNTIME_NODE_ID, {})
    node = {
        "node_id": RUNTIME_NODE_ID,
        "role": existing.get("role", RUNTIME_ROLE),
        "region": existing.get("region", RUNTIME_REGION),
        "capabilities": existing.get("capabilities", ["mesh-routing", "coordination", "ai-runtime"]),
        "metadata": existing.get("metadata", {}),
        "status": existing.get("status", "online"),
        "reachable": True,
        "public_base_url": existing.get("public_base_url", RUNTIME_PUBLIC_BASE_URL or None),
        "registered_at": existing.get("registered_at", _now_iso()),
        "last_seen_at": existing.get("last_seen_at", _now_iso()),
        "latency_ms": existing.get("latency_ms", 0.0),
        "load": existing.get("load", 0.0),
    }
    nodes[RUNTIME_NODE_ID] = node
    state["updated_at"] = _now_iso()
    return state


def _load_state() -> Dict[str, Any]:
    _ensure_state_parent()
    if not STATE_PATH.exists():
        state = _bootstrap_runtime_node(_default_state())
        _persist_state(state)
        return state

    try:
        raw = json.loads(STATE_PATH.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raw = _default_state()
    except Exception:
        raw = _default_state()

    state = _bootstrap_runtime_node(raw)
    _persist_state(state)
    return state


def _persist_state(state: Dict[str, Any]) -> None:
    _ensure_state_parent()
    state["updated_at"] = _now_iso()
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


_STATE = _load_state()


def _snapshot() -> Dict[str, Any]:
    with _STATE_LOCK:
        return json.loads(json.dumps(_STATE))


def _upsert_node(node_id: str, **fields: Any) -> Dict[str, Any]:
    with _STATE_LOCK:
        nodes = _STATE.setdefault("nodes", {})
        current = nodes.get(node_id, {})
        merged = {
            "node_id": node_id,
            "role": current.get("role", "worker"),
            "region": current.get("region", "global"),
            "capabilities": current.get("capabilities", []),
            "metadata": current.get("metadata", {}),
            "status": current.get("status", "registered"),
            "reachable": current.get("reachable", False),
            "public_base_url": current.get("public_base_url"),
            "registered_at": current.get("registered_at", _now_iso()),
            "last_seen_at": current.get("last_seen_at"),
            "latency_ms": current.get("latency_ms"),
            "load": current.get("load"),
        }
        for key, value in fields.items():
            if value is not None:
                merged[key] = value
        nodes[node_id] = merged
        _persist_state(_STATE)
        return json.loads(json.dumps(merged))


def _node_list() -> List[Dict[str, Any]]:
    state = _snapshot()
    nodes = list(state.get("nodes", {}).values())
    return sorted(nodes, key=lambda item: (item.get("role") != "coordinator", item.get("node_id", "")))


def _online_count(nodes: List[Dict[str, Any]]) -> int:
    return sum(1 for node in nodes if str(node.get("status", "")).lower() in {"online", "ready", "healthy"})


def _last_submit(state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    submissions = state.get("submissions", [])
    return submissions[-1] if submissions else None


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "status": "ok",
        "node_id": RUNTIME_NODE_ID,
        "docs": "/docs",
    }


@app.get("/health")
def health() -> Dict[str, Any]:
    nodes = _node_list()
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "registered_node_count": len(nodes),
        "online_node_count": _online_count(nodes),
    }


@app.get("/status")
def status() -> Dict[str, Any]:
    state = _snapshot()
    nodes = _node_list()
    last_submit = _last_submit(state)
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "runtime": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "node_id": RUNTIME_NODE_ID,
        "role": RUNTIME_ROLE,
        "region": RUNTIME_REGION,
        "public_base_url": RUNTIME_PUBLIC_BASE_URL or None,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "sync": "ready" if last_submit else "waiting",
        "received_submit_count": len(state.get("submissions", [])),
        "last_submit_at": last_submit.get("received_at") if last_submit else None,
        "registered_node_count": len(nodes),
        "online_node_count": _online_count(nodes),
        "nodes": [
            {
                "id": node.get("node_id"),
                "state": node.get("status"),
                "role": node.get("role"),
                "region": node.get("region"),
            }
            for node in nodes
        ],
    }


@app.get("/peers")
def peers() -> Dict[str, Any]:
    peers_list = [
        {
            "id": node.get("node_id"),
            "role": node.get("role"),
            "region": node.get("region"),
            "reachable": str(node.get("status", "")).lower() in {"online", "ready", "healthy"},
            "status": node.get("status"),
            "last_seen_at": node.get("last_seen_at"),
            "capabilities": node.get("capabilities", []),
        }
        for node in _node_list()
    ]
    return {
        "service": SERVICE_NAME,
        "count": len(peers_list),
        "peers": peers_list,
    }


@app.get("/state")
def state() -> Dict[str, Any]:
    snapshot = _snapshot()
    nodes = _node_list()
    last_submit = _last_submit(snapshot)
    online_count = _online_count(nodes)
    return {
        "service": SERVICE_NAME,
        "state": "synchronized" if last_submit else "monitoring",
        "proof_of_life": bool(online_count > 0 or last_submit),
        "registered_node_count": len(nodes),
        "online_node_count": online_count,
        "last_submit_at": last_submit.get("received_at") if last_submit else None,
        "last_submit_source": last_submit.get("source") if last_submit else None,
        "mesh": {
            "coordinator": RUNTIME_NODE_ID,
            "region": RUNTIME_REGION,
        },
    }


@app.get("/nodes")
def list_nodes() -> Dict[str, Any]:
    nodes = _node_list()
    return {
        "service": SERVICE_NAME,
        "count": len(nodes),
        "nodes": nodes,
    }


@app.post("/nodes/register")
def register_node(request: RegisterNodeRequest) -> Dict[str, Any]:
    node = _upsert_node(
        request.node_id,
        role=request.role,
        region=request.region,
        capabilities=request.capabilities,
        metadata=request.metadata,
        status="registered" if request.node_id != RUNTIME_NODE_ID else "online",
        reachable=request.node_id == RUNTIME_NODE_ID,
        last_seen_at=_now_iso() if request.node_id == RUNTIME_NODE_ID else None,
    )
    return {
        "registered": True,
        "node": node,
        "count": len(_node_list()),
    }


@app.post("/nodes/heartbeat")
def node_heartbeat(request: HeartbeatRequest) -> Dict[str, Any]:
    existing_nodes = {node["node_id"] for node in _node_list()}
    if request.node_id not in existing_nodes:
        _upsert_node(
            request.node_id,
            role="worker",
            region="unknown",
            capabilities=[],
            metadata={},
            status="registered",
            reachable=False,
        )

    node = _upsert_node(
        request.node_id,
        status=request.status,
        reachable=str(request.status).lower() in {"online", "ready", "healthy"},
        latency_ms=request.latency_ms,
        load=request.load,
        metadata=request.metadata,
        last_seen_at=_now_iso(),
    )
    return {
        "status": "heartbeat-recorded",
        "node": node,
        "online_node_count": _online_count(_node_list()),
    }


@app.post("/submit")
def submit(request: SubmitRequest) -> Dict[str, Any]:
    with _STATE_LOCK:
        if request.source and request.source not in _STATE.setdefault("nodes", {}):
            _STATE["nodes"][request.source] = {
                "node_id": request.source,
                "role": "bridge-client",
                "region": "external",
                "capabilities": ["submit"],
                "metadata": {},
                "status": "online",
                "reachable": True,
                "public_base_url": None,
                "registered_at": _now_iso(),
                "last_seen_at": _now_iso(),
                "latency_ms": None,
                "load": None,
            }

        entry = {
            "received_at": _now_iso(),
            "source": request.source,
            "ops": request.ops,
            "tags": request.tags,
            "payload_present": request.payload is not None,
        }
        _STATE.setdefault("submissions", []).append(entry)
        _STATE["submissions"] = _STATE["submissions"][-500:]
        _persist_state(_STATE)

    return {
        "accepted": True,
        "status": "queued",
        "received_at": entry["received_at"],
        "received_submit_count": len(_snapshot().get("submissions", [])),
        "mesh_state": "active",
        "echo": {
            "source": request.source,
            "ops": request.ops,
            "payload_present": request.payload is not None,
        },
    }


@app.get("/admin/summary")
def admin_summary() -> Dict[str, Any]:
    state = _snapshot()
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "state_path": str(STATE_PATH),
        "updated_at": state.get("updated_at"),
        "node_count": len(state.get("nodes", {})),
        "submission_count": len(state.get("submissions", [])),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
