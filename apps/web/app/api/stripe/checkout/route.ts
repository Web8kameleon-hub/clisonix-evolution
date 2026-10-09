/**
 * Clisonix Cloud - Stripe Checkout API
 *
 * Creates checkout sessions for subscription plans
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Clisonix Cloud
 */

import { NextRequest, NextResponse } from "next/server";
import { auth, currentUser } from "@/lib/auth/server";
import Stripe from "stripe";

function resolveBaseUrl(request: NextRequest): string {
  const forwardedProto = request.headers.get("x-forwarded-proto");
  const forwardedHost = request.headers.get("x-forwarded-host");
  const host = forwardedHost || request.headers.get("host");

  if (host) {
    return `${forwardedProto || "https"}://${host}`;
  }

  if (process.env.NEXT_PUBLIC_APP_URL) {
    return process.env.NEXT_PUBLIC_APP_URL;
  }

  throw new Error("APP_URL_NOT_CONFIGURED");
}

// Initialize Stripe lazily to avoid build-time errors
const getStripe = () => {
  if (!process.env.STRIPE_SECRET_KEY) {
    throw new Error("STRIPE_SECRET_KEY is not configured");
  }
  return new Stripe(process.env.STRIPE_SECRET_KEY, {
    apiVersion: "2024-12-18.acacia" as Stripe.LatestApiVersion,
  });
};

// Price IDs for each plan (configured via environment)
const PRICE_IDS: Record<string, Record<string, string>> = {
  starter: {
    monthly: process.env.STRIPE_PRICE_STARTER_MONTHLY || "",
    yearly: process.env.STRIPE_PRICE_STARTER_YEARLY || "",
  },
  professional: {
    monthly: process.env.STRIPE_PRICE_PROFESSIONAL_MONTHLY || "",
    yearly: process.env.STRIPE_PRICE_PROFESSIONAL_YEARLY || "",
  },
  enterprise: {
    monthly: process.env.STRIPE_PRICE_ENTERPRISE_MONTHLY || "",
    yearly: process.env.STRIPE_PRICE_ENTERPRISE_YEARLY || "",
  },
};

export async function POST(request: NextRequest) {
  try {
    const { userId } = await auth();

    if (!userId) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const user = await currentUser();
    if (!user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const customerEmail = user.emailAddresses[0]?.emailAddress;
    if (!customerEmail) {
      return NextResponse.json(
        { error: "User email is required" },
        { status: 400 },
      );
    }

    const body = await request.json();
    const { plan, interval = "monthly" } = body;
    const baseUrl = resolveBaseUrl(request);

    if (!plan || !PRICE_IDS[plan]) {
      return NextResponse.json({ error: "Invalid plan" }, { status: 400 });
    }

    const priceId = PRICE_IDS[plan][interval];
    if (!priceId) {
      return NextResponse.json({ error: "Invalid interval" }, { status: 400 });
    }

    const stripe = getStripe();

    // Create or retrieve Stripe customer
    let customerId: string;

    // Check if user already has a Stripe customer
    const existingCustomers = await stripe.customers.list({
      email: customerEmail,
      limit: 1,
    });

    if (existingCustomers.data.length > 0) {
      customerId = existingCustomers.data[0].id;
    } else {
      const customer = await stripe.customers.create({
        email: customerEmail,
        name:
          `${user?.firstName || ""} ${user?.lastName || ""}`.trim() ||
          undefined,
        metadata: {
          user_id: userId,
        },
      });
      customerId = customer.id;
    }

    // Create checkout session
    const session = await stripe.checkout.sessions.create({
      customer: customerId,
      payment_method_types: ["card"],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: "subscription",
      success_url: `${baseUrl}/subscription?success=true&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${baseUrl}/pricing?cancelled=true`,
      metadata: {
        user_id: userId,
        plan: plan,
        interval: interval,
      },
      subscription_data: {
        metadata: {
          user_id: userId,
          plan: plan,
        },
      },
      allow_promotion_codes: false, // promo logic not yet implemented
      billing_address_collection: "required",
    });

    return NextResponse.json({
      sessionId: session.id,
      url: session.url,
    });
  } catch (error) {
    console.error("Error creating checkout session:", error);
    return NextResponse.json(
      { error: "Failed to create checkout session" },
      { status: 500 },
    );
  }
}

export async function GET() {
  try {
    const stripe = getStripe();
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
