const { spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

function candidateRoots(startDir) {
  const roots = [];
  let current = path.resolve(startDir);

  for (let depth = 0; depth < 4; depth += 1) {
    roots.push(current);
    const parent = path.dirname(current);
    if (parent === current) break;
    current = parent;
  }

  return roots;
}

function getEnvironmentCandidates(root) {
  return [
    {
      python: path.join(root, ".venv-1", "Scripts", "python.exe"),
      scriptsDir: path.join(root, ".venv-1", "Scripts"),
    },
    {
      python: path.join(root, ".venv", "Scripts", "python.exe"),
      scriptsDir: path.join(root, ".venv", "Scripts"),
    },
  ];
}

function resolveCommand(startDir, args) {
  const requestedModule = args[0] === "-m" ? args[1] : null;

  for (const root of candidateRoots(startDir)) {
    const candidates = getEnvironmentCandidates(root);

    for (const candidate of candidates) {
      if (!fs.existsSync(candidate.python)) {
        continue;
      }

      if (requestedModule) {
        const moduleLauncher = path.join(
          candidate.scriptsDir,
          `${requestedModule}.exe`,
        );
        if (fs.existsSync(moduleLauncher)) {
          return {
            command: moduleLauncher,
            args: args.slice(2),
          };
        }
      }

      return {
        command: candidate.python,
        args,
      };
    }
  }

  return {
    command: process.env.PYTHON || "python",
    args,
  };
}

const args = process.argv.slice(2);
const resolved = resolveCommand(process.cwd(), args);

const child = spawn(resolved.command, resolved.args, {
  stdio: "inherit",
  shell: false,
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});

child.on("error", (error) => {
  console.error(
    `Failed to start Python via ${resolved.command}:`,
    error.message,
  );
  process.exit(1);
});
