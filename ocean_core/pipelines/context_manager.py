#!/usr/bin/env python3
"""
CONTEXT MANAGER
===============
Menaxhon kontekstin e bisedës dhe memorien e sesionit.
"""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ContextManager")


@dataclass
class Message:
    """Një mesazh në bisedë"""
    role: str  # user, assistant, system
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Konteksti i një bisede"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def message_count(self) -> int:
        return len(self.messages)
    
    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at
    
    @property
    def idle_seconds(self) -> float:
        return time.time() - self.last_activity


class ContextManager:
    """Menaxher i kontekstit të bisedave"""
    
    def __init__(
        self, 
        max_history: int = 50,
        session_timeout: int = 3600,  # 1 hour
        max_sessions: int = 1000
    ):
        self.sessions: Dict[str, ConversationContext] = {}
        self.max_history = max_history
        self.session_timeout = session_timeout
        self.max_sessions = max_sessions
        logger.info(f"✅ ContextManager initialized (max_history={max_history})")
    
    def _generate_session_id(self, user_id: Optional[str] = None) -> str:
        """Gjenero ID unike për sesion"""
        base = f"{user_id or 'anon'}:{time.time()}"
        return hashlib.sha256(base.encode()).hexdigest()[:16]
    
    def create_session(
        self, 
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ConversationContext:
        """Krijo sesion të ri"""
        self._cleanup_expired()
        
        if len(self.sessions) >= self.max_sessions:
            # Remove oldest session
            oldest = min(self.sessions.values(), key=lambda x: x.last_activity)
            del self.sessions[oldest.session_id]
        
        sid = session_id or self._generate_session_id(user_id)
        ctx = ConversationContext(session_id=sid, user_id=user_id)
        self.sessions[sid] = ctx
        
        logger.debug(f"Created session: {sid}")
        return ctx
    
    def get_session(self, session_id: str) -> Optional[ConversationContext]:
        """Merr sesionin nëse ekziston dhe nuk ka skaduar"""
        ctx = self.sessions.get(session_id)
        if ctx and ctx.idle_seconds < self.session_timeout:
            ctx.last_activity = time.time()
            return ctx
        return None
    
    def get_or_create(
        self, 
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> ConversationContext:
        """Merr sesionin ekzistues ose krijo të ri"""
        if session_id:
            ctx = self.get_session(session_id)
            if ctx:
                return ctx
        return self.create_session(session_id, user_id)
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Shto mesazh në sesion"""
        ctx = self.get_session(session_id)
        if not ctx:
            return False
        
        msg = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        ctx.messages.append(msg)
        
        # Trim history if too long
        if len(ctx.messages) > self.max_history:
            ctx.messages = ctx.messages[-self.max_history:]
        
        ctx.last_activity = time.time()
        return True
    
    def get_history(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """Merr historinë e mesazheve në formatin e Ollama"""
        ctx = self.get_session(session_id)
        if not ctx:
            return []
        
        messages = ctx.messages[-limit:]
        return [
            {"role": m.role, "content": m.content}
            for m in messages
        ]
    
    def get_full_context(self, session_id: str) -> Optional[str]:
        """Merr kontekstin e plotë si tekst"""
        ctx = self.get_session(session_id)
        if not ctx:
            return None
        
        parts = []
        for msg in ctx.messages[-20:]:
            role = "User" if msg.role == "user" else "Ocean"
            parts.append(f"{role}: {msg.content}")
        
        return "\n\n".join(parts)
    
    def clear_session(self, session_id: str) -> bool:
        """Pastro një sesion"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def _cleanup_expired(self):
        """Pastro sesionet e skaduara"""
        now = time.time()
        expired = [
            sid for sid, ctx in self.sessions.items()
            if ctx.idle_seconds > self.session_timeout
        ]
        for sid in expired:
            del self.sessions[sid]
        
        if expired:
            logger.debug(f"Cleaned up {len(expired)} expired sessions")
    
    def get_stats(self) -> Dict[str, Any]:
        """Merr statistikat"""
        self._cleanup_expired()
        
        total_messages = sum(len(ctx.messages) for ctx in self.sessions.values())
        
        return {
            "active_sessions": len(self.sessions),
            "total_messages": total_messages,
            "max_sessions": self.max_sessions,
            "session_timeout_seconds": self.session_timeout,
            "oldest_session_age": max(
                (ctx.age_seconds for ctx in self.sessions.values()), 
                default=0
            )
        }


# Singleton
_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Merr instancën singleton"""
    global _manager
    if _manager is None:
        _manager = ContextManager()
    return _manager
