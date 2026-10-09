"""
Model Selector - Zgjedh modelin më të mirë për detyrën
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger("model-selector")

@dataclass
class ModelInfo:
    name: str
    provider: str
    capabilities: List[str]
    context_length: int = 8192
    speed: str = "medium"  # fast, medium, slow
    quality: str = "medium"  # low, medium, high

class ModelSelector:
    """Zgjedh modelin më të mirë për një detyrë"""
    
    def __init__(self):
        self._models = {}
        self._register_default_models()
    
    def _register_default_models(self):
        """Regjistron modelet e parazgjedhura"""
        self._models = {
            "llama3.1:8b": ModelInfo(
                name="llama3.1:8b",
                provider="ollama",
                capabilities=["text", "chat", "reasoning"],
                context_length=8192,
                speed="fast",
                quality="medium"
            ),
            "llama3.2": ModelInfo(
                name="llama3.2",
                provider="ollama",
                capabilities=["text", "chat", "reasoning"],
                context_length=8192,
                speed="fast",
                quality="medium"
            ),
            "llava": ModelInfo(
                name="llava",
                provider="llava",
                capabilities=["text", "vision", "multimodal"],
                context_length=4096,
                speed="medium",
                quality="medium"
            ),
            "clx": ModelInfo(
                name="clx",
                provider="clx",
                capabilities=["text", "reasoning", "research", "logic"],
                context_length=32768,
                speed="medium",
                quality="high"
            ),
            "wwwmmm": ModelInfo(
                name="wwwmmm",
                provider="wwwmmm",
                capabilities=["text", "reasoning", "research", "resonance"],
                context_length=131072,
                speed="medium",
                quality="high"
            )
        }
    
    def register_model(self, model_info: ModelInfo):
        """Regjistron një model të ri"""
        self._models[model_info.name] = model_info
        logger.info(f"Registered model: {model_info.name} ({model_info.provider})")
    
    def select_model(self, capabilities: List[str], speed: str = "medium") -> Optional[str]:
        """Zgjedh modelin më të mirë"""
        candidates = []
        
        for name, info in self._models.items():
            # Kontrollon nëse modeli ka të gjitha aftësitë e kërkuara
            if all(cap in info.capabilities for cap in capabilities):
                candidates.append((name, info))
        
        if not candidates:
            return None
        
        # Rendit sipas shpejtësisë dhe cilësisë
        speed_order = {"fast": 3, "medium": 2, "slow": 1}
        quality_order = {"high": 3, "medium": 2, "low": 1}
        
        best = max(candidates, key=lambda x: (
            speed_order.get(x[1].speed, 0),
            quality_order.get(x[1].quality, 0),
            x[1].context_length
        ))
        
        return best[0]
    
    def get_model_info(self, name: str) -> Optional[ModelInfo]:
        """Kthen informacionin e një modeli"""
        return self._models.get(name)
    
    def list_models(self) -> List[str]:
        """Liston të gjithë modelet"""
        return list(self._models.keys())

# Singleton
_model_selector = None

def get_model_selector() -> ModelSelector:
    global _model_selector
    if _model_selector is None:
        _model_selector = ModelSelector()
    return _model_selector
