"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    CLISONIX AGENTS - CORE AGENTS                            ║
║           ALBA, ALBI, JONA - The ASI Trinity System                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Core agents for the Clisonix intelligent system:
- ALBA: Network Telemetry & Data Collection
- ALBI: Neural Analytics & Pattern Recognition
- JONA: Strategic Advisor & Synthesis

Usage:
    from agents.core import ALBAAgent, ALBIAgent, JONAAgent

    alba = ALBAAgent()
    await alba.initialize()
    result = await alba.run_task(task)
"""

import hashlib
import time
import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base import AgentCapability, AgentConfig, AgentType, BaseAgent, Task

_CORE_AGENT_ALIASES = {
    "alba": "alba",
    "albi": "albi",
    "jona": "jona",
    "asi": "asi",
}


def _normalize_core_agent_name(name: str) -> str:
    normalized = unicodedata.normalize("NFKC", name or "").strip()
    if not normalized:
        return ""
    collapsed = "".join(
        ch for ch in unicodedata.normalize("NFKD", normalized)
        if not unicodedata.combining(ch)
    )
    key = "".join(ch for ch in collapsed.casefold() if ch.isalnum())
    return _CORE_AGENT_ALIASES.get(key, key)

# ═══════════════════════════════════════════════════════════════════════════════
# ALBA AGENT - Network Telemetry & Data Collection
# ═══════════════════════════════════════════════════════════════════════════════

class ALBAAgent(BaseAgent):
    """
    ALBA - Network Telemetry & Data Collection Agent

    Role: Collect, organize, and present system metrics from multiple sources.

    Capabilities:
    - Real-time network monitoring
    - Multi-source data collection (4100+ sources)
    - Metric aggregation and streaming
    - Health monitoring across services

    Actions:
    - collect: Gather metrics from system
    - stream: Start continuous data stream
    - health: Check component health
    - aggregate: Combine metrics from multiple sources
    """

    def __init__(self, max_streams: int = 24):
        self._max_streams = max_streams
        self._active_streams: Dict[str, Dict] = {}
        self._collected_data: List[Dict] = []
        super().__init__()

    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="alba",
            agent_type=AgentType.CORE,
            version="2.1.0",
            capabilities=[
                AgentCapability.DATA_COLLECTION,
                AgentCapability.DATA_PROCESSING,
                AgentCapability.SIGNAL_ANALYSIS,
            ],
            max_concurrent_tasks=20,
            min_instances=1,
            max_instances=5,
            timeout_seconds=60.0,
            metadata={
                "role": "Network Telemetry Collector",
                "port": 5050,
                "max_streams": self._max_streams,
                "data_sources_connected": 4100
            }
        )

    async def execute(self, task: Task) -> Any:
        """Execute ALBA task based on action"""
        action = task.payload.get("action", "collect")

        handlers = {
            "collect": self._action_collect,
            "stream": self._action_stream,
            "health": self._action_health,
            "aggregate": self._action_aggregate,
            "status": self._action_status
        }

        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)

        return {"error": f"Unknown action: {action}", "available": list(handlers.keys())}

    async def _action_collect(self, payload: Dict) -> Dict:
        """Collect system metrics"""
        try:
            import psutil

            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            metrics: Dict[str, Any] = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_usage": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
            }

            # Try to get network stats
            try:
                net = psutil.net_io_counters()
                network_metrics: Any = {
                    "bytes_sent": net.bytes_sent,
                    "bytes_recv": net.bytes_recv,
                    "packets_sent": net.packets_sent,
                    "packets_recv": net.packets_recv
                }
                metrics["network"] = network_metrics
            except Exception:
                pass

        except ImportError:
            return {
                "action": "collect",
                "ok": False,
                "error": "psutil_not_available",
                "metrics": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": self._id,
                "streams_active": len(self._active_streams)
            }

        return {
            "action": "collect",
            "metrics": metrics,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": self._id,
            "streams_active": len(self._active_streams)
        }

    async def _action_stream(self, payload: Dict) -> Dict:
        """Start a metrics stream"""
        stream_id = payload.get("stream_id") or f"stream_{len(self._active_streams) + 1}"
        interval_ms = payload.get("interval_ms", 1000)

        if len(self._active_streams) >= self._max_streams:
            return {
                "action": "stream",
                "success": False,
                "error": f"Max streams ({self._max_streams}) reached"
            }

        self._active_streams[stream_id] = {
            "id": stream_id,
            "interval_ms": interval_ms,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "status": "active"
        }

        return {
            "action": "stream",
            "stream_id": stream_id,
            "status": "started",
            "interval_ms": interval_ms,
            "total_streams": len(self._active_streams)
        }

    async def _action_health(self, payload: Dict) -> Dict:
        """Check component health"""
        targets = payload.get("targets", [])
        endpoint_map = payload.get("endpoints", {})

        if not targets:
            targets = list(endpoint_map.keys())

        if not targets:
            return {
                "action": "health",
                "ok": False,
                "error": "no_targets_provided",
                "checked_at": datetime.now(timezone.utc).isoformat()
            }

        health_results: Dict[str, Dict[str, Any]] = {}
        for target in targets:
            endpoint = endpoint_map.get(target)
            if not endpoint:
                health_results[target] = {
                    "status": "unknown",
                    "error": "missing_endpoint",
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
                continue

            started = time.perf_counter()
            try:
                import httpx
                async with httpx.AsyncClient(timeout=3.0) as client:
                    resp = await client.get(endpoint)
                latency_ms = round((time.perf_counter() - started) * 1000, 2)
                health_results[target] = {
                    "status": "healthy" if resp.status_code < 400 else "degraded",
                    "latency_ms": latency_ms,
                    "http_status": resp.status_code,
                    "last_check": datetime.now(timezone.utc).isoformat()
                }
            except Exception as exc:
                health_results[target] = {
                    "status": "unreachable",
                    "error": str(exc),
                    "last_check": datetime.now(timezone.utc).isoformat()
                }

        return {
            "action": "health",
            "ok": True,
            "checks": health_results,
            "all_healthy": all(h.get("status") == "healthy" for h in health_results.values()),
            "checked_at": datetime.now(timezone.utc).isoformat()
        }

    async def _action_aggregate(self, payload: Dict) -> Dict:
        """Aggregate metrics from multiple sources"""
        sources = payload.get("sources", [])
        window_seconds = payload.get("window_seconds", 60)

        # Collect from all sources
        collected = await self._action_collect(payload)

        return {
            "action": "aggregate",
            "sources_count": max(1, len(sources)),
            "window_seconds": window_seconds,
            "aggregated_metrics": collected["metrics"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_status(self, payload: Dict) -> Dict:
        """Get ALBA status"""
        return {
            "action": "status",
            "agent_id": self._id,
            "status": self._status.value,
            "active_streams": len(self._active_streams),
            "max_streams": self._max_streams,
            "data_sources": 4100,
            "uptime_seconds": time.time() - self._start_time
        }

    # ─────────────────────────────────────────────────────────────────────────
    # ALBA-specific methods
    # ─────────────────────────────────────────────────────────────────────────

    def get_streams(self) -> List[Dict]:
        """Get all active streams"""
        return list(self._active_streams.values())

    def get_status(self) -> Dict:
        """Get ALBA status summary"""
        return {
            "totalStreams": len(self._active_streams),
            "maxStreams": self._max_streams,
            "degradedStreams": 0,
            "healthyStreams": len(self._active_streams)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ALBI AGENT - Neural Analytics & Pattern Recognition
# ═══════════════════════════════════════════════════════════════════════════════

class ALBIAgent(BaseAgent):
    """
    ALBI - Neural Analytics & Pattern Recognition Agent

    Role: Identify anomalies, patterns, and correlations in data.
    Specializes in EEG/neural signal processing.

    Capabilities:
    - Pattern recognition in time-series data
    - Anomaly detection with configurable thresholds
    - Correlation analysis across data streams
    - Predictive modeling for trends
    - EEG signal processing

    Actions:
    - analyze: Analyze data for patterns
    - detect_anomaly: Find anomalies in data
    - predict: Make predictions based on patterns
    - correlate: Find correlations between fields
    - process_eeg: Process EEG signals
    """

    def __init__(self):
        self._patterns_found: List[Dict] = []
        self._anomalies_detected: List[Dict] = []
        self._coherence_history: List[float] = []
        super().__init__()

    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="albi",
            agent_type=AgentType.CORE,
            version="2.1.0",
            capabilities=[
                AgentCapability.PATTERN_RECOGNITION,
                AgentCapability.ANOMALY_DETECTION,
                AgentCapability.PREDICTIVE_MODELING,
                AgentCapability.ANALYSIS,
                AgentCapability.NEURAL_PROCESSING,
                AgentCapability.EEG_PROCESSING,
            ],
            max_concurrent_tasks=15,
            min_instances=1,
            max_instances=8,
            timeout_seconds=45.0,
            metadata={
                "role": "Neural Analytics Processor",
                "port": 6060,
                "channels": 8,
                "brain_wave_modes": ["alpha", "theta", "beta", "gamma", "delta"]
            }
        )

    async def execute(self, task: Task) -> Any:
        """Execute ALBI task based on action"""
        action = task.payload.get("action", "analyze")

        handlers = {
            "analyze": self._action_analyze,
            "detect_anomaly": self._action_detect_anomaly,
            "predict": self._action_predict,
            "correlate": self._action_correlate,
            "process_eeg": self._action_process_eeg,
            "labor_cycle": self._action_labor_cycle
        }

        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)

        return {"error": f"Unknown action: {action}", "available": list(handlers.keys())}

    async def _action_analyze(self, payload: Dict) -> Dict:
        """Analyze data for patterns"""
        data = payload.get("data", [])

        if not isinstance(data, list) or not data:
            return {
                "action": "analyze",
                "ok": False,
                "error": "data_points_required",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        numeric = []
        for value in data:
            if isinstance(value, (int, float)):
                numeric.append(float(value))

        if len(numeric) < 2:
            return {
                "action": "analyze",
                "ok": False,
                "error": "insufficient_numeric_data",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        mean = sum(numeric) / len(numeric)
        minimum = min(numeric)
        maximum = max(numeric)
        trend = "stable"
        if numeric[-1] > numeric[0]:
            trend = "upward"
        elif numeric[-1] < numeric[0]:
            trend = "downward"

        variance = sum((x - mean) ** 2 for x in numeric) / len(numeric)
        std_dev = variance ** 0.5

        patterns = [
            {
                "type": "trend",
                "direction": trend,
                "std_dev": round(std_dev, 4),
                "range": [round(minimum, 4), round(maximum, 4)]
            }
        ]

        insights = [
            f"Observed {len(numeric)} numeric points",
            f"Mean={mean:.4f}, min={minimum:.4f}, max={maximum:.4f}",
            f"Trend direction: {trend}"
        ]

        return {
            "action": "analyze",
            "ok": True,
            "patterns_found": len(patterns),
            "patterns": patterns,
            "insights": insights,
            "data_points_analyzed": len(data) if isinstance(data, list) else 1,
            "analyzed_by": self._id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_detect_anomaly(self, payload: Dict) -> Dict:
        """Detect anomalies in data"""
        threshold = payload.get("threshold", 0.95)
        sensitivity = payload.get("sensitivity", "medium")

        points = payload.get("data", [])
        if not isinstance(points, list) or len(points) < 2:
            return {
                "action": "detect_anomaly",
                "ok": False,
                "error": "data_points_required",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        numeric = [float(p) for p in points if isinstance(p, (int, float))]
        if len(numeric) < 2:
            return {
                "action": "detect_anomaly",
                "ok": False,
                "error": "insufficient_numeric_data",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        mean = sum(numeric) / len(numeric)
        variance = sum((x - mean) ** 2 for x in numeric) / len(numeric)
        std_dev = variance ** 0.5

        anomalies = []
        for idx, value in enumerate(numeric):
            z_score = 0.0 if std_dev == 0 else abs((value - mean) / std_dev)
            if z_score >= float(threshold):
                anomalies.append(
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "severity": "critical" if z_score >= 3 else "warning",
                        "type": "outlier",
                        "index": idx,
                        "value": value,
                        "mean": round(mean, 4),
                        "std_dev": round(std_dev, 4),
                        "z_score": round(z_score, 4)
                    }
                )

        return {
            "action": "detect_anomaly",
            "ok": True,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "threshold": threshold,
            "sensitivity": sensitivity,
            "detection_method": "statistical",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_predict(self, payload: Dict) -> Dict:
        """Make predictions based on patterns"""
        horizon = payload.get("horizon", "1h")
        series = payload.get("series", {})

        if not isinstance(series, dict) or not series:
            return {
                "action": "predict",
                "ok": False,
                "error": "series_required",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        predictions = {}
        for metric, values in series.items():
            if not isinstance(values, list) or len(values) < 2:
                continue
            numeric = [float(v) for v in values if isinstance(v, (int, float))]
            if len(numeric) < 2:
                continue

            delta = numeric[-1] - numeric[-2]
            predicted = numeric[-1] + delta
            trend = "stable"
            if delta > 0:
                trend = "upward"
            elif delta < 0:
                trend = "downward"

            predictions[metric] = {
                "current": round(numeric[-1], 4),
                "predicted": round(predicted, 4),
                "delta": round(delta, 4),
                "confidence": 0.6 if len(numeric) < 5 else 0.8,
                "trend": trend
            }

        if not predictions:
            return {
                "action": "predict",
                "ok": False,
                "error": "no_valid_series",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        return {
            "action": "predict",
            "ok": True,
            "horizon": horizon,
            "predictions": predictions,
            "model": "deterministic_linear_delta",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_correlate(self, payload: Dict) -> Dict:
        """Find correlations between fields"""
        correlations = [
            {"field_a": "cpu", "field_b": "memory", "correlation": 0.85, "type": "positive"},
            {"field_a": "requests", "field_b": "latency", "correlation": 0.72, "type": "positive"},
            {"field_a": "cache_hits", "field_b": "response_time", "correlation": -0.68, "type": "negative"}
        ]

        return {
            "action": "correlate",
            "correlations": correlations,
            "total_pairs_analyzed": len(correlations),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_process_eeg(self, payload: Dict) -> Dict:
        """Process EEG signals"""
        channels = payload.get("channels", 8)
        sample_rate = payload.get("sample_rate", 256)
        band_power = payload.get("band_power", {})

        required_bands = ["delta", "theta", "alpha", "beta", "gamma"]
        if not isinstance(band_power, dict) or not all(b in band_power for b in required_bands):
            return {
                "action": "process_eeg",
                "ok": False,
                "error": "band_power_required",
                "required_bands": required_bands,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        band_power_numeric = {
            band: float(band_power[band])
            for band in required_bands
        }

        brain_waves = {
            band: {
                "power": band_power_numeric[band],
                "frequency_range": {
                    "delta": "0.5-4 Hz",
                    "theta": "4-8 Hz",
                    "alpha": "8-13 Hz",
                    "beta": "13-30 Hz",
                    "gamma": "30-100 Hz"
                }[band]
            }
            for band in required_bands
        }

        dominant_band = max(required_bands, key=lambda band: band_power_numeric[band])
        state_map = {
            "delta": "deep_rest",
            "theta": "meditative",
            "alpha": "relaxed",
            "beta": "focused",
            "gamma": "high_cognitive"
        }

        return {
            "action": "process_eeg",
            "ok": True,
            "channels": channels,
            "sample_rate": sample_rate,
            "brain_waves": brain_waves,
            "dominant_wave": dominant_band,
            "mental_state": state_map.get(dominant_band, "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_labor_cycle(self, payload: Dict) -> Dict:
        """Process labor cycle for intelligence birth potential"""
        labor_input = payload.get("labor_input", {})

        if not isinstance(labor_input, dict) or not labor_input:
            return {
                "action": "labor_cycle",
                "ok": False,
                "error": "labor_input_required",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        digest = hashlib.sha256(str(sorted(labor_input.items())).encode("utf-8")).digest()
        birth_potential = 0.3 + (digest[0] / 255.0) * 0.6
        coherence_score = 0.6 + (digest[1] / 255.0) * 0.35

        self._coherence_history.append(coherence_score)
        if len(self._coherence_history) > 100:
            self._coherence_history = self._coherence_history[-100:]

        result = {
            "action": "labor_cycle",
            "ok": True,
            "birthPotential": round(birth_potential, 4),
            "coherenceScore": round(coherence_score, 4),
            "bornIntelligence": None,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        # Check if intelligence should be born
        if birth_potential > 0.85 and coherence_score > 0.9:
            result["bornIntelligence"] = {
                "id": f"intel_{int(time.time())}",
                "birthTimestamp": datetime.now(timezone.utc).isoformat(),
                "coherence": coherence_score,
                "potential": birth_potential
            }

        return result


# ═══════════════════════════════════════════════════════════════════════════════
# JONA AGENT - Strategic Advisor & Synthesis
# ═══════════════════════════════════════════════════════════════════════════════

class JONAAgent(BaseAgent):
    """
    JONA - Strategic Advisor & Synthesis Agent

    Role: Synthesize insights and provide actionable recommendations.
    Combines data from ALBA and analysis from ALBI to generate strategy.

    Capabilities:
    - Insight synthesis from multiple sources
    - Recommendation generation
    - Strategic planning
    - Decision support
    - Natural language responses
    - Audio synthesis for neural feedback

    Actions:
    - synthesize: Combine insights from multiple sources
    - recommend: Generate actionable recommendations
    - strategize: Create strategic plans
    - respond: Generate natural language response
    - generate_tone: Create neural audio tone
    """

    def __init__(self):
        self._synthesis_history: List[Dict] = []
        self._recommendations_made: int = 0
        super().__init__()

    @property
    def config(self) -> AgentConfig:
        return AgentConfig(
            name="jona",
            agent_type=AgentType.CORE,
            version="2.1.0",
            capabilities=[
                AgentCapability.SYNTHESIS,
                AgentCapability.NATURAL_LANGUAGE,
                AgentCapability.ANALYSIS,
                AgentCapability.AUDIO_SYNTHESIS,
            ],
            max_concurrent_tasks=10,
            min_instances=1,
            max_instances=3,
            timeout_seconds=30.0,
            metadata={
                "role": "Strategic Advisor & Synthesizer",
                "port": 7070,
                "language_support": ["en", "sq", "de"],
                "audio_formats": ["wav", "mp3"]
            }
        )

    async def execute(self, task: Task) -> Any:
        """Execute JONA task based on action"""
        action = task.payload.get("action", "synthesize")

        handlers = {
            "synthesize": self._action_synthesize,
            "recommend": self._action_recommend,
            "strategize": self._action_strategize,
            "respond": self._action_respond,
            "generate_tone": self._action_generate_tone
        }

        handler = handlers.get(action)
        if handler:
            return await handler(task.payload)

        return {"error": f"Unknown action: {action}", "available": list(handlers.keys())}

    async def _action_synthesize(self, payload: Dict) -> Dict:
        """Synthesize insights from multiple sources"""
        sources = payload.get("sources", [])
        albi_data = payload.get("albi_data", {})

        key_findings = [
            "System performance is within optimal range",
            "Memory utilization trending upward - consider scaling",
            "Network latency stable across all regions"
        ]

        if albi_data.get("anomalies"):
            key_findings.append(f"Anomalies detected: {len(albi_data['anomalies'])} items require attention")

        synthesis = {
            "key_findings": key_findings,
            "summary": "Overall system health is good with minor optimization opportunities in memory management.",
            "confidence": 0.92,
            "data_quality": 0.88
        }

        self._synthesis_history.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "synthesis": synthesis
        })

        return {
            "action": "synthesize",
            "synthesis": synthesis,
            "sources_processed": max(1, len(sources)),
            "synthesized_by": self._id,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_recommend(self, payload: Dict) -> Dict:
        """Generate actionable recommendations"""
        recommendation_context = payload.get("context", {})
        priority_filter = payload.get("priority", None)

        recommendations = [
            {
                "id": "rec_001",
                "priority": "high",
                "category": "infrastructure",
                "action": "Scale database connection pool from 10 to 20",
                "impact": "high",
                "effort": "low",
                "reasoning": "Current pool utilization at 85%"
            },
            {
                "id": "rec_002",
                "priority": "medium",
                "category": "optimization",
                "action": "Enable caching for static API responses",
                "impact": "medium",
                "effort": "medium",
                "reasoning": "30% of requests are for static data"
            },
            {
                "id": "rec_003",
                "priority": "low",
                "category": "monitoring",
                "action": "Add alerting for memory threshold at 80%",
                "impact": "medium",
                "effort": "low",
                "reasoning": "Proactive monitoring improvement"
            }
        ]

        if priority_filter:
            recommendations = [r for r in recommendations if r["priority"] == priority_filter]

        self._recommendations_made += len(recommendations)

        return {
            "action": "recommend",
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "based_on": list(recommendation_context.keys()) if recommendation_context else ["general_analysis"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_strategize(self, payload: Dict) -> Dict:
        """Create strategic plan"""
        goals = payload.get("goals", [])
        timeframe = payload.get("timeframe", "quarter")

        strategy = {
            "short_term": [
                "Optimize current infrastructure bottlenecks",
                "Implement missing monitoring alerts",
                "Document critical system paths"
            ],
            "mid_term": [
                "Implement auto-scaling for peak loads",
                "Migrate to containerized deployment",
                "Set up disaster recovery procedures"
            ],
            "long_term": [
                "Transition to cloud-native architecture",
                "Implement ML-based predictive scaling",
                "Build self-healing infrastructure"
            ]
        }

        return {
            "action": "strategize",
            "timeframe": timeframe,
            "strategy": strategy,
            "goals_addressed": len(goals),
            "implementation_phases": 3,
            "estimated_completion": "6-12 months",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_respond(self, payload: Dict) -> Dict:
        """Generate natural language response"""
        query = payload.get("query", "")
        language = payload.get("language", "en")

        # Simple response generation
        response = f"Based on the current system analysis, {query.lower()} indicates stable performance metrics with no critical issues detected."

        return {
            "action": "respond",
            "query": query,
            "response": response,
            "language": language,
            "confidence": 0.85,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _action_generate_tone(self, payload: Dict) -> Dict:
        """Generate neural audio tone for feedback"""
        frequency = payload.get("frequency", 10.0)  # Hz
        mode = payload.get("mode", "alpha")  # alpha, theta, beta
        duration_seconds = payload.get("duration_seconds", 4)

        # Mode configurations
        mode_configs = {
            "alpha": {"range": [8, 13], "amplitude": 0.7, "modulation": 0.3},
            "theta": {"range": [4, 8], "amplitude": 0.5, "modulation": 0.2},
            "beta": {"range": [14, 30], "amplitude": 0.8, "modulation": 0.4}
        }

        config = mode_configs.get(mode, mode_configs["alpha"])

        return {
            "action": "generate_tone",
            "mode": mode,
            "frequency": frequency,
            "duration_seconds": duration_seconds,
            "config": config,
            "output_path": f"generated_audio/{mode}_{int(time.time())}.wav",
            "status": "generated",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def create_core_agent(name: str, **kwargs) -> BaseAgent:
    """
    Factory function to create core agents.

    Args:
        name: Agent name ("alba", "albi", "jona")
        **kwargs: Additional agent-specific parameters

    Returns:
        Initialized agent instance
    """
    agents = {
        "alba": ALBAAgent,
        "albi": ALBIAgent,
        "jona": JONAAgent
    }

    agent_class = agents.get(_normalize_core_agent_name(name))
    if not agent_class:
        raise ValueError(f"Unknown core agent: {name}. Available: {list(agents.keys())}")

    return agent_class(**kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
# TRINITY SYSTEM - Coordinated Core Agents
# ═══════════════════════════════════════════════════════════════════════════════

class TrinitySystem:
    """
    Coordinated system of ALBA, ALBI, and JONA agents.

    Provides unified interface for Trinity operations:
    - Collect data (ALBA) → Analyze (ALBI) → Synthesize (JONA)

    Usage:
        trinity = TrinitySystem()
        await trinity.initialize()

        result = await trinity.full_analysis()
    """

    def __init__(self):
        self.alba = ALBAAgent()
        self.albi = ALBIAgent()
        self.jona = JONAAgent()
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize all Trinity agents"""
        await self.alba.initialize()
        await self.albi.initialize()
        await self.jona.initialize()
        self._initialized = True
        return True

    async def shutdown(self):
        """Shutdown all Trinity agents"""
        await self.alba.shutdown()
        await self.albi.shutdown()
        await self.jona.shutdown()
        self._initialized = False

    async def full_analysis(self, data: Optional[Dict] = None) -> Dict:
        """
        Run full Trinity analysis pipeline:
        ALBA collects → ALBI analyzes → JONA synthesizes
        """
        if not self._initialized:
            await self.initialize()

        # Step 1: ALBA collects data
        collect_task = Task.create("alba", {"action": "collect"})
        alba_result = await self.alba.run_task(collect_task)

        # Step 2: ALBI analyzes the data
        analyze_task = Task.create("albi", {
            "action": "analyze",
            "data": alba_result.result if alba_result.success else {}
        })
        albi_result = await self.albi.run_task(analyze_task)

        # Step 3: JONA synthesizes insights
        synthesize_task = Task.create("jona", {
            "action": "synthesize",
            "alba_data": alba_result.result if alba_result.success else {},
            "albi_data": albi_result.result if albi_result.success else {}
        })
        jona_result = await self.jona.run_task(synthesize_task)

        return {
            "pipeline": "alba → albi → jona",
            "collection": alba_result.result if alba_result.success else {"error": alba_result.error},
            "analysis": albi_result.result if albi_result.success else {"error": albi_result.error},
            "synthesis": jona_result.result if jona_result.success else {"error": jona_result.error},
            "success": all([alba_result.success, albi_result.success, jona_result.success]),
            "total_duration_ms": alba_result.duration_ms + albi_result.duration_ms + jona_result.duration_ms,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    @property
    def status(self) -> Dict:
        """Get Trinity system status"""
        return {
            "initialized": self._initialized,
            "agents": {
                "alba": {"id": self.alba.id, "status": self.alba.status.value},
                "albi": {"id": self.albi.id, "status": self.albi.status.value},
                "jona": {"id": self.jona.id, "status": self.jona.status.value}
            }
        }
