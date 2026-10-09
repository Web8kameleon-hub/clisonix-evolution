"""
Sentiment Analyzer - Emotional and sentiment analysis
Analyzes text for sentiment (positive/negative/neutral) and emotional dimensions
Supports multiple languages including Albanian (sq)
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Result of sentiment analysis"""
    sentiment: str  # positive, negative, neutral
    confidence: float
    sentiment_score: float  # -1.0 to 1.0
    emotions: Dict[str, float] = field(default_factory=dict)  # joy, anger, sadness, etc.
    language: str = "en"
    details: Dict[str, Any] = field(default_factory=dict)


class SentimentAnalyzer:
    """
    Advanced sentiment analysis with emotional dimensions
    Supports multiple languages and contextual understanding
    """
    
    # Emotion keywords by language
    EMOTION_KEYWORDS = {
        "en": {
            "joy": ["happy", "joy", "delighted", "excited", "wonderful", "great", "love", "amazing"],
            "anger": ["angry", "mad", "furious", "hate", "annoyed", "frustrated"],
            "sadness": ["sad", "unhappy", "depressed", "gloomy", "heartbroken", "miserable"],
            "fear": ["afraid", "scared", "terrified", "anxious", "worried", "fearful"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "wow"],
            "trust": ["trust", "believe", "confident", "sure", "certain"],
            "anticipation": ["expect", "anticipate", "looking forward", "hope"],
            "disgust": ["disgusting", "gross", "repulsive", "awful"]
        },
        "sq": {
            "joy": ["lumtur", "gëzim", "entuziazëm", "mrekullueshëm", "shkëlqyeshëm", "dua", "bukur", "i kënaqur"],
            "anger": ["zemëruar", "i mllefosur", "urrej", "acarohem", "frustruar", "i nervozuar", "inat"],
            "sadness": ["trishtuar", "i palumtur", "deprimuar", "zemërthyer", "mërzit", "pikëlluar"],
            "fear": ["frikë", "i trembur", "ankth", "shqetësim", "i frikësuar", "i merakosur"],
            "surprise": ["i habitur", "i befasuar", "shokuar", "mahnitur", "i çuditur"],
            "trust": ["besoj", "kam besim", "i sigurt", "vendosur"]
        },
        "de": {
            "joy": ["glücklich", "freude", "begeistert", "wunderbar", "liebe", "fantastisch"],
            "anger": ["wütend", "sauer", "hass", "verärgert", "frustriert"],
            "sadness": ["traurig", "unglücklich", "deprimiert", "niedergeschlagen"],
            "fear": ["angst", "ängstlich", "besorgt", "furchtsam"],
            "surprise": ["überrascht", "schockiert", "erstaunt", "verblüfft"]
        }
    }
    
    # Sentiment word lists
    POSITIVE_WORDS = {
        "en": ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "love", "like", "best", 
               "perfect", "awesome", "brilliant", "outstanding", "beautiful", "nice", "happy"],
        "sq": ["mirë", "shkëlqyeshëm", "bukur", "perfekt", "fantastik", "dua", "pëlqej", "madhështor",
               "i mrekullueshëm", "i jashtëzakonshëm", "shiko", "më pëlqen"],
        "de": ["gut", "großartig", "ausgezeichnet", "wunderbar", "fantastisch", "liebe", "beste"]
    }
    
    NEGATIVE_WORDS = {
        "en": ["bad", "terrible", "awful", "horrible", "hate", "worst", "dislike", "poor", 
               "disappointing", "frustrated", "angry", "sad", "wrong", "fail", "mistake"],
        "sq": ["keq", "tmerrshëm", "urrej", "i tmerrshëm", "i dobët", "gabim", "dështim", 
               "zhgënjyes", "i mërzitshëm", "e keqe", "nuk më pëlqen"],
        "de": ["schlecht", "schrecklich", "furchtbar", "hasse", "schlimmste", "enttäuschend"]
    }
    
    # Negation words for context
    NEGATION_WORDS = {
        "en": ["not", "no", "never", "don't", "doesn't", "didn't", "won't", "wouldn't", "can't", "couldn't"],
        "sq": ["nuk", "jo", "kurrë", "mos", "s'ka", "nuk jam", "nuk është"],
        "de": ["nicht", "kein", "nie", "niemals"]
    }
    
    # Intensifiers
    INTENSIFIERS = {
        "en": ["very", "really", "extremely", "absolutely", "completely", "totally", "super", "incredibly"],
        "sq": ["shumë", "tepër", "jashtëzakonisht", "plotësisht", "absolutisht"],
        "de": ["sehr", "wirklich", "extrem", "absolut", "völlig"]
    }
    
    def __init__(self, language: str = "en", use_deep_learning: bool = False):
        self.language = language
        self.use_deep_learning = use_deep_learning
        self.sentiment_pipeline = None
        self.emotion_pipeline = None
        
        # Initialize ML model if requested
        if use_deep_learning:
            self._init_deep_learning()
    
    def _init_deep_learning(self) -> None:
        """Initialize deep learning models"""
        try:
            from transformers import pipeline
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            self.emotion_pipeline = pipeline(
                "text-classification",
                model="j-hartmann/emotion-english-distilroberta-base"
            )
            logger.info("✅ Deep learning models loaded")
        except ImportError:
            logger.warning("⚠️ Transformers not installed, using rule-based")
            self.use_deep_learning = False
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            self.use_deep_learning = False
    
    def analyze(self, text: str, language: Optional[str] = None) -> SentimentResult:
        """
        Analyze sentiment and emotions in text
        
        Args:
            text: Text to analyze
            language: Language code (en, sq, de, etc.)
            
        Returns:
            SentimentResult with sentiment, confidence, emotions
        """
        lang = language or self.language
        
        if self.use_deep_learning and lang == "en" and self.sentiment_pipeline:
            return self._analyze_deep(text)
        else:
            return self._analyze_rule_based(text, lang)
    
    def _analyze_deep(self, text: str) -> SentimentResult:
        """Deep learning based analysis"""
        try:
            # Sentiment analysis
            sentiment_result = self.sentiment_pipeline(text[:512])[0]
            
            # Map to our format
            sentiment_map = {
                "LABEL_0": "negative",
                "LABEL_1": "neutral",
                "LABEL_2": "positive",
                "negative": "negative",
                "neutral": "neutral",
                "positive": "positive"
            }
            sentiment = sentiment_map.get(sentiment_result["label"], "neutral")
            
            # Emotion analysis
            emotions = {}
            if self.emotion_pipeline:
                emotion_result = self.emotion_pipeline(text[:512])[0]
                emotions = {emotion_result["label"]: emotion_result["score"]}
            
            # Calculate sentiment score (-1 to 1)
            score_map = {"negative": -0.8, "neutral": 0.0, "positive": 0.8}
            sentiment_score = score_map.get(sentiment, 0.0)
            
            return SentimentResult(
                sentiment=sentiment,
                confidence=sentiment_result["score"],
                sentiment_score=sentiment_score,
                emotions=emotions,
                language="en",
                details={"model": "transformer", "raw_label": sentiment_result["label"]}
            )
        except Exception as e:
            logger.error(f"Deep analysis failed: {e}")
            return self._analyze_rule_based(text, "en")
    
    def _analyze_rule_based(self, text: str, language: str) -> SentimentResult:
        """Rule-based analysis using keyword matching"""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Get word lists for language
        positive_words = self.POSITIVE_WORDS.get(language, self.POSITIVE_WORDS["en"])
        negative_words = self.NEGATIVE_WORDS.get(language, self.NEGATIVE_WORDS["en"])
        emotion_words = self.EMOTION_KEYWORDS.get(language, self.EMOTION_KEYWORDS["en"])
        negation_words = self.NEGATION_WORDS.get(language, self.NEGATION_WORDS["en"])
        intensifiers = self.INTENSIFIERS.get(language, self.INTENSIFIERS["en"])
        
        # Count sentiment words with context
        positive_count = 0
        negative_count = 0
        
        for i, word in enumerate(words):
            # Check for negation in previous words
            is_negated = any(words[max(0, i-2):i].count(neg) for neg in negation_words)
            
            # Check for intensifier
            has_intensifier = any(words[max(0, i-2):i].count(int_) for int_ in intensifiers)
            multiplier = 1.5 if has_intensifier else 1.0
            
            if word in positive_words:
                if is_negated:
                    negative_count += multiplier
                else:
                    positive_count += multiplier
            elif word in negative_words:
                if is_negated:
                    positive_count += multiplier
                else:
                    negative_count += multiplier
        
        total_count = positive_count + negative_count
        
        # Calculate sentiment score
        if total_count > 0:
            sentiment_score = (positive_count - negative_count) / total_count
        else:
            sentiment_score = 0.0
        
        # Also consider sentence-level patterns
        sentiment_score = self._adjust_for_patterns(text_lower, sentiment_score, language)
        
        # Determine sentiment
        if sentiment_score > 0.15:
            sentiment = "positive"
        elif sentiment_score < -0.15:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Detect emotions
        emotions = {}
        for emotion, keywords in emotion_words.items():
            count = sum(1 for w in words if w in keywords)
            if count > 0:
                emotions[emotion] = min(count / len(words) * 3, 1.0)  # Normalize
        
        # Calculate confidence
        if total_count > 0:
            confidence = min(abs(sentiment_score) + 0.4, 0.95)
        else:
            confidence = 0.5
        
        return SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            sentiment_score=sentiment_score,
            emotions=emotions,
            language=language,
            details={
                "method": "rule_based",
                "positive_count": positive_count,
                "negative_count": negative_count,
                "word_count": len(words)
            }
        )
    
    def _adjust_for_patterns(self, text: str, score: float, language: str) -> float:
        """Adjust sentiment score based on patterns"""
        # Exclamation marks can intensify sentiment
        exclamation_count = text.count('!')
        if exclamation_count > 0:
            score *= (1 + exclamation_count * 0.1)
        
        # Question marks might indicate uncertainty
        question_count = text.count('?')
        if question_count > 0:
            score *= 0.9
        
        # ALL CAPS text often indicates strong emotion
        if text.isupper() and len(text) > 10:
            score *= 1.3
        
        # Emoji patterns (basic)
        positive_emoji = len(re.findall(r'[:;][-]?[)D]|❤|👍|😊|😀|🎉', text))
        negative_emoji = len(re.findall(r'[:;][-]?[(]|😢|😠|👎|😞', text))
        
        if positive_emoji > 0:
            score += positive_emoji * 0.1
        if negative_emoji > 0:
            score -= negative_emoji * 0.1
        
        return max(min(score, 1.0), -1.0)
    
    def analyze_batch(self, texts: List[str], language: Optional[str] = None) -> List[SentimentResult]:
        """Analyze multiple texts"""
        return [self.analyze(text, language) for text in texts]
    
    def get_sentiment_trend(self, texts: List[str], language: Optional[str] = None) -> Dict[str, Any]:
        """Analyze sentiment trend over multiple texts"""
        results = self.analyze_batch(texts, language)
        
        if not results:
            return {"overall_sentiment": "neutral", "average_score": 0, "trend": "stable", "volatility": 0}
        
        sentiments = [r.sentiment for r in results]
        scores = [r.sentiment_score for r in results]
        
        return {
            "overall_sentiment": max(set(sentiments), key=sentiments.count),
            "average_score": sum(scores) / len(scores),
            "trend": "improving" if scores[-1] > scores[0] else "declining" if scores[-1] < scores[0] else "stable",
            "volatility": max(scores) - min(scores) if len(scores) > 1 else 0,
            "count": len(results),
            "positive_count": sentiments.count("positive"),
            "negative_count": sentiments.count("negative"),
            "neutral_count": sentiments.count("neutral"),
            "results": results
        }
    
    def get_emotion_summary(self, texts: List[str], language: Optional[str] = None) -> Dict[str, float]:
        """Get aggregated emotion summary from multiple texts"""
        results = self.analyze_batch(texts, language)
        
        emotion_totals = {}
        for result in results:
            for emotion, score in result.emotions.items():
                emotion_totals[emotion] = emotion_totals.get(emotion, 0) + score
        
        # Normalize
        if results:
            for emotion in emotion_totals:
                emotion_totals[emotion] /= len(results)
        
        return emotion_totals
