#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCEAN + REDIS INTEGRATION - Unlimited Debate Streaming
════════════════════════════════════════════════════════════════════════════

Integrimi i Ocean-Core me Redis Unlimited për:
- Unlimited debate sessions me stream persistence
- Real-time debate state sharing across instances
- Unlimited participant tracking
- No buffering limits - direct SSE stream write
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from services.redis_core.redis_unlimited import (
    RedisClientUnlimited,
    get_redis_client,
)

logger = logging.getLogger("OceanRedisIntegration")


class DebateStreamRedis:
    """Debate session streaming via Redis - unlimited"""

    def __init__(self, redis_client: Optional[RedisClientUnlimited] = None):
        self.redis = redis_client

    async def init(self):
        """Inicializo Redis client"""
        if self.redis is None:
            self.redis = await get_redis_client()

    async def create_debate_session(
        self,
        topic: str,
        personas: list,
        session_id: Optional[str] = None,
    ) -> str:
        """Krijo sesion debate me Redis persistence - UNLIMITED"""
        session_id = session_id or f"debate_{uuid.uuid4().hex[:12]}"

        # Create Redis stream for this debate - NO LIMIT
        debate_data = {
            "session_id": session_id,
            "topic": topic,
            "personas": str(personas),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "token_count": "0",
            "participants": "0",
        }

        # Append to streams - UNLIMITED
        stream_id = await self.redis.stream_append_unlimited(
            f"debates:stream:{session_id}",
            debate_data,
            max_len=None,  # UNLIMITED
        )

        # Index session - unlimited sessions
        await self.redis.set_unlimited(
            f"debate:session:{session_id}",
            debate_data,
            ttl=None,  # No expiry
        )

        # Add to active sessions index - unlimited
        await self.redis.client.sadd("debates:active", session_id)

        logger.info(f"✅ Debate session created: {session_id}")
        return session_id

    async def stream_persona_response(
        self,
        session_id: str,
        persona_id: str,
        token: str,
        persona_name: str = "",
    ) -> None:
        """Stream persona token directly to Redis - UNLIMITED, NO BUFFER"""
        # Append DIRECTLY to stream - no intermediate buffering
        await self.redis.stream_append_unlimited(
            f"debates:persona:{session_id}:{persona_id}",
            {
                "persona_id": persona_id,
                "persona_name": persona_name,
                "token": token,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            max_len=None,  # UNLIMITED
        )

        # Publish to subscribers - unlimited subscribers
        await self.redis.pubsub_publish_unlimited(
            f"debate:tokens:{session_id}:{persona_id}",
            {"token": token, "persona": persona_id},
        )

    async def stream_debate_completion(
        self,
        session_id: str,
        persona_id: str,
        final_response: str,
        token_count: int,
        status: str = "success",
    ) -> None:
        """Stream debate completion marker - UNLIMITED persistence"""
        await self.redis.stream_append_unlimited(
            f"debates:completion:{session_id}",
            {
                "persona_id": persona_id,
                "status": status,
                "token_count": str(token_count),
                "response_length": str(len(final_response.encode("utf-8"))),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            },
            max_len=None,  # UNLIMITED
        )

        # Update session metrics - unlimited
        await self.redis.pubsub_publish_unlimited(
            f"debate:completion:{session_id}",
            {
                "persona_id": persona_id,
                "status": status,
                "tokens": token_count,
            },
        )

    async def get_debate_stream(
        self,
        session_id: str,
        persona_id: Optional[str] = None,
    ):
        """Merr debate stream - UNLIMITED history"""
        if persona_id:
            stream_key = f"debates:persona:{session_id}:{persona_id}"
        else:
            stream_key = f"debates:stream:{session_id}"

        async for entry in self.redis.stream_read_unlimited(stream_key, start_id="0"):
            yield entry

    async def queue_debate_task(
        self,
        task: Dict[str, Any],
        priority: int = 0,
    ) -> int:
        """Queue debate task - UNLIMITED queue depth"""
        return await self.redis.queue_push_unlimited(
            "debates:tasks:queue",
            task,
            priority=priority,
        )

    async def get_debate_stats(self, session_id: str) -> Dict[str, Any]:
        """Merr statistika debate - UNLIMITED tracking"""
        return await self.redis.get_unlimited(f"debate:session:{session_id}")


# Global instance
_debate_redis: Optional[DebateStreamRedis] = None


async def get_debate_redis() -> DebateStreamRedis:
    """Merr debate Redis integration - singleton"""
    global _debate_redis
    if _debate_redis is None:
        _debate_redis = DebateStreamRedis()
        await _debate_redis.init()
    return _debate_redis


# ════════════════════════════════════════════════════════════════════════════
# FASTAPI INTEGRATION
# ════════════════════════════════════════════════════════════════════════════

def create_debate_redis_router():
    """Krijon FastAPI router për Debate + Redis"""
    from fastapi import APIRouter, HTTPException

    router = APIRouter(prefix="/api/debate-redis", tags=["debate-redis"])

    @router.post("/session/create")
    async def create_debate_session(topic: str, personas: list):
        """Krijo debate session me Redis"""
        try:
            debate_redis = await get_debate_redis()
            session_id = await debate_redis.create_debate_session(topic, personas)
            return {"session_id": session_id, "status": "active"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/session/{session_id}/stream")
    async def get_debate_stream(session_id: str):
        """Merr debate stream - unlimited entries"""
        try:
            debate_redis = await get_debate_redis()
            entries = []
            async for entry in debate_redis.get_debate_stream(session_id):
                entries.append(entry)
                if len(entries) >= 1000:
                    break

            return {
                "session_id": session_id,
                "entries": entries,
                "unlimited": True,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/session/{session_id}/token")
    async def stream_token(
        session_id: str,
        persona_id: str,
        token: str,
        persona_name: str = "",
    ):
        """Stream token directly - unlimited"""
        try:
            debate_redis = await get_debate_redis()
            await debate_redis.stream_persona_response(
                session_id,
                persona_id,
                token,
                persona_name,
            )
            return {"status": "streamed"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/session/{session_id}/complete")
    async def complete_persona_response(
        session_id: str,
        persona_id: str,
        final_response: str,
        token_count: int,
    ):
        """Mark persona response complete - unlimited persistence"""
        try:
            debate_redis = await get_debate_redis()
            await debate_redis.stream_debate_completion(
                session_id,
                persona_id,
                final_response,
                token_count,
            )
            return {"status": "completed"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router


if __name__ == "__main__":
    import asyncio
    import uuid

    async def demo():
        print("🔴 Ocean + Redis Integration Demo")
        debate_redis = DebateStreamRedis()
        await debate_redis.init()

        # Create session
        session_id = await debate_redis.create_debate_session(
            "AI Ethics",
            ["Alba", "Albi", "Jona"]
        )
        print(f"✅ Session: {session_id}")

        # Stream tokens
        for i in range(10):
            await debate_redis.stream_persona_response(
                session_id,
                "alba",
                f"token_{i}",
                "Alba",
            )

        print("✅ Tokens streamed (unlimited)")

        # Get stream
        count = 0
        async for entry in debate_redis.get_debate_stream(session_id, "alba"):
            count += 1

        print(f"✅ Stream entries: {count} (unlimited)")

    asyncio.run(demo())
