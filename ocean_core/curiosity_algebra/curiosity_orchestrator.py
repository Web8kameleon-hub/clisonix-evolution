# -*- coding: utf-8 -*-
"""
🧠 CURIOSITY ORCHESTRATOR - Vetëdija e Sistemit
================================================
Motori i pyetjeve të përhershme.
Curiosity Ocean nuk pret - ai kërkon, eksploron, pyet.

Pyetjet e kuriozitetit:
- "Ku ka heshtje të pazakontë?"
- "Cilat sinjale po ndryshojnë ritmin?"
- "Cilat qeliza po devijojnë nga modeli?"
- "Cilat ngjarje lidhen mes tyre?"
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from .event_bus import EventBus, Event, EventType, get_event_bus
from .signal_algebra import SignalAlgebra, get_signal_algebra
from .cell_registry import CellRegistry, CellRole, CellState, get_cell_registry
from .call_operator import CallOperator, CallScope, create_call_operator

logger = logging.getLogger(__name__)


class CuriosityType(Enum):
    """Llojet e pyetjeve të kuriozitetit"""
    SILENCE = "silence"           # Ku ka heshtje?
    RHYTHM_CHANGE = "rhythm"      # Kush po ndryshon ritëm?
    DEVIATION = "deviation"       # Kush po devijon?
    CORRELATION = "correlation"   # Çfarë lidhet?
    ANOMALY = "anomaly"           # Ku ka anomali?
    HEALTH = "health"             # Si është shëndeti?
    EXPLORATION = "exploration"   # Eksplorim i lirë


@dataclass
class CuriosityQuery:
    """Një pyetje kurioziteti"""
    query_type: CuriosityType
    description: str
    condition: Callable[[Event], bool] = None
    interval_seconds: int = 60
    last_run: datetime = None
    enabled: bool = True
    results: List[Any] = field(default_factory=list)


@dataclass
class CuriosityInsight:
    """Një zbulim nga kurioziteti"""
    insight_type: CuriosityType
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, critical
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.insight_type.value,
            "message": self.message,
            "data": self.data,
            "severity": self.severity,
            "timestamp": self.timestamp.isoformat()
        }


class CuriosityOrchestrator:
    """
    🧠 Orkestrator i Kuriozitetit
    
    Ky është "vetëdija" e sistemit Clisonix.
    Bën pyetje të vazhdueshme, zbulon mospërputhje, eksploron.
    """
    
    def __init__(self, 
                 event_bus: EventBus = None,
                 algebra: SignalAlgebra = None,
                 registry: CellRegistry = None,
                 caller: CallOperator = None):
        
        self.bus = event_bus or get_event_bus()
        self.algebra = algebra or get_signal_algebra()
        self.registry = registry or get_cell_registry()
        self.caller = caller or create_call_operator(self.registry)
        
        # Memoria e ngjarjeve
        self.events: List[Event] = []
        self.max_events = 10000
        
        # Pyetjet e kuriozitetit
        self.queries: Dict[str, CuriosityQuery] = {}
        
        # Zbulimet
        self.insights: List[CuriosityInsight] = []
        self.max_insights = 1000
        
        # Statistikat e heshtjes (për çdo burim)
        self.last_seen: Dict[str, datetime] = {}
        self.silence_threshold = timedelta(minutes=5)
        
        # Signal history për korelacion
        self.signal_history: Dict[str, List[float]] = defaultdict(list)
        
        # Lidhu me event bus
        self.bus.subscribe(self._on_event)
        
        # Shto pyetjet default
        self._init_default_queries()
        
        logger.info("🧠 CuriosityOrchestrator initialized - Vetëdija e sistemit është gati")
    
    def _init_default_queries(self):
        """Inicializo pyetjet default të kuriozitetit"""
        
        # Pyetje 1: Ku ka heshtje?
        self.add_query(CuriosityQuery(
            query_type=CuriosityType.SILENCE,
            description="Cilat burime janë të heshtura?",
            interval_seconds=60
        ))
        
        # Pyetje 2: Kush po ndryshon ritëm?
        self.add_query(CuriosityQuery(
            query_type=CuriosityType.RHYTHM_CHANGE,
            description="Cilat sinjale po ndryshojnë frekuencën?",
            interval_seconds=120
        ))
        
        # Pyetje 3: Ku ka devijim?
        self.add_query(CuriosityQuery(
            query_type=CuriosityType.DEVIATION,
            description="Cilat vlera po devijojnë nga pritshmëria?",
            interval_seconds=60
        ))
        
        # Pyetje 4: Si është shëndeti i sistemit?
        self.add_query(CuriosityQuery(
            query_type=CuriosityType.HEALTH,
            description="Si janë qelizat? Ka probleme?",
            interval_seconds=30
        ))
    
    def add_query(self, query: CuriosityQuery) -> None:
        """Shto një pyetje të re kurioziteti"""
        key = f"{query.query_type.value}_{len(self.queries)}"
        self.queries[key] = query
        logger.debug(f"🧠 Curiosity query added: {query.description}")
    
    def _on_event(self, event: Event) -> None:
        """
        Handler për çdo ngjarje që hyn në det.
        Këtu Curiosity Ocean "dëgjon" gjithçka.
        """
        # Ruaj ngjarjen
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
        
        # Përditëso last_seen
        self.last_seen[event.source] = event.timestamp
        
        # Ruaj vlerën në histori (nëse ka)
        if "value" in event.payload:
            self.signal_history[event.source].append(event.payload["value"])
            # Limit history
            if len(self.signal_history[event.source]) > 1000:
                self.signal_history[event.source] = self.signal_history[event.source][-1000:]
        
        # Kontrollo për anomali immediate
        if event.type == EventType.ANOMALY:
            self._handle_anomaly(event)
        
        # Trigero kuriozitetin
        self._trigger_curiosity(event)
    
    def _trigger_curiosity(self, event: Event) -> None:
        """Trigero pyetje kurioziteti bazuar në ngjarje"""
        now = datetime.now(timezone.utc)
        
        for key, query in self.queries.items():
            if not query.enabled:
                continue
            
            # Kontrollo nëse duhet të ekzekutohet
            if query.last_run is None or \
               (now - query.last_run).total_seconds() >= query.interval_seconds:
                
                self._run_curiosity_query(query)
                query.last_run = now
    
    def _run_curiosity_query(self, query: CuriosityQuery) -> None:
        """Ekzekuto një pyetje kurioziteti"""
        
        if query.query_type == CuriosityType.SILENCE:
            self._check_silence()
        
        elif query.query_type == CuriosityType.HEALTH:
            self._check_health()
        
        elif query.query_type == CuriosityType.DEVIATION:
            self._check_deviations()
        
        elif query.query_type == CuriosityType.RHYTHM_CHANGE:
            self._check_rhythm_changes()
        
        elif query.query_type == CuriosityType.CORRELATION:
            self._check_correlations()
    
    def _check_silence(self) -> None:
        """Kontrollo ku ka heshtje të pazakontë"""
        now = datetime.now(timezone.utc)
        silent_sources = []
        
        for source, last_time in self.last_seen.items():
            silence_duration = now - last_time
            if silence_duration > self.silence_threshold:
                silent_sources.append({
                    "source": source,
                    "silent_for": str(silence_duration),
                    "last_seen": last_time.isoformat()
                })
        
        if silent_sources:
            self._add_insight(CuriosityInsight(
                insight_type=CuriosityType.SILENCE,
                message=f"Gjeta {len(silent_sources)} burime të heshtura",
                data={"silent_sources": silent_sources},
                severity="warning" if len(silent_sources) > 3 else "info"
            ))
            
            # Thirr qelizat e heshtura
            for item in silent_sources:
                cell = self.registry.get(item["source"])
                if cell:
                    self.caller.call("wake-up", cell_id=cell.id)
    
    def _check_health(self) -> None:
        """Kontrollo shëndetin e qelizave"""
        stats = self.registry.get_stats()
        unhealthy = stats["total_cells"] - stats["healthy"]
        
        if unhealthy > 0:
            unhealthy_cells = [
                c.to_dict() for c in self.registry.all() 
                if not c.is_healthy()
            ]
            
            self._add_insight(CuriosityInsight(
                insight_type=CuriosityType.HEALTH,
                message=f"{unhealthy} qeliza janë jo të shëndetshme",
                data={"unhealthy_cells": unhealthy_cells, "stats": stats},
                severity="critical" if unhealthy > 5 else "warning"
            ))
    
    def _check_deviations(self) -> None:
        """Kontrollo devijime nga pritshmëria"""
        deviations = []
        
        for key, history in self.signal_history.items():
            if len(history) < 10:
                continue
            
            analysis = self.algebra.analyze(key)
            if analysis.get("is_anomaly"):
                deviations.append({
                    "source": key,
                    "deviation": analysis.get("deviation", 0),
                    "current": analysis.get("current"),
                    "trend": analysis.get("trend")
                })
        
        if deviations:
            self._add_insight(CuriosityInsight(
                insight_type=CuriosityType.DEVIATION,
                message=f"Gjeta {len(deviations)} sinjale me devijim",
                data={"deviations": deviations},
                severity="warning"
            ))
    
    def _check_rhythm_changes(self) -> None:
        """Kontrollo ndryshime në ritëm (frekuencë ngjarjesh)"""
        now = datetime.now(timezone.utc)
        window_recent = timedelta(minutes=5)
        window_baseline = timedelta(minutes=30)
        
        rhythm_changes = []
        
        for source in self.last_seen.keys():
            # Numëro ngjarjet në dy dritare
            recent_events = len([
                e for e in self.events 
                if e.source == source and now - e.timestamp < window_recent
            ])
            
            baseline_events = len([
                e for e in self.events 
                if e.source == source and now - e.timestamp < window_baseline
            ])
            
            # Normalizo
            recent_rate = recent_events / 5  # per minute
            baseline_rate = baseline_events / 30  # per minute
            
            if baseline_rate > 0:
                change = (recent_rate - baseline_rate) / baseline_rate
                if abs(change) > 0.5:  # >50% ndryshim
                    rhythm_changes.append({
                        "source": source,
                        "recent_rate": recent_rate,
                        "baseline_rate": baseline_rate,
                        "change_percent": change * 100
                    })
        
        if rhythm_changes:
            self._add_insight(CuriosityInsight(
                insight_type=CuriosityType.RHYTHM_CHANGE,
                message=f"{len(rhythm_changes)} burime ndryshuan ritmin",
                data={"rhythm_changes": rhythm_changes},
                severity="info"
            ))
    
    def _check_correlations(self) -> None:
        """Gjej korelacione ndërmjet sinjaleve"""
        # Filtro vetëm sinjalet me histori të mjaftueshme
        valid_signals = {
            k: v for k, v in self.signal_history.items() 
            if len(v) >= 20
        }
        
        if len(valid_signals) < 2:
            return
        
        correlations = self.algebra.find_correlations(valid_signals, threshold=0.8)
        
        if correlations:
            self._add_insight(CuriosityInsight(
                insight_type=CuriosityType.CORRELATION,
                message=f"Gjeta {len(correlations)} korelacione të forta",
                data={"correlations": [
                    {"signal1": c[0], "signal2": c[1], "correlation": c[2]}
                    for c in correlations[:10]  # Top 10
                ]},
                severity="info"
            ))
    
    def _handle_anomaly(self, event: Event) -> None:
        """Trajto një anomali immediate"""
        self._add_insight(CuriosityInsight(
            insight_type=CuriosityType.ANOMALY,
            message=f"Anomali e zbuluar nga {event.source}",
            data={"event": event.to_dict()},
            severity="critical"
        ))
        
        # Thirr qelizat e lidhura për informacion
        cell = self.registry.get(event.source)
        if cell:
            self.caller.cascade_call("investigate-anomaly", cell.id, {
                "anomaly_event": event.to_dict()
            })
    
    def _add_insight(self, insight: CuriosityInsight) -> None:
        """Shto një zbulim"""
        self.insights.append(insight)
        if len(self.insights) > self.max_insights:
            self.insights = self.insights[-self.max_insights:]
        
        logger.info(f"🧠 Insight [{insight.severity}]: {insight.message}")
    
    # ==================== API Publike ====================
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        Bëj një pyetje kurioziteti.
        Ky është ndërfaqja kryesore për përdoruesin.
        """
        question_lower = question.lower()
        
        if "heshtje" in question_lower or "silent" in question_lower:
            self._check_silence()
            return self._latest_insight(CuriosityType.SILENCE)
        
        if "shëndet" in question_lower or "health" in question_lower:
            self._check_health()
            return self._latest_insight(CuriosityType.HEALTH)
        
        if "devijim" in question_lower or "deviation" in question_lower:
            self._check_deviations()
            return self._latest_insight(CuriosityType.DEVIATION)
        
        if "ritëm" in question_lower or "rhythm" in question_lower:
            self._check_rhythm_changes()
            return self._latest_insight(CuriosityType.RHYTHM_CHANGE)
        
        if "korelacion" in question_lower or "correlation" in question_lower:
            self._check_correlations()
            return self._latest_insight(CuriosityType.CORRELATION)
        
        # Default: kthe statusin e përgjithshëm
        return self.get_status()
    
    def _latest_insight(self, insight_type: CuriosityType) -> Dict[str, Any]:
        """Merr zbulimet e fundit të një tipi"""
        relevant = [i for i in self.insights if i.insight_type == insight_type]
        if relevant:
            return relevant[-1].to_dict()
        return {"message": "Asnjë zbulim i këtij tipi"}
    
    def get_insights(self, limit: int = 20, severity: str = None) -> List[Dict]:
        """Merr zbulimet e fundit"""
        insights = self.insights
        if severity:
            insights = [i for i in insights if i.severity == severity]
        return [i.to_dict() for i in insights[-limit:]]
    
    def get_status(self) -> Dict[str, Any]:
        """Statusi i plotë i kuriozitetit"""
        return {
            "service": "CuriosityOrchestrator",
            "status": "active",
            "total_events": len(self.events),
            "total_insights": len(self.insights),
            "active_queries": len([q for q in self.queries.values() if q.enabled]),
            "tracked_sources": len(self.last_seen),
            "signal_histories": len(self.signal_history),
            "cells_registered": self.registry.get_stats()["total_cells"],
            "bus_stats": self.bus.get_stats(),
            "recent_insights": self.get_insights(5)
        }
    
    async def run_exploration(self) -> Dict[str, Any]:
        """
        Ekzekuto një eksplorim të plotë të sistemit.
        Thirr të gjitha qelizat, mblidh info, analizoje.
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "exploration": "full_system"
        }
        
        # Thirr të gjitha qelizat
        responses = await self.caller.call_async("report-full-status", CallScope.ALL)
        results["cell_responses"] = len(responses)
        results["successful_responses"] = len([r for r in responses if r.success])
        
        # Kontrollo të gjitha pyetjet
        self._check_silence()
        self._check_health()
        self._check_deviations()
        self._check_rhythm_changes()
        self._check_correlations()
        
        results["new_insights"] = len([
            i for i in self.insights 
            if (datetime.now(timezone.utc) - i.timestamp).total_seconds() < 60
        ])
        
        return results


# Singleton
_orchestrator: Optional[CuriosityOrchestrator] = None

def get_curiosity_orchestrator() -> CuriosityOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CuriosityOrchestrator()
    return _orchestrator
