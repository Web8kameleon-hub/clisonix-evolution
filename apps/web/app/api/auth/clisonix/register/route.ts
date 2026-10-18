import { NextResponse } from "next/server";
import { normalizeAuthResponse, proxyAuthJson } from "../_lib";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const { data: rawData } = await proxyAuthJson("/api/users/register", {
      method: "POST",
      body: JSON.stringify(body),
    });
    const data = normalizeAuthResponse(rawData);

    if (!data?.success) {
      return NextResponse.json(
        {
          success: false,
          error: data?.error || "Register failed",
        },
        { status: 400 },
      );
    }

    return NextResponse.json(data, { status: 200 });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Register failed",
      },
      { status: 502 },
    );
  }
}
