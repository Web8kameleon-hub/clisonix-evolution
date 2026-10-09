#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ocean-Redis Integration Layer
Connects Ocean Core debate streaming with CLX Brain Redis Unlimited
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Optional

from .clx_brain_core import CLXBrain, RedisUnlimited

logger = logging.getLogger("OceanRedisIntegration")


class OceanRedisIntegration:
    """Integration layer between Ocean-Core and CLX Brain Redis"""

    def __init__(self):
        self.redis = RedisUnlimited()
        self.brain: Optional[CLXBrain] = None
        self._initialized = False

    async def initialize(self, brain: Optional[CLXBrain] = None) -> None:
        """Initialize integration"""
        await self.redis.initialize()

        if brain:
            self.brain = brain
        else:
            self.brain = CLXBrain(emri="OceanBrain", versioni="1.0.0")
            await self.brain.initialize_redis()

        self._initialized = True
        logger.info("✅ Ocean-Redis integration initialized")

    async def close(self) -> None:
        """Close all connections"""
        if self.brain:
            await self.brain.close_redis()
        await self.redis.close()
        self._initialized = False

    async def debate_stream_to_redis(
        self,
        debate_id: str,
        messages: AsyncGenerator[Dict[str, Any], None],
    ) -> None:
        """
        Pipes debate stream from Ocean-Core into Redis Unlimited

        Usage:
            async for chunk in trinity_debate_stream(...):
                await integration.debate_stream_to_redis(debate_id, chunk)
        """
        if not self._initialized:
            raise RuntimeError("Integration not initialized")

        stream_key = f"ocean:debate:{debate_id}:stream"

        try:
            async for message in messages:
                # Append to Redis stream (unlimited)
                entry_id = await self.redis.stream_append(
                    stream_key,
                    {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "message": message,
                    },
                )

                # Publish to subscribers
                await self.redis.client.publish(
                    f"ocean:debate:{debate_id}:updates",
                    json.dumps({
                        "entry_id": entry_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }),
                )

                logger.debug(f"Debate message streamed to Redis: {entry_id}")

        except Exception as e:
            logger.error(f"Error streaming debate to Redis: {e}")
            await self.redis.stream_append(
                stream_key,
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                    "status": "failed",
                },
            )
            raise

    async def subscribe_to_debate(
        self,
        debate_id: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Subscribe to debate stream in real-time
        Yields messages as they arrive
        """
        if not self._initialized:
            raise RuntimeError("Integration not initialized")

        stream_key = f"ocean:debate:{debate_id}:stream"

        try:
            async for message in self.redis.stream_subscribe(stream_key):
                yield message
        except asyncio.CancelledError:
            logger.info(f"Debate subscription cancelled: {debate_id}")
        except Exception as e:
            logger.error(f"Error subscribing to debate: {e}")
            raise

    async def store_debate_metrics(
        self,
        debate_id: str,
        metrics: Dict[str, Any],
    ) -> None:
        """Store debate metrics in Redis"""
        if not self._initialized:
            raise RuntimeError("Integration not initialized")

        metrics_key = f"ocean:debate:{debate_id}:metrics"
        await self.redis.set_json(metrics_key, metrics, ttl=86400)  # 24h TTL
        logger.info(f"Debate metrics stored: {debate_id}")

    async def store_debate_decision(
        self,
        debate_id: str,
        decision: Dict[str, Any],
    ) -> None:
        """Store cognitive decision for debate outcome"""
        if not self._initialized:
            raise RuntimeError("Integration not initialized")

        # Process decision through brain
        brain_input = {
            "debate_id": debate_id,
            "tipo": "debate_decision",
            "ndikim": decision.get("confidence", 0.5),
            "veprim": "decide",
        }

        hasil = self.brain.procesoj(brain_input)

        # Store in Redis
        decision_key = f"ocean:debate:{debate_id}:decision"
        await self.redis.set_json(
            decision_key,
            {
                "debate_id": debate_id,
                "decision": decision,
                "cognitive_input": brain_input,
                "brain_result": hasil,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            ttl=86400,
        )

        logger.info(f"Debate decision stored with cognitive processing: {debate_id}")

    async def get_debate_history(
        self,
        debate_id: str,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get complete debate history from Redis"""
        if not self._initialized:
            raise RuntimeError("Integration not initialized")

        stream_key = f"ocean:debate:{debate_id}:stream"
        entries = await self.redis.stream_read(stream_key, start_id="0", count=limit)

        return {
            "debate_id": debate_id,
            "message_count": len(entries),
            "messages": entries,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    async def aggregate_debate_statistics(
        self,
        debate_id: str,
    ) -> Dict[str, Any]:
        """Aggregate statistics for a debate"""
        if not self._initialized:
            raise RuntimeError("Integration not initialized")

        metrics_key = f"ocean:debate:{debate_id}:metrics"
        metrics = await self.redis.get_json(metrics_key)

        decision_key = f"ocean:debate:{debate_id}:decision"
        decision = await self.redis.get_json(decision_key)

        history = await self.get_debate_history(debate_id)

        return {
            "debate_id": debate_id,
            "metrics": metrics or {},
            "decision": decision or {},
            "message_count": len(history["messages"]),
            "aggregation_time": datetime.now(timezone.utc).isoformat(),
        }

    async def learn_from_debate(
        self,
        debate_id: str,
        success: bool,
    ) -> None:
        """Learn from debate outcome"""
        if not self._initialized:
            raise RuntimeError("Integration not initialized")

        if not self.brain:
            raise RuntimeError("Brain not available for learning")

        # Get debate data
        stats = await self.aggregate_debate_statistics(debate_id)

        # Learn
        self.brain.mëso({
            "tipi": "debate_outcome",
            "eksperiencë": {
                "debate_id": debate_id,
                "success": success,
                "message_count": stats["message_count"],
                "metrics": stats["metrics"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        })

        logger.info(f"Brain learned from debate: {debate_id}, success={success}")

    async def health_check(self) -> Dict[str, Any]:
        """Health check for integration"""
        try:
            if not self._initialized:
                return {"status": "not_initialized"}

            # Check Redis
            await self.redis.client.ping()
            redis_ok = True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            redis_ok = False

        # Check Brain
        brain_ok = self.brain is not None if self.brain else False

        return {
            "status": "healthy" if (redis_ok and brain_ok) else "degraded",
            "redis": "ok" if redis_ok else "failed",
            "brain": "ok" if brain_ok else "failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Global integration instance
_integration: Optional[OceanRedisIntegration] = None


async def get_integration() -> OceanRedisIntegration:
    """Get global integration instance"""
    global _integration
    if _integration is None:
        _integration = OceanRedisIntegration()
        await _integration.initialize()
    return _integration


async def close_integration() -> None:
    """Close global integration instance"""
    global _integration
    if _integration:
        await _integration.close()
        _integration = None
