# -*- coding: utf-8 -*-
"""
GRAM SEARCH - Growing Resonance Adaptive Mesh Search Engine
"Kërkimi në fushën e barit - pa kufi"
================================================================================
Author: Ledjan Ahmati
System: Clisonix AI - Universal Cognitive Mesh
================================================================================

GRAM Search = Motorri i kërkimit
- Kërkon në të gjitha drejtimet
- Përdor rezonancën dhe valët
- Gjen lidhjet më të forta
- Kthen rezultatet më relevante
- Pa kufi
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

class SearchDirection(Enum):
    """Drejtimet e kërkimit"""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    PAST = "past"
    FUTURE = "future"
    NEAR = "near"
    FAR = "far"
    RESONANCE = "resonance"
    SEMANTIC = "semantic"
    LANGUAGE = "language"
    WAVE = "wave"
    ALL = "all"
    ANY = "any"

class SearchMode(Enum):
    """Modaliteti i kërkimit"""
    EXACT = "exact"         # I saktë
    FUZZY = "fuzzy"         # I përafërt
    SEMANTIC = "semantic"   # Semantik
    RESONANT = "resonant"   # Rezonant
    WAVE = "wave"           # Valë
    HYBRID = "hybrid"       # Hibrid
    DEEP = "deep"           # I thellë
    BROAD = "broad"         # I gjerë

class SearchRank(Enum):
    """Renditja e kërkimit"""
    RELEVANCE = "relevance"     # Rëndësi
    RESONANCE = "resonance"     # Rezonancë
    DISTANCE = "distance"       # Distancë
    CONFIDENCE = "confidence"   # Besim
    RECENCY = "recency"         # Kohë
    POPULARITY = "popularity"   # Popullaritet

# ============================================================
# DATA CLASSES
# ============================================================

@dataclass
class SearchQuery:
    """Pyetje kërkimi"""
    id: str
    query: str
    mode: SearchMode = SearchMode.HYBRID
    directions: List[SearchDirection] = field(default_factory=lambda: [SearchDirection.ALL])
    max_depth: int = 3
    min_score: float = 0.1
    max_results: int = 100
    language: Optional[str] = None
    tags: Optional[List[str]] = None
    time_range: Optional[Tuple[float, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class SearchResult:
    """Rezultat kërkimi"""
    id: str
    node_id: str
    content: Any
    score: float
    distance: float
    direction: SearchDirection
    depth: int
    path: List[str]
    resonance: float
    confidence: float
    match_type: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "node_id": self.node_id,
            "content": self.content,
            "score": self.score,
            "distance": self.distance,
            "direction": self.direction.value,
            "depth": self.depth,
            "path": self.path,
            "resonance": self.resonance,
            "confidence": self.confidence,
            "match_type": self.match_type,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }

@dataclass
class SearchStats:
    """Statistika kërkimi"""
    total_searches: int = 0
    total_results: int = 0
    avg_score: float = 0.0
    max_score: float = 0.0
    avg_depth: float = 0.0
    avg_time_ms: float = 0.0
    search_modes: Dict[str, int] = field(default_factory=dict)
    search_directions: Dict[str, int] = field(default_factory=dict)
    query_history: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

# ============================================================
# GRAM SEARCH - Main Class
# ============================================================

class GRAMSearchEngine:
    """
    GRAM Search - Motorri i kërkimit

    Kërkon në të gjitha drejtimet.
    Përdor rezonancën dhe valët.
    Gjen lidhjet më të forta.
    Kthen rezultatet më relevante.
    """

    def __init__(
        self,
        language: str = "en"
    ):
        self.language = language

        # Search state
        self.queries: Dict[str, SearchQuery] = {}
        self.results: Dict[str, List[SearchResult]] = {}
        self.cache: Dict[str, List[SearchResult]] = {}

        # Stats
        self.stats = SearchStats()

        # Configuration
        self.config = {
            "max_results": 100,
            "min_score": 0.1,
            "max_depth": 3,
            "cache_size": 1000,
            "cache_ttl": 3600,  # 1 hour
            "result_limit": 100,
            "enable_caching": True
        }

        # Direction weights
        self.direction_weights = {
            SearchDirection.RESONANCE: 1.3,
            SearchDirection.SEMANTIC: 1.2,
            SearchDirection.UP: 1.15,
            SearchDirection.FUTURE: 1.1,
            SearchDirection.NEAR: 1.0,
            SearchDirection.LANGUAGE: 1.0,
            SearchDirection.RIGHT: 0.9,
            SearchDirection.LEFT: 0.9,
            SearchDirection.WAVE: 0.8,
            SearchDirection.DOWN: 0.7,
            SearchDirection.PAST: 0.6,
            SearchDirection.FAR: 0.5,
            SearchDirection.ALL: 1.0,
            SearchDirection.ANY: 1.0
        }

        # Integration with GRAM core
        self._gram_core = None

        # Logger
        self.logger = logging.getLogger("gram_search")
        self.logger.setLevel(logging.INFO)

        print("🔍 GRAM SEARCH Engine initialized")
        print(f"   Max Results: {self.config['max_results']}")
        print(f"   Min Score: {self.config['min_score']}")
        print(f"   Max Depth: {self.config['max_depth']}")
        print(f"   Caching: {self.config['enable_caching']}")
        print("   👤 Author: Ledjan Ahmati")
        print("   🏢 System: Clisonix AI")

    # ============================================================
    # SEARCH METHODS
    # ============================================================

    def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.HYBRID,
        directions: List[SearchDirection] = None,
        max_depth: Optional[int] = None,
        min_score: Optional[float] = None,
        max_results: Optional[int] = None,
        language: Optional[str] = None,
        tags: Optional[List[str]] = None,
        time_range: Optional[Tuple[float, float]] = None,
        use_cache: bool = True
    ) -> List[SearchResult]:
        """
        Kërkon në GRAM.

        Args:
            query: Pyetja e kërkimit
            mode: Modaliteti i kërkimit
            directions: Drejtimet e kërkimit
            max_depth: Thellësia maksimale
            min_score: Rezultati minimal
            max_results: Numri maksimal i rezultateve
            language: Gjuha e kërkimit
            tags: Tagjet e kërkimit
            time_range: Gama kohore
            use_cache: Përdor cache

        Returns:
            List[SearchResult]: Rezultatet e kërkimit
        """
        if not self._gram_core:
            self.logger.warning("GRAM Core not connected")
            return []

        # Set defaults
        if directions is None:
            directions = [SearchDirection.ALL]

        if max_depth is None:
            max_depth = self.config["max_depth"]

        if min_score is None:
            min_score = self.config["min_score"]

        if max_results is None:
            max_results = self.config["max_results"]

        # Check cache
        cache_key = self._generate_cache_key(
            query, mode, directions, max_depth, min_score, language, tags
        )

        if use_cache and self.config["enable_caching"] and cache_key in self.cache:
            cached_results = self.cache[cache_key]
            if cached_results:
                self.logger.debug(f"🔍 Cache hit: {cache_key}")
                return cached_results[:max_results]

        start_time = time.time()

        # Create search query
        query_id = self._generate_id()
        search_query = SearchQuery(
            id=query_id,
            query=query,
            mode=mode,
            directions=directions,
            max_depth=max_depth,
            min_score=min_score,
            max_results=max_results,
            language=language,
            tags=tags,
            time_range=time_range,
            timestamp=start_time
        )

        self.queries[query_id] = search_query

        # Perform search based on mode
        if mode == SearchMode.EXACT:
            results = self._exact_search(search_query)
        elif mode == SearchMode.FUZZY:
            results = self._fuzzy_search(search_query)
        elif mode == SearchMode.SEMANTIC:
            results = self._semantic_search(search_query)
        elif mode == SearchMode.RESONANT:
            results = self._resonant_search(search_query)
        elif mode == SearchMode.WAVE:
            results = self._wave_search(search_query)
        elif mode == SearchMode.DEEP:
            results = self._deep_search(search_query)
        elif mode == SearchMode.BROAD:
            results = self._broad_search(search_query)
        else:
            # Hybrid - combine multiple modes
            results = self._hybrid_search(search_query)

        # Cache results
        if self.config["enable_caching"] and results:
            self.cache[cache_key] = results
            # Limit cache size
            if len(self.cache) > self.config["cache_size"]:
                # Remove oldest entries
                keys_to_remove = list(self.cache.keys())[:-self.config["cache_size"]]
                for key in keys_to_remove:
                    del self.cache[key]

        # Update stats
        elapsed_ms = (time.time() - start_time) * 1000
        self._update_stats(query, results, elapsed_ms)

        self.logger.info(f"🔍 Search completed: {len(results)} results in {elapsed_ms:.2f}ms")

        return results[:max_results]

    # ============================================================
    # SEARCH MODES
    # ============================================================

    def _exact_search(self, query: SearchQuery) -> List[SearchResult]:
        """Kërkim i saktë"""
        results = []
        query_lower = query.query.lower()

        for node in self._gram_core.nodes.values():
            if isinstance(node.content, str):
                content_lower = node.content.lower()
                if query_lower in content_lower:
                    # Calculate score based on match position
                    pos = content_lower.find(query_lower)
                    score = 1.0 - (pos / len(content_lower)) * 0.5
                    score *= 0.8  # Base score for exact matches

                    results.append(self._create_result(node, score, SearchDirection.ALL, 0))

        return sorted(results, key=lambda r: r.score, reverse=True)

    def _fuzzy_search(self, query: SearchQuery) -> List[SearchResult]:
        """Kërkim i përafërt"""
        results = []
        query_words = set(query.query.lower().split())

        for node in self._gram_core.nodes.values():
            if isinstance(node.content, str):
                content_words = set(node.content.lower().split())

                # Calculate Jaccard similarity
                intersection = query_words & content_words
                union = query_words | content_words

                if union:
                    score = len(intersection) / len(union)
                    if score > query.min_score:
                        results.append(self._create_result(node, score, SearchDirection.ALL, 0))

        return sorted(results, key=lambda r: r.score, reverse=True)

    def _semantic_search(self, query: SearchQuery) -> List[SearchResult]:
        """Kërkim semantik"""
        results = []

        # Use resonance engine for semantic similarity
        if hasattr(self._gram_core, 'resonance_engine'):
            resonance_engine = self._gram_core.resonance_engine

            # Create temporary query node
            temp_node = self._gram_core.add_node(
                content=query.query,
                language=self.language,
                tags=["_query"],
                auto_connect=False
            )

            # Calculate resonance with all nodes
            for node in self._gram_core.nodes.values():
                if node.id == temp_node.id:
                    continue

                strength, _ = resonance_engine.calculate_resonance(temp_node, node)
                if strength > query.min_score:
                    results.append(self._create_result(node, strength, SearchDirection.SEMANTIC, 0))

            # Clean up
            self._gram_core.delete_node(temp_node.id)

        return sorted(results, key=lambda r: r.score, reverse=True)

    def _resonant_search(self, query: SearchQuery) -> List[SearchResult]:
        """Kërkim rezonant"""
        results = []

        # Search through resonance connections
        visited = set()
        queue = deque([(None, 0)])  # (node_id, depth)

        while queue:
            current_id, depth = queue.popleft()

            if depth > query.max_depth:
                continue

            if current_id:
                node = self._gram_core.get_node(current_id)
                if not node:
                    continue

                # Calculate resonance score
                if isinstance(node.content, str):
                    score = self._text_similarity(query.query, node.content)

                    # Apply direction weights
                    for direction in query.directions:
                        weight = self.direction_weights.get(direction, 1.0)
                        weighted_score = score * weight * (1 - depth * 0.1)

                        if weighted_score > query.min_score:
                            result = self._create_result(node, weighted_score, direction, depth)
                            results.append(result)

                # Add neighbors
                for neighbor_id in node.get_all_connections():
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append((neighbor_id, depth + 1))
            else:
                # Start from all nodes
                for node in self._gram_core.nodes.values():
                    visited.add(node.id)
                    queue.append((node.id, 0))

        return sorted(results, key=lambda r: r.score, reverse=True)

    def _wave_search(self, query: SearchQuery) -> List[SearchResult]:
        """Kërkim me valë"""
        results = []

        # Use wave engine if available
        if hasattr(self._gram_core, 'wave_engine'):
            wave_engine = self._gram_core.wave_engine

            # Generate wave from query
            temp_node = self._gram_core.add_node(
                content=query.query,
                language=self.language,
                tags=["_wave_query"],
                auto_connect=False
            )

            # Propagate wave
            wave = wave_engine.generate_wave(
                temp_node.id,
                amplitude=0.5,
                frequency=1.0
            )

            if wave:
                # Collect nodes affected by wave
                for node_id in wave.propagated_to:
                    node = self._gram_core.get_node(node_id)
                    if node:
                        score = wave.amplitude * 0.7
                        results.append(self._create_result(node, score, SearchDirection.WAVE, 1))

            # Clean up
            self._gram_core.delete_node(temp_node.id)

        return sorted(results, key=lambda r: r.score, reverse=True)

    def _deep_search(self, query: SearchQuery) -> List[SearchResult]:
        """Kërkim i thellë"""
        results = []

        # First, do semantic search
        semantic_results = self._semantic_search(query)

        # Then, expand through connections
        for result in semantic_results[:10]:
            node = self._gram_core.get_node(result.node_id)
            if not node:
                continue

            # Get all connections
            for neighbor_id in node.get_all_connections():
                neighbor = self._gram_core.get_node(neighbor_id)
                if neighbor:
                    score = result.score * 0.7
                    results.append(self._create_result(neighbor, score, SearchDirection.RESONANCE, 1))

        # Combine and deduplicate
        seen_ids = set()
        combined_results = []

        for r in semantic_results + results:
            if r.node_id not in seen_ids:
                seen_ids.add(r.node_id)
                combined_results.append(r)

        return sorted(combined_results, key=lambda r: r.score, reverse=True)

    def _broad_search(self, query: SearchQuery) -> List[SearchResult]:
        """Kërkim i gjerë"""
        results = []

        # Search all nodes with basic scoring
        for node in self._gram_core.nodes.values():
            if isinstance(node.content, str):
                score = self._text_similarity(query.query, node.content) * 0.5
                if score > query.min_score:
                    results.append(self._create_result(node, score, SearchDirection.ALL, 0))

        return sorted(results, key=lambda r: r.score, reverse=True)

    def _hybrid_search(self, query: SearchQuery) -> List[SearchResult]:
        """Kërkim hibrid"""
        results = []

        # Combine multiple search methods
        search_methods = [
            self._fuzzy_search,
            self._semantic_search,
            self._resonant_search
        ]

        all_results = []
        for method in search_methods:
            method_results = method(query)
            all_results.extend(method_results)

        # Combine and deduplicate
        seen_ids = set()
        for r in all_results:
            if r.node_id not in seen_ids:
                seen_ids.add(r.node_id)

                # Boost score for results found by multiple methods
                boost = all_results.count(lambda x: x.node_id == r.node_id) * 0.1
                r.score = min(1.0, r.score + boost)

                results.append(r)

        return sorted(results, key=lambda r: r.score, reverse=True)

    # ============================================================
    # HELPERS
    # ============================================================

    def _create_result(
        self,
        node: Any,
        score: float,
        direction: SearchDirection,
        depth: int
    ) -> SearchResult:
        """Krijon një rezultat kërkimi"""
        return SearchResult(
            id=self._generate_id(),
            node_id=node.id,
            content=node.content,
            score=score,
            distance=depth * 0.5,
            direction=direction,
            depth=depth,
            path=[],
            resonance=node.resonance,
            confidence=score * 0.8,
            match_type=direction.value
        )

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Similaritet i tekstit"""
        if not text1 or not text2:
            return 0.0

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def _generate_cache_key(self, *args) -> str:
        """Gjeneron cache key"""
        key_str = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()[:16]

    def _generate_id(self) -> str:
        """Gjeneron ID unike"""
        timestamp = int(time.time() * 1000)
        random_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"search_{timestamp}_{random_hash}"

    def _update_stats(
        self,
        query: str,
        results: List[SearchResult],
        elapsed_ms: float
    ) -> None:
        """Përditëson statistikat"""
        self.stats.total_searches += 1
        self.stats.total_results += len(results)

        if results:
            avg_score = sum(r.score for r in results) / len(results)
            self.stats.avg_score = (self.stats.avg_score * (self.stats.total_searches - 1) + avg_score) / self.stats.total_searches

            max_score = max(r.score for r in results)
            self.stats.max_score = max(self.stats.max_score, max_score)

            avg_depth = sum(r.depth for r in results) / len(results)
            self.stats.avg_depth = (self.stats.avg_depth * (self.stats.total_searches - 1) + avg_depth) / self.stats.total_searches

        self.stats.avg_time_ms = (self.stats.avg_time_ms * (self.stats.total_searches - 1) + elapsed_ms) / self.stats.total_searches
        self.stats.query_history.append(query)

        if len(self.stats.query_history) > 1000:
            self.stats.query_history = self.stats.query_history[-1000:]

        self.stats.timestamp = time.time()

    # ============================================================
    # STATISTICS
    # ============================================================

    def get_stats(self) -> SearchStats:
        """Merr statistikat"""
        return self.stats

    def get_query(self, query_id: str) -> Optional[SearchQuery]:
        """Merr një pyetje kërkimi"""
        return self.queries.get(query_id)

    def get_results(self, query_id: str) -> Optional[List[SearchResult]]:
        """Merr rezultatet e një pyetjeje"""
        return self.results.get(query_id)

    def clear_cache(self) -> None:
        """Pastro cache"""
        self.cache.clear()
        self.logger.info("🔍 Cache cleared")

    # ============================================================
    # CONNECT TO GRAM CORE
    # ============================================================

    def connect_gram_core(self, gram_core) -> None:
        """Lidh me GRAM Core"""
        self._gram_core = gram_core
        self.logger.info("🔍 GRAM Search connected to GRAM Core")

    # ============================================================
    # CLEANUP
    # ============================================================

    def cleanup(self) -> None:
        """Cleanup GRAM Search"""
        self.queries.clear()
        self.results.clear()
        self.cache.clear()
        self.logger.info("🧹 GRAM Search cleaned up")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def create_search_engine(language: str = "en") -> GRAMSearchEngine:
    """Krijon një engine kërkimi"""
    return GRAMSearchEngine(language=language)


def get_search_stats(engine: GRAMSearchEngine) -> Dict[str, Any]:
    """Merr statistikat e kërkimit"""
    stats = engine.get_stats()
    return {
        "total_searches": stats.total_searches,
        "total_results": stats.total_results,
        "avg_score": stats.avg_score,
        "max_score": stats.max_score,
        "avg_depth": stats.avg_depth,
        "avg_time_ms": stats.avg_time_ms,
        "query_count": len(stats.query_history)
    }


# ============================================================
# EXPORT
# ============================================================

__all__ = [
    "GRAMSearchEngine",
    "SearchDirection",
    "SearchMode",
    "SearchRank",
    "SearchQuery",
    "SearchResult",
    "SearchStats",
    "create_search_engine",
    "get_search_stats"
]
