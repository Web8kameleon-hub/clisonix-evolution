# ============================================================================
# DISCOVERY ENGINE - Serendipitous Knowledge Discovery
# ============================================================================
# Find unexpected and interesting knowledge
# "Mock lozonjar-e" - playful discovery
# ============================================================================

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
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
class DiscoveryItem:
    """A discovered knowledge item"""
    title: str
    source: str
    url: str
    category: str
    country: str
    description: str
    discovery_type: str  # random, trending, unusual, featured
    fun_fact: Optional[str] = None
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "source": self.source,
            "url": self.url,
            "category": self.category,
            "country": self.country,
            "description": self.description,
            "discovery_type": self.discovery_type,
            "fun_fact": self.fun_fact,
            "score": self.score
        }


@dataclass
class DiscoverySession:
    """A discovery session with multiple items"""
    session_id: str
    theme: Optional[str]
    items: List[DiscoveryItem]
    timestamp: datetime = field(default_factory=datetime.now)
    user_preferences: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# FUN FACTS DATABASE
# ============================================================================

FUN_FACTS = {
    "GOVERNMENT": [
        "The world's oldest parliament is Iceland's Althing, established in 930 AD! 🏛️",
        "Monaco is smaller than Central Park in New York! 🏰",
        "The Vatican City is the world's smallest country with only 800 citizens! ⛪",
    ],
    "UNIVERSITY": [
        "Harvard University was founded before calculus was invented! 📚",
        "The University of Bologna in Italy is the oldest university in the world (1088)! 🎓",
        "Oxford University is older than the Aztec Empire! 🏫",
    ],
    "HOSPITAL": [
        "The heart beats about 100,000 times per day! ❤️",
        "Your brain uses 20% of your body's energy! 🧠",
        "Laughter can boost your immune system! 😄",
    ],
    "BANK": [
        "The first banknote was issued in China during the Tang Dynasty! 💴",
        "The largest gold bar weighs 250 kg! 🥇",
        "Sweden might become the first cashless country by 2025! 💳",
    ],
    "SPORT": [
        "A golf ball has 336 dimples! ⛳",
        "The Olympics were held in ancient Greece for 1,200 years! 🏅",
        "A marathon distance (42.195 km) commemorates a legendary Greek run! 🏃",
    ],
    "ENTERTAINMENT": [
        "The first movie ever made was in 1888 and was 2.11 seconds long! 🎬",
        "The Beatles hold the record for most #1 albums! 🎸",
        "Video games are now a bigger industry than movies and music combined! 🎮",
    ],
    "TOURISM": [
        "France is the most visited country in the world! 🗼",
        "The Great Wall of China is NOT visible from space with the naked eye! 🧱",
        "Disney World is roughly the same size as San Francisco! 🏰",
    ],
    "TECHNOLOGY": [
        "The first computer 'bug' was an actual bug (a moth)! 🦋",
        "Email existed before the World Wide Web! 📧",
        "The first website is still online at info.cern.ch! 🌐",
    ],
    "CULTURE": [
        "There are more than 7,000 languages spoken in the world! 🗣️",
        "The Mona Lisa has her own mailbox for all the love letters she receives! 🎨",
        "Japan has more than 6,800 islands! 🏝️",
    ],
    "STATISTICS": [
        "90% of the world's data was created in the last two years! 📊",
        "There are more possible chess games than atoms in the universe! ♟️",
        "The average person walks about 100,000 miles in a lifetime! 🚶",
    ],
}


# ============================================================================
# DISCOVERY THEMES
# ============================================================================

DISCOVERY_THEMES = [
    {
        "name": "Around the World",
        "description": "Discover sources from different continents",
        "filter": "random_countries",
        "icon": "🌍"
    },
    {
        "name": "Tech Frontiers",
        "description": "Cutting-edge technology sources",
        "filter": "technology",
        "icon": "🚀"
    },
    {
        "name": "Cultural Treasures",
        "description": "Arts, heritage, and traditions",
        "filter": "culture",
        "icon": "🎭"
    },
    {
        "name": "Sports World",
        "description": "Sports data from around the globe",
        "filter": "sport",
        "icon": "⚽"
    },
    {
        "name": "Knowledge Hubs",
        "description": "Universities and research centers",
        "filter": "university",
        "icon": "🎓"
    },
    {
        "name": "Data Wonderland",
        "description": "Amazing statistics and open data",
        "filter": "statistics",
        "icon": "📊"
    },
    {
        "name": "Entertainment Galaxy",
        "description": "Movies, music, and fun",
        "filter": "entertainment",
        "icon": "🎬"
    },
    {
        "name": "Green Planet",
        "description": "Environment and sustainability",
        "filter": "environmental",
        "icon": "🌿"
    },
    {
        "name": "API Treasures",
        "description": "Sources with available APIs",
        "filter": "api_only",
        "icon": "🔌"
    },
    {
        "name": "Random Adventure",
        "description": "Completely random discoveries",
        "filter": "random",
        "icon": "🎲"
    },
]


# ============================================================================
# DISCOVERY ENGINE CLASS
# ============================================================================

class DiscoveryEngine:
    """
    Serendipitous knowledge discovery engine
    
    Features:
    - Random discovery
    - Themed discovery
    - Fun facts integration
    - Unusual source spotlighting
    - "Mock lozonjar-e" mode (playful/fun)
    """
    
    def __init__(self):
        self._sources_cache = None
        self._session_counter = 0
        self.fun_facts = FUN_FACTS
        self.themes = DISCOVERY_THEMES
    
    def _load_sources(self):
        """Load data sources"""
        if self._sources_cache is not None:
            return
        
        try:
            from data_sources import GlobalDataSources
            gds = GlobalDataSources()
            self._sources_cache = gds.get_all_sources()
        except ImportError:
            self._sources_cache = []
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        self._session_counter += 1
        return f"disc_{datetime.now().strftime('%Y%m%d%H%M%S')}_{self._session_counter:04d}"
    
    def discover(
        self,
        theme: Optional[str] = None,
        count: int = 5,
        country: Optional[str] = None,
        category: Optional[str] = None,
        playful: bool = False
    ) -> DiscoverySession:
        """
        Discover interesting knowledge
        
        Args:
            theme: Discovery theme (from DISCOVERY_THEMES)
            count: Number of items to discover
            country: Filter by country
            category: Filter by category
            playful: Enable "mock lozonjar-e" mode with fun facts
        
        Returns:
            DiscoverySession with discovered items
        """
        self._load_sources()
        
        session_id = self._generate_session_id()
        items = []
        
        if not self._sources_cache:
            return DiscoverySession(
                session_id=session_id,
                theme=theme,
                items=items
            )
        
        # Filter sources based on criteria
        filtered = self._filter_sources(theme, country, category)
        
        # Select random items
        if len(filtered) > count:
            selected = random.sample(filtered, count)
        else:
            selected = filtered[:count]
        
        # Build discovery items
        for source in selected:
            cat = source.category.value if hasattr(source.category, 'value') else str(source.category)
            
            # Get fun fact if playful mode
            fun_fact = None
            if playful:
                cat_facts = self.fun_facts.get(cat.upper(), [])
                if cat_facts:
                    fun_fact = random.choice(cat_facts)
            
            items.append(DiscoveryItem(
                title=source.name,
                source=f"{source.country or 'Global'} - {cat}",
                url=source.url,
                category=cat,
                country=source.country or "Global",
                description=source.description[:200],
                discovery_type=self._determine_discovery_type(source),
                fun_fact=fun_fact,
                score=random.uniform(0.5, 1.0)  # Discovery score
            ))
        
        return DiscoverySession(
            session_id=session_id,
            theme=theme,
            items=items,
            user_preferences={
                "country": country,
                "category": category,
                "playful": playful
            }
        )
    
    def _filter_sources(
        self,
        theme: Optional[str],
        country: Optional[str],
        category: Optional[str]
    ) -> List[Any]:
        """Filter sources based on criteria"""
        filtered = self._sources_cache
        
        # Apply theme filter
        if theme:
            theme_info = next((t for t in self.themes if t["name"].lower() == theme.lower()), None)
            if theme_info:
                filter_type = theme_info["filter"]
                if filter_type == "api_only":
                    filtered = [s for s in filtered if s.api_available]
                elif filter_type == "random":
                    pass  # No filter
                elif filter_type == "random_countries":
                    # Select from random countries
                    countries = list(set(s.country for s in filtered if s.country))
                    if len(countries) > 5:
                        selected_countries = random.sample(countries, 5)
                        filtered = [s for s in filtered if s.country in selected_countries]
                else:
                    # Filter by category
                    filtered = [
                        s for s in filtered 
                        if (s.category.value.lower() if hasattr(s.category, 'value') else str(s.category).lower()) == filter_type
                    ]
        
        # Apply country filter
        if country:
            filtered = [s for s in filtered if s.country and s.country.lower() == country.lower()]
        
        # Apply category filter
        if category:
            filtered = [
                s for s in filtered 
                if (s.category.value.lower() if hasattr(s.category, 'value') else str(s.category).lower()) == category.lower()
            ]
        
        return filtered
    
    def _determine_discovery_type(self, source: Any) -> str:
        """Determine the type of discovery"""
        if source.api_available:
            return "featured"
        if random.random() < 0.2:
            return "unusual"
        if random.random() < 0.3:
            return "trending"
        return "random"
    
    def get_random_fun_fact(self, category: Optional[str] = None) -> str:
        """Get a random fun fact"""
        if category and category.upper() in self.fun_facts:
            return random.choice(self.fun_facts[category.upper()])
        
        # Random category
        all_facts = []
        for facts in self.fun_facts.values():
            all_facts.extend(facts)
        
        return random.choice(all_facts) if all_facts else "Knowledge is power! 📚"
    
    def get_themes(self) -> List[Dict[str, Any]]:
        """Get available discovery themes"""
        return self.themes
    
    def suggest_discovery(self) -> Dict[str, Any]:
        """Suggest a discovery adventure"""
        theme = random.choice(self.themes)
        
        return {
            "suggested_theme": theme["name"],
            "description": theme["description"],
            "icon": theme["icon"],
            "prompt": f"Discover {theme['name']}: {theme['description']}",
            "endpoint": f"/discover?theme={theme['name'].lower().replace(' ', '_')}"
        }
    
    def daily_discovery(self) -> DiscoverySession:
        """
        Get the daily discovery - same items for everyone on a given day
        Based on date seed for consistency
        """
        today = datetime.now().strftime("%Y%m%d")
        random.seed(int(today))  # Seed with today's date
        
        session = self.discover(
            theme="Random Adventure",
            count=5,
            playful=True
        )
        
        random.seed()  # Reset random seed
        return session


# ============================================================================
# SINGLETON
# ============================================================================

_discovery_instance: Optional[DiscoveryEngine] = None

def get_discovery() -> DiscoveryEngine:
    """Get the global discovery engine instance"""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = DiscoveryEngine()
    return _discovery_instance
