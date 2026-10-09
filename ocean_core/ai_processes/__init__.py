"""
OCEAN AI PROCESSES
==================
Advanced AI processing engines for Curiosity Ocean

Modules:
- sentiment_analyzer: Emotional and sentiment analysis
- text_summarizer: Intelligent text summarization
- entity_extractor: Named Entity Recognition (NER)
- text_classifier: Multi-label text classification
- code_analyzer: Code understanding and analysis
- language_detector: Multi-language detection
- intent_classifier: User intent classification
- topic_modeler: Topic extraction and modeling
"""

from .sentiment_analyzer import SentimentAnalyzer, get_sentiment_analyzer
from .text_summarizer import TextSummarizer, get_text_summarizer
from .entity_extractor import EntityExtractor, get_entity_extractor
from .text_classifier import TextClassifier, get_text_classifier
from .code_analyzer import CodeAnalyzer, get_code_analyzer
from .language_detector import LanguageDetector, get_language_detector
from .intent_classifier import IntentClassifier, get_intent_classifier

__all__ = [
    "SentimentAnalyzer", "get_sentiment_analyzer",
    "TextSummarizer", "get_text_summarizer",
    "EntityExtractor", "get_entity_extractor",
    "TextClassifier", "get_text_classifier",
    "CodeAnalyzer", "get_code_analyzer",
    "LanguageDetector", "get_language_detector",
    "IntentClassifier", "get_intent_classifier",
]
