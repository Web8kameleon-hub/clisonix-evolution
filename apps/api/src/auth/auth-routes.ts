/**
 * Clisonix SIMPLE USER AUTHENTICATION
 * ====================================
 * Basic user auth pÃ«r payment system
 */

import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import * as crypto from "crypto";
import {
  isAccountLocked,
  checkIpRateLimit,
  recordFailedLogin,
  recordSuccessfulLogin,
  validatePasswordStrength,
  isSuspiciousIp,
  getSecurityMetrics,
} from "./login-security";

const USER_SERVICE_BASE_URL = [
  process.env["USER_SERVICE_URL"],
  process.env["USER_MANAGEMENT_URL"],
  process.env["USER_MANAGEMENT_BASE_URL"],
]
  .find((value) => typeof value === "string" && value.trim().length > 0)
  ?.trim()
  .replace(/\/$/, "");

// =================================================================================
// USER INTERFACES
// =================================================================================

export interface User {
  id: string;
  email: string;
  username: string;
  hashed_password: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreateRequest {
  email: string;
  username: string;
  password: string;
}

export interface UserLoginRequest {
  username_or_email: string;
  password: string;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// =================================================================================
// IN-MEMORY USER STORAGE
// =================================================================================

const users = new Map<string, User>();
const tokens = new Map<string, { user_id: string; expires_at: string }>();

const adminPassword = process.env["ADMIN_PASSWORD"]?.trim();
if (adminPassword) {
  const adminNow = new Date().toISOString();
  const adminUser: User = {
    id: "admin-001",
    email: process.env["ADMIN_EMAIL"]?.trim() || "clisonix@pm.me",
    username: process.env["ADMIN_USERNAME"]?.trim() || "admin",
    hashed_password: hashPassword(adminPassword),
    is_active: true,
    is_superuser: true,
    created_at: adminNow,
    updated_at: adminNow,
  };
  users.set(adminUser.id, adminUser);
}

// =================================================================================
// UTILITY FUNCTIONS
// =================================================================================

import bcryptjs from "bcryptjs";

const BCRYPT_ROUNDS = 12;

function hashPassword(password: string): string {
  // SECURITY: Use bcrypt with proper work factor for password hashing
  return bcryptjs.hashSync(password, BCRYPT_ROUNDS);
}

function verifyPassword(password: string, hashedPassword: string): boolean {
  // SECURITY: Use bcrypt's constant-time comparison
  return bcryptjs.compareSync(password, hashedPassword);
}

function generateToken(): string {
  return (
    crypto.randomUUID() +
    "." +
    Date.now() +
    "." +
    crypto.randomBytes(16).toString("hex")
  );
}

function createTokenPair(user: User): TokenPair {
  const accessToken = generateToken();
  const refreshToken = generateToken();
  const expiresIn = 3600; // 1 hour

  // Store tokens
  tokens.set(accessToken, {
    user_id: user.id,
    expires_at: new Date(Date.now() + expiresIn * 1000).toISOString(),
  });

  tokens.set(refreshToken, {
    user_id: user.id,
    expires_at: new Date(Date.now() + 14 * 24 * 3600 * 1000).toISOString(), // 14 days
  });

  return {
    access_token: accessToken,
    refresh_token: refreshToken,
    token_type: "bearer",
    expires_in: expiresIn,
  };
}

function findUserByEmail(email: string): User | null {
  for (const user of users.values()) {
    if (user.email === email) {
      return user;
    }
  }
  return null;
}

function findUserByUsername(username: string): User | null {
  for (const user of users.values()) {
    if (user.username === username) {
      return user;
    }
  }
  return null;
}

function verifyToken(token: string): User | null {
  const tokenData = tokens.get(token);
  if (!tokenData) return null;

  // Check expiration
  if (new Date() > new Date(tokenData.expires_at)) {
    tokens.delete(token);
    return null;
  }

  return users.get(tokenData.user_id) || null;
}

function getClientIp(request: FastifyRequest): string | null {
  const forwardedFor = request.headers["x-forwarded-for"];
  if (typeof forwardedFor === "string") {
    const firstIp = forwardedFor.split(",")[0]?.trim();
    if (firstIp) {
      return firstIp;
    }
  }

  return request.socket.remoteAddress || null;
}

function buildForwardHeaders(
  request: FastifyRequest,
  contentType?: string,
): Record<string, string> {
  const headers: Record<string, string> = {
    Accept: "application/json",
  };

  if (contentType) {
    headers["Content-Type"] = contentType;
  }

  if (typeof request.headers.authorization === "string") {
    headers["Authorization"] = request.headers.authorization;
  }

  const apiKeyHeader = request.headers["x-api-key"];
  if (typeof apiKeyHeader === "string") {
    headers["X-API-Key"] = apiKeyHeader;
  }

  return headers;
}

async function proxyUserService(
  request: FastifyRequest,
  reply: FastifyReply,
  path: string,
  options?: {
    method?: "GET" | "POST" | "PUT" | "DELETE";
    body?: unknown;
    query?: Record<string, string | number | undefined>;
  },
) {
  if (!USER_SERVICE_BASE_URL) {
    reply.code(503);
    return {
      success: false,
      error:
        "USER_SERVICE_URL, USER_MANAGEMENT_URL, or USER_MANAGEMENT_BASE_URL must be configured",
    };
  }

  const method = options?.method || "GET";
  const url = new URL(`${USER_SERVICE_BASE_URL}${path}`);

  if (options?.query) {
    for (const [key, value] of Object.entries(options.query)) {
      if (value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    }
  }

  try {
    const requestInit: RequestInit = {
      method,
      headers: buildForwardHeaders(
        request,
        options?.body !== undefined ? "application/json" : undefined,
      ),
    };

    if (options?.body !== undefined) {
      requestInit.body = JSON.stringify(options.body);
    }

    const response = await fetch(url, requestInit);

    const rawBody = await response.text();
    let payload: unknown = {};

    if (rawBody.trim().length > 0) {
      try {
        payload = JSON.parse(rawBody);
      } catch {
        payload = { success: response.ok, message: rawBody };
      }
    }

    reply.code(response.status);
    return payload;
  } catch (error) {
    reply.code(503);
    return {
      success: false,
      error: "User management service unavailable",
      details: error instanceof Error ? error.message : "unknown error",
    };
  }
}

// =================================================================================
// AUTH ROUTES
// =================================================================================

export async function registerAuthRoutes(app: FastifyInstance) {
  // =================================================================================
  // REGISTER USER - WITH STRONG PASSWORD REQUIREMENTS
  // =================================================================================
  app.post(
    "/auth/register",
    async (request: FastifyRequest, reply: FastifyReply) => {
      const body = request.body as UserCreateRequest;

      return proxyUserService(request, reply, "/api/users/register", {
        method: "POST",
        body: {
          email: body.email,
          username: body.username,
          password: body.password,
        },
      });
    },
  );

  // =================================================================================
  // LOGIN USER - WITH STRONG SECURITY
  // =================================================================================
  app.post(
    "/auth/login",
    async (request: FastifyRequest, reply: FastifyReply) => {
      const body = request.body as UserLoginRequest;

      return proxyUserService(request, reply, "/api/users/login", {
        method: "POST",
        body: {
          email_or_username: body.username_or_email,
          password: body.password,
        },
      });
    },
  );

  // =================================================================================
  // LOGIN SECURITY STATUS
  // =================================================================================
  app.get(
    "/auth/security-metrics",
    async (request: FastifyRequest, reply: FastifyReply) => {
      reply.code(503);
      return {
        success: false,
        error:
          "Security metrics are not exposed by the configured user-management service",
      };
    },
  );

  // =================================================================================
  // GET CURRENT USER
  // =================================================================================
  app.get("/auth/me", async (request: FastifyRequest, reply: FastifyReply) => {
    return proxyUserService(request, reply, "/api/users/me");
  });

  // =================================================================================
  // LOGOUT
  // =================================================================================
  app.post(
    "/auth/logout",
    async (request: FastifyRequest, reply: FastifyReply) => {
      return proxyUserService(request, reply, "/api/users/logout", {
        method: "POST",
      });
    },
  );

  // =================================================================================
  // GET ALL USERS (Admin only)
  // =================================================================================
  app.get(
    "/auth/users",
    async (request: FastifyRequest, reply: FastifyReply) => {
      const query = request.query as {
        status?: string;
        plan?: string;
        limit?: number;
        offset?: number;
      };

      return proxyUserService(request, reply, "/api/admin/users", {
        query: {
          status: query.status,
          plan: query.plan,
          limit: query.limit,
          offset: query.offset,
        },
      });
    },
  );
}

