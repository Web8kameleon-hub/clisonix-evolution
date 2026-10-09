"""
Text Classifier - Multi-label text classification
Categorizes text into predefined or custom categories
Supports multiple languages
"""

import logging
import math
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of text classification"""
    labels: List[str]
    scores: Dict[str, float]
    dominant_label: str
    confidence: float
    multi_label: bool


class TextClassifier:
    """
    Multi-label text classifier
    Supports predefined categories and custom training
    """
    
    # Default category keywords
    CATEGORY_KEYWORDS = {
        "technology": [
            "software", "hardware", "computer", "ai", "artificial intelligence", "machine learning",
            "programming", "code", "algorithm", "data", "digital", "internet", "cloud", "blockchain",
            "cybersecurity", "api", "database", "neural", "robot", "automation", "tech"
        ],
        "business": [
            "company", "market", "sales", "revenue", "profit", "investment", "stock", "ceo",
            "startup", "entrepreneur", "finance", "banking", "trade", "economy", "corporate",
            "strategy", "management", "growth", "merger", "acquisition", "business"
        ],
        "sports": [
            "game", "team", "player", "score", "championship", "league", "match", "tournament",
            "goal", "victory", "defeat", "coach", "athlete", "football", "basketball", "soccer",
            "tennis", "olympics", "sport", "win"
        ],
        "health": [
            "medical", "hospital", "doctor", "disease", "treatment", "patient", "medicine",
            "health", "vaccine", "symptom", "diagnosis", "surgery", "therapy", "wellness",
            "nutrition", "mental", "covid", "virus", "healthcare", "clinical"
        ],
        "science": [
            "research", "study", "experiment", "discovery", "scientist", "laboratory",
            "physics", "chemistry", "biology", "astronomy", "climate", "environment",
            "nature", "evolution", "theory", "hypothesis", "findings", "scientific"
        ],
        "politics": [
            "government", "president", "election", "vote", "policy", "congress", "senate",
            "law", "regulation", "political", "democrat", "republican", "campaign",
            "legislation", "minister", "parliament", "democracy", "constitution"
        ],
        "entertainment": [
            "movie", "film", "music", "celebrity", "star", "show", "concert", "actor",
            "actress", "director", "album", "song", "tv", "series", "award", "festival",
            "streaming", "netflix", "spotify", "entertainment"
        ],
        "education": [
            "school", "university", "student", "teacher", "learning", "course", "degree",
            "academic", "curriculum", "exam", "graduation", "scholarship", "education",
            "classroom", "professor", "lecture", "study"
        ]
    }
    
    # Albanian category keywords
    ALBANIAN_KEYWORDS = {
        "teknologji": ["kompjuter", "softuer", "harduer", "internet", "programim", "algoritmi", 
                      "të dhëna", "robot", "automatizim", "teknologji", "dixhital", "inteligjencë"],
        "biznes": ["kompani", "treg", "shitje", "fitim", "investim", "bankë", "ekonomi", 
                  "biznes", "menaxhim", "strategji", "rritje"],
        "sport": ["futboll", "basketboll", "ekip", "ndeshje", "fitore", "humbje", "trajner",
                 "kampionat", "lojë", "atlet", "sport", "gol"],
        "shëndetësi": ["spital", "mjek", "pacient", "sëmundje", "trajtim", "vaksinë", 
                      "shëndet", "kirurgji", "terapi", "diagnozë"],
        "shkencë": ["kërkim", "studim", "eksperiment", "zbulim", "shkencëtar", "laborator",
                   "fizikë", "kimi", "biologji", "teori", "natyrë"],
        "arsim": ["shkollë", "universitet", "student", "mësues", "kurs", "diplomë", "arsim",
                 "provim", "mësim", "profesor", "edukim"]
    }
    
    def __init__(self, language: str = "en", use_transformers: bool = False):
        self.language = language
        self.use_transformers = use_transformers
        self.classifier = None
        self.custom_categories: Dict[str, List[str]] = {}
        
        if use_transformers:
            self._init_transformers()
    
    def _init_transformers(self) -> None:
        """Initialize transformer-based classifier"""
        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            logger.info("✅ Transformer classifier loaded")
        except ImportError:
            logger.warning("⚠️ Transformers not installed, using keyword-based")
            self.use_transformers = False
        except Exception as e:
            logger.error(f"❌ Classifier loading failed: {e}")
            self.use_transformers = False
    
    def classify(
        self,
        text: str,
        categories: Optional[List[str]] = None,
        multi_label: bool = True,
        threshold: float = 0.3
    ) -> ClassificationResult:
        """
        Classify text into categories
        
        Args:
            text: Text to classify
            categories: List of target categories (uses defaults if None)
            multi_label: Allow multiple labels
            threshold: Minimum score for label assignment
            
        Returns:
            ClassificationResult with labels and scores
        """
        # Get keyword dict based on language
        if self.language == "sq":
            keyword_dict = {**self.ALBANIAN_KEYWORDS, **self.custom_categories}
        else:
            keyword_dict = {**self.CATEGORY_KEYWORDS, **self.custom_categories}
        
        # Use specified categories or all available
        if categories:
            keyword_dict = {k: v for k, v in keyword_dict.items() if k in categories}
        
        if self.use_transformers and self.classifier:
            return self._classify_transformers(text, list(keyword_dict.keys()), multi_label)
        
        return self._classify_keyword_based(text, keyword_dict, multi_label, threshold)
    
    def _classify_keyword_based(
        self,
        text: str,
        keyword_dict: Dict[str, List[str]],
        multi_label: bool,
        threshold: float
    ) -> ClassificationResult:
        """Keyword-based classification with TF-IDF-like scoring"""
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        scores: Dict[str, float] = {}
        
        for category, keywords in keyword_dict.items():
            score = 0.0
            for keyword in keywords:
                # Count occurrences
                count = text_lower.count(keyword.lower())
                if count > 0:
                    # TF-IDF-like weighting
                    tf = count / len(words) if words else 0
                    # IDF approximation (rarer keywords score higher)
                    idf = math.log(len(keyword_dict) / 1)  # Simplified
                    score += tf * idf * (1 + len(keyword.split()))  # Boost multi-word matches
            
            # Normalize
            if keywords:
                score = score / len(keywords) * 10  # Scale to 0-1 range
            
            scores[category] = min(score, 1.0)
        
        # Get labels above threshold
        labels = [cat for cat, score in scores.items() if score >= threshold]
        
        if not multi_label and len(labels) > 1:
            # Keep only top label
            labels = [max(scores.keys(), key=lambda k: scores[k])]
        
        # Handle case with no labels
        if not labels:
            labels = [max(scores.keys(), key=lambda k: scores[k])]
        
        dominant = max(scores.keys(), key=lambda k: scores[k])
        
        return ClassificationResult(
            labels=labels,
            scores=scores,
            dominant_label=dominant,
            confidence=scores[dominant],
            multi_label=multi_label
        )
    
    def _classify_transformers(
        self,
        text: str,
        categories: List[str],
        multi_label: bool
    ) -> ClassificationResult:
        """Classification using transformers"""
        try:
            result = self.classifier(
                text[:512],  # Limit text length
                categories,
                multi_label=multi_label
            )
            
            scores = dict(zip(result['labels'], result['scores']))
            
            if multi_label:
                labels = [label for label, score in scores.items() if score > 0.5]
                if not labels:
                    labels = [result['labels'][0]]
            else:
                labels = [result['labels'][0]]
            
            return ClassificationResult(
                labels=labels,
                scores=scores,
                dominant_label=result['labels'][0],
                confidence=result['scores'][0],
                multi_label=multi_label
            )
        except Exception as e:
            logger.error(f"Transformer classification failed: {e}")
            return self._classify_keyword_based(text, self.CATEGORY_KEYWORDS, multi_label, 0.3)
    
    def add_category(self, name: str, keywords: List[str]) -> None:
        """Add a custom category with keywords"""
        self.custom_categories[name] = keywords
    
    def remove_category(self, name: str) -> bool:
        """Remove a custom category"""
        if name in self.custom_categories:
            del self.custom_categories[name]
            return True
        return False
    
    def classify_batch(self, texts: List[str], categories: Optional[List[str]] = None) -> List[ClassificationResult]:
        """Classify multiple texts"""
        return [self.classify(text, categories) for text in texts]
    
    def train_from_examples(self, examples: List[Tuple[str, str]]) -> None:
        """
        Train classifier from labeled examples
        
        Args:
            examples: List of (text, category) tuples
        """
        for text, category in examples:
            words = re.findall(r'\b\w{4,}\b', text.lower())
            
            # Get top keywords
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            top_words = sorted(word_counts.keys(), key=lambda w: word_counts[w], reverse=True)[:10]
            
            if category in self.custom_categories:
                self.custom_categories[category].extend(top_words)
            else:
                self.custom_categories[category] = top_words
    
    def get_category_distribution(self, texts: List[str]) -> Dict[str, int]:
        """Get category distribution across multiple texts"""
        distribution = {}
        
        for text in texts:
            result = self.classify(text, multi_label=False)
            category = result.dominant_label
            distribution[category] = distribution.get(category, 0) + 1
        
        return distribution
    
    def explain_classification(self, text: str) -> Dict[str, List[str]]:
        """Explain why text was classified into categories"""
        text_lower = text.lower()
        
        keywords_dict = self.ALBANIAN_KEYWORDS if self.language == "sq" else self.CATEGORY_KEYWORDS
        keywords_dict = {**keywords_dict, **self.custom_categories}
        
        explanations = {}
        
        for category, keywords in keywords_dict.items():
            found_keywords = [kw for kw in keywords if kw.lower() in text_lower]
            if found_keywords:
                explanations[category] = found_keywords
        
        return explanations
    
    def get_available_categories(self) -> List[str]:
        """Get list of available categories"""
        keywords_dict = self.ALBANIAN_KEYWORDS if self.language == "sq" else self.CATEGORY_KEYWORDS
        all_categories = list(keywords_dict.keys()) + list(self.custom_categories.keys())
        return list(set(all_categories))
