import logging
from typing import List, Dict, Any
from .base import BaseProvider, ProviderType, ProviderStatus, ProviderRequest, ProviderResponse
from .wwwmmm_provider import WWWMMMProvider

logger = logging.getLogger("lightning-provider")

class LightningProvider(BaseProvider):
    def __init__(self):
        self._status = ProviderStatus.AVAILABLE
        self._delegate = WWWMMMProvider()

    @property
    def name(self) -> str:
        return "lightning"

    @property
    def type(self) -> ProviderType:
        return ProviderType.WWWMMM

    async def health_check(self) -> ProviderStatus:
        return ProviderStatus.AVAILABLE

    def get_models(self) -> List[str]:
        return ["lightning-fast", "lightning-medium"]

    def get_capabilities(self) -> Dict[str, Any]:
        return {"streaming": True, "speed": "ultra-fast", "no_warmup": True}

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        base = await self._delegate.generate(request)
        return ProviderResponse(
            content=base.content,
            model=base.model,
            provider=self.name,
            status=base.status,
            metadata={**base.metadata, "delegated_provider": "wwwmmm"},
            error=base.error,
            latency_ms=base.latency_ms,
            resonance=base.resonance,
        )

    async def stream(self, request: ProviderRequest):
        async for item in self._delegate.stream(request):
            yield ProviderResponse(
                content=item.content,
                model=item.model,
                provider=self.name,
                status=item.status,
                metadata={**item.metadata, "delegated_provider": "wwwmmm"},
                error=item.error,
                latency_ms=item.latency_ms,
                resonance=item.resonance,
            )
