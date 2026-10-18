import assert from 'node:assert/strict';
import { takeSpeech, takeLines } from '../app/modules/curiosity-ocean/voice/voice-protocol.ts';

// A decimal may arrive in different network chunks. Never speak its prefix.
assert.deepEqual(takeSpeech('Çmimi është 3.'), { phrases: [], rest: 'Çmimi është 3.' });
assert.deepEqual(takeSpeech('Çmimi është 3.14 euro. Si jeni?'), {
  phrases: ['Çmimi është 3.14 euro.'], rest: 'Si jeni?',
});
assert.deepEqual(takeSpeech('Si jeni?', true), { phrases: ['Si jeni?'], rest: '' });
assert.deepEqual(takeSpeech('Përshëndetje! Po ju dëgjoj. ', true), {
  phrases: ['Përshëndetje!', 'Po ju dëgjoj.'], rest: '',
});
const long = ('fjalë ').repeat(70);
const split = takeSpeech(long);
assert.ok(split.phrases.length > 0);
assert.equal(split.phrases.join(' ').replace(/\s+/g, ' ').trim() + ' ' + split.rest.trim(), long.trim());
assert.deepEqual(takeLines('{"text":"Përshën'), { lines: [], rest: '{"text":"Përshën' });
assert.deepEqual(takeLines('{"text":"Përshëndetje"}\n{"done":'), { lines: ['{"text":"Përshëndetje"}'], rest: '{"done":' });
console.log('Voice sentence boundaries and fragmented network records passed.');
