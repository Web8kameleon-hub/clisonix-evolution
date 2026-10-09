"""
CONSISTENCY MATRIX - Same Question = Same Answer Pattern
=========================================================
Ensures consistent responses for similar queries.

Ultra-light: ~60 lines | Hash-based matching | No ML needed
"""

from typing import Dict, Optional, Tuple
import hashlib
import re


class ConsistencyMatrix:
    """
    Tracks query patterns to ensure consistent responses.
    """
    
    def __init__(self, cache_size: int = 1000):
        self._pattern_cache: Dict[str, str] = {}
        self._cache_size = cache_size
    
    def _normalize(self, text: str) -> str:
        """Normalize query for pattern matching."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text)      # Normalize spaces
        # Remove common variations
        text = re.sub(r'\b(please|can you|could you|would you)\b', '', text)
        return text.strip()
    
    def _hash(self, text: str) -> str:
        """Create pattern hash."""
        normalized = self._normalize(text)
        return hashlib.md5(normalized.encode()).hexdigest()[:12]
    
    def get_pattern(self, query: str) -> Tuple[str, Optional[str]]:
        """
        Get pattern hash and any cached response style.
        Returns: (pattern_hash, cached_style or None)
        """
        pattern = self._hash(query)
        cached = self._pattern_cache.get(pattern)
        return pattern, cached
    
    def record(self, query: str, response_style: str) -> None:
        """Record query-response pattern for consistency."""
        pattern = self._hash(query)
        
        # LRU-style cache management
        if len(self._pattern_cache) >= self._cache_size:
            # Remove oldest entry
            oldest = next(iter(self._pattern_cache))
            del self._pattern_cache[oldest]
        
        self._pattern_cache[pattern] = response_style
    
    def is_similar(self, query1: str, query2: str) -> bool:
        """Check if two queries are semantically similar."""
        return self._hash(query1) == self._hash(query2)
    
    def get_stats(self) -> Dict:
        """Get consistency stats."""
        return {
            "patterns_cached": len(self._pattern_cache),
            "cache_capacity": self._cache_size,
            "utilization": f"{len(self._pattern_cache) / self._cache_size * 100:.1f}%"
        }


# Singleton
_matrix = None

def get_consistency() -> ConsistencyMatrix:
    global _matrix
    if _matrix is None:
        _matrix = ConsistencyMatrix()
    return _matrix
