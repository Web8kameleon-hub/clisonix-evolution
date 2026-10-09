#!/usr/bin/env python3
"""
Integration Guide for 7-Layer Mathematical Orchestrator
Albanian-Greek Alphabetic Layer System (60 Base Layers)

Sistemi i plotë i 36+ shtresave alfabetiko-matematikore
α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω (24 Greek)
a b c ç d dh e ë f g gj h i j k l ll m n nj o p q r rr s sh t th u v x xh y z zh (36 Albanian)
= 60 Base Mathematical Layers
"""

import json
import os
import numpy as np
import hashlib
from typing import Dict, List, Callable, Any
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# ALPHABETIC LAYER MAPPING - 60 SHKRONJA = 60 LAYERS BAZË
# ═══════════════════════════════════════════════════════════════════════════════

ALPHABETIC_LAYERS = {
    # Greek (24 shkronja) - Matematikë e Pastër
    'α': 'quantum_superposition',
    'β': 'beta_distribution_transform',
    'γ': 'gamma_function_extension',
    'δ': 'dirac_delta_operator',
    'ε': 'epsilon_delta_calculus',
    'ζ': 'zeta_function_analytic',
    'η': 'eta_invariant_topology',
    'θ': 'theta_wave_function',
    'ι': 'iota_small_infinitesimal',
    'κ': 'kappa_curvature_tensor',
    'λ': 'lambda_calculus_layer',
    'μ': 'mu_measure_theory',
    'ν': 'nu_frequency_domain',
    'ξ': 'xi_complex_analytic',
    'ο': 'omicron_order_theory',
    'π': 'pi_circular_transforms',
    'ρ': 'rho_density_operator',
    'σ': 'sigma_algebra_layer',
    'τ': 'tau_time_evolution',
    'υ': 'upsilon_higher_order',
    'φ': 'phi_golden_ratio_transform',
    'χ': 'chi_characteristic_function',
    'ψ': 'psi_wavelet_transform',
    'ω': 'omega_limit_sets',
    
    # Albanian (36 shkronja) - Fonetikë + Matematikë
    'a': 'a_albanian_fractal',
    'b': 'b_balam_transform',
    'c': 'c_cerek_function',
    'ç': 'ç_chaotic_mapping',
    'd': 'd_delta_albanian',
    'dh': 'dh_digraph_operator',
    'e': 'e_exponential_local',
    'ë': 'ë_schwa_neutral',
    'f': 'f_fourier_albanian',
    'g': 'g_geg_transform',
    'gj': 'gj_digraph_phase',
    'h': 'h_hilbert_local',
    'i': 'i_imaginary_unit',
    'j': 'j_bessel_function',
    'k': 'k_kernel_operator',
    'l': 'l_laplacian_albanian',
    'll': 'll_geminate_operator',
    'm': 'm_matrix_albanian',
    'n': 'n_neural_operator',
    'nj': 'nj_palatal_operator',
    'o': 'o_orbital_function',
    'p': 'p_probability_layer',
    'q': 'q_q_analog_transform',
    'r': 'r_radial_function',
    'rr': 'rr_trill_operator',
    's': 's_spectral_albanian',
    'sh': 'sh_sh_operator',
    't': 't_time_albanian',
    'th': 'th_theta_albanian',
    'u': 'u_unitary_transform',
    'v': 'v_vector_albanian',
    'x': 'x_unknown_operator',
    'xh': 'xh_digraph_complex',
    'y': 'y_y_function',
    'z': 'z_zeta_albanian',
    'zh': 'zh_zh_operator'
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHONETIC PROPERTIES - VETITË FONETIKE TË SHKRONJAVE
# ═══════════════════════════════════════════════════════════════════════════════

PHONETIC_PROPERTIES = {
    # Vowels (Zanoret)
    'a': {'type': 'vowel', 'frequency': 0.8, 'openness': 'open', 'frontness': 'central'},
    'e': {'type': 'vowel', 'frequency': 0.7, 'openness': 'mid', 'frontness': 'front'},
    'ë': {'type': 'vowel', 'frequency': 0.5, 'openness': 'mid', 'frontness': 'central'},
    'i': {'type': 'vowel', 'frequency': 0.9, 'openness': 'close', 'frontness': 'front'},
    'o': {'type': 'vowel', 'frequency': 0.6, 'openness': 'mid', 'frontness': 'back'},
    'u': {'type': 'vowel', 'frequency': 0.7, 'openness': 'close', 'frontness': 'back'},
    'y': {'type': 'vowel', 'frequency': 0.4, 'openness': 'close', 'frontness': 'front'},
    
    # Digraphs (Digrafët)
    'dh': {'type': 'consonant', 'digraph': True, 'frequency': 0.3, 'voiced': True, 'place': 'dental'},
    'gj': {'type': 'consonant', 'digraph': True, 'frequency': 0.25, 'voiced': True, 'place': 'palatal'},
    'll': {'type': 'consonant', 'digraph': True, 'frequency': 0.35, 'voiced': True, 'place': 'lateral', 'complexity': 1.5},
    'nj': {'type': 'consonant', 'digraph': True, 'frequency': 0.2, 'voiced': True, 'place': 'palatal'},
    'rr': {'type': 'consonant', 'digraph': True, 'frequency': 0.4, 'voiced': True, 'place': 'alveolar', 'complexity': 1.8},
    'sh': {'type': 'consonant', 'digraph': True, 'frequency': 0.45, 'voiced': False, 'place': 'palatal'},
    'th': {'type': 'consonant', 'digraph': True, 'frequency': 0.15, 'voiced': False, 'place': 'dental'},
    'xh': {'type': 'consonant', 'digraph': True, 'frequency': 0.1, 'voiced': True, 'place': 'palatal', 'complexity': 2.0},
    'zh': {'type': 'consonant', 'digraph': True, 'frequency': 0.12, 'voiced': True, 'place': 'palatal'},
}


# ═══════════════════════════════════════════════════════════════════════════════
# CLASS: AlbanianGreekLayerSystem - SISTEMI KRYESOR
# ═══════════════════════════════════════════════════════════════════════════════

class AlbanianGreekLayerSystem:
    """
    Sistemi i plotë i 60 shtresave alfabetiko-matematikore
    
    60 base layers = 24 Greek + 36 Albanian letters
    ∞ composed layers = combinations of letters (words)
    """
    
    def __init__(self):
        self.alphabet = self._initialize_alphabet()
        self.layers: Dict[str, Callable] = {}
        self.layer_history: List[Dict] = []
        self.initialize_base_layers()
        
        # Statistics
        self.total_base_layers = len(self.alphabet['all'])
        self.total_composed_layers = 0
    
    def _initialize_alphabet(self) -> Dict:
        """Inicializon alfabetin e plotë greko-shqip (60 shkronja)"""
        # Greek alphabet (24 letters: α to ω)
        greek = [chr(i) for i in range(0x03B1, 0x03C9 + 1)]
        
        # Albanian alphabet (36 letters including digraphs)
        albanian = [
            'a', 'b', 'c', 'ç', 'd', 'dh', 'e', 'ë', 'f', 'g', 'gj', 'h',
            'i', 'j', 'k', 'l', 'll', 'm', 'n', 'nj', 'o', 'p', 'q', 'r',
            'rr', 's', 'sh', 't', 'th', 'u', 'v', 'x', 'xh', 'y', 'z', 'zh'
        ]
        
        return {
            'greek': greek,
            'albanian': albanian,
            'all': greek + albanian,
            'size': len(greek) + len(albanian),  # 60
            'digraphs': ['dh', 'gj', 'll', 'nj', 'rr', 'sh', 'th', 'xh', 'zh']
        }
    
    def initialize_base_layers(self):
        """Krijon 60 shtresat bazë për çdo shkronjë"""
        for letter in self.alphabet['all']:
            self.layers[letter] = self._create_letter_layer(letter)
        
        print(f"✓ Initialized {len(self.layers)} base layers")
    
    def _get_phonetic_properties(self, letter: str) -> Dict:
        """Merr vetitë fonetike të një shkronje"""
        if letter in PHONETIC_PROPERTIES:
            return PHONETIC_PROPERTIES[letter]
        
        # Default properties for consonants
        return {
            'type': 'consonant',
            'frequency': 0.5,
            'voiced': True,
            'place': 'alveolar',
            'complexity': 1.0
        }
    
    def _create_letter_layer(self, letter: str) -> Callable:
        """Krijon një shtresë matematikore unike për çdo shkronjë"""
        # Create unique hash for letter
        letter_hash = int(hashlib.md5(letter.encode()).hexdigest()[:8], 16)
        normalized_hash = letter_hash / (16 ** 8)  # Normalize to [0, 1]
        
        if letter in self.alphabet['greek']:
            # Greek letters - Pure mathematics
            return self._create_greek_layer(letter, normalized_hash)
        else:
            # Albanian letters - Mathematics + Phonetics
            return self._create_albanian_layer(letter, normalized_hash)
    
    def _create_greek_layer(self, letter: str, letter_hash: float) -> Callable:
        """Krijon shtresë për shkronjat greke (matematikë e pastër)"""
        
        layer_functions = {
            'α': lambda x, h=letter_hash: np.exp(1j * h * np.pi) * x,  # Quantum
            'β': lambda x, h=letter_hash: x / (1 + np.exp(-h * x)),  # Beta distribution
            'γ': lambda x, h=letter_hash: np.log1p(np.abs(x) + h),  # Gamma function
            'δ': lambda x, h=letter_hash: x * (1 if np.abs(x) < h else 0),  # Dirac delta
            'ε': lambda x, h=letter_hash: x + h * 1e-6,  # Epsilon (infinitesimal)
            'ζ': lambda x, h=letter_hash: np.sum([1/n**x for n in range(1, 10)]) if np.isscalar(x) else x,  # Zeta
            'η': lambda x, h=letter_hash: np.tanh(h * x),  # Eta invariant
            'θ': lambda x, h=letter_hash: np.cos(h * np.pi * x),  # Theta wave
            'ι': lambda x, h=letter_hash: x + h * 1e-10,  # Iota (very small)
            'κ': lambda x, h=letter_hash: x * np.exp(-h * x**2),  # Kappa curvature
            'λ': lambda x, h=letter_hash: (lambda f: f(f))(lambda f: h * x),  # Lambda calculus
            'μ': lambda x, h=letter_hash: x * h,  # Mu measure
            'ν': lambda x, h=letter_hash: np.fft.fft(np.atleast_1d(x))[0] if hasattr(x, '__len__') else x * h,  # Nu frequency
            'ξ': lambda x, h=letter_hash: x + 1j * h,  # Xi complex
            'ο': lambda x, h=letter_hash: np.floor(x * h) / h if h > 0 else x,  # Omicron order
            'π': lambda x, h=letter_hash: np.sin(np.pi * h * x),  # Pi circular
            'ρ': lambda x, h=letter_hash: x * np.exp(-np.abs(x) * h),  # Rho density
            'σ': lambda x, h=letter_hash: x ** 2 * h,  # Sigma algebra
            'τ': lambda x, h=letter_hash: x * np.exp(1j * h * 2 * np.pi),  # Tau time
            'υ': lambda x, h=letter_hash: x ** (1 + h),  # Upsilon higher order
            'φ': lambda x, h=letter_hash: x * (1 + np.sqrt(5)) / 2,  # Phi golden ratio
            'χ': lambda x, h=letter_hash: 1 if x > h else 0,  # Chi characteristic
            'ψ': lambda x, h=letter_hash: np.sin(h * x) * np.exp(-x**2),  # Psi wavelet
            'ω': lambda x, h=letter_hash: np.tanh(h * x) * np.sign(x),  # Omega limit
        }
        
        return layer_functions.get(letter, lambda x: x)
    
    def _create_albanian_layer(self, letter: str, letter_hash: float) -> Callable:
        """Krijon shtresë për shkronjat shqipe (matematikë + fonetikë)"""
        phonetic = self._get_phonetic_properties(letter)
        
        def albanian_layer(x, h=letter_hash, props=phonetic):
            # Base transformation
            base = np.sin(h * 2 * np.pi * np.atleast_1d(x).astype(float))
            
            # Modify by phonetic type
            if props['type'] == 'vowel':
                # Vowels create smooth, harmonic transformations
                openness_factor = {'open': 1.0, 'mid': 0.7, 'close': 0.4}.get(props.get('openness', 'mid'), 0.7)
                result = base * np.exp(1j * props['frequency'] * np.pi) * openness_factor
            elif props.get('digraph'):
                # Digraphs create complex, multi-phase transformations
                complexity = props.get('complexity', 1.5)
                result = base * (1 + 1j * complexity * h) * props['frequency']
            else:
                # Regular consonants
                result = base * np.tanh(props['frequency'] * h)
            
            return result.real if np.isscalar(x) else result
        
        return albanian_layer
    
    def _decompose_word(self, word: str) -> List[str]:
        """Zbërthen një fjalë në shkronjat e saj (duke trajtuar digrafët)"""
        letters = []
        word_lower = word.lower()
        i = 0
        
        while i < len(word_lower):
            # Check for Albanian digraphs (2-character combinations)
            if i + 1 < len(word_lower):
                digraph = word_lower[i:i+2]
                if digraph in self.alphabet['digraphs']:
                    letters.append(digraph)
                    i += 2
                    continue
            
            # Single letter
            letters.append(word_lower[i])
            i += 1
        
        return letters
    
    def compose(self, word: str) -> Callable:
        """
        Krijon një shtresë të re nga një fjalë
        
        Example:
            "dritë" → Composed layer from d, r, i, t, ë
            "αβγ" → Composed layer from α, β, γ
        """
        letters = self._decompose_word(word)
        
        # Get individual layer functions
        letter_functions = []
        for letter in letters:
            if letter in self.layers:
                letter_functions.append(self.layers[letter])
            elif letter in self.alphabet['greek'] or letter in [chr(i) for i in range(0x03B1, 0x03C9 + 1)]:
                # Create Greek layer on-the-fly
                self.layers[letter] = self._create_letter_layer(letter)
                letter_functions.append(self.layers[letter])
        
        if not letter_functions:
            return lambda x: x  # Identity function if no valid letters
        
        # Compose layers: f_word(x) = f_n(f_{n-1}(...f_1(x)))
        def composed_function(x, funcs=letter_functions):
            result = x
            for func in funcs:
                try:
                    result = func(result)
                except Exception:
                    pass  # Continue with current result if a layer fails
            return result
        
        # Register the new layer
        layer_name = f"composed_{word}"
        self.layers[layer_name] = composed_function
        self.total_composed_layers += 1
        
        # Log history
        self.layer_history.append({
            'word': word,
            'letters': letters,
            'layer_name': layer_name,
            'timestamp': datetime.now().isoformat()
        })
        
        return composed_function
    
    def get_layer_stats(self) -> Dict:
        """Merr statistikat e sistemit të shtresave"""
        return {
            'total_base_layers': self.total_base_layers,
            'total_composed_layers': self.total_composed_layers,
            'total_layers': len(self.layers),
            'greek_letters': len(self.alphabet['greek']),
            'albanian_letters': len(self.alphabet['albanian']),
            'possible_2_combinations': 60 ** 2,  # 3,600
            'possible_3_combinations': 60 ** 3,  # 216,000
            'possible_7_combinations': 60 ** 7,  # 2.8 trillion
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CLASS: DigraphLayer - SHTRESAT E DIGRAFËVE
# ═══════════════════════════════════════════════════════════════════════════════

class DigraphLayer:
    """
    Layer për digrafët shqip (dh, gj, ll, nj, rr, sh, th, xh, zh)
    9 specialized mathematical operators
    """
    
    def __init__(self, digraph: str):
        self.digraph = digraph
        self.phonetic_map = {
            'dh': {'type': 'voiced_dental', 'angle': np.pi/4},
            'gj': {'type': 'voiced_palatal', 'angle': np.pi/3},
            'll': {'type': 'geminate_lateral', 'angle': np.pi/6},
            'nj': {'type': 'palatal_nasal', 'angle': np.pi/5},
            'rr': {'type': 'alveolar_trill', 'angle': 2*np.pi/5},
            'sh': {'type': 'voiceless_palatal', 'angle': np.pi/2},
            'th': {'type': 'voiceless_dental', 'angle': np.pi/7},
            'xh': {'type': 'voiced_palatal_affricate', 'angle': 3*np.pi/4},
            'zh': {'type': 'voiced_palatal_fricative', 'angle': 2*np.pi/3}
        }
        self.matrix = self._create_matrix()
    
    def _create_matrix(self) -> np.ndarray:
        """Krijon matricën transformuese për digrapin"""
        if self.digraph not in self.phonetic_map:
            return np.eye(3)
        
        angle = self.phonetic_map[self.digraph]['angle']
        
        # Create rotation matrix based on phonetic angle
        return np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle), np.cos(angle), 0],
            [0, 0, 1]
        ])
    
    def transform(self, x: np.ndarray) -> np.ndarray:
        """Transformo të dhënat sipas karakteristikave të digrafit"""
        x_array = np.atleast_1d(x).astype(float)
        
        # Pad or truncate to 3D for matrix multiplication
        if len(x_array) < 3:
            x_padded = np.pad(x_array, (0, 3 - len(x_array)))
        else:
            x_padded = x_array[:3]
        
        # Apply transformation
        transformed = np.dot(self.matrix, x_padded)
        
        return transformed[:len(np.atleast_1d(x))]


# ═══════════════════════════════════════════════════════════════════════════════
# INTEGRATION CONFIG GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_integration_config() -> Dict:
    """Generate configuration for integrating with existing ASI Trinity system"""
    
    config = {
        "version": "2.0.0",
        "name": "60-Layer Alphabetic Mathematical Orchestrator",
        "description": "Integration of Greek (24) + Albanian (36) = 60 base mathematical layers",
        
        "integration_points": {
            "alba": {
                "trigger": "When geodesic contains 'alba' or 'managers'",
                "action": "Activate data collection from open sources",
                "parameters": "Use invariant value as collection depth",
                "associated_layers": ["α", "λ", "β", "a"]
            },
            "albi": {
                "trigger": "When geodesic contains 'albi' or 'personas'",
                "action": "Activate creative dialogue formulation",
                "parameters": "Use correlation value as creativity level",
                "associated_layers": ["α", "λ", "β", "i"]
            },
            "jona": {
                "trigger": "When manifold curvature > 0.4",
                "action": "Activate neural array processing",
                "parameters": "Curvature determines processing depth",
                "associated_layers": ["j", "o", "n", "a"]
            },
            "asi_trinity": {
                "trigger": "Always active (fallback)",
                "action": "Generate final response",
                "parameters": "Certainty from decision determines polish level",
                "associated_layers": ["α", "σ", "ι"]
            }
        },
        
        "layer_taxonomy": {
            "quantum": ["α", "β", "γ", "δ", "ω"],
            "fractal": ["ζ", "ξ", "φ", "ç", "xh"],
            "algebraic": ["ε", "η", "θ", "μ", "σ"],
            "topological": ["κ", "λ", "τ", "υ", "ψ"],
            "phonetic_vowels": ["a", "e", "ë", "i", "o", "u", "y"],
            "phonetic_digraphs": ["dh", "gj", "ll", "nj", "rr", "sh", "th", "xh", "zh"]
        },
        
        "mapping_rules": {
            "full_process": {
                "components": ["alba", "albi", "jona", "labs", "personas"],
                "display": "Show complete pipeline visualization",
                "delay": "Allow real-time process display",
                "layer_depth": 7
            },
            "hybrid_process": {
                "components": ["albi", "asi_trinity"],
                "display": "Show creative process + final answer",
                "delay": "Brief process glimpse",
                "layer_depth": 4
            },
            "direct_answer": {
                "components": ["asi_trinity"],
                "display": "Clean, direct response",
                "delay": "Minimal",
                "layer_depth": 2
            }
        },
        
        "monitoring_metrics": {
            "mathematical_metrics": [
                "manifold_curvature",
                "geodesic_length",
                "emergent_pattern_count",
                "lyapunov_exponents",
                "group_representation_traces",
                "letter_activation_frequency"
            ],
            "system_metrics": [
                "component_activation_frequency",
                "decision_certainty_over_time",
                "user_feedback_correlation",
                "layer_composition_efficiency"
            ]
        },
        
        "layer_statistics": {
            "greek_base_layers": 24,
            "albanian_base_layers": 36,
            "total_base_layers": 60,
            "possible_2_letter_combinations": 3600,
            "possible_3_letter_combinations": 216000,
            "possible_7_letter_combinations": "2.8 trillion",
            "words_in_albanian_language": "~450,000",
            "potential_word_layers": "infinite"
        }
    }
    
    return config


def create_docker_integration() -> str:
    """Create Docker integration setup"""
    
    docker_config = """# Dockerfile for 60-Layer Mathematical Orchestrator
# Albanian-Greek Alphabetic Layer System

FROM python:3.11-slim

WORKDIR /app

# Install mathematical dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    libopenblas-dev \\
    && rm -rf /var/lib/apt/lists/*

# Copy orchestrator files
COPY integration_guide.py /app/
COPY mathematical_layers.py /app/
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir \\
    numpy==1.24.0 \\
    scipy==1.10.0 \\
    sympy==1.11.1 \\
    networkx==3.0

# Create mount points for system integration
VOLUME ["/app/integration", "/app/logs", "/app/layers"]

# Environment variables
ENV ALPHABETIC_LAYERS=60
ENV GREEK_LETTERS=24
ENV ALBANIAN_LETTERS=36

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "from integration_guide import AlbanianGreekLayerSystem; s=AlbanianGreekLayerSystem(); print(f'Loaded {len(s.layers)} layers')" || exit 1

# Default command
CMD ["python", "-c", "from integration_guide import main; main()"]
"""
    
    return docker_config


def create_startup_script() -> str:
    """Create startup script for Mathematical Orchestrator"""
    
    startup_script = """#!/bin/bash
# Startup script for 60-Layer Mathematical Orchestrator
# Albanian-Greek Alphabetic Layer System

echo "════════════════════════════════════════════════════════════"
echo "  60-LAYER MATHEMATICAL ORCHESTRATOR"
echo "  Greek (24) + Albanian (36) = 60 Base Layers"
echo "════════════════════════════════════════════════════════════"

# Check dependencies
python -c "import numpy, scipy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing mathematical dependencies..."
    pip install numpy scipy sympy networkx
fi

# Set Python path
export PYTHONPATH=${PYTHONPATH}:$(pwd)

# Start integration service
python - << 'EOF'
import sys
sys.path.insert(0, '.')

from integration_guide import AlbanianGreekLayerSystem

# Initialize the 60-layer system
system = AlbanianGreekLayerSystem()

print(f"\\n✓ Initialized {len(system.layers)} base layers")
print(f"  - Greek layers: {len(system.alphabet['greek'])}")
print(f"  - Albanian layers: {len(system.alphabet['albanian'])}")

# Test with some Albanian words
test_words = ['dritë', 'deti', 'qielli', 'dielli', 'yjet']
print(f"\\nTesting word-to-layer composition:")

for word in test_words:
    layer = system.compose(word)
    test_result = layer(1.0)
    print(f"  '{word}' → layer result: {test_result:.4f}")

stats = system.get_layer_stats()
print(f"\\n📊 Layer Statistics:")
print(f"  Total layers: {stats['total_layers']}")
print(f"  Base layers: {stats['total_base_layers']}")
print(f"  Composed layers: {stats['total_composed_layers']}")
print(f"  Possible 2-letter combinations: {stats['possible_2_combinations']:,}")

print("\\n✅ 60-Layer Mathematical Orchestrator is ready!")
print("═══════════════════════════════════════════════════════════")
EOF

echo "Mathematical Orchestrator integration complete!"
"""
    
    return startup_script


# ═══════════════════════════════════════════════════════════════════════════════
# WORD-TO-LAYER SYSTEM
# ═══════════════════════════════════════════════════════════════════════════════

def word_to_layer(word: str, system: AlbanianGreekLayerSystem = None) -> Callable:
    """
    Konverton një fjalë në një shtresë matematikore
    
    Examples:
        "dritë" → layer që kombinon d, r, i, t, ë
        "deti" → layer që kombinon d, e, t, i
        "αβγ" → layer që kombinon α, β, γ
    """
    if system is None:
        system = AlbanianGreekLayerSystem()
    
    return system.compose(word)


def generate_layers_from_text(text: str, max_layers: int = 100) -> List[Dict]:
    """
    Gjeneron shtresa të reja nga një tekst
    
    Returns list of layer dictionaries with metadata
    """
    system = AlbanianGreekLayerSystem()
    
    # Tokenize text (simple word splitting)
    words = [w.strip('.,!?;:"\'()[]{}') for w in text.split() if len(w) > 1]
    words = list(dict.fromkeys(words))[:max_layers]  # Remove duplicates, limit count
    
    layers = []
    
    for word in words:
        layer = system.compose(word)
        letters = system._decompose_word(word)
        
        layers.append({
            'word': word,
            'letters': letters,
            'letter_count': len(letters),
            'layer_function': layer,
            'test_output': float(np.real(layer(1.0)))
        })
    
    return layers


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Generate all integration files and demonstrate the system"""
    
    print("═" * 70)
    print("  GENERATING 60-LAYER ALPHABETIC MATHEMATICAL ORCHESTRATOR")
    print("  Greek (24) + Albanian (36) = 60 Base Layers")
    print("═" * 70)
    
    # Determine output directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, 'integration_output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Save config
    config = generate_integration_config()
    config_path = os.path.join(output_dir, 'integration_config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"✓ Created {config_path}")
    
    # 2. Save Docker config
    docker_config = create_docker_integration()
    docker_path = os.path.join(output_dir, 'Dockerfile.mathematical')
    with open(docker_path, 'w', encoding='utf-8') as f:
        f.write(docker_config)
    print(f"✓ Created {docker_path}")
    
    # 3. Create startup script
    startup_script = create_startup_script()
    startup_path = os.path.join(output_dir, 'start_mathematical.sh')
    with open(startup_path, 'w', encoding='utf-8') as f:
        f.write(startup_script)
    print(f"✓ Created {startup_path}")
    
    # 4. Initialize and test the system
    print("\n" + "─" * 70)
    print("INITIALIZING 60-LAYER SYSTEM...")
    print("─" * 70)
    
    system = AlbanianGreekLayerSystem()
    
    # Test individual layers
    print("\n📝 Testing individual letter layers:")
    test_letters = ['α', 'β', 'γ', 'a', 'dh', 'll', 'rr']
    for letter in test_letters:
        if letter in system.layers:
            result = system.layers[letter](1.0)
            print(f"  {letter}: f(1.0) = {np.real(result):.6f}")
    
    # Test word composition
    print("\n📚 Testing word-to-layer composition:")
    test_words = ['dritë', 'deti', 'qielli', 'dielli', 'yjet', 'shqipëri', 'matematikë']
    for word in test_words:
        layer = system.compose(word)
        result = layer(1.0)
        letters = system._decompose_word(word)
        print(f"  '{word}' ({len(letters)} letters): f(1.0) = {np.real(result):.6f}")
    
    # Test Greek combinations
    print("\n🏛️ Testing Greek letter compositions:")
    greek_words = ['αβγ', 'φψω', 'πρσ']
    for word in greek_words:
        layer = system.compose(word)
        result = layer(1.0)
        print(f"  '{word}': f(1.0) = {np.real(result):.6f}")
    
    # Print statistics
    stats = system.get_layer_stats()
    print("\n" + "═" * 70)
    print("📊 LAYER STATISTICS")
    print("═" * 70)
    print(f"  Greek base layers:     {stats['greek_letters']}")
    print(f"  Albanian base layers:  {stats['albanian_letters']}")
    print(f"  Total base layers:     {stats['total_base_layers']}")
    print(f"  Composed layers:       {stats['total_composed_layers']}")
    print(f"  Total layers now:      {stats['total_layers']}")
    print(f"\n  Possible combinations:")
    print(f"    2-letter: {stats['possible_2_combinations']:,}")
    print(f"    3-letter: {stats['possible_3_combinations']:,}")
    print(f"    7-letter: {stats['possible_7_combinations']:,}")
    
    print("\n" + "═" * 70)
    print("✅ INTEGRATION COMPLETE")
    print("═" * 70)
    print(f"\nOutput files saved to: {output_dir}")
    print("\nTo integrate with your existing system:")
    print("1. Import: from integration_guide import AlbanianGreekLayerSystem")
    print("2. Initialize: system = AlbanianGreekLayerSystem()")
    print("3. Compose: layer = system.compose('your_word')")
    print("4. Apply: result = layer(input_data)")
    print("\n🧮 The system now makes decisions based on pure mathematics!")
    print("   60 base layers → ∞ possible compositions")


if __name__ == "__main__":
    main()
