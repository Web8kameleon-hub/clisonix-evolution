import { NextResponse } from "next/server";
import { readFileSync, existsSync, readdirSync } from "fs";
import { join } from "path";

const JOBS_DIR =
  process.env.KITCHEN_JOBS_DIR || join(process.cwd(), "kitchen-jobs");

interface Props {
  params: Promise<{ runId: string }>;
}

/**
 * GET /api/kitchen/status/[runId]
 *
 * Returns the status of a test run job
 */
export async function GET(req: Request, { params }: Props) {
  const { runId } = await params;

  if (!runId || runId.length < 10) {
    return NextResponse.json({ error: "Invalid runId" }, { status: 400 });
  }

  // Check for completed job
  const doneFile = join(JOBS_DIR, `${runId}.done.json`);
  if (existsSync(doneFile)) {
    try {
      const status = JSON.parse(readFileSync(doneFile, "utf8"));
      return NextResponse.json({
        ...status,
        phase: "completed",
      });
    } catch (e) {
      return NextResponse.json(
        { error: "Failed to read status file", detail: String(e) },
        { status: 500 },
      );
    }
  }

  // Check for running job
  const runningFile = join(JOBS_DIR, `${runId}.running.json`);
  if (existsSync(runningFile)) {
    try {
      const status = JSON.parse(readFileSync(runningFile, "utf8"));
      const startedAt = new Date(status.startedAt);
      const elapsedSeconds = Math.round(
        (Date.now() - startedAt.getTime()) / 1000,
      );

      return NextResponse.json({
        runId,
        status: "running",
        phase: "running",
        startedAt: status.startedAt,
        elapsedSeconds,
        collection: status.collection,
        baseUrl: status.baseUrl,
      });
    } catch {
      return NextResponse.json({
        runId,
        status: "running",
        phase: "running",
      });
    }
  }

  // Check for queued job
  const queuedFile = join(JOBS_DIR, `${runId}.json`);
  if (existsSync(queuedFile)) {
    try {
      const job = JSON.parse(readFileSync(queuedFile, "utf8"));

      // Calculate queue position
      const allJobs = readdirSync(JOBS_DIR)
        .filter(
          (f) =>
            f.endsWith(".json") &&
            !f.includes(".done") &&
            !f.includes(".running"),
        )
        .map((f) => {
          try {
            const content = JSON.parse(readFileSync(join(JOBS_DIR, f), "utf8"));
            return {
              file: f,
              createdAt: content.createdAt,
              priority: content.priority || 5,
            };
          } catch {
            return null;
          }
        })
        .filter(Boolean)
        .sort((a, b) => {
          if (b!.priority !== a!.priority) return b!.priority - a!.priority;
          return (
            new Date(a!.createdAt).getTime() - new Date(b!.createdAt).getTime()
          );
        });

      const position =
        allJobs.findIndex((j) => j?.file === `${runId}.json`) + 1;

      return NextResponse.json({
        runId,
        status: "queued",
        phase: "queued",
        queuePosition: position,
        estimatedWait: `${position * 2} minutes`,
        collection: job.collection,
        baseUrl: job.baseUrl,
        createdAt: job.createdAt,
      });
    } catch {
      return NextResponse.json({
        runId,
        status: "queued",
        phase: "queued",
      });
    }
  }

  // Job not found
  return NextResponse.json(
    {
      error: "Job not found",
      runId,
      message: "The requested job ID does not exist or has expired",
    },
    { status: 404 },
  );
}
