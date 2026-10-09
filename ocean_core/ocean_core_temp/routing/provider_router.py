"""
Provider Router - Zgjedh provider-in e duhur bazuar në kërkesë
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass

from ocean_core.providers import get_provider_registry, ProviderRequest, ProviderResponse, ProviderStatus

logger = logging.getLogger("provider-router")

@dataclass
class RoutingContext:
    """Konteksti i routing-ut"""
    request_type: str  # text, vision, reasoning, research, multimodal
    preferred_provider: Optional[str] = None
    capabilities: Dict[str, Any] = None
    fallback_allowed: bool = True
    timeout: int = 60

class ProviderRouter:
    """Router që zgjedh provider-in më të mirë bazuar në kërkesë"""
    
    def __init__(self):
        self.registry = get_provider_registry()
        self._routing_cache = {}
    
    def get_provider_for_request(self, request: ProviderRequest) -> str:
        """Përcakton provider-in më të mirë për një kërkesë"""
        
        # 1. Nëse specifikohet provider në metadata
        if request.metadata.get("provider"):
            return request.metadata["provider"]
        
        # 2. Bazuar në stigma profile
        if request.stigma_profile == "lightning":
            return "ollama"  # Më i shpejti
        
        if request.stigma_profile == "conservative":
            # Kërkon provider më të thellë
            available = self.registry.list_providers()
            if "wwwmmm" in available:
                return "wwwmmm"
            if "clx" in available:
                return "clx"
            return "ollama"
        
        # 3. Bazuar në llojin e kërkesës
        if request.metadata.get("image") or request.metadata.get("vision"):
            return "llava" if "llava" in self.registry.list_providers() else "ollama"
        
        if request.metadata.get("command") or request.metadata.get("inspect"):
            return "xlc" if "xlc" in self.registry.list_providers() else "ollama"
        
        if request.metadata.get("telemetry") or request.metadata.get("monitor"):
            return "trinity" if "trinity" in self.registry.list_providers() else "ollama"
        
        # 4. Default: përdor provider-in e parazgjedhur
        return self.registry._default_provider or "ollama"
    
    async def route(self, request: ProviderRequest) -> ProviderResponse:
        """Rrugëzon kërkesën te provider-i i duhur"""
        provider_name = self.get_provider_for_request(request)
        provider = self.registry.get_provider(provider_name)
        
        if provider is None:
            logger.warning(f"Provider {provider_name} not found, using default")
            provider = self.registry.get_default()
        
        if provider is None:
            return ProviderResponse(
                content="No provider available",
                model=request.model,
                provider="none",
                status=ProviderStatus.UNAVAILABLE,
                error="No provider found"
            )
        
        logger.info(f"Routing to {provider_name} for request: {request.prompt[:50]}...")
        return await provider.generate(request)
    
    async def route_stream(self, request: ProviderRequest):
        """Rrugëzon kërkesën për streaming"""
        provider_name = self.get_provider_for_request(request)
        provider = self.registry.get_provider(provider_name)
        
        if provider is None:
            provider = self.registry.get_default()
        
        if provider is None:
            yield ProviderResponse(
                content="No provider available",
                model=request.model,
                provider="none",
                status=ProviderStatus.UNAVAILABLE,
                error="No provider found"
            )
            return
        
        async for chunk in provider.stream(request):
            yield chunk
    
    def list_available_providers(self) -> list:
        """Liston provider-at e disponueshëm"""
        return self.registry.list_providers()
    
    async def health_check_all(self) -> dict:
        """Kontrollon shëndetin e të gjithë provider-ave"""
        return await self.registry.health_check_all()

# Singleton
_provider_router = None

def get_provider_router() -> ProviderRouter:
    global _provider_router
    if _provider_router is None:
        _provider_router = ProviderRouter()
    return _provider_router
