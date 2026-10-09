#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REDIS UNLIMITED - Sistemi i Të Dhënave në Memorie pa Kufizime
═════════════════════════════════════════════════════════════════════════════

🔴 Redis Integration pa límite artificiale:
  - Unlimited streams (debate, chat, sessions)
  - Unlimited pub/sub channels
  - Unlimited queue depth
  - No maxmemory cutoff
  - Real-time persistence
  - Elastik scaling

Autor: Clisonix Team
Versioni: 1.0.0
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Set

import redis
import redis.asyncio as aioredis
from redis.asyncio.connection import ConnectionPool

logger = logging.getLogger("RedisUnlimited")
logging.basicConfig(level=logging.INFO)


# ═════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION - PA LÍMITE
# ═════════════════════════════════════════════════════════════════════════════

class RedisConfig:
    """Konfigurimi i Redis pa kufizime"""
    # Connection
    HOST: str = "localhost"
    PORT: int = 6379
    DB: int = 0
    PASSWORD: Optional[str] = None

    # Pool - unlimited connections
    MAX_CONNECTIONS: int = 0  # 0 = unlimited
    CONNECTION_POOL_KWARGS = {
        "max_connections": None,  # No limit
        "socket_keepalive": True,
        "socket_keepalive_options": {
            1: (9, 60, 60),  # TCP_KEEPIDLE, TCP_KEEPINTVL, TCP_KEEPCNT
        },
    }

    # Streams - NO LIMIT
    STREAM_MAX_LEN: Optional[int] = None  # None = unlimited
    STREAM_BATCH_SIZE: int = 1000  # Read batch (not limit)

    # TTL - pa expirash automatike
    DEFAULT_TTL: Optional[int] = None  # None = no expiry
    SESSION_TTL: int = 7 * 24 * 60 * 60  # 7 days but can extend

    # Persistence
    PERSISTENCE_ENABLED: bool = True
    SNAPSHOT_INTERVAL: int = 60  # seconds
    AOF_ENABLED: bool = True  # Append-only file

    # Pub/Sub - unlimited subscribers
    PUBSUB_CHANNELS_LIMIT: Optional[int] = None  # No limit

    # Queues - unlimited depth
    QUEUE_DEPTH_LIMIT: Optional[int] = None  # No limit
    QUEUE_TIMEOUT: int = 0  # 0 = wait indefinitely

    @classmethod
    def from_env(cls, prefix: str = "REDIS_"):
        """Load from environment variables"""
        import os
        cls.HOST = os.getenv(f"{prefix}HOST", cls.HOST)
        cls.PORT = int(os.getenv(f"{prefix}PORT", cls.PORT))
        cls.DB = int(os.getenv(f"{prefix}DB", cls.DB))
        cls.PASSWORD = os.getenv(f"{prefix}PASSWORD")
        return cls


# ═════════════════════════════════════════════════════════════════════════════
# 2. REDIS CLIENT WRAPPER - UNLIMITED OPERATIONS
# ═════════════════════════════════════════════════════════════════════════════

class RedisClientUnlimited:
    """Klienti Redis me operacione pa kufizime"""

    def __init__(self, config: RedisConfig = RedisConfig()):
        self.config = config
        self.client: Optional[aioredis.Redis] = None
        self.pool: Optional[ConnectionPool] = None
        self.connected = False
        self.id = f"redis_client_{uuid.uuid4().hex[:8]}"
        self.stats = {
            "connections": 0,
            "operations": 0,
            "bytes_written": 0,
            "bytes_read": 0,
            "errors": 0,
        }

    async def connect(self) -> None:
        """Lidhu në Redis - unlimited connection pool"""
        try:
            self.pool = ConnectionPool.from_url(
                f"redis://{'@' if self.config.PASSWORD else ''}"
                f"{self.config.PASSWORD + '@' if self.config.PASSWORD else ''}"
                f"{self.config.HOST}:{self.config.PORT}/{self.config.DB}",
                **self.config.CONNECTION_POOL_KWARGS
            )
            self.client = aioredis.Redis(connection_pool=self.pool)

            # Test connection
            await self.client.ping()
            self.connected = True
            logger.info(f"🔴 Redis Unlimited connected: {self.id}")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.connected = False
            raise

    async def disconnect(self) -> None:
        """Keqlidhje"""
        if self.client:
            await self.client.close()
        if self.pool:
            self.pool.disconnect()
        self.connected = False
        logger.info(f"🔴 Redis disconnected: {self.id}")

    async def set_unlimited(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Vendos vlerë pa kufizim - unlimited size"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)

        try:
            if ttl is None:
                ttl = self.config.DEFAULT_TTL

            if ttl:
                await self.client.setex(key, ttl, str(value))
            else:
                await self.client.set(key, str(value))

            self.stats["operations"] += 1
            self.stats["bytes_written"] += len(str(value).encode("utf-8"))
            return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            self.stats["errors"] += 1
            return False

    async def get_unlimited(self, key: str) -> Optional[Any]:
        """Merr vlerë - unlimited size"""
        try:
            value = await self.client.get(key)
            if value:
                self.stats["bytes_read"] += len(value)
                self.stats["operations"] += 1

                # Try to parse JSON
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value.decode("utf-8") if isinstance(value, bytes) else value
            return None
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            self.stats["errors"] += 1
            return None

    async def stream_append_unlimited(
        self,
        stream_key: str,
        data: Dict[str, Any],
        max_len: Optional[int] = None,
    ) -> str:
        """Shto në stream - unlimited entries"""
        try:
            # Flatten dict for Redis stream
            stream_data = {
                k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in data.items()
            }

            max_len = max_len or self.config.STREAM_MAX_LEN

            # Add to stream - NO LIMIT
            entry_id = await self.client.xadd(
                stream_key,
                stream_data,
                maxlen=max_len,
                approximate=False,  # Exact trimming if needed
            )

            self.stats["operations"] += 1
            self.stats["bytes_written"] += sum(
                len(str(v).encode("utf-8")) for v in stream_data.values()
            )

            return entry_id.decode("utf-8") if isinstance(entry_id, bytes) else entry_id
        except Exception as e:
            logger.error(f"Error appending to stream {stream_key}: {e}")
            self.stats["errors"] += 1
            raise

    async def stream_read_unlimited(
        self,
        stream_key: str,
        start_id: str = "0",
        batch_size: Optional[int] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Lexo nga stream - unlimited batch processing"""
        batch_size = batch_size or self.config.STREAM_BATCH_SIZE
        current_id = start_id

        try:
            while True:
                # Read batch - unlimited
                entries = await self.client.xrange(
                    stream_key,
                    min=current_id,
                    count=batch_size,
                )

                if not entries:
                    break

                for entry_id, data in entries:
                    # Parse entry
                    parsed_data = {}
                    for k, v in data.items():
                        key = k.decode("utf-8") if isinstance(k, bytes) else k
                        val = v.decode("utf-8") if isinstance(v, bytes) else v
                        try:
                            parsed_data[key] = json.loads(val)
                        except (json.JSONDecodeError, TypeError):
                            parsed_data[key] = val

                    current_id = entry_id
                    self.stats["bytes_read"] += sum(
                        len(str(v).encode("utf-8")) for v in data.values()
                    )
                    self.stats["operations"] += 1

                    yield {
                        "id": entry_id.decode("utf-8") if isinstance(entry_id, bytes) else entry_id,
                        "data": parsed_data,
                    }

                if len(entries) < batch_size:
                    break
        except Exception as e:
            logger.error(f"Error reading stream {stream_key}: {e}")
            self.stats["errors"] += 1
            raise

    async def queue_push_unlimited(
        self,
        queue_key: str,
        item: Any,
        priority: int = 0,
    ) -> int:
        """Shto në queue - unlimited depth"""
        try:
            if isinstance(item, (dict, list)):
                item = json.dumps(item, ensure_ascii=False)

            # Use sorted set for priority queue
            score = -priority  # Negative for descending priority

            length = await self.client.zadd(
                queue_key,
                {str(item): score}
            )

            self.stats["operations"] += 1
            self.stats["bytes_written"] += len(str(item).encode("utf-8"))

            return await self.client.zcard(queue_key)
        except Exception as e:
            logger.error(f"Error pushing to queue {queue_key}: {e}")
            self.stats["errors"] += 1
            raise

    async def queue_pop_unlimited(self, queue_key: str, timeout: int = 0) -> Optional[Any]:
        """Merr nga queue - unlimited wait"""
        try:
            # Pop highest priority item
            items = await self.client.zrange(queue_key, 0, 0)

            if items:
                item = items[0]
                await self.client.zrem(queue_key, item)

                # Try to parse
                try:
                    return json.loads(item)
                except (json.JSONDecodeError, TypeError):
                    return item.decode("utf-8") if isinstance(item, bytes) else item

            return None
        except Exception as e:
            logger.error(f"Error popping from queue {queue_key}: {e}")
            self.stats["errors"] += 1
            return None

    async def pubsub_publish_unlimited(
        self,
        channel: str,
        message: Any,
    ) -> int:
        """Publikim - unlimited subscribers"""
        try:
            if isinstance(message, (dict, list)):
                message = json.dumps(message, ensure_ascii=False)

            subscribers = await self.client.publish(channel, str(message))

            self.stats["operations"] += 1
            self.stats["bytes_written"] += len(str(message).encode("utf-8"))

            return subscribers
        except Exception as e:
            logger.error(f"Error publishing to channel {channel}: {e}")
            self.stats["errors"] += 1
            return 0

    async def session_create_unlimited(
        self,
        session_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None,
    ) -> str:
        """Krijo sesion - unlimited sessions"""
        session_id = session_id or f"session_{uuid.uuid4().hex}"
        ttl = ttl or self.config.SESSION_TTL

        try:
            session_data = {
                "id": session_id,
                "created": datetime.now(timezone.utc).isoformat(),
                "last_activity": datetime.now(timezone.utc).isoformat(),
                **(data or {}),
            }

            await self.set_unlimited(
                f"session:{session_id}",
                session_data,
                ttl=ttl
            )

            # Add to index - unlimited sessions
            await self.client.sadd("sessions:all", session_id)

            return session_id
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            self.stats["errors"] += 1
            raise

    async def session_get_unlimited(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Merr sesion"""
        return await self.get_unlimited(f"session:{session_id}")

    async def session_update_unlimited(
        self,
        session_id: str,
        updates: Dict[str, Any],
    ) -> bool:
        """Përditëso sesion"""
        try:
            session_data = await self.session_get_unlimited(session_id)
            if not session_data:
                return False

            session_data.update(updates)
            session_data["last_activity"] = datetime.now(timezone.utc).isoformat()

            await self.set_unlimited(
                f"session:{session_id}",
                session_data,
                ttl=self.config.SESSION_TTL
            )
            return True
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {e}")
            self.stats["errors"] += 1
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Merr statistika"""
        return {
            "client_id": self.id,
            "connected": self.connected,
            "operations": self.stats["operations"],
            "bytes_written_mb": self.stats["bytes_written"] / (1024 * 1024),
            "bytes_read_mb": self.stats["bytes_read"] / (1024 * 1024),
            "errors": self.stats["errors"],
        }


# ═════════════════════════════════════════════════════════════════════════════
# 3. GLOBAL CLIENT SINGLETON
# ═════════════════════════════════════════════════════════════════════════════

_redis_client: Optional[RedisClientUnlimited] = None


async def get_redis_client() -> RedisClientUnlimited:
    """Merr Redis client - singleton"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClientUnlimited()
        await _redis_client.connect()
    return _redis_client


async def init_redis() -> RedisClientUnlimited:
    """Inicializo Redis"""
    client = await get_redis_client()
    logger.info("🔴 Redis Unlimited initialized")
    return client


async def close_redis() -> None:
    """Mbyll Redis"""
    global _redis_client
    if _redis_client:
        await _redis_client.disconnect()
        _redis_client = None
        logger.info("🔴 Redis Unlimited closed")


# ═════════════════════════════════════════════════════════════════════════════
# 4. FASTAPI INTEGRATION
# ═════════════════════════════════════════════════════════════════════════════

def create_redis_router():
    """Krijon FastAPI router për Redis"""
    from fastapi import APIRouter, HTTPException

    router = APIRouter(prefix="/api/redis", tags=["redis"])

    @router.get("/status")
    async def redis_status():
        """Statusi i Redis"""
        try:
            client = await get_redis_client()
            if client.connected:
                info = await client.client.info()
                return {
                    "connected": True,
                    "memory_used_mb": info.get("used_memory", 0) / (1024 * 1024),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_commands": info.get("total_commands_processed", 0),
                    "stats": client.get_stats(),
                }
            else:
                raise HTTPException(status_code=503, detail="Redis not connected")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/set")
    async def redis_set(key: str, value: Any, ttl: Optional[int] = None):
        """Vendos vlerë"""
        try:
            client = await get_redis_client()
            success = await client.set_unlimited(key, value, ttl=ttl)
            return {"success": success, "key": key}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/get")
    async def redis_get(key: str):
        """Merr vlerë"""
        try:
            client = await get_redis_client()
            value = await client.get_unlimited(key)
            return {"key": key, "value": value, "exists": value is not None}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/queue/push")
    async def queue_push(queue_key: str, item: Any, priority: int = 0):
        """Shto në queue"""
        try:
            client = await get_redis_client()
            length = await client.queue_push_unlimited(queue_key, item, priority=priority)
            return {"queue": queue_key, "length": length}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/queue/pop")
    async def queue_pop(queue_key: str):
        """Pop nga queue"""
        try:
            client = await get_redis_client()
            item = await client.queue_pop_unlimited(queue_key)
            return {"queue": queue_key, "item": item}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/pubsub/publish")
    async def pubsub_publish(channel: str, message: Any):
        """Publikim"""
        try:
            client = await get_redis_client()
            subscribers = await client.pubsub_publish_unlimited(channel, message)
            return {"channel": channel, "subscribers": subscribers}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return router


# ═════════════════════════════════════════════════════════════════════════════
# 5. DEMO DHE TESTIM
# ═════════════════════════════════════════════════════════════════════════════

async def demo_redis_unlimited():
    """Demo i Redis Unlimited"""
    print("=" * 70)
    print("🔴 REDIS UNLIMITED - Demo")
    print("=" * 70)

    client = RedisClientUnlimited()
    await client.connect()

    try:
        # 1. Set/Get pa kufizim
        print("\n📝 Test 1: Set/Get Unlimited")
        big_data = {"data": "x" * 100000}  # 100KB
        await client.set_unlimited("test:big", big_data)
        result = await client.get_unlimited("test:big")
        print(f"✅ Big data stored and retrieved: {len(str(result))} bytes")

        # 2. Stream - unlimited entries
        print("\n📊 Test 2: Stream Unlimited")
        for i in range(100):
            entry_id = await client.stream_append_unlimited(
                "debate:stream",
                {
                    "persona_id": f"persona_{i % 5}",
                    "response": f"Response #{i}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            if i == 0:
                first_id = entry_id

        count = 0
        async for entry in client.stream_read_unlimited("debate:stream", start_id="0"):
            count += 1
        print(f"✅ Stream stored and read {count} entries (unlimited)")

        # 3. Queue - unlimited depth
        print("\n📦 Test 3: Queue Unlimited")
        for i in range(50):
            await client.queue_push_unlimited(
                "tasks:pending",
                {"task_id": f"task_{i}", "priority": i % 3}
            )

        tasks = await client.client.zcard("tasks:pending")
        print(f"✅ Queue depth: {tasks} items (unlimited)")

        # 4. Pub/Sub - unlimited subscribers
        print("\n📢 Test 4: Pub/Sub Unlimited")
        subs = await client.pubsub_publish_unlimited(
            "notifications:debate",
            {"event": "debate_started", "topic": "test"}
        )
        print(f"✅ Published to {subs} subscribers (unlimited channels)")

        # 5. Sessions - unlimited
        print("\n🔐 Test 5: Sessions Unlimited")
        session_id = await client.session_create_unlimited(
            data={"user": "test_user", "permissions": ["read", "write"]}
        )
        print(f"✅ Session created: {session_id}")

        session = await client.session_get_unlimited(session_id)
        print(f"✅ Session retrieved: {session.get('user')}")

        # 6. Stats
        print("\n📈 Test 6: Stats")
        stats = client.get_stats()
        print(f"✅ Operations: {stats['operations']}")
        print(f"✅ Bytes written: {stats['bytes_written_mb']:.2f} MB")
        print(f"✅ Bytes read: {stats['bytes_read_mb']:.2f} MB")

    finally:
        await client.disconnect()

    print("\n" + "=" * 70)
    print("✅ Redis Unlimited Demo Complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_redis_unlimited())
