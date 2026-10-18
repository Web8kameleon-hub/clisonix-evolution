# -*- coding: utf-8 -*-
"""
GRAM RESONANCE - Growing Resonance Adaptive Mesh Resonance Engine
"Rezonanca që lidh të gjithë barin"
================================================================================
Author: Ledjan Ahmati
System: Clisonix AI - Universal Cognitive Mesh
================================================================================

GRAM Resonance = Motorri i rezonancës
- Llogarit rezonancën midis nyjeve
- Krijon lidhje rezonante
- Përhap valët e rezonancës
- Harmonizon sistemin
- Pa qendër
================================================================================
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from collections import defaultdict, deque

# ============================================================
# ENUMS
# ============================================================

class ResonanceType(Enum):
    """Llojet e rezonancës"""
    SEMANTIC = "semantic"       # Semantike - kuptim
    SYNTACTIC = "syntactic"     # Sintaktike - strukturë
    TEMPORAL = "temporal"       # Kohore - kohë
    SPATIAL = "spatial"         # Hapësinore - hapësirë
    LINGUISTIC = "linguistic"   # Gjuhësore - gjuhë
    EMOTIONAL = "emotional"     # Emocionale - ndjenjë
    CONCEPTUAL = "conceptual"   # Konceptuale - ide
    WAVE = "wave"               # Vale - frekuencë
    RESONANCE = "resonance"     # Rezonancë - pastër
    NEAR = "near"               # Afër - distancë
    FAR = "far"                 # Larg - distancë
    HARMONIC = "harmonic"       # Harmonike - harmonizim
    SYMPHONIC = "symphonic"     # Simfonike - perfekte

class ResonanceStrength(Enum):
    """Forca e rezonancës"""
    NONE = "none"           # 0.0 - 0.1
    WEAK = "weak"           # 0.1 - 0.3
    MODERATE = "moderate"   # 0.3 - 0.5
    STRONG = "strong"       # 0.5 - 0.7
    RESONANT = "resonant"   # 0.7 - 0.85
    SYMPHONIC = "symphonic" # 0.85 - 1.0

class ResonancePattern(Enum):
    """Modeli i rezonancës"""
    INDIVIDUAL = "individual"   # Individuale
    PAIR = "pair"               # Çift
    CLUSTER = "cluster"         # Tufë
    NETWORK = "network"         # Rrjet
    FIELD = "field"             # Fushë
    GLOBAL = "global"           # Globale
    WAVE = "wave"               # Valë

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class GRAMResonance:
    """Rezonancë midis dy nyjeve"""
    id: str
    source_id: str
    target_id: str
    strength: float
    type: ResonanceType
    distance: float
    pattern: ResonancePattern = ResonancePattern.PAIR
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    decay: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "strength": self.strength,
            "type": self.type.value,
            "distance": self.distance,
            "pattern": self.pattern.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
            "active": self.active,
            "decay": self.decay
        }

@dataclass
class ResonanceField:
    """Fusha e rezonancës"""
    id: str
    nodes: Set[str] = field(default_factory=set)
    strength: float = 0.5
    type: ResonanceType = ResonanceType.SEMANTIC
    pattern: ResonancePattern = ResonancePattern.FIELD
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_node(self, node_id: str) -> None:
        self.nodes.add(node_id)
        self.updated_at = time.time()

    def remove_node(self, node_id: str) -> None:
        self.nodes.discard(node_id)
        self.updated_at = time.time()

    def size(self) -> int:
        return len(self.nodes)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nodes": list(self.nodes),
            "strength": self.strength,
            "type": self.type.value,
            "pattern": self.pattern.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "size": self.size()
        }

@dataclass
class ResonanceWave:
    """Valë rezonance"""
    id: str
    source_id: str
    strength: float
    frequency: float
    amplitude: float
    phase: str
    timestamp: float = field(default_factory=time.time)
    propagated_to: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResonanceStats:
    """Statistika të rezonancës"""
    total_resonances: int = 0
    active_resonances: int = 0
    avg_strength: float = 0.0
    max_strength: float = 0.0
    resonance_types: Dict[str, int] = field(default_factory=dict)
    resonance_patterns: Dict[str, int] = field(default_factory=dict)
    wave_count: int = 0
    coherence: float = 0.0
    timestamp: float = field(default_factory=time.time)

# ============================================================
# GRAM RESONANCE - Main Class
# ============================================================

class GRAMResonanceEngine:
    """
    GRAM Resonance - Motorri i rezonancës

    Llogarit rezonancën midis nyjeve.
    Krijon lidhje rezonante.
    Përhap valët e rezonancës.
    Harmonizon sistemin.
    """

    def __init__(
        self,
        language: str = "en"
    ):
        self.language = language

        # Resonances
        self.resonances: Dict[str, GRAMResonance] = {}
        self.resonance_fields: Dict[str, ResonanceField] = {}
        self.resonance_waves: List[ResonanceWave] = []

        # State
        self.coherence = 0.5
        self.harmony = 0.5
        self.stats = ResonanceStats()

        # Configuration
        self.config = {
            "resonance_threshold": 0.3,
            "wave_decay": 0.95,
            "max_resonances": 10000,
            "max_waves": 1000,
            "coherence_threshold": 0.5,
            "propagation_depth": 3
        }

        # Integration with GRAM core
        self._gram_core = None

        # Logger
        self.logger = logging.getLogger("gram_resonance")
        self.logger.setLevel(logging.INFO)

        print("🌊 GRAM RESONANCE Engine initialized")
        print(f"   Resonance Threshold: {self.config['resonance_threshold']}")
        print(f"   Max Resonances: {self.config['max_resonances']}")
        print(f"   Wave Decay: {self.config['wave_decay']}")
        print("   👤 Author: Ledjan Ahmati")
        print("   🏢 System: Clisonix AI")

    # ============================================================
    # RESONANCE CALCULATION
    # ============================================================

    def calculate_resonance(
        self,
        node1: Any,
        node2: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[float, ResonanceType]:
        """
        Llogarit rezonancën midis dy nyjeve.

        Returns:
            Tuple[float, ResonanceType]: (forca, lloji)
        """
        if not self._gram_core:
            return 0.0, ResonanceType.SEMANTIC

        score = 0.0
        resonance_type = ResonanceType.SEMANTIC

        # 1. Content similarity
        if isinstance(node1.content, str) and isinstance(node2.content, str):
            text_score = self._text_similarity(node1.content, node2.content)
            score += text_score * 0.3
            resonance_type = ResonanceType.SEMANTIC

        # 2. Tag similarity
        tag_score = self._tag_similarity(node1.tags, node2.tags)
        score += tag_score * 0.15

        # 3. Language similarity
        if node1.language == node2.language and node1.language != "any":
            score += 0.15
            resonance_type = ResonanceType.LINGUISTIC

        # 4. Temporal similarity
        time_diff = abs(node1.created_at - node2.created_at)
        temporal_score = 1 / (1 + time_diff / (3600 * 24 * 30))
        score += temporal_score * 0.1
        if temporal_score > 0.7:
            resonance_type = ResonanceType.TEMPORAL

        # 5. Wave similarity
        wave_score = 1 - abs(node1.frequency - node2.frequency)
        score += wave_score * 0.1
        if wave_score > 0.8:
            resonance_type = ResonanceType.WAVE

        # 6. Resonance history
        if node1.id in self.resonances and node2.id in self.resonances:
            history_score = 0.1
            score += history_score
            resonance_type = ResonanceType.RESONANCE

        # 7. Context (if provided)
        if context:
            context_score = self._context_similarity(context, node1, node2)
            score += context_score * 0.1
            if context_score > 0.6:
                resonance_type = ResonanceType.CONCEPTUAL

        # 8. Connection strength (if already connected)
        if node1.is_connected_to(node2.id):
            connection_strength = node1.get_connection_strength(node2.id)
            score += connection_strength * 0.1

        # Normalize
        score = min(1.0, max(0.0, score))

        return score, resonance_type

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

    def _context_similarity(
        self,
        context: Dict[str, Any],
        node1: Any,
        node2: Any
    ) -> float:
        """Similaritet i kontekstit"""
        score = 0.0
        count = 0

        # Check context keys
        for key, value in context.items():
            if hasattr(node1, key) and hasattr(node2, key):
                v1 = getattr(node1, key)
                v2 = getattr(node2, key)

                if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                    score += 1 - abs(v1 - v2) / max(abs(v1) + abs(v2), 1)
                elif v1 == v2:
                    score += 1.0
                else:
                    score += 0.5
                count += 1

        return score / count if count > 0 else 0.0

    # ============================================================
    # RESONANCE CREATION
    # ============================================================

    def create_resonance(
        self,
        source_id: str,
        target_id: str,
        strength: Optional[float] = None,
        resonance_type: Optional[ResonanceType] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[GRAMResonance]:
        """Krijon një rezonancë midis dy nyjeve"""
        if not self._gram_core:
            return None

        source = self._gram_core.get_node(source_id)
        target = self._gram_core.get_node(target_id)

        if not source or not target:
            return None

        # Calculate strength if not provided
        if strength is None:
            strength, _ = self.calculate_resonance(source, target)

        # Check threshold
        if strength < self.config["resonance_threshold"]:
            return None

        # Determine type if not provided
        if resonance_type is None:
            _, resonance_type = self.calculate_resonance(source, target)

        # Create resonance
        resonance = GRAMResonance(
            id=self._generate_id(),
            source_id=source_id,
            target_id=target_id,
            strength=strength,
            type=resonance_type,
            distance=1.0 / (strength + 0.1),
            metadata=metadata or {}
        )

        # Store
        self.resonances[resonance.id] = resonance

        # Update node resonance
        source.resonate(strength)
        target.resonate(strength)

        # Connect nodes
        if strength > 0.6:
            source.add_connection(target_id, "resonance")
            target.add_connection(source_id, "resonance")

        # Update stats
        self._update_stats()

        self.logger.debug(f"🌊 Resonance created: {source_id} ↔ {target_id} ({strength:.2f})")

        return resonance

    def create_field(
        self,
        node_ids: List[str],
        pattern: ResonancePattern = ResonancePattern.FIELD,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ResonanceField]:
        """Krijon një fushë rezonance"""
        if not self._gram_core:
            return None

        # Validate nodes
        valid_nodes = []
        for node_id in node_ids:
            if self._gram_core.get_node(node_id):
                valid_nodes.append(node_id)

        if len(valid_nodes) < 2:
            return None

        # Calculate field strength
        total_strength = 0.0
        type_counts: Dict[ResonanceType, int] = defaultdict(int)

        for i in range(len(valid_nodes)):
            for j in range(i + 1, len(valid_nodes)):
                node1 = self._gram_core.get_node(valid_nodes[i])
                node2 = self._gram_core.get_node(valid_nodes[j])

                if node1 and node2:
                    strength, r_type = self.calculate_resonance(node1, node2)
                    total_strength += strength
                    type_counts[r_type] += 1

        avg_strength = total_strength / (len(valid_nodes) * (len(valid_nodes) - 1) / 2)

        # Determine dominant type
        dominant_type = max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else ResonanceType.SEMANTIC

        # Create field
        field = ResonanceField(
            id=self._generate_id(),
            nodes=set(valid_nodes),
            strength=avg_strength,
            type=dominant_type,
            pattern=pattern,
            metadata=metadata or {}
        )

        self.resonance_fields[field.id] = field

        # Create resonances between all nodes in field
        for i in range(len(valid_nodes)):
            for j in range(i + 1, len(valid_nodes)):
                strength, _ = self.calculate_resonance(
                    self._gram_core.get_node(valid_nodes[i]),
                    self._gram_core.get_node(valid_nodes[j])
                )
                if strength > self.config["resonance_threshold"]:
                    self.create_resonance(valid_nodes[i], valid_nodes[j], strength)

        self.logger.info(f"🌊 Resonance field created: {field.id} ({len(valid_nodes)} nodes)")

        return field

    # ============================================================
    # RESONANCE WAVES
    # ============================================================

    def propagate_wave(
        self,
        source_id: str,
        strength: float = 0.5,
        depth: int = 3
    ) -> List[ResonanceWave]:
        """Përhap një valë rezonance"""
        waves = []

        if not self._gram_core:
            return waves

        source = self._gram_core.get_node(source_id)
        if not source:
            return waves

        # Create wave
        wave = ResonanceWave(
            id=self._generate_id(),
            source_id=source_id,
            strength=strength,
            frequency=source.frequency,
            amplitude=source.amplitude,
            phase=source.phase
        )

        # Propagate through connections
        visited = {source_id}
        queue = deque([(source_id, 0)])

        while queue:
            current_id, current_depth = queue.popleft()

            if current_depth >= depth:
                continue

            current = self._gram_core.get_node(current_id)
            if not current:
                continue

            # Get neighbors
            neighbors = current.get_all_connections()

            for neighbor_id in neighbors:
                if neighbor_id in visited:
                    continue

                neighbor = self._gram_core.get_node(neighbor_id)
                if not neighbor:
                    continue

                # Calculate wave strength at this distance
                decay_factor = self.config["wave_decay"] ** current_depth
                wave_strength = strength * decay_factor

                if wave_strength > self.config["resonance_threshold"]:
                    # Create resonance
                    resonance = self.create_resonance(
                        current_id,
                        neighbor_id,
                        wave_strength
                    )

                    if resonance:
                        visited.add(neighbor_id)
                        queue.append((neighbor_id, current_depth + 1))
                        wave.propagated_to.add(neighbor_id)

                        waves.append(wave)

        if waves:
            self.resonance_waves.append(wave)
            self.logger.debug(f"🌊 Wave propagated to {len(waves)} nodes")

        return waves

    # ============================================================
    # RESONANCE MAINTENANCE
    # ============================================================

    def maintain_resonance(self) -> None:
        """Mirëmban rezonancat - heq ato të dobëta"""
        to_remove = []

        for res_id, resonance in self.resonances.items():
            # Decay over time
            age = time.time() - resonance.timestamp
            decay = age / (3600 * 24 * 7)  # 7 days decay

            if decay > 0.5:
                resonance.strength *= (1 - decay * 0.1)

            # Remove if too weak
            if resonance.strength < 0.1:
                to_remove.append(res_id)

        for res_id in to_remove:
            del self.resonances[res_id]

        if to_remove:
            self.logger.debug(f"🌊 Removed {len(to_remove)} weak resonances")

        self._update_stats()

    def calculate_coherence(self) -> float:
        """Llogarit koherencën e sistemit"""
        if not self.resonances:
            return 0.5

        # Coherence based on resonance distribution
        strengths = [r.strength for r in self.resonances.values()]
        avg_strength = sum(strengths) / len(strengths)

        # Standard deviation
        variance = sum((s - avg_strength) ** 2 for s in strengths) / len(strengths)
        std_dev = math.sqrt(variance)

        # Coherence = 1 - normalized std_dev
        coherence = 1 - min(1.0, std_dev / 0.5)

        self.coherence = max(0.0, min(1.0, coherence))
        return self.coherence

    def calculate_harmony(self) -> float:
        """Llogarit harmoninë e sistemit"""
        if not self.resonances:
            return 0.5

        # Harmony based on resonance types distribution
        type_counts: Dict[ResonanceType, int] = defaultdict(int)
        for resonance in self.resonances.values():
            type_counts[resonance.type] += 1

        # Entropy-based harmony
        total = len(self.resonances)
        entropy = 0.0
        for count in type_counts.values():
            p = count / total
            entropy -= p * math.log2(p) if p > 0 else 0

        # Max entropy for 10 types
        max_entropy = math.log2(10)
        harmony = 1 - (entropy / max_entropy)

        self.harmony = max(0.0, min(1.0, harmony))
        return self.harmony

    # ============================================================
    # STATISTICS
    # ============================================================

    def _update_stats(self) -> None:
        """Përditëson statistikat"""
        self.stats.total_resonances = len(self.resonances)
        self.stats.active_resonances = sum(1 for r in self.resonances.values() if r.active)

        if self.resonances:
            strengths = [r.strength for r in self.resonances.values()]
            self.stats.avg_strength = sum(strengths) / len(strengths)
            self.stats.max_strength = max(strengths)

        # Type distribution
        self.stats.resonance_types = defaultdict(int)
        for resonance in self.resonances.values():
            self.stats.resonance_types[resonance.type.value] += 1

        # Pattern distribution
        self.stats.resonance_patterns = defaultdict(int)
        for resonance in self.resonances.values():
            self.stats.resonance_patterns[resonance.pattern.value] += 1

        self.stats.wave_count = len(self.resonance_waves)
        self.stats.coherence = self.calculate_coherence()
        self.stats.timestamp = time.time()

    def get_stats(self) -> ResonanceStats:
        """Merr statistikat"""
        self._update_stats()
        return self.stats

    def get_resonances(self) -> List[GRAMResonance]:
        """Merr të gjitha rezonancat"""
        return list(self.resonances.values())

    def get_fields(self) -> List[ResonanceField]:
        """Merr të gjitha fushat"""
        return list(self.resonance_fields.values())

    def get_waves(self) -> List[ResonanceWave]:
        """Merr të gjitha valët"""
        return self.resonance_waves

    # ============================================================
    # HELPERS
    # ============================================================

    def _generate_id(self) -> str:
        """Gjeneron ID unike"""
        timestamp = int(time.time() * 1000)
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"res_{timestamp}_{random_hash}"

    # ============================================================
    # CONNECT TO GRAM CORE
    # ============================================================

    def connect_gram_core(self, gram_core) -> None:
        """Lidh me GRAM Core"""
        self._gram_core = gram_core
        self.logger.info("🌊 GRAM Resonance connected to GRAM Core")

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(self) -> None:
        """Cleanup GRAM Resonance"""
        self.resonances.clear()
        self.resonance_fields.clear()
        self.resonance_waves.clear()
        self.logger.info("🧹 GRAM Resonance cleaned up")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_resonance_engine(language: str = "en") -> GRAMResonanceEngine:
    """Krijon një engine rezonance"""
    return GRAMResonanceEngine(language=language)


def get_resonance_stats(engine: GRAMResonanceEngine) -> Dict[str, Any]:
    """Merr statistikat e rezonancës"""
    stats = engine.get_stats()
    return {
        "total_resonances": stats.total_resonances,
        "active_resonances": stats.active_resonances,
        "avg_strength": stats.avg_strength,
        "max_strength": stats.max_strength,
        "coherence": stats.coherence,
        "wave_count": stats.wave_count,
        "resonance_types": stats.resonance_types,
        "resonance_patterns": stats.resonance_patterns
    }


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "GRAMResonanceEngine",
    "GRAMResonance",
    "ResonanceField",
    "ResonanceWave",
    "ResonanceStats",
    "ResonanceType",
    "ResonanceStrength",
    "ResonancePattern",
    "create_resonance_engine",
    "get_resonance_stats"
]
