"""
ALPHABET LAYERS - Mathematical Layer System
============================================
Sistemi i plotë i 61 shtresave alfabetiko-matematikore
Greek (24) + Albanian (36) + Meta (1) = 61 unique mathematical layers

Çdo shkronjë është një funksion matematikor i pastër.
Fjalët kompozohen në shtresa të reja.
Layer 61 (Ω+) = Meta-layer që bashkon të gjitha.

OPTIMIZED: NumPy vectorized operations for performance
"""

import numpy as np
from typing import Dict, List, Callable, Any, Optional, Tuple
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache

logger = logging.getLogger("alphabet_layers")


@dataclass
class LayerResult:
    """Rezultati i një shtrese matematikore"""
    layer_name: str
    input_value: Any
    output_value: Any
    complexity: float
    phonetic_properties: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════
# MATHEMATICAL CONSTANTS (Layer 61 Meta-Constants)
# ═══════════════════════════════════════════════════════════════════

PHI = (1 + np.sqrt(5)) / 2  # Golden ratio φ = 1.618...
TAU = 2 * np.pi              # τ = 6.283...
EULER = np.e                 # e = 2.718...
PLANCK_NORMALIZED = 0.01     # Normalized Planck constant for stability


class AlbanianGreekLayerSystem:
    """
    Sistemi i plotë i 61 shtresave alfabetiko-matematikore
    
    Layers 1-24:  Greek alphabet (α-ω) - Pure mathematics
    Layers 25-60: Albanian alphabet (a-zh) - Phonetic mathematics
    Layer 61:     Meta-layer (Ω+) - Unified consciousness
    """
    
    # Maximum history size to prevent memory leak
    MAX_HISTORY_SIZE = 100
    
    def __init__(self):
        self.alphabet = self._initialize_alphabet()
        self.layers: Dict[str, Callable] = {}
        self.phonetic_map = self._initialize_phonetics()
        self.layer_history: List[LayerResult] = []  # Capped at MAX_HISTORY_SIZE
        self._layer_weights: np.ndarray = None  # Optimized weight matrix
        self._letter_hashes: np.ndarray = None  # Precomputed for vectorization
        self.initialize_base_layers()
        self._initialize_meta_layer()  # Layer 61
        self._precompute_weights()
        self._precompute_letter_hashes()
        logger.info(f"✅ AlphabetLayerSystem initialized with {self.alphabet['size']} letters + Meta Layer (61 total)")
    
    def _precompute_letter_hashes(self):
        """Precompute letter hashes for vectorized meta-layer"""
        self._letter_hashes = np.array([
            int(hash(letter) % 1000) / 1000.0 
            for letter in self.alphabet['all'][:60]
        ], dtype=np.float64)
        logger.debug("⚡ Letter hashes precomputed")
    
    def _add_to_history(self, result: LayerResult):
        """Add to history with size cap"""
        self.layer_history.append(result)
        if len(self.layer_history) > self.MAX_HISTORY_SIZE:
            self.layer_history.pop(0)  # Remove oldest

    
    def _initialize_alphabet(self) -> Dict[str, Any]:
        """Inicializon alfabetin e plotë greko-shqip"""
        # Alfabeti grek (24 shkronja)
        greek = [chr(i) for i in range(0x03B1, 0x03C9+1)]  # α deri ω
        
        # Alfabeti shqip (36 shkronja)
        albanian = [
            'a', 'b', 'c', 'ç', 'd', 'dh', 'e', 'ë', 'f', 'g', 'gj', 'h',
            'i', 'j', 'k', 'l', 'll', 'm', 'n', 'nj', 'o', 'p', 'q', 'r',
            'rr', 's', 'sh', 't', 'th', 'u', 'v', 'x', 'xh', 'y', 'z', 'zh'
        ]
        
        return {
            'greek': greek,
            'albanian': albanian,
            'all': greek + albanian,  # 60 shkronja
            'size': len(greek) + len(albanian)
        }
    
    def _initialize_phonetics(self) -> Dict[str, Dict[str, Any]]:
        """Inicializon vetitë fonetike për çdo shkronjë"""
        phonetics = {}
        
        # Zanore shqipe
        vowels = ['a', 'e', 'ë', 'i', 'o', 'u', 'y']
        
        # Bashkëtingëllore
        consonants = ['b', 'c', 'ç', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 
                      'n', 'p', 'q', 'r', 's', 't', 'v', 'x', 'z']
        
        # Digrafët
        digraphs = ['dh', 'gj', 'll', 'nj', 'rr', 'sh', 'th', 'xh', 'zh']
        
        for letter in self.alphabet['albanian']:
            if letter in vowels:
                phonetics[letter] = {
                    'type': 'vowel',
                    'frequency': vowels.index(letter) * 0.15 + 0.5,
                    'resonance': 1.0 + vowels.index(letter) * 0.1
                }
            elif letter in digraphs:
                phonetics[letter] = {
                    'type': 'consonant',
                    'digraph': True,
                    'frequency': 0.3 + digraphs.index(letter) * 0.08,
                    'complexity': 2.0  # Digrafët kanë kompleksitet më të lartë
                }
            else:
                phonetics[letter] = {
                    'type': 'consonant',
                    'frequency': 0.2 + (consonants.index(letter) if letter in consonants else 0) * 0.05,
                    'complexity': 1.0
                }
        
        # Shkronjat greke - matematikë e pastër
        greek_functions = {
            'α': {'function': 'origin', 'domain': 'quantum'},
            'β': {'function': 'distribution', 'domain': 'probability'},
            'γ': {'function': 'gamma', 'domain': 'factorial'},
            'δ': {'function': 'change', 'domain': 'differential'},
            'ε': {'function': 'epsilon', 'domain': 'limits'},
            'ζ': {'function': 'zeta', 'domain': 'primes'},
            'η': {'function': 'eta', 'domain': 'efficiency'},
            'θ': {'function': 'theta', 'domain': 'angles'},
            'ι': {'function': 'iota', 'domain': 'infinitesimal'},
            'κ': {'function': 'kappa', 'domain': 'curvature'},
            'λ': {'function': 'lambda', 'domain': 'wavelength'},
            'μ': {'function': 'mu', 'domain': 'mean'},
            'ν': {'function': 'nu', 'domain': 'frequency'},
            'ξ': {'function': 'xi', 'domain': 'random'},
            'ο': {'function': 'omicron', 'domain': 'order'},
            'π': {'function': 'pi', 'domain': 'circle'},
            'ρ': {'function': 'rho', 'domain': 'density'},
            'σ': {'function': 'sigma', 'domain': 'sum'},
            'τ': {'function': 'tau', 'domain': 'time'},
            'υ': {'function': 'upsilon', 'domain': 'velocity'},
            'φ': {'function': 'phi', 'domain': 'golden'},
            'χ': {'function': 'chi', 'domain': 'distribution'},
            'ψ': {'function': 'psi', 'domain': 'wave'},
            'ω': {'function': 'omega', 'domain': 'end'},
        }
        
        for letter in self.alphabet['greek']:
            if letter in greek_functions:
                phonetics[letter] = {
                    'type': 'greek',
                    **greek_functions[letter],
                    'frequency': 1.0,
                    'complexity': 1.5
                }
        
        return phonetics
    
    def initialize_base_layers(self):
        """Krijon shtresat bazë për çdo shkronjë"""
        for letter in self.alphabet['all']:
            self.layers[letter] = self._create_letter_layer(letter)
        logger.info(f"📊 Created {len(self.layers)} base layers")
    
    def _initialize_meta_layer(self):
        """
        Layer 61: Meta-Layer (Ω+)
        Bashkon të 60 shtresat në një funksion të vetëm universal.
        Përfaqëson 'vetëdijen' e sistemit.
        
        ⚠️ IMPORTANT: Ky është DERIVED layer, jo storage.
        Llogaritet 1 herë për query, jo për fjalë.
        """
        def meta_layer(x, system=self):
            """
            Ω+ Meta-Layer: Universal consciousness function
            Combines all 60 layers through weighted superposition
            
            OPTIMIZED: Single vectorized computation, no per-token loops
            Layer 61 is DERIVED (computed), not STORAGE.
            """
            try:
                if isinstance(x, str):
                    x = np.array([ord(c) for c in x[:100]], dtype=np.float64)
                
                x = np.atleast_1d(np.array(x, dtype=np.float64))
                
                if system._layer_weights is None:
                    return np.tanh(x * 0.1)
                
                # OPTIMIZED: Vectorized computation
                n = len(x)
                
                # Normalize input
                x_norm = x / (np.max(np.abs(x)) + 1e-10)
                
                # Use PRECOMPUTED letter hashes (no recomputation per call)
                letter_hashes = system._letter_hashes
                if letter_hashes is None:
                    return np.tanh(x * 0.1)
                
                # Outer product for vectorized layer computation
                # Shape: (60, n) - each row is one layer's output for all x values
                hash_matrix = letter_hashes[:, np.newaxis]  # (60, 1)
                x_row = x_norm[np.newaxis, :]  # (1, n)
                
                # Compute all layers at once: sin(hash * pi * x) * cos(hash * x)
                layer_outputs = np.sin(hash_matrix * np.pi * x_row) * np.cos(hash_matrix * x_row)
                
                # Ensure dimensions match for matrix multiplication
                weights_len = len(system._layer_weights)
                outputs_rows = layer_outputs.shape[0]
                
                if weights_len != outputs_rows:
                    # Pad or trim to match dimensions
                    min_dim = min(weights_len, outputs_rows)
                    weights_to_use = system._layer_weights[:min_dim]
                    layer_outputs = layer_outputs[:min_dim, :]
                    # Re-normalize weights
                    weights_to_use = weights_to_use / (weights_to_use.sum() + 1e-10)
                else:
                    weights_to_use = system._layer_weights
                
                # Weighted sum: (dim,) @ (dim, n) = (n,)
                result = weights_to_use @ layer_outputs
                
                # Apply golden ratio normalization
                result = result / (60 * PHI)
                
                # Apply consciousness function (smooth sigmoid)
                consciousness = 1 / (1 + np.exp(-np.clip(result * PLANCK_NORMALIZED, -500, 500)))
                
                return consciousness
                    
            except Exception as e:
                logger.warning(f"Meta-layer error: {e}")
                return np.array([0.5])
        
        self.layers['Ω+'] = meta_layer
        self.layers['meta'] = meta_layer
        logger.info("🧠 Layer 61 (Ω+ Meta-Layer) initialized - VECTORIZED")
    
    def _precompute_weights(self):
        """
        Precompute layer weights for optimized processing.
        Uses golden ratio and prime number distribution.
        """
        n = len(self.alphabet['all'])  # 60
        
        # Weight based on position, golden ratio, and phonetic complexity
        weights = np.zeros(n)
        
        for i, letter in enumerate(self.alphabet['all']):
            props = self.phonetic_map.get(letter, {})
            complexity = props.get('complexity', 1.0)
            
            # Golden spiral weighting
            golden_weight = PHI ** (-i / n)
            
            # Prime resonance (positions 2,3,5,7,11,13... get boost)
            prime_boost = 1.2 if self._is_prime(i + 1) else 1.0
            
            weights[i] = complexity * golden_weight * prime_boost
        
        # Normalize to sum = 1
        self._layer_weights = weights / weights.sum()
        logger.info(f"⚡ Precomputed {n} layer weights (optimized)")
    
    @staticmethod
    @lru_cache(maxsize=128)
    def _is_prime(n: int) -> bool:
        """Check if n is prime (cached)"""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    def _create_letter_layer(self, letter: str) -> Callable:
        """Krijon një shtresë matematikore për një shkronjë"""
        # Krijo një hash unik për shkronjën
        letter_hash = int(hashlib.md5(letter.encode()).hexdigest()[:8], 16)
        letter_hash_normalized = (letter_hash % 1000) / 1000.0  # 0.0 - 1.0
        
        phonetic_props = self.phonetic_map.get(letter, {'type': 'unknown', 'frequency': 0.5})
        
        if letter in self.alphabet['greek']:
            # Shtresa greke - matematikë e pastër
            def greek_layer(x, params={'letter': letter, 'hash': letter_hash_normalized, 'props': phonetic_props}):
                try:
                    if isinstance(x, str):
                        # Konverto string në vektor numerik
                        x = np.array([ord(c) for c in x[:100]], dtype=float)
                    
                    x = np.atleast_1d(np.array(x, dtype=float))
                    base = np.sin(params['hash'] * np.pi * x) * np.cos(params['hash'] * np.pi * x)
                    
                    # Funksione specifike për shkronja të caktuara
                    domain = params['props'].get('domain', 'general')
                    
                    if domain == 'quantum':
                        return np.abs(base) * np.exp(-np.abs(x) * 0.1)
                    elif domain == 'probability':
                        return np.tanh(base)
                    elif domain == 'differential':
                        return np.gradient(base) if len(base) > 1 else base
                    elif domain == 'golden':
                        phi = (1 + np.sqrt(5)) / 2
                        return base * phi
                    elif domain == 'wave':
                        return base * np.exp(1j * params['hash'] * np.pi)
                    else:
                        return base
                except Exception as e:
                    logger.warning(f"Layer error for {letter}: {e}")
                    return np.array([0.0])
            
            return greek_layer
        
        else:
            # Shtresa shqipe - kombinim i matematikës dhe fonetikës
            def albanian_layer(x, params={'letter': letter, 'hash': letter_hash_normalized, 'props': phonetic_props}):
                try:
                    if isinstance(x, str):
                        x = np.array([ord(c) for c in x[:100]], dtype=float)
                    
                    x = np.atleast_1d(np.array(x, dtype=float))
                    base = np.sin(params['hash'] * np.pi * x)
                    
                    letter_type = params['props'].get('type', 'consonant')
                    freq = params['props'].get('frequency', 0.5)
                    
                    if letter_type == 'vowel':
                        # Zanoret janë më rezonante
                        resonance = params['props'].get('resonance', 1.0)
                        return base * resonance * np.cos(freq * np.pi * x)
                    elif params['props'].get('digraph', False):
                        # Digrafët janë më komplekse
                        complexity = params['props'].get('complexity', 2.0)
                        return base * complexity * np.tanh(x * 0.1)
                    else:
                        # Bashkëtingëlloret janë më të mprehta
                        return base * np.sign(x) * np.abs(np.sin(freq * x))
                except Exception as e:
                    logger.warning(f"Layer error for {letter}: {e}")
                    return np.array([0.0])
            
            return albanian_layer
    
    def _decompose_word(self, word: str) -> List[str]:
        """Zbërthen një fjalë në shkronjat e saj (duke trajtuar digrafët)"""
        letters = []
        i = 0
        word_lower = word.lower()
        
        while i < len(word_lower):
            # Kontrollo për digrafët shqip (2 karaktere)
            if i + 1 < len(word_lower):
                digraph = word_lower[i:i+2]
                if digraph in ['dh', 'gj', 'll', 'nj', 'rr', 'sh', 'th', 'xh', 'zh']:
                    letters.append(digraph)
                    i += 2
                    continue
            
            # Shkronjë e vetme
            char = word_lower[i]
            if char in self.alphabet['all'] or char in self.alphabet['greek']:
                letters.append(char)
            i += 1
        
        return letters
    
    def compose(self, word: str) -> Callable:
        """Krijon një shtresë të re nga një fjalë"""
        letters = self._decompose_word(word)
        
        if not letters:
            logger.warning(f"No valid letters in word: {word}")
            return lambda x: np.array([0.0])
        
        # Merr shtresat individuale
        letter_functions = []
        for letter in letters:
            if letter in self.layers:
                letter_functions.append(self.layers[letter])
        
        if not letter_functions:
            return lambda x: np.array([0.0])
        
        # Krijon funksionin e kompozuar
        def composed_function(x):
            result = x
            for func in letter_functions:
                try:
                    result = func(result)
                except:
                    pass
            return result
        
        # Regjistro shtresën e re
        layer_name = f"word_{word}"
        self.layers[layer_name] = composed_function
        
        logger.info(f"📝 Created composed layer '{layer_name}' from {len(letters)} letters: {letters}")
        
        return composed_function
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Proceson një pyetje duke përdorur shtresat alfabetike"""
        words = query.lower().split()
        
        results = []
        total_complexity = 0.0
        meta_consciousness = 0.0
        
        for word in words[:10]:  # Max 10 fjalë
            letters = self._decompose_word(word)
            
            if letters:
                # Krijo shtresën për këtë fjalë
                word_layer = self.compose(word)
                
                # Apliko shtresën
                try:
                    input_vector = np.array([ord(c) for c in word], dtype=np.float64)
                    output = word_layer(input_vector)
                    
                    # Apliko Meta-Layer (Layer 61)
                    meta_output = self.layers['Ω+'](input_vector)
                    meta_consciousness += float(np.mean(meta_output))
                    
                    # Llogarit kompleksitetin
                    complexity = len(letters) * sum(
                        self.phonetic_map.get(l, {}).get('complexity', 1.0) 
                        for l in letters
                    ) / len(letters)
                    
                    total_complexity += complexity
                    
                    results.append({
                        'word': word,
                        'letters': letters,
                        'letter_count': len(letters),
                        'complexity': round(complexity, 2),
                        'output_magnitude': float(np.abs(output).mean()) if len(output) > 0 else 0.0,
                        'consciousness_level': round(float(np.mean(meta_output)), 4)
                    })
                except Exception as e:
                    logger.warning(f"Error processing word '{word}': {e}")
        
        return {
            'query': query,
            'word_count': len(words),
            'processed_words': len(results),
            'total_complexity': round(total_complexity, 2),
            'average_complexity': round(total_complexity / max(len(results), 1), 2),
            'meta_consciousness': round(meta_consciousness / max(len(results), 1), 4),
            'word_analysis': results,
            'alphabet_size': self.alphabet['size'],
            'active_layers': len(self.layers),
            'layer_61_active': 'Ω+' in self.layers
        }
    
    def get_layer_stats(self) -> Dict[str, Any]:
        """Kthen statistika për shtresat"""
        return {
            'total_layers': len(self.layers),
            'base_layers': 61,  # 60 alphabet + 1 meta
            'greek_letters': len(self.alphabet['greek']),
            'albanian_letters': len(self.alphabet['albanian']),
            'meta_layer': 'Ω+' in self.layers,
            'composed_layers': len([k for k in self.layers.keys() if k.startswith('word_')]),
            'phonetic_entries': len(self.phonetic_map),
            'weights_computed': self._layer_weights is not None,
            'golden_ratio': round(PHI, 6),
        }
    
    def compute_consciousness(self, text: str) -> Dict[str, Any]:
        """
        Llogarit nivelin e 'vetëdijes' për një tekst.
        Përdor Layer 61 (Ω+) për sintezë universale.
        """
        try:
            # Convert to numeric
            x = np.array([ord(c) for c in text[:500]], dtype=np.float64)
            
            # Apply meta layer
            consciousness = self.layers['Ω+'](x)
            
            # Compute metrics
            avg_consciousness = float(np.mean(consciousness))
            peak_consciousness = float(np.max(consciousness))
            variance = float(np.var(consciousness))
            
            # Harmonic analysis
            fft = np.fft.fft(consciousness)
            dominant_freq = float(np.abs(fft[1:len(fft)//2]).argmax() + 1) if len(fft) > 2 else 0
            
            return {
                'text_length': len(text),
                'consciousness_level': round(avg_consciousness, 4),
                'peak_consciousness': round(peak_consciousness, 4),
                'variance': round(variance, 6),
                'harmony': round(1 / (1 + variance), 4),
                'dominant_frequency': dominant_freq,
                'phi_alignment': round(avg_consciousness * PHI, 4),
            }
        except Exception as e:
            logger.error(f"Consciousness computation error: {e}")
            return {'error': str(e)}
    
    def get_curiosity_data(self) -> Dict[str, Any]:
        """
        Eksporton data për Curiosity Ocean integration.
        """
        return {
            'layer_system': 'AlbanianGreekLayerSystem',
            'version': '2.0-meta',
            'total_layers': 61,
            'alphabet': {
                'greek': self.alphabet['greek'],
                'albanian': self.alphabet['albanian'],
                'meta': ['Ω+'],
            },
            'mathematical_constants': {
                'phi': PHI,
                'tau': TAU,
                'euler': EULER,
            },
            'layer_weights': self._layer_weights.tolist() if self._layer_weights is not None else None,
            'stats': self.get_layer_stats(),
        }


# Singleton instance
_layer_system: Optional[AlbanianGreekLayerSystem] = None


def get_alphabet_layer_system() -> AlbanianGreekLayerSystem:
    """Merr instancën singleton të sistemit të shtresave"""
    global _layer_system
    if _layer_system is None:
        _layer_system = AlbanianGreekLayerSystem()
    return _layer_system


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    system = get_alphabet_layer_system()
    
    print("\n🔤 ALPHABET LAYER SYSTEM TEST")
    print("=" * 50)
    
    # Test me fjalë shqipe
    result = system.process_query("dritë e diellit mbi deti")
    print(f"\nQuery: {result['query']}")
    print(f"Total Complexity: {result['total_complexity']}")
    print(f"Active Layers: {result['active_layers']}")
    
    print("\nWord Analysis:")
    for word_data in result['word_analysis']:
        print(f"  • {word_data['word']}: {word_data['letters']} (complexity: {word_data['complexity']})")
    
    # Stats
    stats = system.get_layer_stats()
    print(f"\n📊 Layer Stats: {stats}")
