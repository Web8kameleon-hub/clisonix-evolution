"""
Runtime Bus - Event-driven komunikimi midis komponentëve
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("runtime-bus")

class RuntimeEventType(Enum):
    REQUEST_RECEIVED = "request.received"
    PROVIDER_SELECTED = "provider.selected"
    PIPELINE_STARTED = "pipeline.started"
    PIPELINE_COMPLETED = "pipeline.completed"
    RESPONSE_SENT = "response.sent"
    ERROR_OCCURRED = "error.occurred"
    HEALTH_CHECK = "health.check"

@dataclass
class RuntimeEvent:
    """Event në Runtime Bus"""
    type: RuntimeEventType
    data: Any
    source: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    correlation_id: Optional[str] = None

class RuntimeBus:
    """Bus i runtime-it për komunikim event-driven"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers = {}
            cls._instance._event_history = []
            cls._instance._max_history = 1000
        return cls._instance
    
    def subscribe(self, event_type: RuntimeEventType, handler: Callable):
        """Regjistron një handler për një lloj eventi"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Subscribed handler for {event_type}")
    
    def unsubscribe(self, event_type: RuntimeEventType, handler: Callable):
        """Çregjistron një handler"""
        if event_type in self._handlers:
            self._handlers[event_type].remove(handler)
    
    async def emit(self, event: RuntimeEvent):
        """Dërgon një event"""
        logger.debug(f"Emitting {event.type}: {event.correlation_id}")
        
        # Ruaj historinë
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        
        # Thirr handler-at
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Handler failed: {e}")
    
    def get_history(self, limit: int = 100) -> List[RuntimeEvent]:
        """Kthen historinë e eventeve"""
        return self._event_history[-limit:]
    
    def clear_history(self):
        """Pastron historinë"""
        self._event_history.clear()

# Singleton
_runtime_bus = None

def get_runtime_bus() -> RuntimeBus:
    global _runtime_bus
    if _runtime_bus is None:
        _runtime_bus = RuntimeBus()
    return _runtime_bus
