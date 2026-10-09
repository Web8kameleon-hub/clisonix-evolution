# ============================================================================
# SEARCH LINKS - Link Search Engine for Knowledge Index
# ============================================================================
# Fast search across 200,000+ links
# ============================================================================

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import json
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class LinkResult:
    """A link search result"""
    id: str
    title: str
    description: str
    url: str
    source: str
    domain: str
    country: str
    category: str
    layer: int
    tags: List[str]
    score: float
    api_available: bool
    relevance: float = 0.0  # Query relevance score
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "source": self.source,
            "domain": self.domain,
            "country": self.country,
            "category": self.category,
            "layer": self.layer,
            "tags": self.tags,
            "score": round(self.score, 3),
            "api_available": self.api_available,
            "relevance": round(self.relevance, 3)
        }


@dataclass
class IndexStats:
    """Statistics about the index"""
    total_links: int
    unique_domains: int
    countries_covered: int
    categories: int
    api_links: int
    average_score: float
    last_updated: datetime


# ============================================================================
# LINK SEARCH ENGINE
# ============================================================================

class LinkSearchEngine:
    """
    Fast search engine for the knowledge link index
    
    Features:
    - Full-text search
    - Country/category filtering
    - Score-based ranking
    - API availability filtering
    - Caching for performance
    """
    
    def __init__(self, index_path: Optional[str] = None):
        self.index_path = index_path or self._default_index_path()
        self._links: List[Dict[str, Any]] = []
        self._text_index: Dict[str, Set[int]] = {}  # word -> link indices
        self._country_index: Dict[str, Set[int]] = {}
        self._category_index: Dict[str, Set[int]] = {}
        self._domain_index: Dict[str, Set[int]] = {}
        self._loaded = False
    
    def _default_index_path(self) -> str:
        """Get default index path"""
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base, "app", "knowledge", "links_index.json")
    
    def load_index(self, force_rebuild: bool = False) -> bool:
        """
        Load the link index from file or rebuild from data_sources
        
        Args:
            force_rebuild: If True, rebuild from data_sources even if file exists
        
        Returns:
            True if loaded successfully
        """
        if self._loaded and not force_rebuild:
            return True
        
        # Try loading from file
        if os.path.exists(self.index_path) and not force_rebuild:
            try:
                with open(self.index_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._links = data.get("links", [])
                    self._build_indices()
                    self._loaded = True
                    logger.info(f"Loaded {len(self._links)} links from index")
                    return True
            except Exception as e:
                logger.warning(f"Could not load index: {e}")
        
        # Build from data_sources
        return self._rebuild_from_sources()
    
    def _rebuild_from_sources(self) -> bool:
        """Rebuild index from data_sources modules"""
        try:
            from data_sources import GlobalDataSources
            gds = GlobalDataSources()
            sources = gds.get_all_sources()
            
            self._links = []
            for i, source in enumerate(sources):
                # Extract domain from URL
                domain = self._extract_domain(source.url)
                
                # Generate tags
                tags = self._generate_tags(source)
                
                # Calculate initial score
                score = self._calculate_score(source)
                
                link = {
                    "id": f"link_{i:06d}",
                    "title": source.name,
                    "description": source.description,
                    "url": source.url,
                    "source": self._get_source_module(source),
                    "domain": domain,
                    "country": source.country or "Global",
                    "category": source.category.value if hasattr(source.category, 'value') else str(source.category),
                    "layer": self._determine_layer(source),
                    "tags": tags,
                    "score": score,
                    "api_available": source.api_available,
                    "last_verified": datetime.now().isoformat()
                }
                self._links.append(link)
            
            self._build_indices()
            self._save_index()
            self._loaded = True
            
            logger.info(f"Rebuilt index with {len(self._links)} links")
            return True
            
        except ImportError as e:
            logger.error(f"Could not import data_sources: {e}")
            return False
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc or url
        except:
            return url
    
    def _generate_tags(self, source: Any) -> List[str]:
        """Generate tags for a source"""
        tags = []
        
        # From category
        cat = source.category.value if hasattr(source.category, 'value') else str(source.category)
        tags.append(cat.lower())
        
        # From API availability
        if source.api_available:
            tags.append("api")
            tags.append("open-data")
        
        # From license
        if source.license and "open" in source.license.lower():
            tags.append("open-license")
        
        # From country
        if source.country:
            tags.append(source.country.lower())
        
        # From keywords in name/description
        keywords = ["data", "statistics", "portal", "open", "api", "government", "research"]
        text = f"{source.name} {source.description}".lower()
        for keyword in keywords:
            if keyword in text:
                tags.append(keyword)
        
        return list(set(tags))[:10]
    
    def _calculate_score(self, source: Any) -> float:
        """Calculate quality score for a source"""
        score = 0.5  # Base score
        
        # API availability is a major boost
        if source.api_available:
            score += 0.2
        
        # Has description
        if source.description and len(source.description) > 50:
            score += 0.1
        
        # Has license info
        if source.license:
            score += 0.05
        
        # Category bonus for official sources
        cat = source.category.value if hasattr(source.category, 'value') else str(source.category)
        if cat in ["GOVERNMENT", "STATISTICS", "RESEARCH"]:
            score += 0.1
        
        return min(score, 1.0)
    
    def _get_source_module(self, source: Any) -> str:
        """Determine which module the source came from"""
        country = source.country or ""
        country_lower = country.lower()
        
        # Map country to source module
        europe = ["de", "fr", "gb", "it", "es", "nl", "ch", "at", "pl", "be", "se", "no", "dk", "fi", "ie", "pt"]
        asia_china = ["cn", "jp", "kr", "tw", "hk", "mn", "sg"]
        india_south_asia = ["in", "pk", "bd", "lk", "np", "bt", "mv", "af"]
        americas = ["us", "ca", "br", "mx", "ar", "cl", "co", "pe"]
        
        if country_lower in europe:
            return "europe_sources"
        elif country_lower in asia_china:
            return "asia_china_sources"
        elif country_lower in india_south_asia:
            return "india_south_asia_sources"
        elif country_lower in americas:
            return "americas_sources"
        else:
            return "global_data_sources"
    
    def _determine_layer(self, source: Any) -> int:
        """Determine which layer the source belongs to (1-12)"""
        cat = source.category.value if hasattr(source.category, 'value') else str(source.category)
        
        layer_map = {
            "GOVERNMENT": 7,      # Domain APIs layer
            "STATISTICS": 6,      # Global Index layer
            "UNIVERSITY": 7,
            "RESEARCH": 8,        # AGI Core layer
            "TECHNOLOGY": 8,
            "BANK": 7,
            "HOSPITAL": 7,
            "NEWS": 10,           # Experience layer
            "ENTERTAINMENT": 10,
            "SPORT": 10,
            "TOURISM": 10,
            "CULTURE": 10,
        }
        
        return layer_map.get(cat.upper(), 6)
    
    def _build_indices(self):
        """Build search indices from links"""
        self._text_index.clear()
        self._country_index.clear()
        self._category_index.clear()
        self._domain_index.clear()
        
        for i, link in enumerate(self._links):
            # Text index
            words = self._tokenize(f"{link['title']} {link['description']} {' '.join(link.get('tags', []))}")
            for word in words:
                if word not in self._text_index:
                    self._text_index[word] = set()
                self._text_index[word].add(i)
            
            # Country index
            country = link.get('country', 'Global').lower()
            if country not in self._country_index:
                self._country_index[country] = set()
            self._country_index[country].add(i)
            
            # Category index
            category = link.get('category', 'General').lower()
            if category not in self._category_index:
                self._category_index[category] = set()
            self._category_index[category].add(i)
            
            # Domain index
            domain = link.get('domain', '').lower()
            if domain not in self._domain_index:
                self._domain_index[domain] = set()
            self._domain_index[domain].add(i)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into searchable words"""
        words = re.findall(r'\b\w+\b', text.lower())
        stop_words = {'the', 'a', 'an', 'is', 'are', 'of', 'to', 'in', 'for', 'on', 'with', 'and', 'or'}
        return [w for w in words if len(w) > 2 and w not in stop_words]
    
    def _save_index(self):
        """Save index to file"""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "version": "1.0.0",
                    "generated_at": datetime.now().isoformat(),
                    "total_links": len(self._links),
                    "links": self._links
                }, f, indent=2)
            logger.info(f"Saved index to {self.index_path}")
        except Exception as e:
            logger.error(f"Could not save index: {e}")
    
    def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
        countries: List[str] = None,
        categories: List[str] = None,
        api_only: bool = False,
        min_score: float = 0.0
    ) -> List[LinkResult]:
        """
        Search for links matching the query
        
        Args:
            query: Search query
            limit: Maximum results
            offset: Pagination offset
            countries: Filter by countries
            categories: Filter by categories
            api_only: Only return API-enabled links
            min_score: Minimum quality score
        
        Returns:
            List of LinkResult objects
        """
        self.load_index()
        
        if not self._links:
            return []
        
        # Find candidate indices
        candidates = self._find_candidates(query, countries, categories)
        
        # Score and filter
        scored = []
        for idx in candidates:
            link = self._links[idx]
            
            # Apply filters
            if api_only and not link.get('api_available', False):
                continue
            if link.get('score', 0) < min_score:
                continue
            
            # Calculate relevance
            relevance = self._calculate_relevance(link, query)
            scored.append((idx, relevance))
        
        # Sort by relevance
        scored.sort(key=lambda x: x[1], reverse=True)
        
        # Apply pagination
        paginated = scored[offset:offset + limit]
        
        # Build results
        results = []
        for idx, relevance in paginated:
            link = self._links[idx]
            results.append(LinkResult(
                id=link['id'],
                title=link['title'],
                description=link['description'][:200],
                url=link['url'],
                source=link['source'],
                domain=link['domain'],
                country=link['country'],
                category=link['category'],
                layer=link['layer'],
                tags=link.get('tags', []),
                score=link.get('score', 0.5),
                api_available=link.get('api_available', False),
                relevance=relevance
            ))
        
        return results
    
    def _find_candidates(
        self,
        query: str,
        countries: List[str] = None,
        categories: List[str] = None
    ) -> Set[int]:
        """Find candidate link indices"""
        # Start with all indices
        all_indices = set(range(len(self._links)))
        
        # Text search
        query_words = self._tokenize(query)
        if query_words:
            text_matches = set()
            for word in query_words:
                for indexed_word, indices in self._text_index.items():
                    if word in indexed_word or indexed_word in word:
                        text_matches.update(indices)
            if text_matches:
                all_indices = all_indices.intersection(text_matches)
        
        # Country filter
        if countries:
            country_matches = set()
            for country in countries:
                country_matches.update(self._country_index.get(country.lower(), set()))
            all_indices = all_indices.intersection(country_matches)
        
        # Category filter
        if categories:
            category_matches = set()
            for category in categories:
                category_matches.update(self._category_index.get(category.lower(), set()))
            all_indices = all_indices.intersection(category_matches)
        
        return all_indices
    
    def _calculate_relevance(self, link: Dict, query: str) -> float:
        """Calculate relevance of a link to the query"""
        relevance = 0.0
        query_lower = query.lower()
        query_words = self._tokenize(query)
        
        title_lower = link.get('title', '').lower()
        desc_lower = link.get('description', '').lower()
        
        # Title match (highest weight)
        for word in query_words:
            if word in title_lower:
                relevance += 5.0
        
        # Description match
        for word in query_words:
            if word in desc_lower:
                relevance += 2.0
        
        # Tag match
        for tag in link.get('tags', []):
            if tag.lower() in query_lower:
                relevance += 1.5
        
        # Boost by quality score
        relevance += link.get('score', 0.5) * 2
        
        # API availability boost
        if link.get('api_available'):
            relevance += 1.0
        
        return relevance
    
    def get_by_country(self, country: str, limit: int = 50) -> List[LinkResult]:
        """Get all links for a country"""
        return self.search("", limit=limit, countries=[country])
    
    def get_by_category(self, category: str, limit: int = 50) -> List[LinkResult]:
        """Get all links for a category"""
        return self.search("", limit=limit, categories=[category])
    
    def get_api_links(self, limit: int = 100) -> List[LinkResult]:
        """Get all API-enabled links"""
        return self.search("", limit=limit, api_only=True)
    
    def get_stats(self) -> IndexStats:
        """Get index statistics"""
        self.load_index()
        
        if not self._links:
            return IndexStats(
                total_links=0,
                unique_domains=0,
                countries_covered=0,
                categories=0,
                api_links=0,
                average_score=0.0,
                last_updated=datetime.now()
            )
        
        return IndexStats(
            total_links=len(self._links),
            unique_domains=len(self._domain_index),
            countries_covered=len(self._country_index),
            categories=len(self._category_index),
            api_links=sum(1 for l in self._links if l.get('api_available')),
            average_score=sum(l.get('score', 0.5) for l in self._links) / len(self._links),
            last_updated=datetime.now()
        )


# ============================================================================
# SINGLETON
# ============================================================================

_engine_instance: Optional[LinkSearchEngine] = None

def get_search_engine() -> LinkSearchEngine:
    """Get the global search engine instance"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = LinkSearchEngine()
    return _engine_instance
