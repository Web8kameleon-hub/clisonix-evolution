"""
matia_core.py — Matia Engine Core
====================================
M etric   — reads all service metrics from the mesh
A nalyse  — detects patterns, anomalies, trends
T eorie   — applies statistical / cognitive theories
I mpletion — generates concrete implementation steps
A nswer   — produces streaming insight answers

lexon ekranin: accepts a screen snapshot (text/base64) and integrates it
into the analysis pipeline so Matia can understand what the user sees.
"""

from __future__ import annotations

import asyncio
import json
import math
import re
import statistics
import time
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

# ═════════════════════════════════════════════════
# DATA MODELS
# ═════════════════════════════════════════════════

@dataclass
class ScreenSnapshot:
    """What the user sees right now."""
    raw_text: str = ""
    timestamp: float = field(default_factory=time.time)
    source: str = "manual"           # manual | clipboard | vision

    def words(self) -> List[str]:
        return re.findall(r"\w+", self.raw_text.lower())

    def line_count(self) -> int:
        return len(self.raw_text.splitlines())


@dataclass
class MetricSample:
    service: str
    endpoint: str
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class Theory:
    name: str
    confidence: float          # 0.0 – 1.0
    description: str
    evidence: List[str] = field(default_factory=list)


@dataclass
class MatiaInsight:
    timestamp: float
    screen_context: str
    metrics_summary: Dict[str, float]
    theories: List[Theory]
    implementation_steps: List[str]
    answer: str
    anomalies: List[str] = field(default_factory=list)
    ttft_ms: float = 0.0        # time-to-first-token of this analysis


# ═════════════════════════════════════════════════
# METRIC COLLECTOR
# ═════════════════════════════════════════════════

class MetricCollector:
    """Pulls live metrics from the Clisonix service mesh."""

    SERVICE_ENDPOINTS: Dict[str, str] = {
        "ocean-core":       "http://clisonix-ocean-core:8030/status",
        "albi":             "http://clisonix-albi:6680/status",
        "jona":             "http://clisonix-jona:7777/status",
        "api":              "http://clisonix-api:8000/status",
        "kloud-bridge":     "http://clisonix-kloud-bridge:8889/status",
        "kloud-upstream":   "http://clisonix-kloud-upstream-runtime:9080/status",
    }

    def __init__(self, timeout: float = 3.0) -> None:
        self.timeout = timeout
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._cache_ttl = 10.0

    async def fetch_service(self, name: str, url: str) -> Optional[Dict[str, Any]]:
        now = time.time()
        cached_at, cached_val = self._cache.get(name, (0.0, None))
        if cached_val and now - cached_at < self._cache_ttl:
            return cached_val

        try:
            import aiohttp  # type: ignore
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json(content_type=None)
                        self._cache[name] = (now, data)
                        return data
        except Exception:
            pass
        return None

    async def collect_all(self) -> List[MetricSample]:
        tasks = [
            self.fetch_service(name, url)
            for name, url in self.SERVICE_ENDPOINTS.items()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        samples: List[MetricSample] = []

        for svc, result in zip(self.SERVICE_ENDPOINTS.keys(), results):
            if not isinstance(result, dict):
                continue
            # Extract common numeric fields
            for key in ("uptime", "requests_total", "error_rate", "latency_ms",
                        "cpu_percent", "memory_mb", "active_connections"):
                if isinstance(result.get(key), (int, float)):
                    samples.append(MetricSample(
                        service=svc,
                        endpoint=key,
                        value=float(result[key]),
                        unit=_unit_for(key),
                    ))
        return samples


def _unit_for(key: str) -> str:
    mapping = {
        "uptime": "s", "requests_total": "req", "error_rate": "%",
        "latency_ms": "ms", "cpu_percent": "%", "memory_mb": "MB",
        "active_connections": "conn",
    }
    return mapping.get(key, "")


# ═════════════════════════════════════════════════
# THEORY ENGINE
# ═════════════════════════════════════════════════

class TheoryEngine:
    """Applies analytical theories to metric sets and screen context."""

    # Anomaly: value deviates > K standard deviations from the group mean
    ANOMALY_SIGMA = 2.5

    def apply(
        self,
        samples: List[MetricSample],
        screen: ScreenSnapshot,
    ) -> Tuple[List[Theory], List[str], Dict[str, float]]:
        """
        Returns (theories, anomalies, metrics_summary).
        """
        theories: List[Theory] = []
        anomalies: List[str] = []

        # ── Group by endpoint key ────────────────────────────────
        groups: Dict[str, List[MetricSample]] = {}
        for s in samples:
            groups.setdefault(s.endpoint, []).append(s)

        # Build summary (mean per metric key)
        summary: Dict[str, float] = {}
        for key, group in groups.items():
            vals = [s.value for s in group]
            summary[key] = statistics.fmean(vals)

        # ── Theory 1: Latency Spike Theory ───────────────────────
        if "latency_ms" in summary:
            lat = summary["latency_ms"]
            if lat > 3000:
                theories.append(Theory(
                    name="Latency Spike",
                    confidence=0.92,
                    description=(
                        f"Mean latency {lat:.0f}ms exceeds the 3000ms SLO threshold. "
                        "Likely upstream model generation or database contention."
                    ),
                    evidence=[f"latency_ms={lat:.1f}"],
                ))
            elif lat > 1000:
                theories.append(Theory(
                    name="Elevated Latency",
                    confidence=0.70,
                    description=f"Latency at {lat:.0f}ms — within SLO but worth monitoring.",
                    evidence=[f"latency_ms={lat:.1f}"],
                ))

        # ── Theory 2: CPU Saturation ──────────────────────────────
        if "cpu_percent" in summary:
            cpu = summary["cpu_percent"]
            if cpu > 85:
                theories.append(Theory(
                    name="CPU Saturation",
                    confidence=0.88,
                    description=(
                        f"CPU at {cpu:.1f}% — kernel scheduling pressure likely "
                        "reducing throughput. Consider horizontal scaling."
                    ),
                    evidence=[f"cpu_percent={cpu:.1f}"],
                ))

        # ── Theory 3: Error Rate Drift ────────────────────────────
        if "error_rate" in summary:
            err = summary["error_rate"]
            if err > 5:
                theories.append(Theory(
                    name="Error Rate Drift",
                    confidence=min(0.5 + err / 100, 0.99),
                    description=(
                        f"Error rate {err:.1f}% suggests systematic failure. "
                        "Check upstream dependencies and retry budgets."
                    ),
                    evidence=[f"error_rate={err:.1f}"],
                ))

        # ── Theory 4: Screen Context Analysis ────────────────────
        words = set(screen.words())
        tech_signals = {
            "error", "exception", "null", "undefined", "500", "503",
            "timeout", "fail", "crash", "hang", "slow", "freeze",
        }
        hit_signals = words & tech_signals
        if hit_signals:
            theories.append(Theory(
                name="Screen Error Signal",
                confidence=0.75,
                description=(
                    f"Screen contains error indicators: {', '.join(sorted(hit_signals))}. "
                    "System is likely in a degraded state visible to the user."
                ),
                evidence=[f"token={t}" for t in sorted(hit_signals)][:5],
            ))

        # ── Anomaly detection (z-score per metric group) ──────────
        for key, group in groups.items():
            vals = [s.value for s in group]
            if len(vals) < 2:
                continue
            mean = statistics.fmean(vals)
            stdev = statistics.stdev(vals)
            if stdev == 0:
                continue
            for s in group:
                z = abs(s.value - mean) / stdev
                if z >= self.ANOMALY_SIGMA:
                    anomalies.append(
                        f"{s.service}.{key}={s.value:.1f} "
                        f"(z={z:.1f}, mean={mean:.1f}, σ={stdev:.1f})"
                    )

        return theories, anomalies, summary


# ═════════════════════════════════════════════════
# IMPLEMENTATION PLANNER
# ═════════════════════════════════════════════════

class ImplementationPlanner:
    """Converts theories into concrete numbered action steps."""

    THEORY_ACTIONS: Dict[str, List[str]] = {
        "Latency Spike": [
            "Add a 3s hard timeout in the stream proxy with fast-path fallback.",
            "Profile ocean-core `/api/v1/chat/stream` — add early first-token flush.",
            "Enable `processing_mode=fast` for queries with `token_budget <= 64`.",
            "Add `time_to_first_token` SSE metric events from ocean-core.",
        ],
        "Elevated Latency": [
            "Enable chunk coalescing in the SSE relay (already in stream/route.ts).",
            "Monitor TTFT per request; alert when median > 1500ms.",
        ],
        "CPU Saturation": [
            "Scale ocean-core horizontally: add a replica behind nginx upstream.",
            "Keep max_tokens=-1 (unlimited) for all requests - health platform must not truncate.",
            "Move Ollama to a dedicated GPU node.",
        ],
        "Error Rate Drift": [
            "Inspect `/status` endpoints on degraded services.",
            "Enable circuit breaker in kloud-bridge upstream calls.",
            "Add retry with exponential backoff (base 200ms, max 3 retries).",
        ],
        "Screen Error Signal": [
            "Cross-reference screen error tokens with current service /status.",
            "Trigger a Matia live health sweep across all registered services.",
            "Capture full browser console log via web-reader module.",
        ],
    }

    def plan(self, theories: List[Theory]) -> List[str]:
        if not theories:
            return ["All metrics look healthy. No immediate action required."]

        steps: List[str] = []
        # Sort by confidence descending
        for theory in sorted(theories, key=lambda t: t.confidence, reverse=True):
            actions = self.THEORY_ACTIONS.get(theory.name, [
                f"Investigate {theory.name} further using Matia metric sweep."
            ])
            steps.extend(actions)

        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: List[str] = []
        for s in steps:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        return unique[:8]


# ═════════════════════════════════════════════════
# ANSWER GENERATOR (streaming)
# ═════════════════════════════════════════════════

class AnswerGenerator:
    """Builds a human-readable answer and yields it token by token."""

    def build(
        self,
        screen: ScreenSnapshot,
        summary: Dict[str, float],
        theories: List[Theory],
        steps: List[str],
        anomalies: List[str],
        question: str = "",
    ) -> str:
        parts: List[str] = []

        # Greeting line
        if question:
            parts.append(f"**Matia** analizoi: _{question}_\n")
        else:
            parts.append("**Matia** lexoi ekranin dhe mblodhi metrikat.\n")

        # Metric summary
        if summary:
            parts.append("\n### Metrikat\n")
            for k, v in summary.items():
                unit = _unit_for(k)
                parts.append(f"- **{k}**: {v:.1f} {unit}")

        # Anomalies
        if anomalies:
            parts.append("\n\n### Anomali të Zbuluara\n")
            for a in anomalies:
                parts.append(f"- ⚠ {a}")

        # Theories
        if theories:
            parts.append("\n\n### Teoritë (Diagnoza)\n")
            for t in theories:
                bar = "█" * int(t.confidence * 10) + "░" * (10 - int(t.confidence * 10))
                parts.append(
                    f"**{t.name}** [{bar}] {int(t.confidence*100)}%\n"
                    f"> {t.description}"
                )
        else:
            parts.append("\n\n✅ Asnjë teori kritike nuk u zbulua.")

        # Implementation steps
        if steps:
            parts.append("\n\n### Hapat e Implementimit\n")
            for i, s in enumerate(steps, 1):
                parts.append(f"{i}. {s}")

        return "\n".join(parts)

    async def stream(self, text: str, chunk_size: int = 30) -> AsyncGenerator[str, None]:
        """Yield text in small chunks for SSE streaming."""
        for i in range(0, len(text), chunk_size):
            yield text[i : i + chunk_size]
            await asyncio.sleep(0)


# ═════════════════════════════════════════════════
# MATIA ENGINE — main entry point
# ═════════════════════════════════════════════════

class MatiaEngine:
    """
    Stateful engine orchestrating all Matia subsystems.

    Usage:
        engine = MatiaEngine()
        async for chunk in engine.analyse_stream(screen_text, question):
            print(chunk)
    """

    def __init__(self) -> None:
        self.collector = MetricCollector()
        self.theory_engine = TheoryEngine()
        self.planner = ImplementationPlanner()
        self.answer_gen = AnswerGenerator()
        self._status = "ready"
        self._request_count = 0
        self._last_insight: Optional[MatiaInsight] = None

    # ── Public API ────────────────────────────────────────────────

    async def analyse(
        self,
        screen_text: str = "",
        question: str = "",
        pull_metrics: bool = True,
    ) -> MatiaInsight:
        t0 = time.time()
        self._status = "running"
        self._request_count += 1

        screen = ScreenSnapshot(raw_text=screen_text)
        samples: List[MetricSample] = []

        if pull_metrics:
            try:
                samples = await asyncio.wait_for(
                    self.collector.collect_all(), timeout=5.0
                )
            except asyncio.TimeoutError:
                pass

        theories, anomalies, summary = self.theory_engine.apply(samples, screen)
        steps = self.planner.plan(theories)
        answer_text = self.answer_gen.build(
            screen, summary, theories, steps, anomalies, question
        )

        insight = MatiaInsight(
            timestamp=time.time(),
            screen_context=screen_text[:300],
            metrics_summary=summary,
            theories=theories,
            implementation_steps=steps,
            answer=answer_text,
            anomalies=anomalies,
            ttft_ms=(time.time() - t0) * 1000,
        )
        self._last_insight = insight
        self._status = "ready"
        return insight

    async def analyse_stream(
        self,
        screen_text: str = "",
        question: str = "",
        pull_metrics: bool = True,
    ) -> AsyncGenerator[str, None]:
        """Yield SSE-formatted chunks for the stream proxy."""
        insight = await self.analyse(screen_text, question, pull_metrics)

        # Emit TTFT metric immediately
        yield _sse_chunk(json.dumps({"metric": "ttft", "ms": round(insight.ttft_ms)}))

        async for chunk in self.answer_gen.stream(insight.answer):
            yield _sse_chunk(json.dumps({"chunk": chunk}))

        # Emit structured metadata at end
        yield _sse_chunk(json.dumps({
            "done": True,
            "anomalies": insight.anomalies,
            "theory_count": len(insight.theories),
            "steps": insight.implementation_steps,
        }))
        yield "data: [DONE]\n\n"

    def status_dict(self) -> Dict[str, Any]:
        return {
            "engine": "matia",
            "status": self._status,
            "requests_total": self._request_count,
            "last_analysis_ms": round(self._last_insight.ttft_ms if self._last_insight else 0),
            "theories_last": [t.name for t in (self._last_insight.theories if self._last_insight else [])],
            "anomalies_last": (self._last_insight.anomalies if self._last_insight else []),
        }


# ═════════════════════════════════════════════════
# HELPERS
# ═════════════════════════════════════════════════

def _sse_chunk(payload: str) -> str:
    return f"data: {payload}\n\n"
