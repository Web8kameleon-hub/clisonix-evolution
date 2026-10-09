import { NextResponse } from "next/server";
import { readdirSync, readFileSync, existsSync } from "fs";
import { join } from "path";

const JOBS_DIR =
  process.env.KITCHEN_JOBS_DIR || join(process.cwd(), "kitchen-jobs");

interface QueueItem {
  runId: string;
  status: "queued" | "running" | "completed" | "failed";
  collection?: string;
  baseUrl?: string;
  createdAt?: string;
  startedAt?: string;
  completedAt?: string;
  priority?: number;
}

/**
 * GET /api/kitchen/queue
 *
 * Returns current queue status including queued, running, and recent completed jobs
 */
export async function GET() {
  try {
    if (!existsSync(JOBS_DIR)) {
      return NextResponse.json({
        queued: [],
        running: [],
        recentCompleted: [],
        stats: {
          queuedCount: 0,
          runningCount: 0,
          completedToday: 0,
        },
      });
    }

    const files = readdirSync(JOBS_DIR);

    // Categorize jobs
    const queued: QueueItem[] = [];
    const running: QueueItem[] = [];
    const completed: QueueItem[] = [];

    for (const file of files) {
      try {
        const filePath = join(JOBS_DIR, file);
        const content = JSON.parse(readFileSync(filePath, "utf8"));

        if (file.endsWith(".done.json")) {
          completed.push({
            runId: content.runId,
            status: content.status === "failed" ? "failed" : "completed",
            collection: content.collection,
            baseUrl: content.baseUrl,
            completedAt: content.completedAt,
            createdAt: content.createdAt,
          });
        } else if (file.endsWith(".running.json")) {
          running.push({
            runId: content.runId,
            status: "running",
            collection: content.collection,
            baseUrl: content.baseUrl,
            startedAt: content.startedAt,
            createdAt: content.createdAt,
          });
        } else if (
          file.endsWith(".json") &&
          !file.includes(".done") &&
          !file.includes(".running")
        ) {
          queued.push({
            runId: content.runId,
            status: "queued",
            collection: content.collection,
            baseUrl: content.baseUrl,
            createdAt: content.createdAt,
            priority: content.priority || 5,
          });
        }
      } catch (e) {
        // Skip malformed files
        console.error(`[kitchen] Failed to parse ${file}:`, e);
      }
    }

    // Sort queued by priority and creation time
    queued.sort((a, b) => {
      if ((b.priority || 5) !== (a.priority || 5)) {
        return (b.priority || 5) - (a.priority || 5);
      }
      return (
        new Date(a.createdAt || 0).getTime() -
        new Date(b.createdAt || 0).getTime()
      );
    });

    // Sort completed by completion time (most recent first)
    completed.sort(
      (a, b) =>
        new Date(b.completedAt || 0).getTime() -
        new Date(a.completedAt || 0).getTime(),
    );

    // Count completed today
    const today = new Date().toISOString().split("T")[0];
    const completedToday = completed.filter((j) =>
      j.completedAt?.startsWith(today),
    ).length;

    return NextResponse.json({
      queued,
      running,
      recentCompleted: completed.slice(0, 20), // Last 20 completed jobs
      stats: {
        queuedCount: queued.length,
        runningCount: running.length,
        completedToday,
        totalCompleted: completed.length,
      },
    });
  } catch (e) {
    console.error("[kitchen] Error reading queue:", e);
    return NextResponse.json(
      { error: "Failed to read queue", detail: String(e) },
      { status: 500 },
    );
  }
}
