import { randomUUID } from "node:crypto";
import { NextResponse } from "next/server";
import { currentUser } from "@/lib/auth/server";
import { checkoutRedirect, stripeClient } from "@/lib/billing/checkout";

export async function POST(request: Request) {
  try {
    const user = await currentUser();
    if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    const email = user.emailAddresses[0]?.emailAddress;
    if (!email) return NextResponse.json({ error: "User email is required" }, { status: 400 });
    const body = await request.json();
    const priceId = body.price;
    const quantity = body.quantity ?? 1;
    if (typeof priceId !== "string" || !priceId.startsWith("price_") ||
        !Number.isInteger(quantity) || quantity < 1 || quantity > 100) {
      return NextResponse.json({ error: "Invalid price or quantity" }, { status: 400 });
    }
    const success = checkoutRedirect(request, body.success_url,
      "/modules/account?success=true&session_id={CHECKOUT_SESSION_ID}");
    const cancel = checkoutRedirect(request, body.cancel_url, "/pricing?canceled=true");
    const stripe = stripeClient();
    const price = await stripe.prices.retrieve(priceId);
    if (!price.active || price.recurring) {
      return NextResponse.json({ error: "Price is not an active one-time payment" }, { status: 400 });
    }
    const requestKey = request.headers.get("idempotency-key") || body.idempotency_key || randomUUID();
    if (typeof requestKey !== "string" || requestKey.length > 150) {
      return NextResponse.json({ error: "Invalid idempotency key" }, { status: 400 });
    }
    const idempotencyKey = `purchase:${user.id}:${requestKey}`;
    const session = await stripe.checkout.sessions.create({
      customer_email: email, customer_creation: "always", client_reference_id: user.id,
      line_items: [{ price: priceId, quantity }], mode: "payment",
      success_url: success, cancel_url: cancel,
      metadata: { user_id: user.id, price_id: priceId, quantity: String(quantity) },
    }, { idempotencyKey });
    return NextResponse.json({ id: session.id, url: session.url, mode: session.mode,
      payment_status: session.payment_status, idempotency_key: idempotencyKey });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Checkout failed";
    const status = message === "STRIPE_NOT_CONFIGURED" ? 503 :
      message === "INVALID_CHECKOUT_REDIRECT" || error instanceof SyntaxError ? 400 : 502;
    return NextResponse.json({ error: status === 502 ? "Stripe checkout is unavailable" : message }, { status });
  }
}
