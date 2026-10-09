from __future__ import annotations

import base64
import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

SERVICE_NAME = "kloud-bridge"
SERVICE_VERSION = "0.5.0"
API_PREFIX = "/api/v1"
PORT = int(os.getenv("PORT", os.getenv("KLOUD_BRIDGE_PORT", "8889")))
KLOUD_UPSTREAM_URL = os.getenv("KLOUD_UPSTREAM_URL", "").strip().rstrip("/")
KLOUD_UPSTREAM_CANDIDATES_RAW = os.getenv("KLOUD_UPSTREAM_CANDIDATES", "")
KLOUD_SIGNAL_PATH = os.getenv("KLOUD_SIGNAL_PATH", "/submit")
KLOUD_STATUS_PATH = os.getenv("KLOUD_STATUS_PATH", "/status")
KLOUD_PEERS_PATH = os.getenv("KLOUD_PEERS_PATH", "/peers")
KLOUD_STATE_PATH = os.getenv("KLOUD_STATE_PATH", "/state")
KLOUD_ISOLATED_MODE = os.getenv("KLOUD_ISOLATED_MODE", "true").lower() == "true"
KLOUD_TIMEOUT_SECONDS = float(os.getenv("KLOUD_TIMEOUT_SECONDS", "8"))
KLOUD_LLM_UPSTREAM_URL = os.getenv("KLOUD_LLM_UPSTREAM_URL", "").strip().rstrip("/")
KLOUD_LLM_CHAT_PATH = os.getenv("KLOUD_LLM_CHAT_PATH", "/api/v1/chat").strip() or "/api/v1/chat"
KLOUD_LLM_TIMEOUT_SECONDS = max(1.0, float(os.getenv("KLOUD_LLM_TIMEOUT_SECONDS", str(KLOUD_TIMEOUT_SECONDS))))
KLOUD_LLM_STREAM_CHUNK_CHARS = max(8, int(os.getenv("KLOUD_LLM_STREAM_CHUNK_CHARS", "48")))
OCEAN_CORE_URL = os.getenv("OCEAN_CORE_URL", "http://clisonix-ocean-core:8030").rstrip("/")
OCEAN_STATUS_PATH = os.getenv("OCEAN_STATUS_PATH", "/api/v1/status")
OCEAN_SIGNAL_PATH = os.getenv("OCEAN_SIGNAL_PATH", "/api/v1/signals/internal")
KLOUD_BRIDGE_ADMIN_TOKEN = (
    os.getenv("KLOUD_BRIDGE_ADMIN_TOKEN", "").strip()
    or os.getenv("OCEAN_ADMIN_API_TOKEN", "").strip()
)
KLOUD_NODE_API_TOKEN = os.getenv("KLOUD_NODE_API_TOKEN", "").strip()
LIVE_ONLY_MODE = True
BRIDGE_MODE = "production-live" if LIVE_ONLY_MODE else "integration-flex"
ENFORCEMENT_MODE = "hard" if LIVE_ONLY_MODE else "soft"
INSTANCE_ID = os.getenv("INSTANCE_ID", str(uuid.uuid4())[:8])
START_TIME = time.time()
_LAST_LIVE_UPSTREAM_URL = ""
_LAST_SUCCESSFUL_SYNC_AT: Optional[str] = None
_LAST_UPSTREAM_ERROR = ""
_LAST_SIGNAL_ACTIVITY: Dict[str, Any] = {}
KLOUD_NODE_REGISTRY_PATH = os.getenv(
    "KLOUD_NODE_REGISTRY_PATH",
    os.path.join(os.path.dirname(__file__), "data", "hardware_nodes.json"),
).strip()
AUDIT_LOG_PATH = os.getenv(
    "KLOUD_AUDIT_LOG_PATH",
    os.path.join(os.path.dirname(__file__), "data", "audit_events.jsonl"),
).strip()
OPENAPI_SNAPSHOT_PATH = os.getenv(
    "KLOUD_OPENAPI_SNAPSHOT_PATH",
    os.path.join(os.path.dirname(__file__), "openapi", "kloud-bridge-openapi-v1.json"),
).strip()
KLOUD_NODE_HEARTBEAT_TTL_SECONDS = max(5.0, float(os.getenv("KLOUD_NODE_HEARTBEAT_TTL_SECONDS", "30")))
KLOUD_NODE_OFFLINE_GRACE_SECONDS = max(
    KLOUD_NODE_HEARTBEAT_TTL_SECONDS,
    float(os.getenv("KLOUD_NODE_OFFLINE_GRACE_SECONDS", "90")),
)
KLOUD_MESH_PING_TIMEOUT_MS = max(100, int(os.getenv("KLOUD_MESH_PING_TIMEOUT_MS", "1500")))
_LAST_REGISTRY_SYNC_AT: Optional[str] = None
_LAST_REGISTRY_ERROR = ""
_LAST_AUDIT_WRITE_AT: Optional[str] = None
_LAST_AUDIT_ERROR = ""
_LAST_OPENAPI_EXPORT_AT: Optional[str] = None
_LAST_OPENAPI_EXPORT_ERROR = ""
HARDWARE_NODES: Dict[str, Dict[str, Any]] = {}
HEARTBEAT_CONFORMANCE: Dict[str, Any] = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "last_pass_at": None,
    "last_failure_at": None,
    "last_failure_reasons": [],
    "by_node": {},
}
NON_LIVE_NODE_ID_PREFIXES = (
    "test-",
    "verify-",
    "mesh-",
    "root-",
    "ministry-",
    "command-",
    "division-",
    "brigade-",
    "battalion-",
    "company-",
    "platoon-",
    "soldier-",
)
NON_LIVE_SOURCES = {"manual-verify", "verification", "demo", "stub", "mock"}
NON_LIVE_DEPLOYMENT_TARGETS = {"prototype-lab", "verification", "demo"}
HARDWARE_PROFILE: Dict[str, Any] = {
    "name": "OceanCore + KLOUd hardware path",
    "phase": "prototype-contract",
    "chip_ready": False,
    "target_architecture": "RISC-V",
    "runtime": "Rust + GNU-compatible toolchain",
    "role": "Physical edge execution layer for signal processing, telemetry, and distributed coordination.",
    "principles": [
        "Clisonix remains the product and intelligence layer.",
        "Kloud remains the sovereign runtime and trust fabric.",
        "Hardware stays behind the isolated bridge contract.",
        "Use real telemetry and heartbeat signals instead of demo state.",
        "Validate with prototypes before any ASIC claim.",
    ],
}
HIERARCHY_RANK_ORDER: Dict[str, int] = {
    "root": 0,
    "ministry": 1,
    "command": 2,
    "division": 3,
    "brigade": 4,
    "battalion": 5,
    "company": 6,
    "platoon": 7,
    "soldier": 8,
}
HIERARCHY_BLUEPRINT: List[Dict[str, Any]] = [
    {"rank": "root", "label": "Komanda Qendrore", "symbol": "🌍", "parent_rank": None},
    {"rank": "ministry", "label": "Ministri-1", "symbol": "🏛️", "parent_rank": "root"},
    {"rank": "command", "label": "Komanda-1", "symbol": "🏆", "parent_rank": "ministry"},
    {"rank": "division", "label": "Divizion-1", "symbol": "⚔️", "parent_rank": "command"},
    {"rank": "brigade", "label": "Brigada-1", "symbol": "🏰", "parent_rank": "division"},
    {"rank": "battalion", "label": "Batalion-1", "symbol": "🏛️", "parent_rank": "brigade"},
    {"rank": "company", "label": "Kompania-1..3", "symbol": "🏅", "parent_rank": "battalion"},
    {"rank": "platoon", "label": "Toga-1..5", "symbol": "🎖️", "parent_rank": "company"},
    {"rank": "soldier", "label": "Ushtarët 1..10", "symbol": "🪖", "parent_rank": "platoon"},
]
FIRMWARE_CONTRACT: Dict[str, Any] = {
    "version": "v0.2",
    "transport": "http-json",
    "register_endpoint": "/hardware/nodes/register",
    "heartbeat_endpoint": "/hardware/nodes/heartbeat",
    "pulse_endpoint": "/hardware/nodes/pulse",
    "mesh_status_endpoint": "/hardware/mesh/status",
    "mesh_ping_endpoint": "/hardware/mesh/ping",
    "node_detail_endpoint": "/hardware/nodes/{node_id}",
    "recommended_heartbeat_seconds": 15,
    "heartbeat_ttl_seconds": KLOUD_NODE_HEARTBEAT_TTL_SECONDS,
    "offline_grace_seconds": KLOUD_NODE_OFFLINE_GRACE_SECONDS,
    "required_registration_fields": [
        "node_id",
        "node_class",
        "architecture",
        "runtime",
        "firmware_version",
    ],
    "required_heartbeat_fields": [
        "node_id",
        "status",
    ],
    "required_pulse_fields": [
        "node_id",
    ],
    "optional_metrics": [
        "uptime_seconds",
        "temperature_c",
        "power_watts",
        "latency_ms",
        "telemetry",
        "queue_depth",
        "mesh_role",
    ],
    "status_values": ["registered", "online", "stale", "degraded", "offline", "maintenance"],
    "notes": [
        "Register before sending heartbeats or pulse frames.",
        "Pulse is the lightweight proof-of-life path for real nodes.",
        "Ping-pong validates node-to-node mesh reachability through the isolated bridge.",
        "Forward-to-Ocean is optional and reserved for routed internal signals.",
    ],
    "security": {
        "auth": "x-node-token or Bearer token when KLOUD_NODE_API_TOKEN is configured",
        "roles": ["node", "operator", "admin"],
    },
}
FAILURE_MODE_MATRIX: Dict[str, Dict[str, Any]] = {
    "GET /health": {
        "mode": "fail-open",
        "dependencies": ["local"],
        "on_failure": "Return degraded configuration status while keeping health endpoint responsive.",
        "user_status_on_failure": "degraded",
    },
    "GET /status": {
        "mode": "fail-open",
        "dependencies": ["upstream", "ocean"],
        "on_failure": "Return partial bridge visibility and explicit recovery guidance.",
        "user_status_on_failure": "partial-outage",
    },
    "GET /fabric/summary": {
        "mode": "fail-open",
        "dependencies": ["upstream", "ocean"],
        "on_failure": "Expose compact partial-sync summary for dashboards.",
        "user_status_on_failure": "partial-outage",
    },
    "GET /admin/diagnostics": {
        "mode": "fail-open-secured",
        "dependencies": ["upstream", "ocean", "admin_token"],
        "on_failure": "Keep diagnostics available with explicit dependency-level failure details.",
        "user_status_on_failure": "degraded",
    },
    "POST /signals/publish": {
        "mode": "fail-closed",
        "dependencies": ["upstream"],
        "on_failure": "Reject signal forwarding when sovereign target is not configured/reachable.",
        "user_status_on_failure": "blocked",
    },
    "POST /fabric/sync": {
        "mode": "fail-closed",
        "dependencies": ["upstream"],
        "on_failure": "Reject synchronization when no live sovereign snapshot can be collected.",
        "user_status_on_failure": "blocked",
    },
    "POST /ocean/signals/publish": {
        "mode": "fail-closed",
        "dependencies": ["ocean"],
        "on_failure": "Reject forward-to-ocean when Ocean Core is not configured/reachable.",
        "user_status_on_failure": "blocked",
    },
    "POST /hardware/nodes/heartbeat": {
        "mode": "fail-closed",
        "dependencies": ["firmware_contract", "node_registration"],
        "on_failure": "Reject invalid heartbeat payloads and unregistered nodes with explicit reasons.",
        "user_status_on_failure": "rejected",
    },
}

app = FastAPI(
    title="Clisonix Kloud Bridge",
    version=SERVICE_VERSION,
    description="Isolated bridge microservice that connects Clisonix to the sovereign Kloud fabric without merging codebases.",
)


class PublishRequest(BaseModel):
    ops: List[str] = Field(default_factory=lambda: ["S"])
    payload: Dict[str, Any] = Field(default_factory=dict)
    payload_b64: Optional[str] = None
    source: str = "clisonix"
    route: Optional[str] = None
    dry_run: bool = False


class FabricSyncRequest(BaseModel):
    include_state: bool = True
    include_peers: bool = True
    include_status: bool = True
    dry_run: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OceanSignalRequest(BaseModel):
    event_type: str = "kloud.bridge.signal"
    source: str = "kloud-bridge"
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: str = "normal"
    tags: List[str] = Field(default_factory=lambda: ["kloud", "bridge", "ocean"])
    correlation_id: Optional[str] = None
    dry_run: bool = False


class OpenAIChatCompletionsRequest(BaseModel):
    model: str = "llama3.1:8b"
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    stream: bool = False
    user: Optional[str] = None


class OllamaGenerateRequest(BaseModel):
    model: str = "llama3.1:8b"
    prompt: str = ""
    system: Optional[str] = None
    stream: bool = True
    options: Dict[str, Any] = Field(default_factory=dict)


class HardwareNodeRegistration(BaseModel):
    node_id: str = Field(..., min_length=2, max_length=80)
    node_class: str = "oceancore-edge"
    architecture: str = "riscv"
    runtime: str = "rust"
    transport: str = "http"
    firmware_version: str = "0.1.0"
    display_name: Optional[str] = None
    rank: str = "soldier"
    symbol: Optional[str] = None
    parent_node_id: Optional[str] = None
    sleep_capable: bool = True
    pause_seconds: Optional[float] = Field(default=None, ge=0, le=3600)
    capabilities: List[str] = Field(default_factory=lambda: ["heartbeat", "pulse", "telemetry", "mesh-ping", "hierarchy"])
    metadata: Dict[str, Any] = Field(default_factory=dict)


class HardwareNodeHeartbeat(BaseModel):
    node_id: str = Field(..., min_length=2, max_length=80)
    status: str = "online"
    uptime_seconds: Optional[float] = None
    temperature_c: Optional[float] = None
    power_watts: Optional[float] = None
    latency_ms: Optional[float] = None
    telemetry: Dict[str, Any] = Field(default_factory=dict)
    forward_to_ocean: bool = False


class HardwareNodePulse(BaseModel):
    node_id: str = Field(..., min_length=2, max_length=80)
    signal: str = "pulse"
    latency_ms: Optional[float] = None
    queue_depth: Optional[int] = None
    telemetry: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MeshPingRequest(BaseModel):
    source_node_id: str = Field(..., min_length=2, max_length=80)
    target_node_id: str = Field(..., min_length=2, max_length=80)
    signal: str = "ping"
    ttl_ms: int = Field(default=KLOUD_MESH_PING_TIMEOUT_MS, ge=100, le=10000)
    payload: Dict[str, Any] = Field(default_factory=dict)


class NodeControlRequest(BaseModel):
    node_id: str = Field(..., min_length=2, max_length=80)
    action: str = "pause"
    duration_seconds: Optional[float] = Field(default=30, ge=0, le=86400)
    reason: str = "operator-control"


class HierarchyCommandRequest(BaseModel):
    source_node_id: str = Field(..., min_length=2, max_length=80)
    message: str = Field(..., min_length=1, max_length=1000)
    target_node_id: Optional[str] = None
    direction: str = "downstream"
    pause_ms: int = Field(default=0, ge=0, le=3000)
    max_depth: int = Field(default=8, ge=1, le=12)
    metadata: Dict[str, Any] = Field(default_factory=dict)


def _normalize_candidate_urls() -> List[str]:
    def _is_self_referential_upstream(candidate: str) -> bool:
        try:
            parsed = urlparse(candidate)
            host = (parsed.hostname or "").strip().lower()
            if not host:
                return False

            effective_port = parsed.port
            if effective_port is None:
                if parsed.scheme == "https":
                    effective_port = 443
                elif parsed.scheme == "http":
                    effective_port = 80

            self_hosts = {
                "localhost",
                "127.0.0.1",
                "0.0.0.0",
                "kloud-bridge",
                "clisonix-kloud-bridge",
                SERVICE_NAME,
                INSTANCE_ID.lower(),
            }

            runtime_hostname = (os.getenv("HOSTNAME", "") or "").strip().lower()
            if runtime_hostname:
                self_hosts.add(runtime_hostname)

            if host in self_hosts and effective_port == PORT:
                return True

            if "/api/kloud-bridge" in (parsed.path or ""):
                return True

            return False
        except Exception:
            return False

    raw_candidates: List[str] = [KLOUD_UPSTREAM_URL]
    if KLOUD_UPSTREAM_CANDIDATES_RAW:
        raw_candidates.extend(part.strip() for part in KLOUD_UPSTREAM_CANDIDATES_RAW.split(","))
    raw_candidates.extend(
        [
            "http://kloud-upstream-runtime:9080",
            "https://aiagi.io",
            "http://host.docker.internal:9080",
            "http://host.containers.internal:9080",
            "http://gateway.docker.internal:9080",
            "http://172.17.0.1:9080",
            "http://172.18.0.1:9080",
            "http://127.0.0.1:9080",
            "http://localhost:9080",
        ]
    )

    normalized: List[str] = []
    for item in raw_candidates:
        candidate = (item or "").strip().rstrip("/")
        if not candidate:
            continue
        if _is_self_referential_upstream(candidate):
            continue
        if candidate not in normalized:
            normalized.append(candidate)
    return normalized


def _ordered_upstream_candidates() -> List[str]:
    ordered: List[str] = []
    if _LAST_LIVE_UPSTREAM_URL:
        ordered.append(_LAST_LIVE_UPSTREAM_URL)
    ordered.extend(_normalize_candidate_urls())
    return list(dict.fromkeys(ordered))


def _current_upstream_target() -> Optional[str]:
    candidates = _ordered_upstream_candidates()
    return candidates[0] if candidates else None


def _require_admin_access(x_admin_token: Optional[str] = None, authorization: Optional[str] = None) -> None:
    configured = (KLOUD_BRIDGE_ADMIN_TOKEN or "").strip()
    if not configured:
        _append_audit_event(
            "auth.admin",
            "disabled",
            "Admin diagnostics token is not configured.",
            actor="system",
        )
        raise HTTPException(status_code=503, detail="Admin diagnostics token is not configured")

    auth_header = (authorization or "").strip()
    bearer = auth_header[7:].strip() if auth_header.lower().startswith("bearer ") else ""
    candidate = (x_admin_token or "").strip() or bearer
    if candidate != configured:
        _append_audit_event(
            "auth.admin",
            "denied",
            "Unauthorized admin access attempt.",
            actor="anonymous",
            metadata={
                "has_admin_header": bool((x_admin_token or "").strip()),
                "has_bearer_token": bool(bearer),
            },
        )
        raise HTTPException(status_code=401, detail="Unauthorized")


def _require_node_access(x_node_token: Optional[str] = None, authorization: Optional[str] = None) -> None:
    configured = (KLOUD_NODE_API_TOKEN or "").strip()
    if not configured:
        return

    auth_header = (authorization or "").strip()
    bearer = auth_header[7:].strip() if auth_header.lower().startswith("bearer ") else ""
    candidate = (x_node_token or "").strip() or bearer
    admin_token = (KLOUD_BRIDGE_ADMIN_TOKEN or "").strip()
    if candidate not in {configured, admin_token}:
        _append_audit_event(
            "auth.node",
            "denied",
            "Unauthorized node access attempt.",
            actor="unknown-node",
            metadata={
                "has_node_header": bool((x_node_token or "").strip()),
                "has_bearer_token": bool(bearer),
            },
        )
        raise HTTPException(status_code=401, detail="Unauthorized node token")


def _security_summary() -> Dict[str, Any]:
    return {
        "auth": {
            "admin": "x-admin-token or Bearer token",
            "node": "x-node-token or Bearer token" if KLOUD_NODE_API_TOKEN else "optional-until-configured",
        },
        "roles": ["operator", "node", "admin"],
        "admin_token_configured": bool(KLOUD_BRIDGE_ADMIN_TOKEN),
        "node_token_configured": bool(KLOUD_NODE_API_TOKEN),
        "mode": BRIDGE_MODE,
        "enforcement": ENFORCEMENT_MODE,
    }


def _registry_summary() -> Dict[str, Any]:
    return {
        "backend": "json-file",
        "path": KLOUD_NODE_REGISTRY_PATH,
        "persistent": True,
        "last_sync_at": _LAST_REGISTRY_SYNC_AT,
        "last_error": _LAST_REGISTRY_ERROR or None,
    }


def _audit_summary() -> Dict[str, Any]:
    return {
        "backend": "jsonl-file",
        "path": AUDIT_LOG_PATH,
        "enabled": True,
        "last_write_at": _LAST_AUDIT_WRITE_AT,
        "last_error": _LAST_AUDIT_ERROR or None,
    }


def _openapi_summary() -> Dict[str, Any]:
    return {
        "path": OPENAPI_SNAPSHOT_PATH,
        "last_export_at": _LAST_OPENAPI_EXPORT_AT,
        "last_error": _LAST_OPENAPI_EXPORT_ERROR or None,
    }


def _append_audit_event(
    event_type: str,
    outcome: str,
    detail: str,
    actor: str = "system",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    global _LAST_AUDIT_WRITE_AT, _LAST_AUDIT_ERROR

    entry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "instance": INSTANCE_ID,
        "mode": BRIDGE_MODE,
        "event_type": event_type,
        "outcome": outcome,
        "actor": actor,
        "detail": detail,
        "metadata": metadata or {},
    }

    try:
        directory = os.path.dirname(AUDIT_LOG_PATH)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        _LAST_AUDIT_WRITE_AT = entry["timestamp"]
        _LAST_AUDIT_ERROR = ""
    except Exception as exc:
        _LAST_AUDIT_ERROR = str(exc)


def _read_recent_audit_events(limit: int = 50) -> List[Dict[str, Any]]:
    if limit <= 0 or not os.path.exists(AUDIT_LOG_PATH):
        return []

    try:
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as handle:
            lines = handle.readlines()[-limit:]
        events = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return list(reversed(events))
    except Exception as exc:
        _append_audit_event(
            "audit.read",
            "error",
            "Failed to read recent audit events.",
            actor="system",
            metadata={"error": str(exc), "requested_limit": limit},
        )
        return []


def _export_openapi_snapshot() -> None:
    global _LAST_OPENAPI_EXPORT_AT, _LAST_OPENAPI_EXPORT_ERROR

    try:
        directory = os.path.dirname(OPENAPI_SNAPSHOT_PATH)
        if directory:
            os.makedirs(directory, exist_ok=True)
        exported_at = datetime.now(timezone.utc).isoformat()
        schema = app.openapi()
        schema.setdefault("info", {})
        schema["info"]["x-clisonix-service"] = SERVICE_NAME
        schema["info"]["x-exported-at"] = exported_at
        with open(OPENAPI_SNAPSHOT_PATH, "w", encoding="utf-8") as handle:
            json.dump(schema, handle, ensure_ascii=False, indent=2)
        _LAST_OPENAPI_EXPORT_AT = exported_at
        _LAST_OPENAPI_EXPORT_ERROR = ""
    except Exception as exc:
        _LAST_OPENAPI_EXPORT_ERROR = str(exc)


def _is_non_live_seed_node(node_id: str, node: Dict[str, Any]) -> bool:
    lowered_id = str(node_id or "").strip().lower()
    if any(lowered_id.startswith(prefix) for prefix in NON_LIVE_NODE_ID_PREFIXES):
        return True

    metadata_raw = node.get("metadata")
    telemetry_raw = node.get("telemetry")
    metadata: Dict[str, Any] = metadata_raw if isinstance(metadata_raw, dict) else {}
    telemetry: Dict[str, Any] = telemetry_raw if isinstance(telemetry_raw, dict) else {}
    sources = {
        str(metadata.get("source") or "").strip().lower(),
        str(telemetry.get("source") or "").strip().lower(),
    }
    if any(source in NON_LIVE_SOURCES for source in sources if source):
        return True

    deployment_target = str(
        metadata.get("deployment_target") or telemetry.get("deployment_target") or ""
    ).strip().lower()
    if deployment_target in NON_LIVE_DEPLOYMENT_TARGETS:
        return True

    if telemetry.get("last_hierarchy_message"):
        return True

    return False


def _persist_hardware_nodes() -> None:
    global _LAST_REGISTRY_SYNC_AT, _LAST_REGISTRY_ERROR

    try:
        directory = os.path.dirname(KLOUD_NODE_REGISTRY_PATH)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(KLOUD_NODE_REGISTRY_PATH, "w", encoding="utf-8") as handle:
            json.dump(HARDWARE_NODES, handle, ensure_ascii=False, indent=2)
        _LAST_REGISTRY_SYNC_AT = datetime.now(timezone.utc).isoformat()
        _LAST_REGISTRY_ERROR = ""
    except Exception as exc:
        _LAST_REGISTRY_ERROR = str(exc)


def _load_hardware_nodes() -> None:
    global _LAST_REGISTRY_SYNC_AT, _LAST_REGISTRY_ERROR

    try:
        if not os.path.exists(KLOUD_NODE_REGISTRY_PATH):
            return
        with open(KLOUD_NODE_REGISTRY_PATH, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            sanitized = {
                str(node_id): node
                for node_id, node in data.items()
                if isinstance(node, dict)
                and (not LIVE_ONLY_MODE or not _is_non_live_seed_node(str(node_id), node))
            }
            HARDWARE_NODES.clear()
            HARDWARE_NODES.update(sanitized)
            if sanitized != data:
                _persist_hardware_nodes()
            _LAST_REGISTRY_SYNC_AT = datetime.now(timezone.utc).isoformat()
            _LAST_REGISTRY_ERROR = ""
    except Exception as exc:
        _LAST_REGISTRY_ERROR = str(exc)


@app.on_event("startup")
async def load_hardware_registry() -> None:
    _load_hardware_nodes()
    _export_openapi_snapshot()


_load_hardware_nodes()


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "instance": INSTANCE_ID,
        "isolated": KLOUD_ISOLATED_MODE,
        "live_only": LIVE_ONLY_MODE,
        "mode": BRIDGE_MODE,
        "enforcement": ENFORCEMENT_MODE,
        "purpose": "Bridge Clisonix services to the external sovereign Kloud runtime.",
        "policy": "No simulated data or local-accept fallbacks are returned in production live-only mode.",
        "api": {
            "default_version": "v1",
            "primary_prefix": API_PREFIX,
            "legacy_unversioned_paths_supported": True,
        },
        "security": _security_summary(),
        "registry": _registry_summary(),
        "audit": _audit_summary(),
        "contracts": {
            "openapi": "/openapi.json",
            "snapshot": "/api/v1/contracts/openapi-v1",
        },
        "endpoints": {
            "GET /health": "Liveness and configuration probe",
            "GET /status": "Bridge + upstream + Ocean Core visibility",
            "GET /fabric/summary": "Compact NanoGrid/Kloud health summary for dashboards",
            "GET /failure-modes": "Failure mode matrix + dependency state (fail-open/fail-closed)",
            "GET /ocean/status": "Fetch live Ocean Core status through the bridge",
            "GET /hardware/profile": "Professional hardware profile for the OceanCore + KLOUd edge path",
            "GET /hardware/contracts/firmware-v0.1": "Canonical firmware/edge contract for node registration, pulse, and heartbeat behavior",
            "GET /hardware/nodes": "List registered hardware prototype nodes and their live state",
            "GET /hardware/nodes/{node_id}": "Inspect one hardware prototype node in detail",
            "GET /hardware/registry": "Inspect registry backend and persistence state for bound nodes",
            "GET /hardware/mesh/status": "Show multinode mesh health, coordinator, and TTL state",
            "GET /contracts/openapi-v1": "Return and export the current OpenAPI contract snapshot for this bridge",
            "GET /admin/diagnostics": "Protected operator diagnostics with candidate upstream visibility",
            "GET /admin/audit/recent": "Protected recent audit trail for node, auth, and sync lifecycle events",
            "POST /signals/publish": "Forward a real Clisonix signal into Kloud /submit",
            "POST /fabric/sync": "Fetch live remote Kloud state, peers, and status",
            "POST /ocean/signals/publish": "Forward a Kloud-origin signal into Ocean Core routing",
            "POST /hardware/nodes/register": "Register a real OceanCore/KLOUd edge node",
            "POST /hardware/nodes/heartbeat": "Update live heartbeat and optional telemetry for a registered hardware node",
            "POST /hardware/nodes/pulse": "Record a lightweight proof-of-life pulse for a registered node",
            "POST /hardware/mesh/ping": "Validate ping-pong mesh reachability between two registered nodes",
        },
        "hardware": _hardware_summary(),
    }


@app.get("/health")
@app.get(f"{API_PREFIX}/health")
def health() -> Dict[str, Any]:
    upstream_target = _current_upstream_target()
    upstream_configured = bool(upstream_target)
    hardware = _hardware_summary()
    return {
        "status": "ok" if upstream_configured else "degraded",
        "service": SERVICE_NAME,
        "port": PORT,
        "isolated": KLOUD_ISOLATED_MODE,
        "live_only": LIVE_ONLY_MODE,
        "mode": BRIDGE_MODE,
        "enforcement": ENFORCEMENT_MODE,
        "upstream_configured": upstream_configured,
        "upstream_target": upstream_target,
        "ocean_configured": bool(OCEAN_CORE_URL),
        "admin_diagnostics": bool(KLOUD_BRIDGE_ADMIN_TOKEN),
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "hardware_nodes_registered": hardware["registered_nodes"],
        "hardware_nodes_online": hardware["online_nodes"],
        "hardware_nodes_offline": hardware["offline_nodes"],
        "security": _security_summary(),
        "audit": _audit_summary(),
        "openapi_snapshot": _openapi_summary(),
    }


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso_timestamp(value: Any) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _record_heartbeat_conformance(node_id: str, passed: bool, reasons: Optional[List[str]] = None) -> None:
    now_iso = _now_iso()
    HEARTBEAT_CONFORMANCE["total"] += 1
    if passed:
        HEARTBEAT_CONFORMANCE["passed"] += 1
        HEARTBEAT_CONFORMANCE["last_pass_at"] = now_iso
    else:
        HEARTBEAT_CONFORMANCE["failed"] += 1
        HEARTBEAT_CONFORMANCE["last_failure_at"] = now_iso
        HEARTBEAT_CONFORMANCE["last_failure_reasons"] = list(reasons or [])[:10]

    node_key = str(node_id or "unknown").strip() or "unknown"
    by_node = HEARTBEAT_CONFORMANCE.setdefault("by_node", {})
    node_entry = by_node.setdefault(node_key, {"total": 0, "passed": 0, "failed": 0, "last_result": None})
    node_entry["total"] += 1
    if passed:
        node_entry["passed"] += 1
        node_entry["last_result"] = "pass"
    else:
        node_entry["failed"] += 1
        node_entry["last_result"] = "fail"


def _heartbeat_conformance_summary(limit_nodes: int = 5) -> Dict[str, Any]:
    total = int(HEARTBEAT_CONFORMANCE.get("total", 0) or 0)
    passed = int(HEARTBEAT_CONFORMANCE.get("passed", 0) or 0)
    failed = int(HEARTBEAT_CONFORMANCE.get("failed", 0) or 0)
    pass_rate = round((passed / total), 4) if total else 1.0
    fail_rate = round((failed / total), 4) if total else 0.0

    by_node = HEARTBEAT_CONFORMANCE.get("by_node", {})
    sorted_nodes = sorted(
        by_node.items(),
        key=lambda item: int(item[1].get("total", 0) or 0),
        reverse=True,
    )
    top_nodes = [
        {
            "node_id": node_id,
            "total": int(stats.get("total", 0) or 0),
            "passed": int(stats.get("passed", 0) or 0),
            "failed": int(stats.get("failed", 0) or 0),
            "last_result": stats.get("last_result"),
        }
        for node_id, stats in sorted_nodes[: max(1, limit_nodes)]
    ]

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "fail_rate": fail_rate,
        "last_pass_at": HEARTBEAT_CONFORMANCE.get("last_pass_at"),
        "last_failure_at": HEARTBEAT_CONFORMANCE.get("last_failure_at"),
        "last_failure_reasons": HEARTBEAT_CONFORMANCE.get("last_failure_reasons", []),
        "top_nodes": top_nodes,
    }


def _validate_hardware_heartbeat_contract(request: HardwareNodeHeartbeat) -> List[str]:
    reasons: List[str] = []

    allowed_statuses = {
        str(value).strip().lower()
        for value in FIRMWARE_CONTRACT.get("status_values", [])
        if str(value).strip()
    }
    status = str(request.status or "").strip().lower()
    if not status:
        reasons.append("status is required and cannot be empty")
    elif allowed_statuses and status not in allowed_statuses:
        reasons.append(
            "status must be one of: " + ", ".join(sorted(allowed_statuses))
        )

    if request.uptime_seconds is not None and request.uptime_seconds < 0:
        reasons.append("uptime_seconds must be >= 0")
    if request.temperature_c is not None and not (-80 <= request.temperature_c <= 180):
        reasons.append("temperature_c must be between -80 and 180")
    if request.power_watts is not None and request.power_watts < 0:
        reasons.append("power_watts must be >= 0")
    if request.latency_ms is not None and request.latency_ms < 0:
        reasons.append("latency_ms must be >= 0")

    if len(request.telemetry) > 64:
        reasons.append("telemetry contains too many keys; max allowed is 64")

    node_id_lower = str(request.node_id or "").strip().lower()
    if LIVE_ONLY_MODE and any(node_id_lower.startswith(prefix) for prefix in NON_LIVE_NODE_ID_PREFIXES):
        reasons.append("node_id prefix is reserved for non-live or test nodes in live-only mode")

    telemetry_source = str(request.telemetry.get("source") or "").strip().lower()
    if LIVE_ONLY_MODE and telemetry_source in NON_LIVE_SOURCES:
        reasons.append("telemetry source indicates non-live data and is blocked in live-only mode")

    return reasons


def _derive_node_symbol(rank: Any) -> str:
    mapping = {
        "root": "🌍",
        "ministry": "🏛️",
        "command": "🏆",
        "division": "⚔️",
        "brigade": "🏰",
        "battalion": "🏛️",
        "company": "🏅",
        "platoon": "🎖️",
        "soldier": "🪖",
    }
    return mapping.get(str(rank or "").lower(), "🔹")


def _rank_weight(rank: Any) -> int:
    return HIERARCHY_RANK_ORDER.get(str(rank or "").lower(), 999)


def _child_node_ids(node_id: str) -> List[str]:
    children = [
        candidate_id
        for candidate_id, candidate in HARDWARE_NODES.items()
        if str(candidate.get("parent_node_id") or "").strip() == node_id
    ]
    return sorted(children, key=lambda candidate_id: (_rank_weight(HARDWARE_NODES[candidate_id].get("rank")), candidate_id))


def _lineage_for(node_id: str) -> List[str]:
    lineage: List[str] = []
    visited: set[str] = set()
    current = HARDWARE_NODES.get(node_id)
    while current:
        current_id = str(current.get("node_id") or "")
        if not current_id or current_id in visited:
            break
        lineage.append(current_id)
        visited.add(current_id)
        parent_id = str(current.get("parent_node_id") or "").strip()
        current = HARDWARE_NODES.get(parent_id) if parent_id else None
    return list(reversed(lineage))


def _hierarchy_depth(node_id: str) -> int:
    return max(len(_lineage_for(node_id)) - 1, 0)


def _descendant_node_ids(node_id: str, max_depth: int = 12) -> List[str]:
    descendants: List[str] = []
    queue: List[tuple[str, int]] = [(node_id, 0)]
    seen = {node_id}
    while queue:
        current_id, depth = queue.pop(0)
        if depth >= max_depth:
            continue
        for child_id in _child_node_ids(current_id):
            if child_id in seen:
                continue
            descendants.append(child_id)
            seen.add(child_id)
            queue.append((child_id, depth + 1))
    return descendants


def _path_between_nodes(source_node_id: str, target_node_id: str) -> List[str]:
    if source_node_id == target_node_id:
        return [source_node_id]
    source_lineage = _lineage_for(source_node_id)
    target_lineage = _lineage_for(target_node_id)
    if not source_lineage or not target_lineage:
        return []

    shared_index = -1
    for index, (left, right) in enumerate(zip(source_lineage, target_lineage)):
        if left != right:
            break
        shared_index = index

    upward = list(reversed(source_lineage[shared_index + 1 :]))
    shared_root = [source_lineage[shared_index]] if shared_index >= 0 else []
    downward = target_lineage[shared_index + 1 :]
    return upward + shared_root + downward


def _build_hierarchy_tree() -> List[Dict[str, Any]]:
    roots = [
        node_id
        for node_id, node in HARDWARE_NODES.items()
        if not str(node.get("parent_node_id") or "").strip() or str(node.get("parent_node_id") or "").strip() not in HARDWARE_NODES
    ]
    roots = sorted(set(roots), key=lambda node_id: (_rank_weight(HARDWARE_NODES[node_id].get("rank")), node_id))

    def build_branch(node_id: str) -> Dict[str, Any]:
        node = _enrich_hardware_node(HARDWARE_NODES[node_id])
        return {
            "node_id": node.get("node_id"),
            "display_name": node.get("display_name"),
            "rank": node.get("rank"),
            "symbol": node.get("symbol"),
            "runtime_state": node.get("runtime_state"),
            "children": [build_branch(child_id) for child_id in _child_node_ids(node_id)],
        }

    return [build_branch(root_id) for root_id in roots]


def _node_runtime_state(node: Dict[str, Any]) -> tuple[str, Optional[float]]:
    raw_status = str(node.get("status", "registered") or "registered").lower()
    last_seen = _parse_iso_timestamp(node.get("last_seen_at"))
    now = datetime.now(timezone.utc)
    age_seconds: Optional[float] = None
    if last_seen is not None:
        age_seconds = max((now - last_seen).total_seconds(), 0.0)
        age_seconds = round(age_seconds, 2)

    sleep_until = _parse_iso_timestamp(node.get("sleep_until"))
    if sleep_until is not None and sleep_until > now:
        return "sleeping", age_seconds

    pause_until = _parse_iso_timestamp(node.get("pause_until"))
    if pause_until is not None and pause_until > now:
        return "paused", age_seconds

    if raw_status == "maintenance":
        return "maintenance", age_seconds
    if raw_status == "offline":
        return "offline", age_seconds
    if last_seen is None:
        return ("registered" if raw_status == "registered" else raw_status), age_seconds
    if age_seconds is not None and age_seconds <= KLOUD_NODE_HEARTBEAT_TTL_SECONDS:
        if raw_status in {"registered", "degraded"}:
            return raw_status, age_seconds
        return "online", age_seconds
    if age_seconds is not None and age_seconds <= KLOUD_NODE_OFFLINE_GRACE_SECONDS:
        return "stale", age_seconds
    return "offline", age_seconds


def _enrich_hardware_node(node: Dict[str, Any]) -> Dict[str, Any]:
    enriched = dict(node)
    node_id = str(node.get("node_id") or "")
    runtime_state, heartbeat_age_seconds = _node_runtime_state(node)
    mesh_role = str(
        node.get("mesh_role")
        or node.get("metadata", {}).get("mesh_role")
        or ("coordinator" if node.get("metadata", {}).get("coordinator") else "worker")
    )
    rank = str(node.get("rank") or node.get("metadata", {}).get("rank") or "soldier").lower()
    children_ids = _child_node_ids(node_id) if node_id else []
    lineage = _lineage_for(node_id) if node_id else []
    enriched["display_name"] = node.get("display_name") or node_id
    enriched["rank"] = rank
    enriched["symbol"] = node.get("symbol") or _derive_node_symbol(rank)
    enriched["runtime_state"] = runtime_state
    enriched["heartbeat_age_seconds"] = heartbeat_age_seconds
    enriched["heartbeat_ttl_seconds"] = KLOUD_NODE_HEARTBEAT_TTL_SECONDS
    enriched["offline_grace_seconds"] = KLOUD_NODE_OFFLINE_GRACE_SECONDS
    enriched["mesh_role"] = mesh_role
    enriched["pulse_count"] = int(node.get("pulse_count", 0) or 0)
    enriched["last_pulse_at"] = node.get("last_pulse_at")
    enriched["last_ping_at"] = node.get("last_ping_at")
    enriched["last_pong_at"] = node.get("last_pong_at")
    enriched["parent_node_id"] = node.get("parent_node_id")
    enriched["children_ids"] = children_ids
    enriched["lineage"] = lineage
    enriched["depth"] = max(len(lineage) - 1, 0)
    enriched["sleep_capable"] = bool(node.get("sleep_capable", True))
    enriched["pause_until"] = node.get("pause_until")
    enriched["sleep_until"] = node.get("sleep_until")
    enriched["can_accept_commands"] = runtime_state not in {"offline", "sleeping", "maintenance"}
    return enriched


def _hardware_summary() -> Dict[str, Any]:
    nodes = [_enrich_hardware_node(node) for node in HARDWARE_NODES.values()]
    online = sum(1 for node in nodes if node.get("runtime_state") == "online")
    stale = sum(1 for node in nodes if node.get("runtime_state") == "stale")
    degraded = sum(1 for node in nodes if node.get("runtime_state") == "degraded")
    paused = sum(1 for node in nodes if node.get("runtime_state") == "paused")
    sleeping = sum(1 for node in nodes if node.get("runtime_state") == "sleeping")
    offline = sum(1 for node in nodes if node.get("runtime_state") in {"offline", "registered", "maintenance"})
    seen_values = [str(node["last_seen_at"]) for node in nodes if node.get("last_seen_at")]
    last_seen = max(seen_values) if seen_values else None
    latency_values = [float(node["latency_ms"]) for node in nodes if node.get("latency_ms") is not None]
    last_latency = latency_values[-1] if latency_values else None
    total_pulses = sum(int(node.get("pulse_count", 0) or 0) for node in nodes)
    root_nodes = sum(1 for node in nodes if not node.get("parent_node_id"))
    leaf_nodes = sum(1 for node in nodes if not node.get("children_ids"))
    max_depth = max((int(node.get("depth", 0) or 0) for node in nodes), default=0)

    coordinator_node_id = next(
        (
            str(node.get("node_id"))
            for node in nodes
            if node.get("mesh_role") == "coordinator" or node.get("metadata", {}).get("coordinator")
        ),
        None,
    )
    if coordinator_node_id is None:
        coordinator_node_id = next(
            (str(node.get("node_id")) for node in nodes if node.get("runtime_state") in {"online", "degraded", "stale", "paused"}),
            None,
        )

    if not nodes:
        network_health = "no-nodes"
    elif online == len(nodes) and stale == 0 and paused == 0 and sleeping == 0 and (last_latency is None or last_latency <= 25):
        network_health = "healthy"
    elif online > 0 or stale > 0 or degraded > 0 or paused > 0 or sleeping > 0:
        network_health = "degraded"
    else:
        network_health = "offline"

    return {
        "phase": HARDWARE_PROFILE["phase"],
        "chip_ready": HARDWARE_PROFILE["chip_ready"],
        "registered_nodes": len(nodes),
        "online_nodes": online,
        "stale_nodes": stale,
        "degraded_nodes": degraded,
        "paused_nodes": paused,
        "sleeping_nodes": sleeping,
        "offline_nodes": offline,
        "root_nodes": root_nodes,
        "leaf_nodes": leaf_nodes,
        "max_depth": max_depth,
        "hierarchy_enabled": True,
        "last_seen_at": last_seen,
        "last_heartbeat_latency_ms": last_latency,
        "network_health": network_health,
        "cluster_mode": "multinode" if len(nodes) > 1 else ("single-node" if nodes else "empty"),
        "coordinator_node_id": coordinator_node_id,
        "proof_of_life": "active" if online > 0 or stale > 0 or total_pulses > 0 else "pending",
        "total_pulses": total_pulses,
        "heartbeat_ttl_seconds": KLOUD_NODE_HEARTBEAT_TTL_SECONDS,
        "offline_grace_seconds": KLOUD_NODE_OFFLINE_GRACE_SECONDS,
        "contract_conformance": _heartbeat_conformance_summary(limit_nodes=5),
        "registry_backend": "json-file",
        "registry_persistent": True,
        "target_architecture": HARDWARE_PROFILE["target_architecture"],
        "runtime": HARDWARE_PROFILE["runtime"],
    }


def _record_signal_activity(source: str, route: str, payload: Dict[str, Any], upstream_url: str) -> None:
    global _LAST_SIGNAL_ACTIVITY
    _LAST_SIGNAL_ACTIVITY = {
        "timestamp": _now_iso(),
        "source": source,
        "route": route,
        "upstream_url": upstream_url,
        "payload_keys": sorted(list(payload.keys()))[:10],
    }


def _build_truth_contract(upstream: Dict[str, Any], ocean: Dict[str, Any], peer_count: int) -> Dict[str, Any]:
    hardware = _hardware_summary()
    upstream_reachable = bool(upstream.get("reachable"))
    ocean_reachable = bool(ocean.get("reachable"))

    if upstream_reachable and ocean_reachable:
        state = "ready"
        connectivity = "connected"
        sync_status = "synchronized"
        confidence = "verified"
        estimated_recovery = None
    elif upstream_reachable:
        state = "partial-sync"
        connectivity = "connected"
        sync_status = "partial"
        confidence = "partial"
        estimated_recovery = "Ocean visibility is still limited; bridge sync is already active."
    elif upstream.get("configured") and _LAST_SUCCESSFUL_SYNC_AT:
        state = "recovering"
        connectivity = "limited"
        sync_status = "waiting"
        confidence = "partial"
        estimated_recovery = "Retry synchronization when the sovereign upstream responds again."
    elif upstream.get("configured"):
        state = "degraded"
        connectivity = "limited"
        sync_status = "waiting"
        confidence = "verified"
        estimated_recovery = (
            "Ocean is reachable, but the sovereign upstream must respond before synchronization can complete."
            if ocean_reachable
            else "The sovereign upstream must respond before synchronization can complete."
        )
    else:
        state = "setup-required"
        connectivity = "not-configured"
        sync_status = "not-configured"
        confidence = "unknown"
        estimated_recovery = "Set KLOUD_UPSTREAM_URL or KLOUD_UPSTREAM_CANDIDATES."

    live_flow = {
        "synchronized": "Bridge → Sovereign upstream → Ready",
        "partial": "Bridge → Sovereign upstream → Partial sync",
        "waiting": "Bridge → Sovereign upstream → Sync waiting",
        "not-configured": "Bridge → Sovereign upstream → Setup required",
    }.get(sync_status, "Bridge → Sovereign upstream → Review")

    return {
        "state": state,
        "connectivity": connectivity,
        "sync_status": sync_status,
        "confidence": confidence,
        "last_successful_sync": _LAST_SUCCESSFUL_SYNC_AT,
        "estimated_recovery": estimated_recovery,
        "peer_count": peer_count,
        "proof_of_life": "active" if hardware["online_nodes"] > 0 or hardware.get("stale_nodes", 0) > 0 or _LAST_SIGNAL_ACTIVITY else "pending",
        "last_signal": _LAST_SIGNAL_ACTIVITY or None,
        "last_upstream_error": _LAST_UPSTREAM_ERROR or None,
        "live_flow": live_flow,
        "hardware_network_health": hardware["network_health"],
    }


def _build_bridge_summary(upstream: Dict[str, Any], ocean: Dict[str, Any]) -> Dict[str, Any]:
    """Create a concise, UI-friendly summary of live bridge health."""
    upstream_status = "live" if upstream.get("reachable") else ("configured" if upstream.get("configured") else "setup-required")
    ocean_status = "live" if ocean.get("reachable") else ("configured" if ocean.get("configured") else "setup-required")
    upstream_payload = upstream.get("status", {}) if isinstance(upstream.get("status"), dict) else {}

    peer_count = 0
    for candidate_key in ("peers", "nodes", "neighbors"):
        candidate_value = upstream_payload.get(candidate_key)
        if isinstance(candidate_value, list):
            peer_count = len(candidate_value)
            break

    truth = _build_truth_contract(upstream, ocean, peer_count)

    return {
        "bridge": "live" if upstream.get("reachable") or ocean.get("reachable") else "degraded",
        "upstream_status": upstream_status,
        "ocean_status": ocean_status,
        "peer_count": peer_count,
        "upstream_target": upstream.get("url"),
        "ocean_target": ocean.get("url"),
        "hardware_nodes": _hardware_summary(),
        "service_truth": truth,
        "state": truth["state"],
        "connectivity": truth["connectivity"],
        "sync_status": truth["sync_status"],
        "confidence": truth["confidence"],
        "last_successful_sync": truth["last_successful_sync"],
        "estimated_recovery": truth["estimated_recovery"],
    }


def _build_user_facing_status(upstream: Dict[str, Any], ocean: Dict[str, Any], summary: Dict[str, Any]) -> Dict[str, Any]:
    upstream_reachable = bool(upstream.get("reachable"))
    ocean_reachable = bool(ocean.get("reachable"))

    if upstream_reachable and ocean_reachable:
        return {
            "state": "ready",
            "severity": "info",
            "message": "Connected and synchronized.",
            "action": None,
        }

    if upstream_reachable and not ocean_reachable:
        return {
            "state": "partial-outage",
            "severity": "warning",
            "message": "Sovereign upstream is reachable, but Ocean Core visibility is limited.",
            "action": "Check ocean-core service health and bridge route to OCEAN_STATUS_PATH.",
        }

    if not upstream_reachable and ocean_reachable:
        return {
            "state": "partial-outage",
            "severity": "warning",
            "message": "Ocean Core is reachable, but sovereign upstream synchronization is waiting.",
            "action": "Verify KLOUD_UPSTREAM_URL and sovereign fabric runtime availability.",
        }

    if upstream.get("configured") or ocean.get("configured"):
        return {
            "state": "degraded",
            "severity": "error",
            "message": "Bridge dependencies are configured but currently unavailable.",
            "action": summary.get("estimated_recovery") or "Inspect /admin/diagnostics for dependency-level errors.",
        }

    return {
        "state": "setup-required",
        "severity": "warning",
        "message": "Bridge dependencies are not configured.",
        "action": "Set KLOUD_UPSTREAM_URL and OCEAN_CORE_URL.",
    }


def _build_failure_mode_report(upstream: Dict[str, Any], ocean: Dict[str, Any]) -> Dict[str, Any]:
    dependency_state = {
        "upstream": {
            "configured": bool(upstream.get("configured")),
            "reachable": bool(upstream.get("reachable")),
        },
        "ocean": {
            "configured": bool(ocean.get("configured")),
            "reachable": bool(ocean.get("reachable")),
        },
        "admin_token": {
            "configured": bool(KLOUD_BRIDGE_ADMIN_TOKEN),
            "reachable": True,
        },
        "firmware_contract": {
            "configured": True,
            "reachable": True,
        },
        "node_registration": {
            "configured": True,
            "reachable": True,
        },
        "local": {
            "configured": True,
            "reachable": True,
        },
    }

    endpoints: List[Dict[str, Any]] = []
    for endpoint, policy in FAILURE_MODE_MATRIX.items():
        deps = policy.get("dependencies", [])
        blocked = False
        if policy.get("mode") == "fail-closed":
            for dep in deps:
                state = dependency_state.get(dep, {"configured": False, "reachable": False})
                if not state.get("configured") or not state.get("reachable"):
                    blocked = True
                    break

        endpoints.append(
            {
                "endpoint": endpoint,
                "mode": policy.get("mode"),
                "dependencies": deps,
                "blocked": blocked,
                "on_failure": policy.get("on_failure"),
                "user_status_on_failure": policy.get("user_status_on_failure"),
            }
        )

    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "dependency_state": dependency_state,
        "matrix": endpoints,
    }


@app.get("/status")
@app.get(f"{API_PREFIX}/status")
async def status() -> Dict[str, Any]:
    upstream = await _probe_upstream()
    ocean = await _probe_ocean()
    availability = "connected" if upstream.get("reachable") else ("limited" if upstream.get("configured") else "setup-required")
    summary = _build_bridge_summary(upstream, ocean)
    user_facing_status = _build_user_facing_status(upstream, ocean, summary)
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "instance": INSTANCE_ID,
        "isolated": KLOUD_ISOLATED_MODE,
        "live_only": LIVE_ONLY_MODE,
        "mode": BRIDGE_MODE,
        "enforcement": ENFORCEMENT_MODE,
        "port": PORT,
        "availability": availability,
        "user_facing_status": user_facing_status,
        "summary": summary,
        "service_truth": summary.get("service_truth", {}),
        "security": _security_summary(),
        "audit": _audit_summary(),
        "openapi_snapshot": _openapi_summary(),
        "upstream": upstream,
        "ocean_core": ocean,
        "hardware": {
            "profile": HARDWARE_PROFILE,
            "summary": _hardware_summary(),
        },
    }


@app.get("/failure-modes")
@app.get(f"{API_PREFIX}/failure-modes")
async def failure_modes() -> Dict[str, Any]:
    upstream = await _probe_upstream()
    ocean = await _probe_ocean()
    summary = _build_bridge_summary(upstream, ocean)
    report = _build_failure_mode_report(upstream, ocean)
    report["user_facing_status"] = _build_user_facing_status(upstream, ocean, summary)
    return report


@app.get("/fabric/summary")
@app.get("/fabric/state")
@app.get(f"{API_PREFIX}/fabric/summary")
@app.get(f"{API_PREFIX}/fabric/state")
async def fabric_summary() -> Dict[str, Any]:
    upstream = await _probe_upstream()
    ocean = await _probe_ocean()
    return _build_bridge_summary(upstream, ocean)


@app.get("/ocean/status")
@app.get(f"{API_PREFIX}/ocean/status")
async def ocean_status() -> Dict[str, Any]:
    return await _probe_ocean()


@app.get("/hardware/profile")
@app.get(f"{API_PREFIX}/hardware/profile")
def hardware_profile() -> Dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "profile": HARDWARE_PROFILE,
        "summary": _hardware_summary(),
        "firmware_contract": FIRMWARE_CONTRACT,
        "contracts": {
            "register": "POST /hardware/nodes/register",
            "heartbeat": "POST /hardware/nodes/heartbeat",
            "pulse": "POST /hardware/nodes/pulse",
            "mesh_status": "GET /hardware/mesh/status",
            "mesh_ping": "POST /hardware/mesh/ping",
            "hierarchy": "GET /hardware/hierarchy",
            "hierarchy_blueprint": "GET /hardware/hierarchy/blueprint",
            "hierarchy_dispatch": "POST /hardware/hierarchy/dispatch",
            "node_control": "POST /hardware/nodes/control",
            "nodes": "GET /hardware/nodes",
            "node_detail": "GET /hardware/nodes/{node_id}",
        },
    }


@app.get("/hardware/contracts/firmware-v0.1")
@app.get(f"{API_PREFIX}/hardware/contracts/firmware-v0.1")
def hardware_firmware_contract() -> Dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "hardware_profile": HARDWARE_PROFILE,
        "hierarchy_blueprint": HIERARCHY_BLUEPRINT,
        "contract": FIRMWARE_CONTRACT,
    }


@app.get("/hardware/hierarchy/blueprint")
@app.get(f"{API_PREFIX}/hardware/hierarchy/blueprint")
def hardware_hierarchy_blueprint() -> Dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "hierarchy": HIERARCHY_BLUEPRINT,
        "summary": _hardware_summary(),
    }


@app.get("/hardware/hierarchy")
@app.get(f"{API_PREFIX}/hardware/hierarchy")
def hardware_hierarchy() -> Dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "summary": _hardware_summary(),
        "hierarchy": {
            "blueprint": HIERARCHY_BLUEPRINT,
            "tree": _build_hierarchy_tree(),
        },
    }


@app.get("/contracts/openapi-v1")
@app.get(f"{API_PREFIX}/contracts/openapi-v1")
def openapi_contract_snapshot() -> Dict[str, Any]:
    _export_openapi_snapshot()
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "snapshot": _openapi_summary(),
        "document": app.openapi(),
    }


@app.get("/hardware/nodes")
@app.get(f"{API_PREFIX}/hardware/nodes")
def list_hardware_nodes() -> Dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "summary": _hardware_summary(),
        "registry": _registry_summary(),
        "nodes": [_enrich_hardware_node(node) for node in HARDWARE_NODES.values()],
    }


@app.get("/hardware/registry")
@app.get(f"{API_PREFIX}/hardware/registry")
def hardware_registry() -> Dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "registry": _registry_summary(),
        "summary": _hardware_summary(),
        "node_ids": sorted(HARDWARE_NODES.keys()),
    }


@app.get("/hardware/nodes/{node_id}")
@app.get(f"{API_PREFIX}/hardware/nodes/{{node_id}}")
def get_hardware_node(node_id: str) -> Dict[str, Any]:
    node = HARDWARE_NODES.get(node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Hardware node was not found.")
    return {
        "service": SERVICE_NAME,
        "node": _enrich_hardware_node(node),
        "contract_version": FIRMWARE_CONTRACT["version"],
    }


@app.post("/hardware/nodes/register")
@app.post(f"{API_PREFIX}/hardware/nodes/register")
def register_hardware_node(
    request: HardwareNodeRegistration,
    x_node_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_node_access(x_node_token, authorization)
    now = _now_iso()
    existing = HARDWARE_NODES.get(request.node_id, {})
    created = not bool(existing)

    metadata = request.metadata if isinstance(request.metadata, dict) else {}
    parent_node_id = str(request.parent_node_id or existing.get("parent_node_id") or "").strip() or None
    if parent_node_id and parent_node_id not in HARDWARE_NODES:
        raise HTTPException(status_code=404, detail="Parent node must be registered before child nodes can bind to the hierarchy.")

    rank = str(metadata.get("rank") or request.rank or existing.get("rank") or "soldier").lower()
    node = {
        **existing,
        "node_id": request.node_id,
        "display_name": request.display_name or existing.get("display_name") or request.node_id,
        "node_class": request.node_class,
        "architecture": request.architecture,
        "runtime": request.runtime,
        "transport": request.transport,
        "firmware_version": request.firmware_version,
        "capabilities": request.capabilities,
        "metadata": metadata,
        "status": existing.get("status", "registered"),
        "binding_state": "bound",
        "entity_managed": True,
        "rank": rank,
        "symbol": request.symbol or existing.get("symbol") or _derive_node_symbol(rank),
        "parent_node_id": parent_node_id,
        "sleep_capable": bool(request.sleep_capable),
        "configured_pause_seconds": request.pause_seconds,
        "pause_until": existing.get("pause_until"),
        "sleep_until": existing.get("sleep_until"),
        "mesh_role": existing.get("mesh_role") or metadata.get("mesh_role") or ("coordinator" if metadata.get("coordinator") else "worker"),
        "pulse_count": int(existing.get("pulse_count", 0) or 0),
        "last_pulse_at": existing.get("last_pulse_at"),
        "last_ping_at": existing.get("last_ping_at"),
        "last_pong_at": existing.get("last_pong_at"),
        "last_command_at": existing.get("last_command_at"),
        "last_command_message": existing.get("last_command_message"),
        "first_seen_at": existing.get("first_seen_at", now),
        "last_registration_at": now,
        "last_seen_at": now,
    }
    HARDWARE_NODES[request.node_id] = node
    _persist_hardware_nodes()
    _append_audit_event(
        "node.register",
        "registered" if created else "updated",
        f"Hardware node {request.node_id} bound to the persistent registry.",
        actor=request.node_id,
        metadata={
            "architecture": request.architecture,
            "runtime": request.runtime,
            "capabilities": request.capabilities,
        },
    )

    return {
        "status": "registered" if created else "updated",
        "live_only": LIVE_ONLY_MODE,
        "contract_version": FIRMWARE_CONTRACT["version"],
        "binding_state": "bound",
        "node": _enrich_hardware_node(node),
        "summary": _hardware_summary(),
        "registry": _registry_summary(),
    }


@app.post("/hardware/nodes/heartbeat")
@app.post(f"{API_PREFIX}/hardware/nodes/heartbeat")
async def hardware_node_heartbeat(
    request: HardwareNodeHeartbeat,
    x_node_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_node_access(x_node_token, authorization)
    contract_reasons = _validate_hardware_heartbeat_contract(request)
    if contract_reasons:
        _record_heartbeat_conformance(request.node_id, passed=False, reasons=contract_reasons)
        _append_audit_event(
            "node.heartbeat",
            "contract-rejected",
            f"Heartbeat payload rejected for node {request.node_id} due to firmware contract validation errors.",
            actor=request.node_id,
            metadata={"reasons": contract_reasons[:10]},
        )
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Heartbeat payload violates firmware contract.",
                "reasons": contract_reasons,
            },
        )

    _record_heartbeat_conformance(request.node_id, passed=True)
    node = HARDWARE_NODES.get(request.node_id)
    if not node:
        _append_audit_event(
            "node.heartbeat",
            "rejected",
            f"Heartbeat rejected because node {request.node_id} is not registered.",
            actor=request.node_id,
        )
        raise HTTPException(status_code=404, detail="Hardware node is not registered. Call /hardware/nodes/register first.")

    merged_telemetry = {**node.get("telemetry", {}), **request.telemetry}
    node.update(
        {
            "status": request.status,
            "binding_state": "bound",
            "entity_managed": True,
            "uptime_seconds": request.uptime_seconds,
            "temperature_c": request.temperature_c,
            "power_watts": request.power_watts,
            "latency_ms": request.latency_ms,
            "telemetry": merged_telemetry,
            "last_seen_at": _now_iso(),
        }
    )
    _persist_hardware_nodes()
    _append_audit_event(
        "node.heartbeat",
        "accepted",
        f"Heartbeat recorded for node {request.node_id}.",
        actor=request.node_id,
        metadata={
            "status": request.status,
            "latency_ms": request.latency_ms,
            "forward_to_ocean": request.forward_to_ocean,
        },
    )

    forward_result = {"attempted": False, "forwarded": False}
    if request.forward_to_ocean:
        forward_result = await _forward_hardware_heartbeat_to_ocean(node)

    return {
        "status": "heartbeat-recorded",
        "binding_state": "bound",
        "node": _enrich_hardware_node(node),
        "ocean_forward": forward_result,
        "summary": _hardware_summary(),
        "registry": _registry_summary(),
    }


@app.post("/hardware/nodes/control")
@app.post(f"{API_PREFIX}/hardware/nodes/control")
def hardware_node_control(
    request: NodeControlRequest,
    x_node_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_node_access(x_node_token, authorization)
    node = HARDWARE_NODES.get(request.node_id)
    if not node:
        raise HTTPException(status_code=404, detail="Hardware node was not found.")

    action = str(request.action or "pause").lower()
    now_dt = datetime.now(timezone.utc)
    duration_seconds = float(request.duration_seconds or 0)

    if action == "pause":
        node["pause_until"] = (now_dt + timedelta(seconds=duration_seconds)).isoformat() if duration_seconds > 0 else now_dt.isoformat()
        node["status"] = "degraded"
    elif action == "sleep":
        if not bool(node.get("sleep_capable", True)):
            raise HTTPException(status_code=400, detail="This node is not marked as sleep-capable.")
        node["sleep_until"] = (now_dt + timedelta(seconds=duration_seconds)).isoformat() if duration_seconds > 0 else now_dt.isoformat()
        node["status"] = "maintenance"
    elif action in {"resume", "wake", "activate"}:
        node["pause_until"] = None
        node["sleep_until"] = None
        node["status"] = "online"
    else:
        raise HTTPException(status_code=400, detail="Unsupported control action. Use pause, sleep, resume, wake, or activate.")

    node["last_command_at"] = now_dt.isoformat()
    node["last_command_message"] = f"control:{action}"
    node["last_seen_at"] = now_dt.isoformat()
    _persist_hardware_nodes()
    _append_audit_event(
        "node.control",
        action,
        f"Node {request.node_id} control action applied.",
        actor=request.node_id,
        metadata={"duration_seconds": duration_seconds, "reason": request.reason},
    )

    return {
        "status": "control-applied",
        "action": action,
        "node": _enrich_hardware_node(node),
        "summary": _hardware_summary(),
    }


@app.post("/hardware/hierarchy/dispatch")
@app.post(f"{API_PREFIX}/hardware/hierarchy/dispatch")
def hardware_hierarchy_dispatch(
    request: HierarchyCommandRequest,
    x_node_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_node_access(x_node_token, authorization)
    source = HARDWARE_NODES.get(request.source_node_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source node must be registered before hierarchy dispatch.")

    direction = str(request.direction or "downstream").lower()
    route_ids: List[str]
    if request.target_node_id:
        if request.target_node_id not in HARDWARE_NODES:
            raise HTTPException(status_code=404, detail="Target node must be registered before hierarchy dispatch.")
        route_ids = _path_between_nodes(request.source_node_id, request.target_node_id)
    elif direction == "upstream":
        route_ids = list(reversed(_lineage_for(request.source_node_id)))
    else:
        route_ids = [request.source_node_id] + _descendant_node_ids(request.source_node_id, max_depth=request.max_depth)

    if not route_ids:
        raise HTTPException(status_code=400, detail="No hierarchy route could be resolved for this dispatch.")

    delivered_nodes: List[Dict[str, Any]] = []
    delivered_at = _now_iso()
    for index, node_id in enumerate(route_ids):
        node = HARDWARE_NODES.get(node_id)
        if not node:
            continue
        node.setdefault("telemetry", {})
        node["telemetry"]["last_hierarchy_message"] = request.message
        node["telemetry"]["last_hierarchy_direction"] = direction
        node["telemetry"]["last_hierarchy_hop"] = index
        node["last_command_at"] = delivered_at
        node["last_command_message"] = request.message
        if index > 0 and request.pause_ms > 0:
            time.sleep(min(request.pause_ms, 250) / 1000.0)
        delivered_nodes.append(_enrich_hardware_node(node))

    _persist_hardware_nodes()
    _append_audit_event(
        "hierarchy.dispatch",
        "delivered",
        f"Hierarchy command routed from {request.source_node_id} across {len(delivered_nodes)} node(s).",
        actor=request.source_node_id,
        metadata={
            "target_node_id": request.target_node_id,
            "direction": direction,
            "pause_ms": request.pause_ms,
            "max_depth": request.max_depth,
        },
    )

    return {
        "status": "command-delivered",
        "direction": direction,
        "source_node_id": request.source_node_id,
        "target_node_id": request.target_node_id,
        "delivered_count": len(delivered_nodes),
        "pause_ms": request.pause_ms,
        "route": delivered_nodes,
        "summary": _hardware_summary(),
    }


@app.post("/hardware/nodes/pulse")
@app.post(f"{API_PREFIX}/hardware/nodes/pulse")
def hardware_node_pulse(
    request: HardwareNodePulse,
    x_node_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_node_access(x_node_token, authorization)
    node = HARDWARE_NODES.get(request.node_id)
    if not node:
        _append_audit_event(
            "node.pulse",
            "rejected",
            f"Pulse rejected because node {request.node_id} is not registered.",
            actor=request.node_id,
        )
        raise HTTPException(status_code=404, detail="Hardware node is not registered. Call /hardware/nodes/register first.")

    now = _now_iso()
    node.setdefault("telemetry", {})
    node["telemetry"] = {**node.get("telemetry", {}), **request.telemetry}
    if request.queue_depth is not None:
        node["telemetry"]["queue_depth"] = request.queue_depth
    node.update(
        {
            "status": "online" if str(node.get("status", "")).lower() != "maintenance" else "maintenance",
            "last_seen_at": now,
            "last_pulse_at": now,
            "latency_ms": request.latency_ms if request.latency_ms is not None else node.get("latency_ms"),
            "pulse_count": int(node.get("pulse_count", 0) or 0) + 1,
        }
    )
    _persist_hardware_nodes()
    _append_audit_event(
        "node.pulse",
        "accepted",
        f"Pulse recorded for node {request.node_id}.",
        actor=request.node_id,
        metadata={
            "signal": request.signal,
            "queue_depth": request.queue_depth,
            "latency_ms": request.latency_ms,
        },
    )

    return {
        "status": "pulse-recorded",
        "signal": request.signal,
        "node": _enrich_hardware_node(node),
        "summary": _hardware_summary(),
        "registry": _registry_summary(),
    }


@app.get("/hardware/mesh/status")
@app.get(f"{API_PREFIX}/hardware/mesh/status")
def hardware_mesh_status() -> Dict[str, Any]:
    summary = _hardware_summary()
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "mesh": {
            "mode": summary.get("cluster_mode"),
            "coordinator_node_id": summary.get("coordinator_node_id"),
            "heartbeat_ttl_seconds": KLOUD_NODE_HEARTBEAT_TTL_SECONDS,
            "offline_grace_seconds": KLOUD_NODE_OFFLINE_GRACE_SECONDS,
        },
        "summary": summary,
        "nodes": [_enrich_hardware_node(node) for node in HARDWARE_NODES.values()],
    }


@app.post("/hardware/mesh/ping")
@app.post(f"{API_PREFIX}/hardware/mesh/ping")
def hardware_mesh_ping(
    request: MeshPingRequest,
    x_node_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_node_access(x_node_token, authorization)
    source = HARDWARE_NODES.get(request.source_node_id)
    target = HARDWARE_NODES.get(request.target_node_id)
    if not source or not target:
        missing = request.source_node_id if not source else request.target_node_id
        _append_audit_event(
            "mesh.ping",
            "rejected",
            f"Mesh ping rejected because node {missing} is not registered.",
            actor=request.source_node_id,
            metadata={"target_node_id": request.target_node_id},
        )
        raise HTTPException(status_code=404, detail="Both source and target nodes must be registered before ping-pong mesh checks.")

    now = _now_iso()
    roundtrip_ms = min(max(int(request.ttl_ms / 3), 1), request.ttl_ms)
    source.update({
        "last_seen_at": now,
        "last_ping_at": now,
        "status": "online" if str(source.get("status", "")).lower() != "maintenance" else "maintenance",
    })
    target.update({
        "last_seen_at": now,
        "last_pong_at": now,
        "status": "online" if str(target.get("status", "")).lower() != "maintenance" else "maintenance",
    })
    source.setdefault("telemetry", {})
    target.setdefault("telemetry", {})
    source["telemetry"]["last_mesh_target"] = request.target_node_id
    target["telemetry"]["last_mesh_source"] = request.source_node_id
    _persist_hardware_nodes()
    _append_audit_event(
        "mesh.ping",
        "pong",
        f"Mesh ping {request.source_node_id} → {request.target_node_id} acknowledged.",
        actor=request.source_node_id,
        metadata={
            "target_node_id": request.target_node_id,
            "roundtrip_ms": roundtrip_ms,
            "ttl_ms": request.ttl_ms,
            "payload_keys": sorted(list(request.payload.keys()))[:10],
        },
    )

    return {
        "status": "pong",
        "signal": request.signal,
        "source_node_id": request.source_node_id,
        "target_node_id": request.target_node_id,
        "roundtrip_ms": roundtrip_ms,
        "mesh_state": "linked",
        "source": _enrich_hardware_node(source),
        "target": _enrich_hardware_node(target),
        "summary": _hardware_summary(),
    }


@app.get("/admin/diagnostics")
@app.get(f"{API_PREFIX}/admin/diagnostics")
async def admin_diagnostics(
    x_admin_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_admin_access(x_admin_token, authorization)
    upstream = await _probe_upstream()
    ocean = await _probe_ocean()
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "instance": INSTANCE_ID,
        "isolated": KLOUD_ISOLATED_MODE,
        "live_only": LIVE_ONLY_MODE,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "timeout_seconds": KLOUD_TIMEOUT_SECONDS,
        "candidates": _ordered_upstream_candidates(),
        "selected_upstream": upstream.get("url"),
        "paths": {
            "status": KLOUD_STATUS_PATH,
            "peers": KLOUD_PEERS_PATH,
            "state": KLOUD_STATE_PATH,
            "signal": KLOUD_SIGNAL_PATH,
            "ocean_status": OCEAN_STATUS_PATH,
            "ocean_signal": OCEAN_SIGNAL_PATH,
        },
        "hardware": {
            "profile": HARDWARE_PROFILE,
            "summary": _hardware_summary(),
            "contract_conformance": _heartbeat_conformance_summary(limit_nodes=10),
            "nodes": list(HARDWARE_NODES.values()),
        },
        "audit": {
            "summary": _audit_summary(),
            "recent": _read_recent_audit_events(limit=10),
        },
        "openapi_snapshot": _openapi_summary(),
        "upstream": upstream,
        "ocean_core": ocean,
    }


@app.get("/admin/audit/recent")
@app.get(f"{API_PREFIX}/admin/audit/recent")
def admin_recent_audit(
    limit: int = 50,
    x_admin_token: Optional[str] = Header(default=None),
    authorization: Optional[str] = Header(default=None),
) -> Dict[str, Any]:
    _require_admin_access(x_admin_token, authorization)
    safe_limit = max(1, min(limit, 200))
    return {
        "service": SERVICE_NAME,
        "audit": _audit_summary(),
        "events": _read_recent_audit_events(limit=safe_limit),
        "returned": safe_limit,
    }


@app.post("/ocean/signals/publish")
@app.post(f"{API_PREFIX}/ocean/signals/publish")
async def publish_to_ocean(request: OceanSignalRequest) -> Dict[str, Any]:
    _reject_dry_run(request.dry_run, "ocean signal publishing")
    ocean_url = _require_ocean()
    url = f"{ocean_url}{OCEAN_SIGNAL_PATH}"
    outbound = {
        "event_type": request.event_type,
        "source": request.source,
        "payload": request.payload,
        "origin": "internal",
        "priority": request.priority,
        "tags": request.tags,
        "correlation_id": request.correlation_id,
    }

    try:
        async with httpx.AsyncClient(timeout=KLOUD_TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=outbound)
            response.raise_for_status()
            body = _safe_json(response)
        _append_audit_event(
            "signal.publish.ocean",
            "forwarded",
            "Live signal forwarded to Ocean Core.",
            actor=request.source,
            metadata={"event_type": request.event_type, "target": url},
        )
        return {
            "status": "forwarded",
            "forwarded": True,
            "target": "ocean-core",
            "ocean_url": url,
            "signal": body,
        }
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Ocean Core returned {exc.response.status_code} for {OCEAN_SIGNAL_PATH}: {exc.response.text[:300]}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to forward live signal to Ocean Core: {exc}",
        ) from exc


@app.post("/signals/publish")
@app.post(f"{API_PREFIX}/signals/publish")
async def publish_signal(request: PublishRequest) -> Dict[str, Any]:
    _reject_dry_run(request.dry_run, "signal publishing")
    upstream_url = _require_upstream()

    if not request.payload_b64 and not request.payload:
        raise HTTPException(
            status_code=400,
            detail="A real signal payload is required; empty or demo payloads are not allowed.",
        )

    payload_b64 = request.payload_b64 or _encode_payload(request.payload)
    submit_payload = {
        "ops": request.ops,
        "payload": payload_b64,
        "source": request.source,
        "submitted_at": _now_iso(),
    }
    route = request.route or KLOUD_SIGNAL_PATH
    url = f"{upstream_url}{route}"

    try:
        async with httpx.AsyncClient(timeout=KLOUD_TIMEOUT_SECONDS) as client:
            response = await client.post(url, json=submit_payload)
            response.raise_for_status()
            body = _safe_json(response)
        _record_signal_activity(request.source, route, request.payload, url)
        _append_audit_event(
            "signal.publish.kloud",
            "forwarded",
            "Live signal forwarded to the sovereign Kloud upstream.",
            actor=request.source,
            metadata={"route": route, "target": url, "ops": request.ops},
        )
        return {
            "status": "forwarded",
            "forwarded": True,
            "isolated": KLOUD_ISOLATED_MODE,
            "live_only": LIVE_ONLY_MODE,
            "route": route,
            "upstream_url": url,
            "source": request.source,
            "last_signal": _LAST_SIGNAL_ACTIVITY,
            "kloud_response": body,
        }
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Kloud upstream returned {exc.response.status_code} for {route}: {exc.response.text[:300]}",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to forward live signal to Kloud: {exc}",
        ) from exc


@app.post("/fabric/sync")
@app.post(f"{API_PREFIX}/fabric/sync")
async def fabric_sync(request: FabricSyncRequest) -> Dict[str, Any]:
    global _LAST_SUCCESSFUL_SYNC_AT

    _reject_dry_run(request.dry_run, "fabric synchronization")
    upstream_url = _require_upstream()

    collected: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    async with httpx.AsyncClient(timeout=KLOUD_TIMEOUT_SECONDS) as client:
        for key, include, path in (
            ("status", request.include_status, KLOUD_STATUS_PATH),
            ("peers", request.include_peers, KLOUD_PEERS_PATH),
            ("state", request.include_state, KLOUD_STATE_PATH),
        ):
            if not include:
                continue
            try:
                collected[key] = await _fetch_json(client, upstream_url, path)
            except Exception as exc:
                errors[key] = str(exc)

    if errors and not collected:
        raise HTTPException(
            status_code=502,
            detail=f"Unable to fetch live Kloud snapshot: {errors}",
        )

    if collected:
        _LAST_SUCCESSFUL_SYNC_AT = _now_iso()

    response: Dict[str, Any] = {
        "status": "synchronized" if not errors else "partial",
        "isolated": KLOUD_ISOLATED_MODE,
        "live_only": LIVE_ONLY_MODE,
        "upstream_url": upstream_url,
        "last_successful_sync": _LAST_SUCCESSFUL_SYNC_AT,
        "snapshot": collected,
    }
    if errors:
        response["errors"] = errors

    _append_audit_event(
        "fabric.sync",
        response["status"],
        "Live fabric synchronization executed.",
        actor="operator",
        metadata={
            "snapshot_keys": sorted(collected.keys()),
            "error_keys": sorted(errors.keys()),
            "upstream_url": upstream_url,
        },
    )
    return response


async def _probe_upstream() -> Dict[str, Any]:
    global _LAST_LIVE_UPSTREAM_URL, _LAST_SUCCESSFUL_SYNC_AT, _LAST_UPSTREAM_ERROR

    candidates = _ordered_upstream_candidates()
    if not candidates:
        return {
            "configured": False,
            "reachable": False,
            "message": "Kloud upstream is not configured. Set KLOUD_UPSTREAM_URL or KLOUD_UPSTREAM_CANDIDATES to enable live bridge data.",
        }

    last_error = ""
    checked: List[str] = []

    for candidate in candidates:
        checked.append(candidate)
        try:
            async with httpx.AsyncClient(timeout=min(KLOUD_TIMEOUT_SECONDS, 4)) as client:
                response = await client.get(f"{candidate}{KLOUD_STATUS_PATH}")
                response.raise_for_status()
                data = _safe_json(response)
            _LAST_LIVE_UPSTREAM_URL = candidate
            _LAST_SUCCESSFUL_SYNC_AT = _now_iso()
            _LAST_UPSTREAM_ERROR = ""
            return {
                "configured": True,
                "reachable": True,
                "url": candidate,
                "auto_discovered": candidate != KLOUD_UPSTREAM_URL,
                "candidates_checked": checked,
                "last_successful_sync": _LAST_SUCCESSFUL_SYNC_AT,
                "status": data,
            }
        except Exception as exc:
            last_error = str(exc)

    _LAST_UPSTREAM_ERROR = last_error
    return {
        "configured": True,
        "reachable": False,
        "url": KLOUD_UPSTREAM_URL or candidates[0],
        "candidates_checked": checked,
        "error": last_error,
        "last_successful_sync": _LAST_SUCCESSFUL_SYNC_AT,
        "message": "No live Kloud upstream responded. Start the sovereign fabric API or point KLOUD_UPSTREAM_URL to a reachable runtime.",
    }


async def _probe_ocean() -> Dict[str, Any]:
    if not OCEAN_CORE_URL:
        return {
            "configured": False,
            "reachable": False,
            "message": "Ocean Core URL is not configured. Set OCEAN_CORE_URL to enable bidirectional bridge visibility.",
        }

    try:
        async with httpx.AsyncClient(timeout=min(KLOUD_TIMEOUT_SECONDS, 4)) as client:
            response = await client.get(f"{OCEAN_CORE_URL}{OCEAN_STATUS_PATH}")
            response.raise_for_status()
            data = _safe_json(response)
        return {
            "configured": True,
            "reachable": True,
            "url": OCEAN_CORE_URL,
            "status": data,
        }
    except Exception as exc:
        return {
            "configured": True,
            "reachable": False,
            "url": OCEAN_CORE_URL,
            "error": str(exc),
        }


async def _forward_hardware_heartbeat_to_ocean(node: Dict[str, Any]) -> Dict[str, Any]:
    if not OCEAN_CORE_URL:
        return {
            "attempted": False,
            "forwarded": False,
            "message": "Ocean Core URL is not configured.",
        }

    outbound = {
        "event_type": "kloud.hardware.heartbeat",
        "source": "kloud-bridge",
        "payload": {
            "node_id": node.get("node_id"),
            "node_class": node.get("node_class"),
            "architecture": node.get("architecture"),
            "runtime": node.get("runtime"),
            "status": node.get("status"),
            "telemetry": node.get("telemetry", {}),
            "metrics": {
                "uptime_seconds": node.get("uptime_seconds"),
                "temperature_c": node.get("temperature_c"),
                "power_watts": node.get("power_watts"),
                "latency_ms": node.get("latency_ms"),
            },
        },
        "origin": "internal",
        "priority": "normal",
        "tags": ["kloud", "hardware", "edge", "heartbeat"],
        "correlation_id": f"hw-{node.get('node_id', 'unknown')}-{int(time.time())}",
    }

    try:
        async with httpx.AsyncClient(timeout=KLOUD_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{OCEAN_CORE_URL}{OCEAN_SIGNAL_PATH}", json=outbound)
            response.raise_for_status()
            body = _safe_json(response)
        return {
            "attempted": True,
            "forwarded": True,
            "response": body,
        }
    except Exception as exc:
        return {
            "attempted": True,
            "forwarded": False,
            "error": str(exc),
        }


async def _fetch_json(client: httpx.AsyncClient, base_url: str, path: str) -> Dict[str, Any]:
    response = await client.get(f"{base_url}{path}")
    response.raise_for_status()
    return _safe_json(response)


def _require_upstream() -> str:
    upstream_url = _current_upstream_target()
    if not upstream_url:
        raise HTTPException(
            status_code=503,
            detail="Kloud upstream is not configured. Live-only mode does not allow fake or local fallback responses.",
        )
    return upstream_url


def _require_ocean() -> str:
    if not OCEAN_CORE_URL:
        raise HTTPException(
            status_code=503,
            detail="Ocean Core URL is not configured. Bidirectional bridge mode requires OCEAN_CORE_URL.",
        )
    return OCEAN_CORE_URL


def _reject_dry_run(enabled: bool, operation: str) -> None:
    if enabled:
        raise HTTPException(
            status_code=400,
            detail=f"{operation.capitalize()} dry_run mode is disabled in production live-only mode.",
        )


def _encode_payload(payload: Dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def _safe_json(response: httpx.Response) -> Dict[str, Any]:
    try:
        data = response.json()
        if isinstance(data, dict):
            return data
        return {"data": data}
    except Exception:
        return {"text": response.text}


def _require_llm_upstream() -> str:
    value = (KLOUD_LLM_UPSTREAM_URL or "").strip().rstrip("/")
    if not value:
        raise HTTPException(
            status_code=503,
            detail="KLOUD_LLM_UPSTREAM_URL is not configured. Live-only mode requires a real remote LLM endpoint.",
        )
    return value


def _extract_user_prompt(messages: List[Dict[str, Any]]) -> str:
    text_parts: List[str] = []
    for message in messages or []:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role", "")).strip().lower()
        if role not in {"user", "system"}:
            continue
        content = message.get("content", "")
        if isinstance(content, str):
            value = content.strip()
            if value:
                text_parts.append(value)
    return "\n\n".join(text_parts).strip()


async def _call_llm_upstream_chat(*, prompt: str, model: str, temperature: Optional[float], max_tokens: Optional[int]) -> Dict[str, Any]:
    base = _require_llm_upstream()
    url = f"{base}{KLOUD_LLM_CHAT_PATH}"
    payload: Dict[str, Any] = {
        "message": prompt,
        "query": prompt,
        "model": model,
    }
    if temperature is not None:
        payload["temperature"] = temperature
    if isinstance(max_tokens, int) and max_tokens > 0:
        payload["max_tokens"] = max_tokens

    async with httpx.AsyncClient(timeout=KLOUD_LLM_TIMEOUT_SECONDS) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = _safe_json(response)
    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Remote LLM response is not a JSON object")
    return data


def _openai_envelope_from_upstream(data: Dict[str, Any], model: str) -> Dict[str, Any]:
    if isinstance(data.get("choices"), list):
        return data

    text = ""
    if isinstance(data.get("response"), str):
        text = data.get("response", "")
    elif isinstance(data.get("message"), str):
        text = data.get("message", "")
    elif isinstance(data.get("answer"), str):
        text = data.get("answer", "")

    text = text.strip()
    if not text:
        raise HTTPException(status_code=502, detail="Remote LLM returned empty text")

    created = int(time.time())
    return {
        "id": f"chatcmpl-kloud-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": created,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
    }


@app.post("/v1/chat/completions")
@app.post(f"{API_PREFIX}/llm/chat/completions")
async def llm_chat_completions(request: OpenAIChatCompletionsRequest) -> Dict[str, Any]:
    prompt = _extract_user_prompt(request.messages)
    if not prompt:
        raise HTTPException(status_code=400, detail="messages must include non-empty user/system content")

    try:
        upstream_data = await _call_llm_upstream_chat(
            prompt=prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
        return _openai_envelope_from_upstream(upstream_data, request.model)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Remote LLM upstream returned {exc.response.status_code}: {exc.response.text[:300]}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Remote LLM upstream request failed: {exc}") from exc


@app.post("/api/generate")
async def ollama_generate_proxy(request: OllamaGenerateRequest):
    prompt = (request.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    if not request.stream:
        upstream_data = await _call_llm_upstream_chat(
            prompt=prompt,
            model=request.model,
            temperature=request.options.get("temperature") if isinstance(request.options, dict) else None,
            max_tokens=request.options.get("num_predict") if isinstance(request.options, dict) else None,
        )
        envelope = _openai_envelope_from_upstream(upstream_data, request.model)
        content = str(envelope["choices"][0]["message"]["content"])
        return {"model": request.model, "response": content, "done": True}

    async def _iter_lines():
        upstream_data = await _call_llm_upstream_chat(
            prompt=prompt,
            model=request.model,
            temperature=request.options.get("temperature") if isinstance(request.options, dict) else None,
            max_tokens=request.options.get("num_predict") if isinstance(request.options, dict) else None,
        )
        envelope = _openai_envelope_from_upstream(upstream_data, request.model)
        content = str(envelope["choices"][0]["message"]["content"])
        if not content:
            raise HTTPException(status_code=502, detail="Remote LLM returned empty text")
        for i in range(0, len(content), KLOUD_LLM_STREAM_CHUNK_CHARS):
            chunk = content[i:i + KLOUD_LLM_STREAM_CHUNK_CHARS]
            yield json.dumps({"model": request.model, "response": chunk, "done": False}, ensure_ascii=False) + "\n"
        yield json.dumps({"model": request.model, "response": "", "done": True}, ensure_ascii=False) + "\n"

    return StreamingResponse(_iter_lines(), media_type="application/x-ndjson")
