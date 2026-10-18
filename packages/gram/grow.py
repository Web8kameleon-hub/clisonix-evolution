# -*- coding: utf-8 -*-
"""
GRAM GROW - Growing Resonance Adaptive Mesh Growth Engine
"Si rritet bari - natyralisht, organikisht, pa fund"
================================================================================
Author: Ledjan Ahmati
System: Clisonix AI - Universal Cognitive Mesh
================================================================================

GRAM Grow = Motorri i rritjes
- Rritja organike e barit
- Përhapja natyrale
- Lidhje të reja
- Rezonancë dhe valë
- Pa kufi
================================================================================
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import random
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque

# ============================================================
# ENUMS
# ============================================================

class GrowthPhase(Enum):
    """Fazat e rritjes"""
    SEED = "seed"           # Farë - fillimi
    GERMINATION = "germination"  # Mbirje
    SHOOT = "shoot"         # Filiz
    GROWING = "growing"     # Duke u rritur
    MATURE = "mature"       # I pjekur
    SPREADING = "spreading" # Duke u përhapur
    DECAYING = "decaying"   # Duke u kalbur
    REGENERATING = "regenerating" # Duke u rigjeneruar

class GrowthPattern(Enum):
    """Modeli i rritjes"""
    ORGANIC = "organic"     # Organik - i natyrshëm
    RADIAL = "radial"       # Radial - nga qendra
    CLUSTER = "cluster"     # Tufë - grupe
    NETWORK = "network"     # Rrjet - lidhje
    CHAOTIC = "chaotic"     # Kaotik - pa model
    WAVE = "wave"           # Valë - si dallgë
    SPIRAL = "spiral"       # Spiral - rrotullues
    FRACTAL = "fractal"     # Fraktal - vetë-përsëritës

class GrowthTrigger(Enum):
    """Shkaktarët e rritjes"""
    RESONANCE = "resonance"     # Rezonancë
    CONNECTION = "connection"   # Lidhje
    TIME = "time"               # Kohë
    ENERGY = "energy"           # Energji
    LEARNING = "learning"       # Mësim
    ADAPTATION = "adaptation"   # Përshtatje
    EXTERNAL = "external"       # E jashtme

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class GrowthConfig:
    """Konfigurimi i rritjes"""
    max_nodes: int = 100000
    growth_rate: float = 0.1
    spread_rate: float = 0.05
    decay_rate: float = 0.02
    resonance_threshold: float = 0.3
    connection_threshold: float = 0.2
    time_scale: float = 1.0
    energy_scale: float = 1.0
    max_connections: int = 1000
    auto_grow: bool = True
    auto_spread: bool = True
    auto_decay: bool = True
    growth_pattern: GrowthPattern = GrowthPattern.ORGANIC
    seed_count: int = 10
    propagation_depth: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "max_nodes": self.max_nodes,
            "growth_rate": self.growth_rate,
            "spread_rate": self.spread_rate,
            "decay_rate": self.decay_rate,
            "resonance_threshold": self.resonance_threshold,
            "connection_threshold": self.connection_threshold,
            "time_scale": self.time_scale,
            "energy_scale": self.energy_scale,
            "max_connections": self.max_connections,
            "auto_grow": self.auto_grow,
            "auto_spread": self.auto_spread,
            "auto_decay": self.auto_decay,
            "growth_pattern": self.growth_pattern.value,
            "seed_count": self.seed_count,
            "propagation_depth": self.propagation_depth
        }

@dataclass
class GrowthStats:
    """Statistika të rritjes"""
    total_nodes: int = 0
    total_connections: int = 0
    avg_degree: float = 0.0
    avg_resonance: float = 0.0
    growth_rate_current: float = 0.0
    spread_rate_current: float = 0.0
    decay_rate_current: float = 0.0
    phase: GrowthPhase = GrowthPhase.SEED
    timestamp: float = field(default_factory=time.time)
    growth_count: int = 0
    energy_level: float = 0.5
    coherence: float = 0.5

@dataclass
class GrowthEvent:
    """Event i rritjes"""
    id: str
    type: str
    source: str
    target: Optional[str] = None
    strength: float = 0.5
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================
# GRAM GROW - Main Class
# ============================================================

class GRAMGrow:
    """
    GRAM Grow - Motorri i rritjes

    Rritja organike e barit.
    Përhapja natyrale.
    Lidhje të reja.
    Rezonancë dhe valë.
    Pa kufi.
    """

    def __init__(
        self,
        config: Optional[GrowthConfig] = None,
        language: str = "en"
    ):
        self.config = config or GrowthConfig()
        self.language = language

        # State
        self.phase = GrowthPhase.SEED
        self.stats = GrowthStats()
        self.energy = 0.5
        self.coherence = 0.5

        # Events
        self.events: List[GrowthEvent] = []
        self.event_queue: deque = deque(maxlen=1000)

        # Growth state
        self.growth_count = 0
        self.spread_count = 0
        self.decay_count = 0
        self._last_growth_time = time.time()
        self._last_spread_time = time.time()
        self._last_decay_time = time.time()

        # Integration with GRAM core
        self._gram_core = None

        # Logger
        self.logger = logging.getLogger("gram_grow")
        self.logger.setLevel(logging.INFO)

        print("🌿 GRAM GROW Engine initialized")
        print(f"   Growth Pattern: {self.config.growth_pattern.value}")
        print(f"   Growth Rate: {self.config.growth_rate}")
        print(f"   Spread Rate: {self.config.spread_rate}")
        print(f"   Max Nodes: {self.config.max_nodes}")
        print(f"   Auto Grow: {self.config.auto_grow}")
        print("   👤 Author: Ledjan Ahmati")
        print("   🏢 System: Clisonix AI")

    # ============================================================
    # GROWTH METHODS
    # ============================================================

    def grow(self, amount: float = 0.1) -> List[GrowthEvent]:
        """
        Rrit barin.
        Krijon nyje dhe lidhje të reja.
        """
        if not self.config.auto_grow:
            return []

        events = []

        # Update energy
        self._update_energy(amount)

        # Determine phase
        self._update_phase()

        # Grow based on pattern
        if self.config.growth_pattern == GrowthPattern.ORGANIC:
            events.extend(self._grow_organic(amount))
        elif self.config.growth_pattern == GrowthPattern.RADIAL:
            events.extend(self._grow_radial(amount))
        elif self.config.growth_pattern == GrowthPattern.CLUSTER:
            events.extend(self._grow_cluster(amount))
        elif self.config.growth_pattern == GrowthPattern.NETWORK:
            events.extend(self._grow_network(amount))
        elif self.config.growth_pattern == GrowthPattern.WAVE:
            events.extend(self._grow_wave(amount))
        elif self.config.growth_pattern == GrowthPattern.SPIRAL:
            events.extend(self._grow_spiral(amount))
        elif self.config.growth_pattern == GrowthPattern.FRACTAL:
            events.extend(self._grow_fractal(amount))
        else:
            events.extend(self._grow_organic(amount))

        # Update statistics
        self._update_stats()

        # Store events
        for event in events:
            self.events.append(event)
            self.event_queue.append(event)

        self._last_growth_time = time.time()
        self.growth_count += len(events)

        return events

    def spread(self, amount: float = 0.05) -> List[GrowthEvent]:
        """
        Përhap barin.
        Krijon lidhje të reja midis nyjeve ekzistuese.
        """
        if not self.config.auto_spread:
            return []

        events = []

        if not self._gram_core:
            return events

        nodes = list(self._gram_core.nodes.values())
        if len(nodes) < 2:
            return events

        # Spread based on pattern
        for i in range(min(3, len(nodes) // 2)):
            node1 = random.choice(nodes)
            node2 = random.choice([n for n in nodes if n.id != node1.id])

            # Check resonance
            resonance = (node1.resonance + node2.resonance) / 2
            if resonance > self.config.resonance_threshold:
                # Create connection
                strength = resonance * amount
                events.append(GrowthEvent(
                    id=self._generate_event_id(),
                    type="connection",
                    source=node1.id,
                    target=node2.id,
                    strength=strength
                ))

                # Add to GRAM
                self._gram_core._create_resonance_connection(node1, node2, strength)

        self._last_spread_time = time.time()
        self.spread_count += len(events)

        return events

    def decay(self, amount: float = 0.02) -> List[GrowthEvent]:
        """
        Kalbon barin.
        Heq lidhje të dobëta dhe nyje të vjetra.
        """
        if not self.config.auto_decay:
            return []

        events = []

        if not self._gram_core:
            return events

        nodes = list(self._gram_core.nodes.values())

        # Decay based on age and resonance
        for node in nodes:
            age = time.time() - node.created_at
            age_factor = min(1.0, age / (3600 * 24 * 30))  # 30 days max

            # Check if should decay
            if node.resonance < 0.2 and age_factor > 0.5:
                # Too old and low resonance - remove
                events.append(GrowthEvent(
                    id=self._generate_event_id(),
                    type="decay",
                    source=node.id,
                    strength=0.1
                ))
                self._gram_core.delete_node(node.id)

        self._last_decay_time = time.time()
        self.decay_count += len(events)

        return events

    # ============================================================
    # GROWTH PATTERNS
    # ============================================================

    def _grow_organic(self, amount: float) -> List[GrowthEvent]:
        """Rritje organike - e natyrshme, pa model fiks"""
        events = []

        if not self._gram_core:
            return events

        # Add new nodes
        new_nodes_count = int(amount * 5) + 1
        for i in range(min(new_nodes_count, 10)):
            # Create content
            content = f"Organic growth {self.growth_count + i}"
            tags = ["organic", "growth"]

            # Add node
            node = self._gram_core.add_node(
                content=content,
                language=self.language,
                tags=tags,
                resonance=0.3 + random.random() * 0.3
            )

            if node:
                events.append(GrowthEvent(
                    id=self._generate_event_id(),
                    type="node",
                    source=node.id,
                    strength=node.resonance
                ))

        return events

    def _grow_radial(self, amount: float) -> List[GrowthEvent]:
        """Rritje radiale - nga qendra"""
        events = []

        if not self._gram_core:
            return events

        nodes = list(self._gram_core.nodes.values())
        if not nodes:
            return self._grow_organic(amount)

        # Find center node (highest degree or oldest)
        center = max(nodes, key=lambda n: n.get_degree())

        # Add nodes around center
        radius = len(nodes) // 10
        new_nodes_count = int(amount * 3) + 1

        for i in range(min(new_nodes_count, 5)):
            content = f"Radial growth {self.growth_count + i}"
            tags = ["radial", "growth"]

            node = self._gram_core.add_node(
                content=content,
                language=self.language,
                tags=tags,
                resonance=0.4 + random.random() * 0.2
            )

            if node:
                # Connect to center
                self._gram_core._create_resonance_connection(node, center, 0.6)
                events.append(GrowthEvent(
                    id=self._generate_event_id(),
                    type="node",
                    source=node.id,
                    target=center.id,
                    strength=0.6
                ))

        return events

    def _grow_cluster(self, amount: float) -> List[GrowthEvent]:
        """Rritje në tufa - grupe"""
        events = []

        if not self._gram_core:
            return events

        nodes = list(self._gram_core.nodes.values())
        if len(nodes) < 5:
            return self._grow_organic(amount)

        # Find clusters
        clusters = self._find_clusters()

        # Add nodes to existing clusters
        new_nodes_count = int(amount * 2) + 1
        for cluster in clusters[:3]:
            if not cluster:
                continue

            for i in range(min(new_nodes_count, 2)):
                cluster_node = random.choice(cluster)
                content = f"Cluster growth {self.growth_count + i}"
                tags = ["cluster", "growth"]

                node = self._gram_core.add_node(
                    content=content,
                    language=self.language,
                    tags=tags,
                    resonance=0.4 + random.random() * 0.2
                )

                if node:
                    # Connect to cluster node
                    self._gram_core._create_resonance_connection(node, cluster_node, 0.7)
                    events.append(GrowthEvent(
                        id=self._generate_event_id(),
                        type="node",
                        source=node.id,
                        target=cluster_node.id,
                        strength=0.7
                    ))

        return events

    def _grow_network(self, amount: float) -> List[GrowthEvent]:
        """Rritje si rrjet - lidhje të shumta"""
        events = []

        if not self._gram_core:
            return events

        nodes = list(self._gram_core.nodes.values())
        if len(nodes) < 10:
            return self._grow_organic(amount)

        # Create network connections
        connections_count = int(amount * 10) + 1
        for i in range(min(connections_count, 20)):
            node1 = random.choice(nodes)
            node2 = random.choice([n for n in nodes if n.id != node1.id])

            if (node1.id, node2.id) not in self._gram_core.edges:
                resonance = (node1.resonance + node2.resonance) / 2
                if resonance > self.config.resonance_threshold:
                    self._gram_core._create_resonance_connection(node1, node2, resonance)
                    events.append(GrowthEvent(
                        id=self._generate_event_id(),
                        type="connection",
                        source=node1.id,
                        target=node2.id,
                        strength=resonance
                    ))

        return events

    def _grow_wave(self, amount: float) -> List[GrowthEvent]:
        """Rritje si valë - përhapje e valëzuar"""
        events = []

        if not self._gram_core:
            return events

        nodes = list(self._gram_core.nodes.values())
        if len(nodes) < 3:
            return self._grow_organic(amount)

        # Find wave pattern
        wave_center = random.choice(nodes)
        wave_radius = len(nodes) // 10

        # Add nodes in wave pattern
        new_nodes_count = int(amount * 4) + 1
        for i in range(min(new_nodes_count, 6)):
            angle = random.random() * 2 * math.pi
            distance = wave_radius * (0.5 + random.random() * 0.5)

            content = f"Wave growth {self.growth_count + i}"
            tags = ["wave", "growth"]

            node = self._gram_core.add_node(
                content=content,
                language=self.language,
                tags=tags,
                resonance=0.3 + random.random() * 0.4
            )

            if node:
                # Connect to wave center
                self._gram_core._create_resonance_connection(node, wave_center, 0.5)
                events.append(GrowthEvent(
                    id=self._generate_event_id(),
                    type="node",
                    source=node.id,
                    target=wave_center.id,
                    strength=0.5
                ))

        return events

    def _grow_spiral(self, amount: float) -> List[GrowthEvent]:
        """Rritje spirale - rrotulluese"""
        events = []

        if not self._gram_core:
            return events

        nodes = list(self._gram_core.nodes.values())
        if len(nodes) < 2:
            return self._grow_organic(amount)

        # Find spiral center
        center = min(nodes, key=lambda n: n.get_degree())

        # Add nodes in spiral pattern
        new_nodes_count = int(amount * 3) + 1
        spiral_turn = self.growth_count / 100.0

        for i in range(min(new_nodes_count, 5)):
            angle = spiral_turn + i * 0.5
            distance = (i + 1) * 0.5

            content = f"Spiral growth {self.growth_count + i}"
            tags = ["spiral", "growth"]

            node = self._gram_core.add_node(
                content=content,
                language=self.language,
                tags=tags,
                resonance=0.3 + random.random() * 0.3
            )

            if node:
                # Connect to center
                self._gram_core._create_resonance_connection(node, center, 0.5)
                events.append(GrowthEvent(
                    id=self._generate_event_id(),
                    type="node",
                    source=node.id,
                    target=center.id,
                    strength=0.5
                ))

        return events

    def _grow_fractal(self, amount: float) -> List[GrowthEvent]:
        """Rritje fraktale - vetë-përsëritëse"""
        events = []

        if not self._gram_core:
            return events

        nodes = list(self._gram_core.nodes.values())
        if len(nodes) < 5:
            return self._grow_organic(amount)

        # Find pattern nodes
        pattern_nodes = [n for n in nodes if "pattern" in n.tags]
        if not pattern_nodes:
            # Create first pattern
            pattern_node = self._gram_core.add_node(
                content=f"Pattern root {self.growth_count}",
                language=self.language,
                tags=["pattern", "fractal"],
                resonance=0.5
            )
            pattern_nodes = [pattern_node]

        # Replicate pattern
        new_nodes_count = int(amount * 2) + 1
        for pattern in pattern_nodes[:3]:
            for i in range(min(new_nodes_count, 2)):
                content = f"Fractal growth {self.growth_count + i}"
                tags = ["fractal", "growth", f"pattern_{pattern.id[:8]}"]

                node = self._gram_core.add_node(
                    content=content,
                    language=self.language,
                    tags=tags,
                    resonance=pattern.resonance * (0.8 + random.random() * 0.2)
                )

                if node:
                    # Connect to pattern
                    self._gram_core._create_resonance_connection(node, pattern, 0.8)
                    events.append(GrowthEvent(
                        id=self._generate_event_id(),
                        type="node",
                        source=node.id,
                        target=pattern.id,
                        strength=0.8
                    ))

        return events

    # ============================================================
    # HELPERS
    # ============================================================

    def _find_clusters(self) -> List[List[Any]]:
        """Gjen clusters në GRAM"""
        if not self._gram_core:
            return []

        nodes = list(self._gram_core.nodes.values())
        if not nodes:
            return []

        visited = set()
        clusters = []

        for node in nodes:
            if node.id in visited:
                continue

            # BFS to find cluster
            cluster = []
            queue = [node.id]
            visited.add(node.id)

            while queue:
                current_id = queue.pop(0)
                current = self._gram_core.get_node(current_id)
                if not current:
                    continue

                cluster.append(current)

                for neighbor_id in current.get_all_connections():
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append(neighbor_id)

            if cluster:
                clusters.append(cluster)

        return clusters

    def _update_energy(self, amount: float) -> None:
        """Përditëson energjinë"""
        self.energy = min(1.0, self.energy + amount * 0.1)
        self.energy = max(0.0, self.energy - 0.01)  # Natural decay

    def _update_phase(self) -> None:
        """Përditëson fazën e rritjes"""
        if self.growth_count < 10:
            self.phase = GrowthPhase.SEED
        elif self.growth_count < 50:
            self.phase = GrowthPhase.GERMINATION
        elif self.growth_count < 100:
            self.phase = GrowthPhase.SHOOT
        elif self.growth_count < 500:
            self.phase = GrowthPhase.GROWING
        elif self.growth_count < 1000:
            self.phase = GrowthPhase.MATURE
        elif self.growth_count < 2000:
            self.phase = GrowthPhase.SPREADING
        else:
            self.phase = GrowthPhase.DECAYING

    def _update_stats(self) -> None:
        """Përditëson statistikat"""
        if not self._gram_core:
            return

        nodes = list(self._gram_core.nodes.values())
        self.stats.total_nodes = len(nodes)

        total_connections = sum(n.get_connection_count() for n in nodes)
        self.stats.total_connections = total_connections

        self.stats.avg_degree = total_connections / (len(nodes) or 1)
        self.stats.avg_resonance = sum(n.resonance for n in nodes) / (len(nodes) or 1)
        self.stats.growth_rate_current = self.config.growth_rate
        self.stats.spread_rate_current = self.config.spread_rate
        self.stats.decay_rate_current = self.config.decay_rate
        self.stats.phase = self.phase
        self.stats.growth_count = self.growth_count
        self.stats.energy_level = self.energy
        self.stats.coherence = self.coherence
        self.stats.timestamp = time.time()

    def _generate_event_id(self) -> str:
        """Gjeneron ID për event"""
        timestamp = int(time.time() * 1000)
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"grow_{timestamp}_{random_hash}"

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_stats(self) -> GrowthStats:
        """Merr statistikat e rritjes"""
        self._update_stats()
        return self.stats

    def get_events(self, limit: int = 100) -> List[GrowthEvent]:
        """Merr eventet e fundit"""
        return list(self.event_queue)[-limit:]

    # ============================================================
    # CONNECT TO GRAM CORE
    # ============================================================

    def connect_gram_core(self, gram_core) -> None:
        """Lidh me GRAM Core"""
        self._gram_core = gram_core
        self.logger.info("🌿 GRAM Grow connected to GRAM Core")

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(self) -> None:
        """Cleanup GRAM Grow"""
        self.events.clear()
        self.event_queue.clear()
        self.logger.info("🧹 GRAM Grow cleaned up")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_grow_engine(config: Optional[GrowthConfig] = None) -> GRAMGrow:
    """Krijon një engine rritjeje"""
    return GRAMGrow(config=config)


def get_growth_stats(grow_engine: GRAMGrow) -> Dict[str, Any]:
    """Merr statistikat e rritjes"""
    stats = grow_engine.get_stats()
    return {
        "total_nodes": stats.total_nodes,
        "total_connections": stats.total_connections,
        "avg_degree": stats.avg_degree,
        "avg_resonance": stats.avg_resonance,
        "growth_rate": stats.growth_rate_current,
        "phase": stats.phase.value,
        "energy_level": stats.energy_level,
        "coherence": stats.coherence,
        "growth_count": stats.growth_count
    }


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "GRAMGrow",
    "GrowthConfig",
    "GrowthStats",
    "GrowthEvent",
    "GrowthPhase",
    "GrowthPattern",
    "GrowthTrigger",
    "create_grow_engine",
    "get_growth_stats"
]
