import { mkdir, open, readFile } from "node:fs/promises";
import path from "node:path";

const CSP_REPORT_LOG_PATH = path.join(
  process.cwd(),
  "logs",
  "security",
  "csp-reports.jsonl",
);

export type StoredCspReport = {
  documentUri: string | null;
  violatedDirective: string | null;
  effectiveDirective: string | null;
  blockedUri: string | null;
  sourceFile: string | null;
  disposition: string | null;
  originalPolicy: string | null;
  userAgent: string | null;
  receivedAt: string;
};

async function ensureLogDir() {
  await mkdir(path.dirname(CSP_REPORT_LOG_PATH), { recursive: true });
}

export async function appendCspReport(report: StoredCspReport) {
  await ensureLogDir();
  const handle = await open(CSP_REPORT_LOG_PATH, "a");
  try {
    await handle.write(`${JSON.stringify(report)}\n`);
  } finally {
    await handle.close();
  }
}

export async function readRecentCspReports(
  limit = 20,
): Promise<StoredCspReport[]> {
  if (limit <= 0) return [];

  try {
    const raw = await readFile(CSP_REPORT_LOG_PATH, "utf-8");
    return raw
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean)
      .slice(-limit)
      .reverse()
      .map((line) => JSON.parse(line) as StoredCspReport);
  } catch {
    return [];
  }
}
