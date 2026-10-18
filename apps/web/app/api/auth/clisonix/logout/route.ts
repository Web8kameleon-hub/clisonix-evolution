import { NextResponse } from "next/server";
import { ACCESS_COOKIE, REFRESH_COOKIE, proxyAuthPassthrough } from "../_lib";

function clearAuthCookies(response: NextResponse) {
  for (const cookieName of [ACCESS_COOKIE, REFRESH_COOKIE]) {
    response.cookies.set(cookieName, "", {
      httpOnly: true,
      secure: true,
      sameSite: "lax",
      path: "/",
      expires: new Date(0),
    });
  }
  return response;
}

export async function POST(request: Request) {
  const cookieHeader = request.headers.get("cookie") || "";
  const match = cookieHeader
    .split(";")
    .map((chunk) => chunk.trim())
    .find((chunk) => chunk.startsWith(`${ACCESS_COOKIE}=`));
  const token = match
    ? decodeURIComponent(match.split("=").slice(1).join("="))
    : null;

  if (!token) {
    return clearAuthCookies(
      NextResponse.json({ success: true, message: "Logout successful" }),
    );
  }

  try {
    const { response: upstreamResponse } = await proxyAuthPassthrough(
      "/api/users/logout",
      {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      },
    );
    const payload = await upstreamResponse.json().catch(() => null);
    return clearAuthCookies(
      NextResponse.json(payload, { status: upstreamResponse.status }),
    );
  } catch (error) {
    return clearAuthCookies(
      NextResponse.json(
        {
          success: false,
          error:
            error instanceof Error ? error.message : "Internal logout failed",
        },
        { status: 502 },
      ),
    );
  }
}
