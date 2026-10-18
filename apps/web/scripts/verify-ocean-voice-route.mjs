import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import ts from 'typescript';

const originalFetch = globalThis.fetch;
const originalModel = process.env.OCEAN_VOICE_MODEL;
delete process.env.OCEAN_VOICE_MODEL;
const gemma = 'huihui_ai/gemma-4-abliterated:12b';
const source = (await readFile(new URL('../app/api/ocean/voice/chat/route.ts', import.meta.url), 'utf8'))
  .replace("import { auth } from '@/lib/auth/core';", 'const auth = async () => globalThis.voiceTestSession;');
const js = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022 } }).outputText;
const route = await import('data:text/javascript;base64,' + Buffer.from(js).toString('base64'));
const request = () => new Request('https://clisonix.com/api/ocean/voice/chat', {
  method: 'POST', headers: { 'Content-Type': 'application/json', 'X-User-ID': 'spoofed' },
  body: JSON.stringify({ text: 'Si jeni?', language: 'sq', messages: [{ role: 'user', content: 'Quhem Arben.' }] }),
});
let gpu = 0, captured, upstreamModel = gemma, chatCalls = 0;
try {
  globalThis.voiceTestSession = null;
  assert.equal((await route.POST(request())).status, 401, 'A supplied user header must not bypass session authentication');
  globalThis.voiceTestSession = { user: { id: 'voice-test', email: 'voice-test@example.invalid' } };
  globalThis.fetch = async (url, init) => {
    if (String(url).endsWith('/api/generate')) {
      const payload = JSON.parse(init.body);
      assert.equal(payload.model, gemma);
      assert.equal(payload.options.num_ctx, 4096);
      return Response.json({ done: true, model: gemma });
    }
    if (String(url).endsWith('/api/ps')) return Response.json({ models: [{ name: gemma, size: 100, size_vram: gpu }] });
    if (String(url).endsWith('/api/chat')) {
      captured = JSON.parse(init.body);
      chatCalls++;
      const bytes = new TextEncoder().encode(JSON.stringify({ model: upstreamModel, message: { content: 'Përshëndetje Arben.' } }) + '\n' + JSON.stringify({ model: upstreamModel, done: true }) + '\n');
      return new Response(new ReadableStream({ start(controller) {
        // Split within UTF-8 and JSON, just as real network reads can do.
        for (let i = 0; i < bytes.length; i += 2) controller.enqueue(bytes.slice(i, i + 2));
        controller.close();
      } }));
    }
    throw new Error('Unexpected upstream');
  };
  assert.equal((await route.POST(request())).status, 503, 'CPU residency must be rejected');
  gpu = 99;
  assert.equal((await route.POST(request())).status, 503, 'Partial GPU residency must be rejected');
  process.env.OCEAN_VOICE_MODEL = 'llama3.1:8b';
  assert.equal((await route.POST(request())).status, 503, 'Environment cannot select a different model');
  delete process.env.OCEAN_VOICE_MODEL;
  const override = new Request('https://clisonix.com/api/ocean/voice/chat', { method: 'POST', body: JSON.stringify({ text: 'Hi', model: 'llama3.1:8b' }) });
  assert.equal((await route.POST(override)).status, 400, 'Client cannot select a different model');
  assert.equal(chatCalls, 0, 'Forbidden requests must not start generation');
  gpu = 100;
  const response = await route.POST(request());
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('cache-control'), 'no-store, no-transform');
  const events = (await response.text()).trim().split('\n').map(JSON.parse);
  assert.equal(events.find((event) => event.text)?.text, 'Përshëndetje Arben.');
  assert.equal(events.at(-1).done, true);
  assert.equal(captured.options.num_gpu, 999);
  assert.equal(captured.model, gemma);
  assert.equal(captured.options.num_ctx, 4096);
  assert.equal(captured.think, false, 'Voice must not wait for a hidden reasoning response');
  assert.equal(captured.messages[1].content, 'Quhem Arben.', 'Conversation context must survive between voice turns');
  assert.equal(captured.messages.at(-1).content, 'Si jeni?');
  const again = await route.POST(request());
  assert.equal(again.status, 200, 'Completed requests must release capacity');
  await again.body.cancel();
  const afterCancel = await route.POST(request());
  assert.equal(afterCancel.status, 200, 'Interrupted speech must release capacity');
  await afterCancel.text();
  upstreamModel = 'llama3.1:8b';
  const wrongModel = (await (await route.POST(request())).text()).trim().split('\n').map(JSON.parse);
  assert(wrongModel.some(event => event.error), 'Unexpected upstream model must fail closed');
  assert(!wrongModel.some(event => event.text), 'Other models must never produce spoken text');
  assert.equal(chatCalls, 4, 'Model mismatch must not trigger fallback');
  console.log('Gemma-only law, no fallback, full GPU, authentication, history, UTF-8 and cancellation passed.');
} finally {
  globalThis.fetch = originalFetch;
  if (originalModel === undefined) delete process.env.OCEAN_VOICE_MODEL;
  else process.env.OCEAN_VOICE_MODEL = originalModel;
  delete globalThis.voiceTestSession;
}
