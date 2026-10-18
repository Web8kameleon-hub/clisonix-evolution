"""MALI central control plane: project context plus durable Redis signal stream."""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Dict, Optional

import redis.asyncio as redis_async


@dataclass
class SignalEnvelope:
    type: str
    source_module: str
    payload: Dict[str, Any]
    target_modules: list[str] = field(default_factory=list)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    spec_version: str = "clisonix.signal/v1"
    occurred_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    tenant_id: Optional[str] = None
    visibility: str = "internal"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MaliControlPlane:
    def __init__(self, map_path: str | Path) -> None:
        self.project_map = json.loads(Path(map_path).read_text(encoding="utf-8"))
        self.modules: Dict[str, Dict[str, Any]] = self.project_map.get("modules", {})
        self._validate_map()
        self.stream = self.project_map["signal_stream"]
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis: Any = None

    def _validate_map(self) -> None:
        if self.project_map.get("spec_version") != "clisonix.project-map/v1":
            raise ValueError("unsupported project map")
        central = self.project_map.get("central_orchestrator")
        if central != "intelligence-lab" or central not in self.modules:
            raise ValueError("intelligence-lab/MALI must be the central orchestrator")
        for module_id, module in self.modules.items():
            for dependency in module.get("dependencies", []):
                if dependency not in self.modules:
                    raise ValueError(f"{module_id} has unknown dependency {dependency}")

    async def connect(self) -> None:
        self.redis = redis_async.from_url(self.redis_url, decode_responses=True)
        await self.redis.ping()

    async def close(self) -> None:
        if self.redis is not None:
            await self.redis.aclose()
            self.redis = None

    async def publish(self, envelope: SignalEnvelope) -> str:
        if self.redis is None:
            raise RuntimeError("MALI signal fabric unavailable")
        if envelope.source_module not in self.modules:
            raise ValueError(f"unknown source module: {envelope.source_module}")
        unknown = set(envelope.target_modules) - set(self.modules)
        if unknown:
            raise ValueError(f"unknown target modules: {', '.join(sorted(unknown))}")
        await self.redis.xadd(
            self.stream,
            {"event": json.dumps(envelope.to_dict(), ensure_ascii=False)},
            maxlen=int(os.getenv("MALI_SIGNAL_MAXLEN", "100000")),
            approximate=True,
        )
        return envelope.event_id

    async def recent(self, limit: int = 100) -> list[Dict[str, Any]]:
        rows = await self.redis.xrevrange(self.stream, count=max(1, min(limit, 1000)))
        result = [json.loads(fields["event"]) for _, fields in rows]
        result.reverse()
        return result

    async def events(self, last_id: str = "$") -> AsyncIterator[Dict[str, Any]]:
        cursor = last_id
        while True:
            rows = await self.redis.xread({self.stream: cursor}, block=15000, count=100)
            for _, messages in rows:
                for message_id, fields in messages:
                    cursor = message_id
                    yield json.loads(fields["event"])

    def context(self, module_id: str) -> Dict[str, Any]:
        module = self.modules[module_id]
        return {
            "project": self.project_map["project"],
            "module_id": module_id,
            "module": module,
            "dependencies": {key: self.modules[key] for key in module.get("dependencies", [])},
            "signal_stream": self.stream,
        }
