from datetime import datetime, timezone
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from apps.api.clisonix_ai_engine import EAPPipeline

app = FastAPI(title="Clisonix EAP Engine", version="1.0.0")


class EAPProcessRequest(BaseModel):
    document: str
    topic: str = "neuroscience"
    source: str = "api"


def _music_scale_map() -> Dict[str, float]:
    return {
        "do": 261.63,
        "re": 293.66,
        "mi": 329.63,
        "fa": 349.23,
        "so": 392.00,
        "la": 440.00,
        "si": 493.88,
    }


def _analysis_payload(evresi_output: Dict[str, Any]) -> Dict[str, Any]:
    text = str(evresi_output.get("raw_input", {})).lower()
    detected_bands: List[str] = []
    for band in ["delta", "theta", "alpha", "beta", "gamma"]:
        if band in text:
            detected_bands.append(band)

    if not detected_bands:
        detected_bands = ["alpha", "beta"]

    return {
        "domain": "eeg-neural-synthesis",
        "detected_bands": detected_bands,
        "pipeline": ["evresi", "analysi", "proposi"],
        "music_midi_scale": _music_scale_map(),
        "note": "Mapped to do-re-mi-fa-so-la-si for MIDI synthesis support.",
    }


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "service": "eap-engine",
        "pipeline": ["evresi", "analysi", "proposi"],
        "status": "ready",
    }


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "eap-engine",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/eap/process")
async def process_document(payload: EAPProcessRequest):
    if not payload.document.strip():
        raise HTTPException(status_code=400, detail="document must not be empty")

    pipeline = EAPPipeline()
    evresi = pipeline.evresi({
        "document": payload.document,
        "topic": payload.topic,
        "source": payload.source,
    })
    analysi = pipeline.analysi(evresi, analysis_func=_analysis_payload)
    proposi = pipeline.proposi(analysi)
    response = {
        "phase": proposi.phase.value,
        "evresi": evresi,
        "analysi": analysi,
        "proposi": {
            "output_data": proposi.output_data,
            "quality": {
                "overall": proposi.quality.overall,
                "accuracy": proposi.quality.accuracy,
                "completeness": proposi.quality.completeness,
                "clarity": proposi.quality.clarity,
                "relevance": proposi.quality.relevance,
                "tier": proposi.quality.tier.value,
            },
            "metadata": proposi.metadata,
            "processing_time_ms": proposi.processing_time_ms,
        },
    }
    return JSONResponse(content=response, media_type="application/json; charset=utf-8")


@app.post("/eap/phases")
async def process_phases(payload: EAPProcessRequest):
    if not payload.document.strip():
        raise HTTPException(status_code=400, detail="document must not be empty")

    pipeline = EAPPipeline()
    evresi = pipeline.evresi({
        "document": payload.document,
        "topic": payload.topic,
        "source": payload.source,
    })
    analysi = pipeline.analysi(evresi, analysis_func=_analysis_payload)
    proposi = pipeline.proposi(analysi)
    response: Dict[str, Any] = {
        "evresi": evresi,
        "analysi": analysi,
        "proposi": {
            "phase": proposi.phase.value,
            "output_data": proposi.output_data,
            "metadata": proposi.metadata,
            "quality_tier": proposi.quality.tier.value,
        },
    }
    return JSONResponse(content=response, media_type="application/json; charset=utf-8")