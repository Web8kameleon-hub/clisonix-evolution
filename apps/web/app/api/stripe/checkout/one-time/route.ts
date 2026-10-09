import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";

const getStripe = () => {
  if (!process.env.STRIPE_SECRET_KEY) {
    throw new Error("STRIPE_SECRET_KEY is not configured");
  }
  return new Stripe(process.env.STRIPE_SECRET_KEY, {});
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const price = body.price as string | undefined;
    const quantity = Number(body.quantity ?? 1);
    const idempotencyFromHeader =
      request.headers.get("idempotency-key") ||
      request.headers.get("x-idempotency-key") ||
      undefined;
    const idempotencyFromBody =
      typeof body.idempotency_key === "string"
        ? body.idempotency_key
        : undefined;
    const idempotencyKey =
      idempotencyFromBody ||
      idempotencyFromHeader ||
      `ot:${price || "unknown"}:${quantity}:${Date.now()}`;

    if (!price) {
      return NextResponse.json(
        { error: "Missing required field: price" },
        { status: 400 },
      );
    }

    const appUrl =
      process.env.NEXT_PUBLIC_APP_URL || "https://www.clisonix.com";
    const successUrl =
      body.success_url ||
      `${appUrl}/modules/account?success=true&session_id={CHECKOUT_SESSION_ID}`;
    const cancelUrl = body.cancel_url || `${appUrl}/pricing?canceled=true`;

    const stripe = getStripe();
    const session = await stripe.checkout.sessions.create(
      {
        line_items: [
          {
            price,
            quantity,
          },
        ],
        mode: "payment",
        success_url: successUrl,
        cancel_url: cancelUrl,
        metadata: {
          price_id: price,
          quantity: String(quantity),
        },
      },
      { idempotencyKey },
    );

    return NextResponse.json({
      id: session.id,
      url: session.url,
      mode: session.mode,
      payment_status: session.payment_status,
      idempotency_key: idempotencyKey,
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "Stripe error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
