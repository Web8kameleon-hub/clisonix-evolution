# ============================================================================
# KNOWLEDGE SEARCH - Search Engine for Curiosity Ocean
# ============================================================================
# Searches across 4053+ data sources with intelligent ranking
# ============================================================================

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SearchResult:
    """A single search result"""
    url: str
    name: str
    description: str
    category: str
    country: str
    score: float
    api_available: bool
    license: str
    highlights: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "country": self.country,
            "score": round(self.score, 3),
            "api_available": self.api_available,
            "license": self.license,
            "highlights": self.highlights,
            "metadata": self.metadata
        }


@dataclass
class SearchQuery:
    """Parsed search query"""
    raw: str
    keywords: List[str]
    countries: List[str]
    categories: List[str]
    require_api: bool = False
    exact_match: bool = False


# ============================================================================
# KNOWLEDGE SEARCH CLASS
# ============================================================================

class KnowledgeSearch:
    """
    Search engine for Curiosity Ocean
    
    Features:
    - Keyword search with ranking
    - Country and category filtering
    - API availability filtering
    - Intelligent scoring
    - Caching for performance
    """
    
    def __init__(self):
        self._sources_cache: List[Any] = []
        self._index: Dict[str, Set[int]] = {}  # keyword -> source indices
        self._country_index: Dict[str, Set[int]] = {}
        self._category_index: Dict[str, Set[int]] = {}
        self._loaded = False
    
    def _load_sources(self):
        """Load all sources and build indices"""
        if self._loaded:
            return
        
        try:
            from data_sources import GlobalDataSources
            gds = GlobalDataSources()
            self._sources_cache = gds.get_all_sources()
            
            # Build indices
            for i, source in enumerate(self._sources_cache):
                # Keyword index
                words = self._tokenize(f"{source.name} {source.description}")
                for word in words:
                    if word not in self._index:
                        self._index[word] = set()
                    self._index[word].add(i)
                
                # Country index
                country = source.country.lower() if source.country else "global"
                if country not in self._country_index:
                    self._country_index[country] = set()
                self._country_index[country].add(i)
                
                # Category index
                cat = source.category.value.lower() if hasattr(source.category, 'value') else str(source.category).lower()
                if cat not in self._category_index:
                    self._category_index[cat] = set()
                self._category_index[cat].add(i)
            
            self._loaded = True
            logger.info(f"Indexed {len(self._sources_cache)} sources")
            
        except ImportError as e:
            logger.warning(f"Could not load data sources: {e}")
            self._sources_cache = []
            self._loaded = True
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable keywords"""
        # Lowercase and extract words
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter short words and stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'of', 'to', 'in', 'for', 'on', 'with', 'and', 'or'}
        return [w for w in words if len(w) > 2 and w not in stop_words]
    
    def parse_query(self, query: str) -> SearchQuery:
        """Parse a search query into structured form"""
        raw = query.strip()
        
        # Check for special operators
        require_api = "api:" in raw.lower() or "hasapi:" in raw.lower()
        exact_match = raw.startswith('"') and raw.endswith('"')
        
        # Extract country filters (country:DE)
        countries = []
        country_matches = re.findall(r'country:(\w+)', raw, re.IGNORECASE)
        for c in country_matches:
            countries.append(c.lower())
        
        # Extract category filters (category:government)
        categories = []
        cat_matches = re.findall(r'category:(\w+)', raw, re.IGNORECASE)
        for c in cat_matches:
            categories.append(c.lower())
        
        # Remove operators from query
        clean_query = re.sub(r'(api:|hasapi:|country:\w+|category:\w+)', '', raw, flags=re.IGNORECASE)
        
        # Get keywords
        if exact_match:
            keywords = [clean_query.strip('"').lower()]
        else:
            keywords = self._tokenize(clean_query)
        
        return SearchQuery(
            raw=raw,
            keywords=keywords,
            countries=countries,
            categories=categories,
            require_api=require_api,
            exact_match=exact_match
        )
    
    def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        countries: List[str] = None,
        categories: List[str] = None,
        api_only: bool = False
    ) -> List[SearchResult]:
        """
        Search for sources matching the query
        
        Args:
            query: Search query string
            limit: Maximum results to return
            offset: Pagination offset
            countries: Filter by country codes
            categories: Filter by categories
            api_only: Only return sources with API
        
        Returns:
            List of SearchResult objects, ranked by relevance
        """
        self._load_sources()
        
        if not self._sources_cache:
            return []
        
        # Parse query
        parsed = self.parse_query(query)
        
        # Override with explicit parameters
        if countries:
            parsed.countries = [c.lower() for c in countries]
        if categories:
            parsed.categories = [c.lower() for c in categories]
        if api_only:
            parsed.require_api = True
        
        # Find candidate sources
        candidates = self._find_candidates(parsed)
        
        # Score and rank
        scored = []
        for idx in candidates:
            source = self._sources_cache[idx]
            score = self._score_source(source, parsed)
            if score > 0:
                scored.append((idx, score))
        
        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Apply pagination
        paginated = scored[offset:offset + limit]
        
        # Build results
        results = []
        for idx, score in paginated:
            source = self._sources_cache[idx]
            results.append(self._build_result(source, score, parsed))
        
        return results
    
    def _find_candidates(self, query: SearchQuery) -> Set[int]:
        """Find candidate source indices"""
        candidates = None
        
        # Start with keyword matches
        for keyword in query.keywords:
            keyword_candidates = set()
            for indexed_word, indices in self._index.items():
                if keyword in indexed_word or indexed_word in keyword:
                    keyword_candidates.update(indices)
            
            if candidates is None:
                candidates = keyword_candidates
            else:
                if query.exact_match:
                    candidates = candidates.intersection(keyword_candidates)
                else:
                    candidates = candidates.union(keyword_candidates)
        
        # If no keywords, start with all sources
        if candidates is None:
            candidates = set(range(len(self._sources_cache)))
        
        # Filter by country
        if query.countries:
            country_candidates = set()
            for country in query.countries:
                country_candidates.update(self._country_index.get(country, set()))
            candidates = candidates.intersection(country_candidates)
        
        # Filter by category
        if query.categories:
            cat_candidates = set()
            for cat in query.categories:
                cat_candidates.update(self._category_index.get(cat, set()))
            candidates = candidates.intersection(cat_candidates)
        
        # Filter by API
        if query.require_api:
            api_candidates = {
                i for i in candidates 
                if self._sources_cache[i].api_available
            }
            candidates = api_candidates
        
        return candidates
    
    def _score_source(self, source: Any, query: SearchQuery) -> float:
        """Score a source based on query relevance"""
        score = 0.0
        
        name_lower = source.name.lower()
        desc_lower = source.description.lower()
        
        # Keyword matching
        for keyword in query.keywords:
            # Exact name match - highest score
            if keyword in name_lower:
                score += 10.0 if keyword == name_lower else 5.0
            
            # Description match
            if keyword in desc_lower:
                score += 2.0
        
        # API availability bonus
        if source.api_available:
            score += 1.5
        
        # Length penalty for very long descriptions
        if len(source.description) > 500:
            score -= 0.5
        
        # Country match bonus
        if query.countries:
            country = source.country.lower() if source.country else ""
            if country in query.countries:
                score += 3.0
        
        # Category match bonus
        if query.categories:
            cat = source.category.value.lower() if hasattr(source.category, 'value') else str(source.category).lower()
            if cat in query.categories:
                score += 3.0
        
        return score
    
    def _build_result(self, source: Any, score: float, query: SearchQuery) -> SearchResult:
        """Build a SearchResult from a source"""
        # Generate highlights
        highlights = []
        desc_lower = source.description.lower()
        for keyword in query.keywords:
            if keyword in desc_lower:
                # Find context around keyword
                idx = desc_lower.find(keyword)
                start = max(0, idx - 30)
                end = min(len(source.description), idx + len(keyword) + 30)
                snippet = source.description[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(source.description):
                    snippet = snippet + "..."
                highlights.append(snippet)
        
        return SearchResult(
            url=source.url,
            name=source.name,
            description=source.description[:200],
            category=source.category.value if hasattr(source.category, 'value') else str(source.category),
            country=source.country or "Global",
            score=score,
            api_available=source.api_available,
            license=source.license,
            highlights=highlights[:3]
        )
    
    def autocomplete(self, prefix: str, limit: int = 10) -> List[str]:
        """Get autocomplete suggestions"""
        self._load_sources()
        
        prefix_lower = prefix.lower()
        suggestions = set()
        
        # From indexed keywords
        for word in self._index.keys():
            if word.startswith(prefix_lower):
                suggestions.add(word)
        
        # From source names
        for source in self._sources_cache[:1000]:  # Limit for performance
            if source.name.lower().startswith(prefix_lower):
                suggestions.add(source.name)
        
        return sorted(list(suggestions))[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        self._load_sources()
        
        return {
            "total_sources": len(self._sources_cache),
            "indexed_keywords": len(self._index),
            "indexed_countries": len(self._country_index),
            "indexed_categories": len(self._category_index),
            "countries": list(self._country_index.keys()),
            "categories": list(self._category_index.keys())
        }


# ============================================================================
# SINGLETON
# ============================================================================

_search_instance: Optional[KnowledgeSearch] = None

def get_search() -> KnowledgeSearch:
    """Get the global search instance"""
    global _search_instance
    if _search_instance is None:
        _search_instance = KnowledgeSearch()
    return _search_instance
