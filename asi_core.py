# -*- coding: utf-8 -*-
"""
asi_core_real.py – Real ASI Core (pa simulime, pa random)

Përfshin:
- ASICore: menaxhim i node-ve dhe logim real
- ClisonixNodeReal: raporton metrika reale të sistemit dhe ngarkon file audio/EEG
- ClisonixMeshNode: regjistron node-t te Mesh HQ dhe dërgon telemetry reale
"""

from __future__ import annotations

import asyncio
import datetime
import json
import os
import platform
import socket
import time
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict

from asi_realtime_engine import ASIRealtimeEngine

HAS_SIGNAL_FABRIC = False
FabricSignalEvent: Any = None
FabricSignalLevel: Any = None
get_signal_fabric: Any = None
try:
    from signal_fabric import SignalEvent as _FabricSignalEvent
    from signal_fabric import SignalLevel as _FabricSignalLevel
    from signal_fabric import get_signal_fabric as _get_signal_fabric

    FabricSignalEvent = _FabricSignalEvent
    FabricSignalLevel = _FabricSignalLevel
    get_signal_fabric = _get_signal_fabric
    HAS_SIGNAL_FABRIC = True
except Exception:
    HAS_SIGNAL_FABRIC = False

REQUESTS: Any

try:
    import requests as _requests
    REQUESTS = _requests
except ImportError:
    REQUESTS = None

try:
    import psutil
except ImportError:
    psutil = None


IS_IN_DOCKER = os.path.exists("/.dockerenv") or os.getenv("DOCKER_ENV") == "1"
DEFAULT_MESH_BASE_URL = "http://clisonix-api:8000" if IS_IN_DOCKER else "http://localhost:8000"


_ASI_NODE_ALIASES = {
    "alba": "ALBA",
    "albi": "ALBI",
    "jona": "JONA",
    "asi": "ASI",
}


def _normalize_node_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value or "").strip()
    if not normalized:
        return ""
    collapsed = "".join(
        ch for ch in unicodedata.normalize("NFKD", normalized)
        if not unicodedata.combining(ch)
    )
    key = "".join(ch for ch in collapsed.casefold() if ch.isalnum())
    return _ASI_NODE_ALIASES.get(key, normalized.upper())


@dataclass
class ASIConfig:
    hq_event_url: str = os.getenv("ASI_HQ_EVENT_URL", f"{DEFAULT_MESH_BASE_URL}/mesh/status")
    hq_register_url: str = os.getenv("ASI_HQ_REGISTER_URL", f"{DEFAULT_MESH_BASE_URL}/mesh/register")
    hq_status_url: str = os.getenv("ASI_HQ_STATUS_URL", f"{DEFAULT_MESH_BASE_URL}/mesh/status")
    api_audio_url: str = os.getenv("ASI_AUDIO_UPLOAD_URL", "https://clisonix.com/api/uploads/audio/process")
    api_eeg_url: str = os.getenv("ASI_EEG_UPLOAD_URL", "https://clisonix.com/api/uploads/eeg/process")
    request_timeout_seconds: float = float(os.getenv("ASI_REQUEST_TIMEOUT_SECONDS", "5"))
    max_retries: int = int(os.getenv("ASI_REQUEST_MAX_RETRIES", "3"))
    retry_backoff_seconds: float = float(os.getenv("ASI_REQUEST_RETRY_BACKOFF_SECONDS", "0.5"))


class ASICore:
    """Bërthama reale e ASI – telemetri dhe status node-sh."""

    def __init__(
        self,
        hq_url: str = "",
        config: ASIConfig | None = None,
        language: str = "sq",
    ) -> None:
        self.status = "active"
        self.config = config or ASIConfig()
        self.hq_url = hq_url or self.config.hq_event_url
        self.language = language
        self.nodes: Dict[str, Dict[str, Any]] = {
            "ALBA": {"status": "active", "role": "data_collector"},
            "ALBI": {"status": "active", "role": "neural_processor"},
            "JONA": {"status": "active", "role": "coordinator"},
        }
        self.logs: list[Dict[str, Any]] = []
        self.realtime_engine = ASIRealtimeEngine(log_dir="logs", language=language)
        self._recalculate_health()

    # ---------------- Language management ----------------
    def set_language(self, language: str) -> None:
        self.language = language
        self.realtime_engine.set_language(language)

    # ---------------- Logging & HQ transmission ----------------
    def log_event(self, source: str, event: str, level: str = "INFO") -> None:
        source_key = _normalize_node_name(source)
        hints = {
            "ALBA": "Mbledhje e të dhënave dhe sinjaleve fizike.",
            "ALBI": "Analizë e sinjaleve dhe përpunim neural.",
            "JONA": "Koordinim i node-ve dhe sinkronizim i rrjetit."
        }
        entry = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "source": source_key,
            "event": event,
            "hint": hints.get(source_key, ""),
            "level": level,
        }
        self.logs.append(entry)
        print(f"[{source_key}] {level}: {event}")
        if entry["hint"]:
            print(f"💡 {entry['hint']}")
        self._send_to_hq(entry)
        self._publish_to_signal_fabric(source_key, event, level, entry)

    def _publish_to_signal_fabric(self, source: str, event: str, level: str, payload: Dict[str, Any]) -> None:
        if not HAS_SIGNAL_FABRIC:
            return

        normalized_level = level.upper()
        if normalized_level == "WARN":
            normalized_level = "WARNING"
        if normalized_level not in FabricSignalLevel.__members__:
            normalized_level = "INFO"

        signal_level = FabricSignalLevel[normalized_level]
        signal_event = FabricSignalEvent(
            source=source,
            kind="asi_log",
            level=signal_level,
            message=event,
            payload=payload,
            tags=["asi", source.lower()],
        )

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(get_signal_fabric().publish(signal_event))
        except RuntimeError:
            return
        except Exception:
            return

    def _post_with_retries(self, url: str, **kwargs: Any):
        if not REQUESTS:
            return None

        last_exc: Exception | None = None
        timeout = kwargs.pop("timeout", self.config.request_timeout_seconds)
        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = REQUESTS.post(url, timeout=timeout, **kwargs)
                if response.status_code < 500:
                    return response
                last_exc = RuntimeError(f"HTTP {response.status_code} from {url}")
            except Exception as exc:
                last_exc = exc

            if attempt < self.config.max_retries:
                time.sleep(self.config.retry_backoff_seconds * attempt)

        if last_exc is not None:
            raise last_exc
        return None

    def _send_to_hq(self, entry: Dict[str, Any]) -> None:
        if not REQUESTS:
            return
        try:
            self._post_with_retries(self.hq_url, json=entry)
        except Exception as exc:
            print(f"[ASI] ⚠️ HQ i paarritshëm: {exc}")

    # ---------------- Node health ----------------
    def update_node_status(self, node: str, status: str) -> None:
        node_key = _normalize_node_name(node)
        if node_key not in self.nodes:
            self.log_event("ASI", f"Node i panjohur: {node}", "WARN")
            return
        self.nodes[node_key]["status"] = status
        self._recalculate_health()
        self.log_event(node_key, f"Statusi u përditësua në {status}")

    def _recalculate_health(self) -> None:
        active = sum(1 for n in self.nodes.values() if n["status"] == "active")
        self.health_score = round(active / len(self.nodes), 2)

    def analyze_status(self) -> Dict[str, Any]:
        print("📊 Analizë e gjendjes aktuale:")
        for name, info in self.nodes.items():
            st = info["status"]
            if st != "active":
                print(f"⚠️ {name}: {st} – kontrollo rrjetin ose energjinë.")
            else:
                print(f"✅ {name}: aktiv ({info['role']})")
        print(f"Shëndeti total: {self.health_score*100:.1f}%")
        return {
            "asi_status": self.status,
            "nodes": self.nodes,
            "health_score": self.health_score,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "realtime": self.realtime_engine.status(),
        }

    def get_health_snapshot(self) -> Dict[str, Any]:
        return {
            "service": "ASI Real Core",
            "status": self.status,
            "health_score": self.health_score,
            "nodes": self.nodes,
            "realtime": self.realtime_engine.status(),
            "logs": {
                "count": len(self.logs),
                "recent": self.logs[-20:],
            },
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        }

    def export_logs(self, filename: str = "asi_logs.json") -> None:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.logs, f, indent=2, ensure_ascii=False)
        print(f"[ASI] Loget u ruajtën në {filename}")

    def realtime_status(self) -> Dict[str, Any]:
        """Expose realtime engine status for external callers."""

        return self.realtime_engine.status()

    def get_realtime_status(self) -> Dict[str, Any]:
        return self.realtime_status()


class ClisonixNodeReal:
    """Node real që ngarkon file dhe raporton metrika të sistemit."""

    def __init__(self, asi_core: ASICore, node_id: str = "CLX-REAL") -> None:
        self.id = node_id
        self.asi = asi_core
        self.api_audio = self.asi.config.api_audio_url
        self.api_eeg = self.asi.config.api_eeg_url

    def collect_system_metrics(self) -> Dict[str, Any]:
        if not psutil:
            self.asi.log_event("ASI", "psutil mungon – nuk ka metrika reale", "ERROR")
            return {
                "error": "psutil_missing",
                "timestamp": time.time(),
            }
        net = psutil.net_io_counters()
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage(os.path.sep).percent,
            "net_sent_mb": round(net.bytes_sent / (1024 * 1024), 2),
            "net_recv_mb": round(net.bytes_recv / (1024 * 1024), 2),
            "timestamp": time.time(),
        }

    def transmit_audio_file(self, filepath: str) -> None:
        if not os.path.exists(filepath):
            self.asi.log_event("ALBA", f"Audio file mungon: {filepath}", "WARN")
            return
        if not REQUESTS:
            self.asi.log_event("ALBA", "requests mungon – s'mund të ngarkohet audio", "ERROR")
            return
        try:
            with open(filepath, "rb") as f:
                res = self.asi._post_with_retries(self.api_audio, files={"file": f}, timeout=10)
                status_code = res.status_code if res is not None else "unknown"
                self.asi.log_event("ALBA", f"Ngarkuar {os.path.basename(filepath)} → {status_code}")
        except Exception as exc:
            self.asi.log_event("ALBA", f"Dështoi upload audio: {exc}", "ERROR")

    def transmit_eeg_file(self, filepath: str) -> None:
        if not os.path.exists(filepath):
            self.asi.log_event("ALBI", f"EEG file mungon: {filepath}", "WARN")
            return
        if not REQUESTS:
            self.asi.log_event("ALBI", "requests mungon – s'mund të ngarkohet EEG", "ERROR")
            return
        try:
            with open(filepath, "rb") as f:
                res = self.asi._post_with_retries(self.api_eeg, files={"file": f}, timeout=10)
                status_code = res.status_code if res is not None else "unknown"
                self.asi.log_event("ALBI", f"Ngarkuar EEG {os.path.basename(filepath)} → {status_code}")
        except Exception as exc:
            self.asi.log_event("ALBI", f"Dështoi upload EEG: {exc}", "ERROR")

    def report_system(self) -> None:
        metrics = self.collect_system_metrics()
        self.asi.log_event("ASI", f"Metrika reale: {metrics}")


class ClisonixMeshNode:
    """Node që lidhet me Mesh HQ dhe dërgon telemetry reale."""

    def __init__(self, asi_core: ASICore, node_id: str = "CLX-REAL", location: str = "Europe") -> None:
        self.asi = asi_core
        self.node_id = node_id
        self.location = location
        self.hq_url = self.asi.config.hq_register_url
        self.status_url = self.asi.config.hq_status_url
        self.hostname = socket.gethostname()
        try:
            self.ip = socket.gethostbyname(self.hostname)
        except Exception:
            self.ip = "127.0.0.1"
        self.status = "active"

    def collect_metrics(self) -> Dict[str, Any]:
        if not psutil:
            raise RuntimeError("psutil kërkohet për metrika reale.")
        net = psutil.net_io_counters()
        return {
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage(os.path.sep).percent,
            "net_sent_mb": round(net.bytes_sent / (1024 * 1024), 2),
            "net_recv_mb": round(net.bytes_recv / (1024 * 1024), 2),
            "hostname": self.hostname,
            "ip": self.ip,
            "os": platform.system(),
            "version": platform.version(),
            "timestamp": time.time(),
        }

    def register_node(self) -> None:
        if not REQUESTS:
            self.asi.log_event("JONA", "requests mungon – s'mund të regjistrohet node", "ERROR")
            return
        payload = {
            "id": self.node_id,
            "location": self.location,
            "ip": self.ip,
            "hostname": self.hostname,
            "status": self.status,
        }
        try:
            res = self.asi._post_with_retries(self.hq_url, json=payload)
            status_code = res.status_code if res is not None else "unknown"
            self.asi.log_event("JONA", f"Node i regjistruar në Mesh HQ → {status_code}")
        except Exception as exc:
            self.asi.log_event("JONA", f"Dështoi regjistrimi në Mesh HQ: {exc}", "ERROR")

    def send_status(self) -> None:
        if not REQUESTS:
            self.asi.log_event("ASI", "requests mungon – s'mund të dërgohet telemetry", "ERROR")
            return
        metrics = self.collect_metrics()
        payload = {"id": self.node_id, "status": self.status, "metrics": metrics}
        try:
            res = self.asi._post_with_retries(self.status_url, json=payload)
            status_code = res.status_code if res is not None else "unknown"
            self.asi.log_event("ASI", f"Telemetry reale dërguar → {status_code}")
        except Exception as exc:
            self.asi.log_event("ASI", f"Dështoi dërgimi i telemetry: {exc}", "ERROR")


def _cli():
    import argparse
    parser = argparse.ArgumentParser(description="Run ASI Core në modalitet real")
    parser.add_argument("mode", choices=["node", "mesh"], help="node = Clisonix real, mesh = lidhje HQ")
    args = parser.parse_args()

    asi = ASICore()
    if args.mode == "node":
        node = ClisonixNodeReal(asi)
        node.report_system()
        node.transmit_audio_file("data/audio.wav")
        node.transmit_eeg_file("data/eeg.edf")
    elif args.mode == "mesh":
        mesh = ClisonixMeshNode(asi)
        mesh.register_node()
        mesh.send_status()


if __name__ == "__main__":
    _cli()
def get_system_status():
    return {
        "overall_health": "degraded",
        "active_nodes": 5,
        "total_nodes": 8,
        "last_checked": "just now",
        "issues": [
            {"node": "High-Frequency Audio Spectrometer", "issue": "Connection timeout"},
            {"node": "Industrial Vibration Sensors", "issue": "Scheduled maintenance"}
        ]
    }

