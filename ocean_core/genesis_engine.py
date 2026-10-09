# -*- coding: utf-8 -*-
"""
🧬 GENESIS ENGINE - Self-Generating AI Core
============================================
Motori i vetë-gjenerimit të kodit dhe algoritmeve.

Koncepte:
1. Code Synthesis - Krijon funksione të reja nga patterns
2. Algorithm Evolution - Mutacione + seleksion natyror
3. Self-Testing - Teston para se të pranojë
4. Knowledge Crystallization - Konsolidon mësimet

IZOLUAR PLOTËSISHT - Nuk prek asnjë pjesë tjetër të projektit!

Author: Clisonix Team
Version: 1.0.0
"""

import ast
import atexit
import hashlib
import json
import logging
import os
import random
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Lazy state management - Nanogrid-inspired
try:
    from lazy_state_manager import LazyStateManager
    HAS_LAZY_STATE = True
except ImportError:
    HAS_LAZY_STATE = False

logger = logging.getLogger("GenesisEngine")
logger.setLevel(logging.INFO)


# =============================================================================
# DATA STRUCTURES
# =============================================================================

class EvolutionStrategy(Enum):
    """Strategjitë e evolucionit"""
    MUTATION = "mutation"           # Ndryshime të vogla
    CROSSOVER = "crossover"         # Kombinim i dy gjeneve
    SYNTHESIS = "synthesis"         # Krijim i ri nga zero
    OPTIMIZATION = "optimization"   # Përmirësim i ekzistuesit


class FitnessMetric(Enum):
    """Metrikat për vlerësimin e algoritmeve"""
    SPEED = "speed"                 # Sa shpejt ekzekutohet
    ACCURACY = "accuracy"           # Sa saktë është rezultati
    MEMORY = "memory"               # Sa memorie përdor
    SIMPLICITY = "simplicity"       # Sa i thjeshtë është kodi
    ADAPTABILITY = "adaptability"   # Sa mirë përshtatet


@dataclass
class GeneticCode:
    """Një njësi e kodit gjenetik - funksion/algoritëm"""
    gene_id: str
    name: str
    code: str
    purpose: str
    generation: int = 0
    fitness_scores: Dict[str, float] = field(default_factory=dict)
    parent_ids: List[str] = field(default_factory=list)
    mutations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_tested: Optional[datetime] = None
    test_results: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = False  # Vetëm të testuarat aktivohen
    
    @property
    def fitness(self) -> float:
        """Fitness mesatar"""
        if not self.fitness_scores:
            return 0.0
        return sum(self.fitness_scores.values()) / len(self.fitness_scores)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gene_id": self.gene_id,
            "name": self.name,
            "code": self.code,
            "purpose": self.purpose,
            "generation": self.generation,
            "fitness": self.fitness,
            "fitness_scores": self.fitness_scores,
            "parent_ids": self.parent_ids,
            "mutations": self.mutations,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneticCode':
        """Rindërto GeneticCode nga dict"""
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        else:
            created_at = datetime.now(timezone.utc)
        
        return cls(
            gene_id=data['gene_id'],
            name=data['name'],
            code=data.get('code', ''),
            purpose=data.get('purpose', ''),
            generation=data.get('generation', 0),
            fitness_scores=data.get('fitness_scores', {}),
            parent_ids=data.get('parent_ids', []),
            mutations=data.get('mutations', []),
            created_at=created_at,
            is_active=data.get('is_active', False)
        )


@dataclass
class SynthesisGoal:
    """Qëllim për sintezë automatike"""
    goal_id: str
    description: str
    input_types: List[str]
    output_type: str
    constraints: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    priority: int = 5
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class EvolutionCycle:
    """Një cikël evoluimi"""
    cycle_id: str
    generation: int
    population_size: int
    survivors: int
    best_fitness: float
    avg_fitness: float
    mutations_applied: int
    crossovers: int
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# =============================================================================
# CODE TEMPLATES - Building Blocks
# =============================================================================

CODE_TEMPLATES = {
    "filter": '''
def {name}(items: list, condition) -> list:
    """Filter items based on condition"""
    return [item for item in items if condition(item)]
''',
    
    "transform": '''
def {name}(items: list, transform_fn) -> list:
    """Transform each item"""
    return [transform_fn(item) for item in items]
''',
    
    "aggregate": '''
def {name}(items: list, initial, combine_fn):
    """Aggregate items into single value"""
    result = initial
    for item in items:
        result = combine_fn(result, item)
    return result
''',
    
    "search": '''
def {name}(items: list, target, key_fn=None):
    """Search for target in items"""
    for i, item in enumerate(items):
        value = key_fn(item) if key_fn else item
        if value == target:
            return i
    return -1
''',
    
    "sort": '''
def {name}(items: list, key_fn=None, reverse=False) -> list:
    """Sort items with optional key function"""
    return sorted(items, key=key_fn, reverse=reverse)
''',
    
    "validate": '''
def {name}(data, rules: list) -> tuple:
    """Validate data against rules, return (is_valid, errors)"""
    errors = []
    for rule in rules:
        if not rule(data):
            errors.append(f"Rule {{rule.__name__}} failed")
    return len(errors) == 0, errors
''',
    
    "cache": '''
def {name}(fn):
    """Simple memoization decorator"""
    cache = {{}}
    def wrapper(*args):
        key = str(args)
        if key not in cache:
            cache[key] = fn(*args)
        return cache[key]
    return wrapper
''',
    
    "retry": '''
def {name}(fn, max_attempts=3, delay=1.0):
    """Retry function on failure"""
    import time
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(delay)
''',
    
    "pipeline": '''
def {name}(*functions):
    """Create a pipeline of functions"""
    def execute(data):
        result = data
        for fn in functions:
            result = fn(result)
        return result
    return execute
''',
    
    "batch": '''
def {name}(items: list, batch_size: int):
    """Split items into batches"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]
'''
}


# =============================================================================
# MUTATION OPERATORS
# =============================================================================

MUTATION_OPERATORS = {
    "add_logging": lambda code: code.replace(
        "def ", 
        "def ", 1
    ).replace(
        "return ", 
        "# Genesis: Added logging\n    import logging; logging.debug('Executing...')\n    return ", 1
    ),
    
    "add_timing": lambda code: f'''
import time
_genesis_start = time.time()
{code}
# Genesis: Execution time tracking added
''',
    
    "add_validation": lambda code: code.replace(
        "def ", 
        "def "
    ).replace(
        "return result",
        "assert result is not None, 'Result cannot be None'\n    return result"
    ),
    
    "optimize_loop": lambda code: code.replace(
        "for item in items:",
        "for item in items:  # Genesis: Consider list comprehension"
    ),
    
    "add_docstring": lambda code: code if '"""' in code or "'''" in code else code.replace(
        "def ",
        'def '
    ).replace(
        "):\n",
        '):\n    """Genesis auto-generated function"""\n',
        1
    )
}


# =============================================================================
# GENESIS ENGINE - Main Class
# =============================================================================

class GenesisEngine:
    """
    🧬 Genesis Engine - Self-Generating AI
    
    Ky motor krijon, teston, dhe evoluon algoritme automatikisht.
    Plotësisht i izoluar - nuk modifikon asnjë file tjetër.
    """
    
    def __init__(self, storage_dir: str = None, use_lazy_state: bool = True):
        # Storage brenda ocean-core
        if storage_dir is None:
            storage_dir = os.path.join(os.path.dirname(__file__), "genesis_data")
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Lazy state manager - Nanogrid-inspired!
        self._use_lazy_state = use_lazy_state and HAS_LAZY_STATE
        if self._use_lazy_state:
            state_file = self.storage_dir / "genesis_state.json"
            self._state_manager = LazyStateManager(
                state_file=state_file,
                flush_interval=30.0,      # Flush çdo 30 sekonda
                max_pending_changes=10,   # Ose pas 10 ndryshimeve
                use_fast_json=True
            )
            self._state_manager.start()
            # Cleanup on exit
            atexit.register(self._cleanup)
            logger.info("🚀 Using LazyStateManager for efficient state persistence")
        else:
            self._state_manager = None
        
        # Gene pool - të gjithë algoritmet e krijuar
        self.gene_pool: Dict[str, GeneticCode] = {}
        
        # Active genes - vetëm ato që kanë kaluar testet
        self.active_genes: Dict[str, GeneticCode] = {}
        
        # Synthesis goals - qëllimet për krijim automatik
        self.goals: Dict[str, SynthesisGoal] = {}
        
        # Evolution history
        self.evolution_history: List[EvolutionCycle] = []
        self.current_generation: int = 0
        
        # Test sandbox - ambiente të sigurt për testim
        self.sandbox_globals: Dict[str, Any] = {
            "__builtins__": {
                "len": len, "range": range, "list": list, "dict": dict,
                "str": str, "int": int, "float": float, "bool": bool,
                "sum": sum, "min": min, "max": max, "sorted": sorted,
                "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
                "isinstance": isinstance, "type": type, "print": print,
                "True": True, "False": False, "None": None,
            }
        }
        
        # Load existing data
        self._load_state()
        
        logger.info(f"🧬 GenesisEngine initialized - {len(self.gene_pool)} genes in pool")
    
    def _cleanup(self):
        """Cleanup kur programi mbyllet."""
        if self._state_manager:
            self._state_manager.stop()
    
    # =========================================================================
    # SYNTHESIS - Krijimi i kodit të ri
    # =========================================================================
    
    def synthesize(self, 
                   purpose: str, 
                   template_type: str = None,
                   input_examples: List[Tuple[Any, Any]] = None) -> GeneticCode:
        """
        Krijon një funksion të ri bazuar në qëllimin.
        
        Args:
            purpose: Çfarë duhet të bëjë funksioni
            template_type: Lloji i templateit (filter, transform, etc.)
            input_examples: Lista e (input, expected_output) për testim
        
        Returns:
            GeneticCode: Gjeni i ri
        """
        gene_id = self._generate_id(purpose)
        name = self._generate_name(purpose)
        
        # Zgjidh template
        if template_type and template_type in CODE_TEMPLATES:
            code = CODE_TEMPLATES[template_type].format(name=name)
        else:
            # Auto-detect template from purpose
            code = self._auto_select_template(purpose, name)
        
        # Krijo gjenin
        gene = GeneticCode(
            gene_id=gene_id,
            name=name,
            code=code,
            purpose=purpose,
            generation=self.current_generation
        )
        
        # Testo nëse ka shembuj
        if input_examples:
            test_passed = self._test_gene(gene, input_examples)
            if test_passed:
                gene.is_active = True
                self.active_genes[gene_id] = gene
        
        # Ruaj në pool
        self.gene_pool[gene_id] = gene
        self._save_state()
        
        logger.info(f"🧬 Synthesized: {name} (gen {self.current_generation})")
        return gene
    
    def _auto_select_template(self, purpose: str, name: str) -> str:
        """Zgjedh templatein automatikisht bazuar në qëllim"""
        purpose_lower = purpose.lower()
        
        if any(w in purpose_lower for w in ["filter", "select", "find"]):
            return CODE_TEMPLATES["filter"].format(name=name)
        elif any(w in purpose_lower for w in ["transform", "convert", "map"]):
            return CODE_TEMPLATES["transform"].format(name=name)
        elif any(w in purpose_lower for w in ["sum", "count", "aggregate", "total"]):
            return CODE_TEMPLATES["aggregate"].format(name=name)
        elif any(w in purpose_lower for w in ["search", "locate", "index"]):
            return CODE_TEMPLATES["search"].format(name=name)
        elif any(w in purpose_lower for w in ["sort", "order", "arrange"]):
            return CODE_TEMPLATES["sort"].format(name=name)
        elif any(w in purpose_lower for w in ["validate", "check", "verify"]):
            return CODE_TEMPLATES["validate"].format(name=name)
        elif any(w in purpose_lower for w in ["cache", "memo", "remember"]):
            return CODE_TEMPLATES["cache"].format(name=name)
        elif any(w in purpose_lower for w in ["retry", "attempt"]):
            return CODE_TEMPLATES["retry"].format(name=name)
        elif any(w in purpose_lower for w in ["pipeline", "chain", "compose"]):
            return CODE_TEMPLATES["pipeline"].format(name=name)
        elif any(w in purpose_lower for w in ["batch", "chunk", "split"]):
            return CODE_TEMPLATES["batch"].format(name=name)
        else:
            # Default: simple function
            return f'''
def {name}(data):
    """Genesis: {purpose}"""
    # Auto-generated placeholder
    return data
'''
    
    # =========================================================================
    # MUTATION - Ndryshimet gjenetike
    # =========================================================================
    
    def mutate(self, gene_id: str, mutation_type: str = None) -> Optional[GeneticCode]:
        """
        Apliko mutacion në një gjen.
        
        Args:
            gene_id: ID e gjenit origjinal
            mutation_type: Lloji i mutacionit (ose random)
        
        Returns:
            GeneticCode: Gjeni i mutuar (kopje e re)
        """
        if gene_id not in self.gene_pool:
            logger.warning(f"Gene {gene_id} not found")
            return None
        
        parent = self.gene_pool[gene_id]
        
        # Zgjidh mutacionin
        if mutation_type is None:
            mutation_type = random.choice(list(MUTATION_OPERATORS.keys()))
        
        if mutation_type not in MUTATION_OPERATORS:
            logger.warning(f"Unknown mutation: {mutation_type}")
            return None
        
        # Apliko mutacionin
        try:
            mutated_code = MUTATION_OPERATORS[mutation_type](parent.code)
        except Exception as e:
            logger.error(f"Mutation failed: {e}")
            return None
        
        # Krijo gjenin e ri
        child_id = self._generate_id(f"{parent.name}_mut_{mutation_type}")
        child = GeneticCode(
            gene_id=child_id,
            name=f"{parent.name}_v{parent.generation + 1}",
            code=mutated_code,
            purpose=parent.purpose,
            generation=parent.generation + 1,
            parent_ids=[gene_id],
            mutations=[mutation_type]
        )
        
        self.gene_pool[child_id] = child
        logger.info(f"🧬 Mutation: {parent.name} -> {child.name} ({mutation_type})")
        
        return child
    
    # =========================================================================
    # CROSSOVER - Kombinimi i gjeneve
    # =========================================================================
    
    def crossover(self, gene_id_a: str, gene_id_b: str) -> Optional[GeneticCode]:
        """
        Kombinon dy gjene për të krijuar një të ri.
        """
        if gene_id_a not in self.gene_pool or gene_id_b not in self.gene_pool:
            return None
        
        parent_a = self.gene_pool[gene_id_a]
        parent_b = self.gene_pool[gene_id_b]
        
        # Simple crossover: merge docstrings and combine body
        child_code = f'''
def {parent_a.name}_x_{parent_b.name}(data):
    """
    Genesis Crossover:
    - From {parent_a.name}: {parent_a.purpose}
    - From {parent_b.name}: {parent_b.purpose}
    """
    # Phase 1: Apply parent A logic
    intermediate = data  # {parent_a.name} processing
    
    # Phase 2: Apply parent B logic  
    result = intermediate  # {parent_b.name} processing
    
    return result
'''
        
        child_id = self._generate_id(f"{parent_a.name}_x_{parent_b.name}")
        child = GeneticCode(
            gene_id=child_id,
            name=f"{parent_a.name}_x_{parent_b.name}",
            code=child_code,
            purpose=f"Crossover: {parent_a.purpose} + {parent_b.purpose}",
            generation=max(parent_a.generation, parent_b.generation) + 1,
            parent_ids=[gene_id_a, gene_id_b]
        )
        
        self.gene_pool[child_id] = child
        logger.info(f"🧬 Crossover: {parent_a.name} × {parent_b.name}")
        
        return child
    
    # =========================================================================
    # TESTING - Testimi i sigurt
    # =========================================================================
    
    def _test_gene(self, gene: GeneticCode, test_cases: List[Tuple[Any, Any]]) -> bool:
        """
        Teston gjenin në sandbox të sigurt.
        
        Args:
            gene: Gjeni për testim
            test_cases: Lista e (input, expected_output)
        
        Returns:
            bool: True nëse të gjitha testet kalojnë
        """
        # Validate syntax first
        try:
            ast.parse(gene.code)
        except SyntaxError as e:
            gene.test_results["syntax_error"] = str(e)
            return False
        
        # Execute in sandbox
        sandbox = self.sandbox_globals.copy()
        
        try:
            exec(gene.code, sandbox)
        except Exception as e:
            gene.test_results["exec_error"] = str(e)
            return False
        
        # Find the function
        func = None
        for name, obj in sandbox.items():
            if callable(obj) and not name.startswith("_"):
                func = obj
                break
        
        if func is None:
            gene.test_results["no_function"] = True
            return False
        
        # Run test cases
        passed = 0
        total = len(test_cases)
        
        for i, (input_data, expected) in enumerate(test_cases):
            try:
                start = time.time()
                result = func(input_data)
                elapsed = time.time() - start
                
                if result == expected:
                    passed += 1
                    gene.fitness_scores[f"test_{i}"] = 1.0
                else:
                    gene.fitness_scores[f"test_{i}"] = 0.0
                
                # Speed score
                gene.fitness_scores["speed"] = min(1.0, 0.1 / max(elapsed, 0.001))
                
            except Exception as e:
                gene.test_results[f"test_{i}_error"] = str(e)
                gene.fitness_scores[f"test_{i}"] = 0.0
        
        gene.last_tested = datetime.now(timezone.utc)
        gene.test_results["passed"] = passed
        gene.test_results["total"] = total
        gene.test_results["success_rate"] = passed / total if total > 0 else 0
        
        return passed == total
    
    def test_all(self, test_suite: Dict[str, List[Tuple[Any, Any]]]) -> Dict[str, bool]:
        """Teston të gjitha gjenet aktive me test suite"""
        results = {}
        for gene_id, gene in self.active_genes.items():
            if gene_id in test_suite:
                results[gene_id] = self._test_gene(gene, test_suite[gene_id])
        return results
    
    # =========================================================================
    # EVOLUTION CYCLE - Cikli i evoluimit
    # =========================================================================
    
    def evolve(self, 
               population_size: int = 20,
               survivors: int = 5,
               mutation_rate: float = 0.3,
               crossover_rate: float = 0.2) -> EvolutionCycle:
        """
        Ekzekuton një cikël të plotë evoluimi.
        
        1. Vlerëso fitness të të gjithëve
        2. Selekto më të mirët
        3. Apliko mutacione
        4. Bëj crossover
        5. Zëvendëso më të dobëtit
        """
        self.current_generation += 1
        
        # Get all genes sorted by fitness
        all_genes = list(self.gene_pool.values())
        all_genes.sort(key=lambda g: g.fitness, reverse=True)
        
        # Select survivors
        survivor_genes = all_genes[:survivors]
        
        mutations_count = 0
        crossovers_count = 0
        
        # Apply mutations
        for gene in survivor_genes:
            if random.random() < mutation_rate:
                self.mutate(gene.gene_id)
                mutations_count += 1
        
        # Crossover
        if len(survivor_genes) >= 2:
            for _ in range(int(len(survivor_genes) * crossover_rate)):
                parent_a, parent_b = random.sample(survivor_genes, 2)
                self.crossover(parent_a.gene_id, parent_b.gene_id)
                crossovers_count += 1
        
        # Calculate stats
        fitnesses = [g.fitness for g in all_genes if g.fitness > 0]
        
        cycle = EvolutionCycle(
            cycle_id=f"gen_{self.current_generation}",
            generation=self.current_generation,
            population_size=len(self.gene_pool),
            survivors=len(survivor_genes),
            best_fitness=max(fitnesses) if fitnesses else 0,
            avg_fitness=sum(fitnesses) / len(fitnesses) if fitnesses else 0,
            mutations_applied=mutations_count,
            crossovers=crossovers_count
        )
        
        self.evolution_history.append(cycle)
        self._save_state()
        
        logger.info(f"🧬 Evolution Gen {self.current_generation}: "
                   f"pop={len(self.gene_pool)}, best={cycle.best_fitness:.2f}")
        
        return cycle
    
    # =========================================================================
    # GOAL-DRIVEN SYNTHESIS
    # =========================================================================
    
    def add_goal(self, 
                 description: str,
                 input_types: List[str],
                 output_type: str,
                 examples: List[Dict[str, Any]] = None) -> SynthesisGoal:
        """
        Shto një qëllim për sintezë automatike.
        Sistemi do tentojë të krijojë algoritme që e plotësojnë.
        """
        goal_id = self._generate_id(description)
        
        goal = SynthesisGoal(
            goal_id=goal_id,
            description=description,
            input_types=input_types,
            output_type=output_type,
            examples=examples or []
        )
        
        self.goals[goal_id] = goal
        self._save_state()
        
        logger.info(f"🎯 Goal added: {description}")
        return goal
    
    def pursue_goals(self) -> List[GeneticCode]:
        """
        Tento të krijosh algoritme për të gjitha qëllimet.
        """
        created = []
        
        for goal in self.goals.values():
            # Convert examples to test cases
            test_cases = []
            for ex in goal.examples:
                if "input" in ex and "output" in ex:
                    test_cases.append((ex["input"], ex["output"]))
            
            # Synthesize
            gene = self.synthesize(
                purpose=goal.description,
                input_examples=test_cases if test_cases else None
            )
            created.append(gene)
        
        return created
    
    # =========================================================================
    # UTILITY
    # =========================================================================
    
    def _generate_id(self, base: str) -> str:
        """Gjenero ID unike"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        hash_part = hashlib.md5(base.encode()).hexdigest()[:8]
        return f"gene_{timestamp}_{hash_part}"
    
    def _generate_name(self, purpose: str) -> str:
        """Gjenero emër funksioni nga qëllimi"""
        # Clean and convert to snake_case
        name = re.sub(r'[^a-zA-Z0-9\s]', '', purpose.lower())
        name = '_'.join(name.split()[:4])  # First 4 words
        return f"genesis_{name}" or "genesis_func"
    
    def _save_state(self):
        """Ruaj gjendjen në disk - Nanogrid lazy pattern!"""
        state = {
            "generation": self.current_generation,
            "gene_pool": {k: v.to_dict() for k, v in self.gene_pool.items()},
            "active_genes": list(self.active_genes.keys()),
            "goals": {k: {
                "goal_id": v.goal_id,
                "description": v.description,
                "input_types": v.input_types,
                "output_type": v.output_type
            } for k, v in self.goals.items()}
        }
        
        if self._use_lazy_state and self._state_manager:
            # Lazy save - bufferit në memory, flusho periodikisht
            self._state_manager.update_bulk(state)
        else:
            # Fallback - direct save (slower)
            state_file = self.storage_dir / "genesis_state.json"
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
    
    def _load_state(self):
        """Ngarko gjendjen nga disku"""
        state = {}
        
        if self._use_lazy_state and self._state_manager:
            # Load via lazy manager
            loaded = self._state_manager.load()
            if loaded:
                state = self._state_manager.get_all()
        else:
            # Fallback - direct load
            state_file = self.storage_dir / "genesis_state.json"
            if state_file.exists():
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not load state: {e}")
        
        if state:
            try:
                self.current_generation = state.get("generation", 0)
                
                # Reconstruct gene_pool from saved state
                gene_pool_data = state.get("gene_pool", {})
                for gene_id, gene_data in gene_pool_data.items():
                    try:
                        gene = GeneticCode.from_dict(gene_data)
                        self.gene_pool[gene_id] = gene
                        if gene.is_active:
                            self.active_genes[gene_id] = gene
                    except Exception as e:
                        logger.warning(f"Could not restore gene {gene_id}: {e}")
                
                # Reconstruct goals
                goals_data = state.get("goals", {})
                for goal_id, goal_data in goals_data.items():
                    try:
                        self.goals[goal_id] = SynthesisGoal(
                            goal_id=goal_data['goal_id'],
                            description=goal_data['description'],
                            input_types=goal_data.get('input_types', []),
                            output_type=goal_data.get('output_type', 'any')
                        )
                    except Exception as e:
                        logger.warning(f"Could not restore goal {goal_id}: {e}")
                
                logger.info(f"🧬 Loaded state: generation {self.current_generation}, {len(self.gene_pool)} genes")
            except Exception as e:
                logger.warning(f"Could not process state: {e}")
    
    def get_state_stats(self) -> Dict[str, Any]:
        """Statistikat e LazyStateManager"""
        if self._use_lazy_state and self._state_manager:
            return self._state_manager.get_stats()
        return {"mode": "direct_save", "lazy_state": False}
    
    # =========================================================================
    # API
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistikat e motorit"""
        return {
            "generation": self.current_generation,
            "total_genes": len(self.gene_pool),
            "active_genes": len(self.active_genes),
            "goals": len(self.goals),
            "evolution_cycles": len(self.evolution_history),
            "templates_available": list(CODE_TEMPLATES.keys()),
            "mutation_operators": list(MUTATION_OPERATORS.keys())
        }
    
    def get_best_genes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Merr gjenet më të mirë sipas fitness"""
        sorted_genes = sorted(
            self.gene_pool.values(),
            key=lambda g: g.fitness,
            reverse=True
        )
        return [g.to_dict() for g in sorted_genes[:limit]]
    
    def execute_gene(self, gene_id: str, input_data: Any) -> Any:
        """Ekzekuto një gjen me input të dhënë"""
        if gene_id not in self.active_genes:
            raise ValueError(f"Gene {gene_id} not active or not found")
        
        gene = self.active_genes[gene_id]
        
        # Execute in sandbox
        sandbox = self.sandbox_globals.copy()
        exec(gene.code, sandbox)
        
        # Find and call function
        for name, obj in sandbox.items():
            if callable(obj) and not name.startswith("_"):
                return obj(input_data)
        
        raise RuntimeError("No executable function found")


# =============================================================================
# SINGLETON
# =============================================================================

_genesis_engine: Optional[GenesisEngine] = None

def get_genesis_engine() -> GenesisEngine:
    """Get or create Genesis Engine singleton"""
    global _genesis_engine
    if _genesis_engine is None:
        _genesis_engine = GenesisEngine()
    return _genesis_engine


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    engine = get_genesis_engine()
    
    # Demo: Create a filter function
    gene1 = engine.synthesize(
        purpose="Filter even numbers from a list",
        template_type="filter",
        input_examples=[
            ([1, 2, 3, 4, 5, 6], [2, 4, 6]),
        ]
    )
    print(f"Created: {gene1.name}")
    
    # Demo: Create a transform function
    gene2 = engine.synthesize(
        purpose="Transform numbers by doubling them",
        template_type="transform"
    )
    print(f"Created: {gene2.name}")
    
    # Demo: Mutate
    mutated = engine.mutate(gene1.gene_id, "add_logging")
    if mutated:
        print(f"Mutated: {mutated.name}")
    
    # Demo: Evolve
    cycle = engine.evolve()
    print(f"Evolution: {cycle}")
    
    # Stats
    print(f"\n📊 Stats: {engine.get_stats()}")
