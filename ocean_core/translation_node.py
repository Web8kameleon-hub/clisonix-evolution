#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLISONIX TRANSLATION NODE - Nanogrid Pulse Architecture
========================================================
Ultra-lightweight translation microservice with 60+ languages
Uses dictionary-based translations + fallback to deep-translator
Single API endpoint, minimal memory footprint

Port: 8036
Architecture: Nanogrid Node Pulse
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s")
logger = logging.getLogger("TranslationNode")

PORT = int(os.getenv("TRANSLATION_PORT", "8036"))

# ============================================================================
# 60+ WORLD LANGUAGES - ISO 639-1 Codes
# ============================================================================
SUPPORTED_LANGUAGES = {
    # European Languages
    "en": {"name": "English", "native": "English", "flag": "🇬🇧", "region": "europe"},
    "sq": {"name": "Albanian", "native": "Shqip", "flag": "🇦🇱", "region": "europe"},
    "de": {"name": "German", "native": "Deutsch", "flag": "🇩🇪", "region": "europe"},
    "fr": {"name": "French", "native": "Français", "flag": "🇫🇷", "region": "europe"},
    "it": {"name": "Italian", "native": "Italiano", "flag": "🇮🇹", "region": "europe"},
    "es": {"name": "Spanish", "native": "Español", "flag": "🇪🇸", "region": "europe"},
    "pt": {"name": "Portuguese", "native": "Português", "flag": "🇵🇹", "region": "europe"},
    "nl": {"name": "Dutch", "native": "Nederlands", "flag": "🇳🇱", "region": "europe"},
    "pl": {"name": "Polish", "native": "Polski", "flag": "🇵🇱", "region": "europe"},
    "cs": {"name": "Czech", "native": "Čeština", "flag": "🇨🇿", "region": "europe"},
    "sk": {"name": "Slovak", "native": "Slovenčina", "flag": "🇸🇰", "region": "europe"},
    "hu": {"name": "Hungarian", "native": "Magyar", "flag": "🇭🇺", "region": "europe"},
    "ro": {"name": "Romanian", "native": "Română", "flag": "🇷🇴", "region": "europe"},
    "bg": {"name": "Bulgarian", "native": "Български", "flag": "🇧🇬", "region": "europe"},
    "hr": {"name": "Croatian", "native": "Hrvatski", "flag": "🇭🇷", "region": "europe"},
    "sr": {"name": "Serbian", "native": "Српски", "flag": "🇷🇸", "region": "europe"},
    "sl": {"name": "Slovenian", "native": "Slovenščina", "flag": "🇸🇮", "region": "europe"},
    "mk": {"name": "Macedonian", "native": "Македонски", "flag": "🇲🇰", "region": "europe"},
    "bs": {"name": "Bosnian", "native": "Bosanski", "flag": "🇧🇦", "region": "europe"},
    "el": {"name": "Greek", "native": "Ελληνικά", "flag": "🇬🇷", "region": "europe"},
    "uk": {"name": "Ukrainian", "native": "Українська", "flag": "🇺🇦", "region": "europe"},
    "ru": {"name": "Russian", "native": "Русский", "flag": "🇷🇺", "region": "europe"},
    "be": {"name": "Belarusian", "native": "Беларуская", "flag": "🇧🇾", "region": "europe"},
    "lt": {"name": "Lithuanian", "native": "Lietuvių", "flag": "🇱🇹", "region": "europe"},
    "lv": {"name": "Latvian", "native": "Latviešu", "flag": "🇱🇻", "region": "europe"},
    "et": {"name": "Estonian", "native": "Eesti", "flag": "🇪🇪", "region": "europe"},
    "fi": {"name": "Finnish", "native": "Suomi", "flag": "🇫🇮", "region": "europe"},
    "sv": {"name": "Swedish", "native": "Svenska", "flag": "🇸🇪", "region": "europe"},
    "no": {"name": "Norwegian", "native": "Norsk", "flag": "🇳🇴", "region": "europe"},
    "da": {"name": "Danish", "native": "Dansk", "flag": "🇩🇰", "region": "europe"},
    "is": {"name": "Icelandic", "native": "Íslenska", "flag": "🇮🇸", "region": "europe"},
    "ga": {"name": "Irish", "native": "Gaeilge", "flag": "🇮🇪", "region": "europe"},
    "cy": {"name": "Welsh", "native": "Cymraeg", "flag": "🏴󠁧󠁢󠁷󠁬󠁳󠁿", "region": "europe"},
    "mt": {"name": "Maltese", "native": "Malti", "flag": "🇲🇹", "region": "europe"},
    
    # Asian Languages
    "zh": {"name": "Chinese", "native": "中文", "flag": "🇨🇳", "region": "asia"},
    "ja": {"name": "Japanese", "native": "日本語", "flag": "🇯🇵", "region": "asia"},
    "ko": {"name": "Korean", "native": "한국어", "flag": "🇰🇷", "region": "asia"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "flag": "🇮🇳", "region": "asia"},
    "bn": {"name": "Bengali", "native": "বাংলা", "flag": "🇧🇩", "region": "asia"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "flag": "🇮🇳", "region": "asia"},
    "te": {"name": "Telugu", "native": "తెలుగు", "flag": "🇮🇳", "region": "asia"},
    "mr": {"name": "Marathi", "native": "मराठी", "flag": "🇮🇳", "region": "asia"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "flag": "🇮🇳", "region": "asia"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "flag": "🇮🇳", "region": "asia"},
    "ur": {"name": "Urdu", "native": "اردو", "flag": "🇵🇰", "region": "asia"},
    "th": {"name": "Thai", "native": "ไทย", "flag": "🇹🇭", "region": "asia"},
    "vi": {"name": "Vietnamese", "native": "Tiếng Việt", "flag": "🇻🇳", "region": "asia"},
    "id": {"name": "Indonesian", "native": "Bahasa Indonesia", "flag": "🇮🇩", "region": "asia"},
    "ms": {"name": "Malay", "native": "Bahasa Melayu", "flag": "🇲🇾", "region": "asia"},
    "tl": {"name": "Filipino", "native": "Filipino", "flag": "🇵🇭", "region": "asia"},
    "my": {"name": "Burmese", "native": "မြန်မာ", "flag": "🇲🇲", "region": "asia"},
    "km": {"name": "Khmer", "native": "ខ្មែរ", "flag": "🇰🇭", "region": "asia"},
    "lo": {"name": "Lao", "native": "ລາວ", "flag": "🇱🇦", "region": "asia"},
    "ne": {"name": "Nepali", "native": "नेपाली", "flag": "🇳🇵", "region": "asia"},
    "si": {"name": "Sinhala", "native": "සිංහල", "flag": "🇱🇰", "region": "asia"},
    "ka": {"name": "Georgian", "native": "ქართული", "flag": "🇬🇪", "region": "asia"},
    "hy": {"name": "Armenian", "native": "Հայերdelays", "flag": "🇦🇲", "region": "asia"},
    "az": {"name": "Azerbaijani", "native": "Azərbaycan", "flag": "🇦🇿", "region": "asia"},
    "kk": {"name": "Kazakh", "native": "Қазақ", "flag": "🇰🇿", "region": "asia"},
    "uz": {"name": "Uzbek", "native": "O'zbek", "flag": "🇺🇿", "region": "asia"},
    "mn": {"name": "Mongolian", "native": "Монгол", "flag": "🇲🇳", "region": "asia"},
    
    # Middle Eastern & African Languages
    "ar": {"name": "Arabic", "native": "العربية", "flag": "🇸🇦", "region": "middle_east"},
    "fa": {"name": "Persian", "native": "فارسی", "flag": "🇮🇷", "region": "middle_east"},
    "he": {"name": "Hebrew", "native": "עברית", "flag": "🇮🇱", "region": "middle_east"},
    "tr": {"name": "Turkish", "native": "Türkçe", "flag": "🇹🇷", "region": "middle_east"},
    "sw": {"name": "Swahili", "native": "Kiswahili", "flag": "🇹🇿", "region": "africa"},
    "am": {"name": "Amharic", "native": "አማርኛ", "flag": "🇪🇹", "region": "africa"},
    "ha": {"name": "Hausa", "native": "Hausa", "flag": "🇳🇬", "region": "africa"},
    "yo": {"name": "Yoruba", "native": "Yorùbá", "flag": "🇳🇬", "region": "africa"},
    "ig": {"name": "Igbo", "native": "Igbo", "flag": "🇳🇬", "region": "africa"},
    "zu": {"name": "Zulu", "native": "isiZulu", "flag": "🇿🇦", "region": "africa"},
    "af": {"name": "Afrikaans", "native": "Afrikaans", "flag": "🇿🇦", "region": "africa"},
}

# ============================================================================
# CORE PHRASE DICTIONARY - Common phrases in all languages
# ============================================================================
CORE_PHRASES = {
    "greeting": {
        "en": "Hello! How can I help you?",
        "sq": "Përshëndetje! Si mund t'ju ndihmoj?",
        "de": "Hallo! Wie kann ich Ihnen helfen?",
        "fr": "Bonjour! Comment puis-je vous aider?",
        "it": "Ciao! Come posso aiutarti?",
        "es": "¡Hola! ¿Cómo puedo ayudarte?",
        "pt": "Olá! Como posso ajudá-lo?",
        "nl": "Hallo! Hoe kan ik u helpen?",
        "pl": "Cześć! Jak mogę ci pomóc?",
        "ru": "Привет! Чем могу помочь?",
        "zh": "你好！我能帮你什么？",
        "ja": "こんにちは！何かお手伝いできますか？",
        "ko": "안녕하세요! 무엇을 도와드릴까요?",
        "ar": "مرحباً! كيف يمكنني مساعدتك؟",
        "hi": "नमस्ते! मैं आपकी कैसे मदद कर सकता हूं?",
        "tr": "Merhaba! Size nasıl yardımcı olabilirim?",
    },
    "identity": {
        "en": "I am Curiosity Ocean, an AI assistant by Clisonix.",
        "sq": "Jam Curiosity Ocean, një asistent AI nga Clisonix.",
        "de": "Ich bin Curiosity Ocean, ein KI-Assistent von Clisonix.",
        "fr": "Je suis Curiosity Ocean, un assistant IA de Clisonix.",
        "it": "Sono Curiosity Ocean, un assistente AI di Clisonix.",
        "es": "Soy Curiosity Ocean, un asistente de IA de Clisonix.",
        "pt": "Sou Curiosity Ocean, um assistente de IA da Clisonix.",
        "ru": "Я Curiosity Ocean, ИИ-ассистент от Clisonix.",
        "zh": "我是Curiosity Ocean，Clisonix的AI助手。",
        "ja": "私はCuriosity Ocean、ClisonixのAIアシスタントです。",
        "ko": "저는 Clisonix의 AI 어시스턴트 Curiosity Ocean입니다.",
        "ar": "أنا Curiosity Ocean، مساعد ذكاء اصطناعي من Clisonix.",
        "hi": "मैं Curiosity Ocean हूं, Clisonix का AI सहायक।",
        "tr": "Ben Curiosity Ocean, Clisonix'in yapay zeka asistanıyım.",
    },
    "thanks": {
        "en": "Thank you!",
        "sq": "Faleminderit!",
        "de": "Danke!",
        "fr": "Merci!",
        "it": "Grazie!",
        "es": "¡Gracias!",
        "pt": "Obrigado!",
        "nl": "Dank je!",
        "pl": "Dziękuję!",
        "ru": "Спасибо!",
        "zh": "谢谢！",
        "ja": "ありがとう！",
        "ko": "감사합니다!",
        "ar": "شكراً!",
        "hi": "धन्यवाद!",
        "tr": "Teşekkürler!",
    },
    "goodbye": {
        "en": "Goodbye! Have a great day!",
        "sq": "Mirupafshim! Kalofshi një ditë të mrekullueshme!",
        "de": "Auf Wiedersehen! Einen schönen Tag noch!",
        "fr": "Au revoir! Bonne journée!",
        "it": "Arrivederci! Buona giornata!",
        "es": "¡Adiós! ¡Que tengas un buen día!",
        "pt": "Adeus! Tenha um ótimo dia!",
        "ru": "До свидания! Хорошего дня!",
        "zh": "再见！祝你有美好的一天！",
        "ja": "さようなら！良い一日を！",
        "ko": "안녕히 가세요! 좋은 하루 보내세요!",
        "ar": "وداعاً! أتمنى لك يوماً رائعاً!",
        "hi": "अलविदा! आपका दिन शुभ हो!",
        "tr": "Hoşça kal! İyi günler!",
    },
    "error": {
        "en": "Sorry, I encountered an error. Please try again.",
        "sq": "Na vjen keq, ndodhi një gabim. Ju lutem provoni përsëri.",
        "de": "Entschuldigung, ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.",
        "fr": "Désolé, une erreur s'est produite. Veuillez réessayer.",
        "it": "Mi dispiace, si è verificato un errore. Per favore riprova.",
        "es": "Lo siento, ocurrió un error. Por favor, inténtalo de nuevo.",
        "pt": "Desculpe, ocorreu um erro. Por favor, tente novamente.",
        "ru": "Извините, произошла ошибка. Пожалуйста, попробуйте снова.",
        "zh": "抱歉，发生了错误。请重试。",
        "ja": "申し訳ありません、エラーが発生しました。もう一度お試しください。",
        "ko": "죄송합니다, 오류가 발생했습니다. 다시 시도해 주세요.",
        "ar": "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى.",
        "hi": "क्षमा करें, एक त्रुटि हुई। कृपया पुनः प्रयास करें।",
        "tr": "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.",
    },
}

# ============================================================================
# LANGUAGE DETECTION PATTERNS
# ============================================================================
LANGUAGE_PATTERNS = {
    "sq": ["përshëndetje", "faleminderit", "mirëdita", "kush", "çfarë", "mund", "jam", "është", "shqip"],
    "de": ["wie", "was", "warum", "können", "ich", "bitte", "danke", "guten", "ist", "nicht"],
    "fr": ["bonjour", "merci", "comment", "pourquoi", "quoi", "oui", "non", "bien", "très"],
    "it": ["ciao", "grazie", "come", "perché", "cosa", "buongiorno", "sono", "bene"],
    "es": ["hola", "gracias", "cómo", "qué", "por qué", "buenos", "días", "bien"],
    "pt": ["olá", "obrigado", "como", "porquê", "bom", "dia", "bem"],
    "ru": ["привет", "спасибо", "как", "что", "почему", "хорошо", "да", "нет"],
    "zh": ["你好", "谢谢", "什么", "为什么", "怎么", "好", "是"],
    "ja": ["こんにちは", "ありがとう", "なに", "なぜ", "どう", "です", "ます"],
    "ko": ["안녕", "감사", "뭐", "왜", "어떻게", "네", "아니요"],
    "ar": ["مرحبا", "شكرا", "كيف", "ماذا", "لماذا", "نعم", "لا"],
    "hi": ["नमस्ते", "धन्यवाद", "क्या", "कैसे", "क्यों", "हां", "नहीं"],
    "tr": ["merhaba", "teşekkür", "nasıl", "ne", "neden", "evet", "hayır"],
}

# ============================================================================
# API MODELS
# ============================================================================
class TranslateRequest(BaseModel):
    text: str
    source: str = "auto"  # auto-detect if not specified
    target: str = "en"

class DetectRequest(BaseModel):
    text: str

class TranslationResponse(BaseModel):
    original: str
    translated: str
    source_lang: str
    target_lang: str
    method: str  # "dictionary" or "api"
    confidence: float
    processing_time_ms: float

# ============================================================================
# TRANSLATION NODE CLASS
# ============================================================================
class TranslationNode:
    """Nanogrid Translation Node - Dictionary-first, API fallback"""
    
    def __init__(self):
        self.languages = SUPPORTED_LANGUAGES
        self.phrases = CORE_PHRASES
        self.patterns = LANGUAGE_PATTERNS
        self.request_count = 0
        self.cache: Dict[str, str] = {}
        logger.info(f"🌍 Translation Node initialized with {len(self.languages)} languages")
    
    def detect_language(self, text: str) -> tuple[str, float]:
        """Detect language from text patterns"""
        text_lower = text.lower()
        scores = {}
        
        for lang, patterns in self.patterns.items():
            score = sum(1 for p in patterns if p in text_lower)
            if score > 0:
                scores[lang] = score
        
        if scores:
            best_lang = max(scores, key=scores.get)
            confidence = min(scores[best_lang] / 3.0, 1.0)
            return best_lang, confidence
        
        # Default to English if no patterns match
        return "en", 0.5
    
    def translate_phrase(self, text: str, source: str, target: str) -> Optional[str]:
        """Try dictionary-based translation first"""
        text_lower = text.lower().strip()
        
        # Check core phrases
        for phrase_key, translations in self.phrases.items():
            if source in translations:
                source_phrase = translations[source].lower()
                if text_lower == source_phrase or text_lower in source_phrase:
                    if target in translations:
                        return translations[target]
        
        return None
    
    async def translate(self, text: str, source: str = "auto", target: str = "en") -> TranslationResponse:
        """Main translation method"""
        import time
        start = time.time()
        self.request_count += 1
        
        # Auto-detect source language
        if source == "auto":
            source, confidence = self.detect_language(text)
        else:
            confidence = 1.0
        
        # Same language - return as is
        if source == target:
            return TranslationResponse(
                original=text,
                translated=text,
                source_lang=source,
                target_lang=target,
                method="passthrough",
                confidence=1.0,
                processing_time_ms=(time.time() - start) * 1000
            )
        
        # Try dictionary first
        dict_result = self.translate_phrase(text, source, target)
        if dict_result:
            return TranslationResponse(
                original=text,
                translated=dict_result,
                source_lang=source,
                target_lang=target,
                method="dictionary",
                confidence=0.95,
                processing_time_ms=(time.time() - start) * 1000
            )
        
        # Check cache
        cache_key = f"{source}:{target}:{text}"
        if cache_key in self.cache:
            return TranslationResponse(
                original=text,
                translated=self.cache[cache_key],
                source_lang=source,
                target_lang=target,
                method="cache",
                confidence=0.9,
                processing_time_ms=(time.time() - start) * 1000
            )
        
        # Fallback to googletrans API
        try:
            from googletrans import Translator
            translator = Translator()
            result = translator.translate(text, src=source, dest=target).text
            
            # Cache result
            self.cache[cache_key] = result
            
            return TranslationResponse(
                original=text,
                translated=result,
                source_lang=source,
                target_lang=target,
                method="api",
                confidence=0.85,
                processing_time_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return TranslationResponse(
                original=text,
                translated=text,
                source_lang=source,
                target_lang=target,
                method="fallback",
                confidence=0.0,
                processing_time_ms=(time.time() - start) * 1000
            )
    
    def get_stats(self) -> Dict:
        """Get node statistics"""
        return {
            "languages_supported": len(self.languages),
            "phrases_cached": sum(len(p) for p in self.phrases.values()),
            "runtime_cache_size": len(self.cache),
            "total_requests": self.request_count,
            "regions": {
                "europe": len([l for l, d in self.languages.items() if d["region"] == "europe"]),
                "asia": len([l for l, d in self.languages.items() if d["region"] == "asia"]),
                "middle_east": len([l for l, d in self.languages.items() if d["region"] == "middle_east"]),
                "africa": len([l for l, d in self.languages.items() if d["region"] == "africa"]),
            }
        }

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================
app = FastAPI(
    title="Clisonix Translation Node",
    description="Nanogrid Pulse Translation Microservice - 60+ Languages",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize translation node
node = TranslationNode()

@app.get("/")
async def root():
    return {
        "service": "Clisonix Translation Node",
        "architecture": "Nanogrid Pulse",
        "languages": len(SUPPORTED_LANGUAGES),
        "status": "operational"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "translation-node",
        "languages": len(SUPPORTED_LANGUAGES),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/languages")
async def list_languages():
    """List all supported languages"""
    return {
        "total": len(SUPPORTED_LANGUAGES),
        "languages": SUPPORTED_LANGUAGES
    }

@app.get("/api/v1/languages/{region}")
async def list_languages_by_region(region: str):
    """List languages by region"""
    filtered = {k: v for k, v in SUPPORTED_LANGUAGES.items() if v["region"] == region}
    return {
        "region": region,
        "total": len(filtered),
        "languages": filtered
    }

@app.post("/api/v1/detect")
async def detect_language(req: DetectRequest):
    """Detect language of text"""
    lang, confidence = node.detect_language(req.text)
    lang_info = SUPPORTED_LANGUAGES.get(lang, {})
    return {
        "text": req.text[:100],
        "detected_language": lang,
        "language_name": lang_info.get("name", "Unknown"),
        "native_name": lang_info.get("native", "Unknown"),
        "flag": lang_info.get("flag", "🌍"),
        "confidence": confidence
    }

@app.post("/api/v1/translate")
async def translate(req: TranslateRequest):
    """Translate text between languages"""
    if req.target not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported target language: {req.target}")
    
    result = await node.translate(req.text, req.source, req.target)
    return result

@app.get("/api/v1/stats")
async def get_stats():
    """Get translation node statistics"""
    return node.get_stats()

@app.get("/api/v1/phrase/{phrase_key}")
async def get_phrase(phrase_key: str, lang: str = "en"):
    """Get a specific phrase in a language"""
    if phrase_key not in CORE_PHRASES:
        raise HTTPException(status_code=404, detail=f"Phrase not found: {phrase_key}")
    
    phrases = CORE_PHRASES[phrase_key]
    if lang in phrases:
        return {"phrase_key": phrase_key, "language": lang, "text": phrases[lang]}
    else:
        return {"phrase_key": phrase_key, "language": "en", "text": phrases.get("en", "Not available")}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🌍 Translation Node starting on port {PORT}")
    logger.info(f"📊 Supporting {len(SUPPORTED_LANGUAGES)} languages")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
