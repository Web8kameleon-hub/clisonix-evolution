"""
LazyStateManager - Nanogrid-inspired state persistence for Genesis

Koncepte nga Nanogrid:
- Dirty flag: Ruaj vetëm kur ka ndryshime të vërteta
- Batch saves: Grumbulloji ndryshimet, ruaj periodikisht
- Memory-first: Puno në RAM, flusho në disk periodikisht
- Async I/O: Mos blloko main thread

Author: Clisonix Team
Version: 1.0.0
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional

try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

logger = logging.getLogger(__name__)


class LazyStateManager:
    """
    Memory-first state manager me periodic flush.
    
    Inspiruar nga Nanogrid Sleep/Wake pattern:
    - Memory-first: Ndryshimet ruhen në RAM
    - Dirty flag: Vetëm kur ka ndryshime reale
    - Periodic flush: Ruaj çdo N sekonda ose N ndryshime
    - Non-blocking: Async writes në background
    """
    
    def __init__(
        self,
        state_file: Path,
        flush_interval: float = 30.0,      # Flush çdo 30 sekonda
        max_pending_changes: int = 10,      # Ose pas 10 ndryshimeve
        use_fast_json: bool = True          # Përdor orjson nëse ka
    ):
        self.state_file = Path(state_file)
        self.flush_interval = flush_interval
        self.max_pending_changes = max_pending_changes
        self.use_fast_json = use_fast_json and HAS_ORJSON
        
        # State në memory
        self._state: Dict[str, Any] = {}
        self._dirty = False
        self._pending_changes = 0
        self._last_flush = time.time()
        
        # Thread safety
        self._lock = threading.RLock()
        self._flush_thread: Optional[threading.Thread] = None
        self._running = False
        
        # Stats
        self._saves_avoided = 0
        self._actual_saves = 0
        
        logger.info(f"🧠 LazyStateManager initialized: flush every {flush_interval}s or {max_pending_changes} changes")
    
    def start(self):
        """Fillo background flush thread"""
        if self._running:
            return
        
        self._running = True
        self._flush_thread = threading.Thread(target=self._background_flush, daemon=True)
        self._flush_thread.start()
        logger.info("🔄 Background flush thread started")
    
    def stop(self):
        """Ndalo dhe ruaj gjithçka"""
        self._running = False
        if self._flush_thread:
            self._flush_thread.join(timeout=5.0)
        self.force_flush()
        logger.info("💤 LazyStateManager stopped")
    
    def update(self, key: str, value: Any):
        """
        Përditëso vlerën në memory (nuk shkruan në disk menjëherë).
        """
        with self._lock:
            old_value = self._state.get(key)
            
            # Kontrollo nëse vlera ka ndryshuar vërtet
            if self._values_equal(old_value, value):
                self._saves_avoided += 1
                return  # Asnjë ndryshim real
            
            self._state[key] = value
            self._dirty = True
            self._pending_changes += 1
            
            # Auto-flush nëse ka shumë ndryshime pending
            if self._pending_changes >= self.max_pending_changes:
                self._do_flush()
    
    def update_bulk(self, updates: Dict[str, Any]):
        """Përditëso shumë vlera me një thirrje."""
        with self._lock:
            changes_made = False
            for key, value in updates.items():
                old_value = self._state.get(key)
                if not self._values_equal(old_value, value):
                    self._state[key] = value
                    changes_made = True
                    self._pending_changes += 1
            
            if changes_made:
                self._dirty = True
            else:
                self._saves_avoided += 1
            
            if self._pending_changes >= self.max_pending_changes:
                self._do_flush()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Lexo vlerën nga memory."""
        with self._lock:
            return self._state.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Merr kopje të gjithë state."""
        with self._lock:
            return dict(self._state)
    
    def set_state(self, state: Dict[str, Any]):
        """Vendos gjithë state (për load)."""
        with self._lock:
            self._state = dict(state)
            self._dirty = False
            self._pending_changes = 0
    
    def force_flush(self):
        """Forco flush menjëherë."""
        with self._lock:
            self._do_flush()
    
    def _values_equal(self, a: Any, b: Any) -> bool:
        """Krahaso vlerat duke trajtuar nested dicts."""
        if type(a) != type(b):
            return False
        
        if isinstance(a, dict):
            if set(a.keys()) != set(b.keys()):
                return False
            return all(self._values_equal(a[k], b[k]) for k in a)
        
        if isinstance(a, list):
            if len(a) != len(b):
                return False
            return all(self._values_equal(x, y) for x, y in zip(a, b))
        
        return a == b
    
    def _do_flush(self):
        """Internal flush - shkruan në disk."""
        if not self._dirty:
            return
        
        try:
            start = time.perf_counter()
            
            # Serializo
            if self.use_fast_json:
                data = orjson.dumps(self._state, option=orjson.OPT_INDENT_2)
                mode = 'wb'
            else:
                data = json.dumps(self._state, indent=2, ensure_ascii=False)
                mode = 'w'
            
            # Shkruaj atomikisht (temp file + rename)
            temp_file = self.state_file.with_suffix('.tmp')
            if mode == 'wb':
                temp_file.write_bytes(data)
            else:
                temp_file.write_text(data, encoding='utf-8')
            temp_file.replace(self.state_file)
            
            elapsed = time.perf_counter() - start
            
            self._dirty = False
            self._pending_changes = 0
            self._last_flush = time.time()
            self._actual_saves += 1
            
            logger.debug(f"💾 State flushed in {elapsed*1000:.1f}ms")
            
        except Exception as e:
            logger.error(f"❌ Flush failed: {e}")
    
    def _background_flush(self):
        """Background thread që flusho periodikisht."""
        while self._running:
            time.sleep(1.0)  # Check çdo sekondë
            
            with self._lock:
                time_since_flush = time.time() - self._last_flush
                
                if self._dirty and time_since_flush >= self.flush_interval:
                    self._do_flush()
    
    def load(self) -> bool:
        """Ngarko state nga disku."""
        if not self.state_file.exists():
            logger.info("📂 No state file found, starting fresh")
            return False
        
        try:
            with self._lock:
                if self.use_fast_json:
                    data = self.state_file.read_bytes()
                    self._state = orjson.loads(data)
                else:
                    with open(self.state_file, 'r', encoding='utf-8') as f:
                        self._state = json.load(f)
                
                self._dirty = False
                self._pending_changes = 0
                
            logger.info(f"📂 State loaded: {len(self._state)} keys")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load state: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistikat e menaxherit."""
        with self._lock:
            return {
                "dirty": self._dirty,
                "pending_changes": self._pending_changes,
                "saves_avoided": self._saves_avoided,
                "actual_saves": self._actual_saves,
                "efficiency": f"{self._saves_avoided/(self._saves_avoided + self._actual_saves + 0.001)*100:.1f}%",
                "state_keys": len(self._state),
                "time_since_flush": time.time() - self._last_flush,
                "using_orjson": self.use_fast_json
            }


# =============================================================================
# Singleton për easy access
# =============================================================================

_manager: Optional[LazyStateManager] = None

def get_lazy_state_manager(state_file: Optional[Path] = None) -> LazyStateManager:
    """Get or create singleton LazyStateManager."""
    global _manager
    
    if _manager is None:
        if state_file is None:
            raise ValueError("Must provide state_file for first initialization")
        
        _manager = LazyStateManager(state_file)
        _manager.load()
        _manager.start()
    
    return _manager


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    import tempfile
    
    logging.basicConfig(level=logging.DEBUG)
    
    # Test
    with tempfile.TemporaryDirectory() as tmpdir:
        state_file = Path(tmpdir) / "test_state.json"
        
        manager = LazyStateManager(state_file, flush_interval=2.0, max_pending_changes=5)
        manager.start()
        
        print("\n🧪 Testing LazyStateManager...")
        
        # Simulate many updates
        for i in range(20):
            manager.update("counter", i)
            manager.update("nested", {"level": i, "data": [1, 2, 3]})
            time.sleep(0.1)
        
        # Same value - should not trigger save
        for _ in range(10):
            manager.update("counter", 19)  # Same value
        
        time.sleep(3)  # Let background flush happen
        
        stats = manager.get_stats()
        print(f"\n📊 Stats: {stats}")
        print(f"   Saves avoided: {stats['saves_avoided']}")
        print(f"   Actual saves: {stats['actual_saves']}")
        print(f"   Efficiency: {stats['efficiency']}")
        
        manager.stop()
        print("\n✅ Test complete!")
