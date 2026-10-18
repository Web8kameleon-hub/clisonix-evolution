# -*- coding: utf-8 -*-
"""
GRAM MESH - Growing Resonance Adaptive Mesh
"Rrjeti i barit që lidh gjithçka"
================================================================================
Author: Ledjan Ahmati
System: Clisonix AI - Universal Cognitive Mesh
================================================================================

GRAM Mesh = Rrjeti i barit
- Lidh të gjitha nyjet
- Rritet dhe përhapet
- Ka rezonancë dhe valë
- Krijon lidhje të pafundme
- Pa qendër
================================================================================
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque

# ============================================================
# ENUMS
# ============================================================

class MeshState(Enum):
    """Gjendja e rrjetit"""
    SEED = "seed"           # Farë - sapo krijuar
    GROWING = "growing"     # Duke u rritur
    MATURE = "mature"       # I pjekur
    RESONANT = "resonant"   # Në rezonancë
    SPREADING = "spreading" # Duke u përhapur
    CONNECTED = "connected" # I lidhur
    OPTIMAL = "optimal"     # Optimal
    DEGRADED = "degraded"   # I degraduar

class MeshTopology(Enum):
    """Topologjia e rrjetit"""
    RANDOM = "random"           # Rastësore
    SCALE_FREE = "scale_free"   # Pa shkallë
    SMALL_WORLD = "small_world" # Botë e vogël
    CLUSTER = "cluster"         # Tufë
    TREE = "tree"               # Pemë
    CYCLE = "cycle"             # Cikël
    HYBRID = "hybrid"           # Hibrid
    ORGANIC = "organic"         # Organik

class MeshMetric(Enum):
    """Metrikat e rrjetit"""
    DENSITY = "density"
    CONNECTIVITY = "connectivity"
    CLUSTERING = "clustering"
    PATH_LENGTH = "path_length"
    RESONANCE = "resonance"
    COHERENCE = "coherence"
    RESILIENCE = "resilience"
    EFFICIENCY = "efficiency"

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class MeshNode:
    """Nyje në rrjet"""
    id: str
    content: Any
    connections: Set[str] = field(default_factory=set)
    resonance: float = 0.5
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

@dataclass
class MeshEdge:
    """Lidhje në rrjet"""
    source: str
    target: str
    weight: float = 1.0
    strength: float = 0.5
    type: str = "semantic"
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MeshStatistics:
    """Statistika të rrjetit"""
    total_nodes: int = 0
    total_edges: int = 0
    density: float = 0.0
    avg_degree: float = 0.0
    avg_clustering: float = 0.0
    avg_path_length: float = 0.0
    avg_resonance: float = 0.0
    coherence: float = 0.0
    resilience: float = 0.0
    efficiency: float = 0.0
    connected_components: int = 0
    largest_component: int = 0

# ============================================================
# GRAM MESH - Main Class
# ============================================================

class GRAMMesh:
    """
    GRAM Mesh - Rrjeti i barit

    Lidh të gjitha nyjet.
    Rritet dhe përhapet.
    Ka rezonancë dhe valë.
    Pa qendër.
    """

    def __init__(
        self,
        topology: MeshTopology = MeshTopology.ORGANIC,
        name: str = "Unnamed Mesh"
    ):
        self.id = self._generate_id()
        self.name = name
        self.topology = topology

        # Nodes and edges
        self.nodes: Dict[str, MeshNode] = {}
        self.edges: Dict[Tuple[str, str], MeshEdge] = {}

        # State
        self.state = MeshState.SEED
        self.resonance = 0.5
        self.wave_signature = self._generate_wave_signature()

        # Growth
        self.growth_count = 0
        self.growth_rate = 0.1

        # Metrics
        self.statistics = MeshStatistics()

        # Time
        self.created_at = time.time()
        self.updated_at = time.time()
        self.last_growth = 0.0

        # Metadata
        self.metadata: Dict[str, Any] = {}
        self.tags: List[str] = []

        # Connected meshes
        self.connected_meshes: Set[str] = set()
        self.mesh_links: Dict[str, float] = {}

        # Logger
        self.logger = logging.getLogger("gram_mesh")
        self.logger.setLevel(logging.INFO)

        print(f"🌿 GRAM Mesh created: {self.name} ({self.id[:12]})")
        print(f"   Topology: {self.topology.value}")

    # ============================================================
    # ID GENERATION
    # ============================================================

    def _generate_id(self) -> str:
        """Gjeneron ID unike"""
        timestamp = int(time.time() * 1000)
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"mesh_{timestamp}_{random_hash}"

    def _generate_wave_signature(self) -> str:
        """Gjeneron signature vale"""
        return hashlib.md5(
            f"{time.time()}_{self.resonance}".encode()
        ).hexdigest()[:8]

    # ============================================================
    # NODE MANAGEMENT
    # ============================================================

    def add_node(
        self,
        node_id: str,
        content: Any,
        resonance: float = 0.5,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MeshNode:
        """Shton një nyje në rrjet"""
        if node_id in self.nodes:
            return self.nodes[node_id]

        node = MeshNode(
            id=node_id,
            content=content,
            resonance=resonance,
            weight=weight,
            metadata=metadata or {}
        )

        self.nodes[node_id] = node
        self.updated_at = time.time()
        self._update_statistics()

        return node

    def remove_node(self, node_id: str) -> bool:
        """Heq një nyje nga rrjeti"""
        if node_id not in self.nodes:
            return False

        # Remove all edges connected to this node
        edges_to_remove = []
        for (src, tgt), edge in self.edges.items():
            if src == node_id or tgt == node_id:
                edges_to_remove.append((src, tgt))

        for key in edges_to_remove:
            del self.edges[key]

        del self.nodes[node_id]
        self.updated_at = time.time()
        self._update_statistics()

        return True

    def get_node(self, node_id: str) -> Optional[MeshNode]:
        """Merr një nyje"""
        return self.nodes.get(node_id)

    def get_all_nodes(self) -> List[MeshNode]:
        """Merr të gjitha nyjet"""
        return list(self.nodes.values())

    # ============================================================
    # EDGE MANAGEMENT
    # ============================================================

    def add_edge(
        self,
        source: str,
        target: str,
        weight: float = 1.0,
        strength: float = 0.5,
        edge_type: str = "semantic",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[MeshEdge]:
        """Shton një lidhje në rrjet"""
        if source not in self.nodes or target not in self.nodes:
            return None

        if source == target:
            return None

        key = (source, target)
        if key in self.edges:
            return self.edges[key]

        edge = MeshEdge(
            source=source,
            target=target,
            weight=weight,
            strength=strength,
            type=edge_type,
            metadata=metadata or {}
        )

        self.edges[key] = edge

        # Add to node connections
        self.nodes[source].connections.add(target)
        self.nodes[target].connections.add(source)

        self.updated_at = time.time()
        self._update_statistics()

        return edge

    def remove_edge(self, source: str, target: str) -> bool:
        """Heq një lidhje nga rrjeti"""
        key = (source, target)
        if key not in self.edges:
            return False

        del self.edges[key]

        # Remove from node connections
        if source in self.nodes:
            self.nodes[source].connections.discard(target)
        if target in self.nodes:
            self.nodes[target].connections.discard(source)

        self.updated_at = time.time()
        self._update_statistics()

        return True

    def get_edge(self, source: str, target: str) -> Optional[MeshEdge]:
        """Merr një lidhje"""
        return self.edges.get((source, target))

    def get_neighbors(self, node_id: str) -> Set[str]:
        """Merr fqinjët e një nyje"""
        if node_id not in self.nodes:
            return set()
        return self.nodes[node_id].connections.copy()

    def get_degree(self, node_id: str) -> int:
        """Merr shkallën e një nyje"""
        if node_id not in self.nodes:
            return 0
        return len(self.nodes[node_id].connections)

    # ============================================================
    # MESH GROWTH
    # ============================================================

    def grow(self, amount: float = 0.1) -> None:
        """Rrit rrjetin"""
        self.growth_count += 1
        self.growth_rate = min(1.0, self.growth_rate + amount * 0.01)
        self.resonance = min(1.0, self.resonance + amount * 0.05)
        self.updated_at = time.time()
        self.last_growth = time.time()

        # Update state based on growth
        if self.growth_count > 100:
            self.state = MeshState.MATURE
        elif self.growth_count > 50:
            self.state = MeshState.GROWING
        elif self.growth_count > 10:
            self.state = MeshState.GROWING

        # Update wave signature
        self.wave_signature = self._generate_wave_signature()

        # Check if resonant
        if self.resonance > 0.8:
            self.state = MeshState.RESONANT

        # Create connections based on topology
        self._grow_topology()

        self._update_statistics()

    def _grow_topology(self) -> None:
        """Rrit rrjetin bazuar në topologji"""
        if len(self.nodes) < 2:
            return

        if self.topology == MeshTopology.RANDOM:
            self._grow_random()
        elif self.topology == MeshTopology.SCALE_FREE:
            self._grow_scale_free()
        elif self.topology == MeshTopology.SMALL_WORLD:
            self._grow_small_world()
        elif self.topology == MeshTopology.ORGANIC:
            self._grow_organic()

    def _grow_random(self) -> None:
        """Rritje rastësore"""
        import random
        nodes = list(self.nodes.keys())

        # Add random connections
        for i in range(min(3, len(nodes) - 1)):
            source = random.choice(nodes)
            target = random.choice([n for n in nodes if n != source])
            if source != target and (source, target) not in self.edges:
                self.add_edge(
                    source=source,
                    target=target,
                    strength=random.uniform(0.3, 0.8)
                )

    def _grow_scale_free(self) -> None:
        """Rritje pa shkallë"""
        import random
        nodes = list(self.nodes.keys())

        # Preferential attachment
        if len(nodes) > 1:
            # Sort nodes by degree
            degrees = {n: self.get_degree(n) for n in nodes}
            total_degree = sum(degrees.values())

            if total_degree > 0:
                # Weighted random selection
                weights = [degrees[n] / total_degree for n in nodes]
                source = random.choices(nodes, weights=weights, k=1)[0]
                target = random.choices(nodes, weights=weights, k=1)[0]

                if source != target and (source, target) not in self.edges:
                    self.add_edge(
                        source=source,
                        target=target,
                        strength=0.5 + random.uniform(0, 0.3)
                    )

    def _grow_small_world(self) -> None:
        """Rritje botë e vogël"""
        import random
        nodes = list(self.nodes.keys())

        # Connect nearby nodes
        for i, node in enumerate(nodes):
            for j in range(i + 1, min(i + 3, len(nodes))):
                if (node, nodes[j]) not in self.edges:
                    self.add_edge(
                        source=node,
                        target=nodes[j],
                        strength=0.6 + random.uniform(0, 0.2)
                    )

    def _grow_organic(self) -> None:
        """Rritje organike"""
        import random
        nodes = list(self.nodes.keys())

        if len(nodes) > 1:
            # Connect based on resonance
            for i, node1 in enumerate(nodes):
                for j in range(i + 1, min(i + 2, len(nodes))):
                    node2 = nodes[j]
                    if node1 in self.nodes and node2 in self.nodes:
                        resonance1 = self.nodes[node1].resonance
                        resonance2 = self.nodes[node2].resonance
                        strength = (resonance1 + resonance2) / 2

                        if strength > 0.3 and (node1, node2) not in self.edges:
                            self.add_edge(
                                source=node1,
                                target=node2,
                                strength=strength
                            )

    # ============================================================
    # MESH CONNECTIONS
    # ============================================================

    def connect_to_mesh(self, mesh_id: str, strength: float = 0.5) -> None:
        """Lidh rrjetin me një rrjet tjetër"""
        self.connected_meshes.add(mesh_id)
        self.mesh_links[mesh_id] = strength
        self.updated_at = time.time()

    def disconnect_from_mesh(self, mesh_id: str) -> None:
        """Shkëput lidhjen me një rrjet tjetër"""
        self.connected_meshes.discard(mesh_id)
        if mesh_id in self.mesh_links:
            del self.mesh_links[mesh_id]
        self.updated_at = time.time()

    def get_connected_meshes(self) -> Set[str]:
        """Merr të gjitha rrjetet e lidhura"""
        return self.connected_meshes.copy()

    # ============================================================
    # STATISTICS
    # ============================================================

    def _update_statistics(self) -> None:
        """Përditëson statistikat e rrjetit"""
        n = len(self.nodes)
        e = len(self.edges)

        if n == 0:
            self.statistics = MeshStatistics()
            return

        # Basic stats
        self.statistics.total_nodes = n
        self.statistics.total_edges = e

        # Density
        max_edges = n * (n - 1) / 2
        self.statistics.density = e / max_edges if max_edges > 0 else 0

        # Average degree
        total_degree = sum(self.get_degree(node_id) for node_id in self.nodes)
        self.statistics.avg_degree = total_degree / n if n > 0 else 0

        # Average resonance
        total_resonance = sum(node.resonance for node in self.nodes.values())
        self.statistics.avg_resonance = total_resonance / n if n > 0 else 0

        # Clustering coefficient (approximate)
        triangles = 0
        for node_id in self.nodes:
            neighbors = self.get_neighbors(node_id)
            k = len(neighbors)
            if k > 1:
                # Count edges among neighbors
                neighbor_edges = 0
                for n1 in neighbors:
                    for n2 in neighbors:
                        if n1 != n2 and (n1, n2) in self.edges:
                            neighbor_edges += 1
                triangles += neighbor_edges / (k * (k - 1))

        self.statistics.avg_clustering = triangles / n if n > 0 else 0

        # Coherence (based on resonance and clustering)
        self.statistics.coherence = (
            self.statistics.avg_resonance * 0.6 +
            self.statistics.avg_clustering * 0.4
        )

        # Resilience (based on density and avg degree)
        self.statistics.resilience = min(1.0,
            self.statistics.density * 0.5 +
            (self.statistics.avg_degree / (n - 1)) * 0.5
        )

        # Efficiency (based on avg path length - approximate)
        # Simple approximation using density
        self.statistics.efficiency = min(1.0, self.statistics.density * 2)

        # Connected components
        self.statistics.connected_components = self._count_components()
        self.statistics.largest_component = self._get_largest_component()

    def _count_components(self) -> int:
        """Numri i komponentëve të lidhur"""
        visited = set()
        components = 0

        for node_id in self.nodes:
            if node_id not in visited:
                components += 1
                stack = [node_id]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        stack.extend(self.get_neighbors(current) - visited)

        return components

    def _get_largest_component(self) -> int:
        """Madhësia e komponentit më të madh"""
        visited = set()
        largest = 0

        for node_id in self.nodes:
            if node_id not in visited:
                component = set()
                stack = [node_id]
                while stack:
                    current = stack.pop()
                    if current not in component:
                        component.add(current)
                        stack.extend(self.get_neighbors(current) - component)

                visited.update(component)
                largest = max(largest, len(component))

        return largest

    def get_statistics(self) -> MeshStatistics:
        """Merr statistikat e rrjetit"""
        self._update_statistics()
        return self.statistics

    # ============================================================
    # PATH FINDING
    # ============================================================

    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """Gjen rrugën më të shkurtër midis dy nyjeve"""
        if source not in self.nodes or target not in self.nodes:
            return None

        if source == target:
            return [source]

        # BFS
        visited = {source}
        queue = deque([(source, [source])])

        while queue:
            current, path = queue.popleft()

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]

                    if neighbor == target:
                        return new_path

                    queue.append((neighbor, new_path))

        return None

    def get_distance(self, source: str, target: str) -> int:
        """Merr distancën midis dy nyjeve"""
        path = self.find_path(source, target)
        return len(path) - 1 if path else -1

    # ============================================================
    # RESONANCE
    # ============================================================

    def resonate(self, strength: float) -> None:
        """Rezonon rrjetin"""
        self.resonance = min(1.0, (self.resonance + strength) / 2)

        # Propagate resonance to nodes
        for node in self.nodes.values():
            node.resonance = min(1.0, (node.resonance + strength * 0.5) / 2)

        self.updated_at = time.time()

        if self.resonance > 0.8:
            self.state = MeshState.RESONANT

    # ============================================================
    # VISUALIZATION
    # ============================================================

    def visualize(self) -> str:
        """Vizualizon rrjetin"""
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════════╗")
        lines.append("║                   🌿 GRAM MESH VISUALIZATION                    ║")
        lines.append("╠══════════════════════════════════════════════════════════════════╣")
        lines.append(f"║ Mesh: {self.name} ({self.id[:12]})".ljust(58) + "║")
        lines.append(f"║ Topology: {self.topology.value}".ljust(58) + "║")
        lines.append(f"║ State: {self.state.value}".ljust(58) + "║")
        lines.append(f"║ Resonance: {self.resonance:.2f}".ljust(58) + "║")
        lines.append(f"║ Nodes: {len(self.nodes)}".ljust(58) + "║")
        lines.append(f"║ Edges: {len(self.edges)}".ljust(58) + "║")
        lines.append("╠══════════════════════════════════════════════════════════════════╣")

        # Statistics
        stats = self.get_statistics()
        lines.append(f"║ Density: {stats.density:.3f}".ljust(58) + "║")
        lines.append(f"║ Avg Degree: {stats.avg_degree:.2f}".ljust(58) + "║")
        lines.append(f"║ Avg Clustering: {stats.avg_clustering:.3f}".ljust(58) + "║")
        lines.append(f"║ Avg Resonance: {stats.avg_resonance:.3f}".ljust(58) + "║")
        lines.append(f"║ Coherence: {stats.coherence:.3f}".ljust(58) + "║")
        lines.append(f"║ Resilience: {stats.resilience:.3f}".ljust(58) + "║")
        lines.append(f"║ Efficiency: {stats.efficiency:.3f}".ljust(58) + "║")
        lines.append(f"║ Components: {stats.connected_components}".ljust(58) + "║")
        lines.append("╠══════════════════════════════════════════════════════════════════╣")

        # Sample nodes
        nodes_sample = list(self.nodes.keys())[:10]
        if nodes_sample:
            lines.append("\n  🌿 Sample Nodes:")
            for node_id in nodes_sample[:5]:
                node = self.nodes[node_id]
                degree = self.get_degree(node_id)
                lines.append(f"    • {node_id[:12]}: deg={degree}, res={node.resonance:.2f}")

        # Connected meshes
        if self.connected_meshes:
            lines.append("\n  🔗 Connected Meshes:")
            for mesh_id in list(self.connected_meshes)[:5]:
                strength = self.mesh_links.get(mesh_id, 0.5)
                lines.append(f"    • {mesh_id[:12]}: {strength:.2f}")

        lines.append("╚══════════════════════════════════════════════════════════════════╝")
        return "\n".join(lines)

    # ============================================================
    # EXPORT / IMPORT
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        """Konverton në dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "topology": self.topology.value,
            "state": self.state.value,
            "resonance": self.resonance,
            "wave_signature": self.wave_signature,
            "growth_count": self.growth_count,
            "growth_rate": self.growth_rate,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_growth": self.last_growth,
            "metadata": self.metadata,
            "tags": self.tags,
            "connected_meshes": list(self.connected_meshes),
            "mesh_links": self.mesh_links,
            "nodes": {
                nid: {
                    "content": node.content,
                    "resonance": node.resonance,
                    "weight": node.weight,
                    "metadata": node.metadata,
                    "created_at": node.created_at,
                    "updated_at": node.updated_at,
                    "connections": list(node.connections)
                }
                for nid, node in self.nodes.items()
            },
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "weight": e.weight,
                    "strength": e.strength,
                    "type": e.type,
                    "metadata": e.metadata,
                    "created_at": e.created_at
                }
                for e in self.edges.values()
            ],
            "statistics": {
                "total_nodes": self.statistics.total_nodes,
                "total_edges": self.statistics.total_edges,
                "density": self.statistics.density,
                "avg_degree": self.statistics.avg_degree,
                "avg_clustering": self.statistics.avg_clustering,
                "avg_path_length": self.statistics.avg_path_length,
                "avg_resonance": self.statistics.avg_resonance,
                "coherence": self.statistics.coherence,
                "resilience": self.statistics.resilience,
                "efficiency": self.statistics.efficiency,
                "connected_components": self.statistics.connected_components,
                "largest_component": self.statistics.largest_component
            }
        }

    def to_json(self) -> str:
        """Konverton në JSON"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GRAMMesh':
        """Krijon një rrjet nga dictionary"""
        mesh = cls(
            topology=MeshTopology(data["topology"]),
            name=data["name"]
        )

        mesh.id = data["id"]
        mesh.state = MeshState(data["state"])
        mesh.resonance = data["resonance"]
        mesh.wave_signature = data["wave_signature"]
        mesh.growth_count = data["growth_count"]
        mesh.growth_rate = data["growth_rate"]
        mesh.created_at = data["created_at"]
        mesh.updated_at = data["updated_at"]
        mesh.last_growth = data["last_growth"]
        mesh.metadata = data["metadata"]
        mesh.tags = data["tags"]
        mesh.connected_meshes = set(data["connected_meshes"])
        mesh.mesh_links = data["mesh_links"]

        # Restore nodes
        for node_id, node_data in data["nodes"].items():
            mesh.nodes[node_id] = MeshNode(
                id=node_id,
                content=node_data["content"],
                connections=set(node_data["connections"]),
                resonance=node_data["resonance"],
                weight=node_data["weight"],
                metadata=node_data["metadata"],
                created_at=node_data["created_at"],
                updated_at=node_data["updated_at"]
            )

        # Restore edges
        for edge_data in data["edges"]:
            key = (edge_data["source"], edge_data["target"])
            mesh.edges[key] = MeshEdge(
                source=edge_data["source"],
                target=edge_data["target"],
                weight=edge_data["weight"],
                strength=edge_data["strength"],
                type=edge_data["type"],
                metadata=edge_data["metadata"],
                created_at=edge_data["created_at"]
            )

        # Restore statistics
        stats_data = data["statistics"]
        mesh.statistics = MeshStatistics(
            total_nodes=stats_data["total_nodes"],
            total_edges=stats_data["total_edges"],
            density=stats_data["density"],
            avg_degree=stats_data["avg_degree"],
            avg_clustering=stats_data["avg_clustering"],
            avg_path_length=stats_data["avg_path_length"],
            avg_resonance=stats_data["avg_resonance"],
            coherence=stats_data["coherence"],
            resilience=stats_data["resilience"],
            efficiency=stats_data["efficiency"],
            connected_components=stats_data["connected_components"],
            largest_component=stats_data["largest_component"]
        )

        return mesh


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_mesh(
    topology: MeshTopology = MeshTopology.ORGANIC,
    name: str = "Unnamed Mesh"
) -> GRAMMesh:
    """Krijon një rrjet të ri"""
    return GRAMMesh(topology=topology, name=name)


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "GRAMMesh",
    "MeshState",
    "MeshTopology",
    "MeshMetric",
    "MeshNode",
    "MeshEdge",
    "MeshStatistics",
    "create_mesh"
]
