"""
Text Summarizer - Intelligent text summarization
Extractive and abstractive summarization with multiple strategies
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SummaryResult:
    """Result of text summarization"""
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    method: str  # extractive, abstractive, hybrid
    key_sentences: List[str]
    confidence: float


class TextSummarizer:
    """
    Advanced text summarization with multiple strategies
    Supports extractive and abstractive summarization
    """
    
    def __init__(self, use_transformers: bool = False):
        self.use_transformers = use_transformers
        self.summarizer = None
        
        if use_transformers:
            self._init_transformers()
    
    def _init_transformers(self) -> None:
        """Initialize transformer models"""
        try:
            from transformers import pipeline
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            logger.info("✅ Transformer summarizer loaded")
        except ImportError:
            logger.warning("⚠️ Transformers not installed, using extractive")
            self.use_transformers = False
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            self.use_transformers = False
    
    def summarize(
        self,
        text: str,
        max_length: Optional[int] = None,
        min_length: Optional[int] = None,
        method: str = "hybrid",
        language: str = "en"
    ) -> SummaryResult:
        """
        Summarize text using specified method
        
        Args:
            text: Text to summarize
            max_length: Maximum summary length in words
            min_length: Minimum summary length in words
            method: 'extractive', 'abstractive', or 'hybrid'
            language: Language code
            
        Returns:
            SummaryResult with summary and metadata
        """
        # Clean text
        text = self._clean_text(text)
        original_length = len(text.split())
        
        # Set default lengths
        if max_length is None:
            max_length = max(50, original_length // 3)
        if min_length is None:
            min_length = max(20, original_length // 10)
        
        if self.use_transformers and method in ["abstractive", "hybrid"] and language == "en":
            return self._abstractive_summary(text, max_length, min_length)
        else:
            return self._extractive_summary(text, max_length, method == "hybrid")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\'\"]', '', text)
        return text.strip()
    
    def _extractive_summary(
        self,
        text: str,
        max_length: int,
        use_hybrid: bool = False
    ) -> SummaryResult:
        """Extractive summarization using sentence scoring"""
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        if not sentences:
            return SummaryResult(
                summary=text,
                original_length=len(text.split()),
                summary_length=len(text.split()),
                compression_ratio=1.0,
                method="extractive",
                key_sentences=[],
                confidence=1.0
            )
        
        # Score sentences
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = self._score_sentence(sentence, i, sentences, text)
            scored_sentences.append((score, sentence, i))  # Include original index
        
        # Sort by score
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        
        # Select sentences until max_length
        selected = []
        current_length = 0
        key_sentences = []
        
        for score, sentence, idx in scored_sentences:
            sent_len = len(sentence.split())
            if current_length + sent_len <= max_length:
                selected.append((idx, sentence))  # Store index for ordering
                current_length += sent_len
                key_sentences.append(sentence)
        
        # Restore original order (important for coherence)
        selected.sort(key=lambda x: x[0])
        summary = ' '.join(s[1] for s in selected)
        
        # If no sentences selected, take first sentences
        if not selected and sentences:
            summary = ' '.join(sentences[:2])
            key_sentences = sentences[:2]
        
        # Calculate metrics
        summary_length = len(summary.split())
        compression_ratio = summary_length / len(text.split()) if len(text.split()) > 0 else 1
        
        return SummaryResult(
            summary=summary,
            original_length=len(text.split()),
            summary_length=summary_length,
            compression_ratio=compression_ratio,
            method="extractive" if not use_hybrid else "hybrid",
            key_sentences=key_sentences,
            confidence=0.85
        )
    
    def _score_sentence(
        self, 
        sentence: str, 
        position: int, 
        all_sentences: List[str], 
        full_text: str
    ) -> float:
        """Score a sentence for extractive summarization"""
        words = sentence.lower().split()
        
        # Position score (sentences at beginning and end are more important)
        if position == 0:
            position_score = 1.5  # First sentence
        elif position == len(all_sentences) - 1:
            position_score = 1.3  # Last sentence
        else:
            position_score = 1.0 - (position / len(all_sentences)) * 0.5
        
        # Length score (sentences of medium length are better)
        if len(words) <= 20:
            length_score = min(len(words) / 20, 1.0)
        else:
            length_score = max(0, 1.0 - (len(words) - 20) / 30)
        
        # Keyword score (contains important words)
        keywords = self._extract_keywords(full_text, 10)
        keyword_count = sum(1 for w in words if w in keywords)
        keyword_score = min(keyword_count / 3, 1.0) if keyword_count > 0 else 0
        
        # Named entity score (sentences with proper nouns are important)
        proper_noun_count = len(re.findall(r'\b[A-Z][a-z]+\b', sentence))
        entity_score = min(proper_noun_count / 3, 1.0)
        
        # Combine scores with weights
        total_score = (
            position_score * 0.25 +
            length_score * 0.15 +
            keyword_score * 0.45 +
            entity_score * 0.15
        )
        
        return total_score
    
    def _extract_keywords(self, text: str, n: int = 10) -> List[str]:
        """Extract important keywords from text"""
        words = text.lower().split()
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'were', 'are', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'it', 'its', 'they', 'them', 'their', 'he', 'she',
            'him', 'her', 'his', 'hers', 'we', 'us', 'our', 'you', 'your', 'i', 'me', 'my'
        }
        
        # Count word frequencies
        word_counts = {}
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word and clean_word not in stop_words and len(clean_word) > 3:
                word_counts[clean_word] = word_counts.get(clean_word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, count in sorted_words[:n]]
    
    def _abstractive_summary(self, text: str, max_length: int, min_length: int) -> SummaryResult:
        """Abstractive summarization using transformers"""
        try:
            # Truncate if too long
            if len(text) > 1024:
                text = text[:1024]
            
            result = self.summarizer(
                text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )[0]
            
            summary = result['summary_text']
            
            return SummaryResult(
                summary=summary,
                original_length=len(text.split()),
                summary_length=len(summary.split()),
                compression_ratio=len(summary.split()) / len(text.split()),
                method="abstractive",
                key_sentences=[summary],
                confidence=0.9
            )
        except Exception as e:
            logger.error(f"Abstractive summary failed: {e}")
            return self._extractive_summary(text, max_length, False)
    
    def summarize_with_focus(
        self,
        text: str,
        focus_keywords: List[str],
        max_length: Optional[int] = None
    ) -> SummaryResult:
        """Summarize with focus on specific keywords"""
        target_length = max_length or 100
        result = self._extractive_summary(text, target_length, True)
        
        # Boost sentences containing focus keywords
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        focused_sentences = []
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in focus_keywords):
                focused_sentences.append(sentence)
        
        if focused_sentences:
            # Combine focused sentences with original summary
            focused_summary = ' '.join(focused_sentences[:2])
            
            # Trim if too long
            focused_words = focused_summary.split()
            if len(focused_words) > target_length // 2:
                focused_summary = ' '.join(focused_words[:target_length // 2])
            
            result.summary = focused_summary + ' ' + result.summary
            result.key_sentences = focused_sentences + result.key_sentences
            result.method = "focused"
        
        return result
    
    def summarize_batch(self, texts: List[str], max_length: Optional[int] = None) -> List[SummaryResult]:
        """Summarize multiple texts"""
        return [self.summarize(text, max_length=max_length) for text in texts]
    
    def get_reading_time(self, text: str, words_per_minute: int = 200) -> Dict[str, Any]:
        """Estimate reading time for original and summarized versions"""
        original_words = len(text.split())
        summary = self.summarize(text)
        
        return {
            "original_words": original_words,
            "original_reading_time_minutes": original_words / words_per_minute,
            "summary_words": summary.summary_length,
            "summary_reading_time_minutes": summary.summary_length / words_per_minute,
            "time_saved_minutes": (original_words - summary.summary_length) / words_per_minute,
            "compression_ratio": summary.compression_ratio
        }
