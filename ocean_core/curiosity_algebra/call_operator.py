# -*- coding: utf-8 -*-
"""
📞 CALL OPERATOR - Thirrja e Qelizave
======================================
Mekanizmi që i lejon Curiosity Ocean të thërrasë çdo qelizë të brendshme/jashtme.

Llojet e thirrjeve:
- Broadcast: "Të gjitha qelizat, raportoni!"
- Targeted: "Qelizat me rol X, dërgoni detaje"
- Cascade: Thirrje që përhapet nëpër graf
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum

from .cell_registry import CellRegistry, Cell, CellRole, CellState

logger = logging.getLogger(__name__)


class CallScope(Enum):
    """Shtrirja e thirrjes"""
    ALL = "all"                 # Të gjitha qelizat
    ROLE = "role"               # Sipas rolit
    CLUSTER = "cluster"         # Një cluster specifik
    GRAPH_SUBSET = "graph_subset"  # Një nën-graf
    SINGLE = "single"           # Një qelizë e vetme
    HEALTHY = "healthy"         # Vetëm qelizat e shëndetshme
    CAPABILITY = "capability"   # Sipas aftësisë


@dataclass
class CallRequest:
    """Kërkesa për thirrje"""
    query: str
    scope: CallScope = CallScope.ALL
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 5.0
    cascade: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "scope": self.scope.value,
            "parameters": self.parameters,
            "timeout": self.timeout,
            "cascade": self.cascade
        }


@dataclass
class CallResponse:
    """Përgjigja nga një qelizë"""
    cell_id: str
    response: Any
    success: bool = True
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "response": self.response,
            "success": self.success,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
            "latency_ms": self.latency_ms
        }


class CallOperator:
    """
    📞 Operatori i Thirrjeve
    
    Ky mekanizëm i jep Curiosity Ocean fuqinë të thërrasë 
    çdo qelizë të brendshme dhe të jashtme të projektit.
    """
    
    def __init__(self, registry: CellRegistry):
        self.registry = registry
        self.call_history: List[Dict] = []
        self.max_history = 1000
        
        logger.info("📞 CallOperator initialized - Thirrja e qelizave është gati")
    
    def call(self, query: str, 
             scope: Union[CallScope, str] = CallScope.ALL,
             role: CellRole = None,
             capability: str = None,
             cell_id: str = None,
             parameters: Dict[str, Any] = None,
             cascade: bool = False) -> List[CallResponse]:
        """
        Thirr qelizat sipas kritereve.
        
        Shembuj:
        - call("report-status", scope=CallScope.ALL)
        - call("get-metrics", role=CellRole.SENSOR)
        - call("analyze", capability="ml")
        - call("ping", cell_id="sensor-01")
        """
        if isinstance(scope, str):
            scope = CallScope(scope)
        
        # Gjej qelizat target
        cells = self._resolve_targets(scope, role, capability, cell_id)
        
        if not cells:
            logger.warning(f"📞 No cells matched for query: {query}")
            return []
        
        # Thirr çdo qelizë
        responses = []
        for cell in cells:
            response = self._call_cell(cell, query, parameters or {})
            responses.append(response)
            
            # Cascade: thirr edhe qelizat e lidhura
            if cascade and response.success:
                linked_cells = self.registry.get_linked(cell.id)
                for linked in linked_cells:
                    cascade_response = self._call_cell(linked, query, parameters or {})
                    responses.append(cascade_response)
        
        # Ruaj në histori
        self._record_call(query, scope, len(cells), len([r for r in responses if r.success]))
        
        logger.info(f"📞 Call completed: {query} → {len(responses)} responses")
        return responses
    
    async def call_async(self, query: str,
                         scope: Union[CallScope, str] = CallScope.ALL,
                         role: CellRole = None,
                         capability: str = None,
                         timeout: float = 5.0) -> List[CallResponse]:
        """Thirrje asinkrone paralele"""
        if isinstance(scope, str):
            scope = CallScope(scope)
        
        cells = self._resolve_targets(scope, role, capability, None)
        
        if not cells:
            return []
        
        # Thirr të gjitha në paralel
        tasks = [
            self._call_cell_async(cell, query, {}, timeout)
            for cell in cells
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Konverto exceptions në CallResponse
        result = []
        for i, resp in enumerate(responses):
            if isinstance(resp, Exception):
                result.append(CallResponse(
                    cell_id=cells[i].id,
                    response=None,
                    success=False,
                    error=str(resp)
                ))
            else:
                result.append(resp)
        
        self._record_call(query, scope, len(cells), len([r for r in result if r.success]))
        return result
    
    def broadcast(self, query: str, parameters: Dict[str, Any] = None) -> List[CallResponse]:
        """Broadcast: Thirr TË GJITHA qelizat"""
        return self.call(query, scope=CallScope.ALL, parameters=parameters)
    
    def targeted(self, query: str, role: CellRole, parameters: Dict[str, Any] = None) -> List[CallResponse]:
        """Targeted: Thirr qelizat me një rol specifik"""
        return self.call(query, scope=CallScope.ROLE, role=role, parameters=parameters)
    
    def cascade_call(self, query: str, cell_id: str, parameters: Dict[str, Any] = None) -> List[CallResponse]:
        """Cascade: Thirr një qelizë dhe të gjitha të lidhurat"""
        return self.call(query, scope=CallScope.SINGLE, cell_id=cell_id, 
                        parameters=parameters, cascade=True)
    
    def _resolve_targets(self, scope: CallScope, role: CellRole, 
                         capability: str, cell_id: str) -> List[Cell]:
        """Gjej qelizat target bazuar në kritere"""
        if scope == CallScope.SINGLE and cell_id:
            cell = self.registry.get(cell_id)
            return [cell] if cell else []
        
        if scope == CallScope.ROLE and role:
            return self.registry.query(role=role)
        
        if scope == CallScope.CAPABILITY and capability:
            return self.registry.query_by_capability(capability)
        
        if scope == CallScope.HEALTHY:
            return self.registry.query_healthy(role=role)
        
        # ALL - të gjitha qelizat aktive
        return [c for c in self.registry.all() if c.state != CellState.OFFLINE]
    
    def _call_cell(self, cell: Cell, query: str, parameters: Dict[str, Any]) -> CallResponse:
        """Thirr një qelizë të vetme"""
        start_time = datetime.now(timezone.utc)
        
        try:
            if cell.on_call:
                response = cell.on_call(query, parameters)
            else:
                # Default response nëse qeliza nuk ka handler
                response = {
                    "query": query,
                    "cell": cell.id,
                    "state": cell.state.value,
                    "message": "Cell received query but has no handler"
                }
            
            latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return CallResponse(
                cell_id=cell.id,
                response=response,
                success=True,
                latency_ms=latency
            )
        except Exception as e:
            latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            logger.error(f"📞 Call failed for {cell.id}: {e}")
            return CallResponse(
                cell_id=cell.id,
                response=None,
                success=False,
                error=str(e),
                latency_ms=latency
            )
    
    async def _call_cell_async(self, cell: Cell, query: str, 
                                parameters: Dict[str, Any], timeout: float) -> CallResponse:
        """Thirr një qelizë asinkronisht"""
        start_time = datetime.now(timezone.utc)
        
        try:
            if cell.on_call:
                if asyncio.iscoroutinefunction(cell.on_call):
                    response = await asyncio.wait_for(
                        cell.on_call(query, parameters), 
                        timeout=timeout
                    )
                else:
                    response = await asyncio.get_event_loop().run_in_executor(
                        None, lambda: cell.on_call(query, parameters)
                    )
            else:
                response = {"cell": cell.id, "query": query, "status": "no_handler"}
            
            latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            return CallResponse(
                cell_id=cell.id,
                response=response,
                success=True,
                latency_ms=latency
            )
        except asyncio.TimeoutError:
            return CallResponse(
                cell_id=cell.id,
                response=None,
                success=False,
                error="Timeout"
            )
        except Exception as e:
            return CallResponse(
                cell_id=cell.id,
                response=None,
                success=False,
                error=str(e)
            )
    
    def _record_call(self, query: str, scope: CallScope, targets: int, successes: int) -> None:
        """Regjistro thirrjen në histori"""
        self.call_history.append({
            "query": query,
            "scope": scope.value,
            "targets": targets,
            "successes": successes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        if len(self.call_history) > self.max_history:
            self.call_history = self.call_history[-self.max_history:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistikat e thirrjeve"""
        if not self.call_history:
            return {"total_calls": 0}
        
        total = len(self.call_history)
        total_targets = sum(c["targets"] for c in self.call_history)
        total_successes = sum(c["successes"] for c in self.call_history)
        
        return {
            "total_calls": total,
            "total_targets": total_targets,
            "total_successes": total_successes,
            "success_rate": total_successes / total_targets if total_targets > 0 else 0,
            "recent_calls": self.call_history[-10:]
        }


# Factory function
def create_call_operator(registry: CellRegistry = None) -> CallOperator:
    if registry is None:
        from .cell_registry import get_cell_registry
        registry = get_cell_registry()
    return CallOperator(registry)
