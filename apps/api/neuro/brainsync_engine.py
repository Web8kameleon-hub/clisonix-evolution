"""
BrainSync Engine - REAL binaural beats & isochronic tones
NO MOCK - generates actual audio from user profile
"""

import logging
from typing import Dict, Any
import numpy as np

try:
    import soundfile as sf
    HAS_SOUNDFILE = True
except ImportError:
    HAS_SOUNDFILE = False

logger = logging.getLogger(__name__)


class BrainSyncEngine:
    """Generate personalized brain-sync music - REAL audio synthesis"""
    
    # Brainwave frequency ranges (Hz) - scientific data
    BRAINWAVE_FREQUENCIES = {
        'delta': (0.5, 4),    # Deep sleep
        'theta': (4, 8),      # Meditation, creativity
        'alpha': (8, 13),     # Relaxation, flow state
        'beta': (13, 30),     # Focus, alertness
        'gamma': (30, 100)    # High-level cognition
    }
    
    # Mode to target brainwave mapping
    MODE_TO_BRAINWAVE = {
        'relax': 'alpha',
        'focus': 'beta',
        'sleep': 'delta',
        'motivation': 'beta',
        'creativity': 'theta',
        'recovery': 'alpha'
    }
    
    def __init__(self):
        self.sample_rate = 44100
        self.duration = 300  # 5 minutes default
    
    def generate(self, mode: str, profile: Dict[str, Any]) -> str:
        """
        Generate REAL brain-sync audio
        Uses user's HPS profile to personalize
        Returns: path to generated audio file
        """
        if not HAS_SOUNDFILE:
            raise ImportError("soundfile not installed")
        
        try:
            # 1. Determine target brainwave from mode
            target_wave = self.MODE_TO_BRAINWAVE.get(mode, 'alpha')
            freq_min, freq_max = self.BRAINWAVE_FREQUENCIES[target_wave]
            
            # 2. Extract user's harmonic preferences from profile
            user_key = profile.get('key', 'A')
            user_bpm = profile.get('bpm', 60)
            user_valence = profile.get('valence', 0.5)
            
            # Map key to base frequency (A4 = 440 Hz standard)
            base_freq = self._key_to_frequency(user_key)
            
            # 3. Calculate carrier and beat frequencies
            # Carrier frequency based on user preference
            carrier_freq = base_freq
            
            # Beat frequency (binaural) in target brainwave range
            # Adjusted based on user's BPM preference
            beat_freq = freq_min + ((user_bpm / 180) * (freq_max - freq_min))
            beat_freq = max(freq_min, min(freq_max, beat_freq))  # Clamp
            
            # 4. Generate audio
            t = np.linspace(0, self.duration, int(self.sample_rate * self.duration))
            
            # Left channel: carrier frequency
            left_channel = self._generate_tone(t, carrier_freq, user_valence)
            
            # Right channel: carrier + beat frequency (binaural effect)
            right_channel = self._generate_tone(t, carrier_freq + beat_freq, user_valence)
            
            # 5. Add isochronic pulses for enhanced effect
            pulse_rate = beat_freq
            pulse_pattern = self._generate_isochronic(t, pulse_rate)
            
            # Mix channels with pulsing
            left_mixed = left_channel * pulse_pattern
            right_mixed = right_channel * pulse_pattern
            
            # 6. Add ambient harmony based on user's chroma profile
            if 'harmonic_fingerprint' in profile:
                chroma = profile['harmonic_fingerprint'].get('chroma_profile', [])
                if chroma and len(chroma) > 0:
                    harmony = self._generate_harmony(t, chroma, base_freq)
                    left_mixed += harmony * 0.3
                    right_mixed += harmony * 0.3
            
            # 7. Normalize and combine channels
            stereo = np.column_stack((left_mixed, right_mixed))
            stereo = stereo / np.max(np.abs(stereo))  # Normalize
            stereo = stereo * 0.5  # Reduce volume for safety
            
            # 8. Save to file
            import tempfile
            import os
            output_path = os.path.join(tempfile.gettempdir(), f"brainsync_{mode}_{int(np.random.random()*10000)}.wav")
            sf.write(output_path, stereo, self.sample_rate)
            
            logger.info(f"Generated brain-sync audio: {mode}, {beat_freq:.2f}Hz, {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"BrainSync generation error: {e}")
            raise
    
    def _key_to_frequency(self, key: str) -> float:
        """Convert musical key to frequency (Hz)"""
        # A4 = 440 Hz as reference
        note_offsets = {
            'C': -9, 'C#': -8, 'D': -7, 'D#': -6,
            'E': -5, 'F': -4, 'F#': -3, 'G': -2,
            'G#': -1, 'A': 0, 'A#': 1, 'B': 2
        }
        
        offset = note_offsets.get(key.upper(), 0)
        # A4 = 440 Hz, semitone ratio = 2^(1/12)
        frequency = 440 * (2 ** (offset / 12))
        
        return frequency
    
    def _generate_tone(self, t: np.ndarray, frequency: float, valence: float) -> np.ndarray:
        """Generate pure tone with harmonic richness based on valence"""
        # Base sine wave
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Add harmonics based on valence (positive = richer harmonics)
        if valence > 0.5:
            # Add pleasant harmonics (octave, fifth)
            tone += 0.3 * np.sin(2 * np.pi * (frequency * 2) * t)  # Octave
            tone += 0.2 * np.sin(2 * np.pi * (frequency * 1.5) * t)  # Fifth
        else:
            # Simpler tone for melancholic
            tone += 0.2 * np.sin(2 * np.pi * (frequency * 2) * t)
        
        # Apply fade in/out
        fade_samples = int(self.sample_rate * 2)  # 2 second fade
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        
        tone[:fade_samples] *= fade_in
        tone[-fade_samples:] *= fade_out
        
        return tone
    
    def _generate_isochronic(self, t: np.ndarray, pulse_rate: float) -> np.ndarray:
        """Generate isochronic pulse pattern"""
        # Square wave modulation at pulse_rate
        pulse = np.sin(2 * np.pi * pulse_rate * t)
        pulse = (pulse > 0).astype(float)  # Convert to square wave
        
        # Smooth edges
        pulse = pulse * 0.5 + 0.5  # Offset to 0.5-1.0 range
        
        return pulse
    
    def _generate_harmony(self, t: np.ndarray, chroma: list, base_freq: float) -> np.ndarray:
        """Generate harmonic content based on chroma profile"""
        harmony = np.zeros_like(t)
        
        # Use chroma values to weight harmonic content
        for i, weight in enumerate(chroma[:12]):  # 12 chromatic notes
            if weight > 0.1:  # Only significant contributions
                harmonic_freq = base_freq * (2 ** (i / 12))  # Chromatic scale
                harmony += float(weight) * np.sin(2 * np.pi * harmonic_freq * t)
        
        # Normalize
        if np.max(np.abs(harmony)) > 0:
            harmony = harmony / np.max(np.abs(harmony))
        
        return harmony
