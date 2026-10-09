import { NextResponse } from "next/server";

const isDev = process.env.NODE_ENV !== "production";
const API_INTERNAL =
  process.env.API_INTERNAL_URL ||
  (isDev ? "http://localhost:8000" : "http://clisonix-api:8000");

export async function GET() {
  try {
    const endpoints = [
      `${API_INTERNAL}/api/reporting/errors`,
      `${API_INTERNAL}/api/reporting/alerts`,
    ];

    let lastStatus = 503;
    for (const endpoint of endpoints) {
      const response = await fetch(endpoint, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        signal: AbortSignal.timeout(5000),
      });

      if (!response.ok) {
        lastStatus = response.status;
        continue;
      }

      const data = await response.json();
      const errors = Array.isArray(data?.errors)
        ? data.errors
        : Array.isArray(data?.alerts)
          ? data.alerts
          : Array.isArray(data?.recent_errors)
            ? data.recent_errors
            : [];

      return NextResponse.json({ errors }, { status: 200 });
    }

    return NextResponse.json(
      { error: "Failed to fetch errors", status: lastStatus },
      { status: lastStatus },
    );
  } catch (error) {
    return NextResponse.json(
      {
        error: "Failed to connect to reporting service",
        details: String(error),
      },
      { status: 503 },
    );
  }
}
