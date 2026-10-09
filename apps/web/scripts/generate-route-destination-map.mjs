import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { pathToFileURL } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const webRoot = path.resolve(__dirname, '..');
const repoRoot = path.resolve(webRoot, '..', '..');
const appDir = path.join(webRoot, 'app');
const outJson = path.join(repoRoot, 'docs', 'production', 'route-destination-map.json');
const outMd = path.join(repoRoot, 'docs', 'production', 'route-destination-map.md');

function normalizePath(value) {
  return value.replace(/\\/g, '/');
}

function toRouteFromPageFile(relativeFile) {
  const normalized = normalizePath(relativeFile);
  const rawSegments = normalized.split('/').filter(Boolean);
  if (rawSegments.length && /^page\.(tsx|ts|jsx|js)$/i.test(rawSegments[rawSegments.length - 1])) {
    rawSegments.pop();
  }
  const routeSegments = rawSegments.filter((seg) => !seg.startsWith('(') && !seg.startsWith('@'));
  if (routeSegments.length === 0) {
    return '/';
  }
  return `/${routeSegments.join('/')}`;
}

function toRouteFromApiFile(relativeFile) {
  const normalized = normalizePath(relativeFile);
  const rawSegments = normalized.split('/').filter(Boolean);
  if (rawSegments.length && /^route\.(tsx|ts|jsx|js)$/i.test(rawSegments[rawSegments.length - 1])) {
    rawSegments.pop();
  }
  const routeSegments = rawSegments.filter((seg) => !seg.startsWith('(') && !seg.startsWith('@'));
  if (routeSegments.length === 0) {
    return '/';
  }
  return `/${routeSegments.join('/')}`;
}

function walk(dir, base = '') {
  const abs = path.join(dir, base);
  const entries = fs.readdirSync(abs, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    const rel = path.join(base, entry.name);
    if (entry.isDirectory()) {
      files.push(...walk(dir, rel));
      continue;
    }
    files.push(rel);
  }
  return files;
}

function flattenRewriteResult(value) {
  if (Array.isArray(value)) {
    return value;
  }
  if (!value || typeof value !== 'object') {
    return [];
  }

  const keys = ['beforeFiles', 'afterFiles', 'fallback'];
  const out = [];
  for (const key of keys) {
    if (Array.isArray(value[key])) {
      out.push(...value[key]);
    }
  }
  return out;
}

function safeString(value) {
  if (typeof value === 'string') {
    return value;
  }
  return '';
}

async function loadNextConfigMappings() {
  const nextConfigFileUrl = pathToFileURL(path.join(webRoot, 'next.config.js')).href;
  const nextConfigModule = await import(nextConfigFileUrl);
  const nextConfig = nextConfigModule.default || {};

  let redirects = [];
  if (typeof nextConfig.redirects === 'function') {
    redirects = await nextConfig.redirects();
  }

  let rewrites = [];
  if (typeof nextConfig.rewrites === 'function') {
    const rewriteResult = await nextConfig.rewrites();
    rewrites = flattenRewriteResult(rewriteResult);
  }

  const redirectRows = (Array.isArray(redirects) ? redirects : []).map((item) => ({
    source: safeString(item?.source),
    destination: safeString(item?.destination),
    status: item?.permanent ? '308-permanent' : '307-temporary',
    type: 'redirect',
  }));

  const rewriteRows = (Array.isArray(rewrites) ? rewrites : []).map((item) => ({
    source: safeString(item?.source),
    destination: safeString(item?.destination),
    status: 'rewrite',
    type: 'rewrite',
  }));

  return { redirectRows, rewriteRows };
}

function buildMarkdown(payload) {
  const lines = [];
  lines.push('# Route Destination Map');
  lines.push('');
  lines.push(`Generated: ${payload.generatedAt}`);
  lines.push('');
  lines.push('## App Page Routes');
  lines.push('');
  lines.push('| Route | Destination | Type |');
  lines.push('|---|---|---|');
  for (const row of payload.appPageRoutes) {
    lines.push(`| ${row.route} | ${row.destination} | ${row.type} |`);
  }

  lines.push('');
  lines.push('## API Routes');
  lines.push('');
  lines.push('| Route | Destination | Type |');
  lines.push('|---|---|---|');
  for (const row of payload.apiRoutes) {
    lines.push(`| ${row.route} | ${row.destination} | ${row.type} |`);
  }

  lines.push('');
  lines.push('## Redirects');
  lines.push('');
  lines.push('| Source | Destination | Status |');
  lines.push('|---|---|---|');
  for (const row of payload.redirects) {
    lines.push(`| ${row.source} | ${row.destination} | ${row.status} |`);
  }

  lines.push('');
  lines.push('## Rewrites');
  lines.push('');
  lines.push('| Source | Destination | Type |');
  lines.push('|---|---|---|');
  for (const row of payload.rewrites) {
    lines.push(`| ${row.source} | ${row.destination} | ${row.status} |`);
  }

  lines.push('');
  return lines.join('\n');
}

async function main() {
  const allFiles = walk(appDir);

  const pageFiles = allFiles.filter((file) => /(^|\\|\/)page\.(tsx|ts|jsx|js)$/i.test(file));
  const apiFiles = allFiles.filter((file) => /(^|\\|\/)route\.(tsx|ts|jsx|js)$/i.test(file));

  const appPageRoutes = pageFiles
    .map((file) => ({
      route: toRouteFromPageFile(file),
      destination: normalizePath(path.join('apps/web/app', file)),
      type: 'app-page',
    }))
    .sort((a, b) => a.route.localeCompare(b.route));

  const apiRoutes = apiFiles
    .map((file) => ({
      route: toRouteFromApiFile(file),
      destination: normalizePath(path.join('apps/web/app', file)),
      type: 'app-api',
    }))
    .sort((a, b) => a.route.localeCompare(b.route));

  const { redirectRows, rewriteRows } = await loadNextConfigMappings();
  const redirects = redirectRows
    .filter((row) => row.source && row.destination)
    .sort((a, b) => a.source.localeCompare(b.source));
  const rewrites = rewriteRows
    .filter((row) => row.source && row.destination)
    .sort((a, b) => a.source.localeCompare(b.source));

  const payload = {
    generatedAt: new Date().toISOString(),
    summary: {
      appPageRoutes: appPageRoutes.length,
      apiRoutes: apiRoutes.length,
      redirects: redirects.length,
      rewrites: rewrites.length,
      total: appPageRoutes.length + apiRoutes.length + redirects.length + rewrites.length,
    },
    appPageRoutes,
    apiRoutes,
    redirects,
    rewrites,
  };

  fs.mkdirSync(path.dirname(outJson), { recursive: true });
  fs.writeFileSync(outJson, `${JSON.stringify(payload, null, 2)}\n`, 'utf8');
  fs.writeFileSync(outMd, buildMarkdown(payload), 'utf8');

  console.log(`Generated: ${normalizePath(path.relative(repoRoot, outJson))}`);
  console.log(`Generated: ${normalizePath(path.relative(repoRoot, outMd))}`);
  console.log(`Total mappings: ${payload.summary.total}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
