import aiohttp
import asyncio
import json
import time
import logging
import os
import socket
from typing import List, Dict, Any, Optional
from .base import BaseProvider, ProviderType, ProviderStatus, ProviderRequest, ProviderResponse

logger = logging.getLogger("ollama-provider")

class OllamaProvider(BaseProvider):
    def __init__(self, host: Optional[str] = None, model: str = "llama3.1:8b"):
        if host is None:
            host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self._host = host.rstrip("/")
        self._default_model = model
        self._session: Optional[aiohttp.ClientSession] = None
        self._status = ProviderStatus.UNKNOWN
        self._models_cache: List[str] = []

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def type(self) -> ProviderType:
        return ProviderType.OLLAMA

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(ttl_dns_cache=300)
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=60)
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def health_check(self) -> ProviderStatus:
        try:
            session = await self._get_session()
            async with session.get(f"{self._host}/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    self._models_cache = [m["name"] for m in data.get("models", [])]
                    self._status = ProviderStatus.AVAILABLE if self._models_cache else ProviderStatus.DEGRADED
                    return self._status
                self._status = ProviderStatus.UNAVAILABLE
                return self._status
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._status = ProviderStatus.UNAVAILABLE
            return self._status

    def get_models(self) -> List[str]:
        return self._models_cache or ["llama3.2", "llava", "mistral"]

    def get_capabilities(self) -> Dict[str, Any]:
        return {"streaming": True, "vision": "llava" in self.get_models(), "context_length": 8192}

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        start = time.time()
        model = request.model or self._default_model
        try:
            session = await self._get_session()
            payload = {
                "model": model,
                "prompt": request.prompt,
                "stream": False,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "system": request.system_prompt
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            async with session.post(f"{self._host}/api/generate", json=payload) as resp:
                elapsed = (time.time() - start) * 1000
                if resp.status == 200:
                    data = await resp.json()
                    return ProviderResponse(
                        content=data.get("response", ""),
                        model=model,
                        provider=self.name,
                        status=ProviderStatus.AVAILABLE,
                        latency_ms=elapsed
                    )
                else:
                    text = await resp.text()
                    return ProviderResponse(
                        content="",
                        model=model,
                        provider=self.name,
                        status=ProviderStatus.UNAVAILABLE,
                        error=f"HTTP {resp.status}: {text}",
                        latency_ms=elapsed
                    )
        except Exception as e:
            return ProviderResponse(
                content="",
                model=model,
                provider=self.name,
                status=ProviderStatus.UNAVAILABLE,
                error=str(e),
                latency_ms=(time.time() - start) * 1000
            )

    async def stream(self, request: ProviderRequest):
        model = request.model or self._default_model
        try:
            session = await self._get_session()
            payload = {
                "model": model,
                "prompt": request.prompt,
                "stream": True,
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "system": request.system_prompt
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            async with session.post(f"{self._host}/api/generate", json=payload) as resp:
                if resp.status == 200:
                    async for line in resp.content:
                        if line:
                            try:
                                data = json.loads(line.decode('utf-8'))
                                yield ProviderResponse(
                                    content=data.get("response", ""),
                                    model=model,
                                    provider=self.name,
                                    status=ProviderStatus.AVAILABLE,
                                    metadata={"done": data.get("done", False)}
                                )
                                if data.get("done", False):
                                    break
                            except Exception:
                                continue
                else:
                    yield ProviderResponse(
                        content="",
                        model=model,
                        provider=self.name,
                        status=ProviderStatus.UNAVAILABLE,
                        error=f"HTTP {resp.status}"
                    )
        except Exception as e:
            yield ProviderResponse(
                content="",
                model=model,
                provider=self.name,
                status=ProviderStatus.UNAVAILABLE,
                error=str(e)
            )
