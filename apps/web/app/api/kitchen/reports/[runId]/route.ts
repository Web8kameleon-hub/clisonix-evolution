import { NextResponse } from "next/server";
import { readFileSync, existsSync } from "fs";
import { join } from "path";

const REPORTS_DIR =
  process.env.KITCHEN_REPORTS_DIR || join(process.cwd(), "kitchen-reports");

interface Props {
  params: Promise<{ runId: string }>;
}

/**
 * GET /api/kitchen/reports/[runId]
 *
 * Returns the HTML or JSON report for a completed test run
 *
 * Query params:
 *   - format: "html" (default) or "json"
 */
export async function GET(req: Request, { params }: Props) {
  const { runId } = await params;
  const url = new URL(req.url);
  const format = url.searchParams.get("format") || "html";

  if (!runId || runId.length < 10) {
    return NextResponse.json({ error: "Invalid runId" }, { status: 400 });
  }

  // Sanitize runId to prevent path traversal
  const sanitizedRunId = runId.replace(/[^a-zA-Z0-9-]/g, "");
  if (sanitizedRunId !== runId) {
    return NextResponse.json(
      { error: "Invalid runId format" },
      { status: 400 },
    );
  }

  const extension = format === "json" ? "json" : "html";
  const reportFile = join(REPORTS_DIR, `${sanitizedRunId}.${extension}`);

  if (!existsSync(reportFile)) {
    // Check if job is still running or queued
    const JOBS_DIR =
      process.env.KITCHEN_JOBS_DIR || join(process.cwd(), "kitchen-jobs");
    const runningFile = join(JOBS_DIR, `${sanitizedRunId}.running.json`);
    const queuedFile = join(JOBS_DIR, `${sanitizedRunId}.json`);

    if (existsSync(runningFile)) {
      return NextResponse.json(
        {
          error: "Report not ready",
          status: "running",
          message: "The test is still running. Please check back later.",
          statusUrl: `/api/kitchen/status/${sanitizedRunId}`,
        },
        { status: 202 },
      );
    }

    if (existsSync(queuedFile)) {
      return NextResponse.json(
        {
          error: "Report not ready",
          status: "queued",
          message: "The test is still in queue. Please check back later.",
          statusUrl: `/api/kitchen/status/${sanitizedRunId}`,
        },
        { status: 202 },
      );
    }

    return NextResponse.json(
      {
        error: "Report not found",
        runId: sanitizedRunId,
        message: "The requested report does not exist or has expired",
      },
      { status: 404 },
    );
  }

  try {
    const content = readFileSync(reportFile, "utf8");

    if (format === "json") {
      return NextResponse.json(JSON.parse(content));
    }

    // Return HTML report with proper content type
    return new NextResponse(content, {
      status: 200,
      headers: {
        "Content-Type": "text/html; charset=utf-8",
        "Cache-Control": "public, max-age=3600",
        "X-Report-Id": sanitizedRunId,
      },
    });
  } catch (e) {
    console.error(`[kitchen] Error reading report ${sanitizedRunId}:`, e);
    return NextResponse.json(
      { error: "Failed to read report", detail: String(e) },
      { status: 500 },
    );
  }
}
