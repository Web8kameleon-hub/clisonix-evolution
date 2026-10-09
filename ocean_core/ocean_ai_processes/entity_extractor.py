"""
Entity Extractor - Named Entity Recognition (NER)
Extracts people, organizations, locations, dates, and custom entities
Supports multiple languages including Albanian
"""

import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents an extracted entity"""
    text: str
    type: str  # PERSON, ORGANIZATION, LOCATION, DATE, TIME, MONEY, PERCENT, CUSTOM
    confidence: float
    start_pos: int
    end_pos: int
    normalized_value: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionResult:
    """Result of entity extraction"""
    entities: List[Entity]
    text: str
    language: str
    entity_counts: Dict[str, int]
    processing_time: float


class EntityExtractor:
    """
    Advanced Named Entity Recognition
    Supports multiple languages and custom entity types
    """
    
    # Entity type categories
    ENTITY_TYPES = {
        "PERSON": ["mr", "ms", "mrs", "dr", "prof", "sen", "rep", "president", "ceo", "founder", 
                   "director", "manager", "chief", "chairman", "minister"],
        "ORGANIZATION": ["inc", "corp", "llc", "ltd", "co", "company", "university", "institute", 
                        "association", "foundation", "hospital", "bank", "group", "corporation"],
        "LOCATION": ["city", "town", "village", "state", "country", "continent", "region", 
                    "mountain", "river", "street", "avenue", "park", "island"],
        "DATE": ["january", "february", "march", "april", "may", "june", "july", "august", 
                "september", "october", "november", "december", "monday", "tuesday", 
                "wednesday", "thursday", "friday", "saturday", "sunday"],
        "CURRENCY": ["$", "€", "£", "¥", "usd", "eur", "gbp", "jpy", "dollar", "euro", "pound", "lek"],
        "PERCENT": ["%", "percent", "percentage"],
    }
    
    # Albanian-specific entities
    ALBANIAN_ENTITIES = {
        "cities": ["tiranë", "tirana", "durrës", "vlorë", "shkodër", "elbasan", "korçë", 
                  "fier", "berat", "lushnjë", "pogradec", "kavajë", "gjirokastër", "sarandë"],
        "organizations": ["universiteti", "ministria", "bashkia", "qeveria", "parlamenti"],
        "titles": ["zoti", "zonja", "dr", "prof", "ing", "av"]
    }
    
    def __init__(self, language: str = "en", use_spacy: bool = False):
        self.language = language
        self.use_spacy = use_spacy
        self.custom_patterns: List[Dict] = []
        self.nlp = None
        
        if use_spacy:
            self._init_spacy()
    
    def _init_spacy(self) -> None:
        """Initialize spaCy model"""
        try:
            import spacy
            model_map = {"en": "en_core_web_sm", "sq": "xx_ent_wiki_sm", "de": "de_core_news_sm"}
            model = model_map.get(self.language, "xx_ent_wiki_sm")
            
            try:
                self.nlp = spacy.load(model)
            except OSError:
                logger.warning(f"⚠️ Spacy model {model} not found, downloading...")
                spacy.cli.download(model)
                self.nlp = spacy.load(model)
            
            logger.info(f"✅ Spacy NER loaded for {self.language}")
        except ImportError:
            logger.warning("⚠️ Spacy not installed, using rule-based")
            self.use_spacy = False
        except Exception as e:
            logger.error(f"❌ Spacy loading failed: {e}")
            self.use_spacy = False
    
    def extract(self, text: str, language: Optional[str] = None) -> ExtractionResult:
        """
        Extract entities from text
        
        Args:
            text: Text to extract entities from
            language: Language code (overrides default)
            
        Returns:
            ExtractionResult with entities and metadata
        """
        start_time = time.time()
        lang = language or self.language
        
        if self.use_spacy and self.nlp:
            entities = self._extract_spacy(text)
        else:
            entities = self._extract_rule_based(text, lang)
        
        # Add custom pattern matches
        entities.extend(self._extract_custom_patterns(text))
        
        # Remove duplicates (keep highest confidence)
        entities = self._deduplicate_entities(entities)
        
        # Count by type
        entity_counts = {}
        for entity in entities:
            entity_counts[entity.type] = entity_counts.get(entity.type, 0) + 1
        
        processing_time = time.time() - start_time
        
        return ExtractionResult(
            entities=entities,
            text=text,
            language=lang,
            entity_counts=entity_counts,
            processing_time=processing_time
        )
    
    def _extract_spacy(self, text: str) -> List[Entity]:
        """Extract entities using Spacy"""
        entities = []
        doc = self.nlp(text[:100000])  # Limit text length
        
        for ent in doc.ents:
            entities.append(Entity(
                text=ent.text,
                type=ent.label_,
                confidence=1.0,
                start_pos=ent.start_char,
                end_pos=ent.end_char,
                metadata={"source": "spacy"}
            ))
        
        return entities
    
    def _extract_rule_based(self, text: str, language: str) -> List[Entity]:
        """Extract entities using rule-based patterns"""
        entities = []
        
        # Extract different entity types
        entities.extend(self._extract_dates(text))
        entities.extend(self._extract_money(text))
        entities.extend(self._extract_percentages(text))
        entities.extend(self._extract_proper_nouns(text, language))
        entities.extend(self._extract_emails_urls(text))
        
        return entities
    
    def _extract_dates(self, text: str) -> List[Entity]:
        """Extract date entities"""
        entities = []
        
        # Pattern: Month Day, Year
        pattern1 = r'\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+(\d{1,2})(?:st|nd|rd|th)?,?\s*(\d{4})\b'
        for match in re.finditer(pattern1, text, re.IGNORECASE):
            entities.append(Entity(
                text=match.group(0),
                type="DATE",
                confidence=0.95,
                start_pos=match.start(),
                end_pos=match.end(),
                normalized_value=match.group(0),
                metadata={"format": "month_day_year"}
            ))
        
        # Pattern: YYYY-MM-DD
        pattern2 = r'\b(\d{4})-(\d{2})-(\d{2})\b'
        for match in re.finditer(pattern2, text):
            entities.append(Entity(
                text=match.group(0),
                type="DATE",
                confidence=0.98,
                start_pos=match.start(),
                end_pos=match.end(),
                normalized_value=match.group(0),
                metadata={"format": "iso"}
            ))
        
        # Pattern: DD/MM/YYYY or MM/DD/YYYY
        pattern3 = r'\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b'
        for match in re.finditer(pattern3, text):
            entities.append(Entity(
                text=match.group(0),
                type="DATE",
                confidence=0.85,
                start_pos=match.start(),
                end_pos=match.end(),
                metadata={"format": "numeric"}
            ))
        
        return entities
    
    def _extract_money(self, text: str) -> List[Entity]:
        """Extract monetary amounts"""
        entities = []
        
        # Pattern: $1,234.56 or €1234 or 1234 USD
        patterns = [
            (r'\$\s*[\d,]+(?:\.\d{2})?', "USD"),
            (r'€\s*[\d,]+(?:\.\d{2})?', "EUR"),
            (r'£\s*[\d,]+(?:\.\d{2})?', "GBP"),
            (r'¥\s*[\d,]+', "JPY"),
            (r'[\d,]+(?:\.\d{2})?\s*(?:USD|EUR|GBP|JPY|ALL|LEK)', None),
        ]
        
        for pattern, currency in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append(Entity(
                    text=match.group(0),
                    type="MONEY",
                    confidence=0.92,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    metadata={"currency": currency}
                ))
        
        return entities
    
    def _extract_percentages(self, text: str) -> List[Entity]:
        """Extract percentage values"""
        entities = []
        
        pattern = r'\b(\d+(?:\.\d+)?)\s*(?:%|percent|përqind)\b'
        for match in re.finditer(pattern, text, re.IGNORECASE):
            entities.append(Entity(
                text=match.group(0),
                type="PERCENT",
                confidence=0.95,
                start_pos=match.start(),
                end_pos=match.end(),
                normalized_value=float(match.group(1)),
                metadata={}
            ))
        
        return entities
    
    def _extract_proper_nouns(self, text: str, language: str) -> List[Entity]:
        """Extract proper nouns (potential names, organizations, locations)"""
        entities = []
        
        # Find sequences of capitalized words
        pattern = r'\b[A-Z][a-zA-ZÀ-ÿ]*(?:\s+[A-Z][a-zA-ZÀ-ÿ]*)+\b'
        
        for match in re.finditer(pattern, text):
            entity_text = match.group(0)
            
            # Skip if at start of sentence (might just be regular capitalization)
            if match.start() > 0 and text[match.start()-1] not in '.!?\n':
                # Determine entity type
                entity_type = self._determine_type(entity_text, text, language)
                confidence = self._calculate_confidence(entity_text, entity_type)
                
                if confidence > 0.4:
                    entities.append(Entity(
                        text=entity_text,
                        type=entity_type,
                        confidence=confidence,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        metadata={"source": "proper_noun"}
                    ))
        
        # Also extract single capitalized words that look like entities
        single_pattern = r'\b[A-Z][a-zA-ZÀ-ÿ]{2,}\b'
        for match in re.finditer(single_pattern, text):
            entity_text = match.group(0)
            
            # Check against known entities
            if language == "sq":
                for category, words in self.ALBANIAN_ENTITIES.items():
                    if entity_text.lower() in words:
                        type_map = {"cities": "LOCATION", "organizations": "ORGANIZATION", "titles": "PERSON"}
                        entities.append(Entity(
                            text=entity_text,
                            type=type_map.get(category, "MISC"),
                            confidence=0.85,
                            start_pos=match.start(),
                            end_pos=match.end(),
                            metadata={"category": category}
                        ))
        
        return entities
    
    def _extract_emails_urls(self, text: str) -> List[Entity]:
        """Extract emails and URLs"""
        entities = []
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            entities.append(Entity(
                text=match.group(0),
                type="EMAIL",
                confidence=0.98,
                start_pos=match.start(),
                end_pos=match.end(),
                metadata={}
            ))
        
        # URL pattern
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        for match in re.finditer(url_pattern, text):
            entities.append(Entity(
                text=match.group(0),
                type="URL",
                confidence=0.98,
                start_pos=match.start(),
                end_pos=match.end(),
                metadata={}
            ))
        
        return entities
    
    def _determine_type(self, entity_text: str, context: str, language: str) -> str:
        """Determine entity type based on context and patterns"""
        entity_lower = entity_text.lower()
        
        # Check against known indicators
        for entity_type, indicators in self.ENTITY_TYPES.items():
            if any(indicator in entity_lower for indicator in indicators):
                return entity_type
        
        # Check Albanian entities
        if language == "sq":
            for category, words in self.ALBANIAN_ENTITIES.items():
                if any(word in entity_lower for word in words):
                    type_map = {"cities": "LOCATION", "organizations": "ORGANIZATION", "titles": "PERSON"}
                    return type_map.get(category, "MISC")
        
        # Context-based detection
        context_lower = context.lower()
        
        # Location indicators
        if any(ind in context_lower for ind in ["in ", "from ", "at ", "near ", "to "]):
            idx = context_lower.find(entity_lower)
            if idx > 0 and context_lower[idx-4:idx].strip() in ["in", "from", "at", "near", "to"]:
                return "LOCATION"
        
        # Default to PERSON if it looks like a name (2-3 capitalized words)
        if len(entity_text.split()) <= 3 and entity_text[0].isupper():
            return "PERSON"
        
        return "MISC"
    
    def _calculate_confidence(self, entity_text: str, entity_type: str) -> float:
        """Calculate confidence score for extracted entity"""
        confidence = 0.5  # Base confidence
        
        # Multi-word entities are more reliable
        word_count = len(entity_text.split())
        if word_count >= 2:
            confidence += min(word_count * 0.1, 0.25)
        
        # Specific types get boost
        if entity_type in ["PERSON", "ORGANIZATION", "LOCATION"]:
            confidence += 0.15
        
        # Known entity types are more confident
        if entity_type not in ["MISC", "CUSTOM"]:
            confidence += 0.1
        
        return min(max(confidence, 0.2), 0.95)
    
    def _extract_custom_patterns(self, text: str) -> List[Entity]:
        """Extract entities using custom patterns"""
        entities = []
        
        for pattern_config in self.custom_patterns:
            pattern = pattern_config.get("pattern", "")
            entity_type = pattern_config.get("type", "CUSTOM")
            confidence = pattern_config.get("confidence", 0.8)
            
            for match in re.finditer(pattern, text):
                entities.append(Entity(
                    text=match.group(0),
                    type=entity_type,
                    confidence=confidence,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    metadata={"custom": True}
                ))
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities, keeping highest confidence"""
        unique_entities = {}
        
        for entity in entities:
            key = f"{entity.text}_{entity.type}_{entity.start_pos}"
            if key not in unique_entities or unique_entities[key].confidence < entity.confidence:
                unique_entities[key] = entity
        
        return list(unique_entities.values())
    
    def add_custom_pattern(self, pattern: str, entity_type: str, confidence: float = 0.8) -> None:
        """Add custom extraction pattern"""
        self.custom_patterns.append({
            "pattern": pattern,
            "type": entity_type,
            "confidence": confidence
        })
    
    def extract_batch(self, texts: List[str]) -> List[ExtractionResult]:
        """Extract entities from multiple texts"""
        return [self.extract(text) for text in texts]
    
    def get_entity_network(self, texts: List[str]) -> Dict[str, Any]:
        """Build entity co-occurrence network"""
        all_entities = []
        
        for text in texts:
            result = self.extract(text)
            all_entities.extend(result.entities)
        
        # Count entity frequencies
        freq = {}
        for entity in all_entities:
            key = entity.text
            freq[key] = freq.get(key, 0) + 1
        
        # Build co-occurrence (entities appearing in same text)
        cooccurrence = {}
        for text in texts:
            result = self.extract(text)
            entities = [e.text for e in result.entities]
            
            for i, e1 in enumerate(entities):
                for e2 in entities[i+1:]:
                    if e1 != e2:
                        pair = tuple(sorted([e1, e2]))
                        cooccurrence[pair] = cooccurrence.get(pair, 0) + 1
        
        return {
            "entities": list(freq.keys()),
            "frequencies": freq,
            "cooccurrence": {f"{p[0]}|{p[1]}": c for p, c in cooccurrence.items()},
            "total_entities": len(all_entities)
        }
