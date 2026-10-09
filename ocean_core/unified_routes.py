#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UNIFIED ROUTES - Ocean Core Internal API Integration
=====================================================
Lidh Ocean Core me të gjitha modulet interne:

1. Laboratories (23 labs)
2. Signal Managers (Cycle, Alignment, Proposal, DevOps, LoRa, Nanogrid)
3. Autolearning Engine
4. Cognitive Signature Engine
5. Feature Flags Manager
6. I18n Engine (72 gjuhë)
7. Knowledge Engine
8. Curiosity Algebra (Events, Cells, Signals)
9. Pipelines (Context Manager, Reasoning, Safety)
10. External APIs Manager

Port: 8030 (integrated in ocean_core_full.py)
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

logger = logging.getLogger("UnifiedRoutes")

# ═══════════════════════════════════════════════════════════════════
# IMPORT ALL MODULES (with graceful fallbacks)
# ═══════════════════════════════════════════════════════════════════

# 1. Laboratories - 23 labs
try:
    from laboratories import LaboratoryNetwork, get_laboratory_network
    LABS_AVAILABLE = True
    logger.info("✅ Laboratories loaded (23 labs)")
except ImportError as e:
    LABS_AVAILABLE = False
    logger.warning(f"⚠️ Laboratories not available: {e}")

# 2. Signal Managers
try:
    from mega_signal_integrator import (
        AlignmentSignalManager,
        CycleSignalManager,
        DevOpsSignalManager,
        LoRaSignalManager,
        NanogridSignalManager,
        ProposalSignalManager,
        get_mega_signal_integrator,
    )
    SIGNALS_AVAILABLE = True
    logger.info("✅ Signal Managers loaded")
except ImportError as e:
    SIGNALS_AVAILABLE = False
    logger.warning(f"⚠️ Signal Managers not available: {e}")

# 3. Autolearning Engine
try:
    from autolearning_engine import AutolearningEngine, get_autolearning_engine
    AUTOLEARNING_AVAILABLE = True
    logger.info("✅ Autolearning Engine loaded")
except ImportError as e:
    AUTOLEARNING_AVAILABLE = False
    logger.warning(f"⚠️ Autolearning Engine not available: {e}")

# 4. Cognitive Signature Engine
try:
    from cognitive_signature_engine import CognitiveSignatureEngine, get_cognitive_engine
    COGNITIVE_AVAILABLE = True
    logger.info("✅ Cognitive Signature Engine loaded")
except ImportError as e:
    COGNITIVE_AVAILABLE = False
    logger.warning(f"⚠️ Cognitive Signature Engine not available: {e}")

# 5. Feature Flags Manager
try:
    from feature_flags import FeatureFlagManager, get_feature_manager
    FEATURES_AVAILABLE = True
    logger.info("✅ Feature Flags Manager loaded")
except ImportError as e:
    FEATURES_AVAILABLE = False
    logger.warning(f"⚠️ Feature Flags not available: {e}")

# 6. I18n Engine - 72 languages
try:
    from curiosity_algebra.i18n_engine import I18nEngine, get_i18n_engine
    I18N_AVAILABLE = True
    logger.info("✅ I18n Engine loaded (72 languages)")
except ImportError as e:
    I18N_AVAILABLE = False
    logger.warning(f"⚠️ I18n Engine not available: {e}")

# 7. Knowledge Engine
try:
    from knowledge_engine import KnowledgeEngine, get_knowledge_engine
    KNOWLEDGE_ENGINE_AVAILABLE = True
    logger.info("✅ Knowledge Engine loaded")
except ImportError as e:
    KNOWLEDGE_ENGINE_AVAILABLE = False
    logger.warning(f"⚠️ Knowledge Engine not available: {e}")

# 8. Curiosity Algebra
try:
    from curiosity_algebra.cell_registry import get_cell_registry
    from curiosity_algebra.curiosity_orchestrator import get_curiosity_orchestrator
    from curiosity_algebra.event_bus import get_event_bus
    from curiosity_algebra.real_learning_engine import get_real_learning
    from curiosity_algebra.signal_integrator import get_signal_integrator
    CURIOSITY_ALGEBRA_AVAILABLE = True
    logger.info("✅ Curiosity Algebra loaded")
except ImportError as e:
    CURIOSITY_ALGEBRA_AVAILABLE = False
    logger.warning(f"⚠️ Curiosity Algebra not available: {e}")

# 9. Pipelines
try:
    from pipelines.context_manager import ContextManager
    from pipelines.reasoning import ReasoningPipeline
    from pipelines.safety import SafetyFilter
    PIPELINES_AVAILABLE = True
    logger.info("✅ Pipelines loaded")
except ImportError as e:
    PIPELINES_AVAILABLE = False
    logger.warning(f"⚠️ Pipelines not available: {e}")

# 10. External APIs Manager
try:
    from external_apis import ExternalAPIsManager, get_external_apis
    EXTERNAL_APIS_AVAILABLE = True
    logger.info("✅ External APIs Manager loaded")
except ImportError as e:
    EXTERNAL_APIS_AVAILABLE = False
    logger.warning(f"⚠️ External APIs not available: {e}")

# 11. Genesis Engine - Self-Generating AI
try:
    from evolution_loop import EvolutionLoop, get_evolution_loop
    from genesis_engine import GenesisEngine, get_genesis_engine
    from self_synthesis import SelfSynthesisEngine, get_self_synthesis_engine
    GENESIS_AVAILABLE = True
    logger.info("✅ Genesis Engine loaded (Self-Generating AI)")
except ImportError as e:
    GENESIS_AVAILABLE = False
    logger.warning(f"⚠️ Genesis Engine not available: {e}")

# ═══════════════════════════════════════════════════════════════════
# CREATE ROUTERS
# ═══════════════════════════════════════════════════════════════════

# Main unified router
unified_router = APIRouter(prefix="/api/v1", tags=["Unified Internal APIs"])

# Sub-routers
labs_router = APIRouter(prefix="/labs", tags=["Laboratories"])
signals_router = APIRouter(prefix="/signals", tags=["Signal Managers"])
learning_router = APIRouter(prefix="/learning", tags=["Autolearning"])
cognitive_router = APIRouter(prefix="/cognitive", tags=["Cognitive Signatures"])
features_router = APIRouter(prefix="/features", tags=["Feature Flags"])
i18n_router = APIRouter(prefix="/i18n", tags=["Internationalization"])
knowledge_router = APIRouter(prefix="/knowledge-engine", tags=["Knowledge Engine"])
curiosity_router = APIRouter(prefix="/curiosity", tags=["Curiosity Algebra"])
pipelines_router = APIRouter(prefix="/pipelines", tags=["Pipelines"])
external_router = APIRouter(prefix="/external", tags=["External APIs"])
genesis_router = APIRouter(prefix="/genesis", tags=["Genesis Self-Generating AI"])


# ═══════════════════════════════════════════════════════════════════
# REQUEST/RESPONSE MODELS
# ═══════════════════════════════════════════════════════════════════

class SignalRequest(BaseModel):
    source: str
    signal_type: str = "metric"
    payload: Dict[str, Any] = {}
    confidence: float = 1.0

class LearningRequest(BaseModel):
    input_text: str
    feedback: Optional[str] = None
    category: Optional[str] = None

class CognitiveRequest(BaseModel):
    text: str
    context: Optional[str] = None

class FeatureFlagRequest(BaseModel):
    flag_name: str
    enabled: bool
    metadata: Dict[str, Any] = {}

class TranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str = "en"


# ═══════════════════════════════════════════════════════════════════
# 1. LABORATORIES ROUTES (23 labs)
# ═══════════════════════════════════════════════════════════════════

@labs_router.get("/")
async def list_laboratories():
    """Lista e të gjitha laboratorëve"""
    if not LABS_AVAILABLE:
        raise HTTPException(503, "Laboratories module not available")
    
    network = get_laboratory_network()
    return network.get_all_labs_summary()


@labs_router.get("/stats")
async def lab_network_stats():
    """Statistikat e rrjetit të laboratorëve"""
    if not LABS_AVAILABLE:
        raise HTTPException(503, "Laboratories module not available")
    
    network = get_laboratory_network()
    return network.get_network_stats()


@labs_router.get("/types")
async def lab_types():
    """Llojet e laboratorëve"""
    if not LABS_AVAILABLE:
        raise HTTPException(503, "Laboratories module not available")
    
    network = get_laboratory_network()
    return {
        "types": network.get_lab_types(),
        "count": len(network.get_lab_types())
    }


@labs_router.get("/{lab_id}")
async def get_laboratory(lab_id: str):
    """Merr laboratorin sipas ID"""
    if not LABS_AVAILABLE:
        raise HTTPException(503, "Laboratories module not available")
    
    network = get_laboratory_network()
    lab = network.get_lab_by_id(lab_id)
    if not lab:
        raise HTTPException(404, f"Laboratory {lab_id} not found")
    
    return lab.to_dict()


@labs_router.get("/type/{lab_type}")
async def get_labs_by_type(lab_type: str):
    """Merr laboratorët sipas tipit"""
    if not LABS_AVAILABLE:
        raise HTTPException(503, "Laboratories module not available")
    
    network = get_laboratory_network()
    labs = network.get_labs_by_type(lab_type)
    return {
        "type": lab_type,
        "count": len(labs),
        "laboratories": [lab.to_dict() for lab in labs]
    }


@labs_router.get("/location/{location}")
async def get_labs_by_location(location: str):
    """Merr laboratorët sipas vendndodhjes"""
    if not LABS_AVAILABLE:
        raise HTTPException(503, "Laboratories module not available")
    
    network = get_laboratory_network()
    labs = network.get_labs_by_location(location)
    return {
        "location": location,
        "count": len(labs),
        "laboratories": [lab.to_dict() for lab in labs]
    }


@labs_router.get("/search/{keyword}")
async def search_labs(keyword: str):
    """Kërko laboratorë sipas funksionit"""
    if not LABS_AVAILABLE:
        raise HTTPException(503, "Laboratories module not available")
    
    network = get_laboratory_network()
    labs = network.get_labs_by_function_keyword(keyword)
    return {
        "keyword": keyword,
        "count": len(labs),
        "laboratories": [lab.to_dict() for lab in labs]
    }


# ═══════════════════════════════════════════════════════════════════
# 2. SIGNAL MANAGERS ROUTES
# ═══════════════════════════════════════════════════════════════════

@signals_router.get("/")
async def list_signal_managers():
    """Lista e të gjithë menaxherëve të sinjaleve"""
    if not SIGNALS_AVAILABLE:
        raise HTTPException(503, "Signal Managers not available")
    
    integrator = get_mega_signal_integrator()
    return {
        "managers": [
            "CycleSignalManager",
            "AlignmentSignalManager",
            "ProposalSignalManager",
            "DevOpsSignalManager",
            "LoRaSignalManager",
            "NanogridSignalManager"
        ],
        "status": "active",
        "total_signals": integrator.get_total_signals() if hasattr(integrator, 'get_total_signals') else 0
    }


@signals_router.post("/emit")
async def emit_signal(req: SignalRequest):
    """Emito një sinjal të ri"""
    if not SIGNALS_AVAILABLE:
        raise HTTPException(503, "Signal Managers not available")
    
    integrator = get_mega_signal_integrator()
    result = integrator.emit(
        source=req.source,
        signal_type=req.signal_type,
        payload=req.payload,
        confidence=req.confidence
    )
    return {
        "status": "emitted",
        "signal_id": result.get("signal_id") if isinstance(result, dict) else str(result),
        "timestamp": datetime.now().isoformat()
    }


@signals_router.get("/stats")
async def signal_stats():
    """Statistikat e sinjaleve"""
    if not SIGNALS_AVAILABLE:
        raise HTTPException(503, "Signal Managers not available")
    
    integrator = get_mega_signal_integrator()
    return integrator.get_stats() if hasattr(integrator, 'get_stats') else {"status": "active"}


@signals_router.get("/cycles")
async def get_cycle_signals():
    """Sinjalet e cikleve"""
    if not SIGNALS_AVAILABLE:
        raise HTTPException(503, "Signal Managers not available")
    
    return {
        "manager": "CycleSignalManager",
        "status": "active",
        "description": "Menaxhon sinjalet e cikleve të procesit"
    }


@signals_router.get("/alignments")
async def get_alignment_signals():
    """Sinjalet e alignmentit"""
    if not SIGNALS_AVAILABLE:
        raise HTTPException(503, "Signal Managers not available")
    
    return {
        "manager": "AlignmentSignalManager",
        "status": "active",
        "description": "Menaxhon sinjalet e alignmentit të sistemeve"
    }


@signals_router.get("/devops")
async def get_devops_signals():
    """Sinjalet DevOps"""
    if not SIGNALS_AVAILABLE:
        raise HTTPException(503, "Signal Managers not available")
    
    return {
        "manager": "DevOpsSignalManager",
        "status": "active",
        "description": "Menaxhon sinjalet DevOps (CI/CD, deployments)"
    }


@signals_router.get("/lora")
async def get_lora_signals():
    """Sinjalet LoRa"""
    if not SIGNALS_AVAILABLE:
        raise HTTPException(503, "Signal Managers not available")
    
    return {
        "manager": "LoRaSignalManager",
        "status": "active",
        "description": "Menaxhon sinjalet LoRa (IoT, sensors)"
    }


@signals_router.get("/nanogrid")
async def get_nanogrid_signals():
    """Sinjalet Nanogrid"""
    if not SIGNALS_AVAILABLE:
        raise HTTPException(503, "Signal Managers not available")
    
    return {
        "manager": "NanogridSignalManager",
        "status": "active",
        "description": "Menaxhon sinjalet Nanogrid (micro-processing)"
    }


# ═══════════════════════════════════════════════════════════════════
# 3. AUTOLEARNING ENGINE ROUTES
# ═══════════════════════════════════════════════════════════════════

@learning_router.get("/")
async def learning_status():
    """Statusi i Autolearning Engine"""
    if not AUTOLEARNING_AVAILABLE:
        raise HTTPException(503, "Autolearning Engine not available")
    
    engine = get_autolearning_engine()
    return {
        "status": "active",
        "engine": "AutolearningEngine",
        "stats": engine.get_stats() if hasattr(engine, 'get_stats') else {}
    }


@learning_router.post("/learn")
async def learn_from_input(req: LearningRequest):
    """Mëso nga inputi"""
    if not AUTOLEARNING_AVAILABLE:
        raise HTTPException(503, "Autolearning Engine not available")
    
    engine = get_autolearning_engine()
    result = engine.learn(
        input_text=req.input_text,
        feedback=req.feedback,
        category=req.category
    ) if hasattr(engine, 'learn') else {"status": "learning_queued"}
    
    return {
        "status": "learned",
        "result": result,
        "timestamp": datetime.now().isoformat()
    }


@learning_router.get("/patterns")
async def get_learned_patterns():
    """Merr pattern-et e mësuara"""
    if not AUTOLEARNING_AVAILABLE:
        raise HTTPException(503, "Autolearning Engine not available")
    
    engine = get_autolearning_engine()
    return engine.get_patterns() if hasattr(engine, 'get_patterns') else {"patterns": []}


@learning_router.get("/history")
async def get_learning_history(limit: int = Query(100, ge=1, le=1000)):
    """Historia e mësimit"""
    if not AUTOLEARNING_AVAILABLE:
        raise HTTPException(503, "Autolearning Engine not available")
    
    engine = get_autolearning_engine()
    return engine.get_history(limit) if hasattr(engine, 'get_history') else {"history": []}


# ═══════════════════════════════════════════════════════════════════
# 4. COGNITIVE SIGNATURE ENGINE ROUTES
# ═══════════════════════════════════════════════════════════════════

@cognitive_router.get("/")
async def cognitive_status():
    """Statusi i Cognitive Signature Engine"""
    if not COGNITIVE_AVAILABLE:
        raise HTTPException(503, "Cognitive Signature Engine not available")
    
    engine = get_cognitive_engine()
    return {
        "status": "active",
        "engine": "CognitiveSignatureEngine",
        "capabilities": ["signature_generation", "pattern_recognition", "cognitive_analysis"]
    }


@cognitive_router.post("/analyze")
async def analyze_cognitive(req: CognitiveRequest):
    """Analizo tekstin kognitivisht"""
    if not COGNITIVE_AVAILABLE:
        raise HTTPException(503, "Cognitive Signature Engine not available")
    
    engine = get_cognitive_engine()
    result = engine.analyze(req.text, req.context) if hasattr(engine, 'analyze') else {}
    
    return {
        "status": "analyzed",
        "result": result,
        "timestamp": datetime.now().isoformat()
    }


@cognitive_router.post("/signature")
async def generate_signature(req: CognitiveRequest):
    """Gjenero nënshkrim kognitiv"""
    if not COGNITIVE_AVAILABLE:
        raise HTTPException(503, "Cognitive Signature Engine not available")
    
    engine = get_cognitive_engine()
    signature = engine.generate_signature(req.text) if hasattr(engine, 'generate_signature') else ""
    
    return {
        "signature": signature,
        "text_length": len(req.text),
        "timestamp": datetime.now().isoformat()
    }


# ═══════════════════════════════════════════════════════════════════
# 5. FEATURE FLAGS ROUTES
# ═══════════════════════════════════════════════════════════════════

@features_router.get("/")
async def list_features():
    """Lista e të gjitha feature flags"""
    if not FEATURES_AVAILABLE:
        raise HTTPException(503, "Feature Flags Manager not available")
    
    manager = get_feature_manager()
    return {
        "flags": manager.get_all() if hasattr(manager, 'get_all') else {},
        "count": len(manager.get_all()) if hasattr(manager, 'get_all') else 0
    }


@features_router.get("/{flag_name}")
async def get_feature(flag_name: str):
    """Merr një feature flag"""
    if not FEATURES_AVAILABLE:
        raise HTTPException(503, "Feature Flags Manager not available")
    
    manager = get_feature_manager()
    flag = manager.get(flag_name) if hasattr(manager, 'get') else None
    if flag is None:
        raise HTTPException(404, f"Feature flag '{flag_name}' not found")
    
    return flag


@features_router.post("/")
async def set_feature(req: FeatureFlagRequest):
    """Vendos një feature flag"""
    if not FEATURES_AVAILABLE:
        raise HTTPException(503, "Feature Flags Manager not available")
    
    manager = get_feature_manager()
    manager.set(req.flag_name, req.enabled, req.metadata) if hasattr(manager, 'set') else None
    
    return {
        "status": "set",
        "flag": req.flag_name,
        "enabled": req.enabled
    }


@features_router.get("/check/{flag_name}")
async def check_feature_enabled(flag_name: str):
    """Kontrollo nëse feature është aktivizuar"""
    if not FEATURES_AVAILABLE:
        raise HTTPException(503, "Feature Flags Manager not available")
    
    manager = get_feature_manager()
    enabled = manager.is_enabled(flag_name) if hasattr(manager, 'is_enabled') else False
    
    return {
        "flag": flag_name,
        "enabled": enabled
    }


# ═══════════════════════════════════════════════════════════════════
# 6. I18N ENGINE ROUTES (72 LANGUAGES)
# ═══════════════════════════════════════════════════════════════════

@i18n_router.get("/")
async def i18n_status():
    """Statusi i I18n Engine"""
    if not I18N_AVAILABLE:
        raise HTTPException(503, "I18n Engine not available")
    
    engine = get_i18n_engine()
    return {
        "status": "active",
        "engine": "I18nEngine",
        "supported_languages": 72,
        "languages": engine.get_supported_languages() if hasattr(engine, 'get_supported_languages') else []
    }


@i18n_router.get("/languages")
async def list_languages():
    """Lista e gjuhëve të mbështetura"""
    if not I18N_AVAILABLE:
        raise HTTPException(503, "I18n Engine not available")
    
    engine = get_i18n_engine()
    return {
        "languages": engine.get_supported_languages() if hasattr(engine, 'get_supported_languages') else [],
        "total": 72
    }


@i18n_router.post("/translate")
async def translate_text(req: TranslationRequest):
    """Përkthe tekst"""
    if not I18N_AVAILABLE:
        raise HTTPException(503, "I18n Engine not available")
    
    engine = get_i18n_engine()
    result = engine.translate(
        text=req.text,
        source_lang=req.source_lang,
        target_lang=req.target_lang
    ) if hasattr(engine, 'translate') else req.text
    
    return {
        "original": req.text,
        "translated": result,
        "source_lang": req.source_lang,
        "target_lang": req.target_lang
    }


@i18n_router.post("/detect")
async def detect_language(text: str = Query(..., description="Teksti për detektim")):
    """Detekto gjuhën"""
    if not I18N_AVAILABLE:
        raise HTTPException(503, "I18n Engine not available")
    
    engine = get_i18n_engine()
    result = engine.detect(text) if hasattr(engine, 'detect') else {"language": "en", "confidence": 0.5}
    
    return result


# ═══════════════════════════════════════════════════════════════════
# 7. KNOWLEDGE ENGINE ROUTES
# ═══════════════════════════════════════════════════════════════════

@knowledge_router.get("/")
async def knowledge_engine_status():
    """Statusi i Knowledge Engine"""
    if not KNOWLEDGE_ENGINE_AVAILABLE:
        raise HTTPException(503, "Knowledge Engine not available")
    
    engine = get_knowledge_engine()
    return {
        "status": "active",
        "engine": "KnowledgeEngine",
        "stats": engine.get_stats() if hasattr(engine, 'get_stats') else {}
    }


@knowledge_router.get("/query")
async def query_knowledge(q: str = Query(..., description="Query string")):
    """Kërko në bazën e njohurisë"""
    if not KNOWLEDGE_ENGINE_AVAILABLE:
        raise HTTPException(503, "Knowledge Engine not available")
    
    engine = get_knowledge_engine()
    results = engine.query(q) if hasattr(engine, 'query') else []
    
    return {
        "query": q,
        "results": results,
        "count": len(results) if isinstance(results, list) else 1
    }


@knowledge_router.get("/categories")
async def knowledge_categories():
    """Kategoritë e njohurisë"""
    if not KNOWLEDGE_ENGINE_AVAILABLE:
        raise HTTPException(503, "Knowledge Engine not available")
    
    engine = get_knowledge_engine()
    return {
        "categories": engine.get_categories() if hasattr(engine, 'get_categories') else []
    }


# ═══════════════════════════════════════════════════════════════════
# 8. CURIOSITY ALGEBRA ROUTES
# ═══════════════════════════════════════════════════════════════════

@curiosity_router.get("/")
async def curiosity_status():
    """Statusi i Curiosity Algebra"""
    if not CURIOSITY_ALGEBRA_AVAILABLE:
        raise HTTPException(503, "Curiosity Algebra not available")
    
    return {
        "status": "active",
        "components": [
            "EventBus",
            "CellRegistry",
            "SignalIntegrator",
            "CuriosityOrchestrator",
            "RealLearningEngine"
        ]
    }


@curiosity_router.get("/events")
async def get_curiosity_events(limit: int = Query(100, ge=1, le=1000)):
    """Merr ngjarjet e fundit"""
    if not CURIOSITY_ALGEBRA_AVAILABLE:
        raise HTTPException(503, "Curiosity Algebra not available")
    
    bus = get_event_bus()
    events = bus.get_recent(limit) if hasattr(bus, 'get_recent') else []
    
    return {
        "events": [e.to_dict() if hasattr(e, 'to_dict') else e for e in events],
        "count": len(events)
    }


@curiosity_router.get("/cells")
async def get_curiosity_cells():
    """Merr qelizat"""
    if not CURIOSITY_ALGEBRA_AVAILABLE:
        raise HTTPException(503, "Curiosity Algebra not available")
    
    registry = get_cell_registry()
    cells = registry.get_all() if hasattr(registry, 'get_all') else []
    
    return {
        "cells": [c.to_dict() if hasattr(c, 'to_dict') else c for c in cells],
        "count": len(cells)
    }


@curiosity_router.get("/orchestrator")
async def get_orchestrator_status():
    """Statusi i orkestuesit"""
    if not CURIOSITY_ALGEBRA_AVAILABLE:
        raise HTTPException(503, "Curiosity Algebra not available")
    
    orchestrator = get_curiosity_orchestrator()
    return orchestrator.get_status() if hasattr(orchestrator, 'get_status') else {"status": "active"}


@curiosity_router.get("/real-learning")
async def get_real_learning_status():
    """Statusi i Real Learning Engine"""
    if not CURIOSITY_ALGEBRA_AVAILABLE:
        raise HTTPException(503, "Curiosity Algebra not available")
    
    learning = get_real_learning()
    return learning.get_status() if hasattr(learning, 'get_status') else {"status": "active"}


# ═══════════════════════════════════════════════════════════════════
# 9. PIPELINES ROUTES
# ═══════════════════════════════════════════════════════════════════

@pipelines_router.get("/")
async def pipelines_status():
    """Statusi i pipeline-ve"""
    if not PIPELINES_AVAILABLE:
        raise HTTPException(503, "Pipelines not available")
    
    return {
        "status": "active",
        "pipelines": [
            "ContextManager",
            "ReasoningPipeline",
            "SafetyFilter"
        ]
    }


@pipelines_router.get("/context")
async def get_context_status():
    """Statusi i Context Manager"""
    if not PIPELINES_AVAILABLE:
        raise HTTPException(503, "Pipelines not available")
    
    return {
        "pipeline": "ContextManager",
        "status": "active",
        "description": "Menaxhon kontekstin e bisedave"
    }


@pipelines_router.get("/reasoning")
async def get_reasoning_status():
    """Statusi i Reasoning Pipeline"""
    if not PIPELINES_AVAILABLE:
        raise HTTPException(503, "Pipelines not available")
    
    return {
        "pipeline": "ReasoningPipeline",
        "status": "active",
        "description": "Pipeline për arsyetim logjik"
    }


@pipelines_router.get("/safety")
async def get_safety_status():
    """Statusi i Safety Filter"""
    if not PIPELINES_AVAILABLE:
        raise HTTPException(503, "Pipelines not available")
    
    return {
        "pipeline": "SafetyFilter",
        "status": "active",
        "description": "Filtron përmbajtjen për siguri"
    }


# ═══════════════════════════════════════════════════════════════════
# 10. EXTERNAL APIS ROUTES
# ═══════════════════════════════════════════════════════════════════

@external_router.get("/")
async def external_apis_status():
    """Statusi i External APIs"""
    if not EXTERNAL_APIS_AVAILABLE:
        raise HTTPException(503, "External APIs Manager not available")
    
    manager = get_external_apis()
    return {
        "status": "active",
        "manager": "ExternalAPIsManager",
        "apis": manager.list_apis() if hasattr(manager, 'list_apis') else []
    }


@external_router.get("/available")
async def list_external_apis():
    """Lista e API-ve të jashtme të disponueshme"""
    if not EXTERNAL_APIS_AVAILABLE:
        raise HTTPException(503, "External APIs Manager not available")
    
    manager = get_external_apis()
    return {
        "apis": manager.list_apis() if hasattr(manager, 'list_apis') else [
            "arxiv", "wikipedia", "pubmed", "nasa", "weather"
        ]
    }


# ═══════════════════════════════════════════════════════════════════
# GENESIS - SELF-GENERATING AI ROUTES
# Vetë-Gjenerues i Inteligjencës Artificiale
# ═══════════════════════════════════════════════════════════════════

# Genesis Engine instance (lazy initialization)
_genesis_engine = None
_evolution_loop = None
_self_synthesis = None

# Genesis singletons - use module-level imports directly
# (get_genesis_engine, get_evolution_loop, get_self_synthesis_engine are imported above)


@genesis_router.get("/")
async def genesis_status():
    """Statusi i Genesis Engine - Self-Generating AI"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    engine = get_genesis_engine()
    loop = get_evolution_loop()
    synthesis = get_self_synthesis_engine()
    
    # Get loop state
    loop_running = False
    loop_paused = False
    loop_generations = 0
    if loop:
        from evolution_loop import LoopState
        loop_running = loop.state == LoopState.RUNNING
        loop_paused = loop.state == LoopState.PAUSED
        loop_generations = loop.metrics.total_cycles
    
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "engine": {
            "population_size": len(engine.gene_pool),
            "total_evolved": engine.evolution_history[-1].population_size if engine.evolution_history else 0,
            "total_synthesized": engine.metrics.total_synthesized if hasattr(engine, 'metrics') else 0
        },
        "evolution_loop": {
            "running": loop_running,
            "paused": loop_paused,
            "generations": loop_generations
        },
        "synthesis": {
            "concepts_learned": len(synthesis.concepts),
            "goals_discovered": len(synthesis.discovered_goals),
            "patterns_learned": len(synthesis.patterns)
        },
        "capabilities": [
            "code_synthesis",
            "genetic_mutation",
            "crossover_breeding",
            "autonomous_evolution",
            "goal_discovery",
            "meta_learning",
            "pattern_mining"
        ]
    }


@genesis_router.post("/synthesize")
async def synthesize_gene(request: dict):
    """Sintetizo kod të ri nga templates"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    engine = get_genesis_engine()
    
    purpose = request.get("description", "Auto-generated function")
    template_type = request.get("type", "filter")
    
    gene = engine.synthesize(
        purpose=purpose,
        template_type=template_type
    )
    
    return {
        "success": True,
        "gene": {
            "id": gene.gene_id,
            "name": gene.name,
            "generation": gene.generation,
            "fitness": gene.fitness,
            "code_preview": gene.code[:200] + "..." if len(gene.code) > 200 else gene.code
        }
    }


@genesis_router.post("/mutate/{gene_id}")
async def mutate_gene(gene_id: str):
    """Apliko mutacion në një gen ekzistues"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    engine = get_genesis_engine()
    
    if gene_id not in engine.gene_pool:
        raise HTTPException(404, f"Gene {gene_id} not found")
    
    mutated = engine.mutate(gene_id)
    
    if not mutated:
        raise HTTPException(500, "Mutation failed")
    
    return {
        "success": True,
        "original_id": gene_id,
        "mutated": {
            "id": mutated.gene_id,
            "name": mutated.name,
            "generation": mutated.generation,
            "fitness": mutated.fitness
        }
    }


@genesis_router.post("/mutate")
async def mutate_gene_body(request: dict):
    """Apliko mutacion në një gen (via body)"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    gene_id = request.get("gene_id")
    if not gene_id:
        raise HTTPException(400, "gene_id is required")
    
    engine = get_genesis_engine()
    
    if gene_id not in engine.gene_pool:
        raise HTTPException(404, f"Gene {gene_id} not found")
    
    mutated = engine.mutate(gene_id)
    
    if not mutated:
        raise HTTPException(500, "Mutation failed")
    
    return {
        "success": True,
        "original_id": gene_id,
        "mutated": {
            "id": mutated.gene_id,
            "name": mutated.name,
            "generation": mutated.generation,
            "fitness": mutated.fitness
        }
    }


@genesis_router.post("/crossover")
async def crossover_genes(request: dict):
    """Krijo gen të ri nga kryqëzimi i dy gjeneve"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    engine = get_genesis_engine()
    parent1_id = request.get("parent1")
    parent2_id = request.get("parent2")
    
    if not parent1_id or not parent2_id:
        raise HTTPException(400, "Both parent1 and parent2 IDs required")
    
    # Check parents exist
    if parent1_id not in engine.gene_pool or parent2_id not in engine.gene_pool:
        raise HTTPException(404, "One or both parents not found")
    
    offspring = engine.crossover(parent1_id, parent2_id)
    
    if not offspring:
        raise HTTPException(500, "Crossover failed")
    
    return {
        "success": True,
        "parent1": parent1_id,
        "parent2": parent2_id,
        "offspring": {
            "id": offspring.gene_id,
            "name": offspring.name,
            "generation": offspring.generation,
            "fitness": offspring.fitness
        }
    }


@genesis_router.post("/evolve")
async def trigger_evolution(request: dict = None):
    """Nis një cikël evolucioni"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    request = request or {}
    engine = get_genesis_engine()
    
    generations = request.get("generations", 1)
    
    results = []
    for _ in range(generations):
        cycle = engine.evolve()
        results.append({
            "generation": cycle.generation,
            "population_size": cycle.population_size,
            "survivors": cycle.survivors,
            "best_fitness": cycle.best_fitness,
            "avg_fitness": cycle.avg_fitness,
            "mutations": cycle.mutations_applied,
            "crossovers": cycle.crossovers
        })
    
    return {
        "success": True,
        "cycles_completed": len(results),
        "results": results,
        "population_size": len(engine.gene_pool)
    }


@genesis_router.get("/genes")
async def list_genes(limit: int = 50, min_fitness: float = 0.0):
    """Lista e të gjitha gjeneve në pool"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    engine = get_genesis_engine()
    
    genes = [g for g in engine.gene_pool.values() if g.fitness >= min_fitness]
    genes = sorted(genes, key=lambda x: x.fitness, reverse=True)[:limit]
    
    return {
        "total_in_pool": len(engine.gene_pool),
        "returned": len(genes),
        "genes": [
            {
                "id": g.gene_id,
                "name": g.name,
                "purpose": g.purpose,
                "generation": g.generation,
                "fitness": g.fitness,
                "size": len(g.code),
                "parents": len(g.parent_ids)
            }
            for g in genes
        ]
    }


@genesis_router.get("/gene/{gene_id}")
async def get_gene_details(gene_id: str):
    """Detajet e plota të një gjeni"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    engine = get_genesis_engine()
    
    if gene_id in engine.gene_pool:
        g = engine.gene_pool[gene_id]
        return {
            "id": g.gene_id,
            "name": g.name,
            "purpose": g.purpose,
            "code": g.code,
            "fitness": g.fitness,
            "generation": g.generation,
            "parent_ids": g.parent_ids,
            "mutations": g.mutations,
            "created_at": g.created_at.isoformat()
        }
    
    raise HTTPException(404, f"Gene {gene_id} not found")


@genesis_router.post("/loop/start")
async def start_evolution_loop():
    """Nis loop-in e evolucionit autonom"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    loop = get_evolution_loop()
    from evolution_loop import LoopState
    
    if loop.state == LoopState.RUNNING:
        return {"status": "already_running", "generations": loop.metrics.total_cycles}
    
    await loop.start()
    
    return {
        "status": "started",
        "message": "Evolution loop is now running autonomously"
    }


@genesis_router.post("/loop/stop")
async def stop_evolution_loop():
    """Ndalo loop-in e evolucionit"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    loop = get_evolution_loop()
    from evolution_loop import LoopState
    
    if loop.state == LoopState.STOPPED:
        return {"status": "not_running"}
    
    await loop.stop()
    
    return {
        "status": "stopped",
        "generations_completed": loop.metrics.total_cycles,
        "total_evolved": loop.metrics.total_mutations + loop.metrics.total_crossovers
    }


@genesis_router.post("/loop/pause")
async def pause_evolution_loop():
    """Pauzë evolucioni"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    loop = get_evolution_loop()
    loop.pause()
    
    return {"status": "paused"}


@genesis_router.post("/loop/resume")
async def resume_evolution_loop():
    """Rifillo evolucionin"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    loop = get_evolution_loop()
    loop.resume()
    
    return {"status": "resumed"}


@genesis_router.get("/loop/status")
async def evolution_loop_status():
    """Statusi i evolution loop"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    loop = get_evolution_loop()
    from evolution_loop import LoopState
    
    return {
        "running": loop.state == LoopState.RUNNING,
        "paused": loop.state == LoopState.PAUSED,
        "state": loop.state.value,
        "metrics": {
            "total_cycles": loop.metrics.total_cycles,
            "total_mutations": loop.metrics.total_mutations,
            "total_crossovers": loop.metrics.total_crossovers,
            "total_synthesized": loop.metrics.total_synthesized,
            "total_pruned": loop.metrics.total_pruned,
            "best_fitness_ever": loop.metrics.best_fitness_ever,
            "uptime_seconds": loop.metrics.uptime_seconds
        }
    }


@genesis_router.post("/observe")
async def add_observation(request: dict):
    """Shto një observim për meta-learning"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    synthesis = get_self_synthesis_engine()
    
    observation = request.get("observation", {})
    synthesis.observe(observation)
    
    return {
        "success": True,
        "buffer_size": len(synthesis.observation_buffer),
        "patterns_discovered": len(synthesis.learned_patterns)
    }


@genesis_router.get("/goals")
async def list_discovered_goals():
    """Lista e qëllimeve të zbuluara automatikisht"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    synthesis = get_self_synthesis_engine()
    
    return {
        "total": len(synthesis.discovered_goals),
        "goals": [
            {
                "id": g.id,
                "description": g.description,
                "priority": g.priority,
                "status": g.status,
                "source": g.source,
                "discovered_at": g.discovered_at.isoformat()
            }
            for g in synthesis.discovered_goals
        ]
    }


@genesis_router.get("/patterns")
async def list_learned_patterns():
    """Lista e pattern-eve të mësuara"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    synthesis = get_self_synthesis_engine()
    
    return {
        "total": len(synthesis.learned_patterns),
        "patterns": [
            {
                "id": p.id,
                "name": p.name,
                "confidence": p.confidence,
                "observations_count": p.observations_count
            }
            for p in synthesis.learned_patterns
        ]
    }


@genesis_router.get("/concepts")
async def list_concepts():
    """Lista e koncepteve të mësuara"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    synthesis = get_self_synthesis_engine()
    
    return {
        "total": len(synthesis.concepts),
        "concepts": [
            {
                "id": c.id,
                "name": c.name,
                "abstraction_level": c.abstraction_level,
                "related_concepts": c.related_concepts
            }
            for c in synthesis.concepts
        ]
    }


@genesis_router.post("/synthesize-for-goal/{goal_id}")
async def synthesize_for_discovered_goal(goal_id: str):
    """Sintetizo kod për një qëllim të zbuluar"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    synthesis = get_self_synthesis_engine()
    
    # Gjej qëllimin
    goal = None
    for g in synthesis.discovered_goals:
        if g.id == goal_id:
            goal = g
            break
    
    if not goal:
        raise HTTPException(404, f"Goal {goal_id} not found")
    
    result = synthesis.synthesize_for_goal(goal)
    
    return {
        "success": result is not None,
        "goal_id": goal_id,
        "result": result
    }


@genesis_router.post("/discover-goals")
async def discover_new_goals():
    """Zbulo qëllime të reja nga gap-et në njohuri"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    synthesis = get_self_synthesis_engine()
    
    # Provide some gaps for goal discovery
    gaps = [
        "need better caching strategy",
        "missing validation for user input",
        "no error handling in async operations",
        "performance bottleneck in data processing"
    ]
    
    new_goals = synthesis.discover_goals_from_gaps(gaps)
    
    return {
        "discovered": len(new_goals),
        "goals": [
            {
                "id": g.id,
                "description": g.description,
                "priority": g.priority
            }
            for g in new_goals
        ]
    }


@genesis_router.get("/meta")
async def get_meta_knowledge():
    """Njohuri meta - çfarë ka mësuar sistemi rreth vetes"""
    if not GENESIS_AVAILABLE:
        raise HTTPException(503, "Genesis Engine not available")
    
    synthesis = get_self_synthesis_engine()
    engine = get_genesis_engine()
    loop = get_evolution_loop()
    from evolution_loop import LoopState
    
    # Get stats safely
    obs_processed = getattr(synthesis, 'total_observations', 0)
    patterns_ext = len(synthesis.patterns)
    concepts_formed = len(synthesis.concepts)
    
    return {
        "self_awareness": {
            "total_code_generated": len(engine.gene_pool),
            "successful_evolutions": loop.metrics.total_cycles if loop else 0,
            "concepts_understood": len(synthesis.concepts),
            "patterns_recognized": len(synthesis.patterns),
            "goals_autonomously_discovered": len(synthesis.discovered_goals)
        },
        "learning_stats": {
            "observations_processed": obs_processed,
            "patterns_extracted": patterns_ext,
            "concepts_formed": concepts_formed
        },
        "capabilities_summary": {
            "can_synthesize_code": True,
            "can_evolve_algorithms": True,
            "can_discover_goals": True,
            "can_learn_patterns": True,
            "can_self_improve": True,
            "autonomous_operation": loop.state == LoopState.RUNNING if loop else False
        }
    }


# ═══════════════════════════════════════════════════════════════════
# UNIFIED STATUS ENDPOINT
# ═══════════════════════════════════════════════════════════════════

@unified_router.get("/unified/status")
async def unified_status():
    """Statusi i unifikuar i të gjitha moduleve"""
    return {
        "status": "operational",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "laboratories": {"available": LABS_AVAILABLE, "count": 23},
            "signals": {"available": SIGNALS_AVAILABLE},
            "autolearning": {"available": AUTOLEARNING_AVAILABLE},
            "cognitive": {"available": COGNITIVE_AVAILABLE},
            "features": {"available": FEATURES_AVAILABLE},
            "i18n": {"available": I18N_AVAILABLE, "languages": 72},
            "knowledge_engine": {"available": KNOWLEDGE_ENGINE_AVAILABLE},
            "curiosity_algebra": {"available": CURIOSITY_ALGEBRA_AVAILABLE},
            "pipelines": {"available": PIPELINES_AVAILABLE},
            "external_apis": {"available": EXTERNAL_APIS_AVAILABLE},
            "genesis": {"available": GENESIS_AVAILABLE, "components": ["GenesisEngine", "EvolutionLoop", "SelfSynthesis"]}
        },
        "total_available": sum([
            LABS_AVAILABLE, SIGNALS_AVAILABLE, AUTOLEARNING_AVAILABLE,
            COGNITIVE_AVAILABLE, FEATURES_AVAILABLE, I18N_AVAILABLE,
            KNOWLEDGE_ENGINE_AVAILABLE, CURIOSITY_ALGEBRA_AVAILABLE,
            PIPELINES_AVAILABLE, EXTERNAL_APIS_AVAILABLE, GENESIS_AVAILABLE
        ]),
        "total_modules": 11
    }


# ═══════════════════════════════════════════════════════════════════
# INCLUDE ALL SUB-ROUTERS
# ═══════════════════════════════════════════════════════════════════

unified_router.include_router(labs_router)
unified_router.include_router(signals_router)
unified_router.include_router(learning_router)
unified_router.include_router(cognitive_router)
unified_router.include_router(features_router)
unified_router.include_router(i18n_router)
unified_router.include_router(knowledge_router)
unified_router.include_router(curiosity_router)
unified_router.include_router(pipelines_router)
unified_router.include_router(external_router)
unified_router.include_router(genesis_router)


def get_unified_router():
    """Get the unified router with all sub-routers"""
    return unified_router


# Log loaded routes
logger.info("═" * 60)
logger.info("🔌 UNIFIED ROUTES LOADED")
logger.info(f"   ├─ /api/v1/labs/* - {23 if LABS_AVAILABLE else 0} laboratories")
logger.info(f"   ├─ /api/v1/signals/* - Signal Managers")
logger.info(f"   ├─ /api/v1/learning/* - Autolearning")
logger.info(f"   ├─ /api/v1/cognitive/* - Cognitive Signatures")
logger.info(f"   ├─ /api/v1/features/* - Feature Flags")
logger.info(f"   ├─ /api/v1/i18n/* - 72 languages")
logger.info(f"   ├─ /api/v1/knowledge-engine/* - Knowledge")
logger.info(f"   ├─ /api/v1/curiosity/* - Curiosity Algebra")
logger.info(f"   ├─ /api/v1/pipelines/* - Pipelines")
logger.info(f"   ├─ /api/v1/external/* - External APIs")
logger.info(f"   └─ /api/v1/genesis/* - Self-Generating AI")
logger.info("═" * 60)
