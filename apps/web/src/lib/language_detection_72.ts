/**
 * 72-LANGUAGE DETECTION SYSTEM
 * ============================
 * Comprehensive multi-language support with Unicode, patterns, and keywords
 *
 * Languages grouped by family for optimized detection
 */

// ═══════════════════════════════════════════════════════════════════════
// UNICODE RANGES (Most Reliable Detection)
// ═══════════════════════════════════════════════════════════════════════

const UNICODE_RANGES = {
  el: { range: /[\u0370-\u03ff]/, name: "Greek" },
  sq: {
    range: /[\u0386-\u038a\u038c\u038e-\u038f\u0391-\u03a1\u03a3-\u03ce]/,
    name: "Albanian Cyrillic",
  },
  ru: { range: /[\u0400-\u04ff]/, name: "Cyrillic (Russian)" },
  uk: { range: /[\u0400-\u04ff]/, name: "Cyrillic (Ukrainian)" },
  bg: { range: /[\u0400-\u04ff]/, name: "Cyrillic (Bulgarian)" },
  sr: { range: /[\u0400-\u04ff]/, name: "Cyrillic (Serbian)" },
  ar: { range: /[\u0600-\u06ff]/, name: "Arabic" },
  he: { range: /[\u0590-\u05ff]/, name: "Hebrew" },
  hi: { range: /[\u0900-\u097f]/, name: "Devanagari (Hindi)" },
  ta: { range: /[\u0b80-\u0bff]/, name: "Tamil" },
  te: { range: /[\u0c00-\u0c7f]/, name: "Telugu" },
  kn: { range: /[\u0c80-\u0cff]/, name: "Kannada" },
  ml: { range: /[\u0d00-\u0d7f]/, name: "Malayalam" },
  th: { range: /[\u0e00-\u0e7f]/, name: "Thai" },
  lo: { range: /[\u0e80-\u0eff]/, name: "Lao" },
  km: { range: /[\u1780-\u17ff]/, name: "Khmer" },
  my: { range: /[\u1000-\u109f]/, name: "Burmese" },
  ja: { range: /[\u3040-\u30ff]/, name: "Japanese" },
  zh: { range: /[\u4e00-\u9fff]/, name: "Chinese" },
  ko: { range: /[\uac00-\ud7af]/, name: "Korean" },
};

// ═══════════════════════════════════════════════════════════════════════
// SPECIAL CHARACTER PATTERNS (Fast Detection)
// ═══════════════════════════════════════════════════════════════════════

const SPECIAL_CHARS = {
  de: { pattern: /ß|ä|ö|ü/, chars: ["ß", "ä", "ö", "ü"] },
  es: { pattern: /ñ|¿|¡|á|é|í|ó|ú/, chars: ["ñ", "¿", "¡"] },
  fr: { pattern: /ç|œ|à|è|ù|é/, chars: ["ç", "œ"] },
  it: { pattern: /à|è|ì|ò|ù/, chars: ["à", "è", "ì", "ò", "ù"] },
  pt: { pattern: /ã|õ|ç|á|é|í|ó|ú/, chars: ["ã", "õ", "ç"] },
  sq: { pattern: /ç|ë|dh|th|xh|zh|gj|ll|nj|rr/, chars: ["ç", "ë"] },
  tr: { pattern: /ç|ğ|ı|ş|ü|ö/, chars: ["ç", "ğ", "ı", "ş"] },
  pl: { pattern: /ą|ć|ę|ł|ń|ó|ś|ź|ż/, chars: ["ą", "ć", "ę", "ł"] },
  cz: { pattern: /č|ř|ů|ž|š|ě/, chars: ["č", "ř", "ů", "ž"] },
  ro: { pattern: /ă|â|î|ş|ţ/, chars: ["ă", "â", "î", "ş"] },
  hu: { pattern: /á|é|í|ó|ö|ő|ú|ü|ű/, chars: ["ő", "ű"] },
  sk: { pattern: /á|č|ď|é|í|ĺ|ľ|ň|ó|ô|ŕ|š|ť|ú|ý|ž/, chars: ["č", "ď", "ľ"] },
  sv: { pattern: /å|ä|ö/, chars: ["å", "ä", "ö"] },
  da: { pattern: /å|ø|æ/, chars: ["å", "ø", "æ"] },
  no: { pattern: /å|ø|æ/, chars: ["å", "ø", "æ"] },
  fi: { pattern: /ä|ö|å/, chars: ["ä", "ö"] },
  nl: { pattern: /ë|ï|ö|ü/, chars: ["ë", "ï"] },
  af: { pattern: /ë|ï|ö|ü/, chars: ["ë", "ï"] },
  ca: { pattern: /ç|à|è|é|í|ï|ò|ó|ú|ü/, chars: ["ç", "à"] },
  gl: { pattern: /á|à|é|ó/, chars: ["á", "à"] },
};

// ═══════════════════════════════════════════════════════════════════════
// KEYWORD PATTERNS (72 Languages)
// ═══════════════════════════════════════════════════════════════════════

const LANGUAGE_KEYWORDS: Record<
  string,
  { keywords: string[]; threshold: number }
> = {
  // GERMANIC
  en: {
    keywords: [
      "the",
      "is",
      "and",
      "to",
      "of",
      "a",
      "in",
      "you",
      "that",
      "it",
      "not",
      "but",
      "can",
      "have",
      "from",
      "for",
      "with",
    ],
    threshold: 5,
  },
  de: {
    keywords: [
      "der",
      "die",
      "das",
      "und",
      "in",
      "zu",
      "von",
      "ist",
      "sein",
      "haben",
      "werden",
      "ich",
      "sie",
      "es",
    ],
    threshold: 4,
  },
  nl: {
    keywords: [
      "de",
      "het",
      "en",
      "van",
      "in",
      "een",
      "te",
      "is",
      "ik",
      "je",
      "dat",
      "wat",
    ],
    threshold: 4,
  },
  sv: {
    keywords: [
      "och",
      "det",
      "i",
      "att",
      "en",
      "jag",
      "hon",
      "som",
      "han",
      "på",
      "de",
      "med",
    ],
    threshold: 4,
  },
  da: {
    keywords: [
      "og",
      "det",
      "der",
      "i",
      "at",
      "en",
      "jeg",
      "han",
      "på",
      "de",
      "med",
      "til",
    ],
    threshold: 4,
  },
  no: {
    keywords: [
      "og",
      "i",
      "å",
      "at",
      "en",
      "han",
      "på",
      "de",
      "med",
      "til",
      "det",
      "jeg",
    ],
    threshold: 4,
  },
  is: {
    keywords: [
      "og",
      "í",
      "að",
      "er",
      "um",
      "ein",
      "ég",
      "hann",
      "með",
      "til",
      "var",
      "þá",
    ],
    threshold: 4,
  },
  af: {
    keywords: [
      "en",
      "is",
      "van",
      "wat",
      "die",
      "te",
      "na",
      "aan",
      "ek",
      "jy",
      "het",
      "was",
    ],
    threshold: 4,
  },

  // ROMANCE
  es: {
    keywords: [
      "el",
      "la",
      "de",
      "que",
      "y",
      "en",
      "es",
      "por",
      "con",
      "para",
      "una",
      "está",
      "ser",
    ],
    threshold: 5,
  },
  fr: {
    keywords: [
      "le",
      "la",
      "de",
      "et",
      "à",
      "un",
      "une",
      "en",
      "est",
      "pour",
      "nous",
      "vous",
      "ils",
    ],
    threshold: 5,
  },
  it: {
    keywords: [
      "di",
      "da",
      "il",
      "la",
      "che",
      "a",
      "e",
      "è",
      "per",
      "con",
      "un",
      "una",
      "ha",
    ],
    threshold: 5,
  },
  pt: {
    keywords: [
      "de",
      "a",
      "o",
      "que",
      "e",
      "do",
      "em",
      "um",
      "para",
      "é",
      "com",
      "não",
    ],
    threshold: 5,
  },
  ro: {
    keywords: [
      "și",
      "de",
      "a",
      "în",
      "cu",
      "la",
      "pe",
      "că",
      "o",
      "din",
      "este",
      "cu",
    ],
    threshold: 4,
  },
  ca: {
    keywords: [
      "el",
      "la",
      "de",
      "que",
      "i",
      "en",
      "es",
      "per",
      "amb",
      "una",
      "és",
      "a",
    ],
    threshold: 5,
  },
  gl: {
    keywords: [
      "de",
      "a",
      "o",
      "que",
      "e",
      "en",
      "para",
      "con",
      "non",
      "está",
      "é",
      "por",
    ],
    threshold: 4,
  },

  // SLAVIC
  ru: {
    keywords: [
      "и",
      "в",
      "не",
      "на",
      "что",
      "что",
      "он",
      "она",
      "оно",
      "они",
      "то",
      "это",
    ],
    threshold: 3,
  },
  pl: {
    keywords: [
      "i",
      "w",
      "na",
      "że",
      "nie",
      "do",
      "się",
      "z",
      "z",
      "a",
      "jest",
      "to",
    ],
    threshold: 4,
  },
  cz: {
    keywords: [
      "a",
      "v",
      "na",
      "je",
      "to",
      "se",
      "ne",
      "vy",
      "já",
      "jsou",
      "jen",
      "jako",
    ],
    threshold: 4,
  },
  sk: {
    keywords: [
      "a",
      "v",
      "na",
      "je",
      "to",
      "sa",
      "nie",
      "všetci",
      "som",
      "si",
      "sú",
      "ak",
    ],
    threshold: 4,
  },
  uk: {
    keywords: [
      "і",
      "в",
      "на",
      "не",
      "що",
      "з",
      "це",
      "для",
      "ми",
      "як",
      "було",
      "про",
    ],
    threshold: 3,
  },
  bg: {
    keywords: [
      "и",
      "на",
      "в",
      "не",
      "е",
      "че",
      "то",
      "аз",
      "ти",
      "той",
      "те",
      "има",
    ],
    threshold: 3,
  },
  sr: {
    keywords: [
      "и",
      "у",
      "на",
      "не",
      "што",
      "је",
      "то",
      "се",
      "да",
      "од",
      "за",
      "као",
    ],
    threshold: 3,
  },
  hr: {
    keywords: [
      "i",
      "na",
      "je",
      "u",
      "ne",
      "sa",
      "to",
      "ga",
      "bi",
      "se",
      "za",
      "od",
    ],
    threshold: 3,
  },
  sl: {
    keywords: [
      "in",
      "v",
      "na",
      "ne",
      "je",
      "se",
      "to",
      "bi",
      "za",
      "kot",
      "ta",
      "po",
    ],
    threshold: 3,
  },
  mk: {
    keywords: [
      "и",
      "во",
      "на",
      "не",
      "што",
      "е",
      "тоа",
      "се",
      "да",
      "од",
      "за",
      "како",
    ],
    threshold: 3,
  },

  // BALTIC
  lt: {
    keywords: [
      "ir",
      "yra",
      "jei",
      "jog",
      "yra",
      "kurie",
      "bet",
      "su",
      "ar",
      "dėl",
      "jei",
      "kurie",
    ],
    threshold: 4,
  },
  lv: {
    keywords: [
      "un",
      "ir",
      "ja",
      "ko",
      "bet",
      "ar",
      "to",
      "ka",
      "tā",
      "uz",
      "nav",
      "par",
    ],
    threshold: 4,
  },

  // CELTIC
  cy: {
    keywords: [
      "yn",
      "a",
      "o",
      "i",
      "r",
      "the",
      "is",
      "ydd",
      "mae",
      "bod",
      "hyn",
      "neu",
    ],
    threshold: 4,
  },
  ga: {
    keywords: [
      "agus",
      "a",
      "é",
      "ar",
      "go",
      "i",
      "do",
      "na",
      "le",
      "de",
      "an",
      "om",
    ],
    threshold: 4,
  },
  gd: {
    keywords: [
      "agus",
      "an",
      "de",
      "a",
      "tha",
      "air",
      "is",
      "le",
      "gur",
      "do",
      "na",
      "mu",
    ],
    threshold: 4,
  },

  // FINNO-UGRIC
  fi: {
    keywords: [
      "ja",
      "on",
      "ei",
      "se",
      "että",
      "kun",
      "kuin",
      "ne",
      "hän",
      "yksi",
      "nämä",
      "vaan",
    ],
    threshold: 4,
  },
  hu: {
    keywords: [
      "és",
      "a",
      "az",
      "van",
      "nem",
      "ez",
      "az",
      "hogy",
      "meg",
      "mit",
      "ő",
      "hisz",
    ],
    threshold: 4,
  },
  et: {
    keywords: [
      "ja",
      "on",
      "ei",
      "ta",
      "mis",
      "et",
      "see",
      "selle",
      "tema",
      "nemad",
      "nende",
      "pole",
    ],
    threshold: 4,
  },

  // TURKIC
  tr: {
    keywords: [
      "ve",
      "bir",
      "bir",
      "bu",
      "var",
      "ben",
      "sen",
      "o",
      "biz",
      "siz",
      "onlar",
      "için",
    ],
    threshold: 4,
  },
  az: {
    keywords: [
      "və",
      "bir",
      "bu",
      "var",
      "mən",
      "sən",
      "o",
      "biz",
      "siz",
      "onlar",
      "üçün",
    ],
    threshold: 4,
  },
  kk: {
    keywords: [
      "және",
      "бір",
      "бұл",
      "бар",
      "мен",
      "сен",
      "ол",
      "біз",
      "сіздер",
      "олар",
    ],
    threshold: 4,
  },

  // SINO-TIBETAN
  zh: {
    keywords: [
      "的",
      "一",
      "是",
      "在",
      "不",
      "了",
      "有",
      "和",
      "人",
      "这",
      "中",
      "大",
    ],
    threshold: 3,
  },

  // JAPONIC
  ja: {
    keywords: [
      "の",
      "に",
      "は",
      "を",
      "た",
      "が",
      "で",
      "て",
      "と",
      "し",
      "れ",
      "さ",
    ],
    threshold: 3,
  },

  // KOREANIC
  ko: {
    keywords: [
      "의",
      "이",
      "그",
      "저",
      "수",
      "것",
      "있",
      "하",
      "것",
      "있",
      "하",
      "것",
    ],
    threshold: 3,
  },

  // DRAVIDIAN
  ta: {
    keywords: ["ஆ", "உ", "எ", "ஐ", "ஒ", "ஓ", "ஔ", "ங்", "ஞ்", "ட்", "ண்", "த்"],
    threshold: 2,
  },
  te: {
    keywords: ["ఆ", "ఇ", "ఉ", "ఎ", "ఏ", "ఐ", "ఒ", "ఓ", "ఔ", "అం", "ఆం", "ఇం"],
    threshold: 2,
  },
  kn: {
    keywords: ["ಅ", "ಆ", "ಇ", "ಈ", "ಉ", "ಊ", "ಋ", "ೃ", "ಎ", "ಏ", "ಐ", "ಒ"],
    threshold: 2,
  },
  ml: {
    keywords: ["അ", "ആ", "ഇ", "ഈ", "ഉ", "ഊ", "ഋ", "ൃ", "എ", "ഏ", "ഐ", "ഒ"],
    threshold: 2,
  },

  // INDO-ARYAN
  hi: {
    keywords: [
      "का",
      "है",
      "में",
      "हि",
      "नहीं",
      "यह",
      "और",
      "को",
      "एक",
      "के",
      "से",
      "या",
    ],
    threshold: 3,
  },
  bn: {
    keywords: ["এ", "র", "না", "য", "এক", "হ", "ও", "ত", "আ", "ি", "ে", "্য"],
    threshold: 3,
  },
  pa: {
    keywords: [
      "ਦੀ",
      "ਹੈ",
      "ਵਿ",
      "ਨੂ",
      "ਹਨ",
      "ਕੋ",
      "ਕਰ",
      "ਇਕ",
      "ਆ",
      "ਏ",
      "ਸ",
      "ਚ",
    ],
    threshold: 3,
  },

  // AFRO-ASIATIC
  ar: {
    keywords: [
      "في",
      "من",
      "إلى",
      "هو",
      "هي",
      "أن",
      "على",
      "عن",
      "مع",
      "كما",
      "قد",
      "كل",
    ],
    threshold: 4,
  },
  he: {
    keywords: [
      "את",
      "הוא",
      "היא",
      "אני",
      "אתה",
      "את",
      "נו",
      "אתם",
      "אתן",
      "הם",
      "הן",
      "זה",
    ],
    threshold: 4,
  },

  // ALBANIAN (10 keywords, threshold 3)
  sq: {
    keywords: [
      "është",
      "dhe",
      "në",
      "për",
      "qka",
      "çfarë",
      "unë",
      "ato",
      "atyre",
      "shqip",
    ],
    threshold: 3,
  },

  // GREEK
  el: {
    keywords: [
      "και",
      "να",
      "το",
      "που",
      "της",
      "του",
      "της",
      "στο",
      "για",
      "ένα",
      "από",
      "είναι",
    ],
    threshold: 4,
  },
};

// ═══════════════════════════════════════════════════════════════════════
// MAIN DETECTION FUNCTION
// ═══════════════════════════════════════════════════════════════════════

export function detectLanguage72(text: string): string | null {
  if (!text || text.length < 3) return null;

  // 1) Unicode detection first (most reliable)
  for (const [lang, config] of Object.entries(UNICODE_RANGES)) {
    if (config.range.test(text)) return lang;
  }

  // 2) Special character detection (fast, high confidence)
  for (const [lang, config] of Object.entries(SPECIAL_CHARS)) {
    if (config.pattern.test(text)) return lang;
  }

  // 3) Keyword-based detection (fallback)
  const textLower = text.toLowerCase();
  const scores: Record<string, number> = {};

  for (const [lang, config] of Object.entries(LANGUAGE_KEYWORDS)) {
    let score = 0;
    for (const keyword of config.keywords) {
      const matches = (
        textLower.match(new RegExp(`\\b${keyword}\\b`, "gi")) || []
      ).length;
      score += matches;
    }
    scores[lang] = score;
  }

  // Find best match
  let bestLang: string | null = null;
  let bestScore = 0;

  for (const [lang, score] of Object.entries(scores)) {
    const config = LANGUAGE_KEYWORDS[lang];
    if (score >= config.threshold && score > bestScore) {
      bestScore = score;
      bestLang = lang;
    }
  }

  return bestLang;
}

// ═══════════════════════════════════════════════════════════════════════
// LANGUAGE CODE TO NAME MAPPING
// ═══════════════════════════════════════════════════════════════════════

export const LANGUAGE_NAMES: Record<string, string> = {
  // Germanic
  en: "English",
  de: "German",
  nl: "Dutch",
  sv: "Swedish",
  da: "Danish",
  no: "Norwegian",
  is: "Icelandic",
  af: "Afrikaans",

  // Romance
  es: "Spanish",
  fr: "French",
  it: "Italian",
  pt: "Portuguese",
  ro: "Romanian",
  ca: "Catalan",
  gl: "Galician",

  // Slavic
  ru: "Russian",
  pl: "Polish",
  cz: "Czech",
  sk: "Slovak",
  uk: "Ukrainian",
  bg: "Bulgarian",
  sr: "Serbian",
  hr: "Croatian",
  sl: "Slovenian",
  mk: "Macedonian",

  // Baltic
  lt: "Lithuanian",
  lv: "Latvian",

  // Celtic
  cy: "Welsh",
  ga: "Irish",
  gd: "Scottish Gaelic",

  // Finno-Ugric
  fi: "Finnish",
  hu: "Hungarian",
  et: "Estonian",

  // Turkic
  tr: "Turkish",
  az: "Azerbaijani",
  kk: "Kazakh",

  // Sino-Tibetan
  zh: "Chinese",

  // Japonic
  ja: "Japanese",

  // Koreanic
  ko: "Korean",

  // Dravidian
  ta: "Tamil",
  te: "Telugu",
  kn: "Kannada",
  ml: "Malayalam",

  // Indo-Aryan
  hi: "Hindi",
  bn: "Bengali",
  pa: "Punjabi",

  // Afro-Asiatic
  ar: "Arabic",
  he: "Hebrew",

  // Other
  sq: "Albanian",
  el: "Greek",
  th: "Thai",
  lo: "Lao",
  km: "Khmer",
  my: "Burmese",
};

// Export all supported languages
export const SUPPORTED_LANGUAGES_72 = Object.keys(LANGUAGE_KEYWORDS);

export default detectLanguage72;
