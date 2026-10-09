"""
OCEAN CORE — Mega Layer API
============================
FastAPI endpoint për Mega Layer Engine.
Integrohet me ocean-core service (shih docker-compose.yml).

Endpoints:
  GET  /health   → Health check
  GET  /status   → Engine status + statistika
  POST /process  → Proceso query përmes të gjitha shtresave
  GET  /demo     → Demo me queries të paracaktuara
"""

import logging
import time
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from mega_layer_engine import get_mega_layer_engine

# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ocean-core-api")

# ─────────────────────────────────────────────
app = FastAPI(
    title="Ocean Core — Mega Layer API",
    description=(
        "Mega Layer Engine me miliarda kombinime unike.\n\n"
        "Arkitektura: 7 Meta-Layers × 61 Binary × 256 Quantum × "
        "128 Fractal × 64 Neural × 5 Script Zones = ~4.3 Kuadrillion gjendje."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  SCHEMAS
# ─────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10_000, description="Query për t'u procesuar")
    include_vectors: bool = Field(False, description="Përfshi word vectors në përgjigje")
    include_summary: bool = Field(True, description="Përfshi summary human-readable")


class MultiScriptResult(BaseModel):
    zones_found: List[str]
    zone_diversity: float
    dominant_zone: str
    script_confidence: float
    cross_script_blend: bool
    transliteration_flags: List[str] = Field(default_factory=list)
    zone_histogram: Dict[str, int] = Field(default_factory=dict)
    algebraic_signature: str
    total_energy: float
    mod_7: int
    mod_61: int
    mod_97: int


class QueryResponse(BaseModel):
    # Identifikues
    unique_signature: str
    # Kombinime
    combinations_used: int
    theoretical_max: int
    coverage_pct: float
    # Shtresat
    meta_level: int
    meta_level_name: str
    temporal_hour: int
    dimensional_layer: str
    emotional_dimensions: List[str]
    letters_activated: int
    binary_layers_active: int
    neural_pathways_active: int
    fractal_depth: int
    quantum_state_id: int
    quantum_amplitude: float
    linguistic_patterns: int
    total_layers_engaged: int
    # Multi-Script
    multi_script: MultiScriptResult
    # Transformime
    complexity_score: float
    binary_transformation: float
    fractal_output: float
    # Opsionale
    summary: Optional[str] = None
    word_vectors: Optional[List[Any]] = None
    # Metadata
    processing_ms: float


class StatusResponse(BaseModel):
    status: str
    service: str
    version: str
    total_combinations_theoretical: int
    layers: Dict[str, int]
    script_zones: List[str]
    uptime_info: str


# ─────────────────────────────────────────────
#  STARTUP
# ─────────────────────────────────────────────

_startup_time = time.time()


@app.on_event("startup")
async def startup():
    """Pre-initialize engine singleton at startup."""
    logger.info("Ocean Core API duke u nisur...")
    engine = get_mega_layer_engine()
    logger.info(
        "MegaLayerEngine gati — %d kombinime teorike",
        engine.total_combinations,
    )


# ─────────────────────────────────────────────
#  ENDPOINTS
# ─────────────────────────────────────────────

@app.get("/health", tags=["System"])
async def health():
    """
    Health check — i detyrueshëm sipas konventave Clisonix.
    Kthehet gjithmonë 200 nëse shërbimi është live.
    """
    return {"status": "ok", "service": "ocean-core-mega-layer"}


@app.get("/status", response_model=StatusResponse, tags=["System"])
async def status():
    """
    Statistika të detajuara të engine dhe konfigurimi i shtresave.
    """
    engine = get_mega_layer_engine()
    uptime_sec = int(time.time() - _startup_time)
    h, rem = divmod(uptime_sec, 3600)
    m, s = divmod(rem, 60)

    return StatusResponse(
        status="running",
        service="ocean-core-mega-layer",
        version="1.0.0",
        total_combinations_theoretical=engine.total_combinations,
        layers={
            "meta_consciousness": 7,
            "alphabet_extended": 26,
            "binary_algebra": 61,
            "dimensional": 12,
            "temporal": 24,
            "emotional": 16,
            "linguistic_dna": 8,
            "neural_pathways": 64,
            "fractal_depth": 128,
            "quantum_states": 256,
            "script_zones": 5,
        },
        script_zones=["EN", "SQ", "GR", "AR", "ZH"],
        uptime_info=f"{h}h {m}m {s}s",
    )


@app.post("/process", response_model=QueryResponse, tags=["Engine"])
async def process_query(req: QueryRequest):
    """
    Proceso query përmes të gjitha shtresave të Mega Layer Engine.

    Merr tekstin, aktivizon të gjitha shtresat relevante, dhe kthen:
    - Numrin e kombinimeve të përdorura
    - Signaturën unike
    - Analizën Multi-Script (EN/SQ/GR/AR/ZH)
    - Të gjitha metrikat e shtresave
    """
    t0 = time.perf_counter()
    try:
        engine = get_mega_layer_engine()
        activation, results = engine.process_query(req.query)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Gabim në /process: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Gabim i brendshëm i engine")

    processing_ms = (time.perf_counter() - t0) * 1000
    ms_data = results["multi_script"]
    coverage = results["combinations_used"] / results["theoretical_max"] * 100

    summary = None
    if req.include_summary:
        summary = engine.get_layer_summary(activation, results)

    word_vectors = None
    if req.include_vectors:
        word_vectors = activation.multi_script_analysis.get("word_vectors", [])

    return QueryResponse(
        unique_signature=results["unique_signature"],
        combinations_used=results["combinations_used"],
        theoretical_max=results["theoretical_max"],
        coverage_pct=round(coverage, 8),
        meta_level=activation.meta_level.value,
        meta_level_name=activation.meta_level.name,
        temporal_hour=activation.temporal_layer.value,
        dimensional_layer=activation.dimensional_layer.name,
        emotional_dimensions=[e.name for e in activation.emotional_dimensions],
        letters_activated=activation.alphabet_activations["letters_activated"],
        binary_layers_active=len(activation.binary_layers_active),
        neural_pathways_active=results["neural_pathways_active"],
        fractal_depth=activation.fractal_depth,
        quantum_state_id=activation.quantum_state["state_id"],
        quantum_amplitude=results["quantum_amplitude"],
        linguistic_patterns=results["linguistic_patterns"],
        total_layers_engaged=results["total_layers_engaged"],
        multi_script=MultiScriptResult(
            zones_found=ms_data["zones_found"],
            zone_diversity=ms_data["zone_diversity"],
            dominant_zone=ms_data.get("dominant_zone", "UNK"),
            script_confidence=ms_data.get("script_confidence", 0.0),
            cross_script_blend=ms_data.get("cross_script_blend", False),
            transliteration_flags=ms_data.get("transliteration_flags", []),
            zone_histogram=ms_data.get("zone_histogram", {}),
            algebraic_signature=ms_data["algebraic_signature"],
            total_energy=ms_data["total_energy"],
            mod_7=ms_data["mod_signatures"]["mod_7"],
            mod_61=ms_data["mod_signatures"]["mod_61"],
            mod_97=ms_data["mod_signatures"]["mod_97"],
        ),
        complexity_score=results["complexity_score"],
        binary_transformation=results["binary_transformation"],
        fractal_output=results["fractal_output"],
        summary=summary,
        word_vectors=word_vectors,
        processing_ms=round(processing_ms, 3),
    )


@app.get("/demo", tags=["Engine"])
async def demo():
    """
    Demo i shpejtë me 5 queries të paracaktuara.
    Tregon fuqinë e engine-it pa pasur nevojë për POST request.
    """
    engine = get_mega_layer_engine()
    demo_queries = [
        "Sa është 5+7?",
        "What is the meaning of consciousness?",
        "Çfarë është dashuria?",
        "How can I create an AI system?",
        "Explain quantum entanglement in simple terms",
    ]

    results_out = []
    for q in demo_queries:
        t0 = time.perf_counter()
        try:
            activation, results = engine.process_query(q)
            ms = (time.perf_counter() - t0) * 1000
            results_out.append({
                "query": q,
                "combinations": results["combinations_used"],
                "coverage_pct": round(
                    results["combinations_used"] / results["theoretical_max"] * 100, 8
                ),
                "meta_level": activation.meta_level.name,
                "quantum_state": activation.quantum_state["state_id"],
                "fractal_depth": activation.fractal_depth,
                "algebraic_signature": results["multi_script"]["algebraic_signature"],
                "unique_signature": results["unique_signature"],
                "processing_ms": round(ms, 3),
                "status": "ok",
            })
        except Exception as e:
            results_out.append({"query": q, "status": "error", "detail": str(e)})

    total_combinations = sum(r.get("combinations", 0) for r in results_out)

    return {
        "engine": "ocean-core-mega-layer",
        "theoretical_max": engine.total_combinations,
        "queries_processed": len(demo_queries),
        "total_combinations_across_queries": total_combinations,
        "results": results_out,
    }


# ─────────────────────────────────────────────
#  ERROR HANDLERS
# ─────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Exception e pa-kapur: %s %s → %s", request.method, request.url, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Gabim i brendshëm i serverit", "path": str(request.url)},
    )


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_mega_layer:app",
        host="0.0.0.0",
        port=8600,
        reload=True,
        log_level="info",
    )
