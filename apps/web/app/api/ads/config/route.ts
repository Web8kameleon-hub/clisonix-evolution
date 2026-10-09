import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const slot = url.searchParams.get("slot") || "footer";

  return NextResponse.json(
    {
      enabled: false,
      provider: "none",
      reason: "ads_disabled",
      slot,
    },
    { status: 200 },
  );
}
