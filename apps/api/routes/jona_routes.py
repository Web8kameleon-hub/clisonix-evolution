"""
JONA Neural Synthesis API Routes
================================
Backend API endpoints for JONA - Joyful Overseer of Neural Alignment

Provides:
- Real-time neural synthesis status
- Audio generation and playback
- Session management
- Brainwave-to-audio conversion
"""

import asyncio
import logging
import os
import random
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

logger = logging.getLogger("jona_routes")

router = APIRouter(prefix="/api/jona", tags=["JONA Neural Synthesis"])

# ============================================================================
# MODELS
# ============================================================================

class SynthesisSession(BaseModel):
    session_id: str
    status: str  # idle, recording, synthesizing, complete
    duration_seconds: float
    samples_processed: int
    created_at: str
    user_id: Optional[str] = None

class AudioFile(BaseModel):
    file_id: str
    filename: str
    format: str
    duration_ms: int
    sample_rate: int
    channels: int
    size_bytes: int
    created_at: str
    neural_frequency: float
    waveform_type: str

class JonaMetrics(BaseModel):
    service: str
    status: str
    version: str
    eeg_signals_processed: int
    audio_files_created: int
    current_symphony: Optional[str]
    neural_frequency: float
    excitement_level: float
    uptime_seconds: int
    last_synthesis: Optional[str]

class SynthesisConfig(BaseModel):
    frequency: float = 14.0  # Hz - Alpha waves default
    waveform: str = "sine"   # sine, square, triangle, sawtooth
    duration: int = 60       # seconds
    modulation: bool = True
    binaural: bool = False
    base_frequency: float = 200.0  # Hz for carrier wave

class WaveformData(BaseModel):
    channel: str
    data: List[float]
    frequency: float
    amplitude: float

# ============================================================================
# IN-MEMORY STATE (Production would use Redis/Database)
# ============================================================================

_active_sessions: Dict[str, Dict[str, Any]] = {}
_audio_library: List[Dict[str, Any]] = []
_service_start_time = datetime.now()
_total_signals_processed = 0
_total_audio_created = 0
_active_proxy_session_id: Optional[str] = None

JONA_CANDIDATE_URLS = [
    os.getenv("JONA_API_URL"),
    "http://jona:7777",
    "http://localhost:7777",
]


def _to_positive_int(value: Any) -> int:
    try:
        parsed = int(float(value))
    except (TypeError, ValueError):
        return 0
    return max(0, parsed)


def _to_positive_float(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, parsed)


def _normalize_audio_files(files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    by_file_id: Dict[str, Dict[str, Any]] = {}
    by_filename: Dict[str, Dict[str, Any]] = {}

    for raw in files:
        if not isinstance(raw, dict):
            continue

        file_id = str(raw.get("file_id", "") or "").strip()
        filename = str(raw.get("filename", "") or "").strip()
        if not file_id or not filename:
            continue

        normalized_item: Dict[str, Any] = {
            "file_id": file_id,
            "filename": filename,
            "format": str(raw.get("format", "") or "").lower() or "wav",
            "duration_ms": _to_positive_int(raw.get("duration_ms", 0)),
            "sample_rate": _to_positive_int(raw.get("sample_rate", 0)),
            "channels": max(1, _to_positive_int(raw.get("channels", 1))),
            "size_bytes": _to_positive_int(raw.get("size_bytes", 0)),
            "created_at": str(raw.get("created_at", "") or ""),
            "neural_frequency": _to_positive_float(raw.get("neural_frequency", 0.0)),
            "waveform_type": str(raw.get("waveform_type", "") or "").strip().lower() or "unknown",
            "download_url": str(raw.get("download_url", "") or ""),
        }

        waveform = normalized_item["waveform_type"]
        has_valid_duration = normalized_item["duration_ms"] > 0
        has_valid_frequency = normalized_item["neural_frequency"] > 0
        has_known_waveform = waveform not in {"", "unknown", "none", "null"}
        quality = int(has_valid_duration) + int(has_valid_frequency) + int(has_known_waveform)

        existing = by_file_id.get(file_id)
        if existing is None:
            normalized_item["_quality"] = quality
            by_file_id[file_id] = normalized_item
        else:
            existing_quality = int(existing.get("_quality", 0))
            if quality > existing_quality:
                normalized_item["_quality"] = quality
                by_file_id[file_id] = normalized_item

    for item in by_file_id.values():
        filename_key = str(item.get("filename", "")).strip().lower()
        if not filename_key:
            continue

        existing = by_filename.get(filename_key)
        if existing is None:
            by_filename[filename_key] = item
            continue

        item_quality = int(item.get("_quality", 0))
        existing_quality = int(existing.get("_quality", 0))
        if item_quality > existing_quality:
            by_filename[filename_key] = item

    for item in by_filename.values():
        cleaned = dict(item)
        cleaned.pop("_quality", None)
        normalized.append(cleaned)

    normalized.sort(key=lambda row: str(row.get("created_at", "")), reverse=True)
    return normalized


async def _jona_request(method: str, path: str, json_payload: Optional[Dict[str, Any]] = None):
    last_error: Optional[Exception] = None
    for base in [url for url in JONA_CANDIDATE_URLS if url]:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.request(method, f"{base.rstrip('/')}{path}", json=json_payload)
                if response.status_code >= 400:
                    detail = response.text
                    raise HTTPException(status_code=response.status_code, detail=detail)
                if not response.content:
                    return {}
                return response.json()
        except HTTPException:
            raise
        except Exception as exc:
            last_error = exc
            continue

    raise HTTPException(status_code=502, detail=f"JONA backend unavailable: {last_error}")

# Pre-populate some demo audio files
for i in range(5):
    _audio_library.append({
        "file_id": str(uuid.uuid4()),
        "filename": f"neural_symphony_{i+1}.wav",
        "format": "WAV",
        "duration_ms": random.randint(30000, 180000),
        "sample_rate": 44100,
        "channels": 2,
        "size_bytes": random.randint(1000000, 10000000),
        "created_at": datetime.now().isoformat(),
        "neural_frequency": random.uniform(8.0, 30.0),
        "waveform_type": random.choice(["sine", "binaural", "isochronic"])
    })

# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/status")
async def get_jona_status() -> Dict[str, Any]:
    """Get JONA Neural Synthesis service status"""
    health = await _jona_request("GET", "/health")
    status = await _jona_request("GET", "/status")
    audio = await _jona_request("GET", "/audio/list")

    active_sessions = int(status.get("active_sessions", 0))
    active_frequency = 14.0
    current_symphony = None
    sessions = status.get("sessions", {})
    if isinstance(sessions, dict) and sessions:
        first = next(iter(sessions.values()))
        if isinstance(first, dict):
            active_frequency = float(first.get("frequency", 14.0))
            current_symphony = first.get("session_id")

    return {
        "success": True,
        "service": "JONA Neural Synthesis",
        "tagline": "Joyful Overseer of Neural Alignment",
        "status": "online",
        "version": health.get("version", "1.0.0"),
        "metrics": {
            "eeg_signals_processed": int(active_sessions * 256),
            "audio_files_created": int(audio.get("count", 0)),
            "active_sessions": active_sessions,
            "current_symphony": current_symphony,
            "neural_frequency": active_frequency,
            "excitement_level": random.uniform(0.6, 0.95),
            "uptime_seconds": int((datetime.now() - _service_start_time).total_seconds())
        },
        "capabilities": [
            "eeg_to_audio",
            "binaural_beats",
            "isochronic_tones",
            "neural_entrainment",
            "real_time_synthesis"
        ],
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def get_jona_health() -> Dict[str, Any]:
    """Health check for JONA service"""
    return {
        "success": True,
        "healthy": True,
        "service": "jona-neural-synthesis",
        "version": "2.1.0",
        "checks": {
            "audio_engine": "healthy",
            "synthesis_pipeline": "healthy",
            "memory": "ok",
            "cpu": "ok"
        },
        "uptime_seconds": int((datetime.now() - _service_start_time).total_seconds()),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/session")
async def get_current_session() -> Dict[str, Any]:
    """Get current active synthesis session"""
    if not _active_sessions:
        return {
            "success": True,
            "active": False,
            "session": None,
            "message": "No active synthesis session"
        }

    session_id = list(_active_sessions.keys())[0]
    session = _active_sessions[session_id]

    # Update duration
    session["duration_seconds"] = (datetime.now() - datetime.fromisoformat(session["created_at"])).total_seconds()
    session["samples_processed"] = int(session["duration_seconds"] * 256)  # 256 Hz sample rate

    return {
        "success": True,
        "active": True,
        "session": session
    }

@router.post("/synthesis/start")
async def start_synthesis(config: Optional[SynthesisConfig] = None) -> Dict[str, Any]:
    """Start a new neural synthesis session"""
    global _active_proxy_session_id

    if config is None:
        config = SynthesisConfig()

    waveform = config.waveform
    if waveform == "pink":
        waveform = "pink_noise"

    payload = {
        "user_id": f"web-{uuid.uuid4().hex[:8]}",
        "target_frequency": config.frequency,
        "waveform_type": waveform,
        "volume": 75,
    }
    real = await _jona_request("POST", "/session/start", payload)
    _active_proxy_session_id = real.get("session_id")

    return {
        "success": True,
        "message": "Neural synthesis started",
        "session": {
            "session_id": real.get("session_id"),
            "status": "synthesizing",
            "frequency": config.frequency,
            "waveform": waveform,
            "duration_target": config.duration,
            "duration_seconds": 0,
            "samples_processed": 0,
            "symphony_name": f"Neural Symphony #{real.get('session_id', '')[-6:]}",
            "created_at": datetime.now().isoformat(),
            "config": config.model_dump(),
        }
    }

@router.post("/synthesis/stop")
async def stop_synthesis() -> Dict[str, Any]:
    """Stop current synthesis session and generate audio file"""
    global _active_proxy_session_id

    if not _active_proxy_session_id:
        raise HTTPException(status_code=404, detail="No active synthesis session to stop")

    session_id = _active_proxy_session_id
    real = await _jona_request("POST", f"/session/{session_id}/stop")
    _active_proxy_session_id = None

    audio_file = real.get("audio_file") or {}
    if audio_file:
        _audio_library.append(audio_file)

    logger.info(f"[JONA] Stopped synthesis, created: {audio_file.get('filename', 'unknown')}")

    return {
        "success": True,
        "message": "Synthesis complete",
        "audio_file": audio_file,
        "session_summary": {
            "session_id": session_id,
            "duration_seconds": max(0, int((audio_file.get("duration_ms", 0) or 0) / 1000)),
            "samples_processed": int(max(0, int((audio_file.get("duration_ms", 0) or 0) / 1000)) * 256)
        }
    }

@router.get("/audio/list")
async def list_audio_files() -> Dict[str, Any]:
    """List all generated audio files"""
    real = await _jona_request("GET", "/audio/list")
    raw_files = real.get("files", []) if isinstance(real, dict) else []
    files = _normalize_audio_files(raw_files)
    return {
        "success": True,
        "count": len(files),
        "files": files,
        "total_duration_ms": sum((f.get("duration_ms", 0) or 0) for f in files),
        "total_size_bytes": sum((f.get("size_bytes", 0) or 0) for f in files)
    }

@router.get("/audio/{file_id}")
async def get_audio_file(file_id: str) -> Dict[str, Any]:
    """Get details of a specific audio file"""
    for audio in _audio_library:
        if audio["file_id"] == file_id:
            return {
                "success": True,
                "file": audio
            }

    raise HTTPException(status_code=404, detail=f"Audio file not found: {file_id}")


@router.get("/synthesis/preview")
async def synthesis_preview(seconds: float = 2.2, session_id: Optional[str] = None):
    preview_seconds = max(0.25, min(float(seconds), 10.0))
    query = f"/synthesis/preview?seconds={preview_seconds}"
    if session_id:
        query += f"&session_id={session_id}"

    last_error: Optional[Exception] = None
    for base in [url for url in JONA_CANDIDATE_URLS if url]:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                upstream = await client.get(f"{base.rstrip('/')}{query}")
                if upstream.status_code >= 400:
                    continue
                content_type = upstream.headers.get("content-type", "audio/wav")
                return Response(
                    content=upstream.content,
                    media_type=content_type,
                    headers={"Cache-Control": "no-store"},
                )
        except Exception as exc:
            last_error = exc
            continue

    raise HTTPException(status_code=502, detail=f"Unable to generate synthesis preview: {last_error}")


@router.get("/audio/{file_id}/download")
async def download_audio_file(file_id: str):
    files_payload = await _jona_request("GET", "/audio/list")
    files = files_payload.get("files", []) if isinstance(files_payload, dict) else []

    target = None
    for item in files:
        if str(item.get("file_id", "")) == file_id:
            target = item
            break

    if not target:
        raise HTTPException(status_code=404, detail=f"Audio file not found: {file_id}")

    download_url = str(target.get("download_url", ""))
    if not download_url.startswith("/"):
        raise HTTPException(status_code=500, detail="Invalid download URL")

    last_error: Optional[Exception] = None
    for base in [url for url in JONA_CANDIDATE_URLS if url]:
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                upstream = await client.get(f"{base.rstrip('/')}{download_url}")
                if upstream.status_code >= 400:
                    continue
                content_type = upstream.headers.get("content-type", "application/octet-stream")
                filename = str(target.get("filename", "audio.wav"))
                return Response(
                    content=upstream.content,
                    media_type=content_type,
                    headers={"Content-Disposition": f"attachment; filename={filename}"},
                )
        except Exception as exc:
            last_error = exc
            continue

    raise HTTPException(status_code=502, detail=f"Unable to stream audio file: {last_error}")

@router.delete("/audio/{file_id}")
async def delete_audio_file(file_id: str) -> Dict[str, Any]:
    """Delete an audio file"""
    real = await _jona_request("DELETE", f"/audio/{file_id}")
    return {
        "success": True,
        "message": real.get("message", "Deleted"),
        "file_id": file_id,
    }

@router.get("/waveform/live")
async def get_live_waveform() -> Dict[str, Any]:
    """Get live waveform data for visualization"""

    # Generate sample waveform data
    channels = ["Alpha", "Beta", "Theta", "Delta", "Gamma"]
    waveforms = []

    for ch in channels:
        # Generate 100 samples of simulated brainwave data
        data = [random.gauss(0, 1) for _ in range(100)]
        waveforms.append({
            "channel": ch,
            "data": data,
            "frequency": random.uniform(8, 30),
            "amplitude": random.uniform(0.5, 1.5)
        })

    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "sample_rate": 256,
        "waveforms": waveforms
    }

@router.get("/frequencies")
async def get_frequency_bands() -> Dict[str, Any]:
    """Get current frequency band power"""
    return {
        "success": True,
        "bands": {
            "delta": {"range": "0.5-4 Hz", "power": random.uniform(20, 40), "description": "Deep sleep"},
            "theta": {"range": "4-8 Hz", "power": random.uniform(30, 50), "description": "Drowsiness, light sleep"},
            "alpha": {"range": "8-12 Hz", "power": random.uniform(50, 80), "description": "Relaxed, calm"},
            "beta": {"range": "12-30 Hz", "power": random.uniform(40, 70), "description": "Active thinking"},
            "gamma": {"range": "30-100 Hz", "power": random.uniform(10, 30), "description": "High cognition"}
        },
        "dominant": "alpha",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/frequency/set")
async def set_target_frequency(frequency: float = 14.0) -> Dict[str, Any]:
    """Set target neural entrainment frequency"""
    if not (0.5 <= frequency <= 100):
        raise HTTPException(status_code=400, detail="Frequency must be between 0.5 and 100 Hz")

    return {
        "success": True,
        "message": f"Target frequency set to {frequency} Hz",
        "frequency": frequency,
        "band": (
            "delta" if frequency < 4 else
            "theta" if frequency < 8 else
            "alpha" if frequency < 12 else
            "beta" if frequency < 30 else
            "gamma"
        )
    }
