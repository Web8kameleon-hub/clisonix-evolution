/* Industrial AGI Core – real-data orchestrator (no mock)
   - Bootstraps logger, memory store (atomic), metrics, modules
   - Routes inputs to Sense/Mind, executes via Commander
   - Strict config via env; zero fake generators
*/
import { promises as fs } from "node:fs";
import { dirname, join } from "pathe";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { setTimeout as sleep } from "node:timers/promises";
import os from "node:os";
import crypto from "node:crypto";
import pino from "pino";
import { z } from "zod";
import { Mind } from "./mind";
import { Sense } from "./sense";
import { Commander } from "./commander";
import fastGlob from "fast-glob";
import { Counter, Gauge, Registry, collectDefaultMetrics } from "prom-client";

const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// -------- Config (strict) --------
const ConfigSchema = z.object({
    NODE_ENV: z.enum(["development", "production"]).default("production"),
    AGI_DATA_DIR: z.string().default(join(__dirname, "..", "..", "data")),
    AGI_MEMORY_FILE: z.string().default(join(__dirname, "..", "..", "data", "memory.json")),
    AGI_LOG_LEVEL: z.enum(["fatal", "error", "warn", "info", "debug", "trace"]).default("info"),
    AGI_COMMAND_WHITELIST: z.string().default("ffprobe,python,python3,sox,soxi,ls,dir,powershell"),
    AGI_NET_TIMEOUT_MS: z.coerce.number().default(10000),
    AGI_DISABLE_NETWORK: z.enum(["0", "1"]).default("0"), // if "1", Commander.fetch is disabled
});
type Config = z.infer<typeof ConfigSchema>;
const cfg: Config = ConfigSchema.parse(process.env);

// -------- Logger --------
export const logger = pino({
    level: cfg.AGI_LOG_LEVEL,
    base: { svc: "web8-agi" },
});

// -------- Registry / Metrics (real OS metrics) --------
const registry = new Registry();
collectDefaultMetrics({ register: registry });
const jobsCounter = new Counter({ name: "agi_jobs_total", help: "AGI jobs total", registers: [registry] });
const errCounter = new Counter({ name: "agi_errors_total", help: "AGI errors total", registers: [registry] });
const memGauge = new Gauge({ name: "agi_memory_entries", help: "AGI memory items", registers: [registry] });

// -------- Atomic JSON store --------
async function ensureDir(p: string) {
    await fs.mkdir(p, { recursive: true });
}
async function atomicWriteJSON(path: string, data: unknown) {
    const tmp = `${path}.${process.pid}.${Date.now()}.tmp`;
    await fs.writeFile(tmp, JSON.stringify(data, null, 2), "utf-8");
    await fs.rename(tmp, path);
}
async function readJSON<T>(path: string, fallback: T): Promise<T> {
    try {
        const raw = await fs.readFile(path, "utf-8");
        return JSON.parse(raw) as T;
    } catch {
        return fallback;
    }
}

export type MemoryEntry = {
    id: string;             // identifier (cryptographically strong; ID ≠ “data”)
    ts: string;             // ISO timestamp
    kind: "text" | "file" | "event" | "decision";
    tags: string[];
    source: string;         // e.g., "sense:text", "sense:file", "system", "commander"
    payload: unknown;       // raw data reference/summary (never fake)
};

type MemoryState = {
    version: 1;
    entries: MemoryEntry[];
};

export class AGICore {
    private static _instance: AGICore | null = null;
    public readonly config: Config;
    public readonly memoryFile: string;
    public state: MemoryState;
    public readonly sense: Sense;
    public readonly mind: Mind;
    public readonly commander: Commander;

    private constructor(config: Config) {
        this.config = config;
        this.memoryFile = config.AGI_MEMORY_FILE;
        this.state = { version: 1, entries: [] };
        this.sense = new Sense({ logger, cfg: this.config });
        this.mind = new Mind({ logger, cfg: this.config });
        this.commander = new Commander({ logger, cfg: this.config });
    }

    static async init(): Promise<AGICore> {
        if (this._instance) return this._instance;
        const core = new AGICore(cfg);

        // prepare storage
        await ensureDir(dirname(core.memoryFile));
        core.state = await readJSON<MemoryState>(core.memoryFile, { version: 1, entries: [] });
        memGauge.set(core.state.entries.length);

        logger.info({ dataDir: cfg.AGI_DATA_DIR, memoryFile: cfg.AGI_MEMORY_FILE }, "AGI core initialized");

        // preload: scan real files under data dir (no mock) to index
        try {
            const patterns = ["**/*.wav", "**/*.edf", "**/*.bdf", "**/*.txt", "**/*.json"];
            const files = await fastGlob(patterns, { cwd: cfg.AGI_DATA_DIR, dot: false, absolute: true });
            if (files.length) {
                await core.remember({
                    id: crypto.randomUUID(),
                    ts: new Date().toISOString(),
                    kind: "event",
                    tags: ["bootstrap", "index"],
                    source: "system:indexer",
                    payload: { indexed: files.length },
                });
            }
        } catch (e) {
            errCounter.inc();
            logger.warn({ err: String(e) }, "indexer warning");
        }

        this._instance = core;
        return core;
    }

    async remember(entry: MemoryEntry) {
        this.state.entries.push(entry);
        memGauge.set(this.state.entries.length);
        await atomicWriteJSON(this.memoryFile, this.state);
    }

    // ---- Public API (call from your REST layer) ----

    /** Ingest real text (from UI/API). */
    async ingestText(input: { text: string; meta?: Record<string, unknown> }) {
        jobsCounter.inc();
        const sensed = await this.sense.fromText(input.text);
        await this.remember({
            id: crypto.randomUUID(),
            ts: new Date().toISOString(),
            kind: "text",
            tags: ["input", "text", ...sensed.tags],
            source: "sense:text",
            payload: { features: sensed, meta: input.meta ?? {} },
        });

        const plan = await this.mind.plan(sensed);
        await this.remember({
            id: crypto.randomUUID(),
            ts: new Date().toISOString(),
            kind: "decision",
            tags: ["plan"],
            source: "mind:plan",
            payload: plan,
        });

        return { sensed, plan };
    }

    /** Ingest a real file path (WAV/EDF/TXT…). No reading = no record. */
    async ingestFile(path: string) {
        jobsCounter.inc();
        const sensed = await this.sense.fromFile(path);
        await this.remember({
            id: crypto.randomUUID(),
            ts: new Date().toISOString(),
            kind: "file",
            tags: ["input", "file", ...sensed.tags],
            source: "sense:file",
            payload: { summary: sensed.summary, meta: sensed.meta },
        });

        const plan = await this.mind.plan({
            tags: sensed.tags,
            tokens: Math.max(1, Math.round((sensed.features.lineCount ?? 1) * 8)),
            chars: (sensed.features.sample ?? sensed.summary).length,
            languageHint: "unknown",
            sentiment: "neutral",
            keywords: sensed.tags,
            modality: sensed.modality,
        });
        await this.remember({
            id: crypto.randomUUID(),
            ts: new Date().toISOString(),
            kind: "decision",
            tags: ["plan"],
            source: "mind:plan",
            payload: plan,
        });

        return { sensed, plan };
    }

    /** Execute a real command via Commander (whitelist only). */
    async act(command: { type: string; params?: Record<string, unknown> }) {
        jobsCounter.inc();
        const result = await this.commander.execute(command);
        await this.remember({
            id: crypto.randomUUID(),
            ts: new Date().toISOString(),
            kind: "event",
            tags: ["act", command.type],
            source: "commander",
            payload: { result },
        });
        return result;
    }

    /** System status (real OS metrics). */
    status() {
        const mem = process.memoryUsage();
        return {
            time: new Date().toISOString(),
            pid: process.pid,
            node: process.versions.node,
            platform: process.platform,
            arch: process.arch,
            cpus: os.cpus().length,
            loadavg: os.loadavg(),
            mem: {
                rss: mem.rss, heapTotal: mem.heapTotal, heapUsed: mem.heapUsed, external: mem.external,
            },
            dataDir: this.config.AGI_DATA_DIR,
            entries: this.state.entries.length,
        };
    }

    async metrics(): Promise<string> {
        return registry.metrics();
    }
}

// Optional: quick self-test (no mock; only probes real process/env)
if (process.env.AGI_SELFTEST === "1") {
    (async () => {
        const core = await AGICore.init();
        logger.info(core.status(), "selftest-status");
    })().catch(e => {
        logger.error({ err: String(e) }, "selftest failed");
        process.exitCode = 1;
    });
}
