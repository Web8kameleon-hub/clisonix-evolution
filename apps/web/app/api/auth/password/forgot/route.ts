import { NextRequest, NextResponse } from "next/server";
import { fetchFromCandidates } from "../../../_lib/upstream";

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON body" }, { status: 400 });
  }

  try {
    const { response } = await fetchFromCandidates({
      group: "auth",
      path: "/api/users/password/forgot",
      init: {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      },
      acceptNonOk: true,
    });

    const data = await response.json().catch(() => ({}));
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Internal authentication is unavailable." },
      { status: 503 },
    );
  }
}
