# ============================================================================
# KNOWLEDGE INDEX - Centralized Link Index for Curiosity Ocean
# ============================================================================
# 200,000+ free-score links organized by domain, country, category
# ============================================================================

"""
KNOWLEDGE INDEX - The Brain of Curiosity Ocean

Structure:
- links_index.json   → Main index of all links
- search_links.py    → Search and retrieval engine
- index_builder.py   → Build index from data_sources
- link_scorer.py     → Score links for relevance

Link Format:
{
    "id": "unique-link-id",
    "title": "Human readable title",
    "description": "Brief description",
    "url": "https://example.com",
    "source": "source_module",
    "domain": "example.com",
    "country": "DE",
    "category": "government",
    "layer": 1,
    "tags": ["open-data", "api", "statistics"],
    "score": 0.85,
    "api_available": true,
    "last_verified": "2025-01-15T10:00:00Z"
}
"""

__version__ = "1.0.0"

from .search_links import LinkSearchEngine, LinkResult
from .index_builder import IndexBuilder
from .link_scorer import LinkScorer

__all__ = [
    "LinkSearchEngine",
    "LinkResult",
    "IndexBuilder",
    "LinkScorer",
]
