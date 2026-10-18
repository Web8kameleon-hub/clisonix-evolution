/** Keep both public webhook URLs on the same signature-verified persistence path. */
export async function forwardStripeWebhook(request: Request): Promise<Response> {
  const base = process.env.API_INTERNAL_URL?.trim().replace(/\/+$/, "");
  if (!base) {
    return Response.json({ error: "Billing upstream is not configured" }, { status: 503 });
  }
  const signature = request.headers.get("stripe-signature");
  if (!signature) {
    return Response.json({ error: "Missing Stripe signature" }, { status: 400 });
  }
  try {
    const result = await fetch(`${base}/api/v1/billing/webhook`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Stripe-Signature": signature },
      body: await request.arrayBuffer(),
      cache: "no-store",
      signal: AbortSignal.timeout(25000),
      redirect: "error",
    });
    return new Response(await result.arrayBuffer(), {
      status: result.status,
      headers: { "Content-Type": result.headers.get("content-type") || "application/json" },
    });
  } catch {
    // Non-2xx keeps Stripe's retry mechanism active on persistence failures.
    return Response.json({ error: "Billing upstream is unavailable" }, { status: 503 });
  }
}
