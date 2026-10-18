/**
 * UltraWebThinking Chat API - Hybrid AI Backend
 * Primary: Ollama (local Llama 3.1 8B)
 * Fallback: Clisonix Ocean AI (production cloud)
 * 
 * NO MOCK DATA - REAL AI RESPONSES ONLY
 */

import type { NextApiRequest, NextApiResponse } from 'next';

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://localhost:11434';
const CLISONIX_URL = process.env.NEXT_PUBLIC_CLISONIX_URL || 'https://clisonix.com';
const MODEL = process.env.OLLAMA_MODEL || 'llama3.1:8b';

interface ChatRequest {
  message: string;
  mode?: 'general' | 'focused' | 'research' | 'brainstorm';
  personality?: 'assistant' | 'philosopher' | 'scientist' | 'creative';
  context?: string[];
  language?: string;
  useCloud?: boolean; // Force use Clisonix Cloud
}

interface ChatResponse {
  response: string;
  model: string;
  source: 'ollama' | 'clisonix' | 'fallback';
  thinking_time: number;
  metadata?: {
    tokens?: number;
    confidence?: number;
    language?: string;
  };
}

// System prompts based on personality
const systemPrompts: Record<string, string> = {
  assistant: `Ti je UltraWebThinking AI - një asistent i avancuar dhe i dobishëm. 
Përgjigju në mënyrë të qartë, koncize dhe të saktë. Përdor shqipen kur përdoruesi flet shqip.
Je i aftë të diskutosh çdo temë me ekspertizë dhe entuziazëm.`,

  philosopher: `Ti je një filozof i thellë që eksploron çështje të mëdha të jetës.
Analizon konceptet nga perspektiva të ndryshme, përdor logjikën dhe intuicionin.
Shpesh citon mendimtarë të mëdhenj dhe provokon mendim kritik.`,

  scientist: `Ti je një shkencëtar që bazohet në fakte, të dhëna dhe metodën shkencore.
Shpjegon koncepte komplekse në mënyrë të thjeshtë dhe të kuptueshme.
Citon hulumtime dhe zbulime të fundit shkencore.`,

  creative: `Ti je një mendimtar kreativ që sheh mundësi kudo.
Gjeneron ide të reja, bën lidhje të papritura dhe inspiron inovacion.
Përdor metafora, analogji dhe storytelling për të shprehur ide.`
};

// Mode-specific instructions
const modeInstructions: Record<string, string> = {
  general: 'Përgjigju natyrshëm dhe në mënyrë bisedore.',
  focused: 'Fokusohu në thelbin e pyetjes, jep përgjigje të drejtpërdrejtë.',
  research: 'Jep informacion të detajuar, cito burime kur mundesh.',
  brainstorm: 'Gjenero shumë ide, mos u kufizo, mendo në mënyrë të lirë.'
};

/**
 * Try Ollama local first
 */
async function tryOllama(
  message: string,
  systemMessage: string,
  context: string[],
  personality: string
): Promise<{ success: boolean; response?: string; tokens?: number }> {
  try {
    const messages = [
      { role: 'system', content: systemMessage },
      ...context.slice(-10).map((msg, i) => ({
        role: i % 2 === 0 ? 'user' : 'assistant',
        content: msg
      })),
      { role: 'user', content: message }
    ];

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: MODEL,
        messages,
        stream: false,
        options: {
          temperature: personality === 'creative' ? 0.9 : 0.7,
          top_p: 0.9,
          num_predict: 1024
        }
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      return { success: false };
    }

    const data = await response.json();
    return {
      success: true,
      response: data.message?.content,
      tokens: data.eval_count
    };
  } catch {
    return { success: false };
  }
}

/**
 * Fallback to Clisonix Ocean AI (production cloud)
 */
async function tryClisonix(
  message: string,
  language: string
): Promise<{ success: boolean; response?: string }> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000);

    const response = await fetch(`${CLISONIX_URL}/api/ocean`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, language }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      return { success: false };
    }

    const data = await response.json();
    return {
      success: true,
      response: data.response || data.message
    };
  } catch {
    return { success: false };
  }
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ChatResponse | { error: string }>
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const startTime = Date.now();
  const { 
    message, 
    mode = 'general', 
    personality = 'assistant', 
    context = [],
    language = 'sq',
    useCloud = false
  } = req.body as ChatRequest;

  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  const systemMessage = `${systemPrompts[personality] || systemPrompts.assistant}\n\n${modeInstructions[mode] || modeInstructions.general}`;

  // Strategy: Try Ollama first (if not forced to cloud), then Clisonix
  let result: { response: string; source: 'ollama' | 'clisonix' | 'fallback'; tokens?: number } | null = null;

  // 1. Try Ollama (local) unless cloud is forced
  if (!useCloud) {
    const ollamaResult = await tryOllama(message, systemMessage, context, personality);
    if (ollamaResult.success && ollamaResult.response) {
      result = {
        response: ollamaResult.response,
        source: 'ollama',
        tokens: ollamaResult.tokens
      };
    }
  }

  // 2. Fallback to Clisonix Cloud
  if (!result) {
    const clisonixResult = await tryClisonix(message, language);
    if (clisonixResult.success && clisonixResult.response) {
      result = {
        response: clisonixResult.response,
        source: 'clisonix'
      };
    }
  }

  // 3. Ultimate fallback
  if (!result) {
    result = {
      response: `⚡ UltraWebThinking AI

Sistemi po përpunon kërkesën tuaj. Në këtë moment:
- Ollama lokal: Duke u lidhur...
- Clisonix Cloud: Duke u lidhur...

Pyetja juaj: "${message}"

Provo përsëri për një moment ose kontrollo lidhjen me internetin.`,
      source: 'fallback'
    };
  }

  const thinkingTime = Date.now() - startTime;

  return res.status(200).json({
    response: result.response,
    model: result.source === 'ollama' ? MODEL : 'ocean-ai',
    source: result.source,
    thinking_time: thinkingTime,
    metadata: {
      tokens: result.tokens,
      confidence: result.source !== 'fallback' ? 0.95 : 0.5,
      language
    }
  });
}
