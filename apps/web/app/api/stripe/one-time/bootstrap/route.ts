import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";

const getStripe = () => {
  if (!process.env.STRIPE_SECRET_KEY) {
    throw new Error("STRIPE_SECRET_KEY is not configured");
  }
  return new Stripe(process.env.STRIPE_SECRET_KEY, {});
};

type BootstrapPayload = {
  name?: string;
  currency?: string;
  unit_amount?: number;
  quantity?: number;
  success_url?: string;
  cancel_url?: string;
};

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json().catch(() => ({}))) as BootstrapPayload;

    const name = body.name || "Example Product";
    const currency = (body.currency || "usd").toLowerCase();
    const unitAmount = Number(body.unit_amount ?? 2000);
    const quantity = Number(body.quantity ?? 1);
    const idempotencyFromHeader =
      request.headers.get("idempotency-key") ||
      request.headers.get("x-idempotency-key") ||
      undefined;
    const idempotencyFromBody =
      typeof (body as Record<string, unknown>).idempotency_key === "string"
        ? ((body as Record<string, unknown>).idempotency_key as string)
        : undefined;
    const baseIdempotencyKey =
      idempotencyFromBody ||
      idempotencyFromHeader ||
      `boot:${name}:${currency}:${unitAmount}:${quantity}:${Date.now()}`;

    if (
      !name ||
      Number.isNaN(unitAmount) ||
      unitAmount <= 0 ||
      Number.isNaN(quantity) ||
      quantity <= 0
    ) {
      return NextResponse.json(
        {
          error: "Invalid payload",
          required: {
            name: "string",
            currency: "string (e.g. usd, eur)",
            unit_amount: "positive integer in minor units",
            quantity: "positive integer",
          },
        },
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

    const product = await stripe.products.create(
      {
        name,
        default_price_data: {
          currency,
          unit_amount: unitAmount,
        },
      },
      { idempotencyKey: `${baseIdempotencyKey}:product` },
    );

    const defaultPriceId =
      typeof product.default_price === "string"
        ? product.default_price
        : product.default_price?.id;

    if (!defaultPriceId) {
      return NextResponse.json(
        { error: "Product created but no default_price returned" },
        { status: 500 },
      );
    }

    const session = await stripe.checkout.sessions.create(
      {
        line_items: [
          {
            price: defaultPriceId,
            quantity,
          },
        ],
        mode: "payment",
        success_url: successUrl,
        cancel_url: cancelUrl,
        metadata: {
          product_id: product.id,
          price_id: defaultPriceId,
          quantity: String(quantity),
        },
      },
      { idempotencyKey: `${baseIdempotencyKey}:checkout` },
    );

    return NextResponse.json({
      product: {
        id: product.id,
        name: product.name,
        default_price: defaultPriceId,
      },
      checkout_session: {
        id: session.id,
        url: session.url,
        mode: session.mode,
        payment_status: session.payment_status,
      },
      idempotency_key: baseIdempotencyKey,
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "Stripe bootstrap error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
