"""
Autolearning Engine — Continuous learning with self-improvement
Learns from queries, detects patterns, accumulates knowledge
"""

import asyncio
import hashlib
import json
import logging
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Question templates for self-generation
QUESTION_TEMPLATES = [
    "What is {}?",
    "How does {} work?",
    "Explain {}",
    "Why is {} important?",
    "What are the benefits of {}?",
    "Compare {} and {}",
    "What is the difference between {} and {}?",
    "How can I learn {}?",
    "Where can I find {}?",
    "Who invented {}?",
    "When was {} created?",
    "Why do people use {}?",
]

# Topics for auto-generation
LEARNING_TOPICS = [
    "Python", "JavaScript", "machine learning", "blockchain", "cloud computing",
    "Docker", "Kubernetes", "REST APIs", "databases", "cybersecurity",
    "artificial intelligence", "web development", "mobile apps", "devops",
    "microservices", "system design", "data science", "algorithms",
]


@dataclass
class LearnedKnowledge:
    """A unit of learned knowledge"""
    knowledge_id: str
    query: str
    response: str
    sources: List[str]
    confidence: float
    language: str = "en"
    times_used: int = 0
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict:
        return asdict(self)


class AutoLearningEngine:
    """Autonomous learning engine that continuously learns from queries"""

    def __init__(self, memory_dir: str = ".clx/learning"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.knowledge_base: Dict[str, LearnedKnowledge] = {}
        self.patterns: Dict[str, List[str]] = self._init_patterns()
        self.session_queries: List[Dict] = []
        self.learning_active = False

        self._load_knowledge()
        logger.info(f"✅ AutoLearningEngine initialized")
        logger.info(f"   📚 Knowledge entries: {len(self.knowledge_base)}")
        logger.info(f"   🎯 Patterns: {len(self.patterns)}")

    def _init_patterns(self) -> Dict[str, List[str]]:
        """Initialize pattern templates"""
        return {
            "greeting": ["hi", "hello", "hey", "hello there", "hey there", "good morning", "good afternoon", "howdy"],
            "thanks": ["thank you", "thanks", "appreciate it", "much appreciated", "thanks a lot"],
            "affirmation": ["yes", "yep", "yeah", "sure", "of course", "absolutely", "definitely"],
            "negation": ["no", "nope", "no way", "not at all", "never"],
            "help": ["help", "assist", "support", "guide", "explain", "teach"],
            "question": ["?", "what", "how", "why", "when", "where", "who", "which"],
        }

    def _load_knowledge(self):
        """Load persisted knowledge"""
        kb_file = self.memory_dir / "knowledge.json"
        if kb_file.exists():
            try:
                with open(kb_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entry in data:
                        k = LearnedKnowledge(**entry)
                        self.knowledge_base[k.knowledge_id] = k
                logger.info(f"Loaded {len(self.knowledge_base)} knowledge entries")
            except Exception as e:
                logger.warning(f"Could not load knowledge: {e}")

    def _save_knowledge(self):
        """Persist knowledge to disk using atomic write to prevent corruption"""
        kb_file = self.memory_dir / "knowledge.json"
        try:
            import os
            tmp_file = kb_file.with_suffix('.tmp')
            entries = [k.to_dict() for k in self.knowledge_base.values()]
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            tmp_file.replace(kb_file)
        except Exception as e:
            logger.error(f"Could not save knowledge: {e}")

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a query for patterns and cached knowledge

        Returns:
            Dict with pattern_type, pattern_response, cached_knowledge, should_learn
        """
        result = {
            "query": query,
            "pattern_type": None,
            "pattern_response": None,
            "cached_knowledge": None,
            "should_learn": True,
        }

        # Check for pattern matches
        query_lower = query.lower()
        for pattern_type, keywords in self.patterns.items():
            if any(keyword in query_lower for keyword in keywords):
                result["pattern_type"] = pattern_type
                result["pattern_response"] = self._get_pattern_response(pattern_type, query)
                result["should_learn"] = False
                return result

        # Check for cached knowledge (simple keyword matching)
        best_match = None
        best_score = 0.0
        query_words = set(query_lower.split())

        for kb in self.knowledge_base.values():
            kb_words = set(kb.query.lower().split())
            if not query_words or not kb_words:
                continue

            overlap = len(query_words & kb_words)
            score = overlap / max(len(query_words), len(kb_words))

            if score > best_score and score > 0.5:
                best_score = score
                best_match = kb

        if best_match and best_match.confidence > 0.6:
            result["cached_knowledge"] = {
                "knowledge_id": best_match.knowledge_id,
                "response": best_match.response,
                "confidence": best_match.confidence,
                "times_used": best_match.times_used,
            }
            result["should_learn"] = False

        self.session_queries.append(result)
        return result

    def _get_pattern_response(self, pattern_type: str, query: str) -> str:
        """Generate response for pattern matches"""
        responses = {
            "greeting": "👋 Hello! How can I help you today?",
            "thanks": "😊 You're welcome! Anything else?",
            "affirmation": "✅ Great! Let's proceed.",
            "negation": "❌ Understood. What would you prefer?",
            "help": "🤝 I'm here to help. What do you need?",
            "question": "❓ I'm listening. Tell me more.",
        }
        return responses.get(pattern_type, "How can I assist you?")

    async def learn_from_response(
        self,
        query: str,
        response: str,
        sources: List[str],
        confidence: float,
        language: str = "en",
    ) -> str:
        """
        Learn from a query-response pair

        Returns:
            knowledge_id
        """
        # Create knowledge ID
        query_hash = hashlib.md5(query.lower().encode()).hexdigest()
        knowledge_id = f"kb_{query_hash[:8]}_{int(datetime.now().timestamp())}"

        # Create knowledge entry
        knowledge = LearnedKnowledge(
            knowledge_id=knowledge_id,
            query=query,
            response=response,
            sources=sources,
            confidence=confidence,
            language=language,
        )

        self.knowledge_base[knowledge_id] = knowledge
        self._save_knowledge()

        logger.info(f"🧠 Learned: {query[:50]}... (confidence: {confidence:.2f})")
        return knowledge_id

    async def run_learning_loop(self, duration_seconds: int = 4 * 3600):
        """
        Run continuous learning loop
        Generates questions automatically and learns from them
        """
        self.learning_active = True
        start_time = datetime.now(timezone.utc)
        cycle = 0

        logger.info(f"🧠 Starting learning loop ({duration_seconds/3600:.1f}h)")

        while self.learning_active:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            if elapsed > duration_seconds:
                break

            cycle += 1

            # Generate question
            topic = random.choice(LEARNING_TOPICS)
            template = random.choice(QUESTION_TEMPLATES)
            if "{}" in template and template.count("{}") == 2:
                topic2 = random.choice(LEARNING_TOPICS)
                question = template.format(topic, topic2)
            else:
                question = template.format(topic)

            # Simulate learning (in real use, would query data sources)
            logger.debug(f"[Cycle {cycle}] Learning: {question}")

            # Learn it
            await self.learn_from_response(
                query=question,
                response=f"Knowledge about {topic}: This is a complex topic requiring comprehensive understanding.",
                sources=["self-generation"],
                confidence=random.uniform(0.7, 0.95),
                language="en",
            )

            # Brief pause
            await asyncio.sleep(0.5)

        logger.info(f"✅ Learning loop complete ({cycle} cycles)")
        self.learning_active = False

    def stop(self):
        """Stop learning loop"""
        self.learning_active = False

    def get_stats(self) -> Dict[str, Any]:
        """Get learning statistics"""
        return {
            "total_learned": len(self.knowledge_base),
            "avg_confidence": sum(k.confidence for k in self.knowledge_base.values()) / max(1, len(self.knowledge_base)),
            "total_queries_this_session": len(self.session_queries),
            "learning_active": self.learning_active,
        }
