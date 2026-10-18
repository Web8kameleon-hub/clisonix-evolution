// Exercise the actual status component against a real candidate API.
// The isolated test server forwards measurements; it creates no success data.
import assert from 'node:assert/strict';
import http from 'node:http';
import { build } from 'esbuild';
import { chromium } from 'playwright';

const api = process.env.STATUS_TEST_API_URL;
if (!api) throw new Error('STATUS_TEST_API_URL must identify the candidate status API');

const bundle = await build({
  stdin: {
    contents: `import React from 'react'; import { createRoot } from 'react-dom/client';
      import StatusPage from './app/status/page.tsx';
      createRoot(document.getElementById('root')).render(React.createElement(StatusPage));`,
    resolveDir: process.cwd(), loader: 'tsx',
  },
  bundle: true, write: false, platform: 'browser', format: 'iife', jsx: 'automatic',
  define: { 'process.env.NODE_ENV': '"development"', 'process.env': '{}' },
});
let upstream = api;
let evidence;
const server = http.createServer(async (request, response) => {
  if (request.url === '/component.js') {
    response.setHeader('Content-Type', 'text/javascript');
    response.end(bundle.outputFiles[0].text);
  } else if (request.url === '/api/system/health') {
    try {
      const result = await fetch(`${upstream}/api/system/health`);
      response.writeHead(result.status, { 'Content-Type': 'application/json' });
      const body = await result.text();
      if (result.ok) evidence = JSON.parse(body);
      response.end(body);
    } catch {
      response.writeHead(502);
      response.end();
    }
  } else {
    response.setHeader('Content-Type', 'text/html');
    response.end('<!doctype html><html><body><div id="root"></div><script src="/component.js"></script></body></html>');
  }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
let browser;
try {
  browser = await chromium.launch({
    headless: true,
    ...(process.env.STATUS_TEST_BROWSER ? { executablePath: process.env.STATUS_TEST_BROWSER } : {}),
  });
  const page = await browser.newPage();
  page.setDefaultTimeout(15000);
  const errors = [];
  page.on('pageerror', error => { errors.push(error.message); console.error(error.message); });
  await page.clock.install();
  await page.goto(`http://127.0.0.1:${server.address().port}`);
  await page.getByText('All Systems Operational', { exact: true }).waitFor();
  for (const name of ['API', 'WEB', 'CORE', 'EXCEL', 'MARKETPLACE', 'BALANCER']) {
    const row = page.getByText(name, { exact: true }).locator('..').locator('..');
    const text = await row.innerText();
    assert.match(text, /Operational/);
    assert.match(text, /\d+(\.\d+)?ms/);
  }
  assert.ok(evidence.telemetry.uptime_history.length > 0);
  await page.getByText(`${evidence.telemetry.uptime_history.at(-1).samples} observed checks`, { exact: true }).waitFor();
  assert.match(await page.locator('body').innerText(), /unobserved time is not counted/);
  // Genuine connection failure at the test proxy: previously shown success
  // must disappear on the next refresh, not remain as a stale green status.
  upstream = 'http://127.0.0.1:1';
  await page.clock.fastForward(60000);
  await page.getByText('Status Unavailable', { exact: true }).waitFor();
  assert.equal(await page.getByText('Operational', { exact: true }).count(), 0);
  assert.deepEqual(errors, []);
  console.log(JSON.stringify({ ui: 'passed', real_samples: evidence.telemetry.uptime_history.at(-1).samples,
    balancer: evidence.services.find(service => service.name === 'balancer'), stale_success_removed: true }));
} finally {
  await browser?.close();
  await new Promise(resolve => server.close(resolve));
}
