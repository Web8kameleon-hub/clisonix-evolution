import { NextResponse } from "next/server";

type OceanResponse = {
  response?: string;
  ocean_response?: string;
  answer?: string;
};

function parseSuggestions(raw: string): string[] {
  const normalized = raw
    .trim()
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/\s*```$/i, "");
  const parsed = JSON.parse(normalized) as unknown;
  if (!Array.isArray(parsed)) {
    throw new Error("Ocean returned a non-array suggestion payload.");
  }

  const suggestions = parsed
    .filter((item): item is string => typeof item === "string")
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 4);
  if (suggestions.length === 0) {
    throw new Error("Ocean returned no suggestions.");
  }
  return suggestions;
}

export async function POST(request: Request) {
  const body = (await request.json()) as {
    language?: string;
    topic?: string;
  };
  const upstream = (
    process.env.OCEAN_INTERNAL_URL ||
    process.env.OCEAN_CORE_URL ||
    "http://clisonix-ocean-core:8030"
  ).trim().replace(/\/+$/, "");
  if (!upstream) {
    return NextResponse.json(
      { error: "Ocean suggestions upstream is not configured." },
      { status: 503 },
    );
  }

  const language = body.language?.trim() || "auto";
  const topic = body.topic?.trim() || "open conversation";
  let response: Response;
  try {
    response = await fetch(`${upstream}/api/v1/chat`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message:
          `Return exactly one JSON array with 4 short, distinct conversation starters ` +
          `for topic "${topic}" in language "${language}". No markdown and no explanation.`,
        language,
        processing_mode: "fast",
        max_tokens: 160,
      }),
      signal: AbortSignal.timeout(30000),
    });
  } catch (error) {
    console.error("Ocean suggestions unavailable:", error);
    return NextResponse.json(
      { error: "Ocean suggestions unavailable." },
      { status: 503 },
    );
  }

  if (!response.ok) {
    return NextResponse.json(
      { error: `Ocean suggestions failed (${response.status}).` },
      { status: 502 },
    );
  }

  const payload = (await response.json()) as OceanResponse;
  const text = payload.response || payload.ocean_response || payload.answer || "";
  try {
    return NextResponse.json({ suggestions: parseSuggestions(text) });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Invalid suggestions response." },
      { status: 502 },
    );
  }
}
