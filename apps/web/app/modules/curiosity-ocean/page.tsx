'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Sparkles, RefreshCw, Loader2, Mic, Camera, FileText, X, Plus, Settings2, ArrowLeft, Volume2, VolumeX, UserCircle2, Bot } from 'lucide-react';
import { useAuth, useUser } from '@/lib/auth/client';

/**
 * CURIOSITY OCEAN — Ultra-Modern AI Chat
 * Clean, minimal, powerful. Streaming + Multimodal.
 */

// ============================================================================
// TRANSLATIONS
// ============================================================================
const translations: Record<string, {
  welcome: string;
  chatCleared: string;
  modules: string;
  title: string;
  subtitle: string;
  streaming: string;
  normal: string;
  curious: string;
  wild: string;
  chaos: string;
  genius: string;
  tryAsking: string;
  askAnything: string;
  thinking: string;
  streamingIndicator: string;
  exploreFurther: string;
  continueWith: string;
  stopButton: string;
  sendAskButton?: string;
  capture: string;
  switchCam: string;
  close: string;
}> = {
  en: {
    welcome: "Hi! I'm Curiosity Ocean — ask me anything and let's explore the depths of knowledge together. What sparks your curiosity today?",
    chatCleared: "Chat cleared! Ready for new explorations. What would you like to discover?",
    modules: "Modules",
    title: "Curiosity Ocean",
    subtitle: "Infinite Knowledge Engine",
    streaming: "Stream",
    normal: "Normal",
    curious: "Curious",
    wild: "Wild",
    chaos: "Chaos",
    genius: "Genius",
    tryAsking: "Try asking",
    askAnything: "Ask anything...",
    thinking: "Thinking",
    streamingIndicator: "streaming...",
    exploreFurther: "Explore further",
    continueWith: "Continue with",
    stopButton: "Stop",
    sendAskButton: "Send Ask",
    capture: "Capture",
    switchCam: "Switch",
    close: "Close",
  },
  sq: {
    welcome: "Përshëndetje! Jam Curiosity Ocean — më pyet çdo gjë dhe le të eksplorojmë thellësitë e dijes së bashku. Çfarë ngjall kuriozitetin tënd sot?",
    chatCleared: "Biseda u pastrua! Gati për eksplorime të reja. Çfarë dëshiron të zbulosh?",
    modules: "Module",
    title: "Curiosity Ocean",
    subtitle: "Motor i Dijes së Pakufishme",
    streaming: "Stream",
    normal: "Normal",
    curious: "Kurioz",
    wild: "I egër",
    chaos: "Kaos",
    genius: "Gjeni",
    tryAsking: "Provo të pyesësh",
    askAnything: "Pyet çdo gjë...",
    thinking: "Duke menduar",
    streamingIndicator: "duke transmetuar...",
    exploreFurther: "Eksploro më shumë",
    continueWith: "Vazhdo me",
    stopButton: "Ndalo",
    sendAskButton: "Dërgo Pyetjen",
    capture: "Kap",
    switchCam: "Ndrysho",
    close: "Mbyll",
  },
  de: {
    welcome: "Willkommen bei Curiosity Ocean! Frag mich alles und lass uns gemeinsam die Tiefen des Wissens erkunden. Was weckt deine Neugier heute?",
    chatCleared: "Chat gelöscht! Bereit für neue Erkundungen. Was möchtest du entdecken?",
    modules: "Module",
    title: "Curiosity Ocean",
    subtitle: "Unendliche Wissens-Engine",
    streaming: "Stream",
    normal: "Normal",
    curious: "Neugierig",
    wild: "Wild",
    chaos: "Chaos",
    genius: "Genie",
    tryAsking: "Versuch zu fragen",
    askAnything: "Frag was du willst...",
    thinking: "Denke nach",
    streamingIndicator: "streaming...",
    exploreFurther: "Weiter erkunden",
    continueWith: "Weiter mit",
    stopButton: "Stopp",
    capture: "Aufnehmen",
    switchCam: "Wechseln",
    close: "Schließen",
  },
  es: {
    welcome: "¡Bienvenido a Curiosity Ocean! Pregúntame lo que sea y exploremos juntos las profundidades del conocimiento. ¿Qué despierta tu curiosidad hoy?",
    chatCleared: "¡Chat borrado! Listo para nuevas exploraciones. ¿Qué quieres descubrir?",
    modules: "Módulos",
    title: "Curiosity Ocean",
    subtitle: "Motor de Conocimiento Infinito",
    streaming: "Stream",
    normal: "Normal",
    curious: "Curioso",
    wild: "Salvaje",
    chaos: "Caos",
    genius: "Genio",
    tryAsking: "Intenta preguntar",
    askAnything: "Pregunta lo que sea...",
    thinking: "Pensando",
    streamingIndicator: "transmitiendo...",
    exploreFurther: "Explorar más",
    continueWith: "Continuar con",
    stopButton: "Parar",
    capture: "Capturar",
    switchCam: "Cambiar",
    close: "Cerrar",
  },
  fr: {
    welcome: "Bienvenue sur Curiosity Ocean! Pose-moi n'importe quelle question et explorons ensemble les profondeurs du savoir. Qu'est-ce qui éveille ta curiosité aujourd'hui?",
    chatCleared: "Chat effacé! Prêt pour de nouvelles explorations. Que veux-tu découvrir?",
    modules: "Modules",
    title: "Curiosity Ocean",
    subtitle: "Moteur de Connaissance Infinie",
    streaming: "Stream",
    normal: "Normal",
    curious: "Curieux",
    wild: "Sauvage",
    chaos: "Chaos",
    genius: "Génie",
    tryAsking: "Essaye de demander",
    askAnything: "Demande n'importe quoi...",
    thinking: "Je réfléchis",
    streamingIndicator: "diffusion...",
    exploreFurther: "Explorer plus",
    continueWith: "Continuer avec",
    stopButton: "Arrêter",
    capture: "Capturer",
    switchCam: "Changer",
    close: "Fermer",
  },
  it: {
    welcome: "Benvenuto su Curiosity Ocean! Chiedimi qualsiasi cosa ed esploriamo insieme le profondità della conoscenza. Cosa suscita la tua curiosità oggi?",
    chatCleared: "Chat cancellata! Pronto per nuove esplorazioni. Cosa vorresti scoprire?",
    modules: "Moduli",
    title: "Curiosity Ocean",
    subtitle: "Motore di Conoscenza Infinita",
    streaming: "Stream",
    normal: "Normale",
    curious: "Curioso",
    wild: "Selvaggio",
    chaos: "Caos",
    genius: "Genio",
    tryAsking: "Prova a chiedere",
    askAnything: "Chiedi qualsiasi cosa...",
    thinking: "Sto pensando",
    streamingIndicator: "streaming...",
    exploreFurther: "Esplora di più",
    continueWith: "Continua con",
    stopButton: "Ferma",
    capture: "Cattura",
    switchCam: "Cambia",
    close: "Chiudi",
  },
  zh: {
    welcome: "欢迎来到Curiosity Ocean！问我任何问题，让我们一起探索知识的深度。今天什么激发了你的好奇心？",
    chatCleared: "聊天已清除！准备好新的探索。你想发现什么？",
    modules: "模块",
    title: "Curiosity Ocean",
    subtitle: "无限知识引擎",
    streaming: "流",
    normal: "普通",
    curious: "好奇",
    wild: "狂野",
    chaos: "混沌",
    genius: "天才",
    tryAsking: "试着问",
    askAnything: "问任何问题...",
    thinking: "思考中",
    streamingIndicator: "流媒体...",
    exploreFurther: "深入探索",
    continueWith: "继续",
    stopButton: "停止",
    capture: "拍摄",
    switchCam: "切换",
    close: "关闭",
  },
  ja: {
    welcome: "Curiosity Oceanへようこそ！何でも聞いてください。一緒に知識の深みを探検しましょう。今日は何があなたの好奇心をかきたてますか？",
    chatCleared: "チャットがクリアされました！新しい探検の準備ができました。何を発見したいですか？",
    modules: "モジュール",
    title: "Curiosity Ocean",
    subtitle: "無限の知識エンジン",
    streaming: "ストリーム",
    normal: "通常",
    curious: "好奇心",
    wild: "ワイルド",
    chaos: "カオス",
    genius: "天才",
    tryAsking: "質問してみてください",
    askAnything: "何でも聞いてください...",
    thinking: "考え中",
    streamingIndicator: "ストリーミング中...",
    exploreFurther: "さらに探る",
    continueWith: "続ける",
    stopButton: "停止",
    capture: "撮影",
    switchCam: "切替",
    close: "閉じる",
  },
  ko: {
    welcome: "Curiosity Ocean에 오신 것을 환영합니다! 무엇이든 물어보세요. 함께 지식의 깊이를 탐험해 봅시다. 오늘 무엇이 당신의 호기심을 자극하나요?",
    chatCleared: "채팅이 삭제되었습니다! 새로운 탐험 준비가 되었습니다. 무엇을 발견하고 싶으신가요?",
    modules: "모듈",
    title: "Curiosity Ocean",
    subtitle: "무한 지식 엔진",
    streaming: "스트림",
    normal: "일반",
    curious: "호기심",
    wild: "와일드",
    chaos: "카오스",
    genius: "천재",
    tryAsking: "질문해 보세요",
    askAnything: "무엇이든 물어보세요...",
    thinking: "생각 중",
    streamingIndicator: "스트리밍...",
    exploreFurther: "더 탐구하기",
    continueWith: "계속하기",
    stopButton: "중지",
    capture: "촬영",
    switchCam: "전환",
    close: "닫기",
  },
};

function detectLanguage(): string {
  if (typeof window === 'undefined') return 'en';
  const browserLang = navigator.language.split('-')[0].toLowerCase();
  return translations[browserLang] ? browserLang : 'en';
}

function normalizeLangCode(input?: string | null): string {
  if (!input) return 'auto';
  const normalized = input.trim().toLowerCase().replace('_', '-');
  if (!normalized || normalized === 'auto') return 'auto';

  const base = normalized.split('-')[0];
  const aliasMap: Record<string, string> = {
    al: 'sq',
    gb: 'en',
    uk: 'en',
    cn: 'zh',
    jp: 'ja',
    kr: 'ko',
  };

  const mapped = aliasMap[base] || base;
  if (translations[mapped]) return mapped;
  return 'auto';
}

function isAlgebraBinaryTopic(input: string): boolean {
  const text = (input || '').toLowerCase();
  if (!text) return false;
  if (/0b[01]+|\b[01]{5,}\b/.test(text)) return true;
  if (/\d+\s*(xor|and|or|\+|\-|\*|\/|\^|>>|<<|&|\|)\s*\d+/i.test(text)) return true;
  return /(algebra|equation|math|matrix|binary|bitwise|boolean|logic gate|xor|nand|nor)/i.test(text);
}

type PreEnterClass = {
  bitMode: '1bit' | '10000bit';
  tokenBudget: number;
  processingMode: 'fast' | 'deep';
  curiosityHint: 'curious' | 'wild' | 'chaos' | 'genius';
};

function classifyPreEnterIntent(input: string): PreEnterClass {
  const text = (input || '').trim();
  if (!text) {
    return {
      bitMode: '1bit',
      tokenBudget: 64,
      processingMode: 'fast',
      curiosityHint: 'curious',
    };
  }

  const shortLowCost =
    text.length <= 28 &&
    /^(ok|po|jo|yes|no|mir[eë]|pershendetje|hello|hi|test|ping|vazhdo|continue|go)$/i.test(text);

  const deepSignal =
    text.length > 120 ||
    /(deepthink|plan|strateg|arkitektur|algorithm|analiz|research|krahas|optimiz|implement|refactor|design|debug|production|roadmap|enterprise|scal(e|ing))/i.test(text);

  if (shortLowCost) {
    return {
      bitMode: '1bit',
      tokenBudget: 64,
      processingMode: 'fast',
      curiosityHint: 'curious',
    };
  }

  if (deepSignal) {
    return {
      bitMode: '10000bit',
      tokenBudget: 10000,
      processingMode: 'deep',
      curiosityHint: 'genius',
    };
  }

  return {
    bitMode: '10000bit',
    tokenBudget: 1024,
    processingMode: 'fast',
    curiosityHint: 'wild',
  };
}

function toBoundedInt(value: string | null, fallback: number, min: number, max: number): number {
  const parsed = Number.parseInt(value || '', 10);
  if (Number.isNaN(parsed)) return fallback;
  return Math.max(min, Math.min(max, parsed));
}

const SUGGESTED_QUESTIONS: Record<string, string[]> = {
  en: [
    "🧠 DeepThink this topic and give me a clear plan",
    "🎙️ Create a podcast episode outline with segments",
    "📝 Build a quiz with answers and scoring",
    "🛍️ Do shopping research with pros/cons and best picks",
  ],
  sq: [
    "🧠 Bëj DeepThink për këtë temë dhe jep plan të qartë",
    "🎙️ Krijo strukturë podcasti me seksione",
    "📝 Krijo quiz me përgjigje dhe pikëzim",
    "🛍️ Bëj shopping research me krahasim të qartë",
  ],
  de: [
    "🧠 DeepThink zu diesem Thema und gib mir einen klaren Plan",
    "🎙️ Erstelle einen Podcast-Ablauf mit Segmenten",
    "📝 Erstelle ein Quiz mit Antworten und Bewertung",
    "🛍️ Mache Shopping-Recherche mit klaren Empfehlungen",
  ],
  es: [
    "¿Qué es la consciencia?",
    "¿Cómo procesa el cerebro la música?",
    "Explica la computación cuántica simplemente",
    "¿Cómo funciona la memoria?",
  ],
  fr: [
    "Qu'est-ce que la conscience?",
    "Comment le cerveau traite-t-il la musique?",
    "Explique l'informatique quantique simplement",
    "Comment fonctionne la mémoire?",
  ],
  it: [
    "Cos'è la coscienza?",
    "Come elabora il cervello la musica?",
    "Spiega il calcolo quantistico semplicemente",
    "Come funziona la memoria?",
  ],
  zh: [
    "什么是意识？",
    "大脑如何处理音乐？",
    "简单解释量子计算",
    "记忆是如何工作的？",
  ],
  ja: [
    "意識とは何ですか？",
    "脳はどのように音楽を処理しますか？",
    "量子コンピューティングを簡単に説明してください",
    "記憶はどのように機能しますか？",
  ],
  ko: [
    "의식이란 무엇인가요?",
    "뇌는 음악을 어떻게 처리하나요?",
    "양자 컴퓨팅을 간단히 설명해주세요",
    "기억은 어떻게 작동하나요?",
  ],
};

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
  rabbitHoles?: string[];
  nextQuestions?: string[];
}

type RuntimeCardState = 'live' | 'limited' | 'offline';

interface RuntimeSignalCard {
  label: string;
  emoji: string;
  state: RuntimeCardState;
  detail: string;
}

function getRuntimeCardClasses(state: RuntimeCardState): string {
  if (state === 'live') return 'border-emerald-200 bg-emerald-50 text-emerald-800';
  if (state === 'limited') return 'border-amber-200 bg-amber-50 text-amber-800';
  return 'border-slate-200 bg-slate-100 text-slate-700';
}

const OCEAN_LOCAL_MEMORY_KEY_PREFIX = 'clisonix:ocean:memory:v1';
const OCEAN_LOCAL_REFERENCE_KEY_PREFIX = 'clisonix:ocean:reference:v1';
const OCEAN_MAX_LOCAL_MESSAGES = 80;

function serializeMessagesForLocal(messages: Message[]): Array<Record<string, unknown>> {
  return messages
    .slice(-OCEAN_MAX_LOCAL_MESSAGES)
    .map((message) => ({
      id: message.id,
      type: message.type,
      content: message.content,
      timestamp: message.timestamp instanceof Date
        ? message.timestamp.toISOString()
        : new Date(message.timestamp as unknown as string).toISOString(),
      rabbitHoles: message.rabbitHoles || [],
      nextQuestions: message.nextQuestions || [],
    }));
}

function deserializeMessagesFromLocal(raw: unknown): Message[] {
  if (!Array.isArray(raw)) return [];

  return raw
    .map((item) => {
      if (!item || typeof item !== 'object') return null;
      const row = item as Record<string, unknown>;
      const id = typeof row.id === 'string' ? row.id : '';
      const type = row.type === 'user' || row.type === 'ai' ? row.type : null;
      const content = typeof row.content === 'string' ? row.content : '';
      const timestampRaw = typeof row.timestamp === 'string' ? row.timestamp : '';
      const timestamp = timestampRaw ? new Date(timestampRaw) : new Date();
      if (!id || !type || !content || Number.isNaN(timestamp.getTime())) return null;

      return {
        id,
        type,
        content,
        timestamp,
        rabbitHoles: Array.isArray(row.rabbitHoles) ? row.rabbitHoles.filter((x) => typeof x === 'string') as string[] : undefined,
        nextQuestions: Array.isArray(row.nextQuestions) ? row.nextQuestions.filter((x) => typeof x === 'string') as string[] : undefined,
        isStreaming: false,
      } as Message;
    })
    .filter((value): value is Message => Boolean(value));
}

function normalizeOceanSSE(text: string): string {
  if (!text || !text.includes('data:')) return text;

  const lines = text.split(/\r?\n/);
  let rebuilt = '';
  let foundData = false;

  for (const rawLine of lines) {
    const line = rawLine.replace(/\r$/, '');
    if (!line || !line.startsWith('data:')) continue;

    foundData = true;
    let payload = line.slice(5);
    if (payload.startsWith(' ')) payload = payload.slice(1);
    if (!payload || payload === '[DONE]') continue;

    try {
      const parsed = JSON.parse(payload);
      if (typeof parsed?.chunk === 'string') rebuilt += parsed.chunk;
      else if (typeof parsed?.response === 'string') rebuilt += parsed.response;
      else if (typeof parsed?.text === 'string') rebuilt += parsed.text;
    } catch {
      rebuilt += payload;
    }
  }

  return foundData && rebuilt ? rebuilt : text;
}

function sanitizeOceanMessage(text: string): string {
  if (!text) return '';

  const normalized = normalizeOceanSSE(text)
    .replace(/\[DONE\]/gi, '')
    .replace(/\bdata:\s*/gi, '')
    .replace(/"chunk"\s*:\s*/gi, '');

  // Strip non-functional reaction emojis returned by some upstream payloads.
  const withoutReactionEmojis = normalized
    .replace(/[👍😂🤔👏]/g, '')
    .replace(/❤️|❤/g, '')
    .replace(/🔥/g, '')
    .replace(/\n\s*[👍😂🤔👏❤️❤🔥\s]+\n/g, '\n')
    .replace(/\s{2,}/g, ' ');

  const sensitivePattern = /(?:api[_-]?key|access[_-]?token|secret[_-]?(?:key|token|value)|password\s*[=:]|authorization\s*:|bearer\s+[a-z0-9._-]+)/i;
  const credentialPattern = /(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+|sk_(?:live|test)_[A-Za-z0-9]+)/i;
  const internalPattern = /(?:docker-compose|\.env(?:\.[A-Za-z0-9_-]+)?|\/app\/|[A-Za-z]:\\Users\\|services\/[a-z0-9_.-]+|apps\/[a-z0-9_./-]+|host\.docker\.internal|localhost:\d{2,5}|127\.0\.0\.1:\d{2,5}|clisonix-[a-z0-9-]+|KLOUD_[A-Z_]+|OCEAN_[A-Z_]+|REDIS_URL|DATABASE_URL|OPENAI_API_KEY|STRIPE_[A-Z_]+|PAYPAL_[A-Z_]+)/i;

  const lines = withoutReactionEmojis.split(/\r?\n/);
  const cleaned: string[] = [];

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      cleaned.push(line);
      continue;
    }

    if (/^(sources?|references?)\s*:/i.test(trimmed)) break;
    if (/^\[?sources?\]?$/i.test(trimmed)) break;
    if (/^\[?references?\]?$/i.test(trimmed)) break;

    if (credentialPattern.test(trimmed) || sensitivePattern.test(trimmed)) {
      if (cleaned[cleaned.length - 1] !== 'Sensitive security details were removed from this public response.') {
        cleaned.push('Sensitive security details were removed from this public response.');
      }
      continue;
    }

    if (internalPattern.test(trimmed)) {
      if (cleaned[cleaned.length - 1] !== 'Internal implementation details were hidden to keep this experience client-safe.') {
        cleaned.push('Internal implementation details were hidden to keep this experience client-safe.');
      }
      continue;
    }

    cleaned.push(line);
  }

  return cleaned.join('\n').replace(/\n{3,}/g, '\n\n').trim();
}

function extractOceanText(value: unknown): string {
  if (typeof value !== 'string' || !value) return '';
  return value;
}
function extractOceanChunkFromPayload(payload: unknown): string {
  if (!payload || typeof payload !== 'object') return '';

  const row = payload as Record<string, unknown>;
  return (
    extractOceanText(row.chunk) ||
    extractOceanText(row.response) ||
    extractOceanText(row.text) ||
    extractOceanText(row.content) ||
    extractOceanText(row.delta) ||
    extractOceanText(row.token) ||
    extractOceanText((row.message as Record<string, unknown> | undefined)?.content) ||
    extractOceanText((row.choices as Array<Record<string, unknown>> | undefined)?.[0]?.delta as unknown as string) ||
    extractOceanText(
      ((row.choices as Array<Record<string, unknown>> | undefined)?.[0]?.delta as Record<string, unknown> | undefined)?.content,
    ) ||
    ''
  );
}

type ResponsePayload = Record<string, unknown>;

async function readJsonOrTextResponse(response: Response): Promise<{
  data: ResponsePayload | null;
  text: string;
}> {
  const text = (await response.text()).trim();
  if (!text) {
    return { data: null, text: '' };
  }

  try {
    const parsed = JSON.parse(text) as unknown;
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return { data: parsed as ResponsePayload, text };
    }
  } catch {
  }

  return { data: null, text };
}

function getPayloadMessage(
  payload: { data: ResponsePayload | null; text: string },
  fallback: string,
): string {
  const message = payload.data?.message;
  if (typeof message === 'string' && message.trim()) {
    return message.trim();
  }

  const detail = payload.data?.detail;
  if (typeof detail === 'string' && detail.trim()) {
    return detail.trim();
  }

  const error = payload.data?.error;
  if (typeof error === 'string' && error.trim()) {
    return error.trim();
  }

  return payload.text || fallback;
}

type ParsedBlock =
  | { type: 'paragraph'; lines: string[] }
  | { type: 'table'; rows: string[][] }
  | { type: 'image'; alt: string; src: string };

function isMarkdownTableSeparator(line: string): boolean {
  const normalized = line.trim();
  if (!normalized.includes('|')) return false;
  const parts = normalized
    .split('|')
    .map((part) => part.trim())
    .filter(Boolean);
  return parts.length > 0 && parts.every((part) => /^:?-{3,}:?$/.test(part));
}

function isLikelyTableLine(line: string): boolean {
  const trimmed = line.trim();
  return trimmed.includes('|') && !trimmed.startsWith('```');
}

function parseTableRow(line: string): string[] {
  return line
    .trim()
    .replace(/^\|/, '')
    .replace(/\|$/, '')
    .split('|')
    .map((cell) => cell.trim());
}

function parseMessageBlocks(content: string): ParsedBlock[] {
  const lines = content.split(/\r?\n/);
  const blocks: ParsedBlock[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i] || '';
    const trimmed = line.trim();

    if (!trimmed) {
      i += 1;
      continue;
    }

    const imageMatch = trimmed.match(/^!\[(.*?)\]\((https?:\/\/[^\s)]+)\)$/i);
    if (imageMatch) {
      blocks.push({
        type: 'image',
        alt: imageMatch[1] || 'figure',
        src: imageMatch[2],
      });
      i += 1;
      continue;
    }

    const nextLine = lines[i + 1] || '';
    if (isLikelyTableLine(line) && isMarkdownTableSeparator(nextLine)) {
      const tableRows: string[][] = [parseTableRow(line)];
      i += 2;
      while (i < lines.length && isLikelyTableLine(lines[i])) {
        tableRows.push(parseTableRow(lines[i]));
        i += 1;
      }
      blocks.push({ type: 'table', rows: tableRows });
      continue;
    }

    const paragraphLines: string[] = [];
    while (i < lines.length) {
      const current = lines[i] || '';
      const currentTrimmed = current.trim();
      if (!currentTrimmed) break;

      const currentImage = currentTrimmed.match(/^!\[(.*?)\]\((https?:\/\/[^\s)]+)\)$/i);
      const upcoming = lines[i + 1] || '';
      if (currentImage) break;
      if (isLikelyTableLine(current) && isMarkdownTableSeparator(upcoming)) break;

      paragraphLines.push(current);
      i += 1;
    }

    if (paragraphLines.length > 0) {
      blocks.push({ type: 'paragraph', lines: paragraphLines });
      continue;
    }

    i += 1;
  }

  return blocks;
}

function renderInlineFormatting(text: string): JSX.Element[] {
  const strongParts = text.split(/(\*\*[^*]+\*\*)/g);

  return strongParts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return <strong key={`b-${idx}`}>{part.slice(2, -2)}</strong>;
    }

    const linkRegex = /(\[[^\]]+\]\(https?:\/\/[^)\s]+\)|https?:\/\/[^\s)]+)/g;
    const segments = part.split(linkRegex);

    return (
      <span key={`t-${idx}`}>
        {segments.map((segment, segIdx) => {
          if (!segment) return null;

          const markdownMatch = segment.match(/^\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)$/);
          if (markdownMatch) {
            return (
              <a
                key={`md-${idx}-${segIdx}`}
                href={markdownMatch[2]}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 underline decoration-blue-300 underline-offset-2 hover:text-blue-700"
              >
                {markdownMatch[1]}
              </a>
            );
          }

          if (/^https?:\/\//.test(segment)) {
            return (
              <a
                key={`url-${idx}-${segIdx}`}
                href={segment}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 underline decoration-blue-300 underline-offset-2 hover:text-blue-700"
              >
                {segment}
              </a>
            );
          }

          return <span key={`txt-${idx}-${segIdx}`}>{segment}</span>;
        })}
      </span>
    );
  });
}

function renderMessageContent(content: string): JSX.Element {
  const blocks = parseMessageBlocks(content);
  if (blocks.length === 0) {
    return <div className="whitespace-pre-wrap break-words [overflow-wrap:anywhere] text-[14.5px] leading-relaxed">{content}</div>;
  }

  return (
    <div className="space-y-3 text-[14.5px] leading-relaxed">
      {blocks.map((block, idx) => {
        if (block.type === 'paragraph') {
          const listLike = block.lines.every((line) => /^\s*([-*•]|\d+\.)\s+/.test(line));
          if (listLike) {
            return (
              <ul key={`list-${idx}`} className="list-disc pl-5 space-y-1">
                {block.lines.map((line, liIdx) => (
                  <li key={`li-${idx}-${liIdx}`} className="break-words [overflow-wrap:anywhere]">
                    {renderInlineFormatting(line.replace(/^\s*([-*•]|\d+\.)\s+/, ''))}
                  </li>
                ))}
              </ul>
            );
          }

          return (
            <div key={`p-${idx}`} className="whitespace-pre-wrap break-words [overflow-wrap:anywhere]">
              {block.lines.map((line, lineIdx) => (
                <div key={`pl-${idx}-${lineIdx}`}>{renderInlineFormatting(line)}</div>
              ))}
            </div>
          );
        }

        if (block.type === 'table') {
          const [header, ...rows] = block.rows;
          return (
            <div key={`tbl-${idx}`} className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    {header.map((cell, cellIdx) => (
                      <th key={`th-${idx}-${cellIdx}`} className="px-3 py-2 font-medium">
                        {cell}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, rowIdx) => (
                    <tr key={`tr-${idx}-${rowIdx}`} className="border-t border-gray-100">
                      {row.map((cell, cellIdx) => (
                        <td key={`td-${idx}-${rowIdx}-${cellIdx}`} className="px-3 py-2 align-top text-gray-700 whitespace-pre-wrap">
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );
        }

        return (
          <figure key={`img-${idx}`} className="rounded-lg border border-gray-200 bg-gray-50/60 p-2">
            <Image
              src={block.src}
              alt={block.alt}
              width={800}
              height={600}
              className="w-full h-auto rounded-md object-contain"
              loading="lazy"
            />
            {block.alt && (
              <figcaption className="mt-2 text-xs text-gray-500">{block.alt}</figcaption>
            )}
          </figure>
        );
      })}
    </div>
  );
}

// ============================================================================
// COMPONENT
// ============================================================================
export default function CuriosityOceanChat() {
  const { userId } = useAuth();
  const { user: authUser } = useUser();
  const user = {
    firstName: authUser?.firstName ?? null,
    username: authUser?.emailAddresses?.[0]?.emailAddress?.split('@')[0] ?? null,
  };
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [useStreaming, setUseStreaming] = useState(true);
  const [curiosityLevel, setCuriosityLevel] = useState<'curious' | 'wild' | 'chaos' | 'genius'>('curious');
  const [language, setLanguage] = useState('auto');
  const [isRecording, setIsRecording] = useState(false);
  const [showCamera, setShowCamera] = useState(false);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('user');
  const [showAttachMenu, setShowAttachMenu] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const [readTypingEnabled, setReadTypingEnabled] = useState(false);
  const [exportingFormat, setExportingFormat] = useState<'pdf' | 'docx' | null>(null);
  const [memoryHydrated, setMemoryHydrated] = useState(false);
  const [savedReferenceCode, setSavedReferenceCode] = useState<string | null>(null);
  const [nanoGridPreset, setNanoGridPreset] = useState<{
    mode: string;
    vision: string;
    grid: string;
    profile: 'balanced' | 'clinical' | 'athlete';
    intensity: number;
    precision: number;
  } | null>(null);
  const [fabricSignals, setFabricSignals] = useState<RuntimeSignalCard[]>([
    { label: 'Alphabet', emoji: '🔤', state: 'live', detail: 'multilingual support ready' },
    { label: 'NanoGrid', emoji: '🛰️', state: 'offline', detail: 'smart assistance standing by' },
    { label: 'Kloud Bridge', emoji: '☁️', state: 'offline', detail: 'secure connection check in progress' },
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordingStreamRef = useRef<MediaStream | null>(null);
  const attachMenuRef = useRef<HTMLDivElement>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const audioUrlRef = useRef<string | null>(null);
  const typingSpeechDebounceRef = useRef<number | null>(null);
  const typingLastSpokenRef = useRef('');
  const preEnterWarmDebounceRef = useRef<number | null>(null);
  const lastWarmSignatureRef = useRef('');

  const uiLanguage = (() => {
    const normalized = normalizeLangCode(language);
    if (normalized && normalized !== 'auto' && translations[normalized]) return normalized;
    return detectLanguage();
  })();

  const t = translations[uiLanguage] || translations.en;
  const suggestedQuestions = SUGGESTED_QUESTIONS[uiLanguage] || SUGGESTED_QUESTIONS.en;

  const refreshFabricSignals = useCallback(async () => {
    try {
      const [nanoRes, kloudRes] = await Promise.all([
        fetch('/api/ocean/nanogrid/status', { cache: 'no-store' }).catch(() => null),
        fetch('/api/kloud-bridge/status', { cache: 'no-store' }).catch(() => null),
      ]);

      const nanoData = nanoRes && nanoRes.ok ? await nanoRes.json() : null;
      const kloudData = kloudRes && kloudRes.ok ? await kloudRes.json() : null;

      const nanoLive = Boolean(nanoData?.available);
      const kloudReachable = Boolean(kloudData?.upstream?.reachable);
      const kloudConfigured = Boolean(kloudData?.upstream?.configured);
      setFabricSignals([
        { label: 'Alphabet', emoji: '🔤', state: 'live', detail: 'multilingual support active' },
        {
          label: 'NanoGrid',
          emoji: '🛰️',
          state: nanoLive ? 'live' : 'offline',
          detail: nanoLive ? 'visual assistance ready' : 'visual assistance standing by',
        },
        {
          label: 'Kloud Bridge',
          emoji: '☁️',
          state: kloudReachable ? 'live' : kloudConfigured ? 'limited' : 'offline',
          detail: kloudReachable
            ? 'secure connection ready'
            : kloudConfigured
              ? 'secure connection syncing'
              : 'service unavailable',
        },
      ]);
    } catch {
      setFabricSignals((current) => current);
    }
  }, []);

  const getConversationLanguage = useCallback(() => {
    const normalized = normalizeLangCode(language);
    return normalized === 'auto' ? undefined : normalized;
  }, [language]);

  const withOptionalLanguage = useCallback((payload: Record<string, unknown>) => {
    const elasticDefaults = {
      long_response: true,
      max_tokens: -1,
      use_mega_layers: true,
      use_knowledge_seeds: true,
      strict_mode: false,
    };

    const presetPayload = nanoGridPreset
      ? {
        mode: nanoGridPreset.mode,
        vision: nanoGridPreset.vision,
        grid: nanoGridPreset.grid,
        profile: nanoGridPreset.profile,
        intensity: nanoGridPreset.intensity,
        precision: nanoGridPreset.precision,
      }
      : {};

    const hasPromptText =
      typeof payload.message === 'string' ||
      typeof payload.question === 'string' ||
      typeof payload.query === 'string' ||
      typeof payload.text === 'string';

    const conversationLanguage = getConversationLanguage();
    const languagePayload = conversationLanguage ? { language: conversationLanguage } : {};

    if (hasPromptText) {
      return {
        ...payload,
        ...elasticDefaults,
        ...presetPayload,
        ...languagePayload,
      };
    }

    return { ...payload, ...elasticDefaults, ...presetPayload, ...languagePayload };
  }, [getConversationLanguage, nanoGridPreset]);

  const buildSystemMessage = useCallback((content: string): Message => ({
    id: `system-${Date.now()}`,
    type: 'ai',
    content,
    timestamp: new Date(),
  }), []);

  const getAuthHeaders = useCallback(() => {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (userId) headers['X-User-ID'] = userId;
    return headers;
  }, [userId]);

  const parseFilename = useCallback((disposition: string | null, fallback: string): string => {
    if (!disposition) return fallback;

    const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (utf8Match?.[1]) {
      try {
        return decodeURIComponent(utf8Match[1]);
      } catch {
      }
    }

    const plainMatch = disposition.match(/filename="?([^";]+)"?/i);
    return plainMatch?.[1] || fallback;
  }, []);

  const localMemoryKey = useCallback(() => {
    const nodeId = userId || 'guest';
    return `${OCEAN_LOCAL_MEMORY_KEY_PREFIX}:${nodeId}`;
  }, [userId]);

  const buildConversationHistory = useCallback((sourceMessages: Message[]) => {
    return sourceMessages
      .filter((item) => item.id !== 'welcome' && typeof item.content === 'string' && item.content.trim())
      .slice(-20)
      .map((item): { role: 'user' | 'assistant'; content: string } => ({
        role: item.type === 'user' ? 'user' : 'assistant',
        content: item.content,
      }));
  }, []);

  const scrollToBottom = useCallback((instant = false) => {
    messagesEndRef.current?.scrollIntoView({ behavior: instant ? 'instant' : 'smooth' });
  }, []);

  // Scroll on new messages (smooth), but NOT on every streaming chunk
  const prevMsgCountRef = useRef(0);
  useEffect(() => {
    if (messages.length !== prevMsgCountRef.current) {
      prevMsgCountRef.current = messages.length;
      scrollToBottom();
    }
  }, [messages, scrollToBottom]);
  useEffect(() => {
    refreshFabricSignals();
    const interval = window.setInterval(() => {
      refreshFabricSignals();
    }, 20000);

    return () => window.clearInterval(interval);
  }, [refreshFabricSignals]);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const params = new URLSearchParams(window.location.search);
    const topicFromUrl = (params.get('topic') || '').trim();
    const langFromUrl = normalizeLangCode(params.get('lang'));
    const modeFromUrl = (params.get('mode') || '').trim().toLowerCase();
    const visionFromUrl = (params.get('vision') || '').trim().toLowerCase();
    const gridFromUrl = (params.get('grid') || '').trim().toLowerCase();
    const profileFromUrl = (params.get('profile') || '').trim().toLowerCase();
    const profile = profileFromUrl === 'clinical' || profileFromUrl === 'athlete' ? profileFromUrl : 'balanced';
    const intensity = toBoundedInt(params.get('intensity'), 92, 60, 100);
    const precision = toBoundedInt(params.get('precision'), 97, 70, 100);

    if (langFromUrl) {
      setLanguage(langFromUrl);
    }
    if (topicFromUrl) {
      setInputValue(topicFromUrl);
    }

    if (modeFromUrl || visionFromUrl || gridFromUrl) {
      setNanoGridPreset({
        mode: modeFromUrl || 'limit',
        vision: visionFromUrl || 'zeiss_ultra',
        grid: gridFromUrl || 'nanogrid_plus',
        profile,
        intensity,
        precision,
      });
    }
  }, []);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const raw = localStorage.getItem(localMemoryKey());
      if (!raw) {
        setMemoryHydrated(true);
        return;
      }

      const parsed = JSON.parse(raw) as Record<string, unknown>;
      const restoredMessages = deserializeMessagesFromLocal(parsed.messages);
      if (restoredMessages.length > 0) {
        setMessages(restoredMessages);
      }

      const restoredLanguage = normalizeLangCode(typeof parsed.language === 'string' ? parsed.language : 'auto');
      if (restoredLanguage) setLanguage(restoredLanguage);

      const restoredStreaming = typeof parsed.useStreaming === 'boolean' ? parsed.useStreaming : undefined;
      if (typeof restoredStreaming === 'boolean') setUseStreaming(restoredStreaming);

      const restoredCuriosity = typeof parsed.curiosityLevel === 'string' ? parsed.curiosityLevel : '';
      if (restoredCuriosity === 'curious' || restoredCuriosity === 'wild' || restoredCuriosity === 'chaos' || restoredCuriosity === 'genius') {
        setCuriosityLevel(restoredCuriosity);
      }

      if (typeof parsed.readTypingEnabled === 'boolean') {
        setReadTypingEnabled(parsed.readTypingEnabled);
      }
    } catch {
      // ignore corrupted local memory
    } finally {
      setMemoryHydrated(true);
    }
  }, [localMemoryKey]);

  useEffect(() => {
    if (typeof window === 'undefined' || !memoryHydrated) return;
    try {
      const payload = {
        language,
        useStreaming,
        curiosityLevel,
        readTypingEnabled,
        messages: serializeMessagesForLocal(messages),
        updatedAt: new Date().toISOString(),
      };
      localStorage.setItem(localMemoryKey(), JSON.stringify(payload));
    } catch {
      // ignore storage quota/availability errors
    }
  }, [messages, language, useStreaming, curiosityLevel, readTypingEnabled, memoryHydrated, localMemoryKey]);

  useEffect(() => {
    if (!useStreaming) setUseStreaming(true);
  }, [useStreaming]);

  // Close attach menu on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (attachMenuRef.current && !attachMenuRef.current.contains(e.target as Node)) {
        setShowAttachMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        inputRef.current?.focus();
        return;
      }

      if (event.key === 'Escape') {
        setShowCamera(false);
        setShowSettings(false);
        setShowAttachMenu(false);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  useEffect(() => {
    setMessages((prev) => {
      if (prev.length > 0) return prev;
      return [buildSystemMessage(t.welcome)];
    });
  }, [t.welcome, buildSystemMessage]);

  // Auto-resize textarea
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + 'px';
    }
  }, [inputValue]);

  useEffect(() => {
    if (!readTypingEnabled || typeof window === 'undefined' || !window.speechSynthesis) {
      if (typingSpeechDebounceRef.current) {
        window.clearTimeout(typingSpeechDebounceRef.current);
        typingSpeechDebounceRef.current = null;
      }
      window.speechSynthesis?.cancel();
      return;
    }

    const text = inputValue.trim();
    if (!text || text.length < 2 || text === typingLastSpokenRef.current) {
      return;
    }

    if (typingSpeechDebounceRef.current) {
      window.clearTimeout(typingSpeechDebounceRef.current);
    }

    typingSpeechDebounceRef.current = window.setTimeout(() => {
      if (!window.speechSynthesis || !readTypingEnabled) return;

      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      const ttsLanguage = getConversationLanguage() || uiLanguage;
      utterance.lang = ttsLanguage === 'sq' ? 'sq-AL' : ttsLanguage;
      utterance.rate = 1;
      utterance.pitch = 1;

      typingLastSpokenRef.current = text;
      window.speechSynthesis.speak(utterance);
    }, 500);

    return () => {
      if (typingSpeechDebounceRef.current) {
        window.clearTimeout(typingSpeechDebounceRef.current);
        typingSpeechDebounceRef.current = null;
      }
    };
  }, [inputValue, readTypingEnabled, getConversationLanguage, uiLanguage]);

  useEffect(() => {
    return () => {
      if (preEnterWarmDebounceRef.current) {
        window.clearTimeout(preEnterWarmDebounceRef.current);
        preEnterWarmDebounceRef.current = null;
      }
    };
  }, []);

  const handleInputChange = useCallback((value: string) => {
    setInputValue(value);
    const normalized = value.trim();
    if (!normalized) {
      typingLastSpokenRef.current = '';
      lastWarmSignatureRef.current = '';
      if (preEnterWarmDebounceRef.current) {
        window.clearTimeout(preEnterWarmDebounceRef.current);
        preEnterWarmDebounceRef.current = null;
      }
      return;
    }

    if (normalized.length < 3) return;

    const klass = classifyPreEnterIntent(normalized);
    const signature = `${normalized}|${klass.bitMode}|${klass.processingMode}|${klass.tokenBudget}`;
    if (signature === lastWarmSignatureRef.current) return;

    if (preEnterWarmDebounceRef.current) {
      window.clearTimeout(preEnterWarmDebounceRef.current);
    }

    preEnterWarmDebounceRef.current = window.setTimeout(() => {
      lastWarmSignatureRef.current = signature;
      void fetch('/api/ocean/stream/warm', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(withOptionalLanguage({
          message: normalized,
          bit_mode: klass.bitMode,
          token_budget: klass.tokenBudget,
          processing_mode: klass.processingMode,
          curiosity_level: klass.curiosityHint,
          pre_enter: true,
          user_id: userId,
        })),
      }).catch(() => {
      });
    }, 220);
  }, [getAuthHeaders, userId, withOptionalLanguage]);

  // ============================================================================
  // 🎤 MICROPHONE - Voice Conversation Pipeline
  // ============================================================================
  const voiceMode = true; // true = full voice conversation

  const toggleRecording = async () => {
    setShowAttachMenu(false);
    if (isRecording) {
      mediaRecorderRef.current?.stop();
      setIsRecording(false);
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        recordingStreamRef.current = stream;
        const mediaRecorder = new MediaRecorder(stream);
        const chunks: BlobPart[] = [];

        mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
        mediaRecorder.onstop = async () => {
          const blob = new Blob(chunks, { type: 'audio/webm' });
          const reader = new FileReader();
          reader.onloadend = async () => {
            const base64 = (reader.result as string).split(',')[1];
            const userMsgId = `user-${Date.now()}`;
            setMessages(prev => [...prev, { id: userMsgId, type: 'user', content: '🎤 Voice message...', timestamp: new Date() }]);

            try {
              if (voiceMode) {
                // 🔊 FULL VOICE CONVERSATION: Audio → STT → LLM → TTS → Audio
                const res = await fetch('/api/ocean/voice', {
                  method: 'POST',
                  headers: getAuthHeaders(),
                  body: JSON.stringify(withOptionalLanguage({
                    audio_base64: base64,
                    curiosity_level: curiosityLevel,
                    user_id: userId
                  }))
                });

                if (res.ok) {
                  // Get metadata from headers
                  const transcript = res.headers.get('X-Transcript') || '';
                  const responseText = res.headers.get('X-Response-Text') || '';

                  // Update user message with transcript
                  setMessages(prev => prev.map(m =>
                    m.id === userMsgId ? { ...m, content: `🎤 "${transcript}"` } : m
                  ));

                  // Add AI response
                  const aiMsgId = `ai-${Date.now()}`;
                  setMessages(prev => [...prev, {
                    id: aiMsgId,
                    type: 'ai',
                    content: responseText || 'Voice response received',
                    timestamp: new Date()
                  }]);

                  // 🔊 Play audio response automatically
                  const audioBlob = await res.blob();
                  const audioUrl = URL.createObjectURL(audioBlob);
                  const audio = new Audio(audioUrl);
                  audioRef.current = audio;
                  setSpeakingMessageId(aiMsgId);

                  audio.onended = () => {
                    setSpeakingMessageId(null);
                    URL.revokeObjectURL(audioUrl);
                    audioRef.current = null;
                  };

                  await audio.play();
                } else {
                  const payload = await readJsonOrTextResponse(res);
                  throw new Error(getPayloadMessage(payload, 'Voice conversation failed'));
                }
              } else {
                // 📝 TEXT ONLY: Audio → STT → Text response
                const res = await fetch('/api/ocean/audio', {
                  method: 'POST',
                  headers: getAuthHeaders(),
                  body: JSON.stringify(withOptionalLanguage({ audio_base64: base64, user_id: userId }))
                });
                const payload = await readJsonOrTextResponse(res);

                if (!res.ok) {
                  throw new Error(getPayloadMessage(payload, 'Audio transcription failed'));
                }

                const transcript =
                  (typeof payload.data?.transcript === 'string' && payload.data.transcript.trim()) ||
                  payload.text;

                // Update user message with transcript
                setMessages(prev => prev.map(m =>
                  m.id === userMsgId ? { ...m, content: `🎤 "${transcript || 'Audio'}"` } : m
                ));

                // Send transcript to chat
                if (transcript) {
                  await sendMessage(transcript);
                }
              }
            } catch (error) {
              const message = error instanceof Error ? error.message : 'Error processing voice message';
              setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: `❌ ${message}`, timestamp: new Date() }]);
            }
          };
          reader.readAsDataURL(blob);
          stream.getTracks().forEach(track => track.stop());
          if (recordingStreamRef.current === stream) {
            recordingStreamRef.current = null;
          }
        };

        mediaRecorderRef.current = mediaRecorder;
        mediaRecorder.start();
        setIsRecording(true);
      } catch {
        // Microphone access denied
      }
    }
  };

  // ============================================================================
  // 📷 CAMERA
  // ============================================================================
  const stopCameraStream = useCallback(() => {
    const video = videoRef.current;
    if (video?.srcObject) {
      (video.srcObject as MediaStream).getTracks().forEach((track) => track.stop());
      video.srcObject = null;
    }
  }, []);

  const startCameraStream = useCallback(async (mode: 'user' | 'environment') => {
    try {
      if (!navigator?.mediaDevices?.getUserMedia) {
        throw new Error('Camera API unavailable');
      }

      stopCameraStream();

      const supported = navigator.mediaDevices.getSupportedConstraints?.() || {} as MediaTrackSupportedConstraints;
      const qualityLadder = [
        { width: 7680, height: 4320 }, // 8K UHD
        { width: 6144, height: 3456 }, // 6K
        { width: 3840, height: 2160 }, // 4K UHD
        { width: 2560, height: 1440 }, // QHD
        { width: 1920, height: 1080 }, // Full HD fallback
      ];

      let stream: MediaStream | null = null;
      for (const preset of qualityLadder) {
        try {
          const videoConstraints: MediaTrackConstraintSet = {
            facingMode: { ideal: mode },
            width: supported.width ? { ideal: preset.width } : undefined,
            height: supported.height ? { ideal: preset.height } : undefined,
            frameRate: supported.frameRate ? { ideal: 30, max: 60 } : undefined,
            aspectRatio: supported.aspectRatio ? { ideal: 16 / 9 } : undefined,
          };

          if ((supported as Record<string, boolean>).resizeMode) {
            (videoConstraints as Record<string, unknown>).resizeMode = 'crop-and-scale';
          }

          stream = await navigator.mediaDevices.getUserMedia({
            video: videoConstraints,
            audio: false,
          });
          break;
        } catch {
          stream = null;
        }
      }

      if (!stream) {
        throw new Error('Unable to acquire camera stream');
      }

      const video = videoRef.current;

      const track = stream.getVideoTracks()[0];
      if (track && track.applyConstraints) {
        const advanced: MediaTrackConstraintSet[] = [];
        const supportedRecord = supported as Record<string, boolean>;
        if (supportedRecord.focusMode) advanced.push({ focusMode: 'continuous' } as MediaTrackConstraintSet);
        if (supportedRecord.exposureMode) advanced.push({ exposureMode: 'continuous' } as MediaTrackConstraintSet);
        if (supportedRecord.whiteBalanceMode) advanced.push({ whiteBalanceMode: 'continuous' } as MediaTrackConstraintSet);
        if (supportedRecord.noiseSuppression) advanced.push({ noiseSuppression: true } as MediaTrackConstraintSet);
        if (advanced.length > 0) {
          try {
            await track.applyConstraints({ advanced });
          } catch {
          }
        }
      }

      if (video) {
        video.srcObject = stream;
        video.setAttribute('playsinline', 'true');
        video.setAttribute('autoplay', 'true');
        video.setAttribute('muted', 'true');
        try {
          await video.play();
        } catch {
        }
      }
    } catch {
      setShowCamera(false);
    }
  }, [stopCameraStream]);

  const toggleCamera = async () => {
    setShowAttachMenu(false);
    if (showCamera) {
      stopCameraStream();
      setShowCamera(false);
    } else {
      setShowCamera(true);
      setTimeout(() => startCameraStream(facingMode), 100);
    }
  };

  const switchCamera = async () => {
    const newMode = facingMode === 'user' ? 'environment' : 'user';
    setFacingMode(newMode);
    if (showCamera) await startCameraStream(newMode);
  };

  const capturePhoto = async () => {
    const video = videoRef.current;
    if (!video) return;

    const blobToBase64 = async (blob: Blob): Promise<string> => {
      return await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
          const value = typeof reader.result === 'string' ? reader.result : '';
          const encoded = value.includes(',') ? value.split(',')[1] : value;
          if (!encoded) reject(new Error('Empty image payload'));
          else resolve(encoded);
        };
        reader.onerror = () => reject(reader.error || new Error('Failed to read image'));
        reader.readAsDataURL(blob);
      });
    };

    let base64 = '';

    const stream = video.srcObject as MediaStream | null;
    const track = stream?.getVideoTracks?.()[0];
    type ImageCaptureLike = new (track: MediaStreamTrack) => { takePhoto: () => Promise<Blob> };
    const ImageCaptureCtor = typeof window !== 'undefined' && 'ImageCapture' in window
      ? (window as Window & { ImageCapture: ImageCaptureLike }).ImageCapture
      : null;

    if (track && typeof ImageCaptureCtor === 'function') {
      try {
        const imageCapture = new ImageCaptureCtor(track);
        const photoBlob: Blob = await imageCapture.takePhoto();
        base64 = await blobToBase64(photoBlob);
      } catch {
      }
    }

    if (!base64) {
      const canvas = document.createElement('canvas');
      const width = Math.max(video.videoWidth || 0, 1280);
      const height = Math.max(video.videoHeight || 0, 720);
      canvas.width = width;
      canvas.height = height;
      canvas.getContext('2d')?.drawImage(video, 0, 0, width, height);
      const webpData = canvas.toDataURL('image/webp', 0.95);
      const jpegData = canvas.toDataURL('image/jpeg', 0.95);
      const encoded = (webpData.includes(',') ? webpData.split(',')[1] : '') || (jpegData.includes(',') ? jpegData.split(',')[1] : '');
      base64 = encoded;
    }

    if (!base64) {
      setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: '❌ Unable to capture photo from camera', timestamp: new Date() }]);
      return;
    }

    setMessages(prev => [...prev, { id: `user-${Date.now()}`, type: 'user', content: '📷 Photo captured', timestamp: new Date() }]);

    try {
      const res = await fetch('/api/ocean/vision', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(withOptionalLanguage({
          image_base64: base64,
          prompt: uiLanguage === 'sq' ? 'Përshkruaj këtë foto në shqip' : 'Describe this photo',
          user_id: userId,
        }))
      });
      const payload = await readJsonOrTextResponse(res);

      if (!res.ok) {
        throw new Error(getPayloadMessage(payload, 'Error analyzing image'));
      }

      const analysis =
        (typeof payload.data?.analysis === 'string' && payload.data.analysis.trim()) ||
        (typeof payload.data?.text_extracted === 'string' && payload.data.text_extracted.trim()) ||
        (typeof payload.data?.response === 'string' && payload.data.response.trim()) ||
        payload.text;

      if (!analysis) {
        throw new Error('Vision service returned no analysis.');
      }

      setMessages(prev => [...prev, { id: `ai-${Date.now()}`, type: 'ai', content: analysis, timestamp: new Date() }]);
    } catch (error) {
      const message = error instanceof Error && error.message.trim()
        ? error.message.trim()
        : 'Error analyzing image';
      setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: `❌ ${message}`, timestamp: new Date() }]);
    }
    toggleCamera();
  };

  // ============================================================================
  // 📄 DOCUMENT
  // ============================================================================
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) return;
    setShowAttachMenu(false);

    const ext = (file.name.split('.').pop() || '').toLowerCase();

    setMessages(prev => [...prev, { id: `user-${Date.now()}`, type: 'user', content: `📄 ${file.name}`, timestamp: new Date() }]);

    const sendDocument = async (contentBase64: string) => {
      try {
        const res = await fetch('/api/ocean/document', {
          method: 'POST',
          headers: getAuthHeaders(),
          body: JSON.stringify({
            action: 'scan',
            filename: file.name,
            doc_type: ext,
            content_type: file.type || 'application/octet-stream',
            content_base64: contentBase64,
            max_chars: 8000,
            user_id: userId,
          })
        });
        const payload = await readJsonOrTextResponse(res);
        const data = payload.data;
        const analysisText =
          (typeof data?.extracted_text === 'string' && data.extracted_text.trim()) ||
          (typeof data?.analysis === 'string' && data.analysis.trim()) ||
          (typeof data?.summary === 'string' && data.summary.trim()) ||
          (typeof data?.response === 'string' && data.response.trim()) ||
          payload.text ||
          '';

        if (!res.ok || !analysisText) {
          const errorText = getPayloadMessage(payload, 'Document analysis failed.');
          setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: `❌ ${errorText}`, timestamp: new Date() }]);
          return;
        }

        const parser = typeof data?.parser === 'string' ? data.parser : 'unknown';
        const validation = typeof data?.validation_status === 'string' ? data.validation_status : 'unknown';
        const checksum = typeof data?.checksum_sha256 === 'string' ? `${data.checksum_sha256.slice(0, 12)}…` : 'n/a';
        const ingestionId = typeof data?.ingestion_id === 'string' ? data.ingestion_id : 'n/a';

        setMessages(prev => [...prev, {
          id: `ai-${Date.now()}`,
          type: 'ai',
          content: `${analysisText}\n\n✅ Document reviewed successfully and prepared for follow-up questions.`,
          timestamp: new Date(),
        }]);
      } catch (error) {
        const detail = error instanceof Error && error.message.trim()
          ? error.message.trim()
          : 'Document processing request failed.';
        setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: `❌ ${detail}`, timestamp: new Date() }]);
      }
    };

    const reader = new FileReader();
    reader.onloadend = async () => {
      const value = typeof reader.result === 'string' ? reader.result : '';
      const base64 = value.includes(',') ? value.split(',')[1] : value;
      await sendDocument(base64);
    };
    reader.readAsDataURL(file);

    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // ============================================================================
  // STREAMING
  // ============================================================================
  const sendStreamingMessage = async (
    messageText: string,
    conversationHistory: Array<{ role: 'user' | 'assistant'; content: string }>,
  ) => {
    const aiMessageId = `ai-${Date.now()}`;
    setMessages(prev => [...prev, { id: aiMessageId, type: 'ai', content: '', timestamp: new Date(), isStreaming: true }]);
    setIsStreaming(true);

    try {
      abortControllerRef.current = new AbortController();
      const response = await fetch('/api/ocean/stream', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(withOptionalLanguage({
          message: messageText,
          messages: conversationHistory,
          curiosity_level: curiosityLevel,
          curiosityLevel,
          user_id: userId,
          user_name: user?.firstName || user?.username,
        })),
        signal: abortControllerRef.current.signal,
      });
      if (!response.ok) {
        const payload = await readJsonOrTextResponse(response);
        const detail = getPayloadMessage(payload, '');
        const statusDetail = detail
          ? `Stream failed (${response.status}): ${detail}`
          : `Stream failed (${response.status})`;
        throw new Error(statusDetail);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';
      let pending = '';
      let lastScroll = 0;
      let callbackAccepted: { requestId?: string; callbackUrl?: string | null } | null = null;

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          pending += decoder.decode(value, { stream: true });
          const lines = pending.split('\n');
          pending = lines.pop() || '';

          for (const rawLine of lines) {
            const line = rawLine.replace(/\r$/, '');
            if (!line || !line.startsWith('data:')) continue;

            let payload = line.slice(5);
            if (payload.startsWith(' ')) payload = payload.slice(1);
            if (!payload || payload === '[DONE]') continue;

            try {
              const parsed = JSON.parse(payload);
              const parsedText = extractOceanChunkFromPayload(parsed);
              if (parsedText) {
                fullContent += parsedText;
              } else if (parsed?.status === 'accepted' && parsed?.mode === 'callback') {
                callbackAccepted = {
                  requestId: typeof parsed?.request_id === 'string' ? parsed.request_id : undefined,
                  callbackUrl:
                    typeof parsed?.callback_url === 'string'
                      ? parsed.callback_url
                      : parsed?.callback_url === null
                        ? null
                        : undefined,
                };
              } else if (typeof parsed?.error === 'string' && parsed.error.trim()) {
                // Terminal error from upstream — stop streaming and surface as error state
                throw new Error(parsed.error);
              }
            } catch (parseErr) {
              if ((parseErr as Error).message && !(parseErr instanceof SyntaxError)) throw parseErr;
              fullContent += extractOceanText(payload);
            }
          }

          const cleanContent = sanitizeOceanMessage(fullContent);
          setMessages(prev => prev.map(msg => msg.id === aiMessageId ? { ...msg, content: cleanContent } : msg));
          // Throttle scroll during streaming — max once per 80ms, instant (no smooth animation)
          const now = Date.now();
          if (now - lastScroll > 80) {
            lastScroll = now;
            scrollToBottom(true);
          }
        }

        const trailing = pending.replace(/\r$/, '');
        if (trailing.startsWith('data:')) {
          let payload = trailing.slice(5);
          if (payload.startsWith(' ')) payload = payload.slice(1);
          if (payload && payload !== '[DONE]') {
            try {
              const parsed = JSON.parse(payload);
              const parsedText = extractOceanChunkFromPayload(parsed);
              if (parsedText) {
                fullContent += parsedText;
              } else if (parsed?.status === 'accepted' && parsed?.mode === 'callback') {
                callbackAccepted = {
                  requestId: typeof parsed?.request_id === 'string' ? parsed.request_id : undefined,
                  callbackUrl:
                    typeof parsed?.callback_url === 'string'
                      ? parsed.callback_url
                      : parsed?.callback_url === null
                        ? null
                        : undefined,
                };
              } else if (typeof parsed?.error === 'string' && parsed.error.trim()) {
                throw new Error(parsed.error);
              }
            } catch (parseErr) {
              if ((parseErr as Error).message && !(parseErr instanceof SyntaxError)) throw parseErr;
              fullContent += extractOceanText(payload);
            }
            const cleanContent = sanitizeOceanMessage(fullContent);
            setMessages(prev => prev.map(msg => msg.id === aiMessageId ? { ...msg, content: cleanContent } : msg));
          }
        }

        // Final scroll after stream ends
        scrollToBottom(true);
      }
      if (!fullContent.trim() && callbackAccepted) {
        const callbackMsg = callbackAccepted.callbackUrl
          ? callbackAccepted.requestId
            ? `⚠️ Procesim asinkron aktiv (request_id: ${callbackAccepted.requestId}). Rezultati final do të dërgohet te callback_url i konfiguruar: ${callbackAccepted.callbackUrl}`
            : `⚠️ Procesim asinkron aktiv. Rezultati final do të dërgohet te callback_url i konfiguruar: ${callbackAccepted.callbackUrl}`
          : '❌ Serveri ktheu accepted/callback pa callback_url. Nuk ka kanal real për rezultatin final. Konfiguro callback_url ose përdor modalitet sinkron.';
        setMessages(prev => prev.map(msg => msg.id === aiMessageId ? {
          ...msg,
          content: callbackMsg,
          isStreaming: false,
        } : msg));
      } else if (!fullContent.trim()) {
        setMessages(prev => prev.map(msg => msg.id === aiMessageId ? {
          ...msg,
          content: '❌ Ocean nuk u përgjigj. Provo përsëri.',
          isStreaming: false,
        } : msg));
      } else {
        setMessages(prev => prev.map(msg => msg.id === aiMessageId ? { ...msg, isStreaming: false } : msg));
      }
    } catch (error) {
      if ((error as Error).name !== 'AbortError') {
        const errorMessage = error instanceof Error && error.message
          ? error.message
          : 'Streaming request failed.';
        setMessages(prev => prev.map(msg => msg.id === aiMessageId ? {
          ...msg,
          content: `Error: ${errorMessage}`,
          isStreaming: false,
        } : msg));
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  };

  // ============================================================================
  // REGULAR MESSAGE
  // ============================================================================
  const sendRegularMessage = async (
    messageText: string,
    conversationHistory: Array<{ role: 'user' | 'assistant'; content: string }>,
  ) => {
    try {
      const res = await fetch('/api/ocean', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(withOptionalLanguage({
          question: messageText,
          curiosity_level: curiosityLevel,
          curiosityLevel,
          messages: conversationHistory,
          user_id: userId,
          user_name: user?.firstName || user?.username,
        })),
      });
      if (res.ok) {
        const payload = await readJsonOrTextResponse(res);
        const data = payload.data;
        const cleanResponse = sanitizeOceanMessage(
          (typeof data?.response === 'string' && data.response) ||
          (typeof data?.ocean_response === 'string' && data.ocean_response) ||
          (typeof data?.persona_answer === 'string' && data.persona_answer) ||
          payload.text ||
          ''
        );
        setMessages(prev => [...prev, {
          id: `ai-${Date.now()}`, type: 'ai',
          content: cleanResponse || 'Ocean-Core returned an empty response.',
          timestamp: new Date(),
        }]);
      } else {
        let errorText = `Ocean-Core request failed (${res.status}).`;
        const payload = await readJsonOrTextResponse(res);
        const detail = getPayloadMessage(payload, '');
        if (detail) {
          errorText = `${errorText} ${detail}`;
        }
        setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: errorText, timestamp: new Date() }]);
      }
    } catch {
      setMessages(prev => [...prev, { id: `error-${Date.now()}`, type: 'ai', content: 'Ocean-Core request failed.', timestamp: new Date() }]);
    }
  };

  // ============================================================================
  // SEND / CONTROLS
  // ============================================================================
  const sendMessage = async (question?: string) => {
    const messageText = question || inputValue.trim();
    if (!messageText || isLoading || isStreaming) return;
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: messageText,
      timestamp: new Date(),
    };
    const nextMessages = [...messages, userMessage];
    const conversationHistory = buildConversationHistory(nextMessages);

    setMessages(nextMessages);
    setInputValue('');
    typingLastSpokenRef.current = '';
    window.speechSynthesis?.cancel();
    setIsLoading(true);
    try {
      await sendStreamingMessage(messageText, conversationHistory);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const stopStreaming = () => { abortControllerRef.current?.abort(); };

  const activateNanoGridModule = useCallback(() => {
    setNanoGridPreset({
      mode: 'limit',
      vision: 'zeiss_ultra',
      grid: 'nanogrid_plus',
      profile: 'balanced',
      intensity: 92,
      precision: 97,
    });
    setInputValue((current) => current || 'Analyze this with NanoGrid support and ZEISS Ultra precision');
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  const clearChat = () => {
    setMessages([buildSystemMessage(t.chatCleared)]);
    setShowSettings(false);
    setSavedReferenceCode(null);
  };

  const exportConversation = useCallback(async (format: 'pdf' | 'docx') => {
    if (exportingFormat || messages.length < 2) return;
    setExportingFormat(format);

    try {
      const res = await fetch(`/api/ocean/curiosity/export?format=${format}`, {
        method: 'GET',
        headers: {
          ...getAuthHeaders(),
          'Cache-Control': 'no-store',
        },
      });

      if (!res.ok) {
        const payload = await readJsonOrTextResponse(res);
        throw new Error(getPayloadMessage(payload, `${format.toUpperCase()} export failed.`));
      }

      const blob = await res.blob();
      const fallback = `curiosity-ocean-export.${format}`;
      const filename = parseFilename(res.headers.get('content-disposition'), fallback);
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);

      setMessages((prev) => [...prev, {
        id: `ai-${Date.now()}`,
        type: 'ai',
        content: `Export ready: ${filename}`,
        timestamp: new Date(),
      }]);
    } catch (error) {
      const detail = error instanceof Error && error.message.trim()
        ? error.message.trim()
        : `${format.toUpperCase()} export failed.`;
      setMessages((prev) => [...prev, {
        id: `error-${Date.now()}`,
        type: 'ai',
        content: `❌ ${detail}`,
        timestamp: new Date(),
      }]);
    } finally {
      setExportingFormat(null);
    }
  }, [exportingFormat, messages.length, getAuthHeaders, parseFilename]);

  const saveLocalMemoryReference = useCallback(() => {
    if (typeof window === 'undefined') return;

    const reference = `OCEAN-${Date.now()}-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
    const snapshot = {
      reference,
      owner: localMemoryKey(),
      language,
      useStreaming,
      curiosityLevel,
      readTypingEnabled,
      messages: serializeMessagesForLocal(messages),
      createdAt: new Date().toISOString(),
    };

    try {
      localStorage.setItem(`${OCEAN_LOCAL_REFERENCE_KEY_PREFIX}:${reference}`, JSON.stringify(snapshot));
      setSavedReferenceCode(reference);
      if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        navigator.clipboard.writeText(reference).catch(() => {
          // ignore clipboard errors
        });
      }
    } catch {
      // ignore storage quota/availability errors
    }
  }, [curiosityLevel, language, localMemoryKey, messages, readTypingEnabled, useStreaming]);

  const getDebateSeedTopic = useCallback(() => {
    const fromInput = inputValue.trim();
    if (fromInput) return fromInput;

    const lastUser = [...messages]
      .reverse()
      .find((message) => message.type === 'user' && typeof message.content === 'string' && message.content.trim().length > 0);

    return lastUser?.content?.trim() || '';
  }, [inputValue, messages]);

  const openTrinityDebate = useCallback(() => {
    const seed = getDebateSeedTopic();
    const params = new URLSearchParams();
    if (seed) {
      params.set('topic', seed);
      params.set('autostart', '1');
      if (isAlgebraBinaryTopic(seed)) {
        params.set('mode', 'algebra-binary');
        params.set('binary', '1');
      }
    }
    const handoffLang = normalizeLangCode(language);
    if (handoffLang && handoffLang !== 'en') {
      params.set('lang', handoffLang);
    }
    params.set('from', 'ocean');
    params.set('return_to', '/modules/curiosity-ocean');

    const query = params.toString();
    const url = query ? `/debate?${query}` : '/debate';
    window.location.href = url;
  }, [getDebateSeedTopic, language]);

  const getTrinityDebateHref = useCallback(() => {
    const seed = getDebateSeedTopic();
    const params = new URLSearchParams();
    if (seed) {
      params.set('topic', seed);
      params.set('autostart', '1');
      if (isAlgebraBinaryTopic(seed)) {
        params.set('mode', 'algebra-binary');
        params.set('binary', '1');
      }
    }
    const handoffLang = normalizeLangCode(language);
    if (handoffLang && handoffLang !== 'en') {
      params.set('lang', handoffLang);
    }
    params.set('from', 'ocean');
    params.set('return_to', '/modules/curiosity-ocean');

    return `/debate?${params.toString()}`;
  }, [getDebateSeedTopic, language]);

  // ============================================================================
  // 🔊 TEXT-TO-SPEECH (Server-Side Neural Voice)
  // ============================================================================

  const speakMessage = async (messageId: string, text: string) => {
    // If already speaking this message, stop it
    if (speakingMessageId === messageId) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
        audioUrlRef.current = null;
      }
      window.speechSynthesis?.cancel();
      setSpeakingMessageId(null);
      return;
    }

    // Stop any ongoing speech
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (audioUrlRef.current) {
      URL.revokeObjectURL(audioUrlRef.current);
      audioUrlRef.current = null;
    }
    window.speechSynthesis?.cancel();

    setSpeakingMessageId(messageId);

    try {
      // Try server-side TTS first (higher quality neural voices)
      const response = await fetch('/api/ocean/tts', {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(withOptionalLanguage({ text }))
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        audioUrlRef.current = audioUrl;
        const audio = new Audio(audioUrl);
        audioRef.current = audio;

        audio.onended = () => {
          setSpeakingMessageId(null);
          URL.revokeObjectURL(audioUrl);
          if (audioUrlRef.current === audioUrl) {
            audioUrlRef.current = null;
          }
          audioRef.current = null;
        };
        audio.onerror = () => {
          setSpeakingMessageId(null);
          URL.revokeObjectURL(audioUrl);
          if (audioUrlRef.current === audioUrl) {
            audioUrlRef.current = null;
          }
          audioRef.current = null;
          // Fallback to browser TTS
          fallbackBrowserTTS(text);
        };

        await audio.play();
        return;
      }
    } catch {
      // Server TTS failed, fallback to browser
    }

    // Fallback: Browser Speech Synthesis
    fallbackBrowserTTS(text);
  };

  const fallbackBrowserTTS = (text: string) => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      setSpeakingMessageId(null);
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    const ttsLanguage = getConversationLanguage() || uiLanguage;
    utterance.lang = ttsLanguage === 'sq' ? 'sq-AL' : ttsLanguage;
    utterance.rate = 0.95;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v =>
      v.name.includes('Google') || v.name.includes('Microsoft') || v.name.includes('Natural')
    ) || voices.find(v => v.lang.toLowerCase().startsWith(ttsLanguage.toLowerCase())) || voices[0];

    if (preferredVoice) utterance.voice = preferredVoice;

    utterance.onend = () => setSpeakingMessageId(null);
    utterance.onerror = () => setSpeakingMessageId(null);

    window.speechSynthesis.speak(utterance);
  };

  // Load voices (they load async)
  useEffect(() => {
    if (typeof window !== 'undefined' && window.speechSynthesis) {
      window.speechSynthesis.getVoices();
    }
  }, []);

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
      stopCameraStream();

      try {
        if (mediaRecorderRef.current?.state !== 'inactive') {
          mediaRecorderRef.current?.stop();
        }
      } catch {
      }

      recordingStreamRef.current?.getTracks().forEach(track => track.stop());
      recordingStreamRef.current = null;

      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = '';
        audioRef.current = null;
      }

      if (audioUrlRef.current) {
        URL.revokeObjectURL(audioUrlRef.current);
        audioUrlRef.current = null;
      }

      if (typingSpeechDebounceRef.current) {
        window.clearTimeout(typingSpeechDebounceRef.current);
        typingSpeechDebounceRef.current = null;
      }

      window.speechSynthesis?.cancel();
    };
  }, [stopCameraStream]);

  // ============================================================================
  // RENDER
  // ============================================================================
  return (
    <div className="h-screen flex flex-col bg-gradient-to-b from-slate-100 to-slate-200">

      {/* ── Minimal Header ── */}
      <header className="flex-shrink-0 flex items-center justify-between px-4 sm:px-6 h-14 border-b border-slate-300/70 bg-slate-100/85 backdrop-blur-xl z-10">
        <div className="flex items-center gap-3">
          <Link href="/modules" className="p-1.5 -ml-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-sm shadow-emerald-500/20">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <div className="leading-tight hidden sm:block">
              <h1 className="text-sm font-semibold text-gray-900">{t.title}</h1>
              <p className="text-[11px] text-gray-400 font-normal">{t.subtitle}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {nanoGridPreset && (
            <div className="hidden lg:flex items-center rounded-lg border border-cyan-300 bg-cyan-50 px-2.5 py-1 text-[11px] font-semibold text-cyan-700">
              Enhanced visual mode active
            </div>
          )}

          <div className="hidden md:flex items-center rounded-xl border border-slate-300 bg-slate-100/90 p-1">
            <Link
              href="/modules/curiosity-ocean"
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 text-white"
            >
              Ask Ocean
            </Link>
            <Link
              href={getTrinityDebateHref()}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-indigo-700 hover:bg-indigo-100 transition-colors"
            >
              Trinity Debate
            </Link>
          </div>

          <button
            onClick={openTrinityDebate}
            className="hidden sm:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 transition-colors"
            title="Open deep analysis"
          >
            <span>🎭</span>
            <span>Deep Analysis</span>
          </button>

          {/* Language mode */}
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            className="appearance-none bg-transparent border-none text-sm cursor-pointer focus:outline-none px-1"
            title="Language"
          >
            <option value="auto">🌐 Auto</option>
            <option value="en">🇬🇧 English</option>
            <option value="sq">🇦🇱 Shqip</option>
            <option value="de">🇩🇪 Deutsch</option>
            <option value="es">🇪🇸 Español</option>
            <option value="fr">🇫🇷 Français</option>
            <option value="it">🇮🇹 Italiano</option>
            <option value="zh">🇨🇳 中文</option>
            <option value="ja">🇯🇵 日本語</option>
            <option value="ko">🇰🇷 한국어</option>
          </select>

          {/* Settings gear */}
          <div className="relative">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`p-2 rounded-lg transition-colors ${showSettings ? 'bg-gray-100 text-gray-700' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'}`}
            >
              <Settings2 className="w-[18px] h-[18px]" />
            </button>

            {/* Settings dropdown */}
            {showSettings && (
              <div className="absolute right-0 top-full mt-2 w-60 bg-white rounded-2xl shadow-2xl shadow-gray-200/60 border border-gray-100 p-4 z-50 space-y-4">
                {/* Streaming */}
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-gray-600">Streaming</span>
                  <button
                    type="button"
                    disabled
                    title="Streaming is always enabled for lower latency"
                    className="relative w-11 h-6 rounded-full transition-colors bg-emerald-500 cursor-not-allowed opacity-80"
                  >
                    <div className="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm transition-all left-6" />
                  </button>
                </div>

                <div className="h-px bg-gray-100" />

                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-gray-600">Read while typing</span>
                  <button
                    onClick={() => setReadTypingEnabled(!readTypingEnabled)}
                    className={`relative w-11 h-6 rounded-full transition-colors ${readTypingEnabled ? 'bg-emerald-500' : 'bg-gray-200'}`}
                  >
                    <div className={`absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm transition-all ${readTypingEnabled ? 'left-6' : 'left-1'}`} />
                  </button>
                </div>

                <div className="h-px bg-gray-100" />

                {/* Curiosity level */}
                <div>
                  <span className="text-xs font-medium text-gray-600 block mb-2">Curiosity Level</span>
                  <div className="grid grid-cols-2 gap-1.5">
                    {(['curious', 'wild', 'chaos', 'genius'] as const).map(level => (
                      <button
                        key={level}
                        onClick={() => setCuriosityLevel(level)}
                        className={`text-xs px-3 py-2 rounded-xl transition-all capitalize ${curiosityLevel === level
                            ? 'bg-emerald-50 text-emerald-700 font-semibold ring-1 ring-emerald-200'
                            : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
                          }`}
                      >
                        {t[level]}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="h-px bg-gray-100" />

                {/* Clear */}
                <button
                  onClick={clearChat}
                  className="w-full text-xs text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-xl py-2 transition-colors flex items-center justify-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Clear conversation
                </button>

                <button
                  onClick={saveLocalMemoryReference}
                  className="w-full text-xs text-gray-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-xl py-2 transition-colors"
                >
                  Save note
                </button>

                {savedReferenceCode && (
                  <div className="text-[11px] text-gray-500 bg-gray-50 border border-gray-100 rounded-xl px-2.5 py-2 leading-relaxed">
                    <div className="font-medium text-gray-600">Saved note:</div>
                    <div className="font-mono text-gray-700 break-all">{savedReferenceCode}</div>
                    <div className="mt-1">Keep this for later.</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      <section className="flex-shrink-0 border-b border-slate-200/70 bg-white/70">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-3 grid grid-cols-1 sm:grid-cols-3 gap-2">
          {fabricSignals.map((signal) => (
            <div
              key={signal.label}
              className={`rounded-2xl border px-3 py-2 shadow-sm ${getRuntimeCardClasses(signal.state)}`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-semibold">{signal.emoji} {signal.label}</span>
                <span className="text-[10px] uppercase tracking-[0.18em]">{signal.state}</span>
              </div>
              <p className="mt-1 text-[11px] opacity-90">{signal.detail}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Messages ── */}
      <main className="flex-1 overflow-y-auto" onClick={() => { setShowSettings(false); setShowAttachMenu(false); }}>
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-6 space-y-5">
          {messages.map((message) => {
            const renderedContent = message.type === 'ai'
              ? sanitizeOceanMessage(message.content)
              : message.content;

            return (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[88%] sm:max-w-[80%]`}>
                  {/* AI label */}
                  {message.type === 'ai' && (
                    <div className="flex items-center gap-1.5 mb-1.5 ml-0.5">
                      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center shadow-sm">
                        <Bot className="w-4 h-4 text-white" />
                      </div>
                      <span className="text-[11px] font-medium text-gray-500 emoji-inline-fallback"><span className="emoji-safe" aria-hidden="true">🌊</span> Ocean</span>
                      {message.isStreaming && (
                        <span className="text-[10px] text-emerald-500 animate-pulse ml-1">● {t.streamingIndicator}</span>
                      )}
                    </div>
                  )}

                  {message.type === 'user' && (
                    <div className="flex items-center justify-end gap-1.5 mb-1.5 mr-0.5">
                      <span className="text-[11px] font-medium text-gray-500 emoji-inline-fallback"><span className="emoji-safe" aria-hidden="true">🧑</span> You</span>
                      <div className="w-7 h-7 rounded-full bg-slate-800 flex items-center justify-center shadow-sm">
                        <UserCircle2 className="w-4 h-4 text-white" />
                      </div>
                    </div>
                  )}

                  {/* Bubble */}
                  <div
                    className={`rounded-2xl px-4 py-3 overflow-hidden ${message.type === 'user'
                        ? 'bg-emerald-600 text-white rounded-tr-md'
                        : 'bg-slate-100 text-slate-800 shadow-sm shadow-slate-300/20 border border-slate-200 rounded-tl-md'
                      }`}
                  >
                    {renderMessageContent(renderedContent)}

                    {/* 🔊 Speak Button (AI messages only) */}
                    {message.type === 'ai' && renderedContent && !message.isStreaming && (
                      <button
                        onClick={() => speakMessage(message.id, renderedContent)}
                        className={`mt-2 flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg transition-all ${speakingMessageId === message.id
                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                            : 'text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 border border-transparent'
                          }`}
                        title={speakingMessageId === message.id ? 'Stop speaking' : 'Listen to response'}
                      >
                        {speakingMessageId === message.id ? (
                          <><VolumeX className="w-3.5 h-3.5" /><span>Stop</span></>
                        ) : (
                          <><Volume2 className="w-3.5 h-3.5" /><span>Listen</span></>
                        )}
                      </button>
                    )}

                  </div>

                  {/* Timestamp */}
                  <div className={`mt-1 text-[10px] text-gray-300 ${message.type === 'user' ? 'text-right mr-1' : 'ml-1'}`}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            )
          })}

          {/* Loading */}
          {isLoading && !isStreaming && (
            <div className="flex justify-start">
              <div>
                <div className="flex items-center gap-1.5 mb-1.5 ml-0.5">
                  <div className="w-5 h-5 rounded-md bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                    <Sparkles className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-[11px] font-medium text-gray-400">Ocean</span>
                </div>
                <div className="bg-slate-100 shadow-sm shadow-slate-300/20 border border-slate-200 rounded-2xl rounded-tl-md px-4 py-4">
                  <div className="flex items-center gap-3">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    <span className="text-xs text-gray-400">{t.thinking}</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </main>

      {/* ── Suggested Questions (welcome state) ── */}
      {messages.length <= 1 && (
        <div className="max-w-2xl mx-auto w-full px-4 sm:px-6 pb-3">
          <button
            onClick={openTrinityDebate}
            className="w-full mb-2.5 text-left text-sm text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded-xl px-4 py-3 transition-all border border-indigo-100 hover:border-indigo-200"
          >
            🎭 Open Deep Analysis
          </button>
          <p className="text-xs text-gray-400 mb-2.5 font-medium">{t.tryAsking}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {suggestedQuestions.map((q, idx) => (
              <button
                key={idx}
                onClick={() => sendMessage(q)}
                className="text-left text-sm text-gray-600 bg-slate-100 hover:bg-emerald-50 hover:text-emerald-700 rounded-xl px-4 py-3 transition-all border border-slate-200 hover:border-emerald-200 hover:shadow-sm"
              >
                {q}
              </button>
            ))}
          </div>

          <div className="mt-4 space-y-2.5">
            <p className="text-xs text-gray-400 font-medium">Helpful ways to explore</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <button
                onClick={activateNanoGridModule}
                className="text-left text-sm text-cyan-700 bg-cyan-50 hover:bg-cyan-100 rounded-xl px-4 py-3 transition-all border border-cyan-100 hover:border-cyan-200"
              >
                🔷 Visual help · guided exploration
              </button>
              <button
                onClick={openTrinityDebate}
                className="text-left text-sm text-indigo-700 bg-indigo-50 hover:bg-indigo-100 rounded-xl px-4 py-3 transition-all border border-indigo-100 hover:border-indigo-200"
              >
                🎭 Deep analysis · clearer comparison
              </button>
              <button
                onClick={toggleRecording}
                className="text-left text-sm text-emerald-700 bg-emerald-50 hover:bg-emerald-100 rounded-xl px-4 py-3 transition-all border border-emerald-100 hover:border-emerald-200"
              >
                🎤 Voice · speak directly with Ocean
              </button>
              <button
                onClick={toggleCamera}
                className="text-left text-sm text-blue-700 bg-blue-50 hover:bg-blue-100 rounded-xl px-4 py-3 transition-all border border-blue-100 hover:border-blue-200"
              >
                📷 Camera · understand what you capture
              </button>
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-left text-sm text-purple-700 bg-purple-50 hover:bg-purple-100 rounded-xl px-4 py-3 transition-all border border-purple-100 hover:border-purple-200"
              >
                📄 Document · scan and analyze files
              </button>
              <button
                onClick={() => sendMessage(uiLanguage === 'sq' ? 'Shpjego këtë term në shqip me Albanian Dictionary' : 'Explain this term in Albanian using the Albanian Dictionary')}
                className="text-left text-sm text-amber-700 bg-amber-50 hover:bg-amber-100 rounded-xl px-4 py-3 transition-all border border-amber-100 hover:border-amber-200"
              >
                🇦🇱 Language help · simple Albanian definitions
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Camera Overlay (fullscreen modal) ── */}
      {showCamera && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-100 rounded-3xl overflow-hidden shadow-2xl shadow-slate-500/20 max-w-sm w-full">
            <video ref={videoRef} autoPlay playsInline className="w-full aspect-[4/3] bg-gray-900 object-cover" />
            <div className="flex items-center justify-center gap-4 p-5">
              <button onClick={switchCamera} className="p-3 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors text-gray-600" title={t.switchCam}>
                <RefreshCw className="w-5 h-5" />
              </button>
              <button onClick={capturePhoto} className="p-5 bg-emerald-500 hover:bg-emerald-600 rounded-full transition-all text-white shadow-lg shadow-emerald-500/30 active:scale-95">
                <Camera className="w-6 h-6" />
              </button>
              <button onClick={toggleCamera} className="p-3 bg-gray-100 hover:bg-red-50 rounded-full transition-colors text-gray-600 hover:text-red-500" title={t.close}>
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Input Area ── */}
      <div className="flex-shrink-0 border-t border-slate-300/70 bg-slate-100/85 backdrop-blur-xl">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-3">
          {/* Recording indicator */}
          {isRecording && (
            <div className="flex items-center gap-2.5 mb-3 px-4 py-2.5 bg-red-50 border border-red-100 rounded-xl">
              <div className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse" />
              <span className="text-xs text-red-600 font-medium flex-1">Recording audio...</span>
              <button onClick={toggleRecording} className="text-xs text-red-500 hover:text-red-700 font-semibold transition-colors px-2 py-1 hover:bg-red-100 rounded-lg">
                {t.stopButton}
              </button>
            </div>
          )}

          <div className="relative flex items-end gap-2 bg-slate-100/90 border border-slate-300 rounded-2xl px-3 py-2 focus-within:border-emerald-300 focus-within:ring-2 focus-within:ring-emerald-500/10 focus-within:bg-slate-50 transition-all">
            {/* Attach (+) button */}
            <div className="relative flex-shrink-0 self-end" ref={attachMenuRef}>
              <button
                onClick={(e) => { e.stopPropagation(); setShowAttachMenu(!showAttachMenu); }}
                disabled={isLoading || isStreaming}
                className={`p-2 rounded-xl transition-all ${showAttachMenu ? 'bg-emerald-100 text-emerald-600' : 'hover:bg-gray-200/80 text-gray-400 hover:text-gray-600'}`}
              >
                <Plus className={`w-5 h-5 transition-transform duration-200 ${showAttachMenu ? 'rotate-45' : ''}`} />
              </button>

              {showAttachMenu && (
                <div className="absolute bottom-full left-0 mb-2 bg-slate-100 rounded-2xl shadow-2xl shadow-slate-400/20 border border-slate-200 py-2 z-50 min-w-[180px] overflow-hidden">
                  <button
                    onClick={toggleRecording}
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center">
                      <Mic className="w-4 h-4 text-emerald-600" />
                    </div>
                    <span className="font-medium">Voice</span>
                  </button>
                  <button
                    onClick={toggleCamera}
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                      <Camera className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="font-medium">Camera</span>
                  </button>
                  <button
                    onClick={() => { setShowAttachMenu(false); fileInputRef.current?.click(); }}
                    className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center">
                      <FileText className="w-4 h-4 text-purple-600" />
                    </div>
                    <span className="font-medium">Document</span>
                  </button>
                </div>
              )}
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              className="hidden"
              accept=".txt,.pdf,.doc,.docx,.md,.csv,.json"
            />

            {/* Text area */}
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => handleInputChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t.askAnything}
              rows={1}
              className="flex-1 bg-transparent border-none resize-none text-sm text-gray-900 placeholder-gray-400 focus:outline-none py-2 max-h-[120px] leading-relaxed"
              disabled={isLoading || isStreaming}
            />

            {/* Send / Stop */}
            <div className="flex-shrink-0 self-end">
              {isStreaming ? (
                <button onClick={stopStreaming} className="px-4 py-2 bg-red-500 hover:bg-red-600 rounded-xl transition-colors active:scale-95 text-white text-sm font-medium">
                  {t.stopButton}
                </button>
              ) : (
                <div className="flex items-center gap-2">
                  <button
                    onClick={openTrinityDebate}
                    className="hidden md:inline-flex px-3 py-2 bg-indigo-50 hover:bg-indigo-100 rounded-xl transition-all text-indigo-700 text-sm font-medium"
                    title="Send this topic to Trinity Debate"
                  >
                    🎭 Debate
                  </button>
                  <button
                    onClick={() => exportConversation('pdf')}
                    disabled={Boolean(exportingFormat) || messages.length < 2}
                    className="hidden md:inline-flex px-3 py-2 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all text-slate-700 text-sm font-medium disabled:opacity-40"
                    title="Export chat as PDF"
                  >
                    {exportingFormat === 'pdf' ? 'PDF...' : 'PDF'}
                  </button>
                  <button
                    onClick={() => exportConversation('docx')}
                    disabled={Boolean(exportingFormat) || messages.length < 2}
                    className="hidden md:inline-flex px-3 py-2 bg-slate-100 hover:bg-slate-200 rounded-xl transition-all text-slate-700 text-sm font-medium disabled:opacity-40"
                    title="Export chat as Word"
                  >
                    {exportingFormat === 'docx' ? 'WORD...' : 'WORD'}
                  </button>
                  <button
                    onClick={() => sendMessage()}
                    disabled={isLoading || !inputValue.trim()}
                    className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-200 disabled:cursor-not-allowed rounded-xl transition-all active:scale-95 text-white text-sm font-medium"
                  >
                    {isLoading ? (
                      <Loader2 className="w-4 h-4 text-white animate-spin" />
                    ) : (
                      (t.sendAskButton || 'Send Ask')
                    )}
                  </button>
                </div>
              )}
            </div>
          </div>

          <p className="text-center text-[10px] text-gray-300 mt-2 select-none">Curiosity Ocean by Clisonix</p>
        </div>
      </div>
    </div>
  );
}
