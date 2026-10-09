# -*- coding: utf-8 -*-
"""
🧬 CELL REGISTRY - Anatomia e Organizmës
=========================================
Çdo modul regjistrohet si qelizë.
Të gjitha qelizat formojnë një graf të gjallë: G = (Cells, Edges)
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CellRole(Enum):
    """Rolet e qelizave në organizëm"""
    SENSOR = "sensor"           # Mbledh të dhëna
    PROCESSOR = "processor"     # Përpunon të dhëna
    GATEWAY = "gateway"         # Lidh me botën e jashtme
    UI = "ui"                   # Ndërfaqe përdoruesi
    LOGIC = "logic"             # Logjikë biznesi
    STORAGE = "storage"         # Ruajtje të dhënash
    ORCHESTRATOR = "orchestrator"  # Koordinon të tjerat
    MONITOR = "monitor"         # Monitoron gjendjen
    EXTERNAL = "external"       # Shërbim i jashtëm
    API = "api"                 # Endpoint API
    DATABASE = "database"       # Bazë të dhënash
    CACHE = "cache"             # Cache
    QUEUE = "queue"             # Message queue
    AI = "ai"                   # Inteligjencë artificiale
    CORE = "core"               # Komponent thelbësor


class CellState(Enum):
    """Gjendjet e mundshme të një qelize"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


@dataclass
class Cell:
    """
    Një qelizë në organizmin Clisonix.
    Çdo modul, sensor, shërbim ka një identitet qelizor.
    """
    id: str
    role: CellRole
    name: str = ""
    capabilities: List[str] = field(default_factory=list)
    state: CellState = CellState.UNKNOWN
    links: List[str] = field(default_factory=list)  # IDs of linked cells
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Callback për thirrje
    on_call: Optional[Callable[[str], Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "capabilities": self.capabilities,
            "state": self.state.value,
            "links": self.links,
            "metadata": self.metadata,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Cell':
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            role=CellRole(data.get("role", "logic")),
            capabilities=data.get("capabilities", []),
            state=CellState(data.get("state", "unknown")),
            links=data.get("links", []),
            metadata=data.get("metadata", {})
        )
    
    def heartbeat(self) -> None:
        """Rifresko heartbeat"""
        self.last_heartbeat = datetime.now(timezone.utc)
    
    def is_healthy(self, timeout_seconds: int = 60) -> bool:
        """Kontrollo nëse qeliza është e shëndetshme"""
        if self.state in [CellState.ERROR, CellState.OFFLINE]:
            return False
        age = (datetime.now(timezone.utc) - self.last_heartbeat).total_seconds()
        return age < timeout_seconds


class CellRegistry:
    """
    🧬 Regjistri i Qelizave - Cell Registry
    
    Mban gjurmët e të gjitha qelizave në organizëm.
    Formon grafin e lidhjeve ndërmjet tyre.
    """
    
    def __init__(self):
        self.cells: Dict[str, Cell] = {}
        self.edges: Set[tuple] = set()  # (from_id, to_id)
        self._role_index: Dict[CellRole, Set[str]] = {role: set() for role in CellRole}
        
        logger.info("🧬 CellRegistry initialized - Anatomia e organizmës është gati")
    
    def register(self, cell: Cell) -> None:
        """Regjistro një qelizë të re"""
        self.cells[cell.id] = cell
        self._role_index[cell.role].add(cell.id)
        
        # Shto edges për links
        for linked_id in cell.links:
            self.edges.add((cell.id, linked_id))
        
        logger.info(f"🧬 Cell registered: {cell.id} ({cell.role.value})")
    
    def register_simple(self, 
                        cell_id: str, 
                        role: str, 
                        name: str = "",
                        capabilities: List[str] = None,
                        links: List[str] = None,
                        metadata: Dict[str, Any] = None) -> Cell:
        """Regjistro një qelizë me parametra të thjeshtë"""
        cell = Cell(
            id=cell_id,
            name=name or cell_id,
            role=CellRole(role),
            capabilities=capabilities or [],
            links=links or [],
            metadata=metadata or {},
            state=CellState.ACTIVE
        )
        self.register(cell)
        return cell
    
    def unregister(self, cell_id: str) -> bool:
        """Hiq një qelizë nga regjistri"""
        if cell_id not in self.cells:
            return False
        
        cell = self.cells[cell_id]
        self._role_index[cell.role].discard(cell_id)
        
        # Hiq edges
        self.edges = {e for e in self.edges if cell_id not in e}
        
        del self.cells[cell_id]
        logger.info(f"🧬 Cell unregistered: {cell_id}")
        return True
    
    def get(self, cell_id: str) -> Optional[Cell]:
        """Merr një qelizë sipas ID"""
        return self.cells.get(cell_id)
    
    def query(self, role: CellRole = None, state: CellState = None) -> List[Cell]:
        """
        Kërko qeliza sipas rolit dhe/ose gjendjes.
        """
        if role:
            cell_ids = self._role_index.get(role, set())
            cells = [self.cells[cid] for cid in cell_ids if cid in self.cells]
        else:
            cells = list(self.cells.values())
        
        if state:
            cells = [c for c in cells if c.state == state]
        
        return cells
    
    def query_by_capability(self, capability: str) -> List[Cell]:
        """Gjej qelizat që kanë një aftësi të caktuar"""
        return [c for c in self.cells.values() if capability in c.capabilities]
    
    def query_healthy(self, role: CellRole = None) -> List[Cell]:
        """Gjej vetëm qelizat e shëndetshme"""
        cells = self.query(role=role)
        return [c for c in cells if c.is_healthy()]
    
    def link(self, from_id: str, to_id: str) -> bool:
        """Krijo një lidhje ndërmjet dy qelizave"""
        if from_id not in self.cells or to_id not in self.cells:
            return False
        
        self.edges.add((from_id, to_id))
        self.cells[from_id].links.append(to_id)
        logger.debug(f"🔗 Link created: {from_id} → {to_id}")
        return True
    
    def unlink(self, from_id: str, to_id: str) -> bool:
        """Hiq një lidhje"""
        self.edges.discard((from_id, to_id))
        if from_id in self.cells and to_id in self.cells[from_id].links:
            self.cells[from_id].links.remove(to_id)
        return True
    
    def get_linked(self, cell_id: str) -> List[Cell]:
        """Merr të gjitha qelizat e lidhura me një qelizë"""
        linked_ids = [e[1] for e in self.edges if e[0] == cell_id]
        return [self.cells[lid] for lid in linked_ids if lid in self.cells]
    
    def get_dependents(self, cell_id: str) -> List[Cell]:
        """Merr qelizat që varen nga kjo qelizë"""
        dependent_ids = [e[0] for e in self.edges if e[1] == cell_id]
        return [self.cells[did] for did in dependent_ids if did in self.cells]
    
    def update_state(self, cell_id: str, state: CellState) -> bool:
        """Përditëso gjendjen e një qelize"""
        if cell_id not in self.cells:
            return False
        self.cells[cell_id].state = state
        self.cells[cell_id].heartbeat()
        return True
    
    def heartbeat(self, cell_id: str) -> bool:
        """Regjistro heartbeat për një qelizë"""
        if cell_id not in self.cells:
            return False
        self.cells[cell_id].heartbeat()
        return True
    
    def get_graph(self) -> Dict[str, Any]:
        """
        Merr grafin e plotë të organizmës.
        G = (Cells, Edges)
        """
        return {
            "cells": [c.to_dict() for c in self.cells.values()],
            "edges": [{"from": e[0], "to": e[1]} for e in self.edges],
            "stats": self.get_stats()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistikat e regjistrit"""
        state_counts = {}
        for cell in self.cells.values():
            state = cell.state.value
            state_counts[state] = state_counts.get(state, 0) + 1
        
        role_counts = {role.value: len(ids) for role, ids in self._role_index.items() if ids}
        
        return {
            "total_cells": len(self.cells),
            "total_edges": len(self.edges),
            "by_state": state_counts,
            "by_role": role_counts,
            "healthy": len([c for c in self.cells.values() if c.is_healthy()])
        }
    
    def all(self) -> List[Cell]:
        """Merr të gjitha qelizat"""
        return list(self.cells.values())


# Singleton
_registry: Optional[CellRegistry] = None

def get_cell_registry() -> CellRegistry:
    global _registry
    if _registry is None:
        _registry = CellRegistry()
    return _registry
