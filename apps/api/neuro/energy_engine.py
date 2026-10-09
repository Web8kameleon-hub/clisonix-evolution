"""
Energy Engine - Daily Energy Check from Voice/Audio
REAL vocal analysis - pitch, formants, energy
"""

import logging
from typing import Dict, Any
import numpy as np

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

logger = logging.getLogger(__name__)


class EnergyEngine:
    """Analyze daily energy from voice sample - REAL analysis"""
    
    def analyze(self, audio_path: str) -> Dict[str, Any]:
        """
        Analyze energy level from audio sample
        Returns: dominant frequency, vocal tension, emotional tone, energy level
        """
        if not HAS_LIBROSA:
            return {"error": "librosa not installed"}
        
        try:
            # Load real audio
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            
            # 1. DOMINANT FREQUENCY (pitch)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(float(pitch))
            
            if pitch_values:
                dominant_freq = float(np.median(pitch_values))
                pitch_std = float(np.std(pitch_values))
            else:
                dominant_freq = 0.0
                pitch_std = 0.0
            
            # 2. VOCAL TENSION (from spectral features)
            spectral_flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
            spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
            
            # Higher flatness = more tension/stress
            tension_score = spectral_flatness * 100
            
            if tension_score > 70:
                vocal_tension = "high"
            elif tension_score > 40:
                vocal_tension = "moderate"
            else:
                vocal_tension = "low"
            
            # 3. EMOTIONAL TONE (from pitch variation)
            if pitch_std > 50:
                emotional_tone = "expressive"
            elif pitch_std < 20:
                emotional_tone = "monotone"
            else:
                emotional_tone = "balanced"
            
            # 4. ENERGY LEVEL (0-100)
            rms = float(np.mean(librosa.feature.rms(y=y)))
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            
            # Real energy calculation
            energy_level = min(100, (
                (rms * 1000) * 0.4 +
                (dominant_freq / 5) * 0.3 +
                (tempo / 2) * 0.3
            ))
            
            # 5. RECOMMENDED QUICK SOUND (based on energy)
            if energy_level < 30:
                recommended_sound = "energizing_432hz"
                recommendation = "Low energy detected - try 432Hz energizing tone"
            elif energy_level > 70:
                recommended_sound = "calming_528hz"
                recommendation = "High energy - try 528Hz calming tone"
            else:
                recommended_sound = "balancing_396hz"
                recommendation = "Balanced energy - maintain with 396Hz grounding"
            
            return {
                "dominant_frequency_hz": round(dominant_freq, 2),
                "pitch_variation": round(pitch_std, 2),
                "vocal_tension": vocal_tension,
                "tension_score": round(tension_score, 2),
                "emotional_tone": emotional_tone,
                "energy_level": round(energy_level, 2),
                "rms_energy": round(rms * 100, 2),
                "detected_tempo": round(float(tempo), 2),
                "recommended_sound": recommended_sound,
                "recommendation": recommendation
            }
            
        except Exception as e:
            logger.error(f"Energy analysis error: {e}")
            return {"error": str(e)}
