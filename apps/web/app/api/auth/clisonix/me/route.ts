import { NextResponse } from "next/server";
import {
  ACCESS_COOKIE,
  normalizeAuthResponse,
  proxyAuthPassthrough,
} from "../_lib";

export async function GET(request: Request) {
  try {
    const cookieHeader = request.headers.get("cookie") || "";
    const authorization = request.headers.get("authorization");

    let token: string | null = null;

    if (authorization && authorization.toLowerCase().startsWith("bearer ")) {
      token = authorization.slice(7).trim();
    }

    if (!token && cookieHeader) {
      const match = cookieHeader
        .split(";")
        .map((chunk) => chunk.trim())
        .find((chunk) => chunk.startsWith(`${ACCESS_COOKIE}=`));
      if (match) {
        token = decodeURIComponent(match.split("=").slice(1).join("="));
      }
    }

    if (!token) {
      return NextResponse.json(
        {
          success: false,
          error: "No authorization token provided",
        },
        { status: 401 },
      );
    }

    const { response } = await proxyAuthPassthrough("/api/users/validate-token", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const payload = normalizeAuthResponse(await response.json());
    return NextResponse.json(payload, { status: response.status });
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Auth check failed",
      },
      { status: 502 },
    );
  }
}
