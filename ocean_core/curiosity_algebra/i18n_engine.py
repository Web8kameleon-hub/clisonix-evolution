# -*- coding: utf-8 -*-
"""
🌍 I18N ENGINE - Internationalization System
============================================
Sistem i vërtetë për shumë gjuhë - jo fake, vetëm funksione reale!

Gjuhët e mbështetura:
- sq (Shqip)
- en (English)
- de (Deutsch)
- fr (Français)
- it (Italiano)
- es (Español)
- pt (Português)
- tr (Türkçe)
- sr (Srpski)
- mk (Македонски)
- el (Ελληνικά)

Author: Clisonix Team
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class Language(Enum):
    """Gjuhët e mbështetura"""
    SQ = "sq"  # Shqip
    EN = "en"  # English
    DE = "de"  # Deutsch
    FR = "fr"  # Français
    IT = "it"  # Italiano
    ES = "es"  # Español
    PT = "pt"  # Português
    TR = "tr"  # Türkçe
    SR = "sr"  # Srpski
    MK = "mk"  # Македонски
    EL = "el"  # Ελληνικά
    

@dataclass
class TranslationEntry:
    """Një hyrje përkthimi"""
    key: str
    translations: Dict[str, str]
    context: str = ""
    
    def get(self, lang: str, fallback: str = "en") -> str:
        """Merr përkthimin për gjuhën"""
        return self.translations.get(lang, self.translations.get(fallback, self.key))


# Fjalori kryesor i përkthimeve
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Përshëndetje
    "hello": {
        "sq": "Përshëndetje",
        "en": "Hello",
        "de": "Hallo",
        "fr": "Bonjour",
        "it": "Ciao",
        "es": "Hola",
        "pt": "Olá",
        "tr": "Merhaba",
        "sr": "Zdravo",
        "mk": "Здраво",
        "el": "Γεια σου"
    },
    "goodbye": {
        "sq": "Mirupafshim",
        "en": "Goodbye",
        "de": "Auf Wiedersehen",
        "fr": "Au revoir",
        "it": "Arrivederci",
        "es": "Adiós",
        "pt": "Adeus",
        "tr": "Hoşça kal",
        "sr": "Doviđenja",
        "mk": "Довидување",
        "el": "Αντίο"
    },
    "thank_you": {
        "sq": "Faleminderit",
        "en": "Thank you",
        "de": "Danke",
        "fr": "Merci",
        "it": "Grazie",
        "es": "Gracias",
        "pt": "Obrigado",
        "tr": "Teşekkürler",
        "sr": "Hvala",
        "mk": "Благодарам",
        "el": "Ευχαριστώ"
    },
    "yes": {
        "sq": "Po",
        "en": "Yes",
        "de": "Ja",
        "fr": "Oui",
        "it": "Sì",
        "es": "Sí",
        "pt": "Sim",
        "tr": "Evet",
        "sr": "Da",
        "mk": "Да",
        "el": "Ναι"
    },
    "no": {
        "sq": "Jo",
        "en": "No",
        "de": "Nein",
        "fr": "Non",
        "it": "No",
        "es": "No",
        "pt": "Não",
        "tr": "Hayır",
        "sr": "Ne",
        "mk": "Не",
        "el": "Όχι"
    },
    
    # Matematikë
    "result_is": {
        "sq": "Rezultati është",
        "en": "The result is",
        "de": "Das Ergebnis ist",
        "fr": "Le résultat est",
        "it": "Il risultato è",
        "es": "El resultado es",
        "pt": "O resultado é",
        "tr": "Sonuç",
        "sr": "Rezultat je",
        "mk": "Резултатот е",
        "el": "Το αποτέλεσμα είναι"
    },
    "calculation": {
        "sq": "Llogaritje",
        "en": "Calculation",
        "de": "Berechnung",
        "fr": "Calcul",
        "it": "Calcolo",
        "es": "Cálculo",
        "pt": "Cálculo",
        "tr": "Hesaplama",
        "sr": "Proračun",
        "mk": "Пресметка",
        "el": "Υπολογισμός"
    },
    "equals": {
        "sq": "baraz",
        "en": "equals",
        "de": "gleich",
        "fr": "égale",
        "it": "uguale",
        "es": "igual",
        "pt": "igual",
        "tr": "eşittir",
        "sr": "jednako",
        "mk": "еднакво",
        "el": "ίσον"
    },
    "plus": {
        "sq": "plus",
        "en": "plus",
        "de": "plus",
        "fr": "plus",
        "it": "più",
        "es": "más",
        "pt": "mais",
        "tr": "artı",
        "sr": "plus",
        "mk": "плус",
        "el": "συν"
    },
    "minus": {
        "sq": "minus",
        "en": "minus",
        "de": "minus",
        "fr": "moins",
        "it": "meno",
        "es": "menos",
        "pt": "menos",
        "tr": "eksi",
        "sr": "minus",
        "mk": "минус",
        "el": "μείον"
    },
    "times": {
        "sq": "herë",
        "en": "times",
        "de": "mal",
        "fr": "fois",
        "it": "per",
        "es": "por",
        "pt": "vezes",
        "tr": "kere",
        "sr": "puta",
        "mk": "пати",
        "el": "επί"
    },
    "divided_by": {
        "sq": "pjesëtuar me",
        "en": "divided by",
        "de": "geteilt durch",
        "fr": "divisé par",
        "it": "diviso per",
        "es": "dividido por",
        "pt": "dividido por",
        "tr": "bölü",
        "sr": "podeljeno sa",
        "mk": "поделено со",
        "el": "διά"
    },
    
    # Sistem
    "status": {
        "sq": "Gjendja",
        "en": "Status",
        "de": "Status",
        "fr": "Statut",
        "it": "Stato",
        "es": "Estado",
        "pt": "Estado",
        "tr": "Durum",
        "sr": "Status",
        "mk": "Статус",
        "el": "Κατάσταση"
    },
    "operational": {
        "sq": "Operacional",
        "en": "Operational",
        "de": "Betriebsbereit",
        "fr": "Opérationnel",
        "it": "Operativo",
        "es": "Operativo",
        "pt": "Operacional",
        "tr": "Çalışıyor",
        "sr": "Operativan",
        "mk": "Оперативен",
        "el": "Λειτουργικό"
    },
    "error": {
        "sq": "Gabim",
        "en": "Error",
        "de": "Fehler",
        "fr": "Erreur",
        "it": "Errore",
        "es": "Error",
        "pt": "Erro",
        "tr": "Hata",
        "sr": "Greška",
        "mk": "Грешка",
        "el": "Σφάλμα"
    },
    "success": {
        "sq": "Sukses",
        "en": "Success",
        "de": "Erfolg",
        "fr": "Succès",
        "it": "Successo",
        "es": "Éxito",
        "pt": "Sucesso",
        "tr": "Başarı",
        "sr": "Uspeh",
        "mk": "Успех",
        "el": "Επιτυχία"
    },
    
    # Pyetje dhe përgjigje
    "how_can_i_help": {
        "sq": "Si mund t'ju ndihmoj?",
        "en": "How can I help you?",
        "de": "Wie kann ich Ihnen helfen?",
        "fr": "Comment puis-je vous aider?",
        "it": "Come posso aiutarti?",
        "es": "¿Cómo puedo ayudarte?",
        "pt": "Como posso ajudá-lo?",
        "tr": "Size nasıl yardımcı olabilirim?",
        "sr": "Kako mogu da vam pomognem?",
        "mk": "Како можам да ви помогнам?",
        "el": "Πώς μπορώ να σας βοηθήσω;"
    },
    "i_understand": {
        "sq": "Kuptoj",
        "en": "I understand",
        "de": "Ich verstehe",
        "fr": "Je comprends",
        "it": "Capisco",
        "es": "Entiendo",
        "pt": "Eu entendo",
        "tr": "Anlıyorum",
        "sr": "Razumem",
        "mk": "Разбирам",
        "el": "Καταλαβαίνω"
    },
    "please_specify": {
        "sq": "Ju lutem specifikoni",
        "en": "Please specify",
        "de": "Bitte spezifizieren Sie",
        "fr": "Veuillez préciser",
        "it": "Per favore specifica",
        "es": "Por favor especifique",
        "pt": "Por favor especifique",
        "tr": "Lütfen belirtin",
        "sr": "Molimo vas da navedete",
        "mk": "Ве молиме наведете",
        "el": "Παρακαλώ διευκρινίστε"
    },
    
    # Kohë
    "today": {
        "sq": "Sot",
        "en": "Today",
        "de": "Heute",
        "fr": "Aujourd'hui",
        "it": "Oggi",
        "es": "Hoy",
        "pt": "Hoje",
        "tr": "Bugün",
        "sr": "Danas",
        "mk": "Денес",
        "el": "Σήμερα"
    },
    "now": {
        "sq": "Tani",
        "en": "Now",
        "de": "Jetzt",
        "fr": "Maintenant",
        "it": "Adesso",
        "es": "Ahora",
        "pt": "Agora",
        "tr": "Şimdi",
        "sr": "Sada",
        "mk": "Сега",
        "el": "Τώρα"
    },
    
    # Ditët e javës
    "monday": {"sq": "E hënë", "en": "Monday", "de": "Montag", "fr": "Lundi", "it": "Lunedì", "es": "Lunes", "pt": "Segunda-feira", "tr": "Pazartesi", "sr": "Ponedeljak", "mk": "Понеделник", "el": "Δευτέρα"},
    "tuesday": {"sq": "E martë", "en": "Tuesday", "de": "Dienstag", "fr": "Mardi", "it": "Martedì", "es": "Martes", "pt": "Terça-feira", "tr": "Salı", "sr": "Utorak", "mk": "Вторник", "el": "Τρίτη"},
    "wednesday": {"sq": "E mërkurë", "en": "Wednesday", "de": "Mittwoch", "fr": "Mercredi", "it": "Mercoledì", "es": "Miércoles", "pt": "Quarta-feira", "tr": "Çarşamba", "sr": "Sreda", "mk": "Среда", "el": "Τετάρτη"},
    "thursday": {"sq": "E enjte", "en": "Thursday", "de": "Donnerstag", "fr": "Jeudi", "it": "Giovedì", "es": "Jueves", "pt": "Quinta-feira", "tr": "Perşembe", "sr": "Četvrtak", "mk": "Четврток", "el": "Πέμπτη"},
    "friday": {"sq": "E premte", "en": "Friday", "de": "Freitag", "fr": "Vendredi", "it": "Venerdì", "es": "Viernes", "pt": "Sexta-feira", "tr": "Cuma", "sr": "Petak", "mk": "Петок", "el": "Παρασκευή"},
    "saturday": {"sq": "E shtunë", "en": "Saturday", "de": "Samstag", "fr": "Samedi", "it": "Sabato", "es": "Sábado", "pt": "Sábado", "tr": "Cumartesi", "sr": "Subota", "mk": "Сабота", "el": "Σάββατο"},
    "sunday": {"sq": "E diel", "en": "Sunday", "de": "Sonntag", "fr": "Dimanche", "it": "Domenica", "es": "Domingo", "pt": "Domingo", "tr": "Pazar", "sr": "Nedelja", "mk": "Недела", "el": "Κυριακή"},
    
    # Muajt
    "january": {"sq": "Janar", "en": "January", "de": "Januar", "fr": "Janvier", "it": "Gennaio", "es": "Enero", "pt": "Janeiro", "tr": "Ocak", "sr": "Januar", "mk": "Јануари", "el": "Ιανουάριος"},
    "february": {"sq": "Shkurt", "en": "February", "de": "Februar", "fr": "Février", "it": "Febbraio", "es": "Febrero", "pt": "Fevereiro", "tr": "Şubat", "sr": "Februar", "mk": "Февруари", "el": "Φεβρουάριος"},
    "march": {"sq": "Mars", "en": "March", "de": "März", "fr": "Mars", "it": "Marzo", "es": "Marzo", "pt": "Março", "tr": "Mart", "sr": "Mart", "mk": "Март", "el": "Μάρτιος"},
    "april": {"sq": "Prill", "en": "April", "de": "April", "fr": "Avril", "it": "Aprile", "es": "Abril", "pt": "Abril", "tr": "Nisan", "sr": "April", "mk": "Април", "el": "Απρίλιος"},
    "may": {"sq": "Maj", "en": "May", "de": "Mai", "fr": "Mai", "it": "Maggio", "es": "Mayo", "pt": "Maio", "tr": "Mayıs", "sr": "Maj", "mk": "Мај", "el": "Μάιος"},
    "june": {"sq": "Qershor", "en": "June", "de": "Juni", "fr": "Juin", "it": "Giugno", "es": "Junio", "pt": "Junho", "tr": "Haziran", "sr": "Jun", "mk": "Јуни", "el": "Ιούνιος"},
    "july": {"sq": "Korrik", "en": "July", "de": "Juli", "fr": "Juillet", "it": "Luglio", "es": "Julio", "pt": "Julho", "tr": "Temmuz", "sr": "Jul", "mk": "Јули", "el": "Ιούλιος"},
    "august": {"sq": "Gusht", "en": "August", "de": "August", "fr": "Août", "it": "Agosto", "es": "Agosto", "pt": "Agosto", "tr": "Ağustos", "sr": "Avgust", "mk": "Август", "el": "Αύγουστος"},
    "september": {"sq": "Shtator", "en": "September", "de": "September", "fr": "Septembre", "it": "Settembre", "es": "Septiembre", "pt": "Setembro", "tr": "Eylül", "sr": "Septembar", "mk": "Септември", "el": "Σεπτέμβριος"},
    "october": {"sq": "Tetor", "en": "October", "de": "Oktober", "fr": "Octobre", "it": "Ottobre", "es": "Octubre", "pt": "Outubro", "tr": "Ekim", "sr": "Oktobar", "mk": "Октомври", "el": "Οκτώβριος"},
    "november": {"sq": "Nëntor", "en": "November", "de": "November", "fr": "Novembre", "it": "Novembre", "es": "Noviembre", "pt": "Novembro", "tr": "Kasım", "sr": "Novembar", "mk": "Ноември", "el": "Νοέμβριος"},
    "december": {"sq": "Dhjetor", "en": "December", "de": "Dezember", "fr": "Décembre", "it": "Dicembre", "es": "Diciembre", "pt": "Dezembro", "tr": "Aralık", "sr": "Decembar", "mk": "Декември", "el": "Δεκέμβριος"},
}


# Patterns për detektim gjuhe
LANGUAGE_PATTERNS = {
    "sq": [
        r'\b(sa|çfarë|si|ku|kur|pse|mund|duhet|kam|je|është|janë|bëjnë|llogarit|faleminderit|mirëdita|përshëndetje)\b',
        r'[ëç]',  # Shqip karaktere speciale
    ],
    "en": [
        r'\b(what|how|where|when|why|can|could|would|should|the|is|are|was|were|hello|hi|thanks|please)\b',
    ],
    "de": [
        r'\b(was|wie|wo|wann|warum|kann|könnte|würde|sollte|der|die|das|ist|sind|war|waren|hallo|danke|bitte)\b',
        r'[äöüß]',
    ],
    "fr": [
        r'\b(que|quoi|comment|où|quand|pourquoi|peut|pourrait|devrait|le|la|les|est|sont|était|bonjour|merci|sil vous plaît)\b',
        r'[àâçéèêëîïôûùüÿœæ]',
    ],
    "it": [
        r'\b(che|cosa|come|dove|quando|perché|può|potrebbe|dovrebbe|il|la|lo|gli|le|è|sono|era|ciao|grazie|prego)\b',
        r'[àèéìòù]',
    ],
    "es": [
        r'\b(qué|cómo|dónde|cuándo|por qué|puede|podría|debería|el|la|los|las|es|son|era|hola|gracias|por favor)\b',
        r'[áéíóúüñ¿¡]',
    ],
    "pt": [
        r'\b(que|como|onde|quando|por que|pode|poderia|deveria|o|a|os|as|é|são|era|olá|obrigado|por favor)\b',
        r'[àáâãçéêíóôõú]',
    ],
    "tr": [
        r'\b(ne|nasıl|nerede|ne zaman|neden|olabilir|merhaba|teşekkürler|lütfen)\b',
        r'[çğıöşü]',
    ],
    "sr": [
        r'\b(šta|kako|gde|kada|zašto|može|zdravo|hvala|molim)\b',
        r'[čćžšđ]',
    ],
    "mk": [
        r'[абвгдѓежзѕијклљмнњопрстќуфхцчџш]',
    ],
    "el": [
        r'[αβγδεζηθικλμνξοπρστυφχψω]',
    ],
}


class LanguageDetector:
    """Detektor gjuhe"""
    
    def __init__(self):
        self.patterns = LANGUAGE_PATTERNS
        self.cache: Dict[str, str] = {}
    
    def detect(self, text: str) -> str:
        """Detekto gjuhën e tekstit"""
        if not text:
            return "en"
        
        # Check cache
        cache_key = text[:100]
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        text_lower = text.lower()
        scores: Dict[str, int] = {}
        
        for lang, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE | re.UNICODE)
                score += len(matches) * 2
            scores[lang] = score
        
        # Merr gjuhën me pikë më të lartë
        if scores:
            best_lang = max(scores, key=scores.get)
            if scores[best_lang] > 0:
                self.cache[cache_key] = best_lang
                return best_lang
        
        # Default: English
        return "en"
    
    def detect_with_confidence(self, text: str) -> Tuple[str, float]:
        """Detekto gjuhën me besueshmëri"""
        if not text:
            return "en", 0.0
        
        text_lower = text.lower()
        scores: Dict[str, int] = {}
        
        for lang, patterns in self.patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE | re.UNICODE)
                score += len(matches)
            scores[lang] = score
        
        total = sum(scores.values())
        if total == 0:
            return "en", 0.5
        
        best_lang = max(scores, key=scores.get)
        confidence = scores[best_lang] / total if total > 0 else 0.5
        
        return best_lang, confidence


class I18nEngine:
    """Motori kryesor i18n"""
    
    def __init__(self, default_lang: str = "en"):
        self.default_lang = default_lang
        self.translations = TRANSLATIONS
        self.detector = LanguageDetector()
        self.custom_translations: Dict[str, Dict[str, str]] = {}
        self.stats = {
            "translations_served": 0,
            "detections_made": 0,
            "languages_used": {}
        }
    
    def t(self, key: str, lang: Optional[str] = None) -> str:
        """Përkthe çelësin në gjuhën e dhënë"""
        target_lang = lang or self.default_lang
        
        # Check custom first
        if key in self.custom_translations:
            trans = self.custom_translations[key].get(target_lang)
            if trans:
                self._update_stats(target_lang)
                return trans
        
        # Then standard
        if key in self.translations:
            trans = self.translations[key].get(target_lang)
            if trans:
                self._update_stats(target_lang)
                return trans
            # Fallback to English
            return self.translations[key].get("en", key)
        
        return key
    
    def translate(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """Përkthe me mbështetje për variabla"""
        text = self.t(key, lang)
        
        # Replace variables like {name}
        for var_key, var_value in kwargs.items():
            text = text.replace(f"{{{var_key}}}", str(var_value))
        
        return text
    
    def detect_language(self, text: str) -> str:
        """Detekto gjuhën"""
        self.stats["detections_made"] += 1
        return self.detector.detect(text)
    
    def detect_and_translate(self, key: str, context_text: str) -> str:
        """Detekto gjuhën nga konteksti dhe përkthe"""
        lang = self.detect_language(context_text)
        return self.t(key, lang)
    
    def add_translation(self, key: str, lang: str, value: str):
        """Shto përkthim të ri"""
        if key not in self.custom_translations:
            self.custom_translations[key] = {}
        self.custom_translations[key][lang] = value
    
    def get_all_keys(self) -> List[str]:
        """Merr të gjithë çelësat"""
        keys = set(self.translations.keys())
        keys.update(self.custom_translations.keys())
        return sorted(keys)
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Merr gjuhët e mbështetura"""
        return [
            {"code": "sq", "name": "Shqip", "native": "Shqip"},
            {"code": "en", "name": "English", "native": "English"},
            {"code": "de", "name": "German", "native": "Deutsch"},
            {"code": "fr", "name": "French", "native": "Français"},
            {"code": "it", "name": "Italian", "native": "Italiano"},
            {"code": "es", "name": "Spanish", "native": "Español"},
            {"code": "pt", "name": "Portuguese", "native": "Português"},
            {"code": "tr", "name": "Turkish", "native": "Türkçe"},
            {"code": "sr", "name": "Serbian", "native": "Srpski"},
            {"code": "mk", "name": "Macedonian", "native": "Македонски"},
            {"code": "el", "name": "Greek", "native": "Ελληνικά"},
        ]
    
    def format_number(self, number: float, lang: str = "en") -> str:
        """Formato numrin sipas gjuhës"""
        # Gjuhët që përdorin presje për decimal
        comma_decimal = ["de", "fr", "it", "es", "pt", "tr", "sr", "mk", "el", "sq"]
        
        if lang in comma_decimal:
            # 1.234,56 format
            if isinstance(number, float):
                int_part = int(number)
                dec_part = abs(number - int_part)
                int_str = f"{int_part:,}".replace(",", ".")
                dec_str = f"{dec_part:.2f}"[2:]
                return f"{int_str},{dec_str}"
            else:
                return f"{number:,}".replace(",", ".")
        else:
            # 1,234.56 format
            if isinstance(number, float):
                return f"{number:,.2f}"
            else:
                return f"{number:,}"
    
    def format_date(self, dt: datetime, lang: str = "en", format_type: str = "short") -> str:
        """Formato datën sipas gjuhës"""
        day_names = {
            0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday",
            4: "friday", 5: "saturday", 6: "sunday"
        }
        month_names = {
            1: "january", 2: "february", 3: "march", 4: "april",
            5: "may", 6: "june", 7: "july", 8: "august",
            9: "september", 10: "october", 11: "november", 12: "december"
        }
        
        day_name = self.t(day_names[dt.weekday()], lang)
        month_name = self.t(month_names[dt.month], lang)
        
        if format_type == "long":
            return f"{day_name}, {dt.day} {month_name} {dt.year}"
        elif format_type == "medium":
            return f"{dt.day} {month_name} {dt.year}"
        else:  # short
            return f"{dt.day}/{dt.month}/{dt.year}"
    
    def _update_stats(self, lang: str):
        """Përditëso statistikat"""
        self.stats["translations_served"] += 1
        if lang not in self.stats["languages_used"]:
            self.stats["languages_used"][lang] = 0
        self.stats["languages_used"][lang] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Merr statistikat"""
        return {
            **self.stats,
            "total_keys": len(self.get_all_keys()),
            "custom_keys": len(self.custom_translations),
            "supported_languages": len(self.get_supported_languages())
        }


# Global instance
_i18n_engine: Optional[I18nEngine] = None


def get_i18n_engine() -> I18nEngine:
    """Merr instancën globale të i18n"""
    global _i18n_engine
    if _i18n_engine is None:
        _i18n_engine = I18nEngine()
    return _i18n_engine


def t(key: str, lang: Optional[str] = None) -> str:
    """Shortcut për përkthim"""
    return get_i18n_engine().t(key, lang)


def detect_lang(text: str) -> str:
    """Shortcut për detektim gjuhe"""
    return get_i18n_engine().detect_language(text)
