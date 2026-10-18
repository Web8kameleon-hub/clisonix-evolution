export type VoiceMessage = { role: 'user' | 'assistant'; content: string };

export type VoiceOption = {
  id: string;
  locale: string;
  gender: string;
  name: string;
};

export type VoiceLanguageCapability = {
  code: string;
  label: string;
  locales: string[];
  default_voice: string;
  voices: VoiceOption[];
};

export type VoiceCapabilities = {
  version: string;
  source: 'runtime-discovery' | string;
  default_language: string;
  languages: VoiceLanguageCapability[];
};

export function chooseVoiceLanguage(capabilities: VoiceCapabilities, browserLocale = ''): string {
  const requested = browserLocale.trim().split('-', 1)[0].toLowerCase();
  if (requested && capabilities.languages.some((item) => item.code === requested)) return requested;
  if (capabilities.languages.some((item) => item.code === capabilities.default_language)) {
    return capabilities.default_language;
  }
  return capabilities.languages[0]?.code || '';
}

export function languageDisplayName(capability: VoiceLanguageCapability, uiLocale = 'en'): string {
  try {
    return new Intl.DisplayNames([uiLocale], { type: 'language' }).of(capability.code) || capability.label;
  } catch {
    return capability.label;
  }
}

export function takeSpeech(text: string, flush = false): { phrases: string[]; rest: string } {
  const phrases: string[] = [];
  let rest = text;
  while (rest.trim()) {
    const sentence = /[.!?。！？](?:["”']?)\s/.exec(rest);
    let cut = sentence ? sentence.index + sentence[0].length : 0;
    if (!cut && rest.length > 220) {
      cut = rest.lastIndexOf(' ', 220);
      if (cut < 80) cut = 220;
    }
    if (!cut && flush) cut = rest.length;
    if (!cut) break;
    const phrase = rest.slice(0, cut).replace(/[*#`]/g, '').trim();
    rest = rest.slice(cut);
    if (phrase) phrases.push(phrase);
  }
  return { phrases, rest };
}

export function takeLines(pending: string): { lines: string[]; rest: string } {
  const lines = pending.split('\n');
  return { lines, rest: lines.pop() || '' };
}
