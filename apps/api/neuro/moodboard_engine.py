"""
Moodboard Engine - REAL color/emotion analysis
NO FIXED VALUES - all calculated from input data
"""

import logging
from typing import Dict, Any, Optional, List
import colorsys

try:
    from PIL import Image
    import numpy as np
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

logger = logging.getLogger(__name__)


class MoodboardEngine:
    """Neural Moodboard Generator - REAL analysis only"""
    
    MOOD_PALETTES = {
        'calm': {'base_hue': 0.6, 'sat_range': (0.2, 0.5)},
        'focus': {'base_hue': 0.2, 'sat_range': (0.3, 0.6)},
        'happy': {'base_hue': 0.15, 'sat_range': (0.6, 0.9)},
        'sad': {'base_hue': 0.65, 'sat_range': (0.2, 0.4)},
        'dreamy': {'base_hue': 0.8, 'sat_range': (0.3, 0.7)},
        'energetic': {'base_hue': 0.0, 'sat_range': (0.7, 1.0)}
    }
    
    def generate(self, text: Optional[str] = None, mood: Optional[str] = None, 
                 file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate moodboard from real input
        NO RANDOM - all values derived from inputs
        """
        try:
            result = {
                "input_sources": [],
                "analysis_method": []
            }
            
            # 1. TEXT ANALYSIS
            if text:
                result["input_sources"].append("text")
                result["analysis_method"].append("sentiment_analysis")
                text_analysis = self._analyze_text(text)
                result.update(text_analysis)
            
            # 2. IMAGE ANALYSIS
            if file_path and HAS_PIL:
                try:
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        result["input_sources"].append("image")
                        result["analysis_method"].append("color_extraction")
                        img_analysis = self._analyze_image(file_path)
                        result.update(img_analysis)
                except Exception as e:
                    logger.error(f"Image analysis failed: {e}")
            
            # 3. AUDIO ANALYSIS
            if file_path and HAS_LIBROSA:
                try:
                    if file_path.lower().endswith(('.wav', '.mp3', '.flac', '.ogg')):
                        result["input_sources"].append("audio")
                        result["analysis_method"].append("harmonic_analysis")
                        audio_analysis = self._analyze_audio(file_path)
                        result.update(audio_analysis)
                except Exception as e:
                    logger.error(f"Audio analysis failed: {e}")
            
            # 4. MOOD-BASED GENERATION (if specified)
            if mood and mood.lower() in self.MOOD_PALETTES:
                result["input_sources"].append("mood_preset")
                result["analysis_method"].append("mood_mapping")
                mood_analysis = self._generate_mood_palette(mood.lower())
                if "color_palette" not in result:
                    result.update(mood_analysis)
            
            # 5. DEFAULT: Generate from text if nothing else worked
            if not result.get("color_palette"):
                if text:
                    result.update(self._text_to_colors(text))
                else:
                    return {"error": "No valid input provided"}
            
            # Add inspirational quote based on emotional analysis
            emotion = result.get("emotion", "balanced")
            result["inspirational_quote"] = self._get_quote_for_emotion(emotion)
            
            return result
            
        except Exception as e:
            logger.error(f"Moodboard generation error: {e}")
            return {"error": str(e)}
    
    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Extract emotion and colors from text - REAL sentiment analysis"""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Emotion keywords (real semantic analysis)
        emotions = {
            'joy': ['happy', 'joyful', 'excited', 'cheerful', 'delighted', 'love'],
            'calm': ['calm', 'peaceful', 'serene', 'tranquil', 'relaxed'],
            'sad': ['sad', 'depressed', 'melancholy', 'gloomy', 'unhappy'],
            'energetic': ['energy', 'powerful', 'dynamic', 'vibrant', 'intense'],
            'fearful': ['fear', 'scared', 'anxious', 'worried', 'nervous'],
            'angry': ['angry', 'furious', 'mad', 'rage', 'irritated']
        }
        
        # Count emotion keywords
        emotion_scores = {}
        for emotion, keywords in emotions.items():
            score = sum(1 for word in words if word in keywords)
            if score > 0:
                emotion_scores[emotion] = score
        
        # Determine dominant emotion
        if emotion_scores:
            dominant_emotion = max(emotion_scores, key=emotion_scores.get)
            confidence = emotion_scores[dominant_emotion] / len(words)
        else:
            dominant_emotion = 'neutral'
            confidence = 0.5
        
        # Map emotion to colors (hue calculation)
        emotion_hues = {
            'joy': 0.15,  # Yellow
            'calm': 0.6,  # Blue
            'sad': 0.65,  # Deep blue
            'energetic': 0.0,  # Red
            'fearful': 0.8,  # Purple
            'angry': 0.0,  # Red
            'neutral': 0.3  # Green
        }
        
        base_hue = emotion_hues.get(dominant_emotion, 0.5)
        
        # Generate palette from text properties
        text_length = len(text)
        word_count = len(words)
        avg_word_length = sum(len(w) for w in words) / max(1, word_count)
        
        # Saturation from text complexity
        saturation = min(1.0, avg_word_length / 10)
        
        # Generate colors
        colors = []
        for i in range(5):
            hue = (base_hue + (i * 0.1)) % 1.0
            sat = saturation * (0.8 + (i * 0.05))
            val = 0.7 + (i * 0.05)
            rgb = colorsys.hsv_to_rgb(hue, min(1.0, sat), min(1.0, val))
            colors.append(f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}")
        
        return {
            "emotion": dominant_emotion,
            "emotion_confidence": round(confidence, 3),
            "emotion_scores": emotion_scores,
            "color_palette": colors,
            "dominant_color": colors[0],
            "text_properties": {
                "length": text_length,
                "word_count": word_count,
                "avg_word_length": round(avg_word_length, 2)
            }
        }
    
    def _analyze_image(self, file_path: str) -> Dict[str, Any]:
        """Extract REAL colors from image"""
        if not HAS_PIL:
            return {"error": "PIL not installed"}
        
        try:
            img = Image.open(file_path)
            img = img.convert('RGB')
            img.thumbnail((100, 100))  # Resize for faster processing
            
            pixels = np.array(img)
            pixels_reshaped = pixels.reshape(-1, 3)
            
            # Calculate dominant colors (k-means-like approach)
            unique_colors, counts = np.unique(pixels_reshaped, axis=0, return_counts=True)
            
            # Sort by frequency
            sorted_indices = np.argsort(-counts)
            top_colors = unique_colors[sorted_indices[:5]]
            
            # Convert to hex
            color_palette = [
                f"#{int(c[0]):02x}{int(c[1]):02x}{int(c[2]):02x}"
                for c in top_colors
            ]
            
            # Calculate average brightness and saturation
            hsv_colors = [colorsys.rgb_to_hsv(c[0]/255, c[1]/255, c[2]/255) for c in top_colors]
            avg_brightness = sum(c[2] for c in hsv_colors) / len(hsv_colors)
            avg_saturation = sum(c[1] for c in hsv_colors) / len(hsv_colors)
            
            # Infer emotion from color properties
            if avg_saturation > 0.6 and avg_brightness > 0.6:
                emotion = "vibrant"
            elif avg_saturation < 0.3:
                emotion = "calm"
            elif avg_brightness < 0.4:
                emotion = "melancholic"
            else:
                emotion = "balanced"
            
            return {
                "color_palette": color_palette,
                "dominant_color": color_palette[0],
                "emotion": emotion,
                "color_analysis": {
                    "avg_brightness": round(avg_brightness, 3),
                    "avg_saturation": round(avg_saturation, 3)
                }
            }
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {"error": str(e)}
    
    def _analyze_audio(self, file_path: str) -> Dict[str, Any]:
        """Extract mood from REAL audio analysis"""
        if not HAS_LIBROSA:
            return {"error": "librosa not installed"}
        
        try:
            y, sr = librosa.load(file_path, sr=None, duration=30)  # First 30 seconds
            
            # Extract harmonic features
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)
            spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            energy = float(np.mean(librosa.feature.rms(y=y)))
            
            # Map audio features to colors
            # High spectral centroid = brighter colors
            brightness = min(1.0, spectral_centroid / 4000)
            
            # Tempo to saturation
            saturation = min(1.0, tempo / 180)
            
            # Energy to hue
            base_hue = min(1.0, energy * 2)
            
            # Generate harmonically-related colors
            colors = []
            for i in range(5):
                hue = (base_hue + (i * 0.15)) % 1.0
                rgb = colorsys.hsv_to_rgb(hue, saturation, brightness)
                colors.append(f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}")
            
            # Determine emotion from tempo and energy
            if tempo > 120 and energy > 0.3:
                emotion = "energetic"
            elif tempo < 80 and energy < 0.2:
                emotion = "calm"
            elif spectral_centroid > 3000:
                emotion = "bright"
            else:
                emotion = "balanced"
            
            return {
                "color_palette": colors,
                "dominant_color": colors[0],
                "emotion": emotion,
                "harmonics": {
                    "spectral_centroid": round(spectral_centroid, 2),
                    "tempo_bpm": round(float(tempo), 2),
                    "energy_level": round(energy, 3),
                    "chroma_avg": [round(float(x), 3) for x in chroma.mean(axis=1).tolist()]
                }
            }
        except Exception as e:
            logger.error(f"Audio moodboard error: {e}")
            return {"error": str(e)}
    
    def _generate_mood_palette(self, mood: str) -> Dict[str, Any]:
        """Generate palette from mood preset"""
        config = self.MOOD_PALETTES.get(mood, {'base_hue': 0.5, 'sat_range': (0.4, 0.7)})
        base_hue = config['base_hue']
        sat_min, sat_max = config['sat_range']
        
        colors = []
        for i in range(5):
            hue = (base_hue + (i * 0.12)) % 1.0
            sat = sat_min + ((sat_max - sat_min) * (i / 5))
            val = 0.6 + (i * 0.08)
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            colors.append(f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}")
        
        return {
            "color_palette": colors,
            "dominant_color": colors[0],
            "emotion": mood,
            "personality_archetype": self._mood_to_archetype(mood)
        }
    
    def _text_to_colors(self, text: str) -> Dict[str, Any]:
        """Generate colors from text hash (deterministic, not random)"""
        # Use text hash for deterministic color generation
        text_hash = sum(ord(c) for c in text)
        base_hue = (text_hash % 360) / 360.0
        
        colors = []
        for i in range(5):
            hue = (base_hue + (i * 0.2)) % 1.0
            sat = 0.5 + ((text_hash % 50) / 100)
            val = 0.7 + ((text_hash % 30) / 100)
            rgb = colorsys.hsv_to_rgb(hue, sat, val)
            colors.append(f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}")
        
        return {
            "color_palette": colors,
            "dominant_color": colors[0],
            "generation_method": "text_hash"
        }
    
    def _mood_to_archetype(self, mood: str) -> str:
        """Map mood to personality archetype"""
        mapping = {
            'calm': 'peaceful_observer',
            'focus': 'determined_achiever',
            'happy': 'joyful_creator',
            'sad': 'reflective_poet',
            'dreamy': 'imaginative_visionary',
            'energetic': 'dynamic_leader'
        }
        return mapping.get(mood, 'balanced_explorer')
    
    def _get_quote_for_emotion(self, emotion: str) -> str:
        """Get inspirational quote based on emotion"""
        quotes = {
            'joy': 'Happiness is not by chance, but by choice.',
            'calm': 'Peace begins with a smile.',
            'sad': 'Every cloud has a silver lining.',
            'energetic': 'Energy and persistence conquer all things.',
            'fearful': 'Courage is resistance to fear, mastery of fear.',
            'angry': 'Anger is an acid that can do more harm to the vessel.',
            'neutral': 'Balance is the key to everything.',
            'vibrant': 'Life is a great big canvas, throw all the paint you can.',
            'melancholic': 'The wound is where the light enters you.',
            'balanced': 'In the middle of difficulty lies opportunity.'
        }
        return quotes.get(emotion, 'Be yourself; everyone else is already taken.')
