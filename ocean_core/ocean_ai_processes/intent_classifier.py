"""
Intent Classifier - Context-aware intent detection
Classifies user intents from text input
Supports custom intent definitions and context tracking
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class IntentResult:
    """Result of intent classification"""
    intent: str
    confidence: float
    parameters: Dict[str, Any]
    alternatives: List[Tuple[str, float]]
    requires_confirmation: bool
    context_used: bool


@dataclass
class IntentContext:
    """Context for multi-turn intent understanding"""
    previous_intents: List[str] = field(default_factory=list)
    entities: Dict[str, Any] = field(default_factory=dict)
    session_start: float = 0.0
    turn_count: int = 0


class IntentClassifier:
    """
    Advanced intent classifier with context awareness
    Supports multi-language intent patterns
    """
    
    # Default intent patterns (English and Albanian)
    INTENT_PATTERNS = {
        "greeting": {
            "patterns": [
                r'\b(?:hi|hello|hey|good\s*(?:morning|afternoon|evening)|greetings)\b',
                r'\b(?:përshëndetje|mirëdita|mirëmbrëma|tungjatjeta|ç\'kemi)\b',  # Albanian
            ],
            "parameters": [],
            "priority": 1,
        },
        "farewell": {
            "patterns": [
                r'\b(?:bye|goodbye|see\s*you|farewell|take\s*care|later)\b',
                r'\b(?:mirupafshim|natën\s*e\s*mirë|prit|kalofsh\s*mirë)\b',  # Albanian
            ],
            "parameters": [],
            "priority": 1,
        },
        "help": {
            "patterns": [
                r'\b(?:help|assist|support|guide|how\s*(?:do|can|to))\b',
                r'\b(?:ndihmë|asistencë|si\s*mund|si\s*ta|më\s*ndihmo)\b',  # Albanian
            ],
            "parameters": [],
            "priority": 2,
        },
        "search": {
            "patterns": [
                r'\b(?:search|find|look\s*(?:for|up)|where\s*is|locate)\b',
                r'\b(?:kërko|gjej|ku\s*(?:është|ndodhet)|lokalizon)\b',  # Albanian
            ],
            "parameters": ["query", "filter"],
            "priority": 3,
        },
        "create": {
            "patterns": [
                r'\b(?:create|make|build|generate|new|add)\b',
                r'\b(?:krijo|bëj|ndërto|gjeneroj|shto|e?\s*re)\b',  # Albanian
            ],
            "parameters": ["type", "name", "options"],
            "priority": 3,
        },
        "update": {
            "patterns": [
                r'\b(?:update|modify|change|edit|alter|fix)\b',
                r'\b(?:përditëso|modifiko|ndrysho|edito|korrigjo)\b',  # Albanian
            ],
            "parameters": ["target", "field", "value"],
            "priority": 3,
        },
        "delete": {
            "patterns": [
                r'\b(?:delete|remove|destroy|eliminate|clear)\b',
                r'\b(?:fshi|hiq|largo|elimino|pastro)\b',  # Albanian
            ],
            "parameters": ["target", "confirmation"],
            "priority": 4,
        },
        "analyze": {
            "patterns": [
                r'\b(?:analyze|analysis|evaluate|assess|examine|review)\b',
                r'\b(?:analizo|analizë|vlerëso|ekzamino|shqyrto)\b',  # Albanian
            ],
            "parameters": ["subject", "type"],
            "priority": 3,
        },
        "query": {
            "patterns": [
                r'\b(?:what|who|when|where|why|how|which|tell\s*me)\b',
                r'\b(?:çfarë|kush|kur|ku|pse|si|cili|më\s*thuaj)\b',  # Albanian
            ],
            "parameters": ["subject"],
            "priority": 2,
        },
        "confirm": {
            "patterns": [
                r'\b(?:yes|yeah|yep|sure|okay|ok|correct|right|affirmative)\b',
                r'\b(?:po|patjetër|sigurisht|dakord|saktë|korrekt)\b',  # Albanian
            ],
            "parameters": [],
            "priority": 1,
        },
        "deny": {
            "patterns": [
                r'\b(?:no|nope|nah|wrong|incorrect|cancel|stop)\b',
                r'\b(?:jo|gabim|pasaktë|anulo|ndalo)\b',  # Albanian
            ],
            "parameters": [],
            "priority": 1,
        },
        "status": {
            "patterns": [
                r'\b(?:status|state|progress|how\s*is|show\s*(?:me)?)\b',
                r'\b(?:statusi|gjendje|progres|si\s*është|ma\s*trego)\b',  # Albanian
            ],
            "parameters": ["target"],
            "priority": 2,
        },
        "navigate": {
            "patterns": [
                r'\b(?:go\s*to|navigate|open|take\s*me|show)\b',
                r'\b(?:shko\s*tek|navigo|hap|më\s*çoj|trego)\b',  # Albanian
            ],
            "parameters": ["destination"],
            "priority": 2,
        },
        "report": {
            "patterns": [
                r'\b(?:report|generate\s*report|summary|statistics|metrics)\b',
                r'\b(?:raport|gjenero\s*raport|përmbledhje|statistika|metrika)\b',  # Albanian
            ],
            "parameters": ["type", "timeframe"],
            "priority": 3,
        },
        "schedule": {
            "patterns": [
                r'\b(?:schedule|plan|set|book|reserve|appointment)\b',
                r'\b(?:planifiko|cakto|rezervo|takim|orari)\b',  # Albanian
            ],
            "parameters": ["action", "time", "date"],
            "priority": 3,
        },
        "compare": {
            "patterns": [
                r'\b(?:compare|versus|vs|difference|between)\b',
                r'\b(?:krahaso|kundrejt|ndryshimi|midis)\b',  # Albanian
            ],
            "parameters": ["item1", "item2"],
            "priority": 3,
        },
    }
    
    # Context-dependent intent mappings
    CONTEXT_RULES = {
        ("greeting", "query"): {"boost": 0.1, "context": "conversation_start"},
        ("search", "confirm"): {"action": "execute_search", "context": "search_pending"},
        ("delete", "confirm"): {"action": "execute_delete", "context": "delete_pending"},
        ("create", "confirm"): {"action": "execute_create", "context": "create_pending"},
    }
    
    def __init__(self, language: str = "en", use_transformers: bool = False):
        self.language = language
        self.use_transformers = use_transformers
        self.custom_intents: Dict[str, Dict] = {}
        self.context = IntentContext()
        self.classifier = None
        
        if use_transformers:
            self._init_transformers()
    
    def _init_transformers(self) -> None:
        """Initialize transformer classifier"""
        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            logger.info("✅ Transformer intent classifier loaded")
        except ImportError:
            logger.warning("⚠️ Transformers not installed, using rule-based")
            self.use_transformers = False
        except Exception as e:
            logger.error(f"❌ Intent classifier loading failed: {e}")
            self.use_transformers = False
    
    def classify(
        self,
        text: str,
        use_context: bool = True,
        extract_params: bool = True
    ) -> IntentResult:
        """
        Classify user intent from text
        
        Args:
            text: User input text
            use_context: Use conversation context
            extract_params: Extract intent parameters
            
        Returns:
            IntentResult with classified intent and parameters
        """
        text_lower = text.lower().strip()
        
        if self.use_transformers and self.classifier:
            result = self._classify_transformers(text_lower)
        else:
            result = self._classify_rule_based(text_lower)
        
        # Apply context
        if use_context and self.context.previous_intents:
            result = self._apply_context(result)
        
        # Extract parameters
        if extract_params:
            result.parameters = self._extract_parameters(text, result.intent)
        
        # Update context
        self.context.previous_intents.append(result.intent)
        if len(self.context.previous_intents) > 5:
            self.context.previous_intents.pop(0)
        self.context.turn_count += 1
        
        return result
    
    def _classify_rule_based(self, text: str) -> IntentResult:
        """Rule-based intent classification"""
        all_intents = {**self.INTENT_PATTERNS, **self.custom_intents}
        
        matches: List[Tuple[str, float, int]] = []
        
        for intent, config in all_intents.items():
            patterns = config.get("patterns", [])
            priority = config.get("priority", 2)
            
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    # Calculate match quality
                    match_length = len(match.group(0))
                    position_bonus = 1.0 - (match.start() / max(len(text), 1)) * 0.2
                    confidence = min((match_length / len(text)) * 2 + position_bonus, 1.0)
                    
                    matches.append((intent, confidence, priority))
                    break  # One match per intent is enough
        
        if not matches:
            return IntentResult(
                intent="unknown",
                confidence=0.0,
                parameters={},
                alternatives=[],
                requires_confirmation=False,
                context_used=False
            )
        
        # Sort by confidence and priority
        matches.sort(key=lambda x: (x[1], -x[2]), reverse=True)
        
        top_intent = matches[0][0]
        top_confidence = matches[0][1]
        
        # Get alternatives
        alternatives = [(m[0], m[1]) for m in matches[1:4]]
        
        # Check if confirmation needed
        requires_confirmation = top_intent in ["delete", "create", "update"] and top_confidence < 0.8
        
        return IntentResult(
            intent=top_intent,
            confidence=top_confidence,
            parameters={},
            alternatives=alternatives,
            requires_confirmation=requires_confirmation,
            context_used=False
        )
    
    def _classify_transformers(self, text: str) -> IntentResult:
        """Transformer-based classification"""
        try:
            all_intents = list(self.INTENT_PATTERNS.keys()) + list(self.custom_intents.keys())
            
            result = self.classifier(text[:256], all_intents, multi_label=False)
            
            scores = dict(zip(result['labels'], result['scores']))
            top_intent = result['labels'][0]
            
            alternatives = [(label, score) for label, score in zip(result['labels'][1:4], result['scores'][1:4])]
            
            requires_confirmation = top_intent in ["delete", "create"] and result['scores'][0] < 0.7
            
            return IntentResult(
                intent=top_intent,
                confidence=result['scores'][0],
                parameters={},
                alternatives=alternatives,
                requires_confirmation=requires_confirmation,
                context_used=False
            )
        except Exception as e:
            logger.error(f"Transformer classification failed: {e}")
            return self._classify_rule_based(text)
    
    def _apply_context(self, result: IntentResult) -> IntentResult:
        """Apply conversation context to improve classification"""
        if not self.context.previous_intents:
            return result
        
        prev_intent = self.context.previous_intents[-1]
        current_intent = result.intent
        
        # Check context rules
        context_key = (prev_intent, current_intent)
        if context_key in self.CONTEXT_RULES:
            rule = self.CONTEXT_RULES[context_key]
            
            if "boost" in rule:
                result.confidence = min(result.confidence + rule["boost"], 1.0)
            
            result.context_used = True
        
        # Confirmation/denial handling
        if current_intent == "confirm" and prev_intent in ["delete", "create", "update"]:
            result.parameters["confirmed_action"] = prev_intent
            result.context_used = True
        elif current_intent == "deny" and prev_intent in ["delete", "create", "update"]:
            result.parameters["cancelled_action"] = prev_intent
            result.context_used = True
        
        return result
    
    def _extract_parameters(self, text: str, intent: str) -> Dict[str, Any]:
        """Extract parameters for the detected intent"""
        params = {}
        
        if intent == "search":
            # Extract search query
            match = re.search(r'(?:search|find|look\s*for)\s+(.+?)(?:\s+in|\s+from|$)', text, re.IGNORECASE)
            if match:
                params["query"] = match.group(1).strip()
        
        elif intent == "create":
            # Extract what to create
            match = re.search(r'(?:create|make|new)\s+(?:a\s+)?(\w+)', text, re.IGNORECASE)
            if match:
                params["type"] = match.group(1)
            
            # Extract name
            name_match = re.search(r'(?:named?|called)\s+["\']?(\w+)["\']?', text, re.IGNORECASE)
            if name_match:
                params["name"] = name_match.group(1)
        
        elif intent == "delete":
            # Extract target
            match = re.search(r'(?:delete|remove)\s+(?:the\s+)?(.+?)(?:\s+from|$)', text, re.IGNORECASE)
            if match:
                params["target"] = match.group(1).strip()
        
        elif intent == "navigate":
            # Extract destination
            match = re.search(r'(?:go\s*to|navigate\s*to|open)\s+(.+?)$', text, re.IGNORECASE)
            if match:
                params["destination"] = match.group(1).strip()
        
        elif intent == "schedule":
            # Extract time/date
            time_match = re.search(r'(?:at|for)\s+(\d{1,2}(?::\d{2})?\s*(?:am|pm)?)', text, re.IGNORECASE)
            if time_match:
                params["time"] = time_match.group(1)
            
            date_match = re.search(r'(?:on|for)\s+(\w+\s+\d{1,2}|\d{1,2}[/-]\d{1,2})', text, re.IGNORECASE)
            if date_match:
                params["date"] = date_match.group(1)
        
        elif intent == "compare":
            # Extract items to compare
            match = re.search(r'compare\s+(.+?)\s+(?:and|vs|versus|with)\s+(.+?)$', text, re.IGNORECASE)
            if match:
                params["item1"] = match.group(1).strip()
                params["item2"] = match.group(2).strip()
        
        return params
    
    def add_intent(
        self,
        name: str,
        patterns: List[str],
        parameters: Optional[List[str]] = None,
        priority: int = 2
    ) -> None:
        """Add a custom intent"""
        self.custom_intents[name] = {
            "patterns": patterns,
            "parameters": parameters or [],
            "priority": priority,
        }
    
    def remove_intent(self, name: str) -> bool:
        """Remove a custom intent"""
        if name in self.custom_intents:
            del self.custom_intents[name]
            return True
        return False
    
    def reset_context(self) -> None:
        """Reset conversation context"""
        self.context = IntentContext()
    
    def get_context(self) -> IntentContext:
        """Get current conversation context"""
        return self.context
    
    def classify_batch(self, texts: List[str]) -> List[IntentResult]:
        """Classify multiple texts"""
        results = []
        for text in texts:
            results.append(self.classify(text))
        return results
    
    def get_available_intents(self) -> List[str]:
        """Get all available intents"""
        return list(self.INTENT_PATTERNS.keys()) + list(self.custom_intents.keys())
    
    def get_intent_info(self, intent: str) -> Optional[Dict]:
        """Get information about an intent"""
        if intent in self.INTENT_PATTERNS:
            return self.INTENT_PATTERNS[intent]
        if intent in self.custom_intents:
            return self.custom_intents[intent]
        return None
