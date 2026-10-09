"""
Pipeline Registry - Regjistron dhe menaxhon pipeline-et
"""

import logging
from typing import Dict, Type, Any, Optional

logger = logging.getLogger("pipeline-registry")

class PipelineRegistry:
    """Regjistron pipeline-et e disponueshme"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._pipelines = {}
        return cls._instance
    
    def register(self, name: str, pipeline_class):
        """Regjistron një pipeline"""
        self._pipelines[name] = pipeline_class
        logger.info(f"Registered pipeline: {name}")
    
    def get_pipeline(self, name: str):
        """Merr një pipeline sipas emrit"""
        return self._pipelines.get(name)
    
    def list_pipelines(self) -> list:
        """Liston të gjithë pipeline-et"""
        return list(self._pipelines.keys())
    
    async def execute(self, name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ekzekuton një pipeline"""
        pipeline_class = self.get_pipeline(name)
        if pipeline_class is None:
            return {"error": f"Pipeline {name} not found"}
        
        pipeline = pipeline_class()
        return await pipeline.execute(context)
    
    async def stream_execute(self, name: str, context: Dict[str, Any]):
        """Ekzekuton një pipeline me streaming"""
        pipeline_class = self.get_pipeline(name)
        if pipeline_class is None:
            yield f"Error: Pipeline {name} not found"
            return
        
        pipeline = pipeline_class()
        async for chunk in pipeline.stream_execute(context):
            yield chunk

# Singleton
_pipeline_registry = None

def get_pipeline_registry() -> PipelineRegistry:
    global _pipeline_registry
    if _pipeline_registry is None:
        _pipeline_registry = PipelineRegistry()
    return _pipeline_registry
