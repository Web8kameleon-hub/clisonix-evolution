import { randomUUID } from "node:crypto";
import { NextResponse } from "next/server";
import { currentUser } from "@/lib/auth/server";
import { checkoutRedirect, planForPrice, stripeClient } from "@/lib/billing/checkout";

export async function POST(request: Request) {
  try {
    const user = await currentUser();
    if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    const email = user.emailAddresses[0]?.emailAddress;
    if (!email) return NextResponse.json({ error: "User email is required" }, { status: 400 });
    const body = await request.json();
    const interval = body.interval || "monthly";
    const planName = typeof body.plan === "string" ? body.plan.toUpperCase() : "";
    const priceId = body.priceId || body.price_id || (
      ["STARTER", "STANDARD", "PROFESSIONAL", "ENTERPRISE"].includes(planName) &&
      ["monthly", "yearly"].includes(interval)
        ? process.env[`STRIPE_PRICE_${planName}_${interval.toUpperCase()}`] : undefined
    );
    if (typeof priceId !== "string" || !priceId.startsWith("price_")) {
      return NextResponse.json({ error: "A configured subscription price is required" }, { status: 400 });
    }
    const plan = planForPrice(priceId);
    if (!plan) return NextResponse.json({ error: "Subscription plan is not configured" }, { status: 503 });
    const successUrl = checkoutRedirect(request, body.successUrl || body.success_url,
      "/modules/account?success=true&session_id={CHECKOUT_SESSION_ID}");
    const cancelUrl = checkoutRedirect(request, body.cancelUrl || body.cancel_url,
      "/modules/account?canceled=true");
    const stripe = stripeClient();
    const price = await stripe.prices.retrieve(priceId);
    if (!price.active || !price.recurring) {
      return NextResponse.json({ error: "Price is not an active subscription" }, { status: 400 });
    }
    const customers = await stripe.customers.list({ email, limit: 100 });
    let customer = customers.data.find(candidate => candidate.metadata.user_id === user.id) ||
      customers.data.find(candidate => !candidate.metadata.user_id);
    if (!customer) {
      customer = await stripe.customers.create({ email, name: user.fullName || undefined,
        metadata: { user_id: user.id } }, { idempotencyKey: `customer:${user.id}:${email}` });
    }
    const subscriptions = await stripe.subscriptions.list({ customer: customer.id, status: "all", limit: 100 });
    if (subscriptions.data.some(sub => ["active", "trialing", "past_due", "unpaid", "incomplete"].includes(sub.status))) {
      return NextResponse.json({ error: "Manage the existing subscription in the billing portal" }, { status: 409 });
    }
    const requestKey = request.headers.get("idempotency-key") || randomUUID();
    if (requestKey.length > 150) return NextResponse.json({ error: "Invalid idempotency key" }, { status: 400 });
    const session = await stripe.checkout.sessions.create({
      customer: customer.id, client_reference_id: user.id,
      line_items: [{ price: priceId, quantity: 1 }], mode: "subscription",
      success_url: successUrl, cancel_url: cancelUrl,
      metadata: { user_id: user.id, plan, price_id: priceId },
      subscription_data: { metadata: { user_id: user.id, plan } },
      billing_address_collection: "required",
    }, { idempotencyKey: `sub:${user.id}:${requestKey}` });
    return NextResponse.json({ success: true, sessionId: session.id, url: session.url,
      data: { sessionId: session.id, url: session.url } });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Checkout failed";
    const status = message === "STRIPE_NOT_CONFIGURED" ? 503 :
      message === "INVALID_CHECKOUT_REDIRECT" || error instanceof SyntaxError ? 400 : 502;
    return NextResponse.json({ error: status === 502 ? "Stripe checkout is unavailable" : message }, { status });
  }
}
