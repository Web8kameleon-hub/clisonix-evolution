import { NextRequest, NextResponse } from "next/server";
import { promises as fs } from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

type AssistAction =
  | "screen_analyze"
  | "web_wwwmmm"
  | "consent_grant"
  | "consent_status"
  | "consent_revoke";

type ConsentMode = "once" | "15m";

type ConsentRecord = {
  token: string;
  mode: ConsentMode;
  scope: string;
  granted_at: string;
  expires_at: string;
  remaining_uses: number | null;
  revoked_at?: string;
};

type ConsentStore = Record<string, ConsentRecord>;

const CONSENT_RUNTIME_DIR = ".runtime";
const CONSENT_RUNTIME_FILE = "ocean-user-assist-consent.json";

function getOrigin(request: NextRequest): string {
  const host =
    request.headers.get("x-forwarded-host") ||
    request.headers.get("host") ||
    "localhost:3000";
  const proto = request.headers.get("x-forwarded-proto") || "http";
  return `${proto}://${host}`;
}

function consentFilePath(): string {
  return path.join(process.cwd(), CONSENT_RUNTIME_DIR, CONSENT_RUNTIME_FILE);
}

async function loadConsentStore(): Promise<ConsentStore> {
  try {
    const raw = await fs.readFile(consentFilePath(), "utf-8");
    const parsed = JSON.parse(raw) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      return {};
    }
    return parsed as ConsentStore;
  } catch {
    return {};
  }
}

async function saveConsentStore(store: ConsentStore): Promise<void> {
  const dir = path.join(process.cwd(), CONSENT_RUNTIME_DIR);
  await fs.mkdir(dir, { recursive: true });
  await fs.writeFile(consentFilePath(), JSON.stringify(store, null, 2) + "\n", "utf-8");
}

function getUserKey(request: NextRequest): string {
  const userId = request.headers.get("X-User-ID") || request.headers.get("X-User-Id");
  if (userId && userId.trim()) return `user:${userId.trim()}`;

  const forwarded = request.headers.get("x-forwarded-for");
  const ip = (forwarded || "").split(",")[0]?.trim();
  if (ip) return `ip:${ip}`;

  return "anonymous";
}

function isConsentActive(record: ConsentRecord | undefined): boolean {
  if (!record) return false;
  if (record.revoked_at) return false;
  if (Date.now() >= Date.parse(record.expires_at)) return false;
  if (typeof record.remaining_uses === "number" && record.remaining_uses <= 0) {
    return false;
  }
  return true;
}

function generateConsentToken(): string {
  return `${crypto.randomUUID()}-${crypto.randomBytes(8).toString("hex")}`;
}

function grantConsentRecord(mode: ConsentMode): ConsentRecord {
  const now = new Date();
  const expiresAt = new Date(
    now.getTime() + (mode === "15m" ? 15 * 60 * 1000 : 5 * 60 * 1000),
  );

  return {
    token: generateConsentToken(),
    mode,
    scope:
      mode === "15m"
        ? "screen-and-web-assist-15m"
        : "screen-and-web-assist-single-use",
    granted_at: now.toISOString(),
    expires_at: expiresAt.toISOString(),
    remaining_uses: mode === "once" ? 1 : null,
  };
}

function consentReceipt(record: ConsentRecord) {
  return {
    approved: true,
    mode: record.mode,
    scope: record.scope,
    granted_at: record.granted_at,
    expires_at: record.expires_at,
    remaining_uses: record.remaining_uses,
  };
}

async function validateAndConsumeConsent(
  request: NextRequest,
  body: Record<string, unknown>,
): Promise<{ ok: true; receipt: ReturnType<typeof consentReceipt> } | { ok: false; message: string }> {
  const token = safeMessage(body.consent_token);
  if (!token) {
    return { ok: false, message: "Consent token is required." };
  }

  const userKey = getUserKey(request);
  const store = await loadConsentStore();
  const record = store[userKey];

  if (!record || record.token !== token) {
    return { ok: false, message: "Consent token is invalid for this user/session." };
  }

  if (!isConsentActive(record)) {
    delete store[userKey];
    await saveConsentStore(store);
    return { ok: false, message: "Consent token expired or revoked." };
  }

  if (record.mode === "once") {
    const remaining = (record.remaining_uses || 1) - 1;
    if (remaining <= 0) {
      delete store[userKey];
      await saveConsentStore(store);
      return {
        ok: true,
        receipt: {
          ...consentReceipt(record),
          remaining_uses: 0,
        },
      };
    }

    record.remaining_uses = remaining;
    store[userKey] = record;
    await saveConsentStore(store);
    return { ok: true, receipt: consentReceipt(record) };
  }

  return { ok: true, receipt: consentReceipt(record) };
}

function safeMessage(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

async function readUpstreamJsonOrText(response: Response): Promise<Record<string, unknown>> {
  const text = (await response.text()).trim();
  if (!text) return {};

  try {
    const parsed = JSON.parse(text) as unknown;
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>;
    }
  } catch {
  }

  return { text };
}

async function callOceanChat(
  origin: string,
  message: string,
  userId: string | null,
): Promise<Record<string, unknown>> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (userId) {
    headers["X-User-ID"] = userId;
    headers["X-User-Id"] = userId;
  }

  const response = await fetch(`${origin}/api/ocean`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      message,
      stream: false,
      response_mode: "single",
      phase: "wwwmmm",
      transport: "scanner_printer_leaser",
      scanner: "wwwmmm-scanner",
      printer: "wwwmmm-printer",
      leaser: "wwwmmm-leaser",
      measurement_unit: "nanodecibel",
    }),
  });

  const payload = await readUpstreamJsonOrText(response);
  if (!response.ok) {
    const detail =
      (typeof payload.message === "string" && payload.message) ||
      (typeof payload.error === "string" && payload.error) ||
      `Ocean response failed with ${response.status}`;
    throw new Error(detail);
  }

  return payload;
}

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as Record<string, unknown>;
    const action = String(body.action || "") as AssistAction;

    const userKey = getUserKey(request);
    const store = await loadConsentStore();

    if (action === "consent_status") {
      const record = store[userKey];
      const active = isConsentActive(record);
      if (!active && record) {
        delete store[userKey];
        await saveConsentStore(store);
      }

      return NextResponse.json({
        ok: true,
        active,
        consent: active && record ? consentReceipt(record) : null,
      });
    }

    if (action === "consent_revoke") {
      if (store[userKey]) {
        delete store[userKey];
        await saveConsentStore(store);
      }

      return NextResponse.json({
        ok: true,
        revoked: true,
      });
    }

    if (action === "consent_grant") {
      const modeRaw = safeMessage(body.mode).toLowerCase();
      const mode: ConsentMode = modeRaw === "15m" ? "15m" : "once";
      const record = grantConsentRecord(mode);
      store[userKey] = record;
      await saveConsentStore(store);

      return NextResponse.json({
        ok: true,
        active: true,
        consent_token: record.token,
        consent: consentReceipt(record),
      });
    }

    if (!action || (action !== "screen_analyze" && action !== "web_wwwmmm")) {
      return NextResponse.json(
        {
          ok: false,
          error: "invalid_action",
          supported_actions: [
            "consent_grant",
            "consent_status",
            "consent_revoke",
            "screen_analyze",
            "web_wwwmmm",
          ],
        },
        { status: 400 },
      );
    }

    const consentValidation = await validateAndConsumeConsent(request, body);
    if (!consentValidation.ok) {
      const consentMessage =
        "message" in consentValidation
          ? consentValidation.message
          : "Consent token is required.";
      return NextResponse.json(
        {
          ok: false,
          error: "consent_required",
          message: consentMessage,
        },
        { status: 403 },
      );
    }

    const origin = getOrigin(request);
    const userId =
      request.headers.get("X-User-ID") || request.headers.get("X-User-Id");

    if (action === "screen_analyze") {
      const screenText = safeMessage(body.screen_text);
      const interactionIntent = safeMessage(body.interaction_intent);

      if (!screenText) {
        return NextResponse.json(
          {
            ok: false,
            error: "screen_text_required",
          },
          { status: 422 },
        );
      }

      const prompt = [
        "WWWMMM screen analysis mode enabled.",
        "Analyze the provided user screen text and propose safe next actions.",
        "Do not pretend to click or control anything; provide approval-required action steps.",
        interactionIntent
          ? `Interaction goal: ${interactionIntent}`
          : "Interaction goal: general assistance",
        "Screen context:",
        screenText,
      ].join("\n\n");

      const result = await callOceanChat(origin, prompt, userId);
      return NextResponse.json({
        ok: true,
        mode: "screen_assist",
        consent: consentValidation.receipt,
        wwwmmm: {
          phase: "wwwmmm",
          transport: "scanner_printer_leaser",
          measurement_unit: "nanodecibel",
        },
        result,
      });
    }

    const targetUrl = safeMessage(body.url);
    const maxCharsRaw = Number(body.max_chars || 12000);
    const maxChars = Number.isFinite(maxCharsRaw)
      ? Math.max(500, Math.min(500000, Math.trunc(maxCharsRaw)))
      : 12000;

    if (!targetUrl) {
      return NextResponse.json(
        {
          ok: false,
          error: "url_required",
        },
        { status: 422 },
      );
    }

    const params = new URLSearchParams({
      action: "browse",
      url: targetUrl,
      max_chars: String(maxChars),
    });

    const webHeaders: Record<string, string> = {};
    if (userId) {
      webHeaders["X-User-ID"] = userId;
      webHeaders["X-User-Id"] = userId;
    }

    const webResponse = await fetch(`${origin}/api/ocean/web-reader?${params.toString()}`, {
      method: "GET",
      headers: webHeaders,
      cache: "no-store",
    });

    const webPayload = await readUpstreamJsonOrText(webResponse);
    if (!webResponse.ok) {
      const detail =
        (typeof webPayload.message === "string" && webPayload.message) ||
        (typeof webPayload.error === "string" && webPayload.error) ||
        `Web reader failed with ${webResponse.status}`;
      return NextResponse.json(
        {
          ok: false,
          error: "web_reader_failed",
          message: detail,
        },
        { status: webResponse.status },
      );
    }

    return NextResponse.json({
      ok: true,
      mode: "web_wwwmmm",
      consent: consentValidation.receipt,
      wwwmmm: {
        phase: "wwwmmm",
        transport: "scanner_printer_leaser",
        measurement_unit: "nanodecibel",
      },
      data: webPayload,
    });
  } catch (error) {
    return NextResponse.json(
      {
        ok: false,
        error: "user_assist_failed",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      { status: 500 },
    );
  }
}
