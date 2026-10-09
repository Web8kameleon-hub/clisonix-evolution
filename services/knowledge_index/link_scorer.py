# ============================================================================
# LINK SCORER - Score Links for Quality and Relevance
# ============================================================================
# Multi-factor scoring for knowledge links
# ============================================================================

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

logger = logging.getLogger(__name__)


# ============================================================================
# SCORING WEIGHTS
# ============================================================================

@dataclass
class ScoringWeights:
    """Weights for different scoring factors"""
    api_availability: float = 0.25      # API = high value
    description_quality: float = 0.15   # Good description
    license_clarity: float = 0.10       # Clear license
    category_importance: float = 0.15   # Official sources
    url_quality: float = 0.10           # HTTPS, good domain
    completeness: float = 0.15          # All fields filled
    freshness: float = 0.10             # Recently updated


# Category importance scores
CATEGORY_IMPORTANCE = {
    "GOVERNMENT": 1.0,
    "STATISTICS": 0.95,
    "RESEARCH": 0.90,
    "UNIVERSITY": 0.85,
    "HOSPITAL": 0.85,
    "BANK": 0.80,
    "TECHNOLOGY": 0.80,
    "NEWS": 0.70,
    "CULTURE": 0.70,
    "SPORT": 0.65,
    "ENTERTAINMENT": 0.60,
    "TOURISM": 0.65,
    "TRANSPORT": 0.75,
    "ENERGY": 0.80,
    "TELECOM": 0.75,
    "INDUSTRY": 0.75,
    "ENVIRONMENTAL": 0.80,
    "AGRICULTURE": 0.75,
    "HOBBY": 0.50,
    "PLAYFUL": 0.45,
}

# Trusted domains get bonus
TRUSTED_DOMAINS = [
    ".gov", ".edu", ".org", ".int",
    "europa.eu", "un.org", "worldbank.org",
    "imf.org", "who.int", "unesco.org",
    "oecd.org", "wto.org", "data.gov",
]


# ============================================================================
# LINK SCORER CLASS
# ============================================================================

class LinkScorer:
    """
    Scores links based on multiple quality factors
    
    Factors:
    - API availability (25%)
    - Description quality (15%)
    - License clarity (10%)
    - Category importance (15%)
    - URL quality (10%)
    - Completeness (15%)
    - Freshness (10%)
    """
    
    def __init__(self, weights: Optional[ScoringWeights] = None):
        self.weights = weights or ScoringWeights()
        self.category_importance = CATEGORY_IMPORTANCE
        self.trusted_domains = TRUSTED_DOMAINS
    
    def score(self, source: Any) -> float:
        """
        Calculate overall quality score for a source
        
        Args:
            source: Source object with name, url, description, etc.
        
        Returns:
            Score between 0.0 and 1.0
        """
        scores = []
        
        # API availability (highest weight)
        api_score = 1.0 if source.api_available else 0.0
        scores.append(api_score * self.weights.api_availability)
        
        # Description quality
        desc_score = self._score_description(source.description)
        scores.append(desc_score * self.weights.description_quality)
        
        # License clarity
        license_score = self._score_license(source.license)
        scores.append(license_score * self.weights.license_clarity)
        
        # Category importance
        cat = source.category.value if hasattr(source.category, 'value') else str(source.category)
        cat_score = self.category_importance.get(cat.upper(), 0.5)
        scores.append(cat_score * self.weights.category_importance)
        
        # URL quality
        url_score = self._score_url(source.url)
        scores.append(url_score * self.weights.url_quality)
        
        # Completeness
        completeness_score = self._score_completeness(source)
        scores.append(completeness_score * self.weights.completeness)
        
        # Freshness (assume current if no date)
        freshness_score = 1.0  # Default to fresh
        scores.append(freshness_score * self.weights.freshness)
        
        # Sum all weighted scores
        total = sum(scores)
        
        # Normalize to 0-1 range
        return min(max(total, 0.0), 1.0)
    
    def _score_description(self, description: str) -> float:
        """Score the quality of a description"""
        if not description:
            return 0.0
        
        score = 0.0
        length = len(description)
        
        # Length scoring
        if length > 200:
            score += 0.3
        elif length > 100:
            score += 0.2
        elif length > 50:
            score += 0.1
        
        # Has useful keywords
        useful_words = ["data", "api", "open", "public", "statistics", 
                       "information", "access", "download", "database"]
        desc_lower = description.lower()
        keyword_hits = sum(1 for w in useful_words if w in desc_lower)
        score += min(keyword_hits * 0.1, 0.4)
        
        # Proper sentences (has periods, capitals)
        if "." in description and any(c.isupper() for c in description):
            score += 0.2
        
        # Not just URL or generic
        if not description.startswith("http") and len(set(description.split())) > 5:
            score += 0.1
        
        return min(score, 1.0)
    
    def _score_license(self, license_text: str) -> float:
        """Score the clarity and openness of license"""
        if not license_text:
            return 0.3  # Unknown license
        
        license_lower = license_text.lower()
        
        # Open licenses score highest
        if any(term in license_lower for term in ["cc0", "public domain", "cc-by"]):
            return 1.0
        
        if any(term in license_lower for term in ["open", "free", "mit", "apache"]):
            return 0.9
        
        if any(term in license_lower for term in ["creative commons", "cc-"]):
            return 0.8
        
        if any(term in license_lower for term in ["attribution", "share"]):
            return 0.7
        
        if any(term in license_lower for term in ["terms", "conditions"]):
            return 0.5
        
        if any(term in license_lower for term in ["proprietary", "restricted", "commercial"]):
            return 0.2
        
        return 0.4  # Default for unclear licenses
    
    def _score_url(self, url: str) -> float:
        """Score URL quality and trustworthiness"""
        if not url:
            return 0.0
        
        score = 0.5  # Base score
        url_lower = url.lower()
        
        # HTTPS bonus
        if url_lower.startswith("https://"):
            score += 0.2
        elif url_lower.startswith("http://"):
            score += 0.1
        
        # Trusted domain bonus
        for domain in self.trusted_domains:
            if domain in url_lower:
                score += 0.3
                break
        
        # Penalize very long URLs (might be deep/specific pages)
        if len(url) > 200:
            score -= 0.1
        
        # Bonus for root/main pages
        if url.count("/") <= 3:
            score += 0.1
        
        return min(max(score, 0.0), 1.0)
    
    def _score_completeness(self, source: Any) -> float:
        """Score how complete the source information is"""
        fields_to_check = [
            ('name', 0.25),
            ('url', 0.25),
            ('description', 0.20),
            ('country', 0.15),
            ('license', 0.15),
        ]
        
        score = 0.0
        for field, weight in fields_to_check:
            value = getattr(source, field, None)
            if value and str(value).strip():
                score += weight
        
        return score
    
    def score_batch(self, sources: List[Any]) -> List[float]:
        """Score multiple sources"""
        return [self.score(source) for source in sources]
    
    def get_score_breakdown(self, source: Any) -> Dict[str, float]:
        """Get detailed score breakdown for debugging"""
        cat = source.category.value if hasattr(source.category, 'value') else str(source.category)
        
        return {
            "api_availability": (1.0 if source.api_available else 0.0) * self.weights.api_availability,
            "description_quality": self._score_description(source.description) * self.weights.description_quality,
            "license_clarity": self._score_license(source.license) * self.weights.license_clarity,
            "category_importance": self.category_importance.get(cat.upper(), 0.5) * self.weights.category_importance,
            "url_quality": self._score_url(source.url) * self.weights.url_quality,
            "completeness": self._score_completeness(source) * self.weights.completeness,
            "freshness": 1.0 * self.weights.freshness,
            "total": self.score(source)
        }
    
    def filter_by_score(self, sources: List[Any], min_score: float = 0.5) -> List[Any]:
        """Filter sources by minimum score"""
        return [s for s in sources if self.score(s) >= min_score]
    
    def rank_sources(self, sources: List[Any]) -> List[tuple]:
        """Rank sources by score, returning (source, score) tuples"""
        scored = [(s, self.score(s)) for s in sources]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored


# ============================================================================
# SINGLETON
# ============================================================================

_scorer_instance: Optional[LinkScorer] = None

def get_scorer() -> LinkScorer:
    """Get the global scorer instance"""
    global _scorer_instance
    if _scorer_instance is None:
        _scorer_instance = LinkScorer()
    return _scorer_instance
