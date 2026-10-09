"""
Topic Modeler - Topic extraction and modeling
Discovers topics in text collections using keyword analysis and LDA
"""

import logging
import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Topic:
    """Represents a discovered topic"""
    id: int
    keywords: List[str]
    weight: float
    label: Optional[str] = None
    sample_documents: List[str] = None


@dataclass
class TopicModelResult:
    """Result of topic modeling"""
    topics: List[Topic]
    document_topics: Dict[int, List[Tuple[int, float]]]  # doc_id -> [(topic_id, weight), ...]
    coherence_score: float
    num_topics: int


class TopicModeler:
    """
    Topic modeling using keyword extraction and optional LDA
    Discovers themes in document collections
    """
    
    # Common stop words (multiple languages)
    STOP_WORDS = {
        "en": {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", 
            "of", "with", "by", "from", "as", "is", "was", "were", "are", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "can", "this", "that",
            "these", "those", "it", "its", "they", "them", "their", "he", "she",
            "him", "her", "his", "hers", "we", "us", "our", "you", "your", "i",
            "me", "my", "not", "no", "so", "if", "then", "than", "just", "also",
            "very", "more", "some", "any", "all", "each", "every", "both", "few",
            "most", "other", "into", "only", "own", "same", "such", "what", "which",
            "who", "whom", "how", "when", "where", "why", "here", "there", "now",
            "about", "above", "after", "again", "against", "before", "below",
            "between", "during", "further", "once", "through", "under", "until"
        },
        "sq": {
            "dhe", "ose", "por", "në", "me", "për", "nga", "si", "që", "është",
            "janë", "ka", "kanë", "do", "mund", "duhet", "kjo", "ky", "kur", "ku",
            "çfarë", "pse", "nuk", "po", "jo", "edhe", "vetëm", "shumë", "pak",
            "të", "i", "e", "së", "një", "disa", "gjithë", "secili", "asnjë",
            "mirë", "keq", "si", "ashtu", "kështu", "atje", "këtu", "tani", "pastaj"
        },
        "de": {
            "der", "die", "das", "ein", "eine", "und", "oder", "aber", "in", "auf",
            "an", "zu", "für", "von", "mit", "bei", "aus", "als", "ist", "sind",
            "war", "waren", "hat", "haben", "wird", "werden", "kann", "können",
            "muss", "müssen", "soll", "sollen", "nicht", "auch", "so", "wie",
            "dann", "wenn", "weil", "dass", "ob", "doch", "noch", "schon", "nur"
        }
    }
    
    def __init__(self, language: str = "en", use_sklearn: bool = False):
        self.language = language
        self.use_sklearn = use_sklearn
        self.lda_model = None
        self.vectorizer = None
        self.vocabulary: Dict[str, int] = {}
        
        if use_sklearn:
            self._init_sklearn()
    
    def _init_sklearn(self) -> None:
        """Initialize sklearn LDA"""
        try:
            from sklearn.decomposition import LatentDirichletAllocation
            from sklearn.feature_extraction.text import CountVectorizer
            
            self.vectorizer = CountVectorizer(
                max_df=0.95,
                min_df=2,
                max_features=1000,
                stop_words='english'
            )
            self.sklearn_available = True
            logger.info("✅ Sklearn LDA available")
        except ImportError:
            logger.warning("⚠️ Sklearn not installed, using keyword-based")
            self.use_sklearn = False
            self.sklearn_available = False
    
    def fit(self, documents: List[str], num_topics: int = 5) -> TopicModelResult:
        """
        Fit topic model to documents
        
        Args:
            documents: List of documents to model
            num_topics: Number of topics to extract
            
        Returns:
            TopicModelResult with discovered topics
        """
        if self.use_sklearn and self.sklearn_available:
            return self._fit_sklearn(documents, num_topics)
        
        return self._fit_keyword_based(documents, num_topics)
    
    def _fit_sklearn(self, documents: List[str], num_topics: int) -> TopicModelResult:
        """Fit using sklearn LDA"""
        try:
            from sklearn.decomposition import LatentDirichletAllocation
            
            # Vectorize documents
            doc_term_matrix = self.vectorizer.fit_transform(documents)
            
            # Fit LDA
            self.lda_model = LatentDirichletAllocation(
                n_components=num_topics,
                max_iter=10,
                learning_method='online',
                random_state=42
            )
            doc_topics = self.lda_model.fit_transform(doc_term_matrix)
            
            # Extract topics
            feature_names = self.vectorizer.get_feature_names_out()
            topics = []
            
            for topic_idx, topic in enumerate(self.lda_model.components_):
                top_words_idx = topic.argsort()[-10:][::-1]
                keywords = [feature_names[i] for i in top_words_idx]
                weight = topic[top_words_idx].sum() / topic.sum()
                
                # Get sample documents
                topic_docs = []
                for doc_idx, topic_dist in enumerate(doc_topics):
                    if topic_dist.argmax() == topic_idx:
                        topic_docs.append(documents[doc_idx][:100] + "...")
                        if len(topic_docs) >= 3:
                            break
                
                topics.append(Topic(
                    id=topic_idx,
                    keywords=keywords,
                    weight=weight,
                    sample_documents=topic_docs
                ))
            
            # Build document-topic mapping
            document_topics = {}
            for doc_idx, topic_dist in enumerate(doc_topics):
                sorted_topics = sorted(enumerate(topic_dist), key=lambda x: x[1], reverse=True)
                document_topics[doc_idx] = [(t[0], float(t[1])) for t in sorted_topics if t[1] > 0.1]
            
            # Calculate coherence (simplified)
            coherence = self._calculate_coherence(topics, documents)
            
            return TopicModelResult(
                topics=topics,
                document_topics=document_topics,
                coherence_score=coherence,
                num_topics=num_topics
            )
            
        except Exception as e:
            logger.error(f"Sklearn LDA failed: {e}")
            return self._fit_keyword_based(documents, num_topics)
    
    def _fit_keyword_based(self, documents: List[str], num_topics: int) -> TopicModelResult:
        """Fit using keyword-based clustering"""
        # Build vocabulary
        all_words = []
        doc_words = []
        
        stop_words = self.STOP_WORDS.get(self.language, self.STOP_WORDS["en"])
        
        for doc in documents:
            words = self._tokenize(doc, stop_words)
            doc_words.append(words)
            all_words.extend(words)
        
        # Calculate word frequencies
        word_freq = Counter(all_words)
        
        # Calculate TF-IDF-like scores
        num_docs = len(documents)
        tfidf_scores = {}
        
        for word, freq in word_freq.items():
            # Document frequency
            df = sum(1 for words in doc_words if word in words)
            # IDF
            idf = math.log(num_docs / (df + 1)) + 1
            # TF-IDF
            tfidf_scores[word] = freq * idf
        
        # Get top keywords
        top_keywords = sorted(tfidf_scores.items(), key=lambda x: x[1], reverse=True)[:num_topics * 10]
        
        # Cluster keywords into topics
        topics = []
        used_keywords = set()
        
        for topic_idx in range(num_topics):
            topic_keywords = []
            topic_weight = 0.0
            
            for word, score in top_keywords:
                if word not in used_keywords and len(topic_keywords) < 10:
                    topic_keywords.append(word)
                    topic_weight += score
                    used_keywords.add(word)
            
            if topic_keywords:
                # Find sample documents
                sample_docs = []
                for doc_idx, words in enumerate(doc_words):
                    if any(kw in words for kw in topic_keywords[:3]):
                        sample_docs.append(documents[doc_idx][:100] + "...")
                        if len(sample_docs) >= 3:
                            break
                
                topics.append(Topic(
                    id=topic_idx,
                    keywords=topic_keywords,
                    weight=topic_weight / sum(tfidf_scores.values()) if tfidf_scores else 0,
                    sample_documents=sample_docs
                ))
        
        # Assign documents to topics
        document_topics = {}
        for doc_idx, words in enumerate(doc_words):
            word_set = set(words)
            topic_scores = []
            
            for topic in topics:
                overlap = len(word_set & set(topic.keywords))
                if overlap > 0:
                    score = overlap / len(topic.keywords)
                    topic_scores.append((topic.id, score))
            
            topic_scores.sort(key=lambda x: x[1], reverse=True)
            document_topics[doc_idx] = topic_scores[:3]
        
        coherence = self._calculate_coherence(topics, documents)
        
        return TopicModelResult(
            topics=topics,
            document_topics=document_topics,
            coherence_score=coherence,
            num_topics=num_topics
        )
    
    def _tokenize(self, text: str, stop_words: set) -> List[str]:
        """Tokenize text and remove stop words"""
        text_lower = text.lower()
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]{3,}\b', text_lower)
        return [w for w in words if w not in stop_words]
    
    def _calculate_coherence(self, topics: List[Topic], documents: List[str]) -> float:
        """Calculate topic coherence score"""
        if not topics:
            return 0.0
        
        total_coherence = 0.0
        
        for topic in topics:
            # Calculate pairwise co-occurrence
            keywords = topic.keywords[:5]
            if len(keywords) < 2:
                continue
            
            co_occurrences = 0
            pairs = 0
            
            for i, w1 in enumerate(keywords):
                for w2 in keywords[i+1:]:
                    pairs += 1
                    for doc in documents:
                        if w1 in doc.lower() and w2 in doc.lower():
                            co_occurrences += 1
                            break
            
            if pairs > 0:
                total_coherence += co_occurrences / pairs
        
        return total_coherence / len(topics) if topics else 0.0
    
    def get_document_topics(
        self,
        document: str,
        result: Optional[TopicModelResult] = None
    ) -> List[Tuple[int, float]]:
        """Get topic distribution for a single document"""
        if self.use_sklearn and self.lda_model and self.vectorizer:
            try:
                doc_vector = self.vectorizer.transform([document])
                topic_dist = self.lda_model.transform(doc_vector)[0]
                return [(i, float(score)) for i, score in enumerate(topic_dist) if score > 0.1]
            except:
                pass
        
        # Keyword-based fallback
        if result is None:
            return []
        
        stop_words = self.STOP_WORDS.get(self.language, self.STOP_WORDS["en"])
        words = set(self._tokenize(document, stop_words))
        
        topic_scores = []
        for topic in result.topics:
            overlap = len(words & set(topic.keywords))
            if overlap > 0:
                score = overlap / len(topic.keywords)
                topic_scores.append((topic.id, score))
        
        topic_scores.sort(key=lambda x: x[1], reverse=True)
        return topic_scores[:3]
    
    def extract_keywords(self, text: str, num_keywords: int = 10) -> List[Tuple[str, float]]:
        """Extract keywords from a single text"""
        stop_words = self.STOP_WORDS.get(self.language, self.STOP_WORDS["en"])
        words = self._tokenize(text, stop_words)
        
        word_freq = Counter(words)
        total_words = len(words)
        
        if total_words == 0:
            return []
        
        keywords = []
        for word, freq in word_freq.most_common(num_keywords * 2):
            # Simple TF score
            tf = freq / total_words
            # Boost longer words
            length_boost = min(len(word) / 8, 1.5)
            score = tf * length_boost
            keywords.append((word, score))
        
        # Normalize scores
        if keywords:
            max_score = max(k[1] for k in keywords)
            keywords = [(k[0], k[1] / max_score) for k in keywords]
        
        return keywords[:num_keywords]
    
    def get_topic_trends(
        self,
        documents: List[str],
        timestamps: List[Any],
        num_topics: int = 5
    ) -> Dict[str, Any]:
        """Analyze topic trends over time"""
        result = self.fit(documents, num_topics)
        
        # Group by timestamp
        time_topic_counts: Dict[Any, Dict[int, int]] = {}
        
        for doc_idx, doc_topics in result.document_topics.items():
            if doc_idx < len(timestamps):
                time = timestamps[doc_idx]
                if time not in time_topic_counts:
                    time_topic_counts[time] = {t.id: 0 for t in result.topics}
                
                for topic_id, _ in doc_topics:
                    time_topic_counts[time][topic_id] += 1
        
        return {
            "topics": [{"id": t.id, "keywords": t.keywords} for t in result.topics],
            "trends": time_topic_counts,
            "num_documents": len(documents)
        }
    
    def label_topics(self, result: TopicModelResult, labels: Dict[int, str]) -> TopicModelResult:
        """Assign human-readable labels to topics"""
        for topic in result.topics:
            if topic.id in labels:
                topic.label = labels[topic.id]
        return result
    
    def find_similar_documents(
        self,
        query: str,
        documents: List[str],
        result: Optional[TopicModelResult] = None,
        top_k: int = 5
    ) -> List[Tuple[int, str, float]]:
        """Find documents similar to query based on topic distribution"""
        if result is None:
            result = self.fit(documents, 5)
        
        query_topics = self.get_document_topics(query, result)
        
        if not query_topics:
            return []
        
        similarities = []
        
        for doc_idx, doc_topics in result.document_topics.items():
            if doc_idx >= len(documents):
                continue
            
            # Calculate topic overlap
            query_topic_ids = {t[0] for t in query_topics}
            doc_topic_ids = {t[0] for t in doc_topics}
            
            overlap = len(query_topic_ids & doc_topic_ids)
            similarity = overlap / len(query_topic_ids) if query_topic_ids else 0
            
            if similarity > 0:
                similarities.append((doc_idx, documents[doc_idx], similarity))
        
        similarities.sort(key=lambda x: x[2], reverse=True)
        return similarities[:top_k]
    
    def get_topic_summary(self, result: TopicModelResult) -> Dict[str, Any]:
        """Get summary statistics for topic model"""
        return {
            "num_topics": result.num_topics,
            "coherence_score": result.coherence_score,
            "topics": [
                {
                    "id": t.id,
                    "label": t.label,
                    "keywords": t.keywords[:5],
                    "weight": t.weight,
                    "num_documents": sum(1 for dt in result.document_topics.values() 
                                        if any(tid == t.id for tid, _ in dt))
                }
                for t in result.topics
            ]
        }
