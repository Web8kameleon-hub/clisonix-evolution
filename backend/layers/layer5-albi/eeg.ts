import { spawn } from "child_process";
import { AppConfig } from "../../config";
import fs from "fs";
import path from "path";

const ALLOWED_INPUT_DIRS = [
  path.resolve(process.cwd(), "data"),
  path.resolve(process.cwd(), "uploads"),
  path.resolve("/tmp/clisonix"),
];

const ALLOWED_EXTENSIONS = new Set([".edf", ".bdf", ".csv", ".json", ".txt"]);
const MAX_FILE_SIZE_BYTES = Number(
  process.env.ALBI_EEG_MAX_FILE_SIZE_BYTES ?? 100 * 1024 * 1024,
);
const PROCESS_TIMEOUT_MS = Number(process.env.ALBI_EEG_TIMEOUT_MS ?? 30_000);
const MAX_RETRIES = Math.max(0, Number(process.env.ALBI_EEG_MAX_RETRIES ?? 1));
const RETRY_BACKOFF_MS = Math.max(
  100,
  Number(process.env.ALBI_EEG_RETRY_BACKOFF_MS ?? 400),
);

type EegAnalyzeResult = {
  ok: boolean;
  dominant_hz?: number;
  bands?: Record<string, number>;
  detail?: unknown;
};

type EegProcessResult = {
  ok: boolean;
  dominant_hz?: number;
  bands?: Record<string, number>;
  detail?: unknown;
  durationMs: number;
  attempt: number;
};

function isPathSafe(filePath: string): boolean {
  const resolvedPath = path.resolve(filePath);

  return ALLOWED_INPUT_DIRS.some((baseDir) => {
    const relative = path.relative(baseDir, resolvedPath);
    return (
      relative !== "" &&
      !relative.startsWith("..") &&
      !path.isAbsolute(relative)
    );
  });
}

function shouldCleanupTempFile(filePath: string): boolean {
  const normalized = path.resolve(filePath);
  return (
    normalized.includes(`${path.sep}uploads${path.sep}`) ||
    normalized.startsWith(path.resolve("/tmp/clisonix"))
  );
}

function sanitizeErrorText(text: string): string {
  return text.replace(/\s+/g, " ").trim().slice(0, 1200);
}

function logEvent(
  level: "info" | "warn" | "error",
  event: string,
  payload: Record<string, unknown>,
) {
  const record = {
    ts: new Date().toISOString(),
    event,
    ...payload,
  };

  const message = `[ALBI_EEG] ${JSON.stringify(record)}`;
  if (level === "error") {
    console.error(message);
    return;
  }
  if (level === "warn") {
    console.warn(message);
    return;
  }
  console.info(message);
}

function validateInputFile(filePath: string): { ok: boolean; reason?: string } {
  if (!isPathSafe(filePath)) {
    return {
      ok: false,
      reason: "Access denied: path outside allowed directories",
    };
  }

  if (!fs.existsSync(filePath)) {
    return { ok: false, reason: "File not found" };
  }

  const ext = path.extname(filePath).toLowerCase();
  if (!ALLOWED_EXTENSIONS.has(ext)) {
    return {
      ok: false,
      reason: `Unsupported file extension: ${ext || "(none)"}`,
    };
  }

  try {
    const stat = fs.statSync(filePath);
    if (!stat.isFile()) {
      return { ok: false, reason: "Path is not a regular file" };
    }

    if (stat.size <= 0) {
      return { ok: false, reason: "File is empty" };
    }

    if (stat.size > MAX_FILE_SIZE_BYTES) {
      return {
        ok: false,
        reason: `File too large (${stat.size} bytes). Max allowed: ${MAX_FILE_SIZE_BYTES} bytes`,
      };
    }
  } catch (err) {
    return {
      ok: false,
      reason: `Cannot read file metadata: ${err instanceof Error ? err.message : "unknown error"}`,
    };
  }

  return { ok: true };
}

async function runPythonAttempt(
  cfg: AppConfig,
  filePath: string,
  attempt: number,
): Promise<EegProcessResult> {
  const startedAt = Date.now();

  return new Promise((resolve) => {
    let settled = false;

    const finish = (
      result: Omit<EegProcessResult, "durationMs" | "attempt">,
    ) => {
      if (settled) return;
      settled = true;
      resolve({ ...result, durationMs: Date.now() - startedAt, attempt });
    };

    const pythonBin = cfg.PYTHON || "python";
    const scriptPath = cfg.MNE_SCRIPT || "./python/eeg_process.py";
    const py = spawn(pythonBin, [scriptPath, filePath], {
      stdio: ["ignore", "pipe", "pipe"],
    });

    let out = "";
    let err = "";

    py.stdout.on("data", (chunk: Buffer) => {
      out += chunk.toString();
    });

    py.stderr.on("data", (chunk: Buffer) => {
      err += chunk.toString();
    });

    py.on("error", (spawnErr: Error) => {
      finish({
        ok: false,
        detail: `Failed to spawn Python process: ${spawnErr.message}`,
      });
    });

    const timeout = setTimeout(() => {
      py.kill();
      finish({
        ok: false,
        detail: `Processing timeout (${PROCESS_TIMEOUT_MS}ms)`,
      });
    }, PROCESS_TIMEOUT_MS);

    py.on("close", (code) => {
      clearTimeout(timeout);

      try {
        if (code !== 0) {
          return finish({
            ok: false,
            detail: `Python exit code: ${code}, stderr: ${sanitizeErrorText(err) || "(empty)"}`,
          });
        }

        const parsed = JSON.parse(out);
        return finish({
          ok: true,
          dominant_hz: parsed.dominant_hz,
          bands: parsed.bands,
          detail: parsed,
        });
      } catch {
        return finish({
          ok: false,
          detail: sanitizeErrorText(
            err || out || "Failed to parse Python output",
          ),
        });
      }
    });
  });
}

export async function eegAnalyze(
  cfg: AppConfig,
  filePath: string,
): Promise<EegAnalyzeResult> {
  const validation = validateInputFile(filePath);
  if (!validation.ok) {
    return { ok: false, detail: validation.reason };
  }

  const startedAt = Date.now();
  const attempts = MAX_RETRIES + 1;
  let lastError: unknown = "Unknown EEG processing error";

  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    const result = await runPythonAttempt(cfg, filePath, attempt);

    logEvent(result.ok ? "info" : "warn", "eeg_process_attempt", {
      filePath,
      attempt,
      maxAttempts: attempts,
      ok: result.ok,
      durationMs: result.durationMs,
      dominantHz: result.dominant_hz ?? null,
      error: result.ok ? null : result.detail,
    });

    if (result.ok) {
      if (shouldCleanupTempFile(filePath)) {
        fs.unlink(filePath, () => {});
      }

      return {
        ok: true,
        dominant_hz: result.dominant_hz,
        bands: result.bands,
        detail: {
          ...(typeof result.detail === "object" && result.detail !== null
            ? result.detail
            : { raw: result.detail }),
          telemetry: {
            totalDurationMs: Date.now() - startedAt,
            attemptsUsed: attempt,
          },
        },
      };
    }

    lastError = result.detail;
    if (attempt < attempts) {
      await new Promise((resolve) =>
        setTimeout(resolve, RETRY_BACKOFF_MS * attempt),
      );
    }
  }

  if (shouldCleanupTempFile(filePath)) {
    fs.unlink(filePath, () => {});
  }

  logEvent("error", "eeg_process_failed", {
    filePath,
    totalDurationMs: Date.now() - startedAt,
    attempts: attempts,
    error: lastError,
  });

  return {
    ok: false,
    detail: {
      message: "EEG processing failed after retries",
      error: lastError,
      telemetry: {
        totalDurationMs: Date.now() - startedAt,
        attempts,
      },
    },
  };
}
