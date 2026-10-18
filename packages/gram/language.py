# -*- coding: utf-8 -*-
"""
GRAM LANGUAGE - Growing Resonance Adaptive Mesh Language Bridge
"Ura gjuhësore që lidh të gjithë barin"
================================================================================
Author: Ledjan Ahmati
System: Clisonix AI - Universal Cognitive Mesh
================================================================================

GRAM Language = Ura gjuhësore
- Lidh nyje në gjuhë të ndryshme
- Krijon lidhje gjuhësore
- Përkthim dhe adaptim
- Harmonizim gjuhësor
- Pa barrierë
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

class LanguageType(Enum):
    """Llojet e gjuhëve"""
    ENGLISH = "en"
    ALBANIAN = "sq"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    ARABIC = "ar"
    HINDI = "hi"
    MULTILINGUAL = "multi"
    ANY = "any"

class LanguageFamily(Enum):
    """Familjet e gjuhëve"""
    INDO_EUROPEAN = "indo_european"
    ROMANCE = "romance"
    GERMANIC = "germanic"
    SLAVIC = "slavic"
    URALIC = "uralic"
    TURKIC = "turkic"
    SEMITIC = "semitic"
    SINO_TIBETAN = "sino_tibetan"
    JAPONIC = "japonic"
    DRAVIDIAN = "dravidian"
    OTHER = "other"

class LanguageProficiency(Enum):
    """Niveli i gjuhës"""
    NATIVE = "native"       # Gjuhë amtare
    FLUENT = "fluent"       # Rrjedhshëm
    PROFESSIONAL = "professional"  # Profesional
    CONVERSATIONAL = "conversational"  # Bisedor
    BASIC = "basic"         # Bazë
    LEARNING = "learning"   # Duke mësuar

class LanguageState(Enum):
    """Gjendja e gjuhës"""
    ACTIVE = "active"       # Aktive
    LEARNING = "learning"   # Duke mësuar
    ADAPTING = "adapting"   # Duke u përshtatur
    BRIDGING = "bridging"   # Duke lidhur
    TRANSLATING = "translating" # Duke përkthyer

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class LanguageNode:
    """Nyje gjuhësore"""
    id: str
    language: LanguageType
    family: LanguageFamily
    proficiency: LanguageProficiency
    content: Any
    translations: Dict[LanguageType, Any] = field(default_factory=dict)
    confidence: float = 0.8
    weight: float = 1.0
    state: LanguageState = LanguageState.ACTIVE
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LanguageBridge:
    """Urë gjuhësore"""
    id: str
    source_language: LanguageType
    target_language: LanguageType
    source_node_id: str
    target_node_id: str
    strength: float = 0.5
    confidence: float = 0.5
    translations: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_language": self.source_language.value,
            "target_language": self.target_language.value,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "strength": self.strength,
            "confidence": self.confidence,
            "translations": self.translations,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }

@dataclass
class LanguageStats:
    """Statistika gjuhësore"""
    total_languages: int = 0
    total_nodes: int = 0
    total_bridges: int = 0
    language_distribution: Dict[str, int] = field(default_factory=dict)
    family_distribution: Dict[str, int] = field(default_factory=dict)
    avg_confidence: float = 0.0
    avg_strength: float = 0.0
    active_languages: Set[str] = field(default_factory=set)
    timestamp: float = field(default_factory=time.time)

# ============================================================
# GRAM LANGUAGE - Main Class
# ============================================================

class GRAMLanguageEngine:
    """
    GRAM Language - Ura gjuhësore

    Lidh nyje në gjuhë të ndryshme.
    Krijon lidhje gjuhësore.
    Përkthim dhe adaptim.
    Harmonizim gjuhësor.
    """

    def __init__(
        self,
        language: str = "en"
    ):
        self.default_language = LanguageType(language) if language in LanguageType._value2member_map_ else LanguageType.ENGLISH

        # Language nodes
        self.language_nodes: Dict[str, LanguageNode] = {}
        self.language_bridges: Dict[str, LanguageBridge] = {}

        # Language mappings
        self.language_families: Dict[LanguageType, LanguageFamily] = {
            LanguageType.ENGLISH: LanguageFamily.GERMANIC,
            LanguageType.ALBANIAN: LanguageFamily.INDO_EUROPEAN,
            LanguageType.SPANISH: LanguageFamily.ROMANCE,
            LanguageType.FRENCH: LanguageFamily.ROMANCE,
            LanguageType.GERMAN: LanguageFamily.GERMANIC,
            LanguageType.ITALIAN: LanguageFamily.ROMANCE,
            LanguageType.PORTUGUESE: LanguageFamily.ROMANCE,
            LanguageType.RUSSIAN: LanguageFamily.SLAVIC,
            LanguageType.CHINESE: LanguageFamily.SINO_TIBETAN,
            LanguageType.JAPANESE: LanguageFamily.JAPONIC,
            LanguageType.ARABIC: LanguageFamily.SEMITIC,
            LanguageType.HINDI: LanguageFamily.INDO_EUROPEAN,
            LanguageType.MULTILINGUAL: LanguageFamily.OTHER,
            LanguageType.ANY: LanguageFamily.OTHER
        }

        # Language similarities (cosine similarity between languages)
        self.language_similarities: Dict[Tuple[LanguageType, LanguageType], float] = {
            (LanguageType.ENGLISH, LanguageType.GERMAN): 0.6,
            (LanguageType.ENGLISH, LanguageType.FRENCH): 0.5,
            (LanguageType.ENGLISH, LanguageType.SPANISH): 0.4,
            (LanguageType.ENGLISH, LanguageType.ITALIAN): 0.4,
            (LanguageType.SPANISH, LanguageType.FRENCH): 0.8,
            (LanguageType.SPANISH, LanguageType.ITALIAN): 0.8,
            (LanguageType.FRENCH, LanguageType.ITALIAN): 0.8,
            (LanguageType.GERMAN, LanguageType.DUTCH): 0.7,
            (LanguageType.RUSSIAN, LanguageType.UKRAINIAN): 0.8,
            (LanguageType.CHINESE, LanguageType.JAPANESE): 0.3,
        }

        # State
        self.stats = LanguageStats()
        self.coherence = 0.5

        # Configuration
        self.config = {
            "confidence_threshold": 0.3,
            "bridge_threshold": 0.2,
            "max_bridges": 1000,
            "translation_cache": True,
            "cross_language_learning": True
        }

        # Integration with GRAM core
        self._gram_core = None

        # Logger
        self.logger = logging.getLogger("gram_language")
        self.logger.setLevel(logging.INFO)

        print("🌐 GRAM LANGUAGE Engine initialized")
        print(f"   Default Language: {self.default_language.value}")
        print(f"   Confidence Threshold: {self.config['confidence_threshold']}")
        print(f"   Bridge Threshold: {self.config['bridge_threshold']}")
        print(f"   Cross-Language Learning: {self.config['cross_language_learning']}")
        print("   👤 Author: Ledjan Ahmati")
        print("   🏢 System: Clisonix AI")

    # ============================================================
    # LANGUAGE NODE MANAGEMENT
    # ============================================================

    def create_language_node(
        self,
        content: Any,
        language: LanguageType,
        proficiency: LanguageProficiency = LanguageProficiency.PROFESSIONAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LanguageNode:
        """Krijon një nyje gjuhësore"""
        node_id = self._generate_id()

        node = LanguageNode(
            id=node_id,
            language=language,
            family=self.language_families.get(language, LanguageFamily.OTHER),
            proficiency=proficiency,
            content=content,
            confidence=0.8,
            metadata=metadata or {}
        )

        self.language_nodes[node_id] = node

        # Update stats
        self._update_stats()

        self.logger.debug(f"🌐 Language node created: {node_id} ({language.value})")

        return node

    def get_language_node(self, node_id: str) -> Optional[LanguageNode]:
        """Merr një nyje gjuhësore"""
        return self.language_nodes.get(node_id)

    def get_nodes_by_language(self, language: LanguageType) -> List[LanguageNode]:
        """Merr të gjitha nyjet në një gjuhë"""
        return [node for node in self.language_nodes.values() if node.language == language]

    # ============================================================
    # LANGUAGE BRIDGES
    # ============================================================

    def create_bridge(
        self,
        source_node_id: str,
        target_node_id: str,
        strength: Optional[float] = None
    ) -> Optional[LanguageBridge]:
        """Krijon një urë gjuhësore"""
        source = self.language_nodes.get(source_node_id)
        target = self.language_nodes.get(target_node_id)

        if not source or not target:
            return None

        if source.language == target.language:
            return None

        # Calculate bridge strength
        if strength is None:
            strength = self._calculate_bridge_strength(source, target)

        if strength < self.config["bridge_threshold"]:
            return None

        # Create bridge
        bridge_id = self._generate_id()
        bridge = LanguageBridge(
            id=bridge_id,
            source_language=source.language,
            target_language=target.language,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            strength=strength,
            confidence=source.confidence * target.confidence,
            translations={},
            metadata={
                "source_family": source.family.value,
                "target_family": target.family.value
            }
        )

        self.language_bridges[bridge_id] = bridge

        # Update stats
        self._update_stats()

        self.logger.debug(f"🌐 Language bridge created: {source_node_id} ↔ {target_node_id} ({strength:.2f})")

        return bridge

    def _calculate_bridge_strength(
        self,
        source: LanguageNode,
        target: LanguageNode
    ) -> float:
        """Llogarit forcën e urës gjuhësore"""
        strength = 0.0

        # 1. Language similarity
        lang_pair = (source.language, target.language)
        reverse_pair = (target.language, source.language)

        similarity = self.language_similarities.get(lang_pair)
        if similarity is None:
            similarity = self.language_similarities.get(reverse_pair, 0.3)

        strength += similarity * 0.3

        # 2. Confidence product
        confidence = source.confidence * target.confidence
        strength += confidence * 0.2

        # 3. Proficiency weight
        prof_weights = {
            LanguageProficiency.NATIVE: 1.0,
            LanguageProficiency.FLUENT: 0.9,
            LanguageProficiency.PROFESSIONAL: 0.7,
            LanguageProficiency.CONVERSATIONAL: 0.5,
            LanguageProficiency.BASIC: 0.3,
            LanguageProficiency.LEARNING: 0.2
        }

        source_weight = prof_weights.get(source.proficiency, 0.5)
        target_weight = prof_weights.get(target.proficiency, 0.5)
        prof_score = (source_weight + target_weight) / 2
        strength += prof_score * 0.2

        # 4. Language family proximity
        if source.family == target.family:
            strength += 0.2
        elif source.family in [LanguageFamily.ROMANCE, LanguageFamily.GERMANIC] and target.family in [LanguageFamily.ROMANCE, LanguageFamily.GERMANIC]:
            strength += 0.1

        # 5. Content similarity (if text)
        if isinstance(source.content, str) and isinstance(target.content, str):
            # Basic content similarity
            words1 = set(source.content.lower().split())
            words2 = set(target.content.lower().split())
            if words1 and words2:
                intersection = words1 & words2
                union = words1 | words2
                content_score = len(intersection) / len(union)
                strength += content_score * 0.1

        return min(1.0, max(0.0, strength))

    # ============================================================
    # TRANSLATION
    # ============================================================

    def translate_content(
        self,
        content: str,
        source_language: LanguageType,
        target_language: LanguageType
    ) -> Tuple[str, float]:
        """
        Përkthen përmbajtjen nga një gjuhë në tjetrën.

        Returns:
            Tuple[str, float]: (përkthimi, konfidenca)
        """
        if source_language == target_language:
            return content, 1.0

        # Check if we have a bridge
        bridges = self._find_bridges(source_language, target_language)

        if bridges:
            # Use the strongest bridge
            bridge = max(bridges, key=lambda b: b.strength)
            confidence = bridge.confidence

            # Simple translation (in production, use actual translation service)
            translated = self._simple_translate(content, source_language, target_language)

            return translated, confidence

        # No bridge found, use fallback
        return content, 0.3

    def _find_bridges(
        self,
        source_language: LanguageType,
        target_language: LanguageType
    ) -> List[LanguageBridge]:
        """Gjen ura gjuhësore midis dy gjuhëve"""
        bridges = []

        for bridge in self.language_bridges.values():
            if bridge.source_language == source_language and bridge.target_language == target_language:
                bridges.append(bridge)
            elif bridge.source_language == target_language and bridge.target_language == source_language:
                # Reverse bridge
                reversed_bridge = LanguageBridge(
                    id=bridge.id,
                    source_language=bridge.target_language,
                    target_language=bridge.source_language,
                    source_node_id=bridge.target_node_id,
                    target_node_id=bridge.source_node_id,
                    strength=bridge.strength * 0.9,  # Slightly weaker in reverse
                    confidence=bridge.confidence * 0.9,
                    translations={},
                    metadata=bridge.metadata
                )
                bridges.append(reversed_bridge)

        return bridges

    def _simple_translate(
        self,
        content: str,
        source_language: LanguageType,
        target_language: LanguageType
    ) -> str:
        """
        Përkthim i thjeshtë (fallback).
        Në production, përdor API të vërtetë përkthimi.
        """
        # This is a simple placeholder translation
        # In production, use Google Translate API, DeepL, etc.

        # Add language marker
        marker = f"[{source_language.value}→{target_language.value}] "

        return f"{marker}{content}"

    # ============================================================
    # LANGUAGE SIMILARITY
    # ============================================================

    def get_language_similarity(
        self,
        lang1: LanguageType,
        lang2: LanguageType
    ) -> float:
        """Merr ngjashmërinë midis dy gjuhëve"""
        if lang1 == lang2:
            return 1.0

        pair = (lang1, lang2)
        reverse = (lang2, lang1)

        if pair in self.language_similarities:
            return self.language_similarities[pair]
        elif reverse in self.language_similarities:
            return self.language_similarities[reverse]
        else:
            # Calculate based on language families
            family1 = self.language_families.get(lang1, LanguageFamily.OTHER)
            family2 = self.language_families.get(lang2, LanguageFamily.OTHER)

            if family1 == family2:
                return 0.5
            elif family1 in [LanguageFamily.ROMANCE, LanguageFamily.GERMANIC] and family2 in [LanguageFamily.ROMANCE, LanguageFamily.GERMANIC]:
                return 0.3
            else:
                return 0.1

    def get_language_family(self, language: LanguageType) -> LanguageFamily:
        """Merr familjen e një gjuhe"""
        return self.language_families.get(language, LanguageFamily.OTHER)

    # ============================================================
    # MULTILINGUAL NODE CREATION
    # ============================================================

    def create_multilingual_node(
        self,
        content: Dict[LanguageType, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[LanguageNode]:
        """Krijon nyje në shumë gjuhë"""
        nodes = []

        for language, lang_content in content.items():
            node = self.create_language_node(
                content=lang_content,
                language=language,
                metadata=metadata
            )
            nodes.append(node)

        # Create bridges between all language nodes
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                self.create_bridge(nodes[i].id, nodes[j].id)

        return nodes

    # ============================================================
    # STATISTICS
    # ============================================================

    def _update_stats(self) -> None:
        """Përditëson statistikat"""
        self.stats.total_languages = len(set(node.language for node in self.language_nodes.values()))
        self.stats.total_nodes = len(self.language_nodes)
        self.stats.total_bridges = len(self.language_bridges)

        # Language distribution
        self.stats.language_distribution = defaultdict(int)
        for node in self.language_nodes.values():
            self.stats.language_distribution[node.language.value] += 1

        # Family distribution
        self.stats.family_distribution = defaultdict(int)
        for node in self.language_nodes.values():
            self.stats.family_distribution[node.family.value] += 1

        # Average confidence
        if self.language_nodes:
            total_confidence = sum(node.confidence for node in self.language_nodes.values())
            self.stats.avg_confidence = total_confidence / len(self.language_nodes)

        # Average bridge strength
        if self.language_bridges:
            total_strength = sum(bridge.strength for bridge in self.language_bridges.values())
            self.stats.avg_strength = total_strength / len(self.language_bridges)

        # Active languages
        self.stats.active_languages = set(node.language.value for node in self.language_nodes.values())

        self.stats.timestamp = time.time()

    def get_stats(self) -> LanguageStats:
        """Merr statistikat"""
        self._update_stats()
        return self.stats

    def get_languages(self) -> List[LanguageType]:
        """Merr të gjitha gjuhët"""
        return list(set(node.language for node in self.language_nodes.values()))

    def get_bridges(self) -> List[LanguageBridge]:
        """Merr të gjitha urat"""
        return list(self.language_bridges.values())

    # ============================================================
    # HELPERS
    # ============================================================

    def _generate_id(self) -> str:
        """Gjeneron ID unike"""
        timestamp = int(time.time() * 1000)
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"lang_{timestamp}_{random_hash}"

    # ============================================================
    # CONNECT TO GRAM CORE
    # ============================================================

    def connect_gram_core(self, gram_core) -> None:
        """Lidh me GRAM Core"""
        self._gram_core = gram_core
        self.logger.info("🌐 GRAM Language connected to GRAM Core")

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(self) -> None:
        """Cleanup GRAM Language"""
        self.language_nodes.clear()
        self.language_bridges.clear()
        self.logger.info("🧹 GRAM Language cleaned up")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_language_engine(language: str = "en") -> GRAMLanguageEngine:
    """Krijon një engine gjuhësor"""
    return GRAMLanguageEngine(language=language)


def get_language_stats(engine: GRAMLanguageEngine) -> Dict[str, Any]:
    """Merr statistikat gjuhësore"""
    stats = engine.get_stats()
    return {
        "total_languages": stats.total_languages,
        "total_nodes": stats.total_nodes,
        "total_bridges": stats.total_bridges,
        "language_distribution": stats.language_distribution,
        "family_distribution": stats.family_distribution,
        "avg_confidence": stats.avg_confidence,
        "avg_strength": stats.avg_strength,
        "active_languages": list(stats.active_languages)
    }


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "GRAMLanguageEngine",
    "LanguageNode",
    "LanguageBridge",
    "LanguageStats",
    "LanguageType",
    "LanguageFamily",
    "LanguageProficiency",
    "LanguageState",
    "create_language_engine",
    "get_language_stats"
]
