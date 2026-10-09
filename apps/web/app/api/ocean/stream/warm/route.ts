/**
 * OCEAN TYPEAHEAD WARM PROXY
 * ==========================
 * Called while the user is still typing (debounced ~400ms).
 * Triggers Ocean-Core to pre-fetch external context and build the
 * enriched prompt into its warm cache, so when the user hits Enter
 * the streaming response starts instantly (0ms context wait).
 *
 * Human-thinking model: Ocean "reads" the message before it's sent.
 */

const OCEAN_INTERNAL_URL =
  process.env.OCEAN_INTERNAL_URL || "http://clisonix-ocean-core:8030";
const PRIMARY_OCEAN_URL = process.env.OCEAN_CORE_URL;

function getUpstream(): string {
  return (OCEAN_INTERNAL_URL || PRIMARY_OCEAN_URL || "").replace(/\/+$/, "");
}

export async function POST(request: Request) {
  try {
    const body = await request.json().catch(() => ({}));
    const message = String(
      (body as Record<string, unknown>).message ||
        (body as Record<string, unknown>).query ||
        ""
    ).trim();

    if (!message || message.length < 6) {
      return Response.json({ status: "skipped", reason: "too_short" });
    }

    const upstream = getUpstream();
    if (!upstream) {
      return Response.json({ status: "skipped", reason: "no_upstream" });
    }

    // Fire-and-forget: we don't wait for the warm result.
    // The backend builds context asynchronously and caches it.
    const warmPayload = {
      message,
      language: (body as Record<string, unknown>).language,
      bit_mode: (body as Record<string, unknown>).bit_mode,
      token_budget: (body as Record<string, unknown>).token_budget,
      processing_mode: (body as Record<string, unknown>).processing_mode,
      curiosity_level: (body as Record<string, unknown>).curiosity_level,
      pre_enter: (body as Record<string, unknown>).pre_enter === true,
      user_id: (body as Record<string, unknown>).user_id,
    };

    const warmFetch = fetch(`${upstream}/api/v1/chat/stream/warm`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(warmPayload),
    }).catch((err) => {
      console.warn("[Warm] upstream unreachable:", err?.message ?? err);
    });

    // Don't await — return instantly to the frontend.
    void warmFetch;

    return Response.json({ status: "warming" });
  } catch (err) {
    console.error("[Warm] proxy error:", err);
    return Response.json({ status: "error" }, { status: 500 });
  }
}
