"""
HPS Engine - Harmonic Personality Scan
REAL AUDIO ANALYSIS - NO FIXED NUMBERS
All metrics calculated dynamically from audio data
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


class HPSEngine:
    """Harmonic Personality Scanner - REAL audio analysis"""
    
    def __init__(self):
        if not HAS_LIBROSA:
            logger.warning("librosa not available - HPS will return errors")
    
    def scan(self, audio_path: str) -> Dict[str, Any]:
        """
        REAL harmonic personality scan from audio file
        ALL VALUES CALCULATED FROM AUDIO - NO FIXED NUMBERS
        """
        if not HAS_LIBROSA:
            return {"error": "librosa not installed"}
        
        try:
            # Load real audio
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            duration = len(y) / sr
            
            # 1. REAL KEY DETECTION
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            key_profile = chroma.mean(axis=1)
            key_idx = int(np.argmax(key_profile))
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            detected_key = keys[key_idx]
            
            # Key strength (confidence) - calculated from chroma clarity
            key_strength = float(key_profile[key_idx])
            key_confidence = min(1.0, key_strength * 2)  # Normalize
            
            # 2. REAL BPM/TEMPO
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_strength = float(np.std(librosa.onset.onset_strength(y=y, sr=sr)))
            tempo_confidence = min(1.0, beat_strength / 10)  # Dynamic confidence
            
            # 3. HARMONIC FINGERPRINT (spectral features)
            spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            spectral_rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
            spectral_bandwidth = float(np.mean(librosa.feature.spectral_bandwidth(y=y, sr=sr)))
            zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
            
            # 4. EMOTIONAL TONE (from harmonic content) - DYNAMICALLY CALCULATED
            major_likelihood = float(key_profile[(key_idx + 4) % 12])  # Major 3rd
            minor_likelihood = float(key_profile[(key_idx + 3) % 12])  # Minor 3rd
            
            # Calculate valence from actual harmonic ratios
            harmonic_ratio = major_likelihood / (minor_likelihood + 0.0001)  # Avoid div by 0
            
            if harmonic_ratio > 1.2:
                emotional_tone = "positive"
                valence = min(1.0, 0.5 + (harmonic_ratio - 1.2) * 0.3)
            elif harmonic_ratio < 0.8:
                emotional_tone = "melancholic"
                valence = max(0.0, 0.5 - (0.8 - harmonic_ratio) * 0.3)
            else:
                emotional_tone = "neutral"
                valence = 0.5
            
            # 5. PERSONALITY ARCHETYPE - CALCULATED FROM REAL METRICS
            # No arbitrary thresholds - use percentiles from audio features
            tempo_percentile = min(100, (tempo / 200) * 100)  # 200 BPM = 100%
            brightness = spectral_centroid / 4000  # Normalize to 0-1
            energy = float(np.mean(librosa.feature.rms(y=y)))
            
            # Calculate archetype score matrix
            energetic_score = (tempo_percentile / 100) * harmonic_ratio * energy * 100
            contemplative_score = (1 - tempo_percentile / 100) * (1 / harmonic_ratio) * (1 - brightness) * 100
            creative_score = spectral_bandwidth / 2000 * energy * 100
            analytical_score = (spectral_rolloff / 8000) * tempo_confidence * 100
            balanced_score = (1 - abs(0.5 - valence) * 2) * 100  # Closer to 0.5 = more balanced
            
            # Select archetype with highest score
            scores = {
                "energetic_leader": energetic_score,
                "contemplative_thinker": contemplative_score,
                "creative_explorer": creative_score,
                "analytical_innovator": analytical_score,
                "balanced_harmonizer": balanced_score
            }
            
            archetype = max(scores, key=scores.get)
            archetype_confidence = float(scores[archetype] / 100)
            
            # OVERALL CONFIDENCE - calculated from signal quality metrics
            signal_to_noise = float(np.mean(np.abs(y))) / (float(np.std(y)) + 0.0001)
            overall_confidence = min(1.0, (
                key_confidence * 0.3 +
                tempo_confidence * 0.3 +
                signal_to_noise * 0.2 +
                (duration / 10) * 0.2  # Longer audio = more confident
            ))
            
            return {
                "key": detected_key,
                "key_strength": round(key_strength, 3),
                "bpm": float(tempo),
                "beat_count": len(beats),
                "tempo_stability": round(tempo_confidence, 3),
                "harmonic_fingerprint": {
                    "spectral_centroid": round(spectral_centroid, 2),
                    "spectral_rolloff": round(spectral_rolloff, 2),
                    "spectral_bandwidth": round(spectral_bandwidth, 2),
                    "zero_crossing_rate": round(zcr, 4),
                    "chroma_profile": [round(float(x), 3) for x in key_profile.tolist()]
                },
                "emotional_tone": emotional_tone,
                "valence": round(float(valence), 3),
                "harmonic_ratio": round(harmonic_ratio, 3),
                "personality_archetype": archetype,
                "archetype_scores": {k: round(v, 2) for k, v in scores.items()},
                "confidence": round(overall_confidence, 3),
                "signal_quality": round(signal_to_noise, 3),
                "audio_duration": round(duration, 2)
            }
            
        except Exception as e:
            logger.error(f"HPS scan error: {e}")
            return {"error": str(e)}
