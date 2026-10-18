import { spawnSync } from "node:child_process";
import { loadEnvFile } from "node:process";

loadEnvFile("/run/secrets/production_env");

const authSecret =
  process.env.AUTH_SECRET?.trim() || process.env.NEXTAUTH_SECRET?.trim();
if (!authSecret) {
  throw new Error("Missing Auth secret: set AUTH_SECRET or NEXTAUTH_SECRET.");
}

const result = spawnSync(
  process.execPath,
  ["node_modules/next/dist/bin/next", "build", "--webpack"],
  {
    stdio: "inherit",
    env: {
      ...process.env,
      AUTH_SECRET: authSecret,
      NEXTAUTH_SECRET: authSecret,
    },
  },
);

if (result.error) {
  throw result.error;
}
process.exit(result.status ?? 1);
