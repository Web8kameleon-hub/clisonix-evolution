# -*- coding: utf-8 -*-
"""
GRAM FIELD - Growing Resonance Adaptive Mesh Field
"Një fushë me bar që rritet dhe përhapet"
================================================================================
Author: Ledjan Ahmati
System: Clisonix AI - Universal Cognitive Mesh
================================================================================

GRAM Field = Një fushë me bar
- Përmban shumë clusters
- Rritet dhe përhapet
- Ka rezonancë dhe valë
- Krijon lidhje midis clusters
================================================================================
"""

from __future__ import annotations

import hashlib
import time
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict

# ============================================================
# ENUMS
# ============================================================

class FieldType(Enum):
    """Llojet e fushave"""
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    RESONANT = "resonant"
    LINGUISTIC = "linguistic"
    HYBRID = "hybrid"
    ORGANIC = "organic"
    COGNITIVE = "cognitive"

class FieldState(Enum):
    """Gjendja e fushës"""
    SEED = "seed"           # Farë - sapo krijuar
    GROWING = "growing"     # Duke u rritur
    MATURE = "mature"       # E pjekur
    RESONANT = "resonant"   # Në rezonancë
    SPREADING = "spreading" # Duke u përhapur
    DECAYING = "decaying"   # Duke u kalbur
    DORMANT = "dormant"     # E fjetur

class GrowthPattern(Enum):
    """Modeli i rritjes"""
    ORGANIC = "organic"     # Organik - i natyrshëm
    RADIAL = "radial"       # Radial - nga qendra
    NETWORK = "network"     # Rrjet - lidhje të shumta
    CLUSTER = "cluster"     # Tufë - grupe
    CHAOTIC = "chaotic"     # Kaotik - pa model
    WAVE = "wave"           # Valë - si dallgë

# ============================================================
# GRAM FIELD - Main Class
# ============================================================

class GRAMField:
    """
    Një fushë me bar që rritet dhe përhapet.

    Përmban shumë clusters.
    Rritet dhe përhapet natyrshëm.
    Ka rezonancë dhe valë.
    """

    def __init__(
        self,
        field_id: Optional[str] = None,
        field_type: FieldType = FieldType.ORGANIC,
        name: str = "Unnamed Field",
        description: str = ""
    ):
        self.id = field_id or self._generate_id()
        self.type = field_type
        self.name = name
        self.description = description

        # Clusters
        self.clusters: Dict[str, Dict[str, Any]] = {}
        self.cluster_nodes: Dict[str, Set[str]] = defaultdict(set)

        # State
        self.state = FieldState.SEED
        self.resonance = 0.5
        self.wave_signature = self._generate_wave_signature()

        # Growth
        self.growth_pattern = GrowthPattern.ORGANIC
        self.growth_count = 0
        self.growth_rate = 0.1

        # Metrics
        self.total_nodes = 0
        self.total_clusters = 0
        self.avg_resonance = 0.0
        self.coherence = 0.5

        # Time
        self.created_at = time.time()
        self.updated_at = time.time()
        self.last_growth = 0.0

        # Metadata
        self.metadata: Dict[str, Any] = {}
        self.tags: List[str] = []

        # Connections to other fields
        self.connected_fields: Set[str] = set()
        self.field_links: Dict[str, float] = {}  # field_id -> strength

        # Integration with GRAM core
        self._gram_core = None

    # ============================================================
    # ID GENERATION
    # ============================================================

    def _generate_id(self) -> str:
        """Gjeneron ID unike për fushën"""
        timestamp = int(time.time() * 1000)
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"field_{timestamp}_{random_hash}"

    def _generate_wave_signature(self) -> str:
        """Gjeneron signature vale"""
        return hashlib.md5(
            f"{time.time()}_{self.resonance}".encode()
        ).hexdigest()[:8]

    # ============================================================
    # CLUSTER MANAGEMENT
    # ============================================================

    def add_cluster(
        self,
        cluster_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Shton një cluster në fushë"""
        if cluster_id in self.clusters:
            return

        self.clusters[cluster_id] = {
            "id": cluster_id,
            "metadata": metadata or {},
            "added_at": time.time(),
            "node_count": 0
        }

        self.cluster_nodes[cluster_id] = set()
        self.total_clusters += 1
        self.updated_at = time.time()

    def remove_cluster(self, cluster_id: str) -> bool:
        """Heq një cluster nga fusha"""
        if cluster_id not in self.clusters:
            return False

        del self.clusters[cluster_id]
        if cluster_id in self.cluster_nodes:
            del self.cluster_nodes[cluster_id]

        self.total_clusters -= 1
        self.updated_at = time.time()
        return True

    def add_node_to_cluster(self, cluster_id: str, node_id: str) -> bool:
        """Shton një node në një cluster brenda fushës"""
        if cluster_id not in self.clusters:
            return False

        self.cluster_nodes[cluster_id].add(node_id)
        self.clusters[cluster_id]["node_count"] = len(self.cluster_nodes[cluster_id])
        self.total_nodes += 1
        self.updated_at = time.time()
        return True

    def remove_node_from_cluster(self, cluster_id: str, node_id: str) -> bool:
        """Heq një node nga një cluster"""
        if cluster_id not in self.clusters:
            return False

        if node_id in self.cluster_nodes[cluster_id]:
            self.cluster_nodes[cluster_id].remove(node_id)
            self.clusters[cluster_id]["node_count"] = len(self.cluster_nodes[cluster_id])
            self.total_nodes -= 1
            self.updated_at = time.time()
            return True

        return False

    def get_cluster_nodes(self, cluster_id: str) -> Set[str]:
        """Merr të gjitha nodes në një cluster"""
        return self.cluster_nodes.get(cluster_id, set())

    def get_all_nodes(self) -> Set[str]:
        """Merr të gjitha nodes në të gjitha clusters"""
        all_nodes = set()
        for nodes in self.cluster_nodes.values():
            all_nodes.update(nodes)
        return all_nodes

    # ============================================================
    # FIELD GROWTH
    # ============================================================

    def grow(self, amount: float = 0.1) -> None:
        """Rrit fushën"""
        self.growth_count += 1
        self.growth_rate = min(1.0, self.growth_rate + amount * 0.01)
        self.resonance = min(1.0, self.resonance + amount * 0.05)
        self.updated_at = time.time()
        self.last_growth = time.time()

        # Update state based on growth
        if self.growth_count > 100:
            self.state = FieldState.MATURE
        elif self.growth_count > 50:
            self.state = FieldState.GROWING
        elif self.growth_count > 10:
            self.state = FieldState.GROWING

        # Update wave signature
        self.wave_signature = self._generate_wave_signature()

        # Check if resonant
        if self.resonance > 0.8:
            self.state = FieldState.RESONANT

        # Check if spreading
        if self.growth_count > 200:
            self.state = FieldState.SPREADING

    def spread(self, amount: float = 0.05) -> None:
        """Përhap fushën"""
        self.growth_rate = min(1.0, self.growth_rate + amount)
        self.resonance = min(1.0, self.resonance + amount * 0.03)

        # Create new clusters if spreading
        if len(self.clusters) < 10 and self.growth_count > 20:
            # Create a new cluster
            new_cluster_id = f"spread_{int(time.time()*1000)}_{len(self.clusters)}"
            self.add_cluster(new_cluster_id, {"spread_from": "organic_growth"})

        self.updated_at = time.time()
        self.state = FieldState.SPREADING

    def resonate(self, strength: float) -> None:
        """Rezonon fushën"""
        self.resonance = min(1.0, (self.resonance + strength) / 2)
        self.updated_at = time.time()

        if self.resonance > 0.8:
            self.state = FieldState.RESONANT

    def decay(self, amount: float = 0.02) -> None:
        """Kalbon fushën"""
        self.resonance = max(0.0, self.resonance - amount)
        self.growth_rate = max(0.0, self.growth_rate - amount * 0.5)
        self.updated_at = time.time()

        if self.resonance < 0.2:
            self.state = FieldState.DECAYING
        elif self.resonance < 0.1:
            self.state = FieldState.DORMANT

    # ============================================================
    # FIELD CONNECTIONS
    # ============================================================

    def connect_to_field(self, field_id: str, strength: float = 0.5) -> None:
        """Lidh fushën me një fushë tjetër"""
        self.connected_fields.add(field_id)
        self.field_links[field_id] = strength
        self.updated_at = time.time()

    def disconnect_from_field(self, field_id: str) -> None:
        """Shkëput lidhjen me një fushë tjetër"""
        self.connected_fields.discard(field_id)
        if field_id in self.field_links:
            del self.field_links[field_id]
        self.updated_at = time.time()

    def get_connection_strength(self, field_id: str) -> float:
        """Merr forcën e lidhjes me një fushë tjetër"""
        return self.field_links.get(field_id, 0.0)

    def get_connected_fields(self) -> Set[str]:
        """Merr të gjitha fushat e lidhura"""
        return self.connected_fields.copy()

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_stats(self) -> Dict[str, Any]:
        """Merr statistika të fushës"""
        # Calculate average resonance
        avg_res = 0.0
        if self.total_nodes > 0:
            # This would need access to GRAM nodes
            # For now, use field resonance
            avg_res = self.resonance

        # Calculate coherence
        coherence = self.coherence
        if self.total_clusters > 1:
            # Higher cluster count can mean lower coherence
            coherence = max(0.1, 1.0 - (self.total_clusters * 0.05))

        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "state": self.state.value,
            "resonance": self.resonance,
            "wave_signature": self.wave_signature,
            "total_nodes": self.total_nodes,
            "total_clusters": self.total_clusters,
            "avg_resonance": avg_res,
            "coherence": coherence,
            "growth_count": self.growth_count,
            "growth_rate": self.growth_rate,
            "growth_pattern": self.growth_pattern.value,
            "connected_fields": len(self.connected_fields),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_growth": self.last_growth,
            "tags": self.tags
        }

    def get_cluster_stats(self) -> Dict[str, Dict[str, Any]]:
        """Merr statistika për çdo cluster"""
        stats = {}
        for cluster_id, data in self.clusters.items():
            node_count = len(self.cluster_nodes.get(cluster_id, set()))
            stats[cluster_id] = {
                "node_count": node_count,
                "added_at": data["added_at"],
                "metadata": data["metadata"]
            }
        return stats

    # ============================================================
    # VISUALIZATION
    # ============================================================

    def visualize(self) -> str:
        """Vizualizon fushën"""
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════════╗")
        lines.append("║                   🌿 GRAM FIELD VISUALIZATION                   ║")
        lines.append("╠══════════════════════════════════════════════════════════════════╣")
        lines.append(f"║ Field: {self.name} ({self.id[:12]})".ljust(58) + "║")
        lines.append(f"║ Type: {self.type.value}".ljust(58) + "║")
        lines.append(f"║ State: {self.state.value}".ljust(58) + "║")
        lines.append(f"║ Resonance: {self.resonance:.2f}".ljust(58) + "║")
        lines.append(f"║ Total Nodes: {self.total_nodes}".ljust(58) + "║")
        lines.append(f"║ Total Clusters: {self.total_clusters}".ljust(58) + "║")
        lines.append(f"║ Growth Rate: {self.growth_rate:.2f}".ljust(58) + "║")
        lines.append(f"║ Connected Fields: {len(self.connected_fields)}".ljust(58) + "║")
        lines.append("╠══════════════════════════════════════════════════════════════════╣")

        # Clusters
        lines.append("\n  🌿 Clusters:")
        for cluster_id, data in self.clusters.items():
            node_count = len(self.cluster_nodes.get(cluster_id, set()))
            lines.append(f"    • {cluster_id[:12]}: {node_count} nodes")

        # Connected fields
        if self.connected_fields:
            lines.append("\n  🔗 Connected Fields:")
            for field_id in self.connected_fields[:5]:
                strength = self.field_links.get(field_id, 0.5)
                lines.append(f"    • {field_id[:12]}: {strength:.2f}")

        lines.append("╚══════════════════════════════════════════════════════════════════╝")
        return "\n".join(lines)

    # ============================================================
    # EXPORT / IMPORT
    # ============================================================

    def to_dict(self) -> Dict[str, Any]:
        """Konverton në dictionary"""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "state": self.state.value,
            "resonance": self.resonance,
            "wave_signature": self.wave_signature,
            "growth_pattern": self.growth_pattern.value,
            "growth_count": self.growth_count,
            "growth_rate": self.growth_rate,
            "total_nodes": self.total_nodes,
            "total_clusters": self.total_clusters,
            "avg_resonance": self.avg_resonance,
            "coherence": self.coherence,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_growth": self.last_growth,
            "metadata": self.metadata,
            "tags": self.tags,
            "connected_fields": list(self.connected_fields),
            "field_links": self.field_links,
            "clusters": {
                cid: {
                    "node_count": len(self.cluster_nodes.get(cid, set())),
                    "added_at": data["added_at"],
                    "metadata": data["metadata"]
                }
                for cid, data in self.clusters.items()
            }
        }

    def to_json(self) -> str:
        """Konverton në JSON"""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GRAMField':
        """Krijon një fushë nga dictionary"""
        field = cls(
            field_id=data["id"],
            field_type=FieldType(data["type"]),
            name=data["name"],
            description=data.get("description", "")
        )

        field.state = FieldState(data["state"])
        field.resonance = data["resonance"]
        field.wave_signature = data["wave_signature"]
        field.growth_pattern = GrowthPattern(data["growth_pattern"])
        field.growth_count = data["growth_count"]
        field.growth_rate = data["growth_rate"]
        field.total_nodes = data["total_nodes"]
        field.total_clusters = data["total_clusters"]
        field.avg_resonance = data["avg_resonance"]
        field.coherence = data["coherence"]
        field.created_at = data["created_at"]
        field.updated_at = data["updated_at"]
        field.last_growth = data["last_growth"]
        field.metadata = data["metadata"]
        field.tags = data["tags"]
        field.connected_fields = set(data["connected_fields"])
        field.field_links = data["field_links"]

        # Restore clusters
        for cluster_id, cluster_data in data["clusters"].items():
            field.clusters[cluster_id] = {
                "id": cluster_id,
                "metadata": cluster_data["metadata"],
                "added_at": cluster_data["added_at"],
                "node_count": cluster_data["node_count"]
            }
            field.cluster_nodes[cluster_id] = set()

        return field


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_field(
    field_type: FieldType = FieldType.ORGANIC,
    name: str = "Unnamed Field",
    description: str = ""
) -> GRAMField:
    """Krijon një fushë të re"""
    return GRAMField(
        field_type=field_type,
        name=name,
        description=description
    )


def merge_fields(field1: GRAMField, field2: GRAMField) -> GRAMField:
    """Bashkon dy fusha"""
    # Create new field
    merged = GRAMField(
        field_type=FieldType.HYBRID,
        name=f"Merged: {field1.name} + {field2.name}",
        description=f"Merge of {field1.name} and {field2.name}"
    )

    # Copy clusters from field1
    for cluster_id in field1.clusters:
        merged.add_cluster(cluster_id, field1.clusters[cluster_id]["metadata"])
        nodes = field1.get_cluster_nodes(cluster_id)
        for node_id in nodes:
            merged.add_node_to_cluster(cluster_id, node_id)

    # Copy clusters from field2
    for cluster_id in field2.clusters:
        if cluster_id not in merged.clusters:
            merged.add_cluster(cluster_id, field2.clusters[cluster_id]["metadata"])
        nodes = field2.get_cluster_nodes(cluster_id)
        for node_id in nodes:
            merged.add_node_to_cluster(cluster_id, node_id)

    # Merge metadata
    merged.metadata = {
        "source_fields": [field1.id, field2.id],
        "field1_name": field1.name,
        "field2_name": field2.name,
        **field1.metadata,
        **field2.metadata
    }

    # Merge tags
    merged.tags = list(set(field1.tags + field2.tags))

    return merged


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "GRAMField",
    "FieldType",
    "FieldState",
    "GrowthPattern",
    "create_field",
    "merge_fields"
]
