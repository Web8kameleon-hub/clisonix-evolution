import { fetchFromCandidates, fetchJsonFromCandidates } from "../../_lib/upstream";

export const ACCESS_COOKIE = "clx_access_token";
export const REFRESH_COOKIE = "clx_refresh_token";

export type ClisonixTokenPair = {
  access_token?: string;
  refresh_token?: string;
  expires_in?: number;
  token_type?: string;
};

export type ClisonixAuthResponse = {
  success?: boolean;
  valid?: boolean;
  message?: string;
  detail?: string;
  access_token?: string;
  refresh_token?: string;
  expires_at?: string;
  user?: {
    id?: string;
    user_id?: string;
    email?: string | null;
    username?: string | null;
    is_superuser?: boolean;
  } | null;
  tokens?: ClisonixTokenPair;
  error?: string;
};

export function normalizeAuthResponse(
  payload: ClisonixAuthResponse,
): ClisonixAuthResponse {
  const expiresAt = payload.expires_at
    ? Date.parse(payload.expires_at)
    : Number.NaN;
  const expiresIn =
    Number.isFinite(expiresAt) && expiresAt > Date.now()
      ? Math.floor((expiresAt - Date.now()) / 1000)
      : undefined;
  const user = payload.user
    ? {
        ...payload.user,
        id: payload.user.id || payload.user.user_id,
      }
    : null;

  return {
    ...payload,
    success: payload.success ?? payload.valid,
    error: payload.error || payload.detail,
    user,
    tokens:
      payload.tokens ||
      (payload.access_token
        ? {
            access_token: payload.access_token,
            refresh_token: payload.refresh_token,
            expires_in: expiresIn,
            token_type: "bearer",
          }
        : undefined),
  };
}

export type ClisonixResolvedUser = {
  id: string;
  email: string;
  username?: string | null;
  is_superuser?: boolean;
};

function extractBearerToken(request: Request): string | null {
  const authorization = request.headers.get("authorization");
  if (authorization && authorization.toLowerCase().startsWith("bearer ")) {
    return authorization.slice(7).trim();
  }

  const cookieHeader = request.headers.get("cookie") || "";
  const match = cookieHeader
    .split(";")
    .map((chunk) => chunk.trim())
    .find((chunk) => chunk.startsWith(`${ACCESS_COOKIE}=`));

  if (!match) {
    return null;
  }

  return decodeURIComponent(match.split("=").slice(1).join("="));
}

export async function resolveClisonixUser(request: Request): Promise<ClisonixResolvedUser | null> {
  const token = extractBearerToken(request);
  if (!token) {
    return null;
  }

  try {
    const { response } = await proxyAuthPassthrough("/api/users/validate-token", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      return null;
    }

    const payload = normalizeAuthResponse(
      (await response.json()) as ClisonixAuthResponse,
    );
    const email = payload.user?.email || null;
    if (!payload.success || !email) {
      return null;
    }

    return {
      id: payload.user?.id || email,
      email,
      username: payload.user?.username || null,
      is_superuser: payload.user?.is_superuser,
    };
  } catch (error) {
    console.error("Internal auth token validation failed", error);
    return null;
  }
}

export async function proxyAuthJson(path: string, init: RequestInit = {}) {
  return fetchJsonFromCandidates<ClisonixAuthResponse>({
    group: "auth",
    path,
    init,
    headers: {
      "Content-Type": "application/json",
    },
    timeoutMs: 6000,
    acceptNonOk: true,
  });
}

export async function proxyAuthPassthrough(path: string, init: RequestInit = {}) {
  return fetchFromCandidates({
    group: "auth",
    path,
    init,
    timeoutMs: 6000,
    acceptNonOk: true,
  });
}
