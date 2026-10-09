"""
SERVICE BASE CLASS
==================
Base class for services to auto-register and heartbeat.
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Any, List, Optional

if TYPE_CHECKING:
    from services.registry import ServiceRegistry

try:
    from services.registry import init_registry as _init_registry
except ImportError:
    from registry import init_registry as _init_registry

logger = logging.getLogger(__name__)


class ServiceBase:
    """Base class for auto-registering services."""
    
    def __init__(
        self,
        name: str,
        host: str = "localhost",
        port: int = 8000,
        model: str = "unknown",
        capabilities: Optional[List[str]] = None,
        metadata: Optional[dict] = None
    ):
        self.name = name
        self.host = host
        self.port = port
        self.model = model
        self.capabilities = capabilities or []
        self.metadata = metadata or {}
        self.registry: Optional["ServiceRegistry"] = None
    
    async def register(self, firestore_client: Optional[Any] = None) -> bool:
        """Register this service in the registry."""
        try:
            self.registry = await _init_registry(firestore_client)
            if self.registry is None:
                logger.error("❌ Registry initialization returned None")
                return False
            
            # Register service
            success = await self.registry.register_service(
                name=self.name,
                host=self.host,
                port=self.port,
                model=self.model,
                capabilities=self.capabilities,
                metadata=self.metadata
            )
            
            if success:
                # Start heartbeat to keep registration alive
                await self.registry.start_heartbeat(service_name=self.name)
                logger.info(f"✅ {self.name} registered and ready")
            
            return success
        
        except Exception as e:
            logger.error(f"❌ Registration failed: {e}")
            return False
    
    async def shutdown(self):
        """Cleanup on shutdown."""
        if self.registry:
            await self.registry.deregister_service(self.name)
