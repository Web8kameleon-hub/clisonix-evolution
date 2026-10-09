import { NextResponse } from "next/server";

const isDev = process.env.NODE_ENV !== "production";
const OCEAN_CORE_URL =
  process.env.OCEAN_CORE_URL ||
  (isDev ? "http://localhost:8030" : "http://clisonix-ocean-core:8030");

export async function GET() {
  try {
    const response = await fetch(`${OCEAN_CORE_URL}/api/v1/documents/capabilities`, {
      method: "GET",
      cache: "no-store",
    });
    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    console.error("[Document Capabilities Proxy] Error:", error);
    return NextResponse.json(
      { status: "error", message: "Failed to fetch document capabilities." },
      { status: 502 },
    );
  }
}
