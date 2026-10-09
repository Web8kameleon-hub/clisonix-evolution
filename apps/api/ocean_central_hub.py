"""
OCEAN CENTRAL HUB - Curiosity Ocean Core Integration Layer
Connects ALL agents (ALBA, ALBI, Blerina, AGIEM, ASI) with infinite streaming
Author: Ledjan Ahmati
License: Closed Source
Version: 1.0.0
"""

import asyncio
import base64
import json
import logging
import os
import zlib
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Callable, Dict, List, Optional
from uuid import uuid4

import cbor2

logger = logging.getLogger("ocean_central_hub")

# ============================================================================
# ENUMS & TYPES
# ============================================================================

class DataFormat(str, Enum):
    """Supported data formats for streaming"""
    JSON = "json"
    CBOR2 = "cbor2"
    LORA = "lora"
    IOT = "iot"
    MSGPACK = "msgpack"

class AgentType(str, Enum):
    """Agent types in the ecosystem"""
    ALBA = "alba"
    ALBI = "albi"
    BLERINA = "blerina"
    AGIEM = "agiem"
    ASI = "asi"
    CYCLE = "cycle"
    PROPOSAL = "proposal"
    ALIGNMENT = "alignment"
    LABS = "labs"

class DataStreamPriority(str, Enum):
    """Priority levels for data streaming"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

# ============================================================================
# DATA MODELS
# ============================================================================

class OceanCell:
    """Single cell in Ocean grid - represents a module/endpoint"""
    def __init__(self, 
                 cell_id: str,
                 module_name: str,
                 agent_type: AgentType,
                 endpoint: str,
                 description: str = ""):
        self.cell_id = cell_id
        self.module_name = module_name
        self.agent_type = agent_type
        self.endpoint = endpoint
        self.description = description
        self.data_flow: List[str] = []
        self.metrics = {
            "total_calls": 0,
            "successful": 0,
            "failed": 0,
            "avg_latency_ms": 0,
            "last_update": None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "module_name": self.module_name,
            "agent_type": self.agent_type.value,
            "endpoint": self.endpoint,
            "description": self.description,
            "data_flow": self.data_flow,
            "metrics": self.metrics
        }

class DataStream:
    """Represents infinite data stream from a source"""
    def __init__(self,
                 stream_id: str,
                 source_cell: OceanCell,
                 format: DataFormat = DataFormat.JSON,
                 priority: DataStreamPriority = DataStreamPriority.NORMAL):
        self.stream_id = stream_id
        self.source_cell = source_cell
        self.format = format
        self.priority = priority
        self.created_at = datetime.utcnow()
        self.last_data: Optional[Dict[str, Any]] = None
        self.data_buffer: List[Dict] = []
        self.subscribers: List[Callable] = []
        self.is_active = True
    
    async def emit_data(self, data: Dict[str, Any]) -> None:
        """Emit data to all subscribers"""
        if not self.is_active:
            return
        
        # Format conversion
        if self.format == DataFormat.CBOR2:
            data_bytes = cbor2.dumps(data)
            data = {"_cbor2_encoded": data_bytes.hex()}
        elif self.format == DataFormat.LORA:
            # LoRa compression
            data = {"_lora_compressed": self._compress_lora(data)}
        
        self.last_data = data
        self.data_buffer.append(data)
        
        # Keep buffer size manageable
        if len(self.data_buffer) > 1000:
            self.data_buffer = self.data_buffer[-500:]
        
        # Notify subscribers
        for subscriber in self.subscribers:
            try:
                await subscriber(data)
            except Exception as e:
                logger.error(f"Subscriber error: {e}")
    
    def _compress_lora(self, data: Dict) -> str:
        """Compress payload for LoRa transport using zlib + base64."""
        json_bytes = json.dumps(data, separators=(",", ":")).encode("utf-8")
        compressed = zlib.compress(json_bytes, level=9)
        encoded = base64.b64encode(compressed).decode("ascii")
        return f"LORA_ZLIB_B64:{encoded}"
    
    def subscribe(self, callback: Callable) -> None:
        """Subscribe to stream updates"""
        self.subscribers.append(callback)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "source_cell": self.source_cell.cell_id,
            "format": self.format.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "subscribers": len(self.subscribers),
            "buffer_size": len(self.data_buffer)
        }

class UserSession:
    """User session managing data streams"""
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.active_streams: Dict[str, DataStream] = {}
        self.session_data: Dict[str, Any] = {}
    
    async def open_stream(self, 
                         cell: OceanCell,
                         format: DataFormat = DataFormat.JSON,
                         priority: DataStreamPriority = DataStreamPriority.NORMAL) -> DataStream:
        """Open new data stream"""
        stream_id = f"{self.session_id}:{cell.cell_id}:{str(uuid4())[:8]}"
        stream = DataStream(stream_id, cell, format, priority)
        self.active_streams[stream_id] = stream
        return stream
    
    def close_stream(self, stream_id: str) -> None:
        """Close data stream"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id].is_active = False
            del self.active_streams[stream_id]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "active_streams": len(self.active_streams),
            "streams": [s.to_dict() for s in self.active_streams.values()]
        }

# ============================================================================
# LABS INTEGRATION
# ============================================================================

class LabsCell:
    """Integration layer for Labs execution within Ocean Central Hub"""
    
    def __init__(self):
        """Initialize LabsCell with lab executor"""
        self.cell_id = "ocean-labs-cell"
        self.agent_type = AgentType.LABS
        self.active_executions = {}
        self._init_labs()
    
    def _init_labs(self):
        """Initialize lab executor references"""
        try:
            from hybrid_saas_platform.labs.lab_executor import (
                DataValidationLab,
                IntegrationLab,
                LabStatus,
                TransformationLab,
            )
            self.DataValidationLab = DataValidationLab
            self.IntegrationLab = IntegrationLab
            self.TransformationLab = TransformationLab
            self.LabStatus = LabStatus
            logger.info("✅ Labs system initialized within Ocean")
        except ImportError as e:
            logger.warning(f"⚠️ Labs system not available: {e}")
            self.DataValidationLab = None
            self.IntegrationLab = None
            self.TransformationLab = None
    
    async def execute_lab(self, lab_type: str, row: Dict[str, Any]) -> Dict[str, Any]:
        """Execute specified lab type and return results through Ocean format"""
        execution_id = str(uuid4())
        
        try:
            if lab_type == "data_validation":
                if not self.DataValidationLab:
                    raise RuntimeError("data_validation lab is not available")
                lab = self.DataValidationLab()
            elif lab_type == "integration":
                if not self.IntegrationLab:
                    raise RuntimeError("integration lab is not available")
                lab = self.IntegrationLab()
            elif lab_type == "transformation":
                if not self.TransformationLab:
                    raise RuntimeError("transformation lab is not available")
                lab = self.TransformationLab()
            else:
                raise ValueError(f"Unknown lab type: {lab_type}")
            
            # Execute lab synchronously and wrap in async context
            result, artifacts = await asyncio.to_thread(lab.execute, row)
            
            # Track execution
            self.active_executions[execution_id] = {
                "lab_type": lab_type,
                "status": result.status.value,
                "completed_at": datetime.utcnow().isoformat()
            }
            
            # Format result for Ocean streaming
            return {
                "execution_id": execution_id,
                "lab_type": lab_type,
                "result": result.to_dict(),
                "artifacts": [a.to_dict() for a in artifacts],
                "ocean_format": {
                    "stream_type": "lab_execution",
                    "priority": "normal",
                    "agent": self.agent_type.value
                }
            }
        
        except Exception as e:
            logger.error(f"Lab execution failed: {e}")
            return {
                "execution_id": execution_id,
                "lab_type": lab_type,
                "error": str(e),
                "status": "FAILED",
                "ocean_format": {
                    "stream_type": "lab_execution_error",
                    "priority": "high",
                    "agent": self.agent_type.value
                }
            }
    
    def get_lab_types(self) -> List[str]:
        """Get available lab types"""
        labs: List[str] = []
        if self.DataValidationLab:
            labs.append("data_validation")
        if self.IntegrationLab:
            labs.append("integration")
        if self.TransformationLab:
            labs.append("transformation")
        return labs
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a lab execution"""
        return self.active_executions.get(execution_id)

# ============================================================================
# CENTRAL HUB
# ============================================================================

class OceanCentralHub:
    """Central hub coordinating all agents and data streams"""
    
    def __init__(self, max_concurrent_users: Optional[int] = None):
        env_limit = os.getenv("OCEAN_HUB_MAX_USERS", "23")
        configured_limit = max_concurrent_users if max_concurrent_users is not None else int(env_limit)
        self.max_concurrent_users = configured_limit
        self.cells: Dict[str, OceanCell] = {}
        self.streams: Dict[str, DataStream] = {}
        self.sessions: Dict[str, UserSession] = {}
        self.agent_registry: Dict[AgentType, List[str]] = defaultdict(list)
        self.labs_cell = LabsCell()  # Initialize Labs integration
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize the central hub"""
        logger.info("🌊 Initializing Ocean Central Hub...")
        await self._register_all_cells()
        self.initialized = True
        logger.info("✅ Ocean Central Hub initialized")
    
    async def _register_all_cells(self) -> None:
        """Register all application cells"""
        # ALBA cells
        self._register_cell("alba_core", "ALBA Core", AgentType.ALBA, "/api/alba/core")
        self._register_cell("alba_metrics", "ALBA Metrics", AgentType.ALBA, "/api/alba/metrics")
        self._register_cell("alba_health", "ALBA Health", AgentType.ALBA, "/api/alba/health")
        
        # ALBI cells
        self._register_cell("albi_core", "ALBI Core", AgentType.ALBI, "/api/albi/core")
        self._register_cell("albi_metrics", "ALBI Metrics", AgentType.ALBI, "/api/albi/metrics")
        
        # Blerina cells
        self._register_cell("blerina_fmt", "Blerina Formatter", AgentType.BLERINA, "/api/blerina/format")
        self._register_cell("blerina_transform", "Blerina Transform", AgentType.BLERINA, "/api/blerina/transform")
        
        # AGIEM cells
        self._register_cell("agiem_core", "AGIEM Core", AgentType.AGIEM, "/api/agiem/core")
        self._register_cell("agiem_proposal", "AGIEM Proposals", AgentType.AGIEM, "/api/agiem/proposals")
        
        # ASI cells
        self._register_cell("asi_engine", "ASI Engine", AgentType.ASI, "/api/asi/engine")
        self._register_cell("asi_realtime", "ASI Real-time", AgentType.ASI, "/api/asi/realtime")
        
        # Cycle cells
        self._register_cell("cycle_engine", "Cycle Engine", AgentType.CYCLE, "/api/cycle/engine")
        self._register_cell("cycle_proposals", "Cycle Proposals", AgentType.CYCLE, "/api/cycle/proposals")
        
        # Alignment cells
        self._register_cell("alignments", "Cycle Alignments", AgentType.ALIGNMENT, "/api/alignments/check")
        
        # Labs cells - Testing & validation engine
        self._register_cell("labs_executor", "Labs Executor", AgentType.LABS, "/api/labs/execute", 
                           description="Lab execution engine - raw data → validated artifacts")
        
        logger.info(f"✅ Registered {len(self.cells)} cells")
    
    def _register_cell(self,
                      cell_id: str,
                      module_name: str,
                      agent_type: AgentType,
                      endpoint: str,
                      description: str = "") -> None:
        """Register a single cell"""
        cell = OceanCell(cell_id, module_name, agent_type, endpoint, description)
        self.cells[cell_id] = cell
        self.agent_registry[agent_type].append(cell_id)
    
    async def create_session(self, user_id: str) -> UserSession:
        """Create new user session"""
        if len(self.sessions) >= self.max_concurrent_users:
            raise Exception(f"Max concurrent users ({self.max_concurrent_users}) reached")
        
        session_id = str(uuid4())
        session = UserSession(session_id, user_id)
        self.sessions[session_id] = session
        logger.info(f"📱 Created session {session_id} for user {user_id}")
        return session
    
    async def end_session(self, session_id: str) -> None:
        """End user session and close all streams"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        for stream_id in list(session.active_streams.keys()):
            session.close_stream(stream_id)
        
        del self.sessions[session_id]
        logger.info(f"🔌 Ended session {session_id}")
    
    async def open_cell_stream(self,
                              session_id: str,
                              cell_id: str,
                              format: DataFormat = DataFormat.JSON,
                              priority: DataStreamPriority = DataStreamPriority.NORMAL) -> DataStream:
        """Open data stream from specific cell"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        if cell_id not in self.cells:
            raise ValueError(f"Cell {cell_id} not found")
        
        session = self.sessions[session_id]
        cell = self.cells[cell_id]
        stream = await session.open_stream(cell, format, priority)
        self.streams[stream.stream_id] = stream
        
        logger.info(f"🌊 Opened stream {stream.stream_id}: {cell.module_name} ({format.value})")
        return stream
    
    async def emit_to_stream(self, stream_id: str, data: Dict[str, Any]) -> None:
        """Emit data to specific stream"""
        if stream_id not in self.streams:
            logger.warning(f"Stream {stream_id} not found")
            return
        
        stream = self.streams[stream_id]
        await stream.emit_data(data)
    
    async def broadcast_to_agent_type(self,
                                     agent_type: AgentType,
                                     data: Dict[str, Any]) -> None:
        """Broadcast data to all cells of specific agent type"""
        cell_ids = self.agent_registry.get(agent_type, [])
        for cell_id in cell_ids:
            cell = self.cells[cell_id]
            current_calls = cell.metrics.get("total_calls", 0)
            if not isinstance(current_calls, int):
                current_calls = 0
            cell.metrics["total_calls"] = current_calls + 1
            # Update cell's data_flow
            cell.data_flow.append(f"{datetime.utcnow().isoformat()}: {len(str(data))} bytes")
            if len(cell.data_flow) > 100:
                cell.data_flow = cell.data_flow[-50:]
    
    def get_hub_status(self) -> Dict[str, Any]:
        """Get complete hub status"""
        return {
            "initialized": self.initialized,
            "max_concurrent_users": self.max_concurrent_users,
            "active_sessions": len(self.sessions),
            "active_streams": len(self.streams),
            "total_cells": len(self.cells),
            "cells_by_agent": {agent.value: len(ids) for agent, ids in self.agent_registry.items()},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        if session_id not in self.sessions:
            return None
        return self.sessions[session_id].to_dict()
    
    def get_cell_info(self, cell_id: str) -> Optional[Dict[str, Any]]:
        """Get cell information"""
        if cell_id not in self.cells:
            return None
        return self.cells[cell_id].to_dict()
    
    async def stream_infinite_data(self,
                                   stream_id: str,
                                   data_generator: Callable,
                                   interval_ms: int = 1000) -> AsyncIterator[Dict]:
        """Stream infinite data from generator"""
        if stream_id not in self.streams:
            raise ValueError(f"Stream {stream_id} not found")
        
        stream = self.streams[stream_id]
        while stream.is_active:
            try:
                data = await data_generator()
                await self.emit_to_stream(stream_id, data)
                yield data
                await asyncio.sleep(interval_ms / 1000)
            except Exception as e:
                logger.error(f"Error in stream {stream_id}: {e}")
                await asyncio.sleep(interval_ms / 1000)



# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_ocean_hub: Optional[OceanCentralHub] = None
_labs_cell: Optional[LabsCell] = None

async def get_ocean_hub() -> OceanCentralHub:
    """Get or create global Ocean Central Hub"""
    global _ocean_hub
    if _ocean_hub is None:
        _ocean_hub = OceanCentralHub()
        await _ocean_hub.initialize()
    return _ocean_hub

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "OceanCentralHub",
    "OceanCell",
    "DataStream",
    "UserSession",
    "DataFormat",
    "AgentType",
    "DataStreamPriority",
    "get_ocean_hub"
]
