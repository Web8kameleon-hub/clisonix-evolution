#!/usr/bin/env python3
"""
ALDA - Artificial Labor Determined Array
Intelligent Labor Orchestration with Deterministic Array Processing

Core engine for managing and orchestrating labor/computational workloads
using deterministic array-based algorithms.
"""

import hashlib
import struct
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

try:
    import cbor2
    CBOR_AVAILABLE = True
except ImportError:
    CBOR_AVAILABLE = False

try:
    import msgpack
    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False


class LaborState(Enum):
    """Labor unit states"""
    IDLE = "idle"
    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"


class DeterminismLevel(Enum):
    """Level of determinism in array processing"""
    STRICT = "strict"       # Exact reproducibility
    RELAXED = "relaxed"     # Allow minor floating point variance
    STOCHASTIC = "stochastic"  # Controlled randomness with seed


@dataclass
class LaborUnit:
    """Single labor/work unit"""
    id: str
    payload: np.ndarray
    state: LaborState = LaborState.IDLE
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_binary(self) -> bytes:
        """Serialize to binary"""
        id_bytes = self.id.encode('utf-8')
        state_bytes = self.state.value.encode('utf-8')
        payload_bytes = self.payload.tobytes()
        
        header = struct.pack(
            '>IIII',
            len(id_bytes),
            len(state_bytes),
            self.priority,
            len(payload_bytes)
        )
        
        return header + id_bytes + state_bytes + payload_bytes
    
    def compute_hash(self) -> str:
        """Compute deterministic hash of labor unit"""
        content = self.id.encode() + self.payload.tobytes()
        return hashlib.sha256(content).hexdigest()[:16]


@dataclass
class LaborArray:
    """Array of labor units with collective operations"""
    units: List[LaborUnit] = field(default_factory=list)
    dimension: int = 64
    determinism: DeterminismLevel = DeterminismLevel.STRICT
    seed: Optional[int] = None
    
    def __post_init__(self):
        if self.seed is not None:
            np.random.seed(self.seed)
    
    def add_unit(self, unit: LaborUnit) -> int:
        """Add labor unit, return index"""
        self.units.append(unit)
        return len(self.units) - 1
    
    def get_state_vector(self) -> np.ndarray:
        """Get state of all units as numeric vector (no loops via list comprehension + numpy)"""
        state_map = {
            LaborState.IDLE: 0,
            LaborState.ACTIVE: 1,
            LaborState.PROCESSING: 2,
            LaborState.COMPLETED: 3,
            LaborState.FAILED: -1,
            LaborState.SUSPENDED: -2
        }
        states = [state_map[u.state] for u in self.units]
        return np.array(states, dtype=np.int32)
    
    def get_priority_vector(self) -> np.ndarray:
        """Get priority vector"""
        return np.array([u.priority for u in self.units], dtype=np.int32)
    
    def get_payload_matrix(self) -> np.ndarray:
        """Stack all payloads into matrix"""
        if not self.units:
            return np.zeros((0, self.dimension))
        return np.vstack([
            np.pad(u.payload.flatten(), (0, max(0, self.dimension - len(u.payload.flatten()))))[:self.dimension]
            for u in self.units
        ])


class DeterministicScheduler:
    """
    Deterministic Array-Based Scheduler
    Uses matrix operations for scheduling decisions - no loops in core logic.
    """
    
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.schedule_matrix = np.zeros((capacity, capacity), dtype=np.float64)
        self.affinity_matrix = np.eye(capacity, dtype=np.float64)
        
    def compute_schedule(self, labor_array: LaborArray) -> np.ndarray:
        """
        Compute optimal schedule using matrix algebra.
        Returns priority-ordered indices.
        """
        if not labor_array.units:
            return np.array([], dtype=np.int32)
        
        priorities = labor_array.get_priority_vector()
        states = labor_array.get_state_vector()
        
        # Compute schedulability score (vectorized)
        # Active or idle units with higher priority get higher scores
        schedulable_mask = np.isin(states, [0, 1])  # IDLE or ACTIVE
        scores = priorities * schedulable_mask.astype(np.float64)
        
        # Add randomness if stochastic mode
        if labor_array.determinism == DeterminismLevel.STOCHASTIC:
            noise = np.random.randn(len(scores)) * 0.1
            scores = scores + noise
        
        # Return indices sorted by score (descending)
        return np.argsort(scores)[::-1]
    
    def compute_affinity(self, payloads: np.ndarray) -> np.ndarray:
        """
        Compute affinity matrix between labor units.
        Uses cosine similarity via matrix multiplication.
        """
        if payloads.size == 0:
            return np.array([[]])
        
        # Normalize rows
        norms = np.linalg.norm(payloads, axis=1, keepdims=True)
        norms[norms == 0] = 1
        normalized = payloads / norms
        
        # Cosine similarity via matrix multiplication
        return np.dot(normalized, normalized.T)
    
    def optimize_batch(self, labor_array: LaborArray, batch_size: int = 10) -> List[int]:
        """
        Optimize batch selection using matrix operations.
        """
        schedule = self.compute_schedule(labor_array)
        return schedule[:batch_size].tolist()


class ArtificialLaborEngine:
    """
    ALDA Core Engine - Artificial Labor Determined Array
    
    Manages labor/work units using deterministic array processing.
    All operations are reproducible given same inputs and seed.
    """
    
    def __init__(self, dimension: int = 64, seed: Optional[int] = None):
        self.dimension = dimension
        self.seed = seed
        self.labor_array = LaborArray(dimension=dimension, seed=seed)
        self.scheduler = DeterministicScheduler()
        self.processing_history: List[Dict[str, Any]] = []
        
        if seed is not None:
            np.random.seed(seed)
    
    def create_labor_unit(
        self,
        payload: np.ndarray,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LaborUnit:
        """Create a new labor unit with deterministic ID"""
        # Deterministic ID based on payload hash
        payload_hash = hashlib.sha256(payload.tobytes()).hexdigest()[:12]
        unit_id = f"ALDA-{payload_hash}-{len(self.labor_array.units):04d}"
        
        unit = LaborUnit(
            id=unit_id,
            payload=payload,
            priority=priority,
            metadata=metadata or {}
        )
        
        self.labor_array.add_unit(unit)
        return unit
    
    def ingest_work(self, data: Dict[str, Any]) -> LaborUnit:
        """
        Ingest work data and create labor unit.
        Converts data to vector representation.
        """
        # Extract numeric values
        numeric_values = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                numeric_values.append(float(value))
            elif isinstance(value, list) and all(isinstance(v, (int, float)) for v in value):
                numeric_values.extend([float(v) for v in value])
        
        # Create payload array
        payload = np.array(numeric_values, dtype=np.float64)
        if len(payload) < self.dimension:
            payload = np.pad(payload, (0, self.dimension - len(payload)))
        else:
            payload = payload[:self.dimension]
        
        priority = data.get('priority', 0)
        return self.create_labor_unit(payload, priority, data)
    
    def process_batch(self, batch_size: int = 10) -> Dict[str, Any]:
        """
        Process a batch of labor units.
        Uses deterministic scheduling.
        """
        # Get optimized batch
        batch_indices = self.scheduler.optimize_batch(self.labor_array, batch_size)
        
        processed = []
        for idx in batch_indices:
            if idx < len(self.labor_array.units):
                unit = self.labor_array.units[idx]
                if unit.state in [LaborState.IDLE, LaborState.ACTIVE]:
                    # Mark as processing
                    unit.state = LaborState.PROCESSING
                    
                    # Compute result (deterministic transformation)
                    result = self._process_unit(unit)
                    
                    # Mark completed
                    unit.state = LaborState.COMPLETED
                    processed.append({
                        'id': unit.id,
                        'result_hash': result,
                        'priority': unit.priority
                    })
        
        # Record in history
        self.processing_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'batch_size': len(processed),
            'indices': batch_indices
        })
        
        return {
            'processed': processed,
            'batch_size': len(processed),
            'remaining': sum(1 for u in self.labor_array.units if u.state == LaborState.IDLE)
        }
    
    def _process_unit(self, unit: LaborUnit) -> str:
        """
        Process single labor unit with deterministic transformation.
        """
        # Apply deterministic transformation
        transformed = np.dot(unit.payload, np.eye(len(unit.payload)))
        
        # Compute result hash
        return hashlib.sha256(transformed.tobytes()).hexdigest()[:16]
    
    def get_status(self) -> Dict[str, Any]:
        """Get engine status"""
        states = self.labor_array.get_state_vector()
        
        return {
            'total_units': len(self.labor_array.units),
            'idle': int(np.sum(states == 0)),
            'active': int(np.sum(states == 1)),
            'processing': int(np.sum(states == 2)),
            'completed': int(np.sum(states == 3)),
            'failed': int(np.sum(states == -1)),
            'suspended': int(np.sum(states == -2)),
            'dimension': self.dimension,
            'determinism': self.labor_array.determinism.value,
            'history_size': len(self.processing_history)
        }
    
    def compute_labor_metrics(self) -> Dict[str, Any]:
        """
        Compute comprehensive labor metrics using matrix operations.
        """
        if not self.labor_array.units:
            return {'error': 'No labor units'}
        
        payloads = self.labor_array.get_payload_matrix()
        priorities = self.labor_array.get_priority_vector()
        
        # Compute statistics (all vectorized)
        metrics = {
            'payload_mean': np.mean(payloads, axis=0).tolist(),
            'payload_std': np.std(payloads, axis=0).tolist(),
            'priority_distribution': {
                'mean': float(np.mean(priorities)),
                'std': float(np.std(priorities)),
                'min': int(np.min(priorities)),
                'max': int(np.max(priorities))
            },
            'affinity_matrix': self.scheduler.compute_affinity(payloads).tolist(),
            'total_work_volume': float(np.sum(np.abs(payloads))),
            'work_distribution': np.linalg.norm(payloads, axis=1).tolist()
        }
        
        return metrics
    
    def to_binary(self) -> bytes:
        """Export engine state to binary"""
        state = {
            'dimension': self.dimension,
            'seed': self.seed,
            'units_count': len(self.labor_array.units),
            'status': self.get_status(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if CBOR_AVAILABLE:
            return cbor2.dumps(state)
        elif MSGPACK_AVAILABLE:
            return msgpack.packb(state)
        else:
            import json
            return json.dumps(state).encode('utf-8')


# Singleton instance
_alda_engine: Optional[ArtificialLaborEngine] = None

def get_alda_engine(dimension: int = 64, seed: Optional[int] = None) -> ArtificialLaborEngine:
    """Get or create ALDA engine instance"""
    global _alda_engine
    if _alda_engine is None:
        _alda_engine = ArtificialLaborEngine(dimension, seed)
    return _alda_engine
