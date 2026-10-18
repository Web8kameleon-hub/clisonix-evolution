# clx/gram/server.py
"""
Nano GRAM Server for CLX.
Lightweight, dependency-minimal, production-safe.

Features:
- POST /gram/json  → returns processed gram structure
- POST /gram/plot  → returns PNG visualization
- Designed to integrate with clx/gram/visualizer.py
"""

from __future__ import annotations

import io
import json
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union, Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from .visualizer import GramVisualizer
from .core import GRAMEngine

Number = Union[int, float]


# --------------------------------------------------------------------------- #
# Data Model
# --------------------------------------------------------------------------- #

@dataclass
class GramData:
    nodes: List[Union[str, int]]
    edges: List[Tuple[Union[str, int], Union[str, int]]]
    node_scores: Optional[Dict[Union[str, int], Number]] = None
    edge_scores: Optional[Dict[Tuple[Union[str, int], Union[str, int]], Number]] = None


# --------------------------------------------------------------------------- #
# Server Setup
# --------------------------------------------------------------------------- #

app = FastAPI(title="CLX Gram Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

viz = GramVisualizer()
engine = GRAMEngine()


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "clx-gram-server",
        "engine": "Growing Resonance Adaptive Mesh",
        "stats": engine.get_stats(),
    }


@app.post("/gram/nodes")
async def add_gram_node(payload: dict):
    if "content" not in payload:
        raise HTTPException(status_code=422, detail="content is required")
    node = engine.add_node(
        content=payload["content"],
        language=str(payload.get("language", "any")),
        tags=[str(tag) for tag in payload.get("tags", [])],
        resonance=float(payload.get("resonance", 0.5)),
        auto_connect=bool(payload.get("auto_connect", True)),
    )
    return {"ok": True, "node": node.to_dict(), "stats": engine.get_stats()}


@app.get("/gram/nodes/{node_id}")
async def get_gram_node(node_id: str):
    node = engine.get_node(node_id)
    if node is None:
        raise HTTPException(status_code=404, detail="node not found")
    return {"ok": True, "node": node.to_dict()}


@app.post("/gram/search")
async def search_gram(payload: dict):
    query = str(payload.get("query", "")).strip()
    if not query:
        raise HTTPException(status_code=422, detail="query is required")
    results = engine.search(
        query,
        max_depth=max(1, min(int(payload.get("max_depth", 3)), 12)),
        min_score=max(0.0, min(float(payload.get("min_score", 0.1)), 1.0)),
        language=payload.get("language"),
        tags=payload.get("tags"),
    )
    return {"ok": True, "results": [result.to_dict() for result in results], "count": len(results)}


@app.post("/gram/json")
async def gram_json(payload: dict):
    """
    Returns the gram structure back (useful for debugging or pipelines).
    """
    try:
        gram = GramData(
            nodes=payload.get("nodes", []),
            edges=[tuple(e) for e in payload.get("edges", [])],
            node_scores=payload.get("node_scores"),
            edge_scores=payload.get("edge_scores"),
        )
        return {"ok": True, "gram": gram.__dict__}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/gram/plot")
async def gram_plot(payload: dict):
    """
    Returns a PNG visualization of the gram graph.
    """
    try:
        gram = GramData(
            nodes=payload.get("nodes", []),
            edges=[tuple(e) for e in payload.get("edges", [])],
            node_scores=payload.get("node_scores"),
            edge_scores=payload.get("edge_scores"),
        )

        fig = viz.plot_graph(
            nodes=gram.nodes,
            edges=gram.edges,
            node_scores=gram.node_scores,
            edge_scores=gram.edge_scores,
            title=payload.get("title"),
            show=False,
        )

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)

        return Response(content=buf.read(), media_type="image/png")

    except Exception as e:
        return {"ok": False, "error": str(e)}


# --------------------------------------------------------------------------- #
# Optional: Sequence Score Plot
# --------------------------------------------------------------------------- #

@app.post("/gram/sequence")
async def gram_sequence(payload: dict):
    """
    Visualize token sequence scores (attention, activation, etc.).
    """
    try:
        tokens = payload["tokens"]
        scores = payload["scores"]

        fig = viz.plot_sequence_scores(
            tokens=tokens,
            scores=scores,
            title=payload.get("title"),
            show=False,
        )

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)

        return Response(content=buf.read(), media_type="image/png")

    except Exception as e:
        return {"ok": False, "error": str(e)}
