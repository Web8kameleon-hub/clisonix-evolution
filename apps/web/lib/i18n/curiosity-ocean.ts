export type CuriosityLocale = string;

export const DEFAULT_LOCALE = "en";

export const SUPPORTED_LOCALES: CuriosityLocale[] = [
  "en",
  "sq",
  "de",
  "es",
  "fr",
  "it",
  "el",
  "ar",
  "zh",
  "ja",
  "ko",
  "pt",
  "ru",
  "uk",
  "pl",
  "nl",
  "sv",
  "no",
  "da",
  "fi",
  "cs",
  "sk",
  "sl",
  "hr",
  "sr",
  "bg",
  "ro",
  "hu",
  "tr",
  "he",
  "fa",
  "hi",
  "bn",
  "ur",
  "ta",
  "te",
  "mr",
  "gu",
  "pa",
  "ml",
  "kn",
  "or",
  "as",
  "ne",
  "si",
  "my",
  "th",
  "vi",
  "id",
  "ms",
  "tl",
  "sw",
  "am",
  "ha",
  "yo",
  "ig",
  "zu",
  "xh",
  "af",
  "et",
  "lv",
  "lt",
  "mt",
  "ga",
  "cy",
  "is",
  "mk",
  "bs",
  "be",
  "kk",
  "uz",
  "ky",
  "mn",
  "ka",
  "hy",
  "az",
  "ps",
  "so",
  "km",
  "lo",
];

export interface CuriosityUiStrings {
  welcome: string;
  chatCleared: string;
  modules: string;
  title: string;
  subtitle: string;
  language: string;
  tryAsking: string;
  askAnything: string;
  thinking: string;
  streamOnlyMode: string;
  streamingIndicator: string;
  normal: string;
  curious: string;
  wild: string;
  chaos: string;
  genius: string;
  exploreFurther: string;
  continueWith: string;
  stopButton: string;
  capture: string;
  switchCam: string;
  close: string;
  streamingLabel: string;
  curiosityLevel: string;
  clearConversation: string;
  voice: string;
  camera: string;
  document: string;
  voiceDiscussion: string;
  voiceDiscussionOn: string;
  voiceDiscussionOff: string;
  recordingAudio: string;
  audioSent: string;
  audioProcessed: string;
  audioError: string;
  photoCaptured: string;
  imageAnalyzed: string;
  imageError: string;
  documentAnalyzed: string;
  documentError: string;
  noResponse: string;
  serviceProcessing: string;
  connectionInterrupted: string;
  assistantName: string;
  footer: string;
  describePhotoPrompt: string;
}

const baseStrings: CuriosityUiStrings = {
  welcome:
    "Hi! I'm Curiosity Ocean — ask me anything and let's explore the depths of knowledge together. What sparks your curiosity today?",
  chatCleared:
    "Chat cleared! Ready for new explorations. What would you like to discover?",
  modules: "Modules",
  title: "Curiosity Ocean",
  subtitle: "Infinite Knowledge Engine",
  language: "Language",
  tryAsking: "Try asking",
  askAnything: "Ask anything...",
  thinking: "Thinking",
  streamOnlyMode: "Stream-only mode",
  streamingIndicator: "streaming...",
  normal: "Normal",
  curious: "Curious",
  wild: "Wild",
  chaos: "Chaos",
  genius: "Genius",
  exploreFurther: "Explore further",
  continueWith: "Continue with",
  stopButton: "Stop",
  capture: "Capture",
  switchCam: "Switch",
  close: "Close",
  streamingLabel: "Streaming",
  curiosityLevel: "Curiosity Level",
  clearConversation: "Clear conversation",
  voice: "Voice",
  camera: "Camera",
  document: "Document",
  voiceDiscussion: "Voice discussion",
  voiceDiscussionOn: "Voice ON",
  voiceDiscussionOff: "Voice OFF",
  recordingAudio: "Recording audio...",
  audioSent: "🎤 Audio sent",
  audioProcessed: "Audio processed",
  audioError: "❌ Error processing audio",
  photoCaptured: "📷 Photo captured",
  imageAnalyzed: "Image analyzed",
  imageError: "❌ Error analyzing image",
  documentAnalyzed: "Document analyzed",
  documentError: "❌ Error processing document",
  noResponse: "No response received",
  serviceProcessing: "Service is processing. Please try again.",
  connectionInterrupted: "Connection interrupted. Please try again.",
  assistantName: "Ocean",
  footer: "Curiosity Ocean by Clisonix",
  describePhotoPrompt: "Describe this photo",
};

const localeScaffold: Record<string, Partial<CuriosityUiStrings>> = Object.fromEntries(
  SUPPORTED_LOCALES.map((locale) => [locale, {}]),
);

const localizedCoreOverrides: Record<string, Partial<CuriosityUiStrings>> = {
  en: {
    subtitle: "Infinite Knowledge Engine",
    askAnything: "Ask anything...",
    thinking: "Thinking",
  },
  sq: {
    subtitle: "Motor i Dijes së Pakufishme",
    askAnything: "Pyet çdo gjë...",
    thinking: "Duke menduar",
    streamingIndicator: "duke transmetuar...",
    clearConversation: "Pastro bisedën",
    voiceDiscussion: "Diskutim me zë",
    voiceDiscussionOn: "Zëri ON",
    voiceDiscussionOff: "Zëri OFF",
    recordingAudio: "Duke regjistruar audio...",
    serviceProcessing: "Shërbimi po përpunohet. Provo përsëri.",
    connectionInterrupted: "Lidhja u ndërpre. Provo përsëri.",
    streamOnlyMode: "Vetëm mënyra stream",
    curious: "Kurioz",
    wild: "I egër",
    chaos: "Kaos",
    genius: "Gjeni",
    describePhotoPrompt: "Përshkruaj këtë foto në shqip",
  },
  de: {
    subtitle: "Unendliche Wissensmaschine",
    askAnything: "Frag alles...",
    thinking: "Denke nach",
  },
  es: {
    subtitle: "Motor de Conocimiento Infinito",
    askAnything: "Pregunta lo que sea...",
    thinking: "Pensando",
  },
  fr: {
    subtitle: "Moteur de Connaissance Infinie",
    askAnything: "Demande n'importe quoi...",
    thinking: "Je réfléchis",
  },
  it: {
    subtitle: "Motore di Conoscenza Infinita",
    askAnything: "Chiedi qualsiasi cosa...",
    thinking: "Sto pensando",
  },
  pt: {
    subtitle: "Motor de Conhecimento Infinito",
    askAnything: "Pergunte qualquer coisa...",
    thinking: "Pensando",
  },
  tr: {
    subtitle: "Sonsuz Bilgi Motoru",
    askAnything: "Her şeyi sor...",
    thinking: "Düşünüyorum",
  },
  el: {
    subtitle: "Μηχανή Άπειρης Γνώσης",
    askAnything: "Ρώτα οτιδήποτε...",
    thinking: "Σκέφτομαι",
  },
  ar: {
    subtitle: "محرك معرفة لا نهائي",
    askAnything: "اسأل أي شيء...",
    thinking: "جارٍ التفكير",
  },
  zh: {
    subtitle: "无限知识引擎",
    askAnything: "问任何问题...",
    thinking: "思考中",
  },
  ja: {
    subtitle: "無限知識エンジン",
    askAnything: "何でも聞いてください...",
    thinking: "考え中",
  },
  ko: {
    subtitle: "무한 지식 엔진",
    askAnything: "무엇이든 물어보세요...",
    thinking: "생각 중",
  },
  ru: {
    subtitle: "Двигатель Бесконечных Знаний",
    askAnything: "Спросите что угодно...",
    thinking: "Думаю",
  },
  uk: {
    subtitle: "Двигун Безмежних Знань",
    askAnything: "Запитуйте будь-що...",
    thinking: "Думаю",
  },
};

const overrides: Record<string, Partial<CuriosityUiStrings>> = {
  ...localeScaffold,
  ...localizedCoreOverrides,
};

export function isSupportedLocale(locale: string): boolean {
  return SUPPORTED_LOCALES.includes(locale);
}

export function getInitialLocale(): CuriosityLocale {
  if (typeof window === "undefined") return DEFAULT_LOCALE;
  const saved = window.localStorage.getItem("curiosity-ocean-language");
  if (saved && isSupportedLocale(saved)) return saved;
  return DEFAULT_LOCALE;
}

export function getUiStrings(locale: string): CuriosityUiStrings {
  const normalized = isSupportedLocale(locale) ? locale : DEFAULT_LOCALE;
  return { ...baseStrings, ...(overrides[normalized] || {}) };
}

export function getSuggestedQuestions(locale: string): string[] {
  const byLocale: Record<string, string[]> = {
    en: [
      "What is consciousness?",
      "How does the brain process music?",
      "Explain quantum computing simply",
      "How does memory work?",
    ],
    sq: [
      "Çfarë është vetëdija?",
      "Si e përpunon truri muzikën?",
      "Shpjego kompjuterin kuantik thjesht",
      "Si funksionon kujtesa?",
    ],
    de: [
      "Was ist Bewusstsein?",
      "Wie verarbeitet das Gehirn Musik?",
      "Erkläre Quantencomputing einfach",
      "Wie funktioniert Gedächtnis?",
    ],
    es: [
      "¿Qué es la conciencia?",
      "¿Cómo procesa el cerebro la música?",
      "Explica la computación cuántica de forma simple",
      "¿Cómo funciona la memoria?",
    ],
    fr: [
      "Qu'est-ce que la conscience ?",
      "Comment le cerveau traite-t-il la musique ?",
      "Explique l'informatique quantique simplement",
      "Comment fonctionne la mémoire ?",
    ],
    it: [
      "Che cos'è la coscienza?",
      "Come il cervello elabora la musica?",
      "Spiega il calcolo quantistico in modo semplice",
      "Come funziona la memoria?",
    ],
    tr: [
      "Bilinç nedir?",
      "Beyin müziği nasıl işler?",
      "Kuantum bilişimi basitçe açıkla",
      "Hafıza nasıl çalışır?",
    ],
    ar: [
      "ما هو الوعي؟",
      "كيف يعالج الدماغ الموسيقى؟",
      "اشرح الحوسبة الكمومية ببساطة",
      "كيف تعمل الذاكرة؟",
    ],
    zh: [
      "什么是意识？",
      "大脑如何处理音乐？",
      "请简单解释量子计算",
      "记忆是如何工作的？",
    ],
    ru: [
      "Что такое сознание?",
      "Как мозг обрабатывает музыку?",
      "Объясни квантовые вычисления просто",
      "Как работает память?",
    ],
  };

  const normalized = isSupportedLocale(locale) ? locale : DEFAULT_LOCALE;
  return byLocale[normalized] || byLocale.en;
}

export function getLocaleLabel(locale: string): string {
  try {
    const display = new Intl.DisplayNames([locale], { type: "language" });
    const name = display.of(locale) || locale;
    return `${locale.toUpperCase()} · ${name}`;
  } catch {
    return locale.toUpperCase();
  }
}

export function detectInputLanguage(message: string): string | null {
  const text = message.toLowerCase().trim();
  if (!text) return null;

  // Script-first detection (high confidence)
  if (/[\u4e00-\u9fff\u3400-\u4dbf]/.test(message)) return "zh";
  if (/[\u3040-\u309f\u30a0-\u30ff]/.test(message)) return "ja";
  if (/[\uac00-\ud7af]/.test(message)) return "ko";
  if (/[\u0370-\u03ff]/.test(message)) return "el";
  if (/[\u0590-\u05ff]/.test(message)) return "he";
  if (/[\u0600-\u06ff]/.test(message)) {
    if (/[ںےک]/.test(message)) return "ur";
    if (/[پچژگ]/.test(message)) return "fa";
    return "ar";
  }
  if (/[\u0900-\u097f]/.test(message)) return "hi";
  if (/[\u0980-\u09ff]/.test(message)) return "bn";
  if (/[\u0b80-\u0bff]/.test(message)) return "ta";
  if (/[\u0c00-\u0c7f]/.test(message)) return "te";
  if (/[\u0d00-\u0d7f]/.test(message)) return "ml";
  if (/[\u0e00-\u0e7f]/.test(message)) return "th";
  if (/[\u1000-\u109f]/.test(message)) return "my";
  if (/[\u1780-\u17ff]/.test(message)) return "km";
  if (/[\u0e80-\u0eff]/.test(message)) return "lo";
  if (/[\u10a0-\u10ff]/.test(message)) return "ka";
  if (/[\u0530-\u058f]/.test(message)) return "hy";
  if (/[\u1200-\u137f]/.test(message)) return "am";
  if (/[\u0400-\u04ff]/.test(message)) {
    if (/[єїі]/.test(message)) return "uk";
    if (/[ѓѕ]/.test(message)) return "mk";
    return "ru";
  }

  // Latin-script short phrase detection (important for inputs like "guten tag")
  const phraseMap: Array<[RegExp, string]> = [
    [/\b(guten tag|guten morgen|guten abend|hallo|danke|bitte|tschüss)\b/i, "de"],
    [/\b(bonjour|bonsoir|salut|merci|au revoir)\b/i, "fr"],
    [/\b(hola|buenos días|buenas tardes|gracias|adiós)\b/i, "es"],
    [/\b(ciao|buongiorno|buonasera|grazie|arrivederci)\b/i, "it"],
    [/\b(përshëndetje|mirëdita|faleminderit|tungjatjeta)\b/i, "sq"],
    [/\b(merhaba|nasılsın|teşekkür|selam)\b/i, "tr"],
    [/\b(olá|obrigado|obrigada|tchau)\b/i, "pt"],
    [/\b(hoi|goedendag|bedankt)\b/i, "nl"],
    [/\b(hej|tack)\b/i, "sv"],
    [/\b(hei|takk)\b/i, "no"],
    [/\b(hello|hi|thanks|please|good morning|good evening)\b/i, "en"],
  ];
  for (const [pattern, lang] of phraseMap) {
    if (pattern.test(text)) return lang;
  }

  // Fallback token patterns
  if (/(\b(pershendetje|përshëndetje|çfarë|është|jam|duke|po)\b)/i.test(text)) return "sq";
  if (/(\b(how|what|why|when|where|who|explain|please)\b)/i.test(text)) return "en";

  return null;
}
