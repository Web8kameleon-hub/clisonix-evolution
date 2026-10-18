import { NextResponse } from "next/server";
import Stripe from "stripe";
import { stripeClient } from "@/lib/billing/checkout";
export { POST } from "../../billing/checkout/route";

export async function GET() {
  try {
    const stripe = stripeClient();
    const prices = await stripe.prices.list({
      active: true,
      type: "recurring",
      expand: ["data.product"],
      limit: 100,
    });

    const plans = prices.data
      .filter((price) => price.recurring?.interval)
      .map((price) => {
        const product =
          typeof price.product === "string"
            ? null
            : (price.product as Stripe.Product);

        return {
          id: price.id,
          name: product?.name || "",
          interval: price.recurring?.interval,
          amount: (price.unit_amount || 0) / 100,
          currency: (price.currency || "eur").toUpperCase(),
          features: product?.metadata?.features
            ? String(product.metadata.features)
                .split("|")
                .map((entry) => entry.trim())
                .filter(Boolean)
            : [],
        };
      });

    return NextResponse.json({ plans });
  } catch (error) {
    return NextResponse.json(
      {
        error: error instanceof Error ? error.message : "Failed to fetch plans",
      },
      { status: 500 },
    );
  }
}
