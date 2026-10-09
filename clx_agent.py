#!/usr/bin/env python3
"""
CLX Independent Agent — Clisonix AI
Agjent i pavarur CLX me CLX AI core dhe WorldLearner self-learning.
Zëvendëson gatewayun e vjetër Node.js nga serveri i bllokuar.

Endpoints:
  GET  /health       — liveness check
  GET  /status       — status i plote me memory stats
    POST /chat         — kerkesë direkte tek CLX AI core
  GET  /memory       — shikon training memory (knowledge summary)
  POST /observe      — injekton observation manuale per learning
  POST /learn/start  — nis continuous learning loop (default 4h)
  POST /learn/stop   — ndal continuous learning loop
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

try:
    from clx import CLXCore
except Exception:
    local_clx_path = Path(__file__).resolve().parent / "sdist" / "clx-ai"
    if local_clx_path.exists():
        sys.path.insert(0, str(local_clx_path))
    from clx import CLXCore

# ---------------------------------------------------------------------------
# Paths & config
# ---------------------------------------------------------------------------
MEMORY_PATH = Path(os.getenv("CLX_MEMORY_PATH", "/data/.clx/training-memory.json"))
CLX_MEMORY_DIR = os.getenv("CLX_MEMORY_DIR", str(MEMORY_PATH.parent))
CLX_DEFAULT_LANGUAGE = os.getenv("CLX_DEFAULT_LANGUAGE", "en")
SYSTEM_PROMPT_PATH = Path(os.getenv("CLX_SYSTEM_PROMPT", "/app/CLISONIX_SYSTEM_PROMPT.md"))
LEARN_DURATION_SECONDS = int(os.getenv("CLX_LEARN_DURATION", str(4 * 3600)))  # 4 ore default
LEARN_INTERVAL_SECONDS = int(os.getenv("CLX_LEARN_INTERVAL", "60"))

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - CLX-AGENT - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/clx_agent.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("clx_agent")

# ---------------------------------------------------------------------------
# Load CLX identity (system prompt)
# ---------------------------------------------------------------------------
def load_system_prompt() -> str:
    if SYSTEM_PROMPT_PATH.exists():
        return SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    return (
        "You are Clisonix (CLX), an independent AI agent developed by ABA GMBH, "
        "CEO Ledjan Ahmati. You are a European AI platform. Answer in the user's language. "
        "Never produce fake data. Always be honest about what you know and do not know."
    )


SYSTEM_PROMPT = load_system_prompt()

# ---------------------------------------------------------------------------
# Memory (persisted training knowledge)
# ---------------------------------------------------------------------------
class CLXMemory:
    def __init__(self, path: Path):
        self.path = path
        self.data: Dict[str, Any] = {
            "observations": [],
            "patterns": {},
            "knowledge_base": {},
            "session_count": 0,
            "total_observations": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": None,
        }
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                saved = json.loads(self.path.read_text(encoding="utf-8"))
                self.data.update(saved)
                logger.info(f"Memory loaded: {self.path} ({self.data['total_observations']} total obs)")
            except Exception as e:
                logger.warning(f"Could not load memory: {e} — starting fresh")

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.data["last_updated"] = datetime.now(timezone.utc).isoformat()
            self.path.write_text(
                json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except Exception as e:
            logger.error(f"Memory save failed: {e}")

    def add_observation(self, domain: str, data: Dict[str, Any]) -> None:
        obs = {
            "id": self.data["total_observations"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "domain": domain,
            "data": data,
        }
        # Keep last 1000 in memory list
        self.data["observations"].append(obs)
        if len(self.data["observations"]) > 1000:
            self.data["observations"] = self.data["observations"][-1000:]
        self.data["total_observations"] += 1

    def add_insight(self, domain: str, insight: str) -> None:
        if domain not in self.data["knowledge_base"]:
            self.data["knowledge_base"][domain] = []
        self.data["knowledge_base"][domain].append({
            "insight": insight,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        # Keep last 50 per domain
        self.data["knowledge_base"][domain] = self.data["knowledge_base"][domain][-50:]

    def summary(self) -> Dict[str, Any]:
        domains = list(self.data["knowledge_base"].keys())
        return {
            "total_observations": self.data["total_observations"],
            "observations_in_memory": len(self.data["observations"]),
            "session_count": self.data["session_count"],
            "domains_learned": domains,
            "insights_per_domain": {d: len(v) for d, v in self.data["knowledge_base"].items()},
            "created_at": self.data["created_at"],
            "last_updated": self.data["last_updated"],
        }


# ---------------------------------------------------------------------------
# CLX core client
# ---------------------------------------------------------------------------
clx_core: Optional[CLXCore] = None


async def clx_chat(prompt: str, language: str = CLX_DEFAULT_LANGUAGE) -> str:
    """Dërgon kërkesë tek CLXCore dhe kthen përgjigjen."""
    if clx_core is None:
        raise HTTPException(503, "CLX core not initialized")

    result = await clx_core.process_query(
        prompt,
        context={
            "endpoint": "/chat",
            "route": "clx_agent.chat",
            "language": language,
            "source": "clx-agent",
        },
    )
    response = str(result.get("response") or "").strip()
    if not response:
        raise HTTPException(503, "CLX core returned empty response")
    return response


def clx_initialized() -> bool:
    return clx_core is not None


# ---------------------------------------------------------------------------
# Self-learning engine
# ---------------------------------------------------------------------------
class CLXLearningEngine:
    def __init__(self, memory: CLXMemory):
        self.memory = memory
        self.active = False
        self._task: Optional[asyncio.Task] = None
        self._started_at: Optional[float] = None
        self._cycle_count = 0
        self.duration_seconds = LEARN_DURATION_SECONDS

    def is_active(self) -> bool:
        return self.active and self._task is not None and not self._task.done()

    def elapsed(self) -> float:
        if self._started_at is None:
            return 0.0
        return time.time() - self._started_at

    def remaining(self) -> float:
        if not self.is_active():
            return 0.0
        return max(0.0, self.duration_seconds - self.elapsed())

    async def start(self, duration_seconds: Optional[int] = None) -> None:
        if self.is_active():
            return
        if duration_seconds:
            self.duration_seconds = duration_seconds
        self.active = True
        self._started_at = time.time()
        self._task = asyncio.create_task(self._run_loop())
        self.memory.data["session_count"] += 1
        logger.info(f"CLX learning started — duration={self.duration_seconds}s ({self.duration_seconds/3600:.1f}h)")

    async def stop(self) -> None:
        self.active = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self.memory.save()
        logger.info(f"CLX learning stopped after {self.elapsed():.0f}s, {self._cycle_count} cycles")

    async def _run_loop(self) -> None:
        domains = [
            "network_analysis", "system_behavior", "user_patterns",
            "performance_metrics", "error_patterns", "optimization_opportunities",
        ]
        end_time = time.time() + self.duration_seconds

        while self.active and time.time() < end_time:
            cycle_start = time.time()
            self._cycle_count += 1
            logger.info(f"[CLX] Learning cycle #{self._cycle_count} | elapsed={self.elapsed():.0f}s | remaining={self.remaining():.0f}s")

            try:
                # Collect system metrics
                try:
                    import psutil
                    sys_data: Dict[str, Any]
                    cpu = psutil.cpu_percent(interval=1)
                    mem = psutil.virtual_memory()
                    sys_data = {
                        "cpu_percent": cpu,
                        "memory_percent": mem.percent,
                        "memory_available_mb": round(mem.available / 1024 / 1024, 1),
                    }
                except ImportError:
                    sys_data = {"note": "psutil not available"}

                self.memory.add_observation("system_behavior", sys_data)

                # Every 5 cycles: ask CLX core to synthesize insights
                if self._cycle_count % 5 == 0 and clx_initialized():
                    obs_sample = self.memory.data["observations"][-20:]
                    obs_text = json.dumps(obs_sample, ensure_ascii=False)
                    prompt = (
                        f"Analizo këto {len(obs_sample)} observime të fundit të sistemit Clisonix "
                        f"dhe jep 2-3 insights konkrete të shkurtëra (1 rresht secila):\n{obs_text}"
                    )
                    try:
                        insight = await asyncio.wait_for(clx_chat(prompt), timeout=45.0)
                        if insight:
                            self.memory.add_insight("system_behavior", insight)
                            logger.info(f"[CLX] Insight from CLX core: {insight[:100]}")
                    except asyncio.TimeoutError:
                        logger.warning("[CLX] CLX core timeout during learning cycle")
                    except Exception as e:
                        logger.warning(f"[CLX] CLX core error during learning: {e}")

            except Exception as e:
                logger.error(f"[CLX] Learning cycle error: {e}")

            # Save every 10 cycles
            if self._cycle_count % 10 == 0:
                self.memory.save()

            # Sleep until next interval
            elapsed_cycle = time.time() - cycle_start
            sleep_time = max(0, LEARN_INTERVAL_SECONDS - elapsed_cycle)
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        # Final save
        self.active = False
        self.memory.save()
        logger.info(f"[CLX] Learning session complete — {self._cycle_count} cycles, insights: {sum(len(v) for v in self.memory.data['knowledge_base'].values())}")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="CLX Independent Agent",
    description="Clisonix CLX — Agjent i pavarur AI me self-learning",
    version="2.0.0",
)

memory = CLXMemory(MEMORY_PATH)
engine = CLXLearningEngine(memory)


@app.on_event("startup")
async def startup():
    global clx_core
    logger.info("CLX Agent starting up...")
    clx_core = CLXCore(
        memory_dir=CLX_MEMORY_DIR,
        language=CLX_DEFAULT_LANGUAGE,
        enable_security=True,
        enable_learning=True,
    )
    logger.info(f"  CLX memory dir: {CLX_MEMORY_DIR}")
    logger.info(f"  CLX default language: {CLX_DEFAULT_LANGUAGE}")
    logger.info(f"  Memory: {MEMORY_PATH}")
    logger.info(f"  Learn duration: {LEARN_DURATION_SECONDS}s ({LEARN_DURATION_SECONDS/3600:.1f}h)")

    # Auto-start learning on boot
    auto_learn = os.getenv("CLX_AUTO_LEARN", "true").lower() == "true"
    if auto_learn:
        await engine.start()


@app.on_event("shutdown")
async def shutdown():
    await engine.stop()


@app.get("/health")
async def health():
    clx_ok = clx_initialized()
    return {
        "status": "healthy",
        "clx_core": "connected" if clx_ok else "uninitialized",
        "default_language": CLX_DEFAULT_LANGUAGE,
        "learning": engine.is_active(),
    }


@app.get("/status")
async def status():
    clx_status = clx_core.get_status() if clx_core is not None else None
    return {
        "agent": "CLX-Independent",
        "version": "2.0.0",
        "clx_connected": clx_initialized(),
        "default_language": CLX_DEFAULT_LANGUAGE,
        "clx_status": clx_status,
        "learning": {
            "active": engine.is_active(),
            "cycle_count": engine._cycle_count,
            "elapsed_seconds": round(engine.elapsed()),
            "remaining_seconds": round(engine.remaining()),
            "duration_seconds": engine.duration_seconds,
        },
        "memory": memory.summary(),
        "uptime": datetime.now(timezone.utc).isoformat(),
    }


class ChatRequest(BaseModel):
    message: str
    use_memory: bool = True
    language: Optional[str] = None


@app.post("/chat")
async def chat(req: ChatRequest):
    system = SYSTEM_PROMPT
    if req.use_memory:
        mem_summary = memory.summary()
        if mem_summary["domains_learned"]:
            insights_text = ""
            for domain in mem_summary["domains_learned"][:3]:
                last_insights = memory.data["knowledge_base"].get(domain, [])[-3:]
                for ins in last_insights:
                    insights_text += f"\n- [{domain}] {ins['insight'][:150]}"
            if insights_text:
                system = f"{SYSTEM_PROMPT}\n\n## Insights nga memory e CLX:{insights_text}"

    language = (req.language or CLX_DEFAULT_LANGUAGE).strip() or CLX_DEFAULT_LANGUAGE
    response = await clx_chat(f"{system}\n\nUser query: {req.message}", language=language)
    memory.add_observation("user_patterns", {"query_length": len(req.message), "has_memory": req.use_memory})
    return {
        "response": response,
        "model": "clx-core",
        "provider": "clx-ai",
        "memory_used": req.use_memory,
    }


@app.get("/memory")
async def get_memory():
    return {
        "summary": memory.summary(),
        "recent_observations": memory.data["observations"][-10:],
        "recent_insights": {
            domain: insights[-5:]
            for domain, insights in memory.data["knowledge_base"].items()
        },
    }


class ObserveRequest(BaseModel):
    domain: str
    data: Dict[str, Any]


@app.post("/observe")
async def observe(req: ObserveRequest):
    memory.add_observation(req.domain, req.data)
    return {"status": "ok", "total_observations": memory.data["total_observations"]}


class LearnRequest(BaseModel):
    duration_hours: Optional[float] = None


@app.post("/learn/start")
async def learn_start(req: LearnRequest = LearnRequest()):
    if engine.is_active():
        return {"status": "already_active", "remaining_seconds": round(engine.remaining())}
    duration = int(req.duration_hours * 3600) if req.duration_hours else None
    await engine.start(duration_seconds=duration)
    return {
        "status": "started",
        "duration_seconds": engine.duration_seconds,
        "duration_hours": engine.duration_seconds / 3600,
    }


@app.post("/learn/stop")
async def learn_stop():
    await engine.stop()
    return {"status": "stopped", "cycles_completed": engine._cycle_count}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "7778")))
