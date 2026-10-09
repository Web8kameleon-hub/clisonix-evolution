# ============================================================================
# EXPLORER - Topic Exploration for Curiosity Ocean
# ============================================================================
# Explore topics with connections and related knowledge
# ============================================================================

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

logger = logging.getLogger(__name__)


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ExploreResult:
    """Result of topic exploration"""
    topic: str
    description: str
    related_sources: List[Dict[str, Any]]
    related_topics: List[str]
    connections: List[Dict[str, str]]
    depth: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "description": self.description,
            "related_sources": self.related_sources,
            "related_topics": self.related_topics,
            "connections": self.connections,
            "depth": self.depth,
            "metadata": self.metadata
        }


@dataclass
class TopicNode:
    """Node in the topic exploration graph"""
    topic: str
    category: str
    sources: List[str]
    connections: List[str]
    weight: float = 1.0


# ============================================================================
# TOPIC KNOWLEDGE BASE
# ============================================================================

# Pre-defined topic relationships for exploration
TOPIC_GRAPH = {
    # Technology topics
    "technology": {
        "related": ["software", "hardware", "innovation", "startups", "research"],
        "categories": ["TECHNOLOGY", "RESEARCH"],
        "description": "Technology and innovation across the globe"
    },
    "artificial_intelligence": {
        "related": ["machine_learning", "neural_networks", "robotics", "automation", "technology"],
        "categories": ["TECHNOLOGY", "RESEARCH"],
        "description": "AI and machine learning developments"
    },
    
    # Government topics
    "government": {
        "related": ["politics", "legislation", "public_policy", "elections", "democracy"],
        "categories": ["GOVERNMENT"],
        "description": "Government institutions and policies"
    },
    "politics": {
        "related": ["government", "elections", "democracy", "legislation", "international_relations"],
        "categories": ["GOVERNMENT", "NEWS"],
        "description": "Political systems and processes"
    },
    
    # Education topics
    "education": {
        "related": ["university", "research", "schools", "learning", "academic"],
        "categories": ["UNIVERSITY", "RESEARCH"],
        "description": "Educational institutions and learning"
    },
    "university": {
        "related": ["education", "research", "academic", "scholarships", "students"],
        "categories": ["UNIVERSITY"],
        "description": "Higher education and universities"
    },
    
    # Healthcare topics
    "healthcare": {
        "related": ["hospitals", "medicine", "public_health", "medical_research", "wellness"],
        "categories": ["HOSPITAL"],
        "description": "Healthcare systems and medical services"
    },
    "medicine": {
        "related": ["healthcare", "hospitals", "pharmaceuticals", "medical_research", "treatments"],
        "categories": ["HOSPITAL", "RESEARCH"],
        "description": "Medical sciences and treatments"
    },
    
    # Finance topics
    "finance": {
        "related": ["banking", "economics", "investment", "stock_markets", "cryptocurrency"],
        "categories": ["BANK", "STATISTICS"],
        "description": "Financial systems and markets"
    },
    "economics": {
        "related": ["finance", "statistics", "trade", "gdp", "development"],
        "categories": ["STATISTICS", "GOVERNMENT"],
        "description": "Economic data and analysis"
    },
    
    # Sports topics
    "sports": {
        "related": ["football", "olympics", "athletics", "competitions", "fitness"],
        "categories": ["SPORT"],
        "description": "Sports events and organizations"
    },
    "football": {
        "related": ["sports", "fifa", "leagues", "championships", "athletes"],
        "categories": ["SPORT"],
        "description": "Football/Soccer worldwide"
    },
    
    # Entertainment topics
    "entertainment": {
        "related": ["movies", "music", "gaming", "streaming", "celebrities"],
        "categories": ["ENTERTAINMENT"],
        "description": "Entertainment industry and media"
    },
    "music": {
        "related": ["entertainment", "concerts", "artists", "streaming", "culture"],
        "categories": ["ENTERTAINMENT", "CULTURE"],
        "description": "Music industry and artists"
    },
    
    # Tourism topics
    "tourism": {
        "related": ["travel", "destinations", "hotels", "attractions", "culture"],
        "categories": ["TOURISM"],
        "description": "Tourism and travel destinations"
    },
    "travel": {
        "related": ["tourism", "transport", "destinations", "hotels", "culture"],
        "categories": ["TOURISM", "TRANSPORT"],
        "description": "Travel and transportation"
    },
    
    # Environment topics
    "environment": {
        "related": ["climate", "sustainability", "conservation", "nature", "pollution"],
        "categories": ["ENVIRONMENTAL"],
        "description": "Environmental issues and conservation"
    },
    "climate": {
        "related": ["environment", "weather", "sustainability", "energy", "research"],
        "categories": ["ENVIRONMENTAL", "RESEARCH"],
        "description": "Climate science and change"
    },
    
    # Culture topics
    "culture": {
        "related": ["heritage", "arts", "museums", "traditions", "history"],
        "categories": ["CULTURE"],
        "description": "Cultural heritage and arts"
    },
    "history": {
        "related": ["culture", "heritage", "museums", "education", "archaeology"],
        "categories": ["CULTURE", "UNIVERSITY"],
        "description": "Historical records and research"
    }
}


# ============================================================================
# EXPLORER CLASS
# ============================================================================

class Explorer:
    """
    Topic exploration engine for Curiosity Ocean
    
    Features:
    - Topic graph navigation
    - Related source discovery
    - Connection mapping
    - Multi-level exploration
    """
    
    def __init__(self):
        self.topic_graph = TOPIC_GRAPH
        self._sources_cache = None
    
    def _load_sources(self):
        """Load data sources for exploration"""
        if self._sources_cache is not None:
            return
        
        try:
            from data_sources import GlobalDataSources
            gds = GlobalDataSources()
            self._sources_cache = gds.get_all_sources()
        except ImportError:
            self._sources_cache = []
    
    def explore(self, topic: str, depth: int = 2) -> ExploreResult:
        """
        Explore a topic with related knowledge
        
        Args:
            topic: Topic to explore
            depth: How deep to explore connections (1-5)
        
        Returns:
            ExploreResult with related sources and topics
        """
        self._load_sources()
        
        topic_lower = topic.lower().replace(" ", "_")
        
        # Get topic info if available
        topic_info = self.topic_graph.get(topic_lower, {
            "related": [],
            "categories": [],
            "description": f"Exploring: {topic}"
        })
        
        # Find related sources
        related_sources = self._find_related_sources(topic_lower, topic_info)
        
        # Get related topics
        related_topics = self._get_related_topics(topic_lower, depth)
        
        # Build connections
        connections = self._build_connections(topic_lower, related_topics)
        
        return ExploreResult(
            topic=topic,
            description=topic_info.get("description", f"Knowledge about {topic}"),
            related_sources=related_sources[:10],
            related_topics=related_topics[:10],
            connections=connections[:15],
            depth=depth,
            metadata={
                "categories": topic_info.get("categories", []),
                "sources_found": len(related_sources),
                "topics_found": len(related_topics)
            }
        )
    
    def _find_related_sources(self, topic: str, topic_info: Dict) -> List[Dict[str, Any]]:
        """Find sources related to a topic"""
        if not self._sources_cache:
            return []
        
        related = []
        categories = topic_info.get("categories", [])
        topic_words = topic.replace("_", " ").split()
        
        for source in self._sources_cache:
            score = 0
            
            # Check if source matches categories
            cat = source.category.value if hasattr(source.category, 'value') else str(source.category)
            if cat.upper() in categories:
                score += 5
            
            # Check for topic keywords in name/description
            source_text = f"{source.name} {source.description}".lower()
            for word in topic_words:
                if word in source_text:
                    score += 2
            
            if score > 0:
                related.append({
                    "name": source.name,
                    "url": source.url,
                    "category": cat,
                    "country": source.country,
                    "score": score,
                    "api_available": source.api_available
                })
        
        # Sort by score
        related.sort(key=lambda x: x["score"], reverse=True)
        return related
    
    def _get_related_topics(self, topic: str, depth: int) -> List[str]:
        """Get related topics up to specified depth"""
        related = set()
        current_level = {topic}
        
        for level in range(depth):
            next_level = set()
            for t in current_level:
                topic_info = self.topic_graph.get(t, {})
                for related_topic in topic_info.get("related", []):
                    if related_topic not in related:
                        next_level.add(related_topic)
            related.update(next_level)
            current_level = next_level
        
        # Remove the original topic
        related.discard(topic)
        
        return list(related)
    
    def _build_connections(self, topic: str, related_topics: List[str]) -> List[Dict[str, str]]:
        """Build connection links between topics"""
        connections = []
        
        # Direct connections from topic
        topic_info = self.topic_graph.get(topic, {})
        for related in topic_info.get("related", []):
            connections.append({
                "from": topic.replace("_", " ").title(),
                "to": related.replace("_", " ").title(),
                "type": "direct"
            })
        
        # Connections between related topics
        for related_topic in related_topics[:5]:
            related_info = self.topic_graph.get(related_topic, {})
            for connection in related_info.get("related", [])[:2]:
                if connection in related_topics:
                    connections.append({
                        "from": related_topic.replace("_", " ").title(),
                        "to": connection.replace("_", " ").title(),
                        "type": "indirect"
                    })
        
        return connections
    
    def suggest_topics(self, category: Optional[str] = None) -> List[str]:
        """Suggest topics to explore"""
        if category:
            # Find topics matching category
            suggestions = []
            for topic, info in self.topic_graph.items():
                if category.upper() in info.get("categories", []):
                    suggestions.append(topic.replace("_", " ").title())
            return suggestions
        
        # Return random selection
        all_topics = list(self.topic_graph.keys())
        return [t.replace("_", " ").title() for t in random.sample(all_topics, min(10, len(all_topics)))]
    
    def get_topic_categories(self) -> List[str]:
        """Get all unique categories from topics"""
        categories = set()
        for topic_info in self.topic_graph.values():
            categories.update(topic_info.get("categories", []))
        return sorted(list(categories))


# ============================================================================
# SINGLETON
# ============================================================================

_explorer_instance: Optional[Explorer] = None

def get_explorer() -> Explorer:
    """Get the global explorer instance"""
    global _explorer_instance
    if _explorer_instance is None:
        _explorer_instance = Explorer()
    return _explorer_instance
