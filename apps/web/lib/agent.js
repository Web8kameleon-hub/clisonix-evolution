import fs from "node:fs/promises";
import path from "node:path";
import { spawnSync } from "node:child_process";

const CACHE_TTL_MS = 60_000;
const ROOT_DIR = path.resolve(process.cwd(), "..", "..");

let cachedContext = null;
let cachedAt = 0;

function safeTrim(value, fallback = "unknown") {
  if (typeof value !== "string") return fallback;
  const trimmed = value.trim();
  return trimmed || fallback;
}

function discoverGitInfo() {
  const envBranch =
    process.env.VERCEL_GIT_COMMIT_REF ||
    process.env.GITHUB_REF_NAME ||
    process.env.BRANCH_NAME;
  const envCommit =
    process.env.VERCEL_GIT_COMMIT_SHA ||
    process.env.GITHUB_SHA ||
    process.env.COMMIT_SHA;

  const branch =
    safeTrim(envBranch, "") ||
    safeTrim(
      spawnSync("git", ["rev-parse", "--abbrev-ref", "HEAD"], {
        cwd: ROOT_DIR,
        encoding: "utf8",
        timeout: 1200,
      }).stdout,
      "unknown",
    );

  const commit =
    safeTrim(envCommit, "") ||
    safeTrim(
      spawnSync("git", ["rev-parse", "--short", "HEAD"], {
        cwd: ROOT_DIR,
        encoding: "utf8",
        timeout: 1200,
      }).stdout,
      "unknown",
    );

  return { branch, commit };
}

function extractServicesFromCompose(composeText) {
  const services = [];
  const lines = String(composeText || "").split(/\r?\n/);
  let inServices = false;

  for (const rawLine of lines) {
    const line = rawLine || "";

    if (!inServices && /^services:\s*$/.test(line)) {
      inServices = true;
      continue;
    }

    if (!inServices) continue;

    if (/^[^\s].+:\s*$/.test(line) && !/^services:\s*$/.test(line)) {
      break;
    }

    const match = line.match(/^\s{2}([a-zA-Z0-9_-]+):\s*$/);
    if (match?.[1]) {
      services.push(match[1]);
    }
  }

  return [...new Set(services)].slice(0, 24);
}

async function discoverTopDocs() {
  const docCandidates = [];
  const rootEntries = await fs.readdir(ROOT_DIR, { withFileTypes: true });

  for (const entry of rootEntries) {
    if (!entry.isFile()) continue;
    if (!entry.name.toLowerCase().endsWith(".md")) continue;
    docCandidates.push(entry.name);
  }

  const docsDir = path.join(ROOT_DIR, "docs");
  try {
    const docsEntries = await fs.readdir(docsDir, { withFileTypes: true });
    for (const entry of docsEntries) {
      if (!entry.isFile()) continue;
      if (!entry.name.toLowerCase().endsWith(".md")) continue;
      docCandidates.push(`docs/${entry.name}`);
    }
  } catch {
    // docs directory is optional
  }

  return [...new Set(docCandidates)].sort().slice(0, 20);
}

function buildRuntimeHints() {
  return {
    oceanCore:
      process.env.OCEAN_INTERNAL_URL ||
      process.env.OCEAN_CORE_URL ||
      "http://clisonix-ocean-core:8030",
    openMind:
      process.env.OPENMIND_INTERNAL_URL ||
      process.env.OPENMIND_URL ||
      "http://clisonix-openmind:9999",
    albiUser:
      process.env.ALBI_USER_URL ||
      "http://clisonix-albi-user:6681",
  };
}

export function hasProjectContext(context) {
  if (!context || typeof context !== "object") return false;
  if (!context.projectName || !context.git) return false;
  if (!context.runtime || !context.runtime.oceanCore) return false;
  return true;
}

export async function getProjectContext(options = {}) {
  const forceRefresh = options.forceRefresh === true;
  const now = Date.now();

  if (!forceRefresh && cachedContext && now - cachedAt < CACHE_TTL_MS) {
    return cachedContext;
  }

  const packagePath = path.join(ROOT_DIR, "apps", "web", "package.json");
  const composePath = path.join(ROOT_DIR, "docker-compose.yml");

  let projectName = "Clisonix Cloud";
  let projectVersion = "unknown";

  try {
    const pkgRaw = await fs.readFile(packagePath, "utf8");
    const pkg = JSON.parse(pkgRaw);
    projectName = safeTrim(pkg?.name, projectName);
    projectVersion = safeTrim(pkg?.version, projectVersion);
  } catch {
    // keep defaults
  }

  let composeServices = [];
  try {
    const composeRaw = await fs.readFile(composePath, "utf8");
    composeServices = extractServicesFromCompose(composeRaw);
  } catch {
    // docker compose file may be unavailable in some runtimes
  }

  const docs = await discoverTopDocs().catch(() => []);
  const git = discoverGitInfo();
  const runtime = buildRuntimeHints();

  cachedContext = {
    generatedAt: new Date().toISOString(),
    projectName,
    projectVersion,
    git,
    runtime,
    services: composeServices,
    docs,
  };
  cachedAt = now;

  return cachedContext;
}

export function buildProjectSystemMessage(context) {
  const safeContext = hasProjectContext(context)
    ? context
    : {
        projectName: "Clisonix Cloud",
        projectVersion: "unknown",
        git: { branch: "unknown", commit: "unknown" },
        runtime: { oceanCore: "http://clisonix-ocean-core:8030" },
        services: [],
        docs: [],
      };

  const services = Array.isArray(safeContext.services)
    ? safeContext.services.slice(0, 12).join(", ")
    : "unknown";
  const docs = Array.isArray(safeContext.docs)
    ? safeContext.docs.slice(0, 8).join(", ")
    : "unknown";

  return [
    "You are Curiosity Ocean for Clisonix Cloud.",
    "Never claim you do not know the project or where you are running.",
    `Project: ${safeContext.projectName} v${safeContext.projectVersion}`,
    `Git: branch=${safeContext.git.branch}, commit=${safeContext.git.commit}`,
    `Runtime endpoints: ocean_core=${safeContext.runtime.oceanCore}, openmind=${safeContext.runtime.openMind}, albi_user=${safeContext.runtime.albiUser}`,
    `Known services: ${services || "unknown"}`,
    `Key docs: ${docs || "unknown"}`,
    "If stream/tools fail, explain degraded mode briefly and provide a practical next-step plan.",
  ].join("\n");
}

export function buildOceanStreamFallback({ reason, userMessage, context }) {
  const safeContext = hasProjectContext(context) ? context : null;
  const branch = safeContext?.git?.branch || "unknown";
  const commit = safeContext?.git?.commit || "unknown";
  const oceanCore = safeContext?.runtime?.oceanCore || "http://clisonix-ocean-core:8030";

  return [
    "Ocean stream is in degraded mode right now.",
    `Project context is loaded (${branch}@${commit}).`,
    `Primary ocean-core endpoint: ${oceanCore}`,
    `Last failure: ${safeTrim(reason, "upstream unavailable")}`,
    userMessage
      ? `I still received your message and can continue in fallback mode: \"${String(userMessage).slice(0, 160)}\".`
      : "I can continue in fallback mode and provide a direct plan.",
  ].join("\n");
}
