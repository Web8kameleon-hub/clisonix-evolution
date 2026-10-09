#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import importlib
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from service_registry import MicroService, get_service_registry
from signal_schema import SignalPulse

REDIS_AVAILABLE = True
RedisClient = None
try:
    RedisClient = importlib.import_module("redis.asyncio")
except Exception:
    REDIS_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(name)s - %(message)s")
logger = logging.getLogger("BridgeEngine")


class RouteRule(BaseModel):
    signal_type: str
    targets: List[str] = Field(default_factory=list)
    enabled: bool = True


class BridgeResult(BaseModel):
    pulse_id: str
    source: str
    signal_type: str
    routed_targets: List[str]
    success_targets: List[str]
    failed_targets: Dict[str, str]
    latency_ms: float


class BridgeEngine:
    def __init__(self):
        self.registry = get_service_registry()
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.signals_channel = os.getenv("SIGNALS_CHANNEL", "signals")
        self.target_endpoint = os.getenv("SIGNAL_TARGET_PATH", "/process-signal")
        self.default_timeout = float(os.getenv("BRIDGE_TIMEOUT_SECONDS", "5"))
        self._redis: Optional[Any] = None
        self._subscriber_task: Optional[asyncio.Task] = None
        self._http = httpx.AsyncClient(timeout=self.default_timeout)
        self.rules: Dict[str, RouteRule] = {}
        self.route_history: List[Dict[str, Any]] = []

    async def get_redis(self) -> Any:
        if not REDIS_AVAILABLE:
            raise RuntimeError("redis.asyncio is not available. Install redis>=5.0.0")
        if self._redis is None:
            if RedisClient is None:
                raise RuntimeError("redis.asyncio module failed to load")
            self._redis = RedisClient.Redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    def register_rule(self, rule: RouteRule) -> RouteRule:
        self.rules[rule.signal_type] = rule
        return rule

    def get_rule(self, signal_type: str) -> Optional[RouteRule]:
        return self.rules.get(signal_type)

    def _matches_signal(self, service: MicroService, signal_type: str) -> bool:
        signal = signal_type.lower()
        if any(signal == item.lower() for item in service.signal_types):
            return True
        return any(signal in capability.lower() or capability.lower() in signal for capability in service.capabilities)

    def resolve_targets(self, pulse: SignalPulse) -> List[str]:
        rule = self.get_rule(pulse.type)
        if rule and rule.enabled and rule.targets:
            return [target for target in rule.targets if self.registry.get_service(target)]

        targets: List[str] = []
        source_name = pulse.source.lower()
        for key, service in self.registry.get_all_services().items():
            if key == source_name:
                continue
            if self._matches_signal(service, pulse.type):
                targets.append(key)
        return targets

    async def _post_signal(self, service_key: str, pulse: SignalPulse) -> Optional[str]:
        service = self.registry.get_service(service_key)
        if not service:
            return "service_not_found"

        payload = {
            "pulse": pulse.model_dump(),
            "routed_by": "bridge-engine",
            "target": service.name,
        }
        target_url = f"http://localhost:{service.port}{self.target_endpoint}"

        try:
            response = await self._http.post(target_url, json=payload)
            if response.status_code >= 400:
                return f"http_{response.status_code}"
            return None
        except Exception as exc:
            return str(exc)

    async def process_pulse(self, pulse: SignalPulse) -> BridgeResult:
        started = time.perf_counter()
        targets = self.resolve_targets(pulse)
        if not targets:
            result = BridgeResult(
                pulse_id=pulse.id,
                source=pulse.source,
                signal_type=pulse.type,
                routed_targets=[],
                success_targets=[],
                failed_targets={},
                latency_ms=round((time.perf_counter() - started) * 1000, 2),
            )
            self.route_history.append(result.model_dump())
            logger.info(f"Pulse {pulse.id} from {pulse.source} -> no routes for type {pulse.type}")
            return result

        failures: Dict[str, str] = {}
        success: List[str] = []

        for target in targets:
            error = await self._post_signal(target, pulse)
            if error:
                failures[target] = error
            else:
                success.append(target)

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        result = BridgeResult(
            pulse_id=pulse.id,
            source=pulse.source,
            signal_type=pulse.type,
            routed_targets=targets,
            success_targets=success,
            failed_targets=failures,
            latency_ms=latency_ms,
        )
        self.route_history.append(result.model_dump())
        if len(self.route_history) > 500:
            self.route_history = self.route_history[-500:]

        logger.info(f"Pulse {pulse.id} from {pulse.source} -> routed to {targets}; success={len(success)} failed={len(failures)}")
        return result

    async def publish_pulse(self, pulse: SignalPulse) -> None:
        redis = await self.get_redis()
        await redis.publish(self.signals_channel, pulse.model_dump_json())

    async def run_subscriber(self) -> None:
        redis = await self.get_redis()
        pubsub = redis.pubsub(ignore_subscribe_messages=True)
        await pubsub.subscribe(self.signals_channel)
        logger.info(f"BridgeEngine listening on Redis channel: {self.signals_channel}")

        try:
            while True:
                message = await pubsub.get_message(timeout=1.0)
                if message and message.get("type") == "message":
                    raw_data = message.get("data")
                    if isinstance(raw_data, str):
                        try:
                            payload = json.loads(raw_data)
                            pulse = SignalPulse(**payload)
                            await self.process_pulse(pulse)
                        except Exception as exc:
                            logger.warning(f"Invalid pulse payload ignored: {exc}")
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            logger.info("BridgeEngine subscriber stopped")
            raise
        finally:
            await pubsub.unsubscribe(self.signals_channel)
            await pubsub.close()

    async def startup(self) -> None:
        if self._subscriber_task is None:
            self._subscriber_task = asyncio.create_task(self.run_subscriber())

    async def shutdown(self) -> None:
        if self._subscriber_task:
            self._subscriber_task.cancel()
            try:
                await self._subscriber_task
            except asyncio.CancelledError:
                pass
            self._subscriber_task = None
        await self._http.aclose()
        if self._redis:
            await self._redis.close()
            self._redis = None


engine = BridgeEngine()
app = FastAPI(title="Clisonix Bridge Engine", version="1.0.0")


@app.on_event("startup")
async def _on_startup() -> None:
    await engine.startup()


@app.on_event("shutdown")
async def _on_shutdown() -> None:
    await engine.shutdown()


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "bridge-engine",
        "channel": engine.signals_channel,
        "rules": len(engine.rules),
    }


@app.get("/routes")
async def routes() -> Dict[str, Any]:
    return {
        "rules": [rule.model_dump() for rule in engine.rules.values()],
        "recent": engine.route_history[-100:],
    }


@app.get("/routes/{signal_type}")
async def route_for_signal(signal_type: str) -> Dict[str, Any]:
    rule = engine.get_rule(signal_type)
    if not rule:
        return {"signal_type": signal_type, "rule": None, "mode": "auto_by_registry"}
    return {"signal_type": signal_type, "rule": rule.model_dump(), "mode": "manual_override"}


@app.post("/routes/rules")
async def set_rule(rule: RouteRule) -> Dict[str, Any]:
    stored = engine.register_rule(rule)
    return {"status": "ok", "rule": stored.model_dump()}


@app.post("/signals/process", response_model=BridgeResult)
async def process_signal(pulse: SignalPulse) -> BridgeResult:
    return await engine.process_pulse(pulse)


@app.post("/signals/publish")
async def publish_signal(pulse: SignalPulse) -> Dict[str, Any]:
    try:
        await engine.publish_pulse(pulse)
        return {"status": "queued", "pulse_id": pulse.id, "channel": engine.signals_channel}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("BRIDGE_ENGINE_PORT", "8070")))
