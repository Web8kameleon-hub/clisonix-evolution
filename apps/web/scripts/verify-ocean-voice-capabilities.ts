import assert from 'node:assert/strict';
import {
  chooseVoiceLanguage,
  languageDisplayName,
  type VoiceCapabilities,
} from '../app/modules/curiosity-ocean/voice/voice-protocol.ts';

const capabilities: VoiceCapabilities = {
  version: 'test',
  source: 'runtime-discovery',
  default_language: 'de',
  languages: [
    { code: 'de', label: 'German', locales: ['de-DE'], default_voice: 'voice-de', voices: [] },
    { code: 'sq', label: 'Albanian', locales: ['sq-AL'], default_voice: 'voice-sq', voices: [] },
    { code: 'ja', label: 'Japanese', locales: ['ja-JP'], default_voice: 'voice-ja', voices: [] },
  ],
};

assert.equal(chooseVoiceLanguage(capabilities, 'sq-AL'), 'sq');
assert.equal(chooseVoiceLanguage(capabilities, 'ja-JP'), 'ja');
assert.equal(chooseVoiceLanguage(capabilities, 'fr-FR'), 'de');
assert.equal(chooseVoiceLanguage({ ...capabilities, default_language: '' }, ''), 'de');
assert.ok(languageDisplayName(capabilities.languages[1], 'sq').length > 0);

console.log('Ocean voice capability checks passed.');
