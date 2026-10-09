const { spawn } = require("node:child_process");
const path = require("node:path");

const webDir = path.join(process.cwd(), "apps", "web");
const npmCmd = process.platform === "win32" ? "npm.cmd" : "npm";

let sawExistingServerMessage = false;

function inspectChunk(chunk) {
  const text = chunk.toString();
  if (text.includes("Another next dev server is already running.")) {
    sawExistingServerMessage = true;
  }
}

const child = spawn(npmCmd, ["run", "dev:no-turbo"], {
  cwd: webDir,
  shell: process.platform === "win32",
  stdio: ["inherit", "pipe", "pipe"],
});

child.stdout.on("data", (chunk) => {
  inspectChunk(chunk);
  process.stdout.write(chunk);
});

child.stderr.on("data", (chunk) => {
  inspectChunk(chunk);
  process.stderr.write(chunk);
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }

  if (code === 0) {
    process.exit(0);
    return;
  }

  if (sawExistingServerMessage) {
    console.log(
      "ℹ️ Next dev already running for apps/web; continuing without failure.",
    );
    process.exit(0);
    return;
  }

  process.exit(code ?? 1);
});

child.on("error", (error) => {
  console.error("Failed to start web dev process:", error.message);
  process.exit(1);
});
