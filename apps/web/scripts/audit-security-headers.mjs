const DEFAULT_URL = process.argv[2] || process.env.HEADER_AUDIT_URL || "http://127.0.0.1:3005/";

const REQUIRED_HEADERS = {
  "content-security-policy": (value) =>
    typeof value === "string" &&
    value.includes("default-src 'self'") &&
    !value.includes("'unsafe-eval'"),
  "x-frame-options": (value) => value === "DENY",
  "x-content-type-options": (value) => value === "nosniff",
  "referrer-policy": (value) => value === "strict-origin-when-cross-origin",
  "cross-origin-opener-policy": (value) => value === "same-origin",
  "cross-origin-resource-policy": (value) => ["same-site", "same-origin"].includes(value),
  "x-permitted-cross-domain-policies": (value) => value === "none",
};

function printResult(label, status, detail) {
  const prefix = status ? "✅" : "❌";
  console.log(`${prefix} ${label}: ${detail}`);
}

async function run() {
  console.log(`Auditing security headers for: ${DEFAULT_URL}`);

  let response;
  try {
    response = await fetch(DEFAULT_URL, {
      redirect: "manual",
      headers: {
        "user-agent": "clisonix-security-audit/1.0",
      },
      signal: AbortSignal.timeout(15000),
    });
  } catch (error) {
    console.error(`AUDIT_CONNECTION_ERROR: ${error.message}`);
    process.exit(2);
  }

  console.log(`HTTP ${response.status}`);

  let failures = 0;
  for (const [headerName, validator] of Object.entries(REQUIRED_HEADERS)) {
    const value = response.headers.get(headerName);
    const ok = validator(value);
    printResult(headerName, ok, value ?? "<missing>");
    if (!ok) failures += 1;
  }

  const hsts = response.headers.get("strict-transport-security");
  if (DEFAULT_URL.startsWith("https://")) {
    const ok = typeof hsts === "string" && hsts.includes("max-age=31536000");
    printResult("strict-transport-security", ok, hsts ?? "<missing>");
    if (!ok) failures += 1;
  } else {
    console.log(`ℹ️ strict-transport-security: skipped for non-HTTPS target (${hsts ?? "<missing>"})`);
  }

  if (failures > 0) {
    console.error(`AUDIT_FAILED: ${failures} required checks failed.`);
    process.exit(1);
  }

  console.log("AUDIT_PASSED: all required security headers are present.");
}

run();
