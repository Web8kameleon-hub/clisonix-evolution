/**
 * Stripe Subscription API
 * GET /api/billing/subscription - Get customer's active subscription
 */

import { currentUser } from "@/lib/auth/server";
import { apiError, apiSuccess } from "@/lib/api/response";
import Stripe from "stripe";

export async function GET() {
  try {
    // Check if Stripe is configured
    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey || !stripeSecretKey.startsWith("sk_")) {
      return apiSuccess({
        subscription: null,
        message: "Stripe not configured",
      });
    }

    const stripe = new Stripe(stripeSecretKey, {});

    // Get customer email from the authenticated session
    const user = await currentUser();
    if (!user) {
      return apiError("UNAUTHORIZED", "Authentication required", {
        status: 401,
      });
    }

    const customerEmail = user.emailAddresses?.[0]?.emailAddress;
    if (!customerEmail) {
      return apiError("USER_EMAIL_MISSING", "User email is required", {
        status: 400,
      });
    }

    // Search for customer by email
    const customers = await stripe.customers.list({
      email: customerEmail,
      limit: 1,
    });

    if (customers.data.length === 0) {
      return apiSuccess({
        subscription: null,
        message: "No customer found",
      });
    }

    const customerId = customers.data[0].id;

    // Fetch active subscriptions
    const subscriptions = await stripe.subscriptions.list({
      customer: customerId,
      status: "all",
      limit: 1,
    });

    if (subscriptions.data.length === 0) {
      return apiSuccess({
        subscription: null,
        message: "No subscription found",
      });
    }

    const sub = subscriptions.data[0];
    const priceItem = sub.items?.data?.[0];

    // Determine plan name from price metadata or product name
    let planName = "Unknown";
    if (priceItem?.price?.product) {
      try {
        const product = await stripe.products.retrieve(
          priceItem.price.product as string,
        );
        planName = product.name || "Clisonix Plan";
      } catch {
        planName = "Clisonix Plan";
      }
    }

    // Map Stripe status to our status
    const statusMap: Record<string, string> = {
      active: "active",
      canceled: "canceled",
      past_due: "past_due",
      trialing: "trialing",
      incomplete: "pending",
      incomplete_expired: "expired",
      unpaid: "past_due",
    };

    const subscription = {
      id: sub.id,
      plan: planName,
      status: statusMap[sub.status] || sub.status,
      currentPeriodStart: new Date(
        ((sub as unknown as Record<string, number>).current_period_start || 0) *
          1000,
      ).toISOString(),
      currentPeriodEnd: new Date(
        ((sub as unknown as Record<string, number>).current_period_end || 0) *
          1000,
      ).toISOString(),
      cancelAtPeriodEnd: sub.cancel_at_period_end || false,
      amount: (priceItem?.price?.unit_amount || 0) / 100,
      currency: priceItem?.price?.currency?.toUpperCase() || "EUR",
      interval: priceItem?.price?.recurring?.interval || "month",
    };

    return apiSuccess({
      subscription,
    });
  } catch (error: unknown) {
    console.error("Error fetching subscription:", error);
    const errorMessage =
      error instanceof Error ? error.message : "Failed to fetch subscription";
    return apiError(
      "SUBSCRIPTION_FETCH_FAILED",
      "Failed to fetch subscription",
      {
        status: 500,
        details: errorMessage,
      },
    );
  }
}

// Cancel subscription
export async function DELETE(request: Request) {
  try {
    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey || !stripeSecretKey.startsWith("sk_")) {
      return apiError("STRIPE_NOT_CONFIGURED", "Stripe not configured", {
        status: 400,
      });
    }

    const stripe = new Stripe(stripeSecretKey, {});

    const { subscriptionId, cancelAtPeriodEnd = true } = await request.json();

    if (!subscriptionId) {
      return apiError("VALIDATION_ERROR", "Subscription ID required", {
        status: 400,
      });
    }

    if (cancelAtPeriodEnd) {
      // Cancel at end of billing period
      await stripe.subscriptions.update(subscriptionId, {
        cancel_at_period_end: true,
      });
    } else {
      // Cancel immediately
      await stripe.subscriptions.cancel(subscriptionId);
    }

    return apiSuccess({
      message: cancelAtPeriodEnd
        ? "Subscription will cancel at end of billing period"
        : "Subscription canceled immediately",
    });
  } catch (error: unknown) {
    console.error("Error canceling subscription:", error);
    const errorMessage =
      error instanceof Error ? error.message : "Failed to cancel subscription";
    return apiError(
      "SUBSCRIPTION_CANCEL_FAILED",
      "Failed to cancel subscription",
      {
        status: 500,
        details: errorMessage,
      },
    );
  }
}

