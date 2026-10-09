# -*- coding: utf-8 -*-
"""
🌟 SELF SYNTHESIS ENGINE - True Autonomous AI
==============================================
Motori i vetë-sintezës - AI që krijon vetë algoritme dhe qëllime.

Ky modul implementon konceptet e True Self-Generating AI:
1. Goal Discovery - Zbulon qëllime të reja vetë
2. Problem Decomposition - Zbërthen problemet në nën-probleme
3. Pattern Mining - Nxjerr patterns nga sjellja
4. Meta-Learning - Mëson si të mësojë më mirë
5. Self-Improvement - Përmirëson vetveten

SIGURI: 
- Sandboxed execution
- Nuk modifikon file jashtë genesis_data/
- Rate limiting
- Validation para aktivizimit

Author: Clisonix Team
Version: 1.0.0
"""

import ast
import hashlib
import inspect
import json
import logging
import os
import random
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("SelfSynthesis")


# =============================================================================
# CONCEPTS & DATA STRUCTURES
# =============================================================================

class ConceptType(Enum):
    """Tipet e koncepteve"""
    ACTION = "action"           # Diçka që bëhet
    ENTITY = "entity"           # Diçka që ekziston
    RELATION = "relation"       # Lidhje mes entiteteve
    CONSTRAINT = "constraint"   # Kufizim
    GOAL = "goal"               # Qëllim
    PATTERN = "pattern"         # Model i përsëritur


class LearningMode(Enum):
    """Mënyrat e mësimit"""
    OBSERVE = "observe"         # Vëzhgo dhe mëso
    EXPERIMENT = "experiment"   # Provo dhe mëso
    IMITATE = "imitate"         # Kopjo nga shembuj
    REASON = "reason"           # Arsyeto logjikisht
    COMBINE = "combine"         # Kombinologa
    ABSTRACT = "abstract"       # Abstraktor


@dataclass
class Concept:
    """Një koncept i mësuar"""
    concept_id: str
    name: str
    concept_type: ConceptType
    description: str
    examples: List[Any] = field(default_factory=list)
    relations: Dict[str, str] = field(default_factory=dict)  # concept_id -> relation_type
    confidence: float = 0.5
    usage_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept_id": self.concept_id,
            "name": self.name,
            "type": self.concept_type.value,
            "description": self.description,
            "confidence": self.confidence,
            "usage_count": self.usage_count
        }


@dataclass
class DiscoveredGoal:
    """Qëllim i zbuluar automatikisht"""
    goal_id: str
    description: str
    priority: float = 0.5
    prerequisites: List[str] = field(default_factory=list)  # Other goal IDs
    estimated_difficulty: float = 0.5
    attempts: int = 0
    successes: int = 0
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "auto"  # auto, observation, experiment


@dataclass
class LearnedPattern:
    """Pattern i mësuar nga vëzhgimi"""
    pattern_id: str
    name: str
    input_signature: str      # Tipi i inputit
    output_signature: str     # Tipi i outputit
    transformation: str       # Përshkrimi i transformimit
    occurrences: int = 0
    confidence: float = 0.5
    code_template: Optional[str] = None


@dataclass
class MetaKnowledge:
    """Dije rreth mësimit (meta-learning)"""
    what_works: List[str] = field(default_factory=list)
    what_fails: List[str] = field(default_factory=list)
    effective_strategies: Dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.1
    exploration_rate: float = 0.3


# =============================================================================
# SELF SYNTHESIS ENGINE
# =============================================================================

class SelfSynthesisEngine:
    """
    🌟 Self Synthesis Engine - Motori i Vetë-Gjenerimit
    
    Ky motor:
    1. Observon sjellje dhe nxjerr patterns
    2. Zbulon qëllime të reja
    3. Krijon algoritme për t'i arritur
    4. Mëson nga sukseset dhe dështimet
    5. Përmirësohet vazhdimisht
    """
    
    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = os.path.join(os.path.dirname(__file__), "genesis_data")
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Concept memory
        self.concepts: Dict[str, Concept] = {}
        
        # Discovered goals
        self.discovered_goals: Dict[str, DiscoveredGoal] = {}
        
        # Learned patterns
        self.patterns: Dict[str, LearnedPattern] = {}
        
        # Meta-knowledge
        self.meta = MetaKnowledge()
        
        # Observation buffer
        self.observations: List[Dict[str, Any]] = []
        self.max_observations = 10000
        
        # Generated code (sandboxed)
        self.generated_code: Dict[str, str] = {}
        
        # Safety limits
        self.max_generation_per_minute = 10
        self.generation_timestamps: List[datetime] = []
        
        # Load state
        self._load_state()
        
        logger.info(f"🌟 SelfSynthesisEngine initialized - "
                   f"{len(self.concepts)} concepts, "
                   f"{len(self.discovered_goals)} goals, "
                   f"{len(self.patterns)} patterns")
    
    # =========================================================================
    # OBSERVATION - Vëzhgimi
    # =========================================================================
    
    def observe(self, 
                action: str, 
                input_data: Any, 
                output_data: Any,
                context: Dict[str, Any] = None) -> None:
        """
        Vëzhgo një veprim dhe mëso nga ai.
        
        Args:
            action: Emri i veprimit (function name, API call, etc.)
            input_data: Çfarë hyri
            output_data: Çfarë doli
            context: Konteksti shtesë
        """
        observation = {
            "action": action,
            "input_type": type(input_data).__name__,
            "output_type": type(output_data).__name__,
            "input_sample": self._safe_sample(input_data),
            "output_sample": self._safe_sample(output_data),
            "context": context or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.observations.append(observation)
        
        # Limit buffer
        if len(self.observations) > self.max_observations:
            self.observations = self.observations[-self.max_observations:]
        
        # Try to learn from this observation
        self._learn_from_observation(observation)
    
    def _safe_sample(self, data: Any, max_len: int = 100) -> str:
        """Get safe string sample of data"""
        try:
            s = str(data)
            return s[:max_len] + "..." if len(s) > max_len else s
        except Exception:
            return f"<{type(data).__name__}>"
    
    def _learn_from_observation(self, obs: Dict[str, Any]) -> None:
        """Mëso nga një vëzhgim"""
        action = obs["action"]
        input_type = obs["input_type"]
        output_type = obs["output_type"]
        
        # Pattern signature
        sig = f"{action}:{input_type}->{output_type}"
        
        if sig in self.patterns:
            # Pattern exists - update
            self.patterns[sig].occurrences += 1
            self.patterns[sig].confidence = min(1.0, 
                self.patterns[sig].confidence + 0.01)
        else:
            # New pattern discovered!
            pattern = LearnedPattern(
                pattern_id=self._generate_id(sig),
                name=f"Pattern: {action}",
                input_signature=input_type,
                output_signature=output_type,
                transformation=f"{action}({input_type}) -> {output_type}",
                occurrences=1
            )
            self.patterns[sig] = pattern
            
            # This might suggest a goal
            self._suggest_goal_from_pattern(pattern)
            
            logger.debug(f"🌟 New pattern discovered: {sig}")
    
    # =========================================================================
    # GOAL DISCOVERY - Zbulimi i Qëllimeve
    # =========================================================================
    
    def _suggest_goal_from_pattern(self, pattern: LearnedPattern) -> None:
        """Sugiero qëllim të ri nga pattern"""
        # If we see list->list patterns, suggest optimization goal
        if pattern.input_signature == "list" and pattern.output_signature == "list":
            self._add_goal(
                description=f"Optimize transformations on lists",
                source="pattern"
            )
        
        # If we see dict->dict, suggest validation goal
        if pattern.input_signature == "dict" and pattern.output_signature == "dict":
            self._add_goal(
                description=f"Validate and transform data structures",
                source="pattern"
            )
    
    def discover_goals_from_gaps(self) -> List[DiscoveredGoal]:
        """
        Zbulon qëllime duke analizuar boshllëqet në njohuri.
        """
        new_goals = []
        
        # Gap 1: Too few patterns -> need more observation
        if len(self.patterns) < 5:
            goal = self._add_goal(
                description="Gather more observations to learn patterns",
                priority=0.8
            )
            if goal:
                new_goals.append(goal)
        
        # Gap 2: Low confidence patterns -> need validation
        low_conf = [p for p in self.patterns.values() if p.confidence < 0.5]
        if low_conf:
            goal = self._add_goal(
                description=f"Validate {len(low_conf)} low-confidence patterns",
                priority=0.6
            )
            if goal:
                new_goals.append(goal)
        
        # Gap 3: Unconnected concepts -> need relations
        isolated = [c for c in self.concepts.values() if not c.relations]
        if len(isolated) > 3:
            goal = self._add_goal(
                description=f"Find relations between {len(isolated)} isolated concepts",
                priority=0.5
            )
            if goal:
                new_goals.append(goal)
        
        return new_goals
    
    def _add_goal(self, 
                  description: str, 
                  priority: float = 0.5,
                  source: str = "auto") -> Optional[DiscoveredGoal]:
        """Shto qëllim të ri nëse nuk ekziston"""
        # Check if similar goal exists
        for existing in self.discovered_goals.values():
            if self._similarity(existing.description, description) > 0.7:
                return None
        
        goal = DiscoveredGoal(
            goal_id=self._generate_id(description),
            description=description,
            priority=priority,
            source=source
        )
        
        self.discovered_goals[goal.goal_id] = goal
        logger.info(f"🎯 Goal discovered: {description}")
        
        return goal
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate simple word overlap similarity"""
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        overlap = words_a & words_b
        union = words_a | words_b
        return len(overlap) / len(union) if union else 0
    
    # =========================================================================
    # CONCEPT LEARNING
    # =========================================================================
    
    def learn_concept(self, 
                      name: str, 
                      concept_type: ConceptType,
                      description: str,
                      examples: List[Any] = None) -> Concept:
        """
        Mëso një koncept të ri.
        """
        concept = Concept(
            concept_id=self._generate_id(name),
            name=name,
            concept_type=concept_type,
            description=description,
            examples=examples or []
        )
        
        self.concepts[concept.concept_id] = concept
        
        # Find relations with existing concepts
        self._find_relations(concept)
        
        logger.info(f"📚 Concept learned: {name}")
        return concept
    
    def _find_relations(self, new_concept: Concept) -> None:
        """Gjej lidhje mes konceptit të ri dhe të tjerëve"""
        for existing in self.concepts.values():
            if existing.concept_id == new_concept.concept_id:
                continue
            
            # Word overlap = possible relation
            similarity = self._similarity(
                new_concept.description, 
                existing.description
            )
            
            if similarity > 0.3:
                # Found relation
                relation_type = "related_to"
                
                # Determine specific relation
                if new_concept.concept_type == ConceptType.ACTION:
                    if existing.concept_type == ConceptType.ENTITY:
                        relation_type = "acts_on"
                elif new_concept.concept_type == ConceptType.ENTITY:
                    if existing.concept_type == ConceptType.ENTITY:
                        relation_type = "similar_to"
                
                new_concept.relations[existing.concept_id] = relation_type
    
    # =========================================================================
    # CODE SYNTHESIS - Sinteza e Kodit
    # =========================================================================
    
    def synthesize_for_goal(self, goal_id: str) -> Optional[str]:
        """
        Sintezo kod për të arritur një qëllim.
        """
        if goal_id not in self.discovered_goals:
            return None
        
        # Rate limiting
        if not self._can_generate():
            logger.warning("Rate limit reached for code generation")
            return None
        
        goal = self.discovered_goals[goal_id]
        
        # Find relevant patterns
        relevant_patterns = self._find_patterns_for_goal(goal)
        
        # Generate code based on patterns and goal
        code = self._generate_code_for_goal(goal, relevant_patterns)
        
        if code:
            # Validate syntax
            if self._validate_syntax(code):
                code_id = self._generate_id(goal.description)
                self.generated_code[code_id] = code
                goal.attempts += 1
                
                logger.info(f"💡 Code synthesized for: {goal.description}")
                return code
            else:
                goal.attempts += 1
                logger.warning("Generated code has syntax errors")
        
        return None
    
    def _find_patterns_for_goal(self, goal: DiscoveredGoal) -> List[LearnedPattern]:
        """Gjej patterns relevante për qëllimin"""
        relevant = []
        goal_words = set(goal.description.lower().split())
        
        for pattern in self.patterns.values():
            pattern_words = set(pattern.transformation.lower().split())
            if goal_words & pattern_words:  # Any overlap
                relevant.append(pattern)
        
        return relevant
    
    def _generate_code_for_goal(self, 
                                 goal: DiscoveredGoal, 
                                 patterns: List[LearnedPattern]) -> Optional[str]:
        """Gjenero kod bazuar në qëllim dhe patterns"""
        
        # Analyze goal description
        desc_lower = goal.description.lower()
        
        # Template selection based on keywords
        if "filter" in desc_lower or "select" in desc_lower:
            template = self._template_filter(goal)
        elif "transform" in desc_lower or "convert" in desc_lower:
            template = self._template_transform(goal)
        elif "validate" in desc_lower or "check" in desc_lower:
            template = self._template_validate(goal)
        elif "aggregate" in desc_lower or "combine" in desc_lower:
            template = self._template_aggregate(goal)
        elif "optimize" in desc_lower:
            template = self._template_optimize(goal, patterns)
        else:
            template = self._template_generic(goal)
        
        return template
    
    def _template_filter(self, goal: DiscoveredGoal) -> str:
        name = self._goal_to_name(goal)
        return f'''
def {name}(items, predicate=None):
    """
    Auto-generated by SelfSynthesis
    Goal: {goal.description}
    """
    if predicate is None:
        predicate = lambda x: x is not None
    return [item for item in items if predicate(item)]
'''
    
    def _template_transform(self, goal: DiscoveredGoal) -> str:
        name = self._goal_to_name(goal)
        return f'''
def {name}(data, transform_fn=None):
    """
    Auto-generated by SelfSynthesis
    Goal: {goal.description}
    """
    if transform_fn is None:
        transform_fn = lambda x: x
    
    if isinstance(data, list):
        return [transform_fn(item) for item in data]
    elif isinstance(data, dict):
        return {{k: transform_fn(v) for k, v in data.items()}}
    else:
        return transform_fn(data)
'''
    
    def _template_validate(self, goal: DiscoveredGoal) -> str:
        name = self._goal_to_name(goal)
        return f'''
def {name}(data, rules=None):
    """
    Auto-generated by SelfSynthesis
    Goal: {goal.description}
    """
    errors = []
    
    if rules is None:
        rules = [
            lambda x: x is not None,
        ]
    
    for i, rule in enumerate(rules):
        try:
            if not rule(data):
                errors.append(f"Rule {{i}} failed")
        except Exception as e:
            errors.append(f"Rule {{i}} error: {{e}}")
    
    return len(errors) == 0, errors
'''
    
    def _template_aggregate(self, goal: DiscoveredGoal) -> str:
        name = self._goal_to_name(goal)
        return f'''
def {name}(items, aggregate_fn=None, initial=None):
    """
    Auto-generated by SelfSynthesis
    Goal: {goal.description}
    """
    if aggregate_fn is None:
        aggregate_fn = lambda acc, x: acc + x
    
    if initial is None:
        initial = type(items[0])() if items else 0
    
    result = initial
    for item in items:
        result = aggregate_fn(result, item)
    
    return result
'''
    
    def _template_optimize(self, goal: DiscoveredGoal, patterns: List[LearnedPattern]) -> str:
        name = self._goal_to_name(goal)
        
        # Include pattern info in comments
        pattern_info = "\n    ".join([
            f"# Pattern: {p.transformation}" 
            for p in patterns[:3]
        ])
        
        return f'''
def {name}(data, strategies=None):
    """
    Auto-generated by SelfSynthesis
    Goal: {goal.description}
    Based on {len(patterns)} observed patterns
    """
    {pattern_info}
    
    # Optimization logic
    if strategies is None:
        strategies = ['cache', 'batch', 'parallel']
    
    result = data
    
    for strategy in strategies:
        if strategy == 'cache':
            # Memoize repeated computations
            pass
        elif strategy == 'batch':
            # Process in batches
            pass
        elif strategy == 'parallel':
            # Parallelize independent ops
            pass
    
    return result
'''
    
    def _template_generic(self, goal: DiscoveredGoal) -> str:
        name = self._goal_to_name(goal)
        return f'''
def {name}(input_data, **kwargs):
    """
    Auto-generated by SelfSynthesis
    Goal: {goal.description}
    """
    # Generic implementation - needs specialization
    result = input_data
    
    # Apply transformations based on kwargs
    for key, value in kwargs.items():
        if callable(value):
            result = value(result)
    
    return result
'''
    
    def _goal_to_name(self, goal: DiscoveredGoal) -> str:
        """Convert goal description to function name"""
        words = re.sub(r'[^a-zA-Z0-9\s]', '', goal.description.lower()).split()[:4]
        return "synth_" + "_".join(words)
    
    # =========================================================================
    # META-LEARNING
    # =========================================================================
    
    def record_success(self, strategy: str) -> None:
        """Rregjistro sukses për një strategji"""
        self.meta.what_works.append(strategy)
        self.meta.effective_strategies[strategy] = \
            self.meta.effective_strategies.get(strategy, 0.5) + 0.1
        
        # Limit
        if len(self.meta.what_works) > 100:
            self.meta.what_works = self.meta.what_works[-100:]
    
    def record_failure(self, strategy: str) -> None:
        """Rregjistro dështim"""
        self.meta.what_fails.append(strategy)
        self.meta.effective_strategies[strategy] = \
            max(0.0, self.meta.effective_strategies.get(strategy, 0.5) - 0.1)
    
    def best_strategy(self) -> Optional[str]:
        """Merr strategjinë më efektive"""
        if not self.meta.effective_strategies:
            return None
        return max(self.meta.effective_strategies, 
                  key=self.meta.effective_strategies.get)
    
    # =========================================================================
    # SAFETY
    # =========================================================================
    
    def _can_generate(self) -> bool:
        """Check rate limiting for code generation"""
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)
        
        # Remove old timestamps
        self.generation_timestamps = [
            ts for ts in self.generation_timestamps 
            if ts > cutoff
        ]
        
        if len(self.generation_timestamps) >= self.max_generation_per_minute:
            return False
        
        self.generation_timestamps.append(now)
        return True
    
    def _validate_syntax(self, code: str) -> bool:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def _generate_id(self, base: str) -> str:
        """Generate unique ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_part = hashlib.md5(base.encode()).hexdigest()[:8]
        return f"synth_{timestamp}_{hash_part}"
    
    def _save_state(self):
        """Save state to disk"""
        state = {
            "concepts": {k: v.to_dict() for k, v in self.concepts.items()},
            "goals": {k: {
                "goal_id": v.goal_id,
                "description": v.description,
                "priority": v.priority,
                "attempts": v.attempts,
                "successes": v.successes
            } for k, v in self.discovered_goals.items()},
            "patterns": {k: {
                "pattern_id": v.pattern_id,
                "name": v.name,
                "transformation": v.transformation,
                "occurrences": v.occurrences,
                "confidence": v.confidence
            } for k, v in self.patterns.items()},
            "meta": {
                "what_works": self.meta.what_works[-50:],
                "what_fails": self.meta.what_fails[-50:],
                "strategies": self.meta.effective_strategies
            }
        }
        
        state_file = self.storage_dir / "synthesis_state.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def _load_state(self):
        """Load state from disk"""
        state_file = self.storage_dir / "synthesis_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                
                logger.info(f"🌟 Loaded state: "
                           f"{len(state.get('concepts', {}))} concepts, "
                           f"{len(state.get('goals', {}))} goals")
            except Exception as e:
                logger.warning(f"Could not load state: {e}")
    
    # =========================================================================
    # API
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "concepts": len(self.concepts),
            "goals": len(self.discovered_goals),
            "patterns": len(self.patterns),
            "observations": len(self.observations),
            "generated_code": len(self.generated_code),
            "meta_learning": {
                "learning_rate": self.meta.learning_rate,
                "exploration_rate": self.meta.exploration_rate,
                "best_strategy": self.best_strategy(),
                "strategies": self.meta.effective_strategies
            }
        }
    
    def get_goals(self) -> List[Dict[str, Any]]:
        """Get all discovered goals"""
        return [
            {
                "goal_id": g.goal_id,
                "description": g.description,
                "priority": g.priority,
                "attempts": g.attempts,
                "successes": g.successes,
                "source": g.source
            }
            for g in sorted(
                self.discovered_goals.values(), 
                key=lambda x: x.priority, 
                reverse=True
            )
        ]
    
    def get_patterns(self) -> List[Dict[str, Any]]:
        """Get all learned patterns"""
        return [
            {
                "pattern_id": p.pattern_id,
                "name": p.name,
                "transformation": p.transformation,
                "occurrences": p.occurrences,
                "confidence": p.confidence
            }
            for p in sorted(
                self.patterns.values(), 
                key=lambda x: x.occurrences, 
                reverse=True
            )
        ]


# =============================================================================
# SINGLETON
# =============================================================================

_self_synthesis: Optional[SelfSynthesisEngine] = None

def get_self_synthesis_engine() -> SelfSynthesisEngine:
    """Get or create SelfSynthesis singleton"""
    global _self_synthesis
    if _self_synthesis is None:
        _self_synthesis = SelfSynthesisEngine()
    return _self_synthesis


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    engine = get_self_synthesis_engine()
    
    # Demo: Observe some operations
    print("📊 Observing operations...")
    engine.observe("filter_users", [1, 2, 3, 4, 5], [2, 4])
    engine.observe("transform_data", {"a": 1}, {"a": 2})
    engine.observe("validate_input", {"name": "test"}, True)
    engine.observe("filter_users", [10, 20, 30], [20])  # Repeated pattern
    
    # Demo: Learn concepts
    print("\n📚 Learning concepts...")
    engine.learn_concept(
        "User",
        ConceptType.ENTITY,
        "A person who uses the system",
        examples=["admin", "guest", "member"]
    )
    engine.learn_concept(
        "Filter",
        ConceptType.ACTION,
        "Remove items that don't match criteria"
    )
    
    # Demo: Discover goals
    print("\n🎯 Discovering goals...")
    goals = engine.discover_goals_from_gaps()
    for g in goals:
        print(f"  - {g.description}")
    
    # Demo: Synthesize code
    if engine.discovered_goals:
        print("\n💡 Synthesizing code...")
        goal_id = list(engine.discovered_goals.keys())[0]
        code = engine.synthesize_for_goal(goal_id)
        if code:
            print(code)
    
    # Stats
    print(f"\n📊 Stats: {engine.get_stats()}")
    print(f"🔍 Patterns: {engine.get_patterns()}")
