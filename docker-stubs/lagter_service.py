#!/usr/bin/env python3
"""
Clisonix AGE v2.0
Autonomous Growth Engine

AI-driven multi-geo publishing optimizer using:
- Thompson Sampling (Multi-Armed Bandit)
- Bayesian performance updates
- Adaptive budget allocation
- Reinforcement scaling
"""

from __future__ import annotations

import asyncio
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict

from aiohttp import web

# ============================================================
# CONFIGURATION
# ============================================================

GEOS = ["GR", "AL", "IT", "DE"]
BASE_BUDGET = float(os.getenv("BASE_BUDGET", 1000.0))
MIN_VOLUME = 5
MAX_VOLUME = 20
TARGET_CR = 0.10

# ============================================================
# BANDIT INTELLIGENCE CORE
# ============================================================


@dataclass
class GeoArm:
    alpha: float = 1.0  # successes
    beta: float = 1.0   # failures

    def sample(self) -> float:
        return random.betavariate(self.alpha, self.beta)

    def update(self, conversions: int, clicks: int):
        failures = max(clicks - conversions, 0)
        self.alpha += conversions
        self.beta += failures


@dataclass
class GrowthState:
    arms: Dict[str, GeoArm] = field(default_factory=lambda: {
        geo: GeoArm() for geo in GEOS
    })
    dynamic_volume: int = MIN_VOLUME
    dynamic_budget: float = BASE_BUDGET

    def select_geo(self) -> str:
        samples = {geo: arm.sample() for geo, arm in self.arms.items()}
        return max(samples, key=samples.get)

    def update_performance(self, geo: str, conversions: int, clicks: int):
        self.arms[geo].update(conversions, clicks)
        cr = conversions / clicks if clicks > 0 else 0

        # Reinforcement scaling
        if cr >= TARGET_CR:
            self.dynamic_volume = min(MAX_VOLUME, self.dynamic_volume + 1)
            self.dynamic_budget *= 1.05
        else:
            self.dynamic_volume = max(MIN_VOLUME, self.dynamic_volume - 1)
            self.dynamic_budget *= 0.95


STATE = GrowthState()

# ============================================================
# API
# ============================================================


def utc_now():
    return datetime.now(timezone.utc).isoformat()


async def decision(request):
    geo = STATE.select_geo()
    return web.json_response({
        "timestamp": utc_now(),
        "selected_geo": geo,
        "volume": STATE.dynamic_volume,
        "budget": round(STATE.dynamic_budget, 2)
    })


async def feedback(request):
    data = await request.json()
    geo = data["geo"]
    conversions = data["conversions"]
    clicks = data["clicks"]

    STATE.update_performance(geo, conversions, clicks)

    return web.json_response({
        "status": "updated",
        "timestamp": utc_now(),
        "new_volume": STATE.dynamic_volume,
        "new_budget": round(STATE.dynamic_budget, 2)
    })


async def health(request):
    return web.json_response({"status": "healthy"})


# ============================================================
# APP
# ============================================================


def create_app():
    app = web.Application()
    app.add_routes([
        web.get("/decision", decision),
        web.post("/feedback", feedback),
        web.get("/health", health),
    ])
    return app


if __name__ == "__main__":
    app = create_app()
    web.run_app(app, port=9500)
