# -*- coding: utf-8 -*-
"""
GRAM WAVE - Growing Resonance Adaptive Mesh Wave Engine
"Valët që përhapen nëpër bar"
================================================================================
Author: Ledjan Ahmati
System: Clisonix AI - Universal Cognitive Mesh
================================================================================

GRAM Wave = Motorri i valëve
- Gjeneron valë rezonance
- Përhap valët nëpër rrjet
- Llogarit amplitudën dhe frekuencën
- Harmonizon valët
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

class WaveType(Enum):
    """Llojet e valëve"""
    ALPHA = "alpha"         # 8-13 Hz - Relaksim
    BETA = "beta"           # 14-30 Hz - Aktiv
    GAMMA = "gamma"         # 30-100 Hz - Fokus
    DELTA = "delta"         # 0.5-4 Hz - Gjumë
    THETA = "theta"         # 4-8 Hz - Kreativitet
    OMEGA = "omega"         # >100 Hz - Rezonancë
    RESONANCE = "resonance" # Valë rezonance
    HARMONIC = "harmonic"   # Valë harmonike

class WavePhase(Enum):
    """Fazat e valës"""
    CREST = "crest"         # Kurorë - kulm
    TROUGH = "trough"       # Lugë - fund
    RISING = "rising"       # Duke u ngjitur
    FALLING = "falling"     # Duke u zbritur
    PEAK = "peak"           # Kulm
    ZERO = "zero"           # Zero
    RESONANT = "resonant"   # Rezonant

class WaveState(Enum):
    """Gjendja e valës"""
    GENERATING = "generating"   # Duke u gjeneruar
    PROPAGATING = "propagating" # Duke u përhapur
    RESONANT = "resonant"       # Rezonant
    DECAYING = "decaying"       # Duke u kalbur
    HARMONIC = "harmonic"       # Harmonik
    CHAOTIC = "chaotic"         # Kaotik

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class Wave:
    """Valë"""
    id: str
    source_id: str
    type: WaveType
    phase: WavePhase
    state: WaveState
    amplitude: float
    frequency: float
    wavelength: float
    speed: float
    direction: str
    timestamp: float = field(default_factory=time.time)
    propagated_to: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_id": self.source_id,
            "type": self.type.value,
            "phase": self.phase.value,
            "state": self.state.value,
            "amplitude": self.amplitude,
            "frequency": self.frequency,
            "wavelength": self.wavelength,
            "speed": self.speed,
            "direction": self.direction,
            "timestamp": self.timestamp,
            "propagated_to": list(self.propagated_to),
            "metadata": self.metadata
        }

@dataclass
class WavePattern:
    """Model i valës"""
    id: str
    name: str
    type: WaveType
    pattern: str
    nodes: Set[str] = field(default_factory=set)
    strength: float = 0.5
    amplitude: float = 0.5
    frequency: float = 1.0
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
            "name": self.name,
            "type": self.type.value,
            "pattern": self.pattern,
            "nodes": list(self.nodes),
            "strength": self.strength,
            "amplitude": self.amplitude,
            "frequency": self.frequency,
            "created_at": self.created_at,
            "metadata": self.metadata,
            "size": self.size()
        }

@dataclass
class WaveStats:
    """Statistika të valëve"""
    total_waves: int = 0
    active_waves: int = 0
    avg_amplitude: float = 0.0
    avg_frequency: float = 0.0
    max_amplitude: float = 0.0
    wave_types: Dict[str, int] = field(default_factory=dict)
    wave_phases: Dict[str, int] = field(default_factory=dict)
    wave_states: Dict[str, int] = field(default_factory=dict)
    total_propagations: int = 0
    coherence: float = 0.0
    timestamp: float = field(default_factory=time.time)

# ============================================================
# GRAM WAVE - Main Class
# ============================================================

class GRAMWaveEngine:
    """
    GRAM Wave - Motorri i valëve

    Gjeneron valë rezonance.
    Përhap valët nëpër rrjet.
    Llogarit amplitudën dhe frekuencën.
    Harmonizon valët.
    """

    def __init__(
        self,
        language: str = "en"
    ):
        self.language = language

        # Waves
        self.waves: Dict[str, Wave] = {}
        self.wave_patterns: Dict[str, WavePattern] = {}
        self._wave_history: deque = deque(maxlen=1000)

        # State
        self.coherence = 0.5
        self.harmony = 0.5
        self.stats = WaveStats()

        # Configuration
        self.config = {
            "base_amplitude": 0.5,
            "base_frequency": 1.0,
            "wave_decay": 0.95,
            "propagation_speed": 0.5,
            "max_waves": 1000,
            "coherence_threshold": 0.5,
            "propagation_depth": 3
        }

        # Wave types mapping
        self.wave_type_frequencies = {
            WaveType.ALPHA: 10.0,
            WaveType.BETA: 22.0,
            WaveType.GAMMA: 65.0,
            WaveType.DELTA: 2.0,
            WaveType.THETA: 6.0,
            WaveType.OMEGA: 120.0,
            WaveType.RESONANCE: 50.0,
            WaveType.HARMONIC: 30.0
        }

        # Integration with GRAM core
        self._gram_core = None

        # Logger
        self.logger = logging.getLogger("gram_wave")
        self.logger.setLevel(logging.INFO)

        print("🌊 GRAM WAVE Engine initialized")
        print(f"   Base Amplitude: {self.config['base_amplitude']}")
        print(f"   Base Frequency: {self.config['base_frequency']}")
        print(f"   Propagation Speed: {self.config['propagation_speed']}")
        print(f"   Max Waves: {self.config['max_waves']}")
        print("   👤 Author: Ledjan Ahmati")
        print("   🏢 System: Clisonix AI")

    # ============================================================
    # WAVE GENERATION
    # ============================================================

    def generate_wave(
        self,
        source_id: str,
        wave_type: WaveType = WaveType.RESONANCE,
        amplitude: Optional[float] = None,
        frequency: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Wave]:
        """Gjeneron një valë të re"""
        if not self._gram_core:
            return None

        source = self._gram_core.get_node(source_id)
        if not source:
            return None

        # Determine amplitude
        if amplitude is None:
            amplitude = self.config["base_amplitude"] * source.amplitude

        # Determine frequency
        if frequency is None:
            frequency = self.wave_type_frequencies.get(wave_type, self.config["base_frequency"])
            frequency *= source.frequency

        # Create wave
        wave = Wave(
            id=self._generate_id(),
            source_id=source_id,
            type=wave_type,
            phase=WavePhase.CREST,
            state=WaveState.GENERATING,
            amplitude=amplitude,
            frequency=frequency,
            wavelength=1.0 / frequency,
            speed=self.config["propagation_speed"],
            direction="all",
            metadata=metadata or {}
        )

        # Store
        self.waves[wave.id] = wave

        # Propagate immediately
        self.propagate_wave(wave.id, depth=self.config["propagation_depth"])

        self.logger.debug(f"🌊 Wave generated: {wave.id} ({wave_type.value})")

        return wave

    def propagate_wave(
        self,
        wave_id: str,
        depth: int = 3
    ) -> List[str]:
        """Përhap një valë nëpër rrjet"""
        if wave_id not in self.waves:
            return []

        wave = self.waves[wave_id]
        wave.state = WaveState.PROPAGATING

        if not self._gram_core:
            return []

        source = self._gram_core.get_node(wave.source_id)
        if not source:
            return []

        propagated_to = []
        visited = {wave.source_id}
        queue = deque([(wave.source_id, 0)])

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
                decay = self.config["wave_decay"] ** current_depth
                strength = wave.amplitude * decay

                if strength > 0.1:
                    # Propagate to neighbor
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, current_depth + 1))
                    wave.propagated_to.add(neighbor_id)
                    propagated_to.append(neighbor_id)

                    # Update neighbor resonance
                    neighbor.resonate(strength)

                    # Create wave pattern
                    self._create_wave_pattern(wave, neighbor, strength)

        wave.state = WaveState.RESONANT
        wave.timestamp = time.time()

        # Update stats
        self._update_stats()

        self.logger.debug(f"🌊 Wave propagated to {len(propagated_to)} nodes")

        return propagated_to

    def _create_wave_pattern(
        self,
        wave: Wave,
        node: Any,
        strength: float
    ) -> None:
        """Krijon një model valë"""
        pattern_id = f"pattern_{wave.source_id}_{node.id[:6]}"

        if pattern_id in self.wave_patterns:
            pattern = self.wave_patterns[pattern_id]
            pattern.add_node(node.id)
            pattern.strength = (pattern.strength + strength) / 2
        else:
            pattern = WavePattern(
                id=pattern_id,
                name=f"Wave pattern {wave.source_id[:6]} → {node.id[:6]}",
                type=wave.type,
                pattern=f"{wave.type.value}_propagation",
                strength=strength,
                amplitude=wave.amplitude * strength,
                frequency=wave.frequency,
                metadata={"wave_id": wave.id}
            )
            pattern.add_node(node.id)
            self.wave_patterns[pattern_id] = pattern

    # ============================================================
    # WAVE INTERFERENCE
    # ============================================================

    def calculate_interference(
        self,
        wave1: Wave,
        wave2: Wave
    ) -> Tuple[float, WavePhase]:
        """Llogarit interferencën midis dy valëve"""
        # Phase difference
        phase_diff = 0.0

        if wave1.phase == wave2.phase:
            phase_diff = 0.0
        elif wave1.phase in [WavePhase.CREST, WavePhase.PEAK] and wave2.phase in [WavePhase.TROUGH, WavePhase.ZERO]:
            phase_diff = math.pi
        else:
            phase_diff = math.pi / 2

        # Amplitude combination
        amplitude = wave1.amplitude + wave2.amplitude * math.cos(phase_diff)
        amplitude = max(0.0, amplitude)

        # Determine resulting phase
        if amplitude > max(wave1.amplitude, wave2.amplitude):
            phase = WavePhase.CREST if amplitude > 0.5 else WavePhase.RESONANT
        else:
            phase = WavePhase.TROUGH if amplitude < 0.3 else WavePhase.FALLING

        return amplitude, phase

    def create_harmonic_wave(
        self,
        source_id: str,
        amplitude: float = 0.5,
        frequency: float = 1.0
    ) -> Optional[Wave]:
        """Krijon një valë harmonike"""
        return self.generate_wave(
            source_id=source_id,
            wave_type=WaveType.HARMONIC,
            amplitude=amplitude,
            frequency=frequency,
            metadata={"harmonic": True}
        )

    def create_wave_field(
        self,
        center_id: str,
        radius: int = 2,
        amplitude: float = 0.5
    ) -> List[Wave]:
        """Krijon një fushë valësh"""
        waves = []

        if not self._gram_core:
            return waves

        center = self._gram_core.get_node(center_id)
        if not center:
            return waves

        # Generate waves from center and neighbors
        waves.append(self.generate_wave(center_id, WaveType.RESONANCE, amplitude))

        for neighbor_id in center.get_all_connections():
            if len(waves) < 10:  # Limit
                wave = self.generate_wave(
                    neighbor_id,
                    WaveType.RESONANCE,
                    amplitude * 0.7
                )
                if wave:
                    waves.append(wave)

        return waves

    # ============================================================
    # WAVE MAINTENANCE
    # ============================================================

    def maintain_waves(self) -> None:
        """Mirëmban valët - heq ato të kalbura"""
        to_remove = []

        for wave_id, wave in self.waves.items():
            # Decay over time
            age = time.time() - wave.timestamp
            decay = age / 60.0  # 1 minute decay

            if decay > 0:
                wave.amplitude *= (1 - decay * 0.01)
                wave.amplitude = max(0.0, wave.amplitude)

            # Remove if too weak
            if wave.amplitude < 0.05:
                to_remove.append(wave_id)

            # Update phase
            if wave.amplitude > 0.7:
                wave.phase = WavePhase.PEAK
            elif wave.amplitude > 0.5:
                wave.phase = WavePhase.RISING
            elif wave.amplitude > 0.3:
                wave.phase = WavePhase.FALLING
            elif wave.amplitude > 0.1:
                wave.phase = WavePhase.TROUGH
            else:
                wave.phase = WavePhase.ZERO

        for wave_id in to_remove:
            del self.waves[wave_id]

        if to_remove:
            self.logger.debug(f"🌊 Removed {len(to_remove)} decayed waves")

        # Update coherence
        self.calculate_coherence()
        self._update_stats()

    def calculate_coherence(self) -> float:
        """Llogarit koherencën e valëve"""
        if not self.waves:
            self.coherence = 0.5
            return self.coherence

        # Coherence based on wave distribution
        amplitudes = [w.amplitude for w in self.waves.values()]
        frequencies = [w.frequency for w in self.waves.values()]

        avg_amplitude = sum(amplitudes) / len(amplitudes)
        avg_frequency = sum(frequencies) / len(frequencies)

        # Calculate variance
        amp_variance = sum((a - avg_amplitude) ** 2 for a in amplitudes) / len(amplitudes)
        freq_variance = sum((f - avg_frequency) ** 2 for f in frequencies) / len(frequencies)

        # Coherence = 1 - normalized variance
        amp_coherence = 1 - min(1.0, math.sqrt(amp_variance) / 0.3)
        freq_coherence = 1 - min(1.0, math.sqrt(freq_variance) / 0.5)

        self.coherence = (amp_coherence * 0.6 + freq_coherence * 0.4)
        self.coherence = max(0.0, min(1.0, self.coherence))

        return self.coherence

    def calculate_harmony(self) -> float:
        """Llogarit harmoninë e valëve"""
        if not self.waves:
            self.harmony = 0.5
            return self.harmony

        # Harmony based on wave type distribution
        type_counts: Dict[WaveType, int] = defaultdict(int)
        for wave in self.waves.values():
            type_counts[wave.type] += 1

        # Entropy-based harmony
        total = len(self.waves)
        entropy = 0.0
        for count in type_counts.values():
            p = count / total
            entropy -= p * math.log2(p) if p > 0 else 0

        # Max entropy for 8 types
        max_entropy = math.log2(8)
        harmony = 1 - (entropy / max_entropy)

        self.harmony = max(0.0, min(1.0, harmony))
        return self.harmony

    # ============================================================
    # STATISTICS
    # ============================================================

    def _update_stats(self) -> None:
        """Përditëson statistikat"""
        self.stats.total_waves = len(self.waves)
        self.stats.active_waves = sum(1 for w in self.waves.values() if w.state != WaveState.DECAYING)

        if self.waves:
            amplitudes = [w.amplitude for w in self.waves.values()]
            frequencies = [w.frequency for w in self.waves.values()]
            self.stats.avg_amplitude = sum(amplitudes) / len(amplitudes)
            self.stats.avg_frequency = sum(frequencies) / len(frequencies)
            self.stats.max_amplitude = max(amplitudes)

        # Type distribution
        self.stats.wave_types = defaultdict(int)
        for wave in self.waves.values():
            self.stats.wave_types[wave.type.value] += 1

        # Phase distribution
        self.stats.wave_phases = defaultdict(int)
        for wave in self.waves.values():
            self.stats.wave_phases[wave.phase.value] += 1

        # State distribution
        self.stats.wave_states = defaultdict(int)
        for wave in self.waves.values():
            self.stats.wave_states[wave.state.value] += 1

        # Total propagations
        self.stats.total_propagations = sum(len(w.propagated_to) for w in self.waves.values())

        self.stats.coherence = self.coherence
        self.stats.timestamp = time.time()

    def get_stats(self) -> WaveStats:
        """Merr statistikat"""
        self._update_stats()
        return self.stats

    def get_waves(self) -> List[Wave]:
        """Merr të gjitha valët"""
        return list(self.waves.values())

    def get_patterns(self) -> List[WavePattern]:
        """Merr të gjitha modelet"""
        return list(self.wave_patterns.values())

    # ============================================================
    # HELPERS
    # ============================================================

    def _generate_id(self) -> str:
        """Gjeneron ID unike"""
        timestamp = int(time.time() * 1000)
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"wave_{timestamp}_{random_hash}"

    def get_wave_frequency(self, wave_type: WaveType) -> float:
        """Merr frekuencën për një lloj vale"""
        return self.wave_type_frequencies.get(wave_type, self.config["base_frequency"])

    # ============================================================
    # CONNECT TO GRAM CORE
    # ============================================================

    def connect_gram_core(self, gram_core) -> None:
        """Lidh me GRAM Core"""
        self._gram_core = gram_core
        self.logger.info("🌊 GRAM Wave connected to GRAM Core")

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(self) -> None:
        """Cleanup GRAM Wave"""
        self.waves.clear()
        self.wave_patterns.clear()
        self._wave_history.clear()
        self.logger.info("🧹 GRAM Wave cleaned up")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_wave_engine(language: str = "en") -> GRAMWaveEngine:
    """Krijon një engine valësh"""
    return GRAMWaveEngine(language=language)


def get_wave_stats(engine: GRAMWaveEngine) -> Dict[str, Any]:
    """Merr statistikat e valëve"""
    stats = engine.get_stats()
    return {
        "total_waves": stats.total_waves,
        "active_waves": stats.active_waves,
        "avg_amplitude": stats.avg_amplitude,
        "avg_frequency": stats.avg_frequency,
        "max_amplitude": stats.max_amplitude,
        "coherence": stats.coherence,
        "total_propagations": stats.total_propagations,
        "wave_types": stats.wave_types,
        "wave_phases": stats.wave_phases,
        "wave_states": stats.wave_states
    }


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "GRAMWaveEngine",
    "Wave",
    "WavePattern",
    "WaveStats",
    "WaveType",
    "WavePhase",
    "WaveState",
    "create_wave_engine",
    "get_wave_stats"
]
