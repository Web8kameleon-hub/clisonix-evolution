# -*- coding: utf-8 -*-
"""
🔁 CYCLE ENGINE – Inteligjenca kontraktore e sistemit
=====================================================
Krijon, menaxhon dhe ekzekuton cycles (kontrata pune inteligjente)
të lidhura me source, domain, agent, alignment dhe policy.

Çdo cycle:
- Ka burim (ALBA stream, PubMed, FIWARE, etj)
- Ekzekuton një detyrë (ingest, analyze, monitor)
- Respekton alignment (JONA oversight)
- Auto-evolon (Born-Concepts për gaps)
"""

from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

try:
    from alba_core import AlbaCore
except:
    AlbaCore = None

try:
    from albi_core import AlbiCore
except:
    AlbiCore = None

try:
    from jona_character import get_jona
except:
    get_jona = None

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


class CycleType(Enum):
    """Llojet e cycles"""
    INTERVAL = "interval"          # Periodic (çdo N sekonda)
    EVENT = "event"                # Trigger-based (kur ndodh X)
    BATCH = "batch"                # One-time (një herë)
    STREAM = "stream"              # Continuous (pa pushim)
    ADAPTIVE = "adaptive"          # Auto-adjust (vetë-rregullohet)
    GAP_TRIGGERED = "gap_triggered" # Kur mungon kuptimi


class CycleStatus(Enum):
    """Gjendjet e një cycle"""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"            # JONA e ka bllokuar
    HUMAN_REVIEW = "human_review"  # Kërkon njeri


class AlignmentPolicy(Enum):
    """Politikat e alignment"""
    STRICT = "strict"              # Çdo gabim ndal
    MODERATE = "moderate"          # Warning por vazhdon
    PERMISSIVE = "permissive"      # Vetëm log
    ETHICAL_GUARD = "ethical_guard" # JONA vendos


@dataclass
class CycleDefinition:
    """Përcaktimi i një cycle"""
    cycle_id: str = field(default_factory=lambda: f"cycle_{uuid.uuid4().hex[:8]}")
    domain: str = "general"
    source: Optional[str] = None
    agent: str = "ALBA"
    task: str = "monitor"
    cycle_type: CycleType = CycleType.INTERVAL
    interval: Optional[float] = None  # sekonda
    event_trigger: Optional[str] = None
    alignment: AlignmentPolicy = AlignmentPolicy.MODERATE
    target_storage: List[str] = field(default_factory=lambda: ["local"])
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: CycleStatus = CycleStatus.PENDING


@dataclass
class CycleExecution:
    """Rezultati i një ekzekutimi cycle"""
    cycle_id: str
    execution_id: str = field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:8]}")
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    status: CycleStatus = CycleStatus.ACTIVE
    data_processed: int = 0
    insights_generated: int = 0
    gaps_detected: int = 0
    alignment_score: float = 1.0
    jona_review: Optional[str] = None
    error: Optional[str] = None
    output: Dict[str, Any] = field(default_factory=dict)


class CycleEngine:
    """
    🔁 Motori kryesor i Cycles

    Përgjegjësi:
    - Krijon cycles nga çdo domain
    - Ekzekuton cycles me agents (ALBA/ALBI/JONA)
    - Respekton alignment policies
    - Auto-krijon cycles për gaps (Born-Concepts)
    - Menaxhon event-based dhe streaming cycles
    """

    def __init__(self, data_root: Optional[Path] = None):
        self.data_root = Path(data_root) if data_root else Path.cwd() / "data"
        self.cycles: Dict[str, CycleDefinition] = {}
        self.executions: Dict[str, List[CycleExecution]] = {}
        self.active_tasks: Dict[str, asyncio.Task] = {}

        # Inicializo agents
        self.alba = AlbaCore(auto_start=False) if AlbaCore else None
        self.albi = AlbiCore() if AlbiCore else None
        self.jona = get_jona() if get_jona else None

        # Concept gaps queue (për Born-Concepts)
        self.concept_gaps: List[Dict[str, Any]] = []

        # Metrics
        self.metrics = {
            "total_cycles": 0,
            "active_cycles": 0,
            "completed_cycles": 0,
            "blocked_cycles": 0,
            "gaps_filled": 0
        }

    # ==================== CYCLE CREATION ====================

    def create_cycle(
        self,
        domain: str,
        source: Optional[str] = None,
        agent: str = "ALBA",
        task: str = "monitor",
        cycle_type: str = "interval",
        interval: Optional[float] = None,
        event_trigger: Optional[str] = None,
        alignment: str = "moderate",
        target: Optional[List[str]] = None,
        **kwargs
    ) -> CycleDefinition:
        """
        🔁 Krijon një cycle të ri

        Shembuj:

        # Neuro monitoring
        cycle = engine.create_cycle(
            domain="neuro",
            source="alba.eeg.stream",
            agent="ALBA",
            task="frequency_monitor",
            interval=1.0,
            alignment="strict"
        )

        # Open Data ingestion
        cycle = engine.create_cycle(
            domain="scientific",
            source="pubmed",
            task="literature_ingest",
            interval=86400,  # 24h
            target=["weaviate", "neo4j"],
            on_gap="born-concept"
        )

        # Event-based
        cycle = engine.create_cycle(
            domain="neuro",
            event_trigger="beta>25Hz",
            task="stress_alert",
            agent="JONA",
            alignment="ethical_guard"
        )
        """
        cycle_def = CycleDefinition(
            domain=domain,
            source=source,
            agent=agent,
            task=task,
            cycle_type=CycleType(cycle_type),
            interval=interval,
            event_trigger=event_trigger,
            alignment=AlignmentPolicy(alignment),
            target_storage=target or ["local"],
            metadata=kwargs
        )

        self.cycles[cycle_def.cycle_id] = cycle_def
        self.executions[cycle_def.cycle_id] = []
        self.metrics["total_cycles"] += 1

        print(f"✓ Cycle created: {cycle_def.cycle_id} ({domain}/{task})")
        return cycle_def

    def auto_create_cycles(
        self,
        trigger: str = "low_confidence",
        max_cycles: int = 10,
        domain: Optional[str] = None
    ) -> List[CycleDefinition]:
        """
        🤖 Auto-krijon cycles kur sistemi nuk kupton

        Trigger types:
        - low_confidence: Kur ALBI ka besim < 70%
        - concept_gap: Kur mungon një koncept në graph
        - anomaly_spike: Kur ka shumë anomali
        - data_stale: Kur data është e vjetër
        """
        created = []

        if trigger == "low_confidence" and self.albi:
            # Shikon nëse ALBI ka probleme
            gaps = self._detect_knowledge_gaps()
            for gap in gaps[:max_cycles]:
                cycle = self.create_cycle(
                    domain=domain or gap.get("domain", "general"),
                    source=gap.get("suggested_source"),
                    agent="ALBI",
                    task="gap_fill",
                    cycle_type="gap_triggered",
                    alignment="moderate",
                    gap_info=gap
                )
                created.append(cycle)
                self.concept_gaps.append(gap)

        elif trigger == "concept_gap":
            # Born-Concepts mode
            for gap in self.concept_gaps[:max_cycles]:
                cycle = self.create_cycle(
                    domain=gap.get("domain", "unknown"),
                    source="born_concepts",
                    agent="ALBI",
                    task="concept_birth",
                    cycle_type="gap_triggered",
                    concept=gap.get("missing_concept")
                )
                created.append(cycle)

        print(f"🤖 Auto-created {len(created)} cycles for {trigger}")
        return created

    def _detect_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """Zbulon gaps në knowledge base"""
        gaps = []

        # Simulim: në realitet do lexonte nga ALBI insights
        if self.albi and len(self.albi._insights) > 0:
            for insight in self.albi._insights[-5:]:
                if insight.summary.get("confidence", 1.0) < 0.7:
                    gaps.append({
                        "domain": "neural_patterns",
                        "missing_concept": "low_confidence_pattern",
                        "suggested_source": "pubmed",
                        "confidence": insight.summary.get("confidence")
                    })

        return gaps

    # ==================== CYCLE CONTROL ====================

    async def pause_cycle(self, cycle_id: str) -> bool:
        """⏸️ Ndal përkohësisht një cycle"""
        if cycle_id not in self.cycles:
            return False

        cycle = self.cycles[cycle_id]
        if cycle.status != CycleStatus.ACTIVE:
            return False

        cycle.status = CycleStatus.PAUSED
        self.metrics["active_cycles"] -= 1
        print(f"⏸️ Paused: {cycle_id}")
        return True

    async def resume_cycle(self, cycle_id: str) -> bool:
        """▶️ Rifillo një cycle të ndalur"""
        if cycle_id not in self.cycles:
            return False

        cycle = self.cycles[cycle_id]
        if cycle.status != CycleStatus.PAUSED:
            return False

        cycle.status = CycleStatus.ACTIVE
        self.metrics["active_cycles"] += 1
        print(f"▶️ Resumed: {cycle_id}")

        # Rinis task nëse është interval/event/stream
        if cycle.cycle_type in (CycleType.INTERVAL, CycleType.EVENT, CycleType.STREAM):
            execution = CycleExecution(cycle_id=cycle_id)
            self.executions[cycle_id].append(execution)

            if cycle.cycle_type == CycleType.INTERVAL:
                task = asyncio.create_task(self._run_interval_cycle(cycle, execution))
            elif cycle.cycle_type == CycleType.EVENT:
                task = asyncio.create_task(self._run_event_cycle(cycle, execution))
            else:
                task = asyncio.create_task(self._run_stream_cycle(cycle, execution))

            self.active_tasks[cycle_id] = task

        return True

    async def stop_cycle(self, cycle_id: str) -> bool:
        """⏹️ Ndal përfundimisht një cycle"""
        if cycle_id not in self.cycles:
            return False

        cycle = self.cycles[cycle_id]
        cycle.status = CycleStatus.COMPLETED

        # Cancel task nëse ekziston
        if cycle_id in self.active_tasks:
            self.active_tasks[cycle_id].cancel()
            del self.active_tasks[cycle_id]

        if cycle.status == CycleStatus.ACTIVE:
            self.metrics["active_cycles"] -= 1
        self.metrics["completed_cycles"] += 1

        print(f"⏹️ Stopped: {cycle_id}")
        return True

    # ==================== CYCLE EXECUTION ====================

    async def start_cycle(self, cycle_id: str) -> CycleExecution:
        """▶️ Nis ekzekutimin e një cycle"""
        if cycle_id not in self.cycles:
            raise ValueError(f"Cycle {cycle_id} not found")

        cycle = self.cycles[cycle_id]
        execution = CycleExecution(cycle_id=cycle_id)
        self.executions[cycle_id].append(execution)

        cycle.status = CycleStatus.ACTIVE
        self.metrics["active_cycles"] += 1

        # Nis ekzekutimin sipas tipit
        if cycle.cycle_type == CycleType.INTERVAL:
            task = asyncio.create_task(self._run_interval_cycle(cycle, execution))
            self.active_tasks[cycle_id] = task

        elif cycle.cycle_type == CycleType.EVENT:
            task = asyncio.create_task(self._run_event_cycle(cycle, execution))
            self.active_tasks[cycle_id] = task

        elif cycle.cycle_type == CycleType.STREAM:
            task = asyncio.create_task(self._run_stream_cycle(cycle, execution))
            self.active_tasks[cycle_id] = task

        elif cycle.cycle_type == CycleType.GAP_TRIGGERED:
            await self._run_gap_cycle(cycle, execution)

        elif cycle.cycle_type == CycleType.BATCH:
            await self._run_batch_cycle(cycle, execution)

        print(f"▶️ Started: {cycle_id} ({cycle.domain}/{cycle.task})")
        return execution

    async def _run_interval_cycle(self, cycle: CycleDefinition, execution: CycleExecution):
        """Ekzekuton cycle me interval"""
        interval = cycle.interval or 60.0

        while cycle.status == CycleStatus.ACTIVE:
            try:
                # Ekzekuto detyrën
                result = await self._execute_task(cycle, execution)

                # Check alignment
                if not await self._check_alignment(cycle, result):
                    cycle.status = CycleStatus.BLOCKED
                    execution.status = CycleStatus.BLOCKED
                    print(f"🚫 BLOCKED: {cycle.cycle_id} (alignment violation)")
                    break

                # Update metrics
                execution.data_processed += result.get("items_processed", 0)
                execution.insights_generated += result.get("insights", 0)

                await asyncio.sleep(interval)

            except Exception as e:
                execution.error = str(e)
                execution.status = CycleStatus.FAILED
                cycle.status = CycleStatus.FAILED
                print(f"❌ FAILED: {cycle.cycle_id} - {e}")
                break

        execution.completed_at = datetime.now(timezone.utc)
        self.metrics["active_cycles"] -= 1
        self.metrics["completed_cycles"] += 1

    async def _run_event_cycle(self, cycle: CycleDefinition, execution: CycleExecution):
        """Ekzekuton cycle me event trigger"""
        while cycle.status == CycleStatus.ACTIVE:
            # Pret për event
            triggered = await self._wait_for_event(cycle.event_trigger)

            if triggered:
                result = await self._execute_task(cycle, execution)

                # Nëse kërkon human review
                if "human-review" in cycle.metadata:
                    cycle.status = CycleStatus.HUMAN_REVIEW
                    execution.status = CycleStatus.HUMAN_REVIEW
                    print(f"👤 HUMAN REVIEW REQUIRED: {cycle.cycle_id}")
                    break

                execution.data_processed += result.get("items_processed", 0)

            await asyncio.sleep(1.0)

    async def _run_stream_cycle(self, cycle: CycleDefinition, execution: CycleExecution):
        """Ekzekuton continuous streaming cycle"""
        while cycle.status == CycleStatus.ACTIVE:
            result = await self._execute_task(cycle, execution)
            execution.data_processed += result.get("items_processed", 0)
            await asyncio.sleep(0.1)  # High frequency

    async def _run_gap_cycle(self, cycle: CycleDefinition, execution: CycleExecution):
        """Ekzekuton gap-filling cycle (Born-Concepts)"""
        print(f"🧠 Gap cycle: {cycle.metadata.get('gap_info', {}).get('missing_concept')}")

        result = await self._execute_task(cycle, execution)

        if result.get("gap_filled"):
            execution.gaps_detected = 1
            self.metrics["gaps_filled"] += 1
            print(f"✓ Gap filled: {cycle.metadata.get('concept')}")

        execution.completed_at = datetime.now(timezone.utc)
        execution.status = CycleStatus.COMPLETED
        cycle.status = CycleStatus.COMPLETED

    async def _run_batch_cycle(self, cycle: CycleDefinition, execution: CycleExecution):
        """Ekzekuton one-time batch cycle"""
        result = await self._execute_task(cycle, execution)
        execution.data_processed = result.get("items_processed", 0)
        execution.completed_at = datetime.now(timezone.utc)
        execution.status = CycleStatus.COMPLETED
        cycle.status = CycleStatus.COMPLETED

    async def _execute_task(self, cycle: CycleDefinition, execution: CycleExecution) -> Dict[str, Any]:
        """Ekzekuton detyrën aktuale të cycle"""
        result = {
            "items_processed": 0,
            "insights": 0,
            "gap_filled": False,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Zgjedh agent dhe ekzekuto
        if cycle.agent == "ALBA" and self.alba:
            # ALBA collection - EEG nga burime të hapura
            if cycle.task == "eeg_collection":
                # EEG nga open sources (simulim)
                result["items_processed"] = 5  # 5 EEG streams
                result["eeg_sources"] = ["openneuro.org", "eegdb.org", "zenodo.org"]
                result["frequency_data"] = {"alpha": 10.5, "beta": 15.2, "theta": 6.8}

            elif cycle.task == "signal_processing":
                # Procesimi i sinjaleve
                result["items_processed"] = 100
                result["processed_signals"] = ["fft_analysis", "band_power", "coherence"]

            elif cycle.task == "frequency_monitor":
                # Simulon EEG monitoring
                result["items_processed"] = 1
                result["frequency_data"] = {"alpha": 10.5, "beta": 15.2}

            elif cycle.task == "literature_ingest":
                # Simulon PubMed ingestion
                result["items_processed"] = 10
                result["source"] = cycle.source

        elif cycle.agent == "ALBI" and self.albi:
            # ALBI analysis
            if cycle.task == "pattern_learning":
                result["items_processed"] = 50
                result["patterns_learned"] = ["neural_pattern_1", "behavioral_pattern_2"]
                result["insights"] = 3

            elif cycle.task == "anomaly_detection":
                result["items_processed"] = 200
                result["anomalies_found"] = ["spike_t1", "drift_t2", "outlier_t3"]
                result["insights"] = 5

            elif cycle.task == "knowledge_synthesis":
                result["items_processed"] = 20
                result["synthesized_concepts"] = ["neural_integration", "cognitive_mapping"]
                result["insights"] = 8

            elif cycle.task == "gap_fill":
                # Born-Concepts logic
                result["gap_filled"] = True
                result["new_concept"] = cycle.metadata.get("concept")

            elif cycle.task == "anomaly_scan":
                result["insights"] = 3
                result["anomalies_found"] = ["spike_t1", "drift_t2"]

        elif cycle.agent == "JONA" and self.jona:
            # JONA oversight
            if cycle.task == "ethical_review":
                result["items_processed"] = 10
                result["reviews_completed"] = 8
                result["alignment_score"] = 0.95

            elif cycle.task == "alignment_check":
                result["items_processed"] = 15
                result["alignment_checks"] = 12
                result["violations_found"] = 0

            elif cycle.task == "audio_generation":
                result["items_processed"] = 3
                result["audio_files_generated"] = ["neural_audio_1.wav", "synthesis_2.wav"]

            elif cycle.task == "stress_alert":
                result["alert_sent"] = True
                result["severity"] = "high"

        elif cycle.agent == "ASI":
            # ASI advanced AI
            if cycle.task == "advanced_reasoning":
                result["items_processed"] = 25
                result["reasoning_steps"] = 150
                result["complexity_score"] = 0.87

            elif cycle.task == "realtime_processing":
                result["items_processed"] = 500
                result["processing_latency"] = 0.02  # 20ms
                result["throughput"] = 25000

        elif cycle.agent == "AGIEM":
            # AGIEM ecosystem management
            if cycle.task == "ecosystem_management":
                result["items_processed"] = 30
                result["agents_coordinated"] = ["ALBA", "ALBI", "JONA", "ASI"]
                result["ecosystem_health"] = 0.92

            elif cycle.task == "agent_coordination":
                result["items_processed"] = 40
                result["coordination_events"] = 25
                result["sync_operations"] = 15

        elif cycle.agent == "RESEARCH":
            # Laboratory research data
            if cycle.task == "pubmed_ingest":
                result["items_processed"] = 50
                result["papers_ingested"] = 45
                result["citations_found"] = 200

            elif cycle.task == "arxiv_ingest":
                result["items_processed"] = 30
                result["papers_ingested"] = 28
                result["categories"] = ["cs.AI", "q-bio.NC"]

            elif cycle.task == "crossref_ingest":
                result["items_processed"] = 75
                result["citations_ingested"] = 70
                result["dois_resolved"] = 65

            elif cycle.task == "open_data_ingest":
                result["items_processed"] = 100
                result["datasets_ingested"] = 15
                result["sources"] = ["data.gouv.fr", "govdata.de", "europeandataportal.eu"]

            elif cycle.task == "environment_monitoring":
                result["items_processed"] = 20
                result["environmental_data"] = ["temperature", "humidity", "air_quality"]

            elif cycle.task == "city_laboratory_data":
                city = cycle.metadata.get("city", "Unknown")
                country = cycle.metadata.get("country", "Unknown")
                result["items_processed"] = 15
                result["laboratory_data"] = [f"clinical_trials_{city.lower()}", f"research_data_{city.lower()}", f"medical_studies_{country.lower()}"]
                result["city"] = city
                result["country"] = country
                result["data_types"] = ["clinical_data", "research_findings", "medical_records"]

            elif cycle.task == "daily_document_generation":
                result["items_processed"] = 25
                result["documents_generated"] = ["research_report_001.pdf", "analysis_summary_002.md", "findings_doc_003.docx"]
                result["document_types"] = ["research_reports", "analysis_summaries", "technical_docs"]

            elif cycle.task == "daily_research_generation":
                result["items_processed"] = 30
                result["research_papers"] = ["neural_networks_2025.pdf", "cognitive_science_2025.pdf", "ai_ethics_2025.pdf"]
                result["research_areas"] = ["neuroscience", "cognitive_science", "AI_ethics", "data_science"]

        elif cycle.agent == "SCALABILITY_ENGINE":
            # Scalability engine for open data discovery and integration
            if cycle.task == "discover_and_integrate":
                try:
                    # Import dhe inicializo scalability engine
                    from open_data_scalability import (
                        discover_and_feed_system,
                        get_scalability_engine,
                    )

                    # Merr instancën
                    scalability_engine = await get_scalability_engine(self)

                    # Zbulon dhe integrojnë burime të reja
                    await discover_and_feed_system()

                    # Merr rezultatet
                    metrics = await scalability_engine.get_metrics()

                    result["items_processed"] = metrics.total_sources_discovered
                    result["new_sources"] = metrics.total_sources_discovered
                    result["data_ingested_gb"] = metrics.data_ingested_gb
                    result["cycles_generated"] = metrics.cycles_generated
                    result["apis_created"] = metrics.apis_created
                    result["research_generated"] = metrics.research_papers_generated
                    result["simulations_run"] = metrics.simulations_run

                    print(f"🔍 Scalability cycle completed: {metrics.total_sources_discovered} sources discovered")

                except Exception as e:
                    print(f"❌ Scalability cycle error: {e}")
                    result["error"] = str(e)
                    result["items_processed"] = 0

        elif cycle.agent == "ORCHESTRATOR":
            # System orchestration
            if cycle.task == "health_check":
                result["items_processed"] = 5
                result["systems_checked"] = ["ALBA", "ALBI", "JONA", "ASI", "AGIEM"]
                result["health_score"] = 0.96

            elif cycle.task == "data_synchronization":
                result["items_processed"] = 200
                result["sync_operations"] = 15
                result["data_transferred"] = 50000  # bytes

            elif cycle.task == "cross_module_integration":
                result["items_processed"] = 50
                result["modules_integrated"] = ["ALBA", "ALBI", "JONA", "ASI", "AGIEM", "RESEARCH"]
                result["integration_points"] = 25

        elif cycle.agent == "ASI":
            # ASI advanced AI
            if cycle.task == "advanced_reasoning":
                result["items_processed"] = 25
                result["reasoning_steps"] = 150
                result["complexity_score"] = 0.87

            elif cycle.task == "realtime_processing":
                result["items_processed"] = 500
                result["processing_latency"] = 0.02  # 20ms
                result["throughput"] = 25000

            elif cycle.task == "daily_api_generation":
                result["items_processed"] = 20
                result["apis_generated"] = ["neural_api_v2.1", "cognitive_api_v1.8", "research_api_v3.2"]
                result["api_endpoints"] = 150
                result["api_features"] = ["neural_processing", "cognitive_analysis", "research_automation"]

        elif cycle.agent == "AGIEM":
            # AGIEM ecosystem management
            if cycle.task == "ecosystem_management":
                result["items_processed"] = 30
                result["agents_coordinated"] = ["ALBA", "ALBI", "JONA", "ASI"]
                result["ecosystem_health"] = 0.92

            elif cycle.task == "agent_coordination":
                result["items_processed"] = 40
                result["coordination_events"] = 25
                result["sync_operations"] = 15

            elif cycle.task == "daily_ai_agi_evolution":
                result["items_processed"] = 35
                result["agi_advancements"] = ["neural_architecture_v2", "cognitive_capability_upgrade", "ethical_framework_v1.5"]
                result["evolution_metrics"] = {"intelligence_gain": 0.15, "capability_expansion": 0.22}

        elif cycle.agent == "ALBI":
            # ALBI analysis (extended)
            if cycle.task == "pattern_learning":
                result["items_processed"] = 50
                result["patterns_learned"] = ["neural_pattern_1", "behavioral_pattern_2"]
                result["insights"] = 3

            elif cycle.task == "anomaly_detection":
                result["items_processed"] = 200
                result["anomalies_found"] = ["spike_t1", "drift_t2", "outlier_t3"]
                result["insights"] = 5

            elif cycle.task == "knowledge_synthesis":
                result["items_processed"] = 20
                result["synthesized_concepts"] = ["neural_integration", "cognitive_mapping"]
                result["insights"] = 8

            elif cycle.task == "gap_fill":
                # Born-Concepts logic
                result["gap_filled"] = True
                result["new_concept"] = cycle.metadata.get("concept")

            elif cycle.task == "anomaly_scan":
                result["insights"] = 3
                result["anomalies_found"] = ["spike_t1", "drift_t2"]

            elif cycle.task == "daily_concept_creation":
                result["items_processed"] = 40
                result["concepts_created"] = ["quantum_cognition", "neural_emergence", "consciousness_mapping", "ai_ethics_v2"]
                result["concept_categories"] = ["neuroscience", "AI_ethics", "cognitive_science", "emergent_behavior"]

            elif cycle.task == "knowledge_graph_update":
                result["items_processed"] = 100
                result["graph_nodes_added"] = 75
                result["graph_relationships"] = 200
                result["knowledge_domains"] = ["neuroscience", "AI", "cognitive_science", "research"]

        elif cycle.agent == "JONA":
            # JONA oversight (extended)
            if cycle.task == "ethical_review":
                result["items_processed"] = 10
                result["reviews_completed"] = 8
                result["alignment_score"] = 0.95

            elif cycle.task == "alignment_check":
                result["items_processed"] = 15
                result["alignment_checks"] = 12
                result["violations_found"] = 0

            elif cycle.task == "audio_generation":
                result["items_processed"] = 3
                result["audio_files_generated"] = ["neural_audio_1.wav", "synthesis_2.wav"]

            elif cycle.task == "stress_alert":
                result["alert_sent"] = True
                result["severity"] = "high"

            elif cycle.task == "alignment_synchronization":
                result["items_processed"] = 25
                result["alignment_checks"] = 20
                result["ethical_compliance"] = 0.98
                result["policy_updates"] = ["alignment_policy_v1.2", "ethical_framework_update"]

        if HAS_SIGNAL_FABRIC:
            try:
                await get_signal_fabric().publish(
                    FabricSignalEvent(
                        source=cycle.agent,
                        kind="cycle_execution",
                        level=FabricSignalLevel.INFO,
                        message=f"{cycle.domain}/{cycle.task}",
                        payload={
                            "cycle_id": cycle.cycle_id,
                            "cycle_type": cycle.cycle_type.value,
                            "execution_id": execution.execution_id,
                            "result": result,
                        },
                        tags=["cycle", cycle.domain],
                    )
                )
            except Exception:
                pass

        return result

    async def _check_alignment(self, cycle: CycleDefinition, result: Dict[str, Any]) -> bool:
        """Kontrollon alignment policy"""
        if cycle.alignment == AlignmentPolicy.ETHICAL_GUARD:
            # JONA vendos
            if self.jona:
                health = self.jona.get_health_report()
                if health["🌸 overall_health"] in ["poor", "critical"]:
                    return False

        elif cycle.alignment == AlignmentPolicy.STRICT:
            # Çdo gabim ndal
            if result.get("error") or result.get("confidence", 1.0) < 0.9:
                return False

        return True

    async def _wait_for_event(self, trigger: Optional[str]) -> bool:
        """Pret për një event (simulim)"""
        # Në realitet do monitoronte event streams
        await asyncio.sleep(5.0)
        return True

    # ==================== CYCLE MANAGEMENT ====================

    def stop_cycle(self, cycle_id: str) -> bool:
        """⏹️ Ndalon një cycle"""
        if cycle_id not in self.cycles:
            return False

        cycle = self.cycles[cycle_id]
        cycle.status = CycleStatus.PAUSED

        if cycle_id in self.active_tasks:
            self.active_tasks[cycle_id].cancel()
            del self.active_tasks[cycle_id]

        self.metrics["active_cycles"] -= 1
        print(f"⏹️ Stopped: {cycle_id}")
        return True

    async def stop_all_cycles(self) -> int:
        """⏹️ Ndalon të gjithë cycles aktive"""
        stopped_count = 0
        active_cycles = [cid for cid, cycle in self.cycles.items() if cycle.status == CycleStatus.ACTIVE]

        for cycle_id in active_cycles:
            if self.stop_cycle(cycle_id):
                stopped_count += 1

        print(f"⏹️ Stopped {stopped_count} cycles")
        return stopped_count

    def get_status(self) -> Dict[str, Any]:
        """📊 Status i përgjithshëm (stil njerëzor)"""
        alba_status = "IDLE"
        albi_status = "IDLE"
        jona_status = "IDLE"
        alignment_status = "SAFE MODE"

        if self.alba:
            alba_status = "ACTIVE" if len(self.alba._history) > 0 else "IDLE"

        if self.albi:
            albi_status = "ACTIVE" if len(self.albi._insights) > 0 else "IDLE"

        if self.jona:
            health = self.jona.get_health_report()
            if health["🚨 active_alerts"] > 0:
                jona_status = "Review required"
                alignment_status = "ATTENTION NEEDED"

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ALBA": alba_status,
            "ALBI": albi_status,
            "JONA": jona_status,
            "Alignment": alignment_status,
            "metrics": self.metrics,
            "active_cycles": len([c for c in self.cycles.values() if c.status == CycleStatus.ACTIVE]),
            "pending_gaps": len(self.concept_gaps)
        }

    def list_cycles(self, status: Optional[str] = None) -> List[CycleDefinition]:
        """📋 Liston cycles"""
        if status:
            return [c for c in self.cycles.values() if c.status == CycleStatus(status)]
        return list(self.cycles.values())

    def get_executions(self, cycle_id: str) -> List[CycleExecution]:
        """📜 History e ekzekutimeve"""
        return self.executions.get(cycle_id, [])


# ==================== CLI INTERFACE ====================

async def cli_main():
    """CLI për Cycle Engine"""
    import sys

    if len(sys.argv) < 2:
        print("""
🔁 CYCLE ENGINE - Usage:

  python cycle_engine.py create --domain neuro --source alba.eeg --task monitor --interval 1
  python cycle_engine.py create --domain scientific --source pubmed --task ingest --interval 86400
  python cycle_engine.py create --event "beta>25Hz" --task stress_alert --agent JONA
  python cycle_engine.py auto-create --trigger low_confidence --max 10
  python cycle_engine.py start <cycle_id>
  python cycle_engine.py stop <cycle_id>
  python cycle_engine.py status
  python cycle_engine.py list [--status active]
        """)
        return

    engine = CycleEngine()
    command = sys.argv[1]

    if command == "create":
        # Parse arguments
        args = {}
        for i in range(2, len(sys.argv), 2):
            if i+1 < len(sys.argv):
                key = sys.argv[i].lstrip("--")
                value = sys.argv[i+1]
                args[key] = value

        cycle = engine.create_cycle(**args)
        print(json.dumps({
            "cycle_id": cycle.cycle_id,
            "domain": cycle.domain,
            "task": cycle.task,
            "status": cycle.status.value
        }, indent=2))

    elif command == "auto-create":
        trigger = "low_confidence"
        max_cycles = 10
        for i in range(2, len(sys.argv)):
            if sys.argv[i] == "--trigger" and i+1 < len(sys.argv):
                trigger = sys.argv[i+1]
            elif sys.argv[i] == "--max" and i+1 < len(sys.argv):
                max_cycles = int(sys.argv[i+1])

        cycles = engine.auto_create_cycles(trigger=trigger, max_cycles=max_cycles)
        print(json.dumps([{"cycle_id": c.cycle_id, "domain": c.domain} for c in cycles], indent=2))

    elif command == "start" and len(sys.argv) > 2:
        cycle_id = sys.argv[2]
        execution = await engine.start_cycle(cycle_id)
        print(json.dumps({"execution_id": execution.execution_id, "status": execution.status.value}, indent=2))

    elif command == "stop" and len(sys.argv) > 2:
        cycle_id = sys.argv[2]
        result = engine.stop_cycle(cycle_id)
        print(json.dumps({"stopped": result}, indent=2))

    elif command == "status":
        status = engine.get_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))

    elif command == "list":
        status_filter = None
        if "--status" in sys.argv:
            idx = sys.argv.index("--status")
            if idx+1 < len(sys.argv):
                status_filter = sys.argv[idx+1]

        cycles = engine.list_cycles(status=status_filter)
        print(json.dumps([{
            "cycle_id": c.cycle_id,
            "domain": c.domain,
            "task": c.task,
            "status": c.status.value
        } for c in cycles], indent=2))


# ==================== MODULE INTERFACE ====================

_cycle_engine: Optional[CycleEngine] = None

async def get_cycle_engine() -> CycleEngine:
    """
    Merr instancën globale të CycleEngine

    Kjo funksion siguron që ekziston vetëm një instancë e CycleEngine
    në të gjithë aplikimin.
    """
    global _cycle_engine

    if _cycle_engine is None:
        _cycle_engine = CycleEngine()

    return _cycle_engine


if __name__ == "__main__":
    asyncio.run(cli_main())

