/**
 * Stripe Checkout API
 * POST /api/billing/checkout - Create Stripe Checkout session
 */

import { apiError, apiSuccess } from "@/lib/api/response";
import { currentUser } from "@/lib/auth/server";
import { trackEconomyServer } from "@/lib/economy/track";
import Stripe from "stripe";

function resolveBaseUrl(request: Request): string {
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

export async function POST(request: Request) {
  try {
    const { priceId, successUrl, cancelUrl } = await request.json();

    // Check if Stripe is configured
    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey || !stripeSecretKey.startsWith("sk_")) {
      return apiError("STRIPE_NOT_CONFIGURED", "Stripe not configured", {
        status: 503,
        details: "Please add STRIPE_SECRET_KEY to environment variables",
      });
    }

    const stripe = new Stripe(stripeSecretKey, {});

    if (typeof priceId !== "string" || !priceId.startsWith("price_")) {
      return apiError("INVALID_PLAN", `Invalid plan: ${priceId}`, {
        status: 400,
      });
    }

    const selectedPrice = await stripe.prices.retrieve(priceId, {
      expand: ["product"],
    });

    if (!selectedPrice.active || !selectedPrice.recurring) {
      return apiError(
        "INVALID_PRICE",
        "Selected price is not an active subscription",
        { status: 400 },
      );
    }

    const selectedProduct =
      typeof selectedPrice.product === "string" ? null : selectedPrice.product;
    const selectedProductName =
      selectedProduct && "name" in selectedProduct ? selectedProduct.name : "";

    const user = await currentUser();
    if (!user) {
      return apiError("UNAUTHORIZED", "Authentication required", {
        status: 401,
      });
    }

    const customerEmail = user.emailAddresses[0]?.emailAddress;
    if (!customerEmail) {
      return apiError("USER_EMAIL_MISSING", "User email is required", {
        status: 400,
      });
    }

    // Search for existing customer
    const existingCustomers = await stripe.customers.list({
      email: customerEmail,
      limit: 1,
    });

    let customerId: string;
    if (existingCustomers.data.length > 0) {
      customerId = existingCustomers.data[0].id;
    } else {
      // Create new customer
      const customer = await stripe.customers.create({
        email: customerEmail,
        name:
          `${user.firstName || ""} ${user.lastName || ""}`.trim() || undefined,
        metadata: {
          company: process.env.USER_COMPANY || "",
          user_id: user.id,
        },
      });
      customerId = customer.id;
    }

    const successUrlValue =
      successUrl ||
      `${resolveBaseUrl(request)}/modules/account?success=true&session_id={CHECKOUT_SESSION_ID}`;
    const cancelUrlValue =
      cancelUrl || `${resolveBaseUrl(request)}/modules/account?canceled=true`;

    // Create Checkout Session with existing Stripe price
    const session = await stripe.checkout.sessions.create({
      mode: "subscription",
      customer: customerId,
      payment_method_types: ["card"],
      line_items: [
        {
          price: selectedPrice.id,
          quantity: 1,
        },
      ],
      success_url: successUrlValue,
      cancel_url: cancelUrlValue,
      metadata: {
        planName: selectedProductName,
        priceId,
      },
      billing_address_collection: "required",
      allow_promotion_codes: false, // promo logic not yet implemented
    });

    await trackEconomyServer({
      economy_code: "CTD",
      slot: "billing",
      placement_id: "checkout-session-created",
      value: selectedPrice.unit_amount
        ? selectedPrice.unit_amount / 100
        : undefined,
      currency: selectedPrice.currency || undefined,
      metadata: {
        priceId,
        customerId,
        sessionId: session.id,
      },
    });

    return apiSuccess({
      sessionId: session.id,
      url: session.url,
    });
  } catch (error: unknown) {
    console.error("Stripe checkout error:", error);
    await trackEconomyServer({
      economy_code: "CTF",
      slot: "billing",
      placement_id: "checkout-error",
      metadata: {
        message: error instanceof Error ? error.message : "unknown",
      },
    });
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to create checkout session";
    return apiError(
      "CHECKOUT_CREATE_FAILED",
      "Failed to create checkout session",
      {
        status: 500,
        details: errorMessage,
      },
    );
  }
}
