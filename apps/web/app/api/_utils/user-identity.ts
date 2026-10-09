import { auth } from "@/lib/auth/server";
import { NextRequest } from "next/server";

const FALLBACK_USER_ID = "anonymous";

export async function resolveUserId(request: NextRequest): Promise<string> {
  const headerUserId =
    request.headers.get("X-User-ID") || request.headers.get("X-User-Id");
  if (headerUserId?.trim()) {
    return headerUserId.trim();
  }

  const { userId } = await auth();
  if (userId?.trim()) {
    return userId.trim();
  }

  return FALLBACK_USER_ID;
}

export async function getUserHeaders(
  request: NextRequest,
): Promise<Record<string, string>> {
  const userId = await resolveUserId(request);
  return {
    Accept: "application/json",
    "X-User-ID": userId,
    "X-User-Id": userId,
  };
}
