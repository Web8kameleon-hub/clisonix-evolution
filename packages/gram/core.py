# clx/gram/core.py
# ============================================================
# GRAM - Growing Resonance Adaptive Mesh
# "Si bari që rritet pa fund"
# ============================================================
# Author: Ledjan Ahmati
# System: Clisonix AI - Universal Cognitive Mesh
#
# GRAM = Growing Resonance Adaptive Mesh
#      = Global Resonance Associative Memory
#
# Si bari:
#   *     *   *   *     *   *   *   *   *   *   *   *   *     *
#     *   *     *   *   *     *   *     *   *   *   *   *
#       *   *     *   *     *   *     *   *   *   *     *
#
# Nuk ka qendër. Rritet vetë. Lidhet vetë.
# ============================================================

from __future__ import annotations

import hashlib
import json
import logging
import math
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque

# ============================================================
# ENUMS & TYPES
# ============================================================

class ResonanceType(Enum):
    """Llojet e rezonancës në GRAM"""
    SEMANTIC = "semantic"
    SYNTACTIC = "syntactic"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    LINGUISTIC = "linguistic"
    EMOTIONAL = "emotional"
    CONCEPTUAL = "conceptual"
    WAVE = "wave"
    RESONANCE = "resonance"
    NEAR = "near"
    FAR = "far"

class WavePhase(Enum):
    """Fazat e valës në GRAM"""
    CREST = "crest"
    TROUGH = "trough"
    RISING = "rising"
    FALLING = "falling"
    RESONANT = "resonant"
    CHAOTIC = "chaotic"

class GRAMDirection(Enum):
    """Drejtimet në GRAM - 12 dimensione"""
    # HVOW dimensions (6)
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    PAST = "past"
    FUTURE = "future"

    # GRAM additional dimensions (6)
    NEAR = "near"
    FAR = "far"
    RESONANCE = "resonance"
    SEMANTIC = "semantic"
    LANGUAGE = "language"
    WAVE = "wave"

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class GRAMNode:
    """
    Një fije bari në fushën GRAM.
    Lidhet me të tjera në mënyrë natyrale.
    """
    id: str
    content: Any
    resonance: float = 0.5
    wave_signature: str = ""

    # Lidhjet - 12 drejtime
    left: Set[str] = field(default_factory=set)
    right: Set[str] = field(default_factory=set)
    up: Set[str] = field(default_factory=set)
    down: Set[str] = field(default_factory=set)
    past: Set[str] = field(default_factory=set)
    future: Set[str] = field(default_factory=set)
    near: Set[str] = field(default_factory=set)
    far: Set[str] = field(default_factory=set)
    resonance_links: Set[str] = field(default_factory=set)
    semantic_links: Set[str] = field(default_factory=set)
    language_links: Set[str] = field(default_factory=set)
    wave_links: Set[str] = field(default_factory=set)

    # Hierarkia - si rrënjët e barit
    parents: Set[str] = field(default_factory=set)
    children: Set[str] = field(default_factory=set)

    # Memoria - lidhje të kujtesës
    memory_links: Set[str] = field(default_factory=set)

    # Metadata
    language: str = "any"
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    frequency: float = 1.0
    amplitude: float = 0.5

    # Statistikat e rritjes
    growth_count: int = 0
    resonance_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "resonance": self.resonance,
            "wave_signature": self.wave_signature,
            "left": list(self.left),
            "right": list(self.right),
            "up": list(self.up),
            "down": list(self.down),
            "past": list(self.past),
            "future": list(self.future),
            "near": list(self.near),
            "far": list(self.far),
            "resonance_links": list(self.resonance_links),
            "semantic_links": list(self.semantic_links),
            "language_links": list(self.language_links),
            "wave_links": list(self.wave_links),
            "parents": list(self.parents),
            "children": list(self.children),
            "memory_links": list(self.memory_links),
            "language": self.language,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "frequency": self.frequency,
            "amplitude": self.amplitude,
            "growth_count": self.growth_count,
            "resonance_count": self.resonance_count
        }

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

    def add_connection(self, node_id: str, direction: GRAMDirection) -> None:
        """Shton një lidhje në një drejtim"""
        if direction == GRAMDirection.LEFT:
            self.left.add(node_id)
        elif direction == GRAMDirection.RIGHT:
            self.right.add(node_id)
        elif direction == GRAMDirection.UP:
            self.up.add(node_id)
        elif direction == GRAMDirection.DOWN:
            self.down.add(node_id)
        elif direction == GRAMDirection.PAST:
            self.past.add(node_id)
        elif direction == GRAMDirection.FUTURE:
            self.future.add(node_id)
        elif direction == GRAMDirection.NEAR:
            self.near.add(node_id)
        elif direction == GRAMDirection.FAR:
            self.far.add(node_id)
        elif direction == GRAMDirection.RESONANCE:
            self.resonance_links.add(node_id)
        elif direction == GRAMDirection.SEMANTIC:
            self.semantic_links.add(node_id)
        elif direction == GRAMDirection.LANGUAGE:
            self.language_links.add(node_id)
        elif direction == GRAMDirection.WAVE:
            self.wave_links.add(node_id)

@dataclass
class GRAMCluster:
    """Një grup nodes që rriten së bashku"""
    id: str
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

@dataclass
class GRAMField:
    """Një fushë me clusters që rriten së bashku"""
    id: str
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

@dataclass
class GRAMResonance:
    """Rezonancë midis dy nodes"""
    source_id: str
    target_id: str
    strength: float
    type: ResonanceType
    distance: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "strength": self.strength,
            "type": self.type.value,
            "distance": self.distance,
            "timestamp": self.timestamp
        }

@dataclass
class GRAMSearchResult:
    """Rezultat i kërkimit në GRAM"""
    node: GRAMNode
    score: float
    direction: GRAMDirection
    distance: float
    path: List[str]
    resonance_type: ResonanceType
    wave_phase: WavePhase

# ============================================================
# GRAM ENGINE - Main Class
# ============================================================

class GRAMEngine:
    """
    GRAM - Growing Resonance Adaptive Mesh

    Rritet si bari. Lidhet vetë. Nuk ka qendër.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.nodes: Dict[str, GRAMNode] = {}
        self.clusters: Dict[str, GRAMCluster] = {}
        self.fields: Dict[str, GRAMField] = {}
        self.resonances: List[GRAMResonance] = []

        self.config = {
            "auto_grow": True,
            "growth_threshold": 0.3,
            "resonance_threshold": 0.2,
            "max_nodes": 100000,
            "max_connections": 1000,
            "wave_decay": 0.95,
            "language_weight": 1.0,
            "semantic_weight": 1.0,
            "temporal_weight": 0.8,
            "spatial_weight": 0.6,
            **(config or {})
        }

        self._growth_counter = 0
        self._resonance_counter = 0
        self._wave_state = {
            "amplitude": 0.5,
            "frequency": 1.0,
            "phase": WavePhase.RESONANT,
            "timestamp": time.time()
        }

        logger = logging.getLogger("gram")
        logger.setLevel(logging.INFO)
        self.logger = logger

        print("🌿 GRAM Engine initialized")
        print("   Growing Resonance Adaptive Mesh")
        print(f"   Auto-grow: {self.config['auto_grow']}")
        print(f"   Growth threshold: {self.config['growth_threshold']}")
        print(f"   Max nodes: {self.config['max_nodes']}")
        print("   👤 Author: Ledjan Ahmati")
        print("   🏢 System: Clisonix AI")

    # ============================================================
    # NODE MANAGEMENT - Si bari që rritet
    # ============================================================

    def add_node(
        self,
        content: Any,
        language: str = "any",
        tags: Optional[List[str]] = None,
        resonance: float = 0.5,
        auto_connect: bool = True
    ) -> GRAMNode:
        """
        Shton një node të re.
        Si të mbjellësh një farë bari.
        """
        if len(self.nodes) >= self.config["max_nodes"]:
            self._prune_old_nodes()

        node_id = self._generate_id()

        node = GRAMNode(
            id=node_id,
            content=content,
            resonance=resonance,
            language=language,
            tags=tags or [],
            wave_signature=self._generate_wave_signature()
        )

        self.nodes[node_id] = node

        # Auto-connect si bari që rritet
        if auto_connect and self.config["auto_grow"]:
            self._auto_grow(node)

        self._growth_counter += 1
        self._update_wave_state()

        self.logger.info(f"🌱 Node grew: {node_id} ({str(content)[:30]}...)")
        return node

    def get_node(self, node_id: str) -> Optional[GRAMNode]:
        return self.nodes.get(node_id)

    def delete_node(self, node_id: str) -> bool:
        """Fshin një node dhe të gjitha lidhjet e saj"""
        if node_id not in self.nodes:
            return False

        node = self.nodes[node_id]

        # Fshi nga të gjitha lidhjet
        for other_node in self.nodes.values():
            if node_id in other_node.left:
                other_node.left.remove(node_id)
            if node_id in other_node.right:
                other_node.right.remove(node_id)
            if node_id in other_node.up:
                other_node.up.remove(node_id)
            if node_id in other_node.down:
                other_node.down.remove(node_id)
            if node_id in other_node.past:
                other_node.past.remove(node_id)
            if node_id in other_node.future:
                other_node.future.remove(node_id)
            if node_id in other_node.near:
                other_node.near.remove(node_id)
            if node_id in other_node.far:
                other_node.far.remove(node_id)
            if node_id in other_node.resonance_links:
                other_node.resonance_links.remove(node_id)
            if node_id in other_node.semantic_links:
                other_node.semantic_links.remove(node_id)
            if node_id in other_node.language_links:
                other_node.language_links.remove(node_id)
            if node_id in other_node.wave_links:
                other_node.wave_links.remove(node_id)
            if node_id in other_node.parents:
                other_node.parents.remove(node_id)
            if node_id in other_node.children:
                other_node.children.remove(node_id)
            if node_id in other_node.memory_links:
                other_node.memory_links.remove(node_id)

        del self.nodes[node_id]
        self.logger.info(f"🌿 Node removed: {node_id}")
        return True

    def update_node(
        self,
        node_id: str,
        content: Optional[Any] = None,
        resonance: Optional[float] = None,
        tags: Optional[List[str]] = None,
        language: Optional[str] = None
    ) -> Optional[GRAMNode]:
        """Përditëson një node"""
        node = self.nodes.get(node_id)
        if not node:
            return None

        if content is not None:
            node.content = content
        if resonance is not None:
            node.resonance = resonance
        if tags is not None:
            node.tags = tags
        if language is not None:
            node.language = language

        node.updated_at = time.time()
        node.wave_signature = self._generate_wave_signature()

        # Rritja automatike pas përditësimit
        if self.config["auto_grow"]:
            self._auto_grow(node)

        self.logger.info(f"🌱 Node updated: {node_id}")
        return node

    # ============================================================
    # AUTO-GROW - Si bari që rritet vetë
    # ============================================================

    def _auto_grow(self, node: GRAMNode) -> None:
        """
        Rritja automatike e barit.
        Kërkon nodes të ngjashme dhe krijon lidhje.
        """
        # Kërko nodes të ngjashme
        similar_nodes = self._find_similar_nodes(node, limit=20)

        for other_id, score in similar_nodes:
            if other_id == node.id:
                continue

            other = self.nodes.get(other_id)
            if not other:
                continue

            # Lidhje sipas rezonancës
            if score > self.config["resonance_threshold"]:
                self._create_resonance_connection(node, other, score)

                # Lidhje semantike
                if score > 0.6:
                    node.semantic_links.add(other_id)
                    other.semantic_links.add(node.id)

                # Lidhje gjuhësore
                if node.language == other.language and node.language != "any":
                    node.language_links.add(other_id)
                    other.language_links.add(node.id)

                # Lidhje kohore
                time_diff = abs(node.created_at - other.created_at)
                if time_diff < 3600 * 24:  # 24 orë
                    if node.created_at > other.created_at:
                        node.past.add(other_id)
                        other.future.add(node.id)
                    else:
                        node.future.add(other_id)
                        other.past.add(node.id)

                # Lidhje afër/far
                if score > 0.7:
                    node.near.add(other_id)
                    other.near.add(node.id)
                elif score > 0.3:
                    node.far.add(other_id)
                    other.far.add(node.id)

                # Lidhje vale
                if abs(node.frequency - other.frequency) < 0.2:
                    node.wave_links.add(other_id)
                    other.wave_links.add(node.id)

                # Lidhje prind/fëmijë
                if score > 0.8:
                    other.parents.add(node.id)
                    node.children.add(other_id)

                # Lidhje memorie
                if score > 0.5:
                    node.memory_links.add(other_id)
                    other.memory_links.add(node.id)

                # Përditëso rezonancën
                node.resonance = (node.resonance + score) / 2
                node.resonance_count += 1
                node.growth_count += 1

                # Krijo rezonancë
                self.resonances.append(GRAMResonance(
                    source_id=node.id,
                    target_id=other_id,
                    strength=score,
                    type=ResonanceType.SEMANTIC,
                    distance=1.0 / (score + 0.1)
                ))

    def _find_similar_nodes(self, node: GRAMNode, limit: int = 20) -> List[Tuple[str, float]]:
        """Gjen nodes të ngjashme"""
        scores: List[Tuple[str, float]] = []

        for other_id, other in self.nodes.items():
            if other_id == node.id:
                continue

            score = self._calculate_similarity(node, other)
            if score > self.config["resonance_threshold"]:
                scores.append((other_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]

    def _calculate_similarity(self, node1: GRAMNode, node2: GRAMNode) -> float:
        """Llogarit ngjashmërinë midis dy nodes"""
        score = 0.0
        weights = {
            "content": 0.3,
            "tags": 0.2,
            "language": 0.15,
            "resonance": 0.15,
            "wave": 0.1,
            "temporal": 0.1
        }

        # Content similarity
        if isinstance(node1.content, str) and isinstance(node2.content, str):
            content_score = self._text_similarity(node1.content, node2.content)
            score += content_score * weights["content"]

        # Tag similarity
        tag_score = self._tag_similarity(node1.tags, node2.tags)
        score += tag_score * weights["tags"]

        # Language similarity
        if node1.language == node2.language and node1.language != "any":
            score += 1.0 * weights["language"]

        # Resonance similarity
        resonance_score = 1 - abs(node1.resonance - node2.resonance)
        score += resonance_score * weights["resonance"]

        # Wave similarity
        wave_score = 1 - abs(node1.frequency - node2.frequency)
        score += wave_score * weights["wave"]

        # Temporal similarity
        time_diff = abs(node1.created_at - node2.created_at)
        temporal_score = 1 / (1 + time_diff / (3600 * 24 * 30))  # 30 days decay
        score += temporal_score * weights["temporal"]

        return min(1.0, max(0.0, score))

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Similaritet i tekstit"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _tag_similarity(self, tags1: List[str], tags2: List[str]) -> float:
        """Similaritet i tagjeve"""
        if not tags1 or not tags2:
            return 0.0

        set1 = set(tags1)
        set2 = set(tags2)

        intersection = set1 & set2
        union = set1 | set2

        return len(intersection) / len(union)

    def _create_resonance_connection(
        self,
        node1: GRAMNode,
        node2: GRAMNode,
        score: float
    ) -> None:
        """Krijon lidhje rezonance"""
        if score > 0.8:
            node1.resonance_links.add(node2.id)
            node2.resonance_links.add(node1.id)
            self._wave_state["amplitude"] = min(1.0, self._wave_state["amplitude"] + 0.01)
        elif score > 0.5:
            # Lidhje e dobët rezonance
            if len(node1.resonance_links) < self.config["max_connections"]:
                node1.resonance_links.add(node2.id)
                node2.resonance_links.add(node1.id)

    # ============================================================
    # SEARCH - Kërkim në 12 dimensione
    # ============================================================

    def search(
        self,
        query: str,
        max_depth: int = 3,
        min_score: float = 0.1,
        directions: Optional[List[GRAMDirection]] = None,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[GRAMSearchResult]:
        """
        Kërkim në GRAM - 12 dimensione

        Si bari që përhapet në të gjitha drejtimet.
        """
        if directions is None:
            directions = [
                GRAMDirection.LEFT, GRAMDirection.RIGHT,
                GRAMDirection.UP, GRAMDirection.DOWN,
                GRAMDirection.PAST, GRAMDirection.FUTURE,
                GRAMDirection.NEAR, GRAMDirection.FAR,
                GRAMDirection.RESONANCE, GRAMDirection.SEMANTIC,
                GRAMDirection.LANGUAGE, GRAMDirection.WAVE
            ]

        # Krijo node të përkohshëm për query
        query_node = GRAMNode(
            id=f"query_{int(time.time())}",
            content=query,
            language=language or "any",
            tags=tags or [],
            resonance=0.5
        )

        results: List[GRAMSearchResult] = []
        visited: Set[str] = set()

        def traverse(
            node_id: str,
            depth: int,
            direction: GRAMDirection,
            path: List[str]
        ) -> None:
            if depth > max_depth:
                return
            if node_id in visited:
                return

            node = self.nodes.get(node_id)
            if not node:
                return

            visited.add(node_id)

            # Llogarit score
            score = self._calculate_search_score(query_node, node, direction, depth)

            if score >= min_score:
                results.append(GRAMSearchResult(
                    node=node,
                    score=score,
                    direction=direction,
                    distance=depth,
                    path=path + [node_id],
                    resonance_type=self._determine_resonance_type(direction),
                    wave_phase=self._wave_state["phase"]
                ))

            # Vazhdo në të gjitha drejtimet
            next_nodes: List[Tuple[str, GRAMDirection]] = []

            if GRAMDirection.LEFT in directions:
                next_nodes.extend([(n, GRAMDirection.LEFT) for n in node.left])
            if GRAMDirection.RIGHT in directions:
                next_nodes.extend([(n, GRAMDirection.RIGHT) for n in node.right])
            if GRAMDirection.UP in directions:
                next_nodes.extend([(n, GRAMDirection.UP) for n in node.up])
            if GRAMDirection.DOWN in directions:
                next_nodes.extend([(n, GRAMDirection.DOWN) for n in node.down])
            if GRAMDirection.PAST in directions:
                next_nodes.extend([(n, GRAMDirection.PAST) for n in node.past])
            if GRAMDirection.FUTURE in directions:
                next_nodes.extend([(n, GRAMDirection.FUTURE) for n in node.future])
            if GRAMDirection.NEAR in directions:
                next_nodes.extend([(n, GRAMDirection.NEAR) for n in node.near])
            if GRAMDirection.FAR in directions:
                next_nodes.extend([(n, GRAMDirection.FAR) for n in node.far])
            if GRAMDirection.RESONANCE in directions:
                next_nodes.extend([(n, GRAMDirection.RESONANCE) for n in node.resonance_links])
            if GRAMDirection.SEMANTIC in directions:
                next_nodes.extend([(n, GRAMDirection.SEMANTIC) for n in node.semantic_links])
            if GRAMDirection.LANGUAGE in directions:
                next_nodes.extend([(n, GRAMDirection.LANGUAGE) for n in node.language_links])
            if GRAMDirection.WAVE in directions:
                next_nodes.extend([(n, GRAMDirection.WAVE) for n in node.wave_links])

            # Prioritize connections
            priority = {
                GRAMDirection.RESONANCE: 6,
                GRAMDirection.SEMANTIC: 5,
                GRAMDirection.UP: 4,
                GRAMDirection.FUTURE: 4,
                GRAMDirection.NEAR: 3,
                GRAMDirection.LANGUAGE: 3,
                GRAMDirection.RIGHT: 2,
                GRAMDirection.LEFT: 2,
                GRAMDirection.WAVE: 2,
                GRAMDirection.DOWN: 1,
                GRAMDirection.PAST: 1,
                GRAMDirection.FAR: 0
            }

            next_nodes.sort(key=lambda x: priority.get(x[1], 0), reverse=True)

            for next_id, next_dir in next_nodes[:20]:  # Limit per level
                traverse(next_id, depth + 1, next_dir, path + [node_id])

        # Fillimi i kërkimit
        start_nodes = self._find_seed_nodes(query_node, 10)
        for node_id in start_nodes:
            traverse(node_id, 1, GRAMDirection.NEAR, [node_id])

        results.sort(key=lambda x: x.score, reverse=True)

        self.logger.info(f"🌿 GRAM search: {len(results)} results found")
        return results[:100]

    def _calculate_search_score(
        self,
        query: GRAMNode,
        node: GRAMNode,
        direction: GRAMDirection,
        depth: int
    ) -> float:
        """Llogarit score për kërkim"""
        # Base score - depth penalty
        score = 1.0 / (depth + 1)

        # Content similarity
        if isinstance(query.content, str) and isinstance(node.content, str):
            content_score = self._text_similarity(query.content, node.content)
            score += content_score * 0.3

        # Tag similarity
        tag_score = self._tag_similarity(query.tags, node.tags)
        score += tag_score * 0.2

        # Language similarity
        if query.language == node.language and node.language != "any":
            score += 0.15

        # Resonance
        resonance_score = 1 - abs(query.resonance - node.resonance)
        score += resonance_score * 0.15

        # Direction weight
        direction_weights = {
            GRAMDirection.RESONANCE: 1.3,
            GRAMDirection.SEMANTIC: 1.2,
            GRAMDirection.UP: 1.1,
            GRAMDirection.FUTURE: 1.1,
            GRAMDirection.NEAR: 1.0,
            GRAMDirection.LANGUAGE: 1.0,
            GRAMDirection.RIGHT: 0.9,
            GRAMDirection.LEFT: 0.9,
            GRAMDirection.WAVE: 0.8,
            GRAMDirection.DOWN: 0.7,
            GRAMDirection.PAST: 0.6,
            GRAMDirection.FAR: 0.5
        }
        score *= direction_weights.get(direction, 1.0)

        # Growth bonus
        growth_bonus = 1 + (node.growth_count / 1000)
        score *= growth_bonus

        # Wave amplitude
        score *= (0.5 + 0.5 * self._wave_state["amplitude"])

        return min(1.0, max(0.0, score))

    def _find_seed_nodes(self, query: GRAMNode, limit: int = 10) -> List[str]:
        """Gjen nodes fillestare për kërkim"""
        scores: List[Tuple[str, float]] = []

        for node_id, node in self.nodes.items():
            score = self._calculate_similarity(query, node)
            scores.append((node_id, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [node_id for node_id, _ in scores[:limit]]

    def _determine_resonance_type(self, direction: GRAMDirection) -> ResonanceType:
        """Përcakton llojin e rezonancës"""
        mapping = {
            GRAMDirection.LEFT: ResonanceType.SPATIAL,
            GRAMDirection.RIGHT: ResonanceType.SPATIAL,
            GRAMDirection.UP: ResonanceType.CONCEPTUAL,
            GRAMDirection.DOWN: ResonanceType.CONCEPTUAL,
            GRAMDirection.PAST: ResonanceType.TEMPORAL,
            GRAMDirection.FUTURE: ResonanceType.TEMPORAL,
            GRAMDirection.NEAR: ResonanceType.NEAR,
            GRAMDirection.FAR: ResonanceType.FAR,
            GRAMDirection.RESONANCE: ResonanceType.RESONANCE,
            GRAMDirection.SEMANTIC: ResonanceType.SEMANTIC,
            GRAMDirection.LANGUAGE: ResonanceType.LINGUISTIC,
            GRAMDirection.WAVE: ResonanceType.WAVE
        }
        return mapping.get(direction, ResonanceType.SEMANTIC)

    # ============================================================
    # CLUSTER & FIELD MANAGEMENT
    # ============================================================

    def create_cluster(self, node_ids: Optional[List[str]] = None) -> GRAMCluster:
        """Krijon një cluster të ri"""
        cluster_id = f"cluster_{int(time.time())}_{self._growth_counter}"

        cluster = GRAMCluster(
            id=cluster_id,
            wave_signature=self._generate_wave_signature()
        )

        if node_ids:
            for node_id in node_ids:
                if node_id in self.nodes:
                    cluster.add_node(node_id)

        self.clusters[cluster_id] = cluster
        self.logger.info(f"🌿 Cluster created: {cluster_id} ({cluster.size()} nodes)")
        return cluster

    def create_field(self, cluster_ids: Optional[List[str]] = None) -> GRAMField:
        """Krijon një fushë të re"""
        field_id = f"field_{int(time.time())}_{self._growth_counter}"

        field = GRAMField(
            id=field_id,
            wave_signature=self._generate_wave_signature()
        )

        if cluster_ids:
            for cluster_id in cluster_ids:
                if cluster_id in self.clusters:
                    field.add_cluster(cluster_id)

        self.fields[field_id] = field
        self.logger.info(f"🌿 Field created: {field_id} ({field.size()} clusters)")
        return field

    # ============================================================
    # WAVE STATE
    # ============================================================

    def _update_wave_state(self) -> None:
        """Përditëson gjendjen e valës"""
        now = time.time()
        elapsed = (now - self._wave_state["timestamp"]) / 60.0

        self._wave_state["amplitude"] *= self.config["wave_decay"] ** elapsed
        self._wave_state["amplitude"] = max(0.1, min(1.0, self._wave_state["amplitude"]))

        # Frequency based on node count
        self._wave_state["frequency"] = 0.5 + (len(self.nodes) / self.config["max_nodes"]) * 0.5

        # Phase based on growth
        if self._growth_counter % 10 == 0:
            phases = [WavePhase.CREST, WavePhase.TROUGH, WavePhase.RISING,
                     WavePhase.FALLING, WavePhase.RESONANT, WavePhase.CHAOTIC]
            self._wave_state["phase"] = phases[self._growth_counter % len(phases)]

        self._wave_state["timestamp"] = now

    def _generate_wave_signature(self) -> str:
        """Gjeneron një signature vale"""
        return hashlib.md5(
            f"{time.time()}_{self._wave_state['amplitude']}_{self._wave_state['frequency']}".encode()
        ).hexdigest()[:8]

    # ============================================================
    # UTILITY
    # ============================================================

    def _generate_id(self) -> str:
        return f"gram_{int(time.time())}_{self._growth_counter}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:6]}"

    def _prune_old_nodes(self) -> None:
        """Fshin nodes më të vjetra"""
        nodes = sorted(
            self.nodes.items(),
            key=lambda x: x[1].created_at
        )

        to_remove = int(len(nodes) * 0.1)
        for node_id, _ in nodes[:to_remove]:
            self.delete_node(node_id)

        self.logger.info(f"🌿 Pruned {to_remove} old nodes")

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_stats(self) -> Dict[str, Any]:
        """Statistika të GRAM"""
        total_connections = sum(
            node.get_connection_count() for node in self.nodes.values()
        )

        avg_connections = total_connections / (len(self.nodes) or 1)
        avg_resonance = sum(n.resonance for n in self.nodes.values()) / (len(self.nodes) or 1)

        # Language distribution
        lang_dist: Dict[str, int] = defaultdict(int)
        for node in self.nodes.values():
            lang_dist[node.language] += 1

        return {
            "total_nodes": len(self.nodes),
            "total_clusters": len(self.clusters),
            "total_fields": len(self.fields),
            "total_resonances": len(self.resonances),
            "total_connections": total_connections,
            "avg_connections": avg_connections,
            "avg_resonance": avg_resonance,
            "growth_counter": self._growth_counter,
            "wave_state": self._wave_state,
            "language_distribution": dict(lang_dist),
            "max_nodes": self.config["max_nodes"]
        }

    # ============================================================
    # VISUALIZATION
    # ============================================================

    def visualize(self, node_id: str, depth: int = 2) -> str:
        """Vizualizon GRAM si bari"""
        node = self.nodes.get(node_id)
        if not node:
            return "❌ Node not found"

        output = []
        output.append("╔══════════════════════════════════════════════════════════════════╗")
        output.append("║                   🌿 GRAM VISUALIZATION                         ║")
        output.append("║                Growing Resonance Adaptive Mesh                  ║")
        output.append("╠══════════════════════════════════════════════════════════════════╣")
        output.append(f"║ Node: {node.id[:20]}".ljust(60) + "║")
        output.append(f"║ Content: {str(node.content)[:30]}".ljust(60) + "║")
        output.append(f"║ Resonance: {node.resonance:.2f}".ljust(60) + "║")
        output.append(f"║ Wave: {node.wave_signature}".ljust(60) + "║")
        output.append(f"║ Connections: {node.get_connection_count()}".ljust(60) + "║")
        output.append(f"║ Growth: {node.growth_count}".ljust(60) + "║")
        output.append("╠══════════════════════════════════════════════════════════════════╣")

        # Lidhjet
        output.append("\n  🌿 Connections (like grass spreading):")

        directions = [
            ("← LEFT", node.left),
            ("→ RIGHT", node.right),
            ("↑ UP", node.up),
            ("↓ DOWN", node.down),
            ("⏮ PAST", node.past),
            ("⏭ FUTURE", node.future),
            ("⊙ NEAR", node.near),
            ("⊙ FAR", node.far),
            ("◈ RESONANCE", node.resonance_links),
            ("◈ SEMANTIC", node.semantic_links),
            ("◈ LANGUAGE", node.language_links),
            ("◈ WAVE", node.wave_links)
        ]

        for label, links in directions:
            if links:
                count = len(links)
                sample = ", ".join(list(links)[:3])
                output.append(f"  {label}: {count} links {sample}")
            else:
                output.append(f"  {label}: —")

        output.append("╚══════════════════════════════════════════════════════════════════╝")

        return "\n".join(output)

# ============================================================
# CONVENIENCE FUNCTIONS
# ============================================================

_gram_instance: Optional[GRAMEngine] = None

def get_gram() -> GRAMEngine:
    """Merr ose krijon instancën globale të GRAM"""
    global _gram_instance
    if _gram_instance is None:
        _gram_instance = GRAMEngine()
    return _gram_instance

# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    import asyncio

    async def test_gram():
        print("\n" + "=" * 70)
        print("🌿 TESTING GRAM ENGINE")
        print("Growing Resonance Adaptive Mesh")
        print("=" * 70)

        gram = GRAMEngine()

        # Shto nodes
        print("\n📝 Adding nodes (growing grass)...")

        contents = [
            "Clisonix is a universal cognitive system",
            "HVOW memory works like human memory",
            "Tide filters noise from resonance",
            "NodeDB uses nanodecibel scoring",
            "Stigma tracks behavior and trust",
            "WWWMMM merges multiple contexts",
            "EAP analyzes gaps and proposes solutions",
            "Identity kernel manages personas",
            "GRAM grows like grass without center",
            "Resonance connects everything naturally",
            "AI is the nervous system of all hardware",
            "Memory is the foundation of consciousness",
            "Time flows both ways in HVOW",
            "Language shapes thought",
            "Emotion resonates through memory"
        ]

        tags_lists = [
            ["clisonix", "system"],
            ["hvow", "memory"],
            ["tide", "filter"],
            ["nodedb", "security"],
            ["stigma", "trust"],
            ["wwwmmm", "merge"],
            ["eap", "analysis"],
            ["identity", "persona"],
            ["gram", "mesh"],
            ["resonance", "connection"],
            ["ai", "hardware"],
            ["memory", "consciousness"],
            ["time", "hvow"],
            ["language", "thought"],
            ["emotion", "resonance"]
        ]

        languages = ["en", "en", "en", "en", "en", "en", "en", "en", "en", "en", "en", "en", "en", "en", "en"]

        for content, tags, lang in zip(contents, tags_lists, languages):
            gram.add_node(
                content=content,
                language=lang,
                tags=tags,
                auto_connect=True
            )

        print(f"✅ Added {len(contents)} nodes")

        # Search
        print("\n🔍 Searching...")
        results = gram.search(
            query="What is Clisonix?",
            max_depth=3,
            min_score=0.1
        )

        print(f"Found {len(results)} results")
        for i, result in enumerate(results[:5]):
            print(f"  {i+1}. [{result.direction.value}] {result.score:.2f} - {str(result.node.content)[:40]}...")

        # Get stats
        print("\n📊 Stats:")
        stats = gram.get_stats()
        for key, value in stats.items():
            if key != "wave_state":
                print(f"  {key}: {value}")

        # Visualize
        if results:
            print("\n🌿 Visualization:")
            print(gram.visualize(results[0].node.id, depth=2))

        print("\n✅ GRAM test complete!")

    asyncio.run(test_gram())
