import { NextResponse } from "next/server";
import {
  ACCESS_COOKIE,
  REFRESH_COOKIE,
  normalizeAuthResponse,
  proxyAuthJson,
} from "../_lib";

export async function POST(request: Request) {
  try {
    const body = await request.json();

    const { data: rawData } = await proxyAuthJson("/api/users/login", {
      method: "POST",
      body: JSON.stringify({
        email_or_username:
          body.email_or_username || body.username_or_email || "",
        password: body.password,
      }),
    });
    const data = normalizeAuthResponse(rawData);

    if (!data?.success || !data?.tokens?.access_token) {
      return NextResponse.json(
        {
          success: false,
          error: data?.error || "Login failed",
        },
        { status: 401 },
      );
    }

    const response = NextResponse.json(data, { status: 200 });
    const maxAge = Number(data.tokens.expires_in || 3600);

    response.cookies.set(ACCESS_COOKIE, data.tokens.access_token, {
      httpOnly: true,
      secure: true,
      sameSite: "lax",
      path: "/",
      maxAge,
    });

    if (data.tokens.refresh_token) {
      response.cookies.set(REFRESH_COOKIE, data.tokens.refresh_token, {
        httpOnly: true,
        secure: true,
        sameSite: "lax",
        path: "/",
        maxAge: 14 * 24 * 60 * 60,
      });
    }

    return response;
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: error instanceof Error ? error.message : "Login failed",
      },
      { status: 502 },
    );
  }
}
