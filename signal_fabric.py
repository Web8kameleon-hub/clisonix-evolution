from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional

try:
    import aiofiles  # type: ignore[import-untyped]
except ImportError:
    aiofiles = None

HTTPX: Any
try:
    import httpx as _httpx
    HTTPX = _httpx
except ImportError:
    HTTPX = None


class SignalLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SignalEvent:
    source: str
    kind: str
    level: SignalLevel = SignalLevel.INFO
    message: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    trace_id: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["level"] = self.level.value
        return data


class SignalFabric:
    """
    Unified signal fabric for module events.
    """

    def __init__(
        self,
        buffer_size: int = 5000,
        log_dir: str = "data/signal_fabric",
        webhook_url: Optional[str] = None,
    ) -> None:
        self._buffer: List[SignalEvent] = []
        self._subscribers: List[Callable[[SignalEvent], Awaitable[None]]] = []
        self._buffer_size = buffer_size
        self.log_dir = Path(log_dir)
        self.webhook_url = webhook_url
        self._lock = asyncio.Lock()

    async def publish(self, event: SignalEvent) -> None:
        async with self._lock:
            self._buffer.append(event)
            if len(self._buffer) > self._buffer_size:
                self._buffer = self._buffer[-self._buffer_size :]

        await self._fan_out(event)
        await self._persist(event)
        await self._forward_webhook(event)

    def subscribe(self, handler: Callable[[SignalEvent], Awaitable[None]]) -> None:
        self._subscribers.append(handler)

    def recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        return [event.to_dict() for event in self._buffer[-limit:]]

    def load_persisted(self, limit: int = 5000) -> List[Dict[str, Any]]:
        if limit <= 0:
            return []
        if not self.log_dir.exists():
            return []

        files = sorted(self.log_dir.glob("signals_*.jsonl"))
        if not files:
            return []

        rows: List[Dict[str, Any]] = []
        for path in files:
            try:
                with path.open("r", encoding="utf-8") as handle:
                    for line in handle:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            item = json.loads(line)
                            if isinstance(item, dict):
                                rows.append(item)
                        except Exception:
                            continue
            except Exception:
                continue

        return rows[-limit:]

    def all_signals(
        self,
        limit: int = 5000,
        include_buffer: bool = True,
        include_persisted: bool = True,
    ) -> List[Dict[str, Any]]:
        merged: List[Dict[str, Any]] = []

        if include_persisted:
            merged.extend(self.load_persisted(limit=limit * 2))
        if include_buffer:
            merged.extend(self.recent(limit=limit * 2))

        deduped: List[Dict[str, Any]] = []
        seen: set[tuple[Any, ...]] = set()
        for item in merged:
            key = (
                item.get("trace_id"),
                item.get("timestamp"),
                item.get("source"),
                item.get("kind"),
                item.get("message"),
            )
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)

        deduped.sort(key=lambda s: str(s.get("timestamp", "")))
        return deduped[-limit:]

    async def _fan_out(self, event: SignalEvent) -> None:
        for handler in self._subscribers:
            try:
                await handler(event)
            except Exception as exc:
                print(f"[SignalFabric] subscriber error: {exc}")

    async def _persist(self, event: SignalEvent) -> None:
        if not aiofiles:
            return
        self.log_dir.mkdir(parents=True, exist_ok=True)
        logfile = self.log_dir / f"signals_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
        async with aiofiles.open(logfile, "a", encoding="utf-8") as file:
            await file.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")

    async def _forward_webhook(self, event: SignalEvent) -> None:
        if not self.webhook_url or not HTTPX:
            return
        try:
            async with HTTPX.AsyncClient(timeout=5.0) as client:
                await client.post(self.webhook_url, json=event.to_dict())
        except Exception as exc:
            print(f"[SignalFabric] webhook error: {exc}")


_signal_fabric: Optional[SignalFabric] = None


def get_signal_fabric() -> SignalFabric:
    global _signal_fabric
    if _signal_fabric is None:
        _signal_fabric = SignalFabric()
    return _signal_fabric
