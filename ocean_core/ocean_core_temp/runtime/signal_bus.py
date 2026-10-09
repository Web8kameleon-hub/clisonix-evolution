"""
Signal Bus - Komunikim i shpejtë midis komponentëve
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("signal-bus")

@dataclass
class Signal:
    """Signal i komunikimit"""
    name: str
    payload: Any
    source: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

class SignalBus:
    """Bus për sinjale të shpejta"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._signals = {}
            cls._instance._subscribers = {}
        return cls._instance
    
    def register(self, signal_name: str):
        """Regjistron një sinjal të ri"""
        if signal_name not in self._signals:
            self._signals[signal_name] = {
                "subscribers": [],
                "history": []
            }
        logger.debug(f"Registered signal: {signal_name}")
    
    def subscribe(self, signal_name: str, handler):
        """Regjistron një subscriber për një sinjal"""
        if signal_name not in self._signals:
            self.register(signal_name)
        self._signals[signal_name]["subscribers"].append(handler)
    
    def unsubscribe(self, signal_name: str, handler):
        """Çregjistron një subscriber"""
        if signal_name in self._signals:
            self._signals[signal_name]["subscribers"].remove(handler)
    
    async def emit(self, signal: Signal):
        """Dërgon një sinjal"""
        if signal.name not in self._signals:
            self.register(signal.name)
        
        # Ruaj historinë
        self._signals[signal.name]["history"].append(signal)
        if len(self._signals[signal.name]["history"]) > 100:
            self._signals[signal.name]["history"].pop(0)
        
        # Thirr subscriber-at
        for handler in self._signals[signal.name]["subscribers"]:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(signal)
                else:
                    handler(signal)
            except Exception as e:
                logger.error(f"Signal handler failed: {e}")
    
    def get_signal_history(self, signal_name: str, limit: int = 50) -> List[Signal]:
        """Kthen historinë e një sinjali"""
        if signal_name not in self._signals:
            return []
        return self._signals[signal_name]["history"][-limit:]
    
    def list_signals(self) -> List[str]:
        """Liston të gjithë sinjalet e regjistruar"""
        return list(self._signals.keys())

# Singleton
_signal_bus = None

def get_signal_bus() -> SignalBus:
    global _signal_bus
    if _signal_bus is None:
        _signal_bus = SignalBus()
    return _signal_bus
