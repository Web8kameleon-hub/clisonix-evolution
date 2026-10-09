"""
Runtime Initialization - Inicializon të gjithë runtime-in
"""

import logging
from ocean_core.pipelines.chat import ChatPipeline
from ocean_core.pipelines.vision import VisionPipeline
from ocean_core.pipelines.reasoning import ReasoningPipeline
from ocean_core.pipelines.research import ResearchPipeline
from ocean_core.runtime.pipeline_registry import get_pipeline_registry
from ocean_core.runtime.capability_registry import get_capability_registry
from ocean_core.providers.init import initialize_all_providers

logger = logging.getLogger("runtime-init")

_runtime = None

def initialize_runtime():
    global _runtime
    if _runtime is not None:
        return _runtime

    providers = initialize_all_providers()
    logger.info("✅ Providers initialized")

    registry = get_pipeline_registry()
    registry.register("chat", ChatPipeline)
    registry.register("vision", VisionPipeline)
    registry.register("reasoning", ReasoningPipeline)
    registry.register("research", ResearchPipeline)
    logger.info(f"✅ Pipelines registered: {registry.list_pipelines()}")

    cap_reg = get_capability_registry()
    cap_reg.register("ollama", ["text", "chat"])
    cap_reg.register("llava", ["text", "vision", "multimodal"])
    cap_reg.register("clx", ["text", "reasoning", "logic"])
    cap_reg.register("wwwmmm", ["text", "reasoning", "research", "resonance"])
    logger.info(f"✅ Capabilities registered: {cap_reg.list_all_capabilities()}")

    _runtime = {
        "providers": providers,
        "registry": registry,
        "capabilities": cap_reg,
        "initialized": True,
    }
    logger.info("✅ Runtime initialized successfully")
    return _runtime

def get_runtime():
    return initialize_runtime()
