import { NextResponse } from "next/server";

export async function POST() {
  return NextResponse.json(
    {
      ok: false,
      error: "Public approval requests are disabled. Use an existing internal account.",
    },
    { status: 403 },
  );
}
