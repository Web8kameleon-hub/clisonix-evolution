"""
OCEAN TRANSLATOR MODULE
=======================
Auto-translate any language to/from English

Uses googletrans (Google Translate backend)
Supports 100+ languages including Albanian (sq), German (de), etc.
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger("ocean_translator")

# Try to import googletrans
try:
    from googletrans import Translator as GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    logger.warning("googletrans not installed. Run: pip install googletrans==4.0.2")


# Language codes
LANGUAGE_CODES = {
    "albanian": "sq",
    "shqip": "sq",
    "english": "en",
    "anglisht": "en",
    "german": "de",
    "gjermanisht": "de",
    "italian": "it",
    "italisht": "it",
    "french": "fr",
    "frengjisht": "fr",
    "spanish": "es",
    "spanjisht": "es",
    "portuguese": "pt",
    "turkish": "tr",
    "turqisht": "tr",
    "greek": "el",
    "greqisht": "el",
    "arabic": "ar",
    "arabisht": "ar",
    "chinese": "zh-CN",
    "kinezisht": "zh-CN",
    "japanese": "ja",
    "japonisht": "ja",
    "korean": "ko",
    "russian": "ru",
    "rusisht": "ru",
    "serbian": "sr",
    "serbisht": "sr",
    "croatian": "hr",
    "kroatisht": "hr",
    "macedonian": "mk",
    "maqedonisht": "mk",
    "bulgarian": "bg",
    "bullgarisht": "bg",
    "romanian": "ro",
    "rumanisht": "ro",
    "polish": "pl",
    "polonisht": "pl",
    "dutch": "nl",
    "holandisht": "nl",
    "swedish": "sv",
    "suedisht": "sv",
    "norwegian": "no",
    "norvegjisht": "no",
    "danish": "da",
    "danisht": "da",
    "finnish": "fi",
    "finlandisht": "fi",
    "hungarian": "hu",
    "hungarisht": "hu",
    "czech": "cs",
    "cekisht": "cs",
    "slovak": "sk",
    "slovakisht": "sk",
    "slovenian": "sl",
    "slovenisht": "sl",
    "ukrainian": "uk",
    "ukrainisht": "uk",
    "vietnamese": "vi",
    "vietnamese": "vi",
    "thai": "th",
    "indonesian": "id",
    "malay": "ms",
    "hindi": "hi",
    "bengali": "bn",
    "hebrew": "he",
    "persian": "fa",
}

# Strong language indicators for detection
LANGUAGE_INDICATORS = {
    "sq": [
        "përshëndetje", "pershendetje", "tungjatjeta", "mirëdita", "miredita",
        "faleminderit", "shqip", "çfarë", "cfare", "është", "eshte",
        "mund", "jam", "jemi", "kemi", "duhet", "dua", "dëshiroj",
        "pse", "ku", "kur", "si", "sa", "cilat", "cili", "kush",
        "shpjego", "thuaj", "trego", "ndihmo", "për", "nga", "me", "në",
        "dhe", "por", "ose", "nëse", "atëherë", "gjithashtu", "vetëm",
        "shumë", "pak", "mirë", "keq", "bukur", "i madh", "i vogël"
    ],
    "de": [
        "hallo", "guten", "morgen", "tag", "abend", "nacht", "danke", "bitte",
        "was", "wie", "warum", "wann", "wo", "wer", "welche", "welcher",
        "können", "müssen", "sollen", "werden", "haben", "sein",
        "ich", "du", "er", "sie", "es", "wir", "ihr", "sie",
        "und", "oder", "aber", "wenn", "weil", "dass", "damit",
        "sehr", "viel", "wenig", "gut", "schlecht", "schön", "groß", "klein"
    ],
    "it": [
        "ciao", "buongiorno", "buonasera", "grazie", "prego",
        "cosa", "come", "perché", "quando", "dove", "chi", "quale",
        "posso", "devo", "voglio", "sono", "sei", "è", "siamo",
        "io", "tu", "lui", "lei", "noi", "voi", "loro",
        "e", "o", "ma", "se", "perché", "che", "molto", "poco"
    ],
    "fr": [
        "bonjour", "bonsoir", "salut", "merci", "s'il vous plaît",
        "quoi", "comment", "pourquoi", "quand", "où", "qui", "quel",
        "je peux", "je dois", "je veux", "je suis", "tu es", "il est",
        "je", "tu", "il", "elle", "nous", "vous", "ils", "elles",
        "et", "ou", "mais", "si", "parce que", "que", "très", "peu"
    ],
    "es": [
        "hola", "buenos días", "buenas tardes", "gracias", "por favor",
        "qué", "cómo", "por qué", "cuándo", "dónde", "quién", "cuál",
        "puedo", "debo", "quiero", "soy", "eres", "es", "somos",
        "yo", "tú", "él", "ella", "nosotros", "vosotros", "ellos",
        "y", "o", "pero", "si", "porque", "que", "muy", "poco"
    ],
    "tr": [
        "merhaba", "selam", "günaydın", "teşekkürler", "lütfen",
        "ne", "nasıl", "neden", "ne zaman", "nerede", "kim", "hangi",
        "ben", "sen", "o", "biz", "siz", "onlar",
        "ve", "veya", "ama", "eğer", "çünkü", "çok", "az"
    ],
    "ru": [
        "привет", "здравствуйте", "спасибо", "пожалуйста",
        "что", "как", "почему", "когда", "где", "кто", "какой",
        "я", "ты", "он", "она", "мы", "вы", "они",
        "и", "или", "но", "если", "потому что", "очень", "мало"
    ],
    "ar": [
        "مرحبا", "شكرا", "من فضلك",
        "ماذا", "كيف", "لماذا", "متى", "أين", "من", "أي",
        "أنا", "أنت", "هو", "هي", "نحن", "أنتم", "هم"
    ],
    "zh-CN": [
        "你好", "谢谢", "请",
        "什么", "怎么", "为什么", "什么时候", "哪里", "谁", "哪个",
        "我", "你", "他", "她", "我们", "你们", "他们"
    ]
}


class OceanTranslator:
    """Multi-language translator for Ocean"""
    
    def __init__(self):
        self.available = TRANSLATOR_AVAILABLE
        self._cache = {}  # Simple cache for repeated translations
    
    def detect_language(self, text: str) -> str:
        """Detect language from text using pattern matching."""
        text_lower = text.lower()
        
        # Check each language's indicators
        scores = {}
        for lang_code, indicators in LANGUAGE_INDICATORS.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                scores[lang_code] = score
        
        if scores:
            # Return language with highest score
            return max(scores, key=scores.get)
        
        # Default to English if no patterns matched
        return "en"
    
    def translate(self, text: str, source: str = "auto", target: str = "en") -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source: Source language code (or "auto" for auto-detect)
            target: Target language code
            
        Returns:
            Translated text
        """
        if not self.available:
            logger.warning("Translator not available")
            return text
        
        if not text or len(text.strip()) == 0:
            return text
        
        # Don't translate if same language
        if source == target and source != "auto":
            return text
        
        # Check cache
        cache_key = f"{source}:{target}:{text[:50]}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            translator = GoogleTranslator(source=source, target=target)
            result = translator.translate(text)
            
            # Cache result
            self._cache[cache_key] = result
            
            return result
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text
    
    def translate_to_english(self, text: str) -> Tuple[str, str]:
        """
        Translate text to English, return (translated_text, detected_language).
        """
        detected = self.detect_language(text)
        
        if detected == "en":
            return text, "en"
        
        translated = self.translate(text, source=detected, target="en")
        return translated, detected
    
    def translate_from_english(self, text: str, target: str) -> str:
        """
        Translate English text to target language.
        """
        if target == "en":
            return text
        
        return self.translate(text, source="en", target=target)
    
    def smart_translate(self, query: str, response: str) -> Tuple[str, str, str]:
        """
        Smart translation flow:
        1. Detect query language
        2. If not English, translate query to English
        3. Translate response back to query language
        
        Returns: (translated_response, original_lang, english_query)
        """
        original_lang = self.detect_language(query)
        
        if original_lang == "en":
            # English query - return response as-is
            return response, "en", query
        
        # Translate query to English for processing (if needed)
        english_query = self.translate(query, source=original_lang, target="en")
        
        # Translate response back to user's language
        translated_response = self.translate(response, source="en", target=original_lang)
        
        return translated_response, original_lang, english_query


# Singleton instance
_translator = None

def get_translator() -> OceanTranslator:
    """Get singleton translator instance."""
    global _translator
    if _translator is None:
        _translator = OceanTranslator()
    return _translator


# Quick functions for convenience
def translate(text: str, source: str = "auto", target: str = "en") -> str:
    """Quick translate function."""
    return get_translator().translate(text, source, target)

def detect_language(text: str) -> str:
    """Quick detect language function."""
    return get_translator().detect_language(text)

def to_english(text: str) -> Tuple[str, str]:
    """Quick translate to English."""
    return get_translator().translate_to_english(text)

def from_english(text: str, target: str) -> str:
    """Quick translate from English."""
    return get_translator().translate_from_english(text, target)


if __name__ == "__main__":
    # Test the translator
    translator = OceanTranslator()
    
    tests = [
        ("Hello, how are you?", "en"),
        ("Përshëndetje, si jeni?", "sq"),
        ("Hallo, wie geht es dir?", "de"),
        ("Ciao, come stai?", "it"),
        ("Bonjour, comment allez-vous?", "fr"),
        ("Hola, ¿cómo estás?", "es"),
    ]
    
    print("🌍 OCEAN TRANSLATOR TEST\n" + "="*50)
    
    for text, expected_lang in tests:
        detected = translator.detect_language(text)
        print(f"\nText: {text}")
        print(f"Expected: {expected_lang}, Detected: {detected}")
        
        if detected != "en":
            translated, _ = translator.translate_to_english(text)
            print(f"English: {translated}")
