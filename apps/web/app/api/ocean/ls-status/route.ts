import { NextRequest, NextResponse } from "next/server";
import { promises as fs } from "node:fs";
import path from "node:path";

type BridgeState = "planned" | "active" | "offline";

type BridgeDefinition = {
  id: string;
  repo: string;
  role: string;
  state: BridgeState;
  usage_prompt: string;
};

type BridgeHealthState = "unknown" | "healthy" | "degraded" | "down";

type BridgeHealth = {
  status: BridgeHealthState;
  reachable: boolean;
  checked_at: string;
  latency_ms: number;
  http_status?: number;
  detail?: string;
  default_branch?: string;
};

type BridgeRuntimeRecord = {
  state: BridgeState;
  health: BridgeHealth;
  last_activation_at?: string;
  last_error?: string;
};

type BridgeRuntimeStore = Record<string, BridgeRuntimeRecord>;

type BridgeView = BridgeDefinition & {
  health: BridgeHealth;
  last_activation_at?: string;
  last_error?: string;
};

type LsCounts = {
  modules: number;
  laboratories: number;
  engines: number;
  signals: number;
  api_surface: number;
  iot_mesh_lora: number;
};

type EvidenceMap = {
  modules: string[];
  laboratories: string[];
  engines: string[];
  signals: string[];
  api_surface: string[];
  iot_mesh_lora: string[];
};

const MAX_SCAN_FILES = 30000;
const BRIDGE_RUNTIME_DIR = ".runtime";
const BRIDGE_RUNTIME_FILE = "ocean-bridge-state.json";
const BRIDGE_AUDIT_DIR = "artifacts";
const BRIDGE_AUDIT_FILE = "ocean-bridge-audit.jsonl";

const SKIP_DIRS = new Set([
  ".git",
  "node_modules",
  ".next",
  "dist",
  "build",
  "coverage",
  "__pycache__",
  ".venv",
  "venv",
  "tmp",
  "temp",
]);

const BRIDGES: BridgeDefinition[] = [
  {
    id: "bridge-01",
    repo: "LedjanAhmati/clisonix-blog",
    role: "content-pipeline",
    state: "planned",
    usage_prompt: "Pull healthcare content topics and align with current campaign.",
  },
  {
    id: "bridge-02",
    repo: "Web8kameleon-hub/OS-CLX",
    role: "os-runtime",
    state: "planned",
    usage_prompt: "Map runtime hooks needed for OS-CLX interoperability.",
  },
  {
    id: "bridge-03",
    repo: "Web8kameleon-hub/Kloud",
    role: "cloud-control-plane",
    state: "planned",
    usage_prompt: "Inspect control-plane contracts and drift across environments.",
  },
  {
    id: "bridge-04",
    repo: "Web8kameleon-hub/neuclx",
    role: "neural-core",
    state: "planned",
    usage_prompt: "Correlate neuclx model outputs with Ocean reasoning tasks.",
  },
  {
    id: "bridge-05",
    repo: "Web8kameleon-hub/Lightning-SPP-3.14",
    role: "rapid-prototyping",
    state: "planned",
    usage_prompt: "Extract rapid prototype components for frontend acceleration.",
  },
  {
    id: "bridge-06",
    repo: "LedjanAhmati/www.neuroconic.eu",
    role: "neuroconic-public-site-a",
    state: "planned",
    usage_prompt: "Sync public content themes with Clisonix narrative.",
  },
  {
    id: "bridge-07",
    repo: "Web8kameleon-hub/web8",
    role: "web-foundation",
    state: "planned",
    usage_prompt: "Reuse shared web foundation utilities where safe.",
  },
  {
    id: "bridge-08",
    repo: "Web8kameleon-hub/Web8kameleon-hub-clisonix-sdk",
    role: "sdk-contracts",
    state: "planned",
    usage_prompt: "Verify SDK contract parity with current API endpoints.",
  },
  {
    id: "bridge-09",
    repo: "Web8kameleon-hub/Ultrawebthinkig-v2",
    role: "thinking-ui",
    state: "planned",
    usage_prompt: "Port advanced thinking widgets for Ocean module.",
  },
  {
    id: "bridge-10",
    repo: "Web8kameleon-hub/Cwy",
    role: "workflow-engine",
    state: "planned",
    usage_prompt: "Connect workflow primitives for batch orchestration.",
  },
  {
    id: "bridge-11",
    repo: "Web8kameleon-hub/starbooking",
    role: "booking-domain",
    state: "planned",
    usage_prompt: "Analyze booking flows and expose reusable service adapters.",
  },
  {
    id: "bridge-12",
    repo: "Web8kameleon-hub/www.neuroconic.eu",
    role: "neuroconic-public-site-b",
    state: "planned",
    usage_prompt: "Compare deployment footprints against current web stack.",
  },
  {
    id: "bridge-13",
    repo: "Web8kameleon-hub/clisonix-news",
    role: "news-pipeline",
    state: "planned",
    usage_prompt: "Ingest breaking updates and build daily digest cards.",
  },
  {
    id: "bridge-14",
    repo: "Web8kameleon-hub/ultrathinking-web",
    role: "deep-reasoning-ui",
    state: "planned",
    usage_prompt: "Bridge ultrathinking sessions into Curiosity Ocean context.",
  },
  {
    id: "bridge-15",
    repo: "Web8kameleon-hub/clisonixwesterneurope",
    role: "regional-deployment",
    state: "planned",
    usage_prompt: "Plan regional rollout and environment-specific overrides.",
  },
  {
    id: "bridge-16",
    repo: "Web8kameleon-hub/react-router-starter-template",
    role: "frontend-template",
    state: "planned",
    usage_prompt: "Extract reusable router patterns for module navigation.",
  },
];

async function fileExists(targetPath: string): Promise<boolean> {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

async function resolveRepoRoot(): Promise<string> {
  const base = process.cwd();
  const candidates = [
    base,
    path.resolve(base, ".."),
    path.resolve(base, "..", ".."),
    path.resolve(base, "..", "..", ".."),
    path.resolve(base, "..", "..", "..", ".."),
  ];

  for (const candidate of candidates) {
    if (await fileExists(path.join(candidate, "docker-compose.yml"))) {
      return candidate;
    }
  }

  return base;
}

function emptyBridgeHealth(detail = "not_checked"): BridgeHealth {
  return {
    status: "unknown",
    reachable: false,
    checked_at: new Date(0).toISOString(),
    latency_ms: 0,
    detail,
  };
}

function runtimeFilePath(repoRoot: string): string {
  return path.join(repoRoot, BRIDGE_RUNTIME_DIR, BRIDGE_RUNTIME_FILE);
}

function auditFilePath(repoRoot: string): string {
  return path.join(repoRoot, BRIDGE_AUDIT_DIR, BRIDGE_AUDIT_FILE);
}

async function appendBridgeAudit(
  repoRoot: string,
  entry: Record<string, unknown>,
): Promise<void> {
  const dir = path.join(repoRoot, BRIDGE_AUDIT_DIR);
  await fs.mkdir(dir, { recursive: true });
  const line = JSON.stringify(entry) + "\n";
  await fs.appendFile(auditFilePath(repoRoot), line, "utf-8");
}

async function loadBridgeRuntimeStore(repoRoot: string): Promise<BridgeRuntimeStore> {
  const target = runtimeFilePath(repoRoot);
  try {
    const raw = await fs.readFile(target, "utf-8");
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return {};
    }
    return parsed as BridgeRuntimeStore;
  } catch {
    return {};
  }
}

async function saveBridgeRuntimeStore(
  repoRoot: string,
  store: BridgeRuntimeStore,
): Promise<void> {
  const dir = path.join(repoRoot, BRIDGE_RUNTIME_DIR);
  await fs.mkdir(dir, { recursive: true });
  const target = runtimeFilePath(repoRoot);
  await fs.writeFile(target, JSON.stringify(store, null, 2) + "\n", "utf-8");
}

async function testBridgeConnectivity(bridge: BridgeDefinition): Promise<BridgeHealth> {
  const started = Date.now();
  const headers: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "User-Agent": "clisonix-ocean-bridge-check",
  };

  const token = (process.env.GITHUB_TOKEN || process.env.GH_TOKEN || "").trim();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`https://api.github.com/repos/${bridge.repo}`, {
      method: "GET",
      headers,
      cache: "no-store",
    });

    const latency = Date.now() - started;
    const checkedAt = new Date().toISOString();

    if (response.status === 200) {
      const payload = (await response.json()) as Record<string, unknown>;
      return {
        status: "healthy",
        reachable: true,
        checked_at: checkedAt,
        latency_ms: latency,
        http_status: 200,
        detail: "repository_reachable",
        default_branch:
          typeof payload.default_branch === "string"
            ? payload.default_branch
            : undefined,
      };
    }

    if (response.status === 403 || response.status === 429) {
      return {
        status: "degraded",
        reachable: false,
        checked_at: checkedAt,
        latency_ms: latency,
        http_status: response.status,
        detail: "rate_limited_or_forbidden",
      };
    }

    if (response.status === 404) {
      return {
        status: "down",
        reachable: false,
        checked_at: checkedAt,
        latency_ms: latency,
        http_status: 404,
        detail: "repository_not_found",
      };
    }

    return {
      status: "degraded",
      reachable: false,
      checked_at: checkedAt,
      latency_ms: latency,
      http_status: response.status,
      detail: "unexpected_github_status",
    };
  } catch (error) {
    return {
      status: "down",
      reachable: false,
      checked_at: new Date().toISOString(),
      latency_ms: Date.now() - started,
      detail: error instanceof Error ? error.message : "network_failure",
    };
  }
}

function materializeBridges(
  runtimeStore: BridgeRuntimeStore,
): BridgeView[] {
  return BRIDGES.map((bridge) => {
    const runtime = runtimeStore[bridge.id];
    return {
      ...bridge,
      state: runtime?.state || bridge.state,
      health: runtime?.health || emptyBridgeHealth(),
      last_activation_at: runtime?.last_activation_at,
      last_error: runtime?.last_error,
    };
  });
}

function findBridge(bridgeId: string): BridgeDefinition | null {
  return BRIDGES.find((bridge) => bridge.id === bridgeId) || null;
}

function pushSample(bucket: string[], value: string): void {
  if (bucket.length >= 12) return;
  bucket.push(value);
}

function checkCategory(
  relPath: string,
  fileNameLower: string,
): Array<keyof LsCounts> {
  const categories: Array<keyof LsCounts> = [];
  const normalizedPath = relPath.toLowerCase();

  if (
    /(module|service|sdk|pipeline|agent|bridge|core)/.test(fileNameLower) ||
    normalizedPath.includes("/modules/")
  ) {
    categories.push("modules");
  }

  if (/(lab|laboratory|experiment)/.test(fileNameLower)) {
    categories.push("laboratories");
  }

  if (/(engine|_core\.|core\.)/.test(fileNameLower)) {
    categories.push("engines");
  }

  if (/(signal|telemetry|metric|observability)/.test(fileNameLower)) {
    categories.push("signals");
  }

  if (
    /api/.test(fileNameLower) ||
    normalizedPath.includes("/api/") ||
    fileNameLower === "route.ts"
  ) {
    categories.push("api_surface");
  }

  if (/(iot|mesh|lora|lorawan|nanogrid)/.test(fileNameLower)) {
    categories.push("iot_mesh_lora");
  }

  return categories;
}

async function collectRepoSignals(repoRoot: string): Promise<{
  counts: LsCounts;
  evidence: EvidenceMap;
  scanned_files: number;
  scanned_directories: number;
  capped: boolean;
}> {
  const counts: LsCounts = {
    modules: 0,
    laboratories: 0,
    engines: 0,
    signals: 0,
    api_surface: 0,
    iot_mesh_lora: 0,
  };

  const evidence: EvidenceMap = {
    modules: [],
    laboratories: [],
    engines: [],
    signals: [],
    api_surface: [],
    iot_mesh_lora: [],
  };

  const seen = {
    modules: new Set<string>(),
    laboratories: new Set<string>(),
    engines: new Set<string>(),
    signals: new Set<string>(),
    api_surface: new Set<string>(),
    iot_mesh_lora: new Set<string>(),
  };

  const queue: string[] = [repoRoot];
  let scannedFiles = 0;
  let scannedDirectories = 0;
  let capped = false;

  while (queue.length > 0) {
    const current = queue.shift() as string;
    scannedDirectories += 1;

    let entries: Array<import("node:fs").Dirent> = [];
    try {
      entries = await fs.readdir(current, { withFileTypes: true });
    } catch {
      continue;
    }

    for (const entry of entries) {
      if (entry.name.startsWith(".")) {
        if (!entry.name.startsWith(".github")) {
          continue;
        }
      }

      const abs = path.join(current, entry.name);

      if (entry.isDirectory()) {
        if (SKIP_DIRS.has(entry.name.toLowerCase())) {
          continue;
        }
        queue.push(abs);
        continue;
      }

      if (!entry.isFile()) continue;
      scannedFiles += 1;
      if (scannedFiles > MAX_SCAN_FILES) {
        capped = true;
        break;
      }

      const rel = path
        .relative(repoRoot, abs)
        .split(path.sep)
        .join("/");
      const categories = checkCategory(rel, entry.name.toLowerCase());

      for (const category of categories) {
        if (!seen[category].has(rel)) {
          seen[category].add(rel);
          counts[category] += 1;
          pushSample(evidence[category], rel);
        }
      }
    }

    if (capped) break;
  }

  return {
    counts,
    evidence,
    scanned_files: scannedFiles,
    scanned_directories: scannedDirectories,
    capped,
  };
}

export async function GET() {
  try {
    const repoRoot = await resolveRepoRoot();
    const scan = await collectRepoSignals(repoRoot);
    const runtimeStore = await loadBridgeRuntimeStore(repoRoot);
    const bridges = materializeBridges(runtimeStore);

    return NextResponse.json({
      ok: true,
      generated_at: new Date().toISOString(),
      repository: {
        root: repoRoot,
        name: path.basename(repoRoot),
      },
      ls_status: scan,
      bridge_cluster: {
        target: 16,
        defined: bridges.length,
        active: bridges.filter((bridge) => bridge.state === "active").length,
        healthy: bridges.filter((bridge) => bridge.health.status === "healthy").length,
        degraded: bridges.filter((bridge) => bridge.health.status === "degraded").length,
        down: bridges.filter((bridge) => bridge.health.status === "down").length,
        bridges,
      },
      usage_prompts: [
        "List top 10 engines and tell me which one to use for a runtime reasoning task.",
        "Show IoT mesh and LoRa related files, then suggest safe integration points.",
        "Activate and verify bridge health per repository before orchestration.",
        "Map API surface and propose which connector to activate for this request.",
      ],
      policy: {
        no_fake_data: true,
        note: "Counts are computed from scanned repository files. Bridge activation/health is stored from real connectivity checks.",
      },
      evidence: {
        bridge_audit_file: path.join(BRIDGE_AUDIT_DIR, BRIDGE_AUDIT_FILE).split(path.sep).join("/"),
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        error: "ls_status_failed",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as Record<string, unknown>;
    const action = String(body.action || "").trim().toLowerCase();
    const bridgeId = String(body.bridge_id || "").trim();
    const operator =
      request.headers.get("X-User-ID") ||
      request.headers.get("X-User-Id") ||
      request.headers.get("x-forwarded-for") ||
      "anonymous";

    const repoRoot = await resolveRepoRoot();
    const runtimeStore = await loadBridgeRuntimeStore(repoRoot);

    if (action === "test_all") {
      for (const bridge of BRIDGES) {
        const health = await testBridgeConnectivity(bridge);
        const current = runtimeStore[bridge.id];
        const nextState = current?.state || bridge.state;
        runtimeStore[bridge.id] = {
          state: nextState,
          health,
          last_activation_at: current?.last_activation_at,
          last_error: health.status === "healthy" ? undefined : health.detail,
        };

        await appendBridgeAudit(repoRoot, {
          ts: new Date().toISOString(),
          action: "test_all",
          bridge_id: bridge.id,
          repo: bridge.repo,
          operator,
          state_before: current?.state || bridge.state,
          state_after: nextState,
          health,
        });
      }

      await saveBridgeRuntimeStore(repoRoot, runtimeStore);
      return NextResponse.json({
        ok: true,
        action,
        bridge_cluster: {
          bridges: materializeBridges(runtimeStore),
        },
      });
    }

    if (!bridgeId) {
      return NextResponse.json(
        {
          ok: false,
          error: "bridge_id_required",
          supported_actions: ["test", "activate", "deactivate", "test_all"],
        },
        { status: 400 },
      );
    }

    const bridge = findBridge(bridgeId);
    if (!bridge) {
      return NextResponse.json(
        {
          ok: false,
          error: "bridge_not_found",
          bridge_id: bridgeId,
        },
        { status: 404 },
      );
    }

    if (action === "deactivate") {
      const current = runtimeStore[bridge.id];
      const nextState: BridgeState = "planned";
      runtimeStore[bridge.id] = {
        state: nextState,
        health: current?.health || emptyBridgeHealth("deactivated_without_prior_test"),
        last_activation_at: current?.last_activation_at,
        last_error: "deactivated_by_operator",
      };
      await appendBridgeAudit(repoRoot, {
        ts: new Date().toISOString(),
        action: "deactivate",
        bridge_id: bridge.id,
        repo: bridge.repo,
        operator,
        state_before: current?.state || bridge.state,
        state_after: nextState,
        health: runtimeStore[bridge.id].health,
      });
      await saveBridgeRuntimeStore(repoRoot, runtimeStore);
      return NextResponse.json({
        ok: true,
        action,
        bridge: materializeBridges(runtimeStore).find((entry) => entry.id === bridge.id),
      });
    }

    if (action !== "test" && action !== "activate") {
      return NextResponse.json(
        {
          ok: false,
          error: "unsupported_action",
          supported_actions: ["test", "activate", "deactivate", "test_all"],
        },
        { status: 400 },
      );
    }

    const health = await testBridgeConnectivity(bridge);
    const current = runtimeStore[bridge.id];
    const shouldActivate = action === "activate" && health.status === "healthy";
    const nextState: BridgeState = shouldActivate
      ? "active"
      : action === "activate"
        ? "offline"
        : current?.state || bridge.state;

    runtimeStore[bridge.id] = {
      state: nextState,
      health,
      last_activation_at: shouldActivate
        ? new Date().toISOString()
        : current?.last_activation_at,
      last_error: health.status === "healthy" ? undefined : health.detail,
    };

    await appendBridgeAudit(repoRoot, {
      ts: new Date().toISOString(),
      action,
      bridge_id: bridge.id,
      repo: bridge.repo,
      operator,
      state_before: current?.state || bridge.state,
      state_after: nextState,
      health,
      activation_succeeded: shouldActivate,
    });

    await saveBridgeRuntimeStore(repoRoot, runtimeStore);

    const updated = materializeBridges(runtimeStore).find((entry) => entry.id === bridge.id);
    if (action === "activate" && !shouldActivate) {
      return NextResponse.json(
        {
          ok: false,
          error: "bridge_activation_failed_health_check",
          bridge: updated,
        },
        { status: 409 },
      );
    }

    return NextResponse.json({
      ok: true,
      action,
      bridge: updated,
    });
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        error: "ls_status_action_failed",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}
