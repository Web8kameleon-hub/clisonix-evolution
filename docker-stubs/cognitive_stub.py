#!/usr/bin/env python3
"""
Cognitive Signature Engine Stub - Docker container version
Exposes the CognitiveSignatureEngine as a REST API
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'ocean-core'))

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

app = FastAPI(
    title="Cognitive Signature Engine",
    description="Intelligence-Based Query Analysis - KIDS → STUDENT → RESEARCH → GENIUS",
    version="1.0.0"
)

# Cognitive Levels
class CognitiveLevel(str, Enum):
    KIDS = "KIDS"
    STUDENT = "STUDENT"
    RESEARCH = "RESEARCH"
    GENIUS = "GENIUS"

# Request/Response models
class AnalyzeRequest(BaseModel):
    query: str
    context: Optional[str] = None

class CognitiveSignatureResponse(BaseModel):
    level: CognitiveLevel
    complexity_score: float
    primary_domains: List[str]
    reasoning_depth: float
    abstraction_level: float
    confidence: float
    timestamp: str

# Domain keywords for analysis
DOMAIN_KEYWORDS = {
    "physics": ["quantum", "entropy", "relativity", "spacetime", "thermodynamics", "Planck", "Einstein"],
    "neuroscience": ["neural", "cortex", "consciousness", "synaptic", "hippocampus", "fMRI", "EEG"],
    "mathematics": ["theorem", "proof", "integral", "derivative", "topology", "Kolmogorov", "Fourier"],
    "philosophy": ["ontology", "epistemology", "phenomenology", "qualia", "metaphysics", "Kant"],
    "ai_ml": ["transformer", "gradient", "backpropagation", "embedding", "AGI", "neural network"]
}

def analyze_query(query: str) -> CognitiveSignatureResponse:
    """Analyze query and return cognitive signature"""
    q_lower = query.lower()
    word_count = len(query.split())
    
    # Calculate domain scores
    domain_scores = {}
    for domain, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in q_lower)
        if score > 0:
            domain_scores[domain] = score
    
    # Calculate complexity
    total_domain_hits = sum(domain_scores.values())
    complexity = min(1.0, (total_domain_hits * 0.15) + (word_count * 0.01))
    
    # Determine level
    if complexity < 0.20:
        level = CognitiveLevel.KIDS
    elif complexity < 0.45:
        level = CognitiveLevel.STUDENT
    elif complexity < 0.75:
        level = CognitiveLevel.RESEARCH
    else:
        level = CognitiveLevel.GENIUS
    
    # Get primary domains
    primary_domains = sorted(domain_scores.keys(), key=lambda d: domain_scores[d], reverse=True)[:3]
    
    return CognitiveSignatureResponse(
        level=level,
        complexity_score=round(complexity, 3),
        primary_domains=primary_domains if primary_domains else ["general"],
        reasoning_depth=min(1.0, complexity + 0.1),
        abstraction_level=min(1.0, complexity * 1.2),
        confidence=0.85 + (total_domain_hits * 0.02),
        timestamp=datetime.utcnow().isoformat()
    )

@app.get("/")
def root():
    return {
        "service": "Cognitive Signature Engine",
        "version": "1.0.0",
        "levels": [l.value for l in CognitiveLevel],
        "status": "operational"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "cognitive-engine",
        "levels_available": 4,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/analyze", response_model=CognitiveSignatureResponse)
def analyze(request: AnalyzeRequest):
    """Analyze a query and return its cognitive signature"""
    return analyze_query(request.query)

@app.get("/analyze/{query}")
def analyze_get(query: str):
    """GET version of analyze for simple testing"""
    return analyze_query(query)

@app.get("/levels")
def get_levels():
    """Get all cognitive levels and their thresholds"""
    return {
        "levels": [
            {"name": "KIDS", "threshold": "< 0.20", "description": "Simple, concrete explanations"},
            {"name": "STUDENT", "threshold": "0.20 - 0.45", "description": "Educational, structured"},
            {"name": "RESEARCH", "threshold": "0.45 - 0.75", "description": "Technical, precise"},
            {"name": "GENIUS", "threshold": ">= 0.75", "description": "Deep, mathematical, novel"}
        ]
    }

if __name__ == "__main__":
    PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8010
    print(f"🧠 Starting Cognitive Signature Engine on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
