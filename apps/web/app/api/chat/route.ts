/**
 * Clisonix Cloud - Chat API with History
 *
 * Persistent chat with Ocean Core AI
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Clisonix Cloud
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth/server";

const OCEAN_UPSTREAMS = [
  process.env.OCEAN_INTERNAL_URL,
  process.env.OCEAN_CORE_URL,
  process.env.NEXT_PUBLIC_OCEAN_API_URL,
  process.env.NEXT_PUBLIC_OCEAN_API,
  "http://clisonix-ocean-core:8030",
]
  .filter((value): value is string => Boolean(value && value.trim()))
  .map((value) => value.replace(/\/+$/, ""));
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const CHAT_UPSTREAM_TIMEOUT_MS = 25000;

interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string;
}

interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  model: string;
  createdAt: string;
  updatedAt: string;
}

type UpstreamPayload = {
  response?: unknown;
  answer?: unknown;
  ocean_response?: unknown;
};

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  timeoutMs: number,
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

async function queryRealOcean(
  message: string,
  context: Array<{ role: ChatMessage["role"]; content: string }>,
): Promise<string> {
  let lastError = "No upstream configured";

  for (const upstream of OCEAN_UPSTREAMS) {
    for (const path of ["/api/v1/chat", "/api/v1/query"]) {
      const url = `${upstream}${path}`;
      try {
        const response = await fetchWithTimeout(
          url,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message,
              query: message,
              context,
            }),
            cache: "no-store",
          },
          CHAT_UPSTREAM_TIMEOUT_MS,
        );

        if (!response.ok) {
          const errText = await response.text().catch(() => "");
          lastError = `${url} -> ${response.status}${errText ? `: ${errText.slice(0, 200)}` : ""}`;
          continue;
        }

        const payload = (await response.json()) as UpstreamPayload;
        const text =
          typeof payload.ocean_response === "string"
            ? payload.ocean_response
            : typeof payload.response === "string"
              ? payload.response
              : typeof payload.answer === "string"
                ? payload.answer
                : "";

        if (text.trim()) {
          return text.trim();
        }

        lastError = `${url} -> empty_response_payload`;
      } catch (error) {
        lastError = `${url} -> ${error instanceof Error ? error.message : "request_failed"}`;
      }
    }
  }

  throw new Error(lastError);
}

// In-memory store (replace with database in production)
const chatSessions = new Map<string, ChatSession>();

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { message, sessionId, model = "ocean-core" } = body;

    if (!message) {
      return NextResponse.json(
        { error: "Message is required" },
        { status: 400 },
      );
    }

    // Get or create session
    let session: ChatSession;
    const sessionKey = `${userId}-${sessionId || "default"}`;

    if (chatSessions.has(sessionKey)) {
      session = chatSessions.get(sessionKey)!;
    } else {
      session = {
        id: sessionId || crypto.randomUUID(),
        title: message.substring(0, 50) + (message.length > 50 ? "..." : ""),
        messages: [],
        model: model,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };
    }

    // Add user message
    const userMessage: ChatMessage = {
      role: "user",
      content: message,
      timestamp: new Date().toISOString(),
    };
    session.messages.push(userMessage);

    let assistantContent: string;
    try {
      assistantContent = await queryRealOcean(
        message,
        session.messages.slice(-10).map((m) => ({
          role: m.role,
          content: m.content,
        })),
      );
    } catch (error) {
      const reason = error instanceof Error ? error.message : "upstream_failed";
      return NextResponse.json(
        {
          error: "Ocean upstream unavailable",
          details: reason,
          code: "ocean_upstream_unavailable",
        },
        { status: 503 },
      );
    }

    // Add assistant message
    const assistantMessage: ChatMessage = {
      role: "assistant",
      content: assistantContent,
      timestamp: new Date().toISOString(),
    };
    session.messages.push(assistantMessage);

    // Update session
    session.updatedAt = new Date().toISOString();
    chatSessions.set(sessionKey, session);

    // Save to database (async, don't wait)
    saveChatToDatabase(userId, session).catch(console.error);

    return NextResponse.json({
      sessionId: session.id,
      message: assistantMessage,
      title: session.title,
    });
  } catch (error) {
    console.error("Chat error:", error);
    return NextResponse.json(
      { error: "Failed to process chat" },
      { status: 500 },
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("sessionId");

    if (sessionId) {
      // Get specific session
      const sessionKey = `${userId}-${sessionId}`;
      const session = chatSessions.get(sessionKey);

      if (!session) {
        return NextResponse.json(
          { error: "Session not found" },
          { status: 404 },
        );
      }

      return NextResponse.json(session);
    }

    // Get all sessions for user
    const userSessions: ChatSession[] = [];
    chatSessions.forEach((session, key) => {
      if (key.startsWith(`${userId}-`)) {
        userSessions.push({
          ...session,
          messages: [], // Don't include full messages in list
        });
      }
    });

    // Sort by updatedAt descending
    userSessions.sort(
      (a, b) =>
        new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    );

    return NextResponse.json({
      sessions: userSessions.slice(0, 50), // Limit to 50 sessions
    });
  } catch (error) {
    console.error("Get chat error:", error);
    return NextResponse.json(
      { error: "Failed to get chat history" },
      { status: 500 },
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("sessionId");

    if (!sessionId) {
      return NextResponse.json(
        { error: "Session ID required" },
        { status: 400 },
      );
    }

    const sessionKey = `${userId}-${sessionId}`;

    if (chatSessions.has(sessionKey)) {
      chatSessions.delete(sessionKey);
      return NextResponse.json({ deleted: true });
    }

    return NextResponse.json({ error: "Session not found" }, { status: 404 });
  } catch (error) {
    console.error("Delete chat error:", error);
    return NextResponse.json(
      { error: "Failed to delete chat" },
      { status: 500 },
    );
  }
}

async function saveChatToDatabase(userId: string, session: ChatSession) {
  try {
    const internalKey = process.env.INTERNAL_API_KEY;
    if (!internalKey) {
      return;
    }

    await fetch(`${API_URL}/internal/save-chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Internal-Key": internalKey,
      },
      body: JSON.stringify({
        userId,
        session,
      }),
    });
  } catch (error) {
    console.error("Failed to save chat to database:", error);
  }
}
