"""
Vision Pipeline - Pipeline për vision/multimodal
"""

import logging
from typing import Dict, Any, Optional
from ocean_core.routing.provider_router import get_provider_router
from ocean_core.providers import ProviderRequest

logger = logging.getLogger("vision-pipeline")

class VisionPipeline:
    """Pipeline për vision dhe multimodalitet"""
    
    def __init__(self):
        self.router = get_provider_router()
        self.name = "vision"
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ekzekuton pipeline-in e vision-it"""
        prompt = context.get("prompt", "")
        image = context.get("image")
        model = context.get("model", "llava")
        temperature = context.get("temperature", 0.7)
        
        request = ProviderRequest(
            prompt=prompt,
            model=model,
            temperature=temperature,
            stream=context.get("stream", False),
            metadata={
                "image": image,
                "vision": True,
                "provider": context.get("provider", "llava")
            }
        )
        
        if context.get("stream", False):
            return {"stream": True, "request": request}
        else:
            response = await self.router.route(request)
            return {
                "content": response.content,
                "provider": response.provider,
                "model": response.model,
                "latency_ms": response.latency_ms,
                "status": response.status.value,
                "error": response.error
            }
    
    async def stream_execute(self, context: Dict[str, Any]):
        """Ekzekuton pipeline-in me streaming"""
        prompt = context.get("prompt", "")
        image = context.get("image")
        model = context.get("model", "llava")
        temperature = context.get("temperature", 0.7)
        
        request = ProviderRequest(
            prompt=prompt,
            model=model,
            temperature=temperature,
            stream=True,
            metadata={
                "image": image,
                "vision": True,
                "provider": context.get("provider", "llava")
            }
        )
        
        async for chunk in self.router.route_stream(request):
            yield chunk.content
