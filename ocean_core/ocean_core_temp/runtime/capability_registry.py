"""
Capability Registry - Regjistron dhe menaxhon aftësitë e provider-ave
"""

import logging
from typing import Dict, List, Set, Any
from dataclasses import dataclass, field

logger = logging.getLogger("capability-registry")

@dataclass
class Capability:
    """Një aftësi e një provider-i"""
    name: str
    provider: str
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

class CapabilityRegistry:
    """Regjistron aftësitë e të gjithë provider-ave"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._capabilities = {}
            cls._instance._capability_map = {}
        return cls._instance
    
    def register(self, provider: str, capabilities: List[str], metadata: Dict[str, Any] = None):
        """Regjistron aftësitë e një provider-i"""
        if provider not in self._capabilities:
            self._capabilities[provider] = []
        
        for cap in capabilities:
            self._capabilities[provider].append(cap)
            if cap not in self._capability_map:
                self._capability_map[cap] = []
            self._capability_map[cap].append(provider)
        
        logger.info(f"Registered capabilities for {provider}: {capabilities}")
    
    def get_providers_for_capability(self, capability: str) -> List[str]:
        """Kthen provider-at që mbështesin një aftësi"""
        return self._capability_map.get(capability, [])
    
    def get_capabilities(self, provider: str) -> List[str]:
        """Kthen aftësitë e një provider-i"""
        return self._capabilities.get(provider, [])
    
    def get_best_provider(self, capabilities: List[str]) -> Optional[str]:
        """Gjen provider-in më të mirë për një listë aftësish"""
        providers = {}
        for cap in capabilities:
            for p in self.get_providers_for_capability(cap):
                providers[p] = providers.get(p, 0) + 1
        
        if not providers:
            return None
        
        # Kthe provider-in me më shumë aftësi
        return max(providers, key=providers.get)
    
    def has_capability(self, provider: str, capability: str) -> bool:
        """Kontrollon nëse një provider ka një aftësi"""
        return capability in self.get_capabilities(provider)
    
    def list_all_capabilities(self) -> Set[str]:
        """Liston të gjitha aftësitë e regjistruara"""
        return set(self._capability_map.keys())
    
    def list_all_providers(self) -> List[str]:
        """Liston të gjithë provider-at e regjistruar"""
        return list(self._capabilities.keys())

# Singleton
_capability_registry = None

def get_capability_registry() -> CapabilityRegistry:
    global _capability_registry
    if _capability_registry is None:
        _capability_registry = CapabilityRegistry()
    return _capability_registry
