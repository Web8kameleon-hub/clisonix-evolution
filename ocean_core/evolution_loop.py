# -*- coding: utf-8 -*-
"""
🔄 EVOLUTION LOOP - Autonomous Evolution Daemon
================================================
Cikli i vazhdueshëm i evoluimit që punon në background.

Ky modul:
1. Monitoron performancën e gjeneve
2. Ekzekuton evolucione periodike
3. Krijon gjene të reja kur nevojitet
4. Eliminon gjenet e dobëta
5. Optimizon popullatën automatikisht

IZOLUAR PLOTËSISHT - Nuk prek asnjë pjesë tjetër!

Author: Clisonix Team
Version: 1.0.0
"""

import asyncio
import logging
import random
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from genesis_engine import EvolutionCycle, EvolutionStrategy, GenesisEngine, GeneticCode, get_genesis_engine

logger = logging.getLogger("EvolutionLoop")


class LoopState(Enum):
    """Gjendja e loop-it"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    EVOLVING = "evolving"


@dataclass
class EvolutionConfig:
    """Konfiguracioni i evoluimit"""
    population_target: int = 50          # Target population size
    min_population: int = 10             # Minimum genes to keep
    max_population: int = 200            # Maximum before pruning
    evolution_interval: int = 300        # Seconds between evolutions
    mutation_rate: float = 0.3           # Probability of mutation
    crossover_rate: float = 0.2          # Probability of crossover
    survival_threshold: float = 0.3      # Minimum fitness to survive
    auto_synthesis: bool = True          # Auto-create new genes
    auto_prune: bool = True              # Auto-remove weak genes
    diversity_bonus: float = 0.1         # Bonus for unique genes


@dataclass
class LoopMetrics:
    """Metrikat e loop-it"""
    total_cycles: int = 0
    total_mutations: int = 0
    total_crossovers: int = 0
    total_synthesized: int = 0
    total_pruned: int = 0
    best_fitness_ever: float = 0.0
    avg_fitness_history: List[float] = field(default_factory=list)
    uptime_seconds: float = 0.0
    last_evolution: Optional[datetime] = None


class EvolutionLoop:
    """
    🔄 Evolution Loop - Daemon i Evoluimit Autonom
    
    Punon në background dhe evoluon popullatën e gjeneve automatikisht.
    """
    
    def __init__(self, 
                 engine: GenesisEngine = None,
                 config: EvolutionConfig = None):
        
        self.engine = engine or get_genesis_engine()
        self.config = config or EvolutionConfig()
        
        self.state = LoopState.STOPPED
        self.metrics = LoopMetrics()
        
        self._loop_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self._start_time: Optional[datetime] = None
        
        # Callbacks për eventi
        self._on_evolution: List[Callable[[EvolutionCycle], None]] = []
        self._on_mutation: List[Callable[[GeneticCode], None]] = []
        self._on_synthesis: List[Callable[[GeneticCode], None]] = []
        
        logger.info("🔄 EvolutionLoop initialized")
    
    # =========================================================================
    # LIFECYCLE
    # =========================================================================
    
    async def start(self):
        """Fillo loop-in e evoluimit"""
        if self.state == LoopState.RUNNING:
            logger.warning("Evolution loop already running")
            return
        
        self.state = LoopState.RUNNING
        self._start_time = datetime.now(timezone.utc)
        self._stop_event.clear()
        
        self._loop_task = asyncio.create_task(self._evolution_loop())
        logger.info("🔄 Evolution loop started")
    
    async def stop(self):
        """Ndalo loop-in"""
        if self.state == LoopState.STOPPED:
            return
        
        self.state = LoopState.STOPPED
        self._stop_event.set()
        
        if self._loop_task:
            self._loop_task.cancel()
            try:
                await self._loop_task
            except asyncio.CancelledError:
                pass
        
        # Update uptime
        if self._start_time:
            self.metrics.uptime_seconds += (
                datetime.now(timezone.utc) - self._start_time
            ).total_seconds()
        
        logger.info("🔄 Evolution loop stopped")
    
    def pause(self):
        """Pauzë loop-in"""
        if self.state == LoopState.RUNNING:
            self.state = LoopState.PAUSED
            logger.info("🔄 Evolution loop paused")
    
    def resume(self):
        """Vazhdo loop-in"""
        if self.state == LoopState.PAUSED:
            self.state = LoopState.RUNNING
            logger.info("🔄 Evolution loop resumed")
    
    # =========================================================================
    # MAIN LOOP
    # =========================================================================
    
    async def _evolution_loop(self):
        """Loop-i kryesor i evoluimit"""
        logger.info("🔄 Evolution loop main cycle started")
        
        while not self._stop_event.is_set():
            try:
                # Check if paused
                if self.state == LoopState.PAUSED:
                    await asyncio.sleep(1)
                    continue
                
                # Wait for interval
                await asyncio.sleep(self.config.evolution_interval)
                
                if self._stop_event.is_set():
                    break
                
                # Run evolution cycle
                await self._run_evolution_cycle()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Evolution loop error: {e}")
                await asyncio.sleep(10)  # Wait before retry
    
    async def _run_evolution_cycle(self):
        """Ekzekuto një cikël të plotë evoluimi"""
        self.state = LoopState.EVOLVING
        
        try:
            # 1. Check population health
            await self._maintain_population()
            
            # 2. Run evolution
            cycle = self.engine.evolve(
                population_size=self.config.population_target,
                mutation_rate=self.config.mutation_rate,
                crossover_rate=self.config.crossover_rate
            )
            
            # 3. Update metrics
            self.metrics.total_cycles += 1
            self.metrics.total_mutations += cycle.mutations_applied
            self.metrics.total_crossovers += cycle.crossovers
            self.metrics.last_evolution = datetime.now(timezone.utc)
            
            if cycle.best_fitness > self.metrics.best_fitness_ever:
                self.metrics.best_fitness_ever = cycle.best_fitness
            
            self.metrics.avg_fitness_history.append(cycle.avg_fitness)
            # Keep last 100
            if len(self.metrics.avg_fitness_history) > 100:
                self.metrics.avg_fitness_history = self.metrics.avg_fitness_history[-100:]
            
            # 4. Notify callbacks
            for callback in self._on_evolution:
                try:
                    callback(cycle)
                except Exception as e:
                    logger.error(f"Callback error: {e}")
            
            logger.info(f"🔄 Evolution cycle {self.metrics.total_cycles} complete: "
                       f"fitness={cycle.best_fitness:.3f}")
            
        finally:
            self.state = LoopState.RUNNING
    
    async def _maintain_population(self):
        """Mban popullatën të shëndetshme"""
        stats = self.engine.get_stats()
        current_pop = stats["total_genes"]
        
        # Auto-prune if too large
        if self.config.auto_prune and current_pop > self.config.max_population:
            pruned = await self._prune_weak_genes(
                current_pop - self.config.population_target
            )
            self.metrics.total_pruned += pruned
            logger.info(f"🔄 Pruned {pruned} weak genes")
        
        # Auto-synthesize if too small
        if self.config.auto_synthesis and current_pop < self.config.min_population:
            synthesized = await self._synthesize_new_genes(
                self.config.min_population - current_pop
            )
            self.metrics.total_synthesized += synthesized
            logger.info(f"🔄 Synthesized {synthesized} new genes")
    
    async def _prune_weak_genes(self, count: int) -> int:
        """Elimino gjenet më të dobëta"""
        genes = list(self.engine.gene_pool.values())
        genes.sort(key=lambda g: g.fitness)
        
        pruned = 0
        for gene in genes[:count]:
            if gene.fitness < self.config.survival_threshold:
                del self.engine.gene_pool[gene.gene_id]
                if gene.gene_id in self.engine.active_genes:
                    del self.engine.active_genes[gene.gene_id]
                pruned += 1
        
        return pruned
    
    async def _synthesize_new_genes(self, count: int) -> int:
        """Krijo gjene të reja"""
        purposes = [
            "Filter items based on condition",
            "Transform data to new format",
            "Aggregate values into summary",
            "Search for specific pattern",
            "Sort items by criteria",
            "Validate input data",
            "Cache expensive operations",
            "Retry failed operations",
            "Pipeline multiple transforms",
            "Batch process items"
        ]
        
        synthesized = 0
        for _ in range(count):
            purpose = random.choice(purposes)
            gene = self.engine.synthesize(purpose=purpose)
            synthesized += 1
            
            for callback in self._on_synthesis:
                try:
                    callback(gene)
                except Exception:
                    pass
        
        return synthesized
    
    # =========================================================================
    # CALLBACKS
    # =========================================================================
    
    def on_evolution(self, callback: Callable[[EvolutionCycle], None]):
        """Regjistro callback për evolucione"""
        self._on_evolution.append(callback)
    
    def on_mutation(self, callback: Callable[[GeneticCode], None]):
        """Regjistro callback për mutacione"""
        self._on_mutation.append(callback)
    
    def on_synthesis(self, callback: Callable[[GeneticCode], None]):
        """Regjistro callback për sinteza"""
        self._on_synthesis.append(callback)
    
    # =========================================================================
    # MANUAL TRIGGERS
    # =========================================================================
    
    async def trigger_evolution(self) -> EvolutionCycle:
        """Triggero evolucion manual"""
        return self.engine.evolve(
            population_size=self.config.population_target,
            mutation_rate=self.config.mutation_rate,
            crossover_rate=self.config.crossover_rate
        )
    
    async def trigger_synthesis(self, purpose: str) -> GeneticCode:
        """Triggero sintezë manuale"""
        return self.engine.synthesize(purpose=purpose)
    
    async def trigger_mutation(self, gene_id: str, mutation_type: str = None) -> Optional[GeneticCode]:
        """Triggero mutacion manual"""
        return self.engine.mutate(gene_id, mutation_type)
    
    # =========================================================================
    # STATS
    # =========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Merr statusin e loop-it"""
        engine_stats = self.engine.get_stats()
        
        return {
            "state": self.state.value,
            "config": {
                "population_target": self.config.population_target,
                "evolution_interval": self.config.evolution_interval,
                "mutation_rate": self.config.mutation_rate,
                "crossover_rate": self.config.crossover_rate,
                "auto_synthesis": self.config.auto_synthesis,
                "auto_prune": self.config.auto_prune
            },
            "metrics": {
                "total_cycles": self.metrics.total_cycles,
                "total_mutations": self.metrics.total_mutations,
                "total_crossovers": self.metrics.total_crossovers,
                "total_synthesized": self.metrics.total_synthesized,
                "total_pruned": self.metrics.total_pruned,
                "best_fitness_ever": self.metrics.best_fitness_ever,
                "avg_fitness_trend": self.metrics.avg_fitness_history[-10:] if self.metrics.avg_fitness_history else [],
                "uptime_seconds": self.metrics.uptime_seconds,
                "last_evolution": self.metrics.last_evolution.isoformat() if self.metrics.last_evolution else None
            },
            "engine": engine_stats
        }


# =============================================================================
# SINGLETON
# =============================================================================

_evolution_loop: Optional[EvolutionLoop] = None

def get_evolution_loop() -> EvolutionLoop:
    """Get or create Evolution Loop singleton"""
    global _evolution_loop
    if _evolution_loop is None:
        _evolution_loop = EvolutionLoop()
    return _evolution_loop


# =============================================================================
# SYNC WRAPPER (for non-async contexts)
# =============================================================================

class EvolutionDaemon:
    """
    Wrapper sinkron për EvolutionLoop.
    Përdor thread të veçantë për async loop.
    """
    
    def __init__(self):
        self.loop = get_evolution_loop()
        self._thread: Optional[threading.Thread] = None
        self._async_loop: Optional[asyncio.AbstractEventLoop] = None
    
    def start(self):
        """Start daemon in background thread"""
        if self._thread and self._thread.is_alive():
            return
        
        self._thread = threading.Thread(target=self._run_async, daemon=True)
        self._thread.start()
        logger.info("🔄 Evolution daemon started in background")
    
    def _run_async(self):
        """Run async loop in thread"""
        self._async_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._async_loop)
        self._async_loop.run_until_complete(self.loop.start())
        self._async_loop.run_forever()
    
    def stop(self):
        """Stop daemon"""
        if self._async_loop:
            self._async_loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self.loop.stop())
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Get status"""
        return self.loop.get_status()


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    async def demo():
        loop = get_evolution_loop()
        
        # Configure
        loop.config.evolution_interval = 10  # 10 seconds for demo
        loop.config.auto_synthesis = True
        
        # Add callback
        def on_evo(cycle):
            print(f"📊 Evolution: gen={cycle.generation}, fitness={cycle.best_fitness:.3f}")
        
        loop.on_evolution(on_evo)
        
        # Start
        await loop.start()
        
        # Let it run
        print("Running for 60 seconds...")
        await asyncio.sleep(60)
        
        # Stop
        await loop.stop()
        
        # Print stats
        print(f"\n📊 Final Status: {loop.get_status()}")
    
    asyncio.run(demo())
