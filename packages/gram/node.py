# -*- coding: utf-8 -*-
"""
GRAM NODE - Growing Resonance Adaptive Mesh Node
"Një fije bari në fushën GRAM"
================================================================================
Author: Ledjan Ahmati
System: Clisonix AI - Universal Cognitive Mesh
================================================================================

GRAM Node = Një fije bari
- Lidhet me të tjera në mënyrë natyrale
- Rritet dhe përhapet
- Ka rezonancë dhe valë
- Krijon lidhje në 12 dimensione
================================================================================
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

# ============================================================
# ENUMS
# ============================================================

class NodeType(Enum):
    """Llojet e nyjeve në GRAM"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VECTOR = "vector"
    CODE = "code"
    EMOTION = "emotion"
    MEMORY = "memory"
    RESONANCE = "resonance"
    CONCEPT = "concept"
    PATTERN = "pattern"
    INSIGHT = "insight"
    WAVE = "wave"

class ConnectionStrength(Enum):
    """Forca e lidhjes"""
    WEAK = "weak"       # 0.0 - 0.3
    MODERATE = "moderate"  # 0.3 - 0.6
    STRONG = "strong"   # 0.6 - 0.8
    RESONANT = "resonant"  # 0.8 - 0.95
    SYMPHONIC = "symphonic"  # 0.95 - 1.0

class NodeState(Enum):
    """Gjendja e nyjes"""
    SEED = "seed"           # Farë - sapo krijuar
    GROWING = "growing"     # Duke u rritur
    MATURE = "mature"       # E pjekur
    RESONANT = "resonant"   # Në rezonancë
    DECAYING = "decaying"   # Duke u kalbur
    ARCHIVED = "archived"   # E arkivuar

# ============================================================
# GRAM NODE - Main Class
# ============================================================

@dataclass
class GRAMNode:
    """
    Një fije bari në fushën GRAM.

    Lidhet me të tjera në mënyrë natyrale.
    Rritet dhe përhapet.
    """

    # Core
    id: str = field(default_factory=lambda: f"gram_{int(time.time()*1000)}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:6]}")
    content: Any = ""
    type: NodeType = NodeType.TEXT

    # Resonance
    resonance: float = 0.5
    resonance_type: str = "semantic"
    resonance_count: int = 0

    # Wave
    wave_signature: str = ""
    frequency: float = 1.0
    amplitude: float = 0.5
    phase: str = "alpha"

    # Language
    language: str = "any"
    language_confidence: float = 0.5

    # Tags & Metadata
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Growth
    growth_count: int = 0
    growth_pattern: str = "organic"
    state: NodeState = NodeState.SEED

    # Time
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    last_resonance: float = 0.0

    # ============================================================
    # CONNECTIONS - 12 DIMENSIONS
    # ============================================================

    # HVOW Dimensions (6)
    left: Set[str] = field(default_factory=set)
    right: Set[str] = field(default_factory=set)
    up: Set[str] = field(default_factory=set)
    down: Set[str] = field(default_factory=set)
    past: Set[str] = field(default_factory=set)
    future: Set[str] = field(default_factory=set)

    # GRAM Additional Dimensions (6)
    near: Set[str] = field(default_factory=set)
    far: Set[str] = field(default_factory=set)
    resonance_links: Set[str] = field(default_factory=set)
    semantic_links: Set[str] = field(default_factory=set)
    language_links: Set[str] = field(default_factory=set)
    wave_links: Set[str] = field(default_factory=set)

    # Hierarkia - si rrënjët e barit
    parents: Set[str] = field(default_factory=set)
    children: Set[str] = field(default_factory=set)

    # Memoria
    memory_links: Set[str] = field(default_factory=set)

    # ============================================================
    # METHODS
    # ============================================================

    def get_all_connections(self) -> Set[str]:
        """Merr të gjitha lidhjet"""
        return (self.left | self.right | self.up | self.down |
                self.past | self.future | self.near | self.far |
                self.resonance_links | self.semantic_links |
                self.language_links | self.wave_links |
                self.parents | self.children | self.memory_links)

    def get_connection_count(self) -> int:
        """Numri total i lidhjeve"""
        return len(self.get_all_connections())

    def get_connection_count_by_type(self) -> Dict[str, int]:
        """Numri i lidhjeve sipas tipit"""
        return {
            "left": len(self.left),
            "right": len(self.right),
            "up": len(self.up),
            "down": len(self.down),
            "past": len(self.past),
            "future": len(self.future),
            "near": len(self.near),
            "far": len(self.far),
            "resonance": len(self.resonance_links),
            "semantic": len(self.semantic_links),
            "language": len(self.language_links),
            "wave": len(self.wave_links),
            "parents": len(self.parents),
            "children": len(self.children),
            "memory": len(self.memory_links)
        }

    def add_connection(self, node_id: str, direction: str) -> None:
        """Shton një lidhje në një drejtim"""
        direction_map = {
            "left": self.left,
            "right": self.right,
            "up": self.up,
            "down": self.down,
            "past": self.past,
            "future": self.future,
            "near": self.near,
            "far": self.far,
            "resonance": self.resonance_links,
            "semantic": self.semantic_links,
            "language": self.language_links,
            "wave": self.wave_links,
            "parent": self.parents,
            "child": self.children,
            "memory": self.memory_links
        }

        if direction in direction_map:
            direction_map[direction].add(node_id)
            self.updated_at = time.time()

    def remove_connection(self, node_id: str, direction: str) -> None:
        """Heq një lidhje në një drejtim"""
        direction_map = {
            "left": self.left,
            "right": self.right,
            "up": self.up,
            "down": self.down,
            "past": self.past,
            "future": self.future,
            "near": self.near,
            "far": self.far,
            "resonance": self.resonance_links,
            "semantic": self.semantic_links,
            "language": self.language_links,
            "wave": self.wave_links,
            "parent": self.parents,
            "child": self.children,
            "memory": self.memory_links
        }

        if direction in direction_map:
            direction_map[direction].discard(node_id)
            self.updated_at = time.time()

    def remove_connection_to(self, node_id: str) -> None:
        """Heq të gjitha lidhjet me një node"""
        for direction in ["left", "right", "up", "down", "past", "future",
                         "near", "far", "resonance", "semantic", "language", "wave",
                         "parent", "child", "memory"]:
            self.remove_connection(node_id, direction)

    def get_neighbors(self) -> Set[str]:
        """Merr të gjithë fqinjët"""
        return self.get_all_connections()

    def get_degree(self) -> int:
        """Shkalla e nyjes"""
        return len(self.get_neighbors())

    def is_connected_to(self, node_id: str) -> bool:
        """Kontrollon nëse është i lidhur me një node"""
        return node_id in self.get_all_connections()

    def get_connection_strength(self, node_id: str) -> float:
        """Merr forcën e lidhjes me një node"""
        # Based on resonance and connection count
        if not self.is_connected_to(node_id):
            return 0.0

        # Calculate strength based on multiple factors
        strength = 0.5

        # Check if in resonance links
        if node_id in self.resonance_links:
            strength += 0.2

        # Check if in semantic links
        if node_id in self.semantic_links:
            strength += 0.15

        # Check if in language links
        if node_id in self.language_links:
            strength += 0.1

        # Check if in wave links
        if node_id in self.wave_links:
            strength += 0.1

        # Check if parent-child
        if node_id in self.parents or node_id in self.children:
            strength += 0.2

        return min(1.0, strength)

    def get_connection_type(self, node_id: str) -> List[str]:
        """Merr tipet e lidhjeve me një node"""
        types = []

        if node_id in self.left:
            types.append("left")
        if node_id in self.right:
            types.append("right")
        if node_id in self.up:
            types.append("up")
        if node_id in self.down:
            types.append("down")
        if node_id in self.past:
            types.append("past")
        if node_id in self.future:
            types.append("future")
        if node_id in self.near:
            types.append("near")
        if node_id in self.far:
            types.append("far")
        if node_id in self.resonance_links:
            types.append("resonance")
        if node_id in self.semantic_links:
            types.append("semantic")
        if node_id in self.language_links:
            types.append("language")
        if node_id in self.wave_links:
            types.append("wave")
        if node_id in self.parents:
            types.append("parent")
        if node_id in self.children:
            types.append("child")
        if node_id in self.memory_links:
            types.append("memory")

        return types

    def grow(self, amount: float = 0.1) -> None:
        """Rrit nyjen"""
        self.growth_count += 1
        self.resonance = min(1.0, self.resonance + amount * 0.1)
        self.amplitude = min(1.0, self.amplitude + amount * 0.05)
        self.updated_at = time.time()

        # Update state based on growth
        if self.growth_count > 100:
            self.state = NodeState.MATURE
        elif self.growth_count > 50:
            self.state = NodeState.GROWING
        elif self.growth_count > 10:
            self.state = NodeState.GROWING

        # Check if resonant
        if self.resonance > 0.8:
            self.state = NodeState.RESONANT

    def decay(self, amount: float = 0.05) -> None:
        """Kalbon nyjen"""
        self.resonance = max(0.0, self.resonance - amount)
        self.amplitude = max(0.0, self.amplitude - amount * 0.5)
        self.updated_at = time.time()

        if self.resonance < 0.2:
            self.state = NodeState.DECAYING
        elif self.resonance < 0.1:
            self.state = NodeState.ARCHIVED

    def resonate(self, strength: float) -> None:
        """Rezonon me një tjetër node"""
        self.resonance = min(1.0, (self.resonance + strength) / 2)
        self.resonance_count += 1
        self.last_resonance = time.time()
        self.updated_at = time.time()

        if self.resonance > 0.8:
            self.state = NodeState.RESONANT

    def to_dict(self) -> Dict[str, Any]:
        """Konverton në dictionary"""
        return {
            "id": self.id,
            "content": self.content,
            "type": self.type.value,
            "resonance": self.resonance,
            "resonance_type": self.resonance_type,
            "resonance_count": self.resonance_count,
            "wave_signature": self.wave_signature,
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "phase": self.phase,
            "language": self.language,
            "language_confidence": self.language_confidence,
            "tags": self.tags,
            "metadata": self.metadata,
            "growth_count": self.growth_count,
            "growth_pattern": self.growth_pattern,
            "state": self.state.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_resonance": self.last_resonance,
            "connections": {
                "left": list(self.left),
                "right": list(self.right),
                "up": list(self.up),
                "down": list(self.down),
                "past": list(self.past),
                "future": list(self.future),
                "near": list(self.near),
                "far": list(self.far),
                "resonance": list(self.resonance_links),
                "semantic": list(self.semantic_links),
                "language": list(self.language_links),
                "wave": list(self.wave_links),
                "parents": list(self.parents),
                "children": list(self.children),
                "memory": list(self.memory_links)
            },
            "connection_count": self.get_connection_count(),
            "degree": self.get_degree()
        }

    def to_json(self) -> str:
        """Konverton në JSON"""
        import json
        return json.dumps(self.to_dict(), indent=2)

    def get_connection_heatmap(self) -> Dict[str, int]:
        """Merr heatmap të lidhjeve"""
        return self.get_connection_count_by_type()

    def __repr__(self) -> str:
        return f"GRAMNode(id={self.id}, content={str(self.content)[:30]}, resonance={self.resonance:.2f}, connections={self.get_connection_count()})"


# ============================================================
# GRAM CLUSTER - Group of Nodes
# ============================================================

@dataclass
class GRAMCluster:
    """
    Një grup nodes që rriten së bashku.
    Si një tufë bari.
    """
    id: str = field(default_factory=lambda: f"cluster_{int(time.time()*1000)}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:6]}")
    nodes: Set[str] = field(default_factory=set)
    resonance: float = 0.5
    wave_signature: str = ""
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node_id: str) -> None:
        self.nodes.add(node_id)

    def remove_node(self, node_id: str) -> None:
        self.nodes.discard(node_id)

    def size(self) -> int:
        return len(self.nodes)

    def get_average_resonance(self, nodes: Dict[str, GRAMNode]) -> float:
        """Llogarit rezonancën mesatare"""
        if not self.nodes:
            return 0.0

        total = 0.0
        count = 0
        for node_id in self.nodes:
            if node_id in nodes:
                total += nodes[node_id].resonance
                count += 1

        return total / count if count > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nodes": list(self.nodes),
            "resonance": self.resonance,
            "wave_signature": self.wave_signature,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "size": self.size()
        }


# ============================================================
# GRAM FIELD - Group of Clusters
# ============================================================

@dataclass
class GRAMField:
    """
    Një fushë me clusters që rriten së bashku.
    Si një fushë me bar.
    """
    id: str = field(default_factory=lambda: f"field_{int(time.time()*1000)}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:6]}")
    clusters: Set[str] = field(default_factory=set)
    resonance: float = 0.5
    wave_signature: str = ""
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_cluster(self, cluster_id: str) -> None:
        self.clusters.add(cluster_id)

    def remove_cluster(self, cluster_id: str) -> None:
        self.clusters.discard(cluster_id)

    def size(self) -> int:
        return len(self.clusters)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "clusters": list(self.clusters),
            "resonance": self.resonance,
            "wave_signature": self.wave_signature,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "size": self.size()
        }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_node(
    content: Any,
    type: NodeType = NodeType.TEXT,
    language: str = "any",
    tags: Optional[List[str]] = None,
    resonance: float = 0.5
) -> GRAMNode:
    """Krijon një node të ri"""
    return GRAMNode(
        content=content,
        type=type,
        language=language,
        tags=tags or [],
        resonance=resonance
    )


def create_cluster(node_ids: Optional[List[str]] = None) -> GRAMCluster:
    """Krijon një cluster"""
    cluster = GRAMCluster()
    if node_ids:
        for node_id in node_ids:
            cluster.add_node(node_id)
    return cluster


def create_field(cluster_ids: Optional[List[str]] = None) -> GRAMField:
    """Krijon një field"""
    field = GRAMField()
    if cluster_ids:
        for cluster_id in cluster_ids:
            field.add_cluster(cluster_id)
    return field


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "GRAMNode",
    "GRAMCluster",
    "GRAMField",
    "NodeType",
    "ConnectionStrength",
    "NodeState",
    "create_node",
    "create_cluster",
    "create_field"
]
