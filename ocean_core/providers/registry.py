import logging
from typing import Dict, List, Optional
from .base import BaseProvider, ProviderStatus, ProviderRequest, ProviderResponse

logger = logging.getLogger("provider-registry")

class ProviderRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
            cls._instance._default_provider = None
        return cls._instance

    def register(self, provider: BaseProvider, default: bool = False):
        self._providers[provider.name] = provider
        if default or self._default_provider is None:
            self._default_provider = provider.name
        logger.info(f"Registered provider: {provider.name}")

    def get_provider(self, name: Optional[str] = None) -> Optional[BaseProvider]:
        name = name or self._default_provider
        return self._providers.get(name) if name else None

    def get_default(self) -> Optional[BaseProvider]:
        return self.get_provider()

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())

    async def health_check_all(self):
        results = {}
        for name, p in self._providers.items():
            results[name] = await p.health_check()
        return results

    async def generate(self, request: ProviderRequest, provider_name: Optional[str] = None) -> ProviderResponse:
        provider = self.get_provider(provider_name) or self.get_default()
        if provider is None:
            return ProviderResponse(
                content="No provider",
                model=request.model,
                provider="none",
                status=ProviderStatus.UNAVAILABLE,
                error="No provider found"
            )
        return await provider.generate(request)

    async def stream(self, request: ProviderRequest, provider_name: Optional[str] = None):
        provider = self.get_provider(provider_name) or self.get_default()
        if provider is None:
            yield ProviderResponse(
                content="No provider",
                model=request.model,
                provider="none",
                status=ProviderStatus.UNAVAILABLE,
                error="No provider found"
            )
            return
        async for resp in provider.stream(request):
            yield resp

_provider_registry = None

def get_provider_registry() -> ProviderRegistry:
    global _provider_registry
    if _provider_registry is None:
        _provider_registry = ProviderRegistry()
    return _provider_registry
