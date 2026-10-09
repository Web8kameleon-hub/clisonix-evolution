"""
QUERY PROCESSOR
===============
Natural Language → Structured Query Processing

Features:
- Intent detection (technical, business, lab, AGI, operational)
- Context building (what data is relevant)
- Policy filtering (appropriate responses)
- Persona (rational, industrial, professional)
- Source weighting (internal > external)
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger("ocean_query_processor")


class QueryIntent(str, Enum):
    """Intent categories for queries"""
    TECHNICAL = "technical"  # Infrastructure, deployment, APIs, architecture
    BUSINESS = "business"  # KPIs, revenue, operations, strategy
    LABORATORY = "laboratory"  # Lab data, experiments, results
    AGENT = "agent"  # ALBA, ALBI, Blerina, AGIEM, ASI status/decisions
    SYSTEM = "system"  # System metrics, health, monitoring
    KNOWLEDGE = "knowledge"  # General knowledge questions
    DATA = "data"  # Data queries, analytics
    UNKNOWN = "unknown"


class DataSourceWeight(str, Enum):
    """Weighting for data sources"""
    CRITICAL = 1.0  # Must have (internal operational data)
    HIGH = 0.9  # Very important (internal metrics)
    MEDIUM = 0.7  # Important (internal historical)
    LOW = 0.5  # Supporting (external knowledge)
    MINIMAL = 0.2  # Background (open source)


@dataclass
class ProcessedQuery:
    """Structured query after processing"""
    original_query: str
    intent: QueryIntent
    keywords: List[str]
    entities: Dict[str, Any]  # Lab names, agent names, etc.
    required_sources: List[str]  # Which data sources to query
    source_weights: Dict[str, float]  # How much to weight each source
    context: Dict[str, Any]  # Additional context
    policy_tags: List[str]  # Security/policy tags
    timestamp: str


class IntentDetector:
    """Detects query intent from natural language"""
    
    # Keyword patterns for each intent
    INTENT_PATTERNS = {
        QueryIntent.TECHNICAL: [
            r'\b(deploy|build|docker|kubernetes|api|endpoint|latency|error|crash)\b',
            r'\b(infrastructure|server|database|cache|load|traffic)\b',
            r'\b(github|ci|cd|pipeline|test|debug)\b',
        ],
        QueryIntent.BUSINESS: [
            r'\b(revenue|cost|profit|kpi|metric|performance|roi)\b',
            r'\b(customer|user|growth|market|strategy|plan)\b',
            r'\b(budget|spending|efficiency|optimization)\b',
        ],
        QueryIntent.LABORATORY: [
            r'\b(labs?|laboratory|lab network|experiment|result|sample|data quality|quality|specialized)\b',
            r'\b(elbasan|tirana|durres|durrës|shkoder|shkodër|vlore|vlorë|korça|sarandë|prishtina|kostur|athens|rome|zurich|beograd|sofia|zagreb|ljubljana|vienna|prague|budapest|bucharest|istanbul|cairo|jerusalem)\b',
            r'\b(research|medical|iot|marine|agricultural|ecological|ai|quantum|security|energy|biotech|nanotechnology|robotics|finance|trade|heritage|archeology|neuroscience|industrial|chemistry|underwater|data science|functions?)\b',
            r'\b(location|domain|university|test|measurement|analysis|geographic)\b',
        ],
        QueryIntent.AGENT: [
            r'\b(alba|albi|blerina|agiem|asi|agent|decision|status|perform|performing)\b',
            r'\b(task|execution|telemetry|confidence|score)\b',
            r'\b(workflow|agi|llm|model)\b',
        ],
        QueryIntent.SYSTEM: [
            r'\b(cpu|memory|disk|monitor|health|uptime|alert|metric|dashboard|system|infrastructure|resource)\b',
            r'\b(performance|availability|latency|error rate)\b',
        ],
        QueryIntent.DATA: [
            r'\b(report|analytics|query|data|statistics|trend|aggregate|sum|count|average|correlation)\b',
        ],
        QueryIntent.KNOWLEDGE: [
            r'\b(how does|how do|what is|what are|explain|definition|meaning|concept)\b',
            r'\b(why|when|where|who)\b',
            r'\b(science|biology|physics|chemistry|mathematics|history|geography|literature|art|music)\b',
        ]
    }
    
    @staticmethod
    def detect(query: str) -> Tuple[QueryIntent, List[str]]:
        """Detect intent and extract keywords"""
        query_lower = query.lower()
        
        # Calculate score for each intent
        intent_scores = {}
        
        for intent, patterns in IntentDetector.INTENT_PATTERNS.items():
            score = 0
            matches = []
            
            for pattern in patterns:
                found = re.findall(pattern, query_lower)
                if found:
                    score += len(found)
                    matches.extend(found)
            
            intent_scores[intent] = (score, matches)
        
        # Get highest scoring intent
        best_intent = max(intent_scores, key=lambda k: intent_scores[k][0])
        
        keywords = list(set(intent_scores[best_intent][1]))
        
        if intent_scores[best_intent][0] == 0:
            best_intent = QueryIntent.UNKNOWN
            keywords = []
        
        logger.debug(f"Detected intent: {best_intent} with keywords: {keywords}")
        return best_intent, keywords


class EntityExtractor:
    """Extracts entities from queries (lab names, agent names, etc.)"""
    
    KNOWN_ENTITIES = {
        "labs": ["elbasan", "tirana", "durres", "shkoder", "vlore", "korca", "sarrande", 
                 "prishtina", "kostur", "athens", "rome", "zurich"],
        "agents": ["alba", "albi", "blerina", "agiem", "asi"],
        "domains": ["university", "medical", "research", "marine", "agricultural", "ecological", "tech"],
        "countries": ["albania", "kosovo", "greece", "italy", "switzerland", "north macedonia"],
    }
    
    @staticmethod
    def extract(query: str) -> Dict[str, List[str]]:
        """Extract known entities from query"""
        query_lower = query.lower()
        entities = {}
        
        for entity_type, entity_list in EntityExtractor.KNOWN_ENTITIES.items():
            found = [e for e in entity_list if e in query_lower]
            if found:
                entities[entity_type] = found
        
        logger.debug(f"Extracted entities: {entities}")
        return entities


class SourceSelector:
    """Selects which data sources to query"""
    
    # Intent → required data sources
    SOURCE_MAPPING = {
        QueryIntent.TECHNICAL: ["system_metrics", "cycle_data", "excel_data"],
        QueryIntent.BUSINESS: ["cycle_data", "excel_data", "system_metrics"],
        QueryIntent.LABORATORY: ["location_labs", "agent_telemetry"],
        QueryIntent.AGENT: ["agent_telemetry", "cycle_data"],
        QueryIntent.SYSTEM: ["system_metrics", "agent_telemetry"],
        QueryIntent.DATA: ["location_labs", "cycle_data", "excel_data"],
        QueryIntent.KNOWLEDGE: [],  # Will use external sources
    }
    
    # Source weighting - internal > external
    SOURCE_WEIGHTS = {
        "location_labs": DataSourceWeight.CRITICAL.value,
        "agent_telemetry": DataSourceWeight.HIGH.value,
        "cycle_data": DataSourceWeight.HIGH.value,
        "system_metrics": DataSourceWeight.MEDIUM.value,
        "excel_data": DataSourceWeight.MEDIUM.value,
        "wikipedia": DataSourceWeight.LOW.value,
        "arxiv": DataSourceWeight.LOW.value,
        "pubmed": DataSourceWeight.LOW.value,
        "github": DataSourceWeight.MINIMAL.value,
    }
    
    @staticmethod
    def select_sources(intent: QueryIntent, entities: Dict[str, List[str]]) -> Tuple[List[str], Dict[str, float]]:
        """Select relevant data sources and their weights"""
        # CRITICAL: Make a COPY of the list to avoid modifying class-level SOURCE_MAPPING
        required_sources = list(SourceSelector.SOURCE_MAPPING.get(intent, []))
        
        # For knowledge questions, also include external sources
        if intent == QueryIntent.KNOWLEDGE:
            required_sources.extend(["wikipedia", "arxiv", "github"])
        elif intent == QueryIntent.UNKNOWN:
            # Include external knowledge sources
            required_sources.extend(["wikipedia"])
        
        # Build weight dict
        weights = {
            source: SourceSelector.SOURCE_WEIGHTS.get(source, 0.5)
            for source in required_sources
        }
        
        logger.debug(f"Selected sources: {required_sources}, weights: {weights}")
        return required_sources, weights


class PolicyFilter:
    """Filters queries and responses based on policies"""
    
    # Prohibited keywords/patterns
    PROHIBITED_PATTERNS = [
        r'\b(password|secret|api.?key|token|credential)\b',
        r'\b(customer.?data|personal|pii|ssn)\b',
    ]
    
    # Tags for sensitive topics
    SENSITIVE_TAGS = {
        "security": [r'\b(password|auth|token|secret)\b'],
        "financial": [r'\b(revenue|profit|cost|budget|salary)\b'],
        "personal": [r'\b(customer|user|employee|personal)\b'],
    }
    
    @staticmethod
    def check_query(query: str) -> Tuple[bool, List[str]]:
        """Check if query is allowed"""
        query_lower = query.lower()
        
        # Check prohibited patterns
        for pattern in PolicyFilter.PROHIBITED_PATTERNS:
            if re.search(pattern, query_lower):
                logger.warning(f"Query blocked - prohibited pattern matched: {pattern}")
                return False, ["restricted"]
        
        # Detect sensitive tags
        tags = []
        for tag, patterns in PolicyFilter.SENSITIVE_TAGS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    tags.append(tag)
                    break
        
        return True, tags
    
    @staticmethod
    def apply_response_policy(response: Dict[str, Any], policy_tags: List[str]) -> Dict[str, Any]:
        """Apply policy filters to response"""
        # For now, just mark sensitive responses
        if policy_tags:
            response["_policy_tags"] = policy_tags
            response["_sensitivity_level"] = "internal"
        
        return response


class QueryProcessor:
    """Central query processor - coordinates all components"""
    
    def __init__(self):
        self.intent_detector = IntentDetector()
        self.entity_extractor = EntityExtractor()
        self.source_selector = SourceSelector()
        self.policy_filter = PolicyFilter()
    
    async def process(self, query: str) -> ProcessedQuery:
        """Process natural language query into structured form"""
        logger.info(f"🔄 Processing query: {query}")
        
        # 1. Check policy
        allowed, policy_tags = self.policy_filter.check_query(query)
        if not allowed:
            raise ValueError("Query violates policy")
        
        # 2. Detect intent
        intent, keywords = self.intent_detector.detect(query)
        
        # 3. Extract entities
        entities = self.entity_extractor.extract(query)
        
        # 4. Select data sources
        required_sources, source_weights = self.source_selector.select_sources(intent, entities)
        
        # 5. Build context
        context = {
            "query_time": datetime.now().isoformat(),
            "entity_count": sum(len(v) for v in entities.values()),
            "source_count": len(required_sources)
        }
        
        # 6. Create processed query
        processed = ProcessedQuery(
            original_query=query,
            intent=intent,
            keywords=keywords,
            entities=entities,
            required_sources=required_sources,
            source_weights=source_weights,
            context=context,
            policy_tags=policy_tags,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Query processed: intent={intent}, sources={required_sources}")
        return processed


# Global singleton
_query_processor: Optional[QueryProcessor] = None


async def get_query_processor() -> QueryProcessor:
    """Get or create global query processor"""
    global _query_processor
    
    if _query_processor is None:
        _query_processor = QueryProcessor()
        logger.info("✅ Query Processor initialized")
    
    return _query_processor
