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
    const body = await request.json().catch(() => ({}));
    const name: string = body.name || "Example Product";
    const currency: string = (body.currency || "usd").toLowerCase();
    const unitAmount: number = Number(body.unit_amount ?? 2000);

    if (!name || Number.isNaN(unitAmount) || unitAmount <= 0) {
      return NextResponse.json(
        { error: "Invalid product payload" },
        { status: 400 },
      );
    }

    const stripe = getStripe();
    const product = await stripe.products.create({
      name,
      default_price_data: {
        currency,
        unit_amount: unitAmount,
      },
    });

    return NextResponse.json({
      product_id: product.id,
      name: product.name,
      default_price: product.default_price,
    });
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "Stripe error";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
