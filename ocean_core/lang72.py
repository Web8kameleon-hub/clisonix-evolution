"""
lang72.py — 72-Language detector for Ocean Nanogrid
======================================================
Detects language from input text using Unicode script ranges
and high-frequency word signatures. No external dependencies.

Returns ISO 639-1 code (e.g. "sq", "en", "ar", "zh", …)
Falls back to "en" when confidence is too low.

Languages covered (72):
  sq, en, de, es, fr, it, pt, nl, sv, no, da, fi,
  pl, cs, sk, sl, hr, sr, bg, ro, hu, ru, uk, be,
  el, tr, he, ar, fa, ur, hi, bn, ta, te, mr, gu,
  pa, ml, kn, or, as, ne, si, th, my, km, lo, vi,
  id, ms, tl, sw, am, ha, yo, ig, zu, xh, af, et,
  lv, lt, mt, ga, cy, is, mk, bs, kk, uz, ky, mn,
  ka, hy, az, ps, so
"""

from __future__ import annotations

import re
import unicodedata

# ---------------------------------------------------------------------------
# Unicode-script fast checks
# ---------------------------------------------------------------------------

def _has(text: str, *ranges: tuple[int, int]) -> bool:
    return any(any(lo <= ord(c) <= hi for lo, hi in ranges) for c in text)


def _detect_by_script(text: str) -> str | None:
    """Return ISO code if a non-Latin script is dominant."""
    if _has(text, (0x4E00, 0x9FFF), (0x3400, 0x4DBF)):
        return "zh"
    if _has(text, (0x3040, 0x309F), (0x30A0, 0x30FF)):
        return "ja"
    if _has(text, (0xAC00, 0xD7AF)):
        return "ko"
    if _has(text, (0x0600, 0x06FF)):
        # Arabic vs Farsi vs Urdu — check common diacritics
        if "ں" in text or "ے" in text or "ک" in text:
            return "ur"
        if "‌" in text or re.search(r"[پچژگ]", text):
            return "fa"
        if re.search(r"[پچ]", text):
            return "ps"
        return "ar"
    if _has(text, (0x0900, 0x097F)):
        return "hi"
    if _has(text, (0x0980, 0x09FF)):
        return "bn"
    if _has(text, (0x0B80, 0x0BFF)):
        return "ta"
    if _has(text, (0x0C00, 0x0C7F)):
        return "te"
    if _has(text, (0x0D00, 0x0D7F)):
        return "ml"
    if _has(text, (0x0A80, 0x0AFF)):
        return "gu"
    if _has(text, (0x0A00, 0x0A7F)):
        return "pa"
    if _has(text, (0x0C80, 0x0CFF)):
        return "kn"
    if _has(text, (0x0B00, 0x0B7F)):
        return "or"
    if _has(text, (0x0D80, 0x0DFF)):
        return "si"
    if _has(text, (0x0900, 0x097F)):
        # Marathi also uses Devanagari — already covered by "hi" heuristic
        # TODO: improve with trigram model if needed
        return "mr"
    if _has(text, (0x0980, 0x09FF)):
        return "as"
    if _has(text, (0x0900, 0x0963)):
        return "ne"
    if _has(text, (0x0E00, 0x0E7F)):
        return "th"
    if _has(text, (0x1000, 0x109F)):
        return "my"
    if _has(text, (0x1780, 0x17FF)):
        return "km"
    if _has(text, (0x0E80, 0x0EFF)):
        return "lo"
    if _has(text, (0x10A0, 0x10FF)):
        return "ka"
    if _has(text, (0x0530, 0x058F)):
        return "hy"
    if _has(text, (0x0400, 0x04FF)):
        # Cyrillic — distinguish Slavic and Turkic
        if re.search(r"[єїіё]", text):
            return "uk"
        if re.search(r"[ёъы]", text) and re.search(r"\b(и|в|не|на|что)\b", text):
            return "ru"
        if "ў" in text or "қ" in text:
            return "uz" if "ў" in text else "kk"
        if "ң" in text or "ү" in text:
            return "ky"
        if "ş" in text:
            return "az"
        if "є" in text:
            return "be"
        if "ъ" in text and re.search(r"\b(на|в|и)\b", text):
            return "bg"
        if re.search(r"[ѓѕ]", text):
            return "mk"
        return "ru"
    if _has(text, (0x0370, 0x03FF)):
        return "el"
    if _has(text, (0x0590, 0x05FF)):
        return "he"
    if _has(text, (0x1200, 0x137F)):
        return "am"
    if _has(text, (0x13A0, 0x13FF)):
        return "so"  # fallback, Cherokee rarely appears alone
    if _has(text, (0x1800, 0x18AF)):
        return "mn"
    return None


# ---------------------------------------------------------------------------
# Latin-script word-signature recognition
# ---------------------------------------------------------------------------

_SIGNATURES: list[tuple[str, list[str]]] = [
    # Albanian
    ("sq", [r"çfarë", r"\bësh[tëë]", r"\bkamë\b", r"\bne\b.*\bkemi\b",
            r"\bpo\b", r"\bçë\b", r"\bsh[qk]ip", r"\bvllai\b", r"\bë\b",
            r"\b(jam|je|është|jemi|jeni|janë)\b",
            r"\b(dhe|ose|por|si|ku|kur|çfarë|kush|pse)\b"]),
    # German
    ("de", [r"\b(ich|du|er|sie|es|wir|ihr)\b",
            r"\b(ist|bin|bist|sind|haben|sein|werden)\b",
            r"\b(und|oder|aber|weil|wenn|dass|als|nicht|von|für|mit)\b"]),
    # French
    ("fr", [r"\b(je|tu|il|elle|nous|vous|ils|elles)\b",
            r"\b(est|sont|avoir|être|faire|aller)\b",
            r"\b(et|ou|mais|si|que|qui|pour|dans|avec|une|des|les)\b"]),
    # Spanish
    ("es", [r"\b(yo|tú|él|ella|nosotros|vosotros|ellos)\b",
            r"\b(es|son|tener|ser|estar|hacer)\b",
            r"\b(y|o|pero|si|que|para|con|de|en|un|una|los|las)\b",
            r"[¿¡]"]),
    # Italian
    ("it", [r"\b(io|tu|lui|lei|noi|voi|loro)\b",
            r"\b(è|sono|avere|essere|fare|andare)\b",
            r"\b(e|o|ma|se|che|per|con|di|in|un|una|gli|le)\b"]),
    # Portuguese
    ("pt", [r"\b(eu|tu|ele|ela|nós|vós|eles|elas)\b",
            r"\b(é|são|ter|ser|estar|fazer)\b",
            r"\b(e|ou|mas|se|que|para|com|de|em|um|uma|os|as)\b"]),
    # Dutch
    ("nl", [r"\b(ik|jij|hij|zij|wij|jullie|zij)\b",
            r"\b(is|zijn|hebben|worden|gaan)\b",
            r"\b(en|of|maar|als|dat|voor|met|van|de|het|een)\b"]),
    # Swedish
    ("sv", [r"\b(jag|du|han|hon|vi|ni|de)\b",
            r"\b(är|var|ha|hur|vad|när)\b",
            r"\b(och|eller|men|om|att|för|med|av|en|ett)\b"]),
    # Norwegian
    ("no", [r"\b(jeg|du|han|hun|vi|dere|de)\b",
            r"\b(er|var|ha|bli)\b",
            r"\b(og|eller|men|om|at|for|med|av|en|et)\b"]),
    # Danish
    ("da", [r"\b(jeg|du|han|hun|vi|i|de)\b",
            r"\b(er|var|have|blive)\b",
            r"\b(og|eller|men|om|at|for|med|af|en|et)\b"]),
    # Finnish
    ("fi", [r"\b(minä|sinä|hän|me|te|he)\b",
            r"\b(olen|olet|on|olemme|olette|ovat)\b",
            r"\b(ja|tai|mutta|jos|niin|myös|ei|kuin)\b",
            r"[äö]"]),
    # Polish
    ("pl", [r"\b(ja|ty|on|ona|my|wy|oni|one)\b",
            r"\b(jest|są|mieć|być|robić)\b",
            r"\b(i|lub|ale|że|dla|z|w|na|do|też)\b",
            r"[ąęśćźżłń]"]),
    # Czech
    ("cs", [r"\b(já|ty|on|ona|my|vy|oni|ony)\b",
            r"\b(je|jsou|mít|být|dělat)\b",
            r"\b(a|nebo|ale|že|pro|s|v|na|do|také)\b",
            r"[áéíóúůýčřšžě]"]),
    # Slovak
    ("sk", [r"\b(ja|ty|on|ona|my|vy|oni|ony)\b",
            r"\b(je|sú|mať|byť|robiť)\b",
            r"\b(a|alebo|ale|že|pre|s|v|na|do|aj)\b"]),
    # Slovenian
    ("sl", [r"\b(jaz|ti|on|ona|mi|vi|oni)\b",
            r"\b(je|so|imeti|biti|delati)\b"]),
    # Croatian
    ("hr", [r"\b(ja|ti|on|ona|mi|vi|oni)\b",
            r"\b(je|su|imati|biti|raditi)\b",
            r"\b(i|ili|ali|da|za|s|u|na|do|još)\b"]),
    # Serbian (Latin)
    ("sr", [r"\b(ja|ti|on|ona|mi|vi|oni)\b",
            r"\b(je|su|imati|biti|raditi)\b",
            r"[čćšžđ]"]),
    # Romanian
    ("ro", [r"\b(eu|tu|el|ea|noi|voi|ei|ele)\b",
            r"\b(este|sunt|a fi|a avea|face)\b",
            r"\b(și|sau|dar|că|pentru|cu|de|în|un|o)\b",
            r"[ăâîșț]"]),
    # Hungarian
    ("hu", [r"\b(én|te|ő|mi|ti|ők)\b",
            r"\b(van|vannak|volt|lesz)\b",
            r"\b(és|vagy|de|hogy|meg|már)\b",
            r"[áéíóöőúüű]"]),
    # Turkish
    ("tr", [r"\b(ben|sen|o|biz|siz|onlar)\b",
            r"\b(ve|veya|ama|için|ile|da|de|mi|mı|mu|mü)\b",
            r"[çğışöü]"]),
    # Afrikaans
    ("af", [r"\b(ek|jy|hy|sy|ons|julle|hulle)\b",
            r"\b(is|was|het|sal|wil|kan)\b",
            r"\b(en|of|maar|dat|vir|met|van|die)\b"]),
    # Estonian
    ("et", [r"[äõöü]",
            r"\b(ma|sa|ta|me|te|nad)\b",
            r"\b(on|oli|olen|oled|oleme|olete|on)\b"]),
    # Latvian
    ("lv", [r"[āēīūčģķļņšž]",
            r"\b(es|tu|viņš|viņa|mēs|jūs|viņi|viņas)\b"]),
    # Lithuanian
    ("lt", [r"[ąčęėįšųūž]",
            r"\b(aš|tu|jis|ji|mes|jūs|jie|jos)\b"]),
    # Maltese
    ("mt", [r"\b(jien|int|huwa|hija|aħna|intom|huma)\b",
            r"\b(u|jew|imma|li|għal|ma|f|ħ)\b",
            r"[ħġċż]"]),
    # Irish
    ("ga", [r"\b(mé|tú|sé|sí|sinn|sibh|siad)\b",
            r"\b(agus|nó|ach|go|le|i|ar|ó)\b"]),
    # Welsh
    ("cy", [r"\b(fi|ti|ef|hi|ni|chi|nhw)\b",
            r"\b(a|neu|ond|y|yr|am|ar|o|yn)\b",
            r"[âêîôûŵŷ]"]),
    # Icelandic
    ("is", [r"[ðþ]",
            r"\b(ég|þú|hann|hún|við|þið|þeir|þær)\b"]),
    # Macedonian (Latin transliteration markers)
    ("mk", [r"\b(јас|ти|тој|таа|ние|вие|тие)\b"]),
    # Bosnian
    ("bs", [r"\b(ja|ti|on|ona|mi|vi|oni|one)\b",
            r"[čćšžđ]"]),
    # Kazakh (Latin)
    ("kk", [r"[әіңғүұқөһ]"]),
    # Indonesian
    ("id", [r"\b(saya|aku|kamu|dia|kami|kita|mereka)\b",
            r"\b(adalah|ada|bisa|akan|sudah|dengan|untuk|dari|ke|di)\b"]),
    # Malay
    ("ms", [r"\b(saya|anda|dia|kami|kita|mereka)\b",
            r"\b(adalah|ada|boleh|akan|sudah|dengan|untuk|dari|ke|di)\b"]),
    # Filipino/Tagalog
    ("tl", [r"\b(ako|ikaw|siya|kami|kayo|sila)\b",
            r"\b(ang|ng|sa|ay|at|para|kay)\b",
            r"\b(po|na|nga|ba|lang)\b"]),
    # Swahili
    ("sw", [r"\b(mimi|wewe|yeye|sisi|ninyi|wao)\b",
            r"\b(na|au|lakini|kwa|ya|wa|za)\b",
            r"\b(ni|si|pia|sana|tu)\b"]),
    # Amharic (Latin transliteration)
    ("am", [r"\b(እኔ|አንተ|እሱ|እሷ|እኛ|እናንተ|እነሱ)\b"]),
    # Hausa
    ("ha", [r"\b(ni|kai|shi|ita|mu|ku|su)\b",
            r"\b(da|ko|amma|don|a|na|ta|ya)\b"]),
    # Yoruba
    ("yo", [r"\b(mi|o|ẹ|a|ẹyin|wọn)\b",
            r"\b(àti|tàbí|àmọ|fún|ní|lọ|wá)\b",
            r"[ẹọṣ]"]),
    # Igbo
    ("ig", [r"\b(m|i|ya|anyị|unu|ha)\b",
            r"\b(na|ma|mana|maka|n'|ya)\b",
            r"[ịọụ]"]),
    # Zulu
    ("zu", [r"\b(mina|wena|yena|thina|nina|bona)\b",
            r"\b(no|noma|kodwa|ukuze|nga|ku|e)\b"]),
    # Xhosa
    ("xh", [r"\b(mna|wena|yena|thina|nina|bona)\b",
            r"\b(no|okanye|kodwa|ngenxa|nga|ku|e)\b"]),
    # English (catch-all Latin)
    ("en", [r"\b(i|you|he|she|we|they|it)\b",
            r"\b(is|are|was|were|have|has|had|will|would|can|could|should|must)\b",
            r"\b(the|a|an|and|or|but|if|to|of|in|on|at|for|with|this|that)\b"]),
]

# Pre-compile all patterns
_COMPILED: list[tuple[str, list[re.Pattern]]] = [
    (lang, [re.compile(p, re.IGNORECASE) for p in patterns])
    for lang, patterns in _SIGNATURES
]

# ---------------------------------------------------------------------------
# Vocabulary map — single-word and common-phrase lookup (handles short inputs)
# Key: lowercase word/phrase  Value: ISO code
# ---------------------------------------------------------------------------
_VOCAB: dict[str, str] = {
    # English
    "hello":"en","hi":"en","thanks":"en","thank":"en","please":"en",
    "what":"en","how":"en","why":"en","where":"en","when":"en","who":"en",
    # German
    "guten":"de","gut":"de","gute":"de","guter":"de","morgen":"de","abend":"de","nacht":"de",
    "hallo":"de","tschüss":"de","danke":"de","bitte":"de","ja":"de","nein":"de",
    "wie":"de","was":"de","wer":"de","wo":"de","wann":"de","warum":"de","sehr":"de",
    "auch":"de","noch":"de","schon":"de","haben":"de","sein":"de","tag":"de",
    "wiedersehen":"de","entschuldigung":"de","sprechen":"de",
    # French
    "bonjour":"fr","bonsoir":"fr","salut":"fr","merci":"fr","oui":"fr","non":"fr",
    "comment":"fr","pourquoi":"fr","quand":"fr","aussi":"fr","très":"fr",
    "au revoir":"fr","s'il":"fr","madame":"fr","monsieur":"fr",
    # Spanish
    "hola":"es","buenos":"es","buenas":"es","gracias":"es","sí":"es",
    "cómo":"es","también":"es","muy":"es","adiós":"es","señor":"es","señora":"es",
    # Italian
    "ciao":"it","buongiorno":"it","buonasera":"it","grazie":"it","prego":"it",
    "sì":"it","come":"it","anche":"it","molto":"it","arrivederci":"it",
    # Albanian
    "mirëdita":"sq","mirëmëngjes":"sq","mirëmbrëma":"sq","faleminderit":"sq",
    "përshëndetje":"sq","mirupafshim":"sq","tungjatjeta":"sq",
    # Portuguese
    "olá":"pt","obrigado":"pt","obrigada":"pt","tchau":"pt",
    # Dutch
    "hoi":"nl","goedendag":"nl","goedemorgen":"nl","goedemiddag":"nl",
    "goedenavond":"nl","dank je":"nl","bedankt":"nl","alsjeblieft":"nl",
    # Swedish
    "hej":"sv","tack":"sv","snälla":"sv","adjö":"sv","varsågod":"sv",
    # Norwegian
    "hei":"no","takk":"no","vær":"no",
    # Danish  (conflicts with no — use context)
    # Finnish
    "kiitos":"fi","hyvää":"fi","päivää":"fi","moi":"fi","heippa":"fi",
    # Polish
    "cześć":"pl","dzień":"pl","dziękuję":"pl","proszę":"pl",
    # Czech
    "ahoj":"cs","děkuji":"cs","prosím":"cs",
    # Romanian
    "bună":"ro","mulțumesc":"ro","salut":"ro",
    # Hungarian
    "szia":"hu","szervusz":"hu","köszönöm":"hu","kérem":"hu",
    # Turkish
    "merhaba":"tr","teşekkür":"tr","evet":"tr","hayır":"tr","günaydın":"tr",
    "iyi":"tr","nasılsın":"tr","teşekkürler":"tr",
    # Indonesian/Malay
    "halo":"id","selamat":"id","terima":"id","kasih":"id",
    # Swahili
    "habari":"sw","asante":"sw","karibu":"sw","ndiyo":"sw","hapana":"sw",
    # Japanese (romaji)
    "konnichiwa":"ja","ohayou":"ja","oyasumi":"ja","arigatou":"ja",
    # Korean (romaji)
    "annyeong":"ko","gamsahamnida":"ko",
    # Chinese (pinyin)
    "nihao":"zh","xièxie":"zh",
    # Russian (transliteration)
    "privet":"ru","spasibo":"ru","pozhaluysta":"ru",
    # Arabic (transliteration)
    "marhaba":"ar","shukran":"ar","ahlan":"ar",
    # Hindi (transliteration)
    "namaste":"hi","dhanyavaad":"hi",
}


def _vocab_score(text: str) -> dict[str, int]:
    """Score a short text by looking up individual words in _VOCAB."""
    words = re.findall(r"[\w'\u00C0-\u024F]+", text.lower())
    scores: dict[str, int] = {}
    for w in words:
        if w in _VOCAB:
            lang = _VOCAB[w]
            scores[lang] = scores.get(lang, 0) + 2  # vocab hits count double
    return scores


def detect_language(text: str, default: str = "en") -> str:
    """
    Detect ISO 639-1 language code from *text*.
    Fast heuristic: script check → vocabulary lookup → word-signature scoring.
    Returns *default* when confidence is too low.
    """
    if not text or len(text.strip()) < 2:
        return default

    # 1. Non-Latin script fast path
    code = _detect_by_script(text)
    if code:
        return code

    # 2. Vocabulary lookup (handles short greetings / single-word messages)
    vocab_scores = _vocab_score(text)

    # 3. Word-signature scoring for Latin-script languages
    t = text.lower()
    sig_scores: dict[str, int] = {}
    for lang, patterns in _COMPILED:
        hit = sum(bool(p.search(t)) for p in patterns)
        if hit > 0:
            sig_scores[lang] = sig_scores.get(lang, 0) + hit

    # Merge both scoring approaches
    merged: dict[str, int] = {}
    for lang, score in vocab_scores.items():
        merged[lang] = merged.get(lang, 0) + score
    for lang, score in sig_scores.items():
        merged[lang] = merged.get(lang, 0) + score

    if merged:
        best = max(merged, key=merged.__getitem__)
        word_count = len(text.split())
        # For short texts (≤3 words), vocab hit alone is enough
        # For longer texts, require at least 2 combined points
        threshold = 1 if word_count <= 3 else 2
        if merged[best] >= threshold:
            return best

    return default


def build_language_instruction(lang_code: str) -> str:
    """Return a system-prompt snippet that tells the LLM which language to use."""
    _names: dict[str, str] = {
        "sq": "Albanian (Shqip)", "en": "English", "de": "German (Deutsch)",
        "es": "Spanish (Español)", "fr": "French (Français)", "it": "Italian (Italiano)",
        "pt": "Portuguese", "nl": "Dutch", "sv": "Swedish", "no": "Norwegian",
        "da": "Danish", "fi": "Finnish", "pl": "Polish", "cs": "Czech",
        "sk": "Slovak", "sl": "Slovenian", "hr": "Croatian", "sr": "Serbian",
        "bg": "Bulgarian", "ro": "Romanian", "hu": "Hungarian", "ru": "Russian",
        "uk": "Ukrainian", "be": "Belarusian", "el": "Greek", "tr": "Turkish",
        "he": "Hebrew", "ar": "Arabic", "fa": "Persian (Farsi)", "ur": "Urdu",
        "hi": "Hindi", "bn": "Bengali", "ta": "Tamil", "te": "Telugu",
        "mr": "Marathi", "gu": "Gujarati", "pa": "Punjabi", "ml": "Malayalam",
        "kn": "Kannada", "or": "Odia", "as": "Assamese", "ne": "Nepali",
        "si": "Sinhala", "th": "Thai", "my": "Burmese", "km": "Khmer",
        "lo": "Lao", "vi": "Vietnamese", "id": "Indonesian", "ms": "Malay",
        "tl": "Filipino", "sw": "Swahili", "am": "Amharic", "ha": "Hausa",
        "yo": "Yoruba", "ig": "Igbo", "zu": "Zulu", "xh": "Xhosa",
        "af": "Afrikaans", "et": "Estonian", "lv": "Latvian", "lt": "Lithuanian",
        "mt": "Maltese", "ga": "Irish", "cy": "Welsh", "is": "Icelandic",
        "mk": "Macedonian", "bs": "Bosnian", "kk": "Kazakh", "uz": "Uzbek",
        "ky": "Kyrgyz", "mn": "Mongolian", "ka": "Georgian", "hy": "Armenian",
        "az": "Azerbaijani", "ps": "Pashto", "so": "Somali",
    }
    name = _names.get(lang_code, lang_code.upper())
    return (
        f"IMPORTANT: The user wrote in {name} (code: {lang_code}). "
        f"You MUST respond entirely in {name}. "
        f"Do not switch to English or any other language."
    )
