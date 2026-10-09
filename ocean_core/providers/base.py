from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncGenerator, List
from dataclasses import dataclass, field
from enum import Enum

class ProviderType(Enum):
    OLLAMA = "ollama"
    LLAVA = "llava"
    CLX = "clx"
    XLC = "xlc"
    ASI = "asi"
    WWWMMM = "wwwmmm"
    NODEDB = "nodedb"
    TRINITY = "trinity"

class ProviderStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class ProviderRequest:
    prompt: str
    model: str = "default"
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    system_prompt: Optional[str] = None
    stigma_profile: str = "normal"
    resonance_depth: int = 3

@dataclass
class ProviderResponse:
    content: str
    model: str
    provider: str
    status: ProviderStatus
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    latency_ms: float = 0.0
    resonance: float = 0.0

class BaseProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str: pass
    @property
    @abstractmethod
    def type(self) -> ProviderType: pass
    @abstractmethod
    async def generate(self, request: ProviderRequest) -> ProviderResponse: pass
    @abstractmethod
    async def stream(self, request: ProviderRequest): pass
    @abstractmethod
    async def health_check(self) -> ProviderStatus: pass
    @abstractmethod
    def get_models(self) -> List[str]: pass
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]: pass
