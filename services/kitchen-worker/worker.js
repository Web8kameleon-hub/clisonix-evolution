/**
 * Kitchen Worker - Newman Test Runner
 *
 * Polls kitchen-jobs directory for job files, runs newman CLI,
 * and writes HTML reports to kitchen-reports directory.
 *
 * Requirements:
 *  - npm install newman newman-reporter-htmlextra
 *  - In production, replace filesystem queue with Redis/RabbitMQ
 *
 * Environment Variables:
 *  - KITCHEN_JOBS_DIR: Path to jobs directory (default: ./kitchen-jobs)
 *  - KITCHEN_REPORTS_DIR: Path to reports directory (default: ./kitchen-reports)
 *  - POLL_INTERVAL_MS: Polling interval in ms (default: 3000)
 *  - COLLECTIONS_DIR: Path to Postman collections (default: ./postman-collections)
 */

const { exec, spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

// Configuration
const JOBS_DIR =
  process.env.KITCHEN_JOBS_DIR || path.resolve(process.cwd(), "kitchen-jobs");
const REPORTS_DIR =
  process.env.KITCHEN_REPORTS_DIR ||
  path.resolve(process.cwd(), "kitchen-reports");
const COLLECTIONS_DIR =
  process.env.COLLECTIONS_DIR ||
  path.resolve(process.cwd(), "postman-collections");
const POLL_INTERVAL = parseInt(process.env.POLL_INTERVAL_MS || "3000", 10);
const MAX_CONCURRENT_JOBS = parseInt(
  process.env.MAX_CONCURRENT_JOBS || "2",
  10,
);

// State
let runningJobs = 0;
let processedJobs = 0;
let failedJobs = 0;

// Ensure directories exist
function ensureDirectories() {
  [JOBS_DIR, REPORTS_DIR].forEach((dir) => {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      console.log(`[worker] Created directory: ${dir}`);
    }
  });
}

// Get pending job files sorted by priority and creation time
function getPendingJobs() {
  try {
    const files = fs
      .readdirSync(JOBS_DIR)
      .filter(
        (f) =>
          f.endsWith(".json") &&
          !f.includes(".done") &&
          !f.includes(".running"),
      );

    // Read and sort by priority
    const jobs = files
      .map((file) => {
        try {
          const content = fs.readFileSync(path.join(JOBS_DIR, file), "utf8");
          const job = JSON.parse(content);
          return { file, job };
        } catch (e) {
          console.error(`[worker] Failed to read job file ${file}:`, e.message);
          return null;
        }
      })
      .filter(Boolean);

    // Sort by priority (higher first) then by creation time (older first)
    jobs.sort((a, b) => {
      if ((b.job.priority || 5) !== (a.job.priority || 5)) {
        return (b.job.priority || 5) - (a.job.priority || 5);
      }
      return (
        new Date(a.job.createdAt).getTime() -
        new Date(b.job.createdAt).getTime()
      );
    });

    return jobs;
  } catch (e) {
    console.error("[worker] Failed to read jobs directory:", e.message);
    return [];
  }
}

// Run a single job
async function runJob(jobFile, job) {
  const runId = job.runId;
  const collection = job.collectionPath || job.collection;
  const baseUrl = job.baseUrl;

  console.log(`\n${"=".repeat(60)}`);
  console.log(`[worker] Starting job ${runId}`);
  console.log(`[worker] Collection: ${collection}`);
  console.log(`[worker] Base URL: ${baseUrl}`);
  console.log(`[worker] Environment: ${job.environment || "default"}`);
  console.log(`${"=".repeat(60)}\n`);

  // Mark job as running
  const runningFile = path.join(JOBS_DIR, `${runId}.running.json`);
  const startTime = new Date().toISOString();
  fs.writeFileSync(
    runningFile,
    JSON.stringify(
      {
        ...job,
        status: "running",
        startedAt: startTime,
      },
      null,
      2,
    ),
  );

  // Prepare report paths
  const reportFile = path.join(REPORTS_DIR, `${runId}.html`);
  const jsonReportFile = path.join(REPORTS_DIR, `${runId}.json`);

  // Resolve collection path
  let collectionPath = collection;
  if (!path.isAbsolute(collectionPath)) {
    // Try collections directory first
    const inCollections = path.join(COLLECTIONS_DIR, collection);
    const inCwd = path.join(process.cwd(), collection);

    if (fs.existsSync(inCollections)) {
      collectionPath = inCollections;
    } else if (fs.existsSync(inCwd)) {
      collectionPath = inCwd;
    }
  }

  // Build newman command
  const args = [
    "run",
    collectionPath,
    "--env-var",
    `base_url=${baseUrl}`,
    "--reporters",
    "cli,htmlextra,json",
    "--reporter-htmlextra-export",
    reportFile,
    "--reporter-json-export",
    jsonReportFile,
    "--suppress-exit-code",
    "--timeout-request",
    "30000",
    "--delay-request",
    "100",
  ];

  // Add environment file if specified
  if (job.environment && job.environmentFile) {
    args.push("--environment", job.environmentFile);
  }

  return new Promise((resolve) => {
    const startMs = Date.now();

    // Use npx newman for cross-platform compatibility
    const newman = spawn("npx", ["newman", ...args], {
      cwd: process.cwd(),
      shell: true,
      maxBuffer: 1024 * 1024 * 50, // 50MB buffer
    });

    let stdout = "";
    let stderr = "";

    newman.stdout.on("data", (data) => {
      const text = data.toString();
      stdout += text;
      process.stdout.write(text);
    });

    newman.stderr.on("data", (data) => {
      const text = data.toString();
      stderr += text;
      process.stderr.write(text);
    });

    newman.on("close", (code) => {
      const endTime = new Date().toISOString();
      const durationMs = Date.now() - startMs;
      const durationSec = (durationMs / 1000).toFixed(2);

      // Parse JSON report for summary
      let summary = null;
      try {
        if (fs.existsSync(jsonReportFile)) {
          const jsonReport = JSON.parse(
            fs.readFileSync(jsonReportFile, "utf8"),
          );
          summary = {
            totalRequests: jsonReport.run?.stats?.requests?.total || 0,
            failedRequests: jsonReport.run?.stats?.requests?.failed || 0,
            totalAssertions: jsonReport.run?.stats?.assertions?.total || 0,
            failedAssertions: jsonReport.run?.stats?.assertions?.failed || 0,
            totalDuration: jsonReport.run?.timings?.completed || durationMs,
          };
        }
      } catch (e) {
        console.error("[worker] Failed to parse JSON report:", e.message);
      }

      // Write completion status
      const statusFile = path.join(JOBS_DIR, `${runId}.done.json`);
      const status = {
        runId,
        collection,
        baseUrl,
        environment: job.environment,
        status: code === 0 ? "completed" : "completed_with_errors",
        exitCode: code,
        startedAt: startTime,
        completedAt: endTime,
        durationSeconds: parseFloat(durationSec),
        summary,
        error: code !== 0 ? `Exit code: ${code}` : null,
        reports: {
          html: `/api/kitchen/reports/${runId}`,
          json: `/api/kitchen/reports/${runId}?format=json`,
        },
      };

      fs.writeFileSync(statusFile, JSON.stringify(status, null, 2));

      // Clean up job files
      try {
        fs.unlinkSync(path.join(JOBS_DIR, jobFile));
        fs.unlinkSync(runningFile);
      } catch (e) {
        // Ignore cleanup errors
      }

      if (code === 0) {
        processedJobs++;
        console.log(
          `\n[worker] ✅ Job ${runId} completed successfully in ${durationSec}s`,
        );
      } else {
        failedJobs++;
        console.log(
          `\n[worker] ⚠️ Job ${runId} completed with errors (exit code: ${code})`,
        );
      }

      if (summary) {
        console.log(
          `[worker] Summary: ${summary.totalRequests} requests, ${summary.failedRequests} failed`,
        );
        console.log(
          `[worker] Assertions: ${summary.totalAssertions} total, ${summary.failedAssertions} failed`,
        );
      }
      console.log(`[worker] Report: ${reportFile}\n`);

      resolve(status);
    });

    newman.on("error", (err) => {
      console.error(`[worker] ❌ Failed to start newman:`, err.message);

      const statusFile = path.join(JOBS_DIR, `${runId}.done.json`);
      fs.writeFileSync(
        statusFile,
        JSON.stringify(
          {
            runId,
            status: "failed",
            error: err.message,
            completedAt: new Date().toISOString(),
          },
          null,
          2,
        ),
      );

      try {
        fs.unlinkSync(path.join(JOBS_DIR, jobFile));
        fs.unlinkSync(runningFile);
      } catch (e) {}

      failedJobs++;
      resolve(null);
    });
  });
}

// Main polling function
async function poll() {
  if (runningJobs >= MAX_CONCURRENT_JOBS) {
    return;
  }

  const pendingJobs = getPendingJobs();
  if (pendingJobs.length === 0) {
    return;
  }

  // Take next job
  const { file, job } = pendingJobs[0];
  runningJobs++;

  try {
    await runJob(file, job);
  } catch (e) {
    console.error(`[worker] Unexpected error processing job:`, e);
    failedJobs++;
  } finally {
    runningJobs--;
  }
}

// Health check endpoint (for Docker healthcheck)
function startHealthServer() {
  const http = require("http");
  const PORT = process.env.HEALTH_PORT || 3100;

  const server = http.createServer((req, res) => {
    if (req.url === "/health" || req.url === "/") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(
        JSON.stringify({
          status: "healthy",
          service: "kitchen-worker",
          uptime: process.uptime(),
          stats: {
            processedJobs,
            failedJobs,
            runningJobs,
            pendingJobs: getPendingJobs().length,
          },
          config: {
            pollInterval: POLL_INTERVAL,
            maxConcurrentJobs: MAX_CONCURRENT_JOBS,
            jobsDir: JOBS_DIR,
            reportsDir: REPORTS_DIR,
          },
        }),
      );
    } else if (req.url === "/stats") {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(
        JSON.stringify({
          processedJobs,
          failedJobs,
          runningJobs,
          pendingJobs: getPendingJobs().length,
          uptime: process.uptime(),
        }),
      );
    } else {
      res.writeHead(404);
      res.end("Not Found");
    }
  });

  server.listen(PORT, () => {
    console.log(`[worker] Health endpoint listening on port ${PORT}`);
  });
}

// Startup
console.log("\n" + "=".repeat(60));
console.log("  🍳 Kitchen Worker - Newman Test Runner");
console.log("=".repeat(60));
console.log(`  Jobs Directory:    ${JOBS_DIR}`);
console.log(`  Reports Directory: ${REPORTS_DIR}`);
console.log(`  Collections Dir:   ${COLLECTIONS_DIR}`);
console.log(`  Poll Interval:     ${POLL_INTERVAL}ms`);
console.log(`  Max Concurrent:    ${MAX_CONCURRENT_JOBS}`);
console.log("=".repeat(60) + "\n");

ensureDirectories();
startHealthServer();

// Start polling
setInterval(poll, POLL_INTERVAL);
console.log("[worker] Started polling for jobs...\n");

// Graceful shutdown
process.on("SIGTERM", () => {
  console.log("\n[worker] Received SIGTERM, shutting down gracefully...");
  process.exit(0);
});

process.on("SIGINT", () => {
  console.log("\n[worker] Received SIGINT, shutting down gracefully...");
  process.exit(0);
});
