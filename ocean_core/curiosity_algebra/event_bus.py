# -*- coding: utf-8 -*-
"""
🌊 EVENT BUS - Deti ku derdhen të gjitha sinjalet
=================================================
Unified Event Stream për të gjitha modulet, sensorët, shërbimet.
"""

import uuid
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
from collections import deque

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Llojet e ngjarjeve në sistem"""
    METRIC = "metric"
    LOG = "log"
    ANOMALY = "anomaly"
    INTERACTION = "interaction"
    HEALTH_CHECK = "health_check"
    SIGNAL = "signal"
    CELL_UPDATE = "cell_update"
    QUERY = "query"
    RESPONSE = "response"
    ALERT = "alert"
    CURIOSITY = "curiosity"


@dataclass
class Event:
    """
    Një ngjarje në sistemin Curiosity Ocean.
    Çdo sinjal që hyn në det është një Event.
    """
    source: str
    type: EventType = EventType.SIGNAL
    payload: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 1.0
    tags: List[str] = field(default_factory=list)
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "type": self.type.value if isinstance(self.type, EventType) else self.type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "tags": self.tags,
            "processed": self.processed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        return cls(
            id=data.get("id", f"evt_{uuid.uuid4().hex[:12]}"),
            source=data.get("source", "unknown"),
            type=EventType(data.get("type", "signal")),
            payload=data.get("payload", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]) if "timestamp" in data else datetime.now(timezone.utc),
            confidence=data.get("confidence", 1.0),
            tags=data.get("tags", [])
        )


class EventBus:
    """
    🌊 Deti i Sinjaleve - Unified Event Stream
    
    Çdo modul publikon këtu. Curiosity Ocean dëgjon gjithçka.
    """
    
    def __init__(self, max_history: int = 10000):
        self.subscribers: List[Callable[[Event], None]] = []
        self.async_subscribers: List[Callable[[Event], Any]] = []
        self.history: deque = deque(maxlen=max_history)
        self.event_counts: Dict[str, int] = {}
        self.source_counts: Dict[str, int] = {}
        self._lock = asyncio.Lock()
        
        logger.info("🌊 EventBus initialized - Deti i sinjaleve është gati")
    
    def subscribe(self, handler: Callable[[Event], None]) -> None:
        """Regjistro një subscriber sinkron"""
        self.subscribers.append(handler)
        logger.debug(f"📡 New subscriber registered: {handler.__name__}")
    
    def subscribe_async(self, handler: Callable[[Event], Any]) -> None:
        """Regjistro një subscriber asinkron"""
        self.async_subscribers.append(handler)
        logger.debug(f"📡 New async subscriber registered: {handler.__name__}")
    
    def unsubscribe(self, handler: Callable) -> None:
        """Hiq një subscriber"""
        if handler in self.subscribers:
            self.subscribers.remove(handler)
        if handler in self.async_subscribers:
            self.async_subscribers.remove(handler)
    
    def publish(self, event: Event) -> None:
        """
        Publiko një ngjarje në det.
        Të gjithë subscribers do të njoftohen.
        """
        # Ruaj në histori
        self.history.append(event)
        
        # Numëro sipas tipit
        event_type = event.type.value if isinstance(event.type, EventType) else event.type
        self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
        self.source_counts[event.source] = self.source_counts.get(event.source, 0) + 1
        
        # Njofto subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.error(f"❌ Subscriber error: {e}")
        
        logger.debug(f"📨 Event published: {event.id} from {event.source}")
    
    async def publish_async(self, event: Event) -> None:
        """Publiko një ngjarje asinkronisht"""
        async with self._lock:
            self.history.append(event)
            
            event_type = event.type.value if isinstance(event.type, EventType) else event.type
            self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
            self.source_counts[event.source] = self.source_counts.get(event.source, 0) + 1
        
        # Njofto async subscribers
        tasks = []
        for subscriber in self.async_subscribers:
            tasks.append(asyncio.create_task(subscriber(event)))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Njofto sync subscribers
        for subscriber in self.subscribers:
            try:
                subscriber(event)
            except Exception as e:
                logger.error(f"❌ Subscriber error: {e}")
    
    def get_recent(self, count: int = 100) -> List[Event]:
        """Merr ngjarjet e fundit"""
        return list(self.history)[-count:]
    
    def get_by_source(self, source: str, count: int = 100) -> List[Event]:
        """Merr ngjarjet nga një burim specifik"""
        return [e for e in self.history if e.source == source][-count:]
    
    def get_by_type(self, event_type: EventType, count: int = 100) -> List[Event]:
        """Merr ngjarjet sipas tipit"""
        return [e for e in self.history if e.type == event_type][-count:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistikat e detit"""
        return {
            "total_events": len(self.history),
            "max_capacity": self.history.maxlen,
            "subscribers": len(self.subscribers) + len(self.async_subscribers),
            "event_counts": self.event_counts,
            "source_counts": self.source_counts,
            "unique_sources": len(self.source_counts)
        }
    
    def clear(self) -> None:
        """Pastro historinë"""
        self.history.clear()
        self.event_counts.clear()
        self.source_counts.clear()


# Singleton instance
_event_bus: Optional[EventBus] = None

def get_event_bus() -> EventBus:
    """Merr instancën globale të EventBus"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus
