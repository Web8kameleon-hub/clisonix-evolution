"""
TONE GOVERNOR - Professional Tone Control
==========================================
Ensures consistent, appropriate tone in all responses.

Ultra-light: ~60 lines | Tone templates | Style rules
"""

from dataclasses import dataclass
from typing import Dict
from enum import Enum


class ToneStyle(Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    CASUAL = "casual"
    FORMAL = "formal"


@dataclass
class ToneConfig:
    style: ToneStyle
    formality: float  # 0.0 = casual, 1.0 = formal
    warmth: float     # 0.0 = cold, 1.0 = warm
    emoji_allowed: bool
    greeting: str
    closing: str


class ToneGovernor:
    """
    Governs response tone for consistency.
    """
    
    # Predefined tone configurations
    PRESETS: Dict[str, ToneConfig] = {
        "default": ToneConfig(
            style=ToneStyle.PROFESSIONAL,
            formality=0.7,
            warmth=0.6,
            emoji_allowed=True,
            greeting="Përshëndetje!",
            closing="A mund t'ju ndihmoj me diçka tjetër?"
        ),
        "business": ToneConfig(
            style=ToneStyle.FORMAL,
            formality=0.9,
            warmth=0.4,
            emoji_allowed=False,
            greeting="I nderuar,",
            closing="Mbetemi në dispozicionin tuaj."
        ),
        "casual": ToneConfig(
            style=ToneStyle.CASUAL,
            formality=0.3,
            warmth=0.9,
            emoji_allowed=True,
            greeting="Hej! 👋",
            closing="Tregomë nëse të duhet ndonjë gjë tjetër!"
        ),
        "technical": ToneConfig(
            style=ToneStyle.TECHNICAL,
            formality=0.8,
            warmth=0.3,
            emoji_allowed=False,
            greeting="",
            closing=""
        ),
    }
    
    def __init__(self, default_preset: str = "default"):
        self.current = self.PRESETS.get(default_preset, self.PRESETS["default"])
    
    def set_tone(self, preset: str) -> bool:
        """Set tone from preset."""
        if preset in self.PRESETS:
            self.current = self.PRESETS[preset]
            return True
        return False
    
    def get_greeting(self) -> str:
        """Get appropriate greeting."""
        return self.current.greeting
    
    def get_closing(self) -> str:
        """Get appropriate closing."""
        return self.current.closing
    
    def should_use_emoji(self) -> bool:
        """Check if emojis are appropriate."""
        return self.current.emoji_allowed
    
    def get_style_hints(self) -> Dict:
        """Get style hints for response generation."""
        return {
            "style": self.current.style.value,
            "formality": self.current.formality,
            "warmth": self.current.warmth,
            "use_emoji": self.current.emoji_allowed,
        }


# Singleton
_governor = None

def get_tone() -> ToneGovernor:
    global _governor
    if _governor is None:
        _governor = ToneGovernor()
    return _governor
