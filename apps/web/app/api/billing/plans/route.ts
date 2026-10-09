import { apiError, apiSuccess } from "@/lib/api/response";
import Stripe from "stripe";

interface StripePlan {
  id: string;
  productId: string;
  name: string;
  description?: string;
  amount: number;
  currency: string;
  interval: "month" | "year";
  priceId: string;
  features: string[];
  popular: boolean;
  rank: number;
}

function getStripe() {
  const secretKey = process.env.STRIPE_SECRET_KEY;
  if (!secretKey || !secretKey.startsWith("sk_")) {
    return null;
  }

  return new Stripe(secretKey, {});
}

function parseFeatures(metadata: Stripe.Metadata | null | undefined): string[] {
  const raw = metadata?.features;
  if (!raw) {
    return [];
  }

  try {
    const parsed = JSON.parse(raw);
    if (Array.isArray(parsed)) {
      return parsed
        .map((entry) => String(entry).trim())
        .filter(Boolean);
    }
  } catch {
    return raw
      .split("|")
      .map((entry) => entry.trim())
      .filter(Boolean);
  }

  return [];
}

function parseRank(metadata: Stripe.Metadata | null | undefined): number {
  const raw = metadata?.rank;
  if (!raw) {
    return Number.MAX_SAFE_INTEGER;
  }

  const parsed = Number(raw);
  return Number.isFinite(parsed) ? parsed : Number.MAX_SAFE_INTEGER;
}

function parsePopular(metadata: Stripe.Metadata | null | undefined): boolean {
  return metadata?.popular === "true";
}

export async function GET() {
  try {
    const stripe = getStripe();
    if (!stripe) {
      return apiError("STRIPE_NOT_CONFIGURED", "Stripe is not configured", {
        status: 503,
      });
    }

    const prices = await stripe.prices.list({
      active: true,
      expand: ["data.product"],
      limit: 100,
      type: "recurring",
    });

    const plans: StripePlan[] = prices.data
      .filter((price) => {
        const interval = price.recurring?.interval;
        return interval === "month" || interval === "year";
      })
      .map((price) => {
        const product =
          typeof price.product === "string" ? null : (price.product as Stripe.Product);

        return {
          id: price.id,
          productId: typeof price.product === "string" ? price.product : price.product.id,
          name: product?.name || "",
          description: product?.description || undefined,
          amount: (price.unit_amount || 0) / 100,
          currency: (price.currency || "eur").toUpperCase(),
          interval: price.recurring?.interval as "month" | "year",
          priceId: price.id,
          features: parseFeatures(product?.metadata),
          popular: parsePopular(product?.metadata),
          rank: parseRank(product?.metadata),
        };
      })
      .sort((left, right) => {
        if (left.rank !== right.rank) {
          return left.rank - right.rank;
        }

        if (left.amount !== right.amount) {
          return left.amount - right.amount;
        }

        return left.name.localeCompare(right.name);
      });

    return apiSuccess({ plans });
  } catch (error: unknown) {
    return apiError("PLANS_FETCH_FAILED", "Failed to fetch billing plans", {
      status: 500,
      details: error instanceof Error ? error.message : String(error),
    });
  }
}
