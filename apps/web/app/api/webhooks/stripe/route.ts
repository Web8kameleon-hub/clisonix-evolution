/**
 * Clisonix Cloud - Stripe Webhook Handler
 *
 * Handles all Stripe webhook events for subscriptions
 *
 * @author Ledjan Ahmati
 * @copyright 2026 Clisonix Cloud
 */

import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { trackEconomyServer } from "@/lib/economy/track";

// Initialize Stripe lazily to avoid build-time errors
const getStripe = () => {
  const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
  if (!stripeSecretKey || !stripeSecretKey.startsWith("sk_")) {
    throw new Error("STRIPE_SECRET_KEY is not configured");
  }
  return new Stripe(stripeSecretKey, {
    apiVersion: "2024-12-18.acacia" as Stripe.LatestApiVersion,
  });
};

const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

// Subscription plan mapping
const PLAN_MAPPING: Record<string, string> = {};

if (process.env.STRIPE_PRICE_STARTER_MONTHLY) {
  PLAN_MAPPING[process.env.STRIPE_PRICE_STARTER_MONTHLY] = "starter";
}
if (process.env.STRIPE_PRICE_STARTER_YEARLY) {
  PLAN_MAPPING[process.env.STRIPE_PRICE_STARTER_YEARLY] = "starter";
}
if (process.env.STRIPE_PRICE_PROFESSIONAL_MONTHLY) {
  PLAN_MAPPING[process.env.STRIPE_PRICE_PROFESSIONAL_MONTHLY] = "professional";
}
if (process.env.STRIPE_PRICE_PROFESSIONAL_YEARLY) {
  PLAN_MAPPING[process.env.STRIPE_PRICE_PROFESSIONAL_YEARLY] = "professional";
}
if (process.env.STRIPE_PRICE_ENTERPRISE_MONTHLY) {
  PLAN_MAPPING[process.env.STRIPE_PRICE_ENTERPRISE_MONTHLY] = "enterprise";
}
if (process.env.STRIPE_PRICE_ENTERPRISE_YEARLY) {
  PLAN_MAPPING[process.env.STRIPE_PRICE_ENTERPRISE_YEARLY] = "enterprise";
}

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get("stripe-signature");

  if (!webhookSecret) {
    console.error("STRIPE_WEBHOOK_SECRET is not configured");
    return NextResponse.json(
      { error: "Webhook not configured" },
      { status: 503 },
    );
  }

  if (!signature) {
    return NextResponse.json(
      { error: "Missing stripe-signature header" },
      { status: 400 },
    );
  }

  let event: Stripe.Event;
  const stripe = getStripe();

  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err) {
    console.error("⚠️ Webhook signature verification failed:", err);
    return NextResponse.json({ error: "Invalid signature" }, { status: 400 });
  }

  try {
    switch (event.type) {
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;
        await handleCheckoutComplete(session, event.id);
        break;
      }

      case "customer.subscription.created":
      case "customer.subscription.updated": {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionUpdate(subscription);
        break;
      }

      case "customer.subscription.deleted": {
        const subscription = event.data.object as Stripe.Subscription;
        await handleSubscriptionCancelled(subscription);
        break;
      }

      case "invoice.payment_succeeded": {
        const invoice = event.data.object as Stripe.Invoice;
        await handlePaymentSucceeded(invoice);
        break;
      }

      case "invoice.payment_failed": {
        const invoice = event.data.object as Stripe.Invoice;
        await handlePaymentFailed(invoice);
        break;
      }

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error("Error processing webhook:", error);
    return NextResponse.json(
      { error: "Webhook processing failed" },
      { status: 500 },
    );
  }
}

async function handleCheckoutComplete(
  session: Stripe.Checkout.Session,
  eventId: string,
) {
  console.log("✅ Checkout completed:", session.id);

  if (session.mode === "payment") {
    const amountTotal = session.amount_total ?? undefined;
    const lineItemPriceId =
      session.line_items?.data?.[0]?.price?.id ||
      (typeof session.metadata?.price_id === "string"
        ? session.metadata.price_id
        : undefined);
    const lineItemProductId =
      typeof session.metadata?.product_id === "string"
        ? session.metadata.product_id
        : undefined;

    await persistOneTimePayment({
      stripe_event_id: eventId,
      session_id: session.id,
      payment_intent_id:
        typeof session.payment_intent === "string"
          ? session.payment_intent
          : undefined,
      stripe_customer_id:
        typeof session.customer === "string" ? session.customer : undefined,
      customer_email: session.customer_email || undefined,
      amount_total: amountTotal,
      currency: session.currency || undefined,
      payment_status: session.payment_status || undefined,
      product_id: lineItemProductId,
      price_id: lineItemPriceId,
      quantity:
        typeof session.metadata?.quantity === "string"
          ? Number(session.metadata.quantity)
          : undefined,
      metadata: session.metadata || undefined,
    });

    console.log("💳 One-time payment confirmed:", {
      sessionId: session.id,
      customerId: session.customer,
      customerEmail: session.customer_email,
      paymentStatus: session.payment_status,
      amountTotal: session.amount_total,
      currency: session.currency,
    });
    return;
  }

  const customerId = session.customer as string;
  const customerEmail = session.customer_email;
  const subscriptionId = session.subscription as string;

  await trackEconomyServer({
    economy_code: "CTG",
    slot: "billing",
    placement_id: "checkout-completed",
    value: session.amount_total ? session.amount_total / 100 : undefined,
    currency: session.currency || undefined,
    metadata: {
      eventId,
      sessionId: session.id,
      customerId,
      subscriptionId,
      customerEmail,
    },
  });

  // Update user in database
  await updateUserSubscription({
    email: customerEmail!,
    stripeCustomerId: customerId,
    subscriptionId: subscriptionId,
    status: "active",
  });
}

async function handleSubscriptionUpdate(subscription: Stripe.Subscription) {
  console.log("📝 Subscription updated:", subscription.id);

  const customerId = subscription.customer as string;
  const priceId = subscription.items.data[0]?.price.id;
  const plan = PLAN_MAPPING[priceId] || "free";

  await updateUserSubscription({
    stripeCustomerId: customerId,
    subscriptionId: subscription.id,
    plan: plan,
    status: subscription.status,
    currentPeriodEnd: new Date(
      (subscription as unknown as { current_period_end: number })
        .current_period_end * 1000,
    ),
  });
}

async function handleSubscriptionCancelled(subscription: Stripe.Subscription) {
  console.log("❌ Subscription cancelled:", subscription.id);

  const customerId = subscription.customer as string;

  await updateUserSubscription({
    stripeCustomerId: customerId,
    subscriptionId: subscription.id,
    plan: "free",
    status: "cancelled",
  });
}

async function handlePaymentSucceeded(invoice: Stripe.Invoice) {
  console.log("💰 Payment succeeded:", invoice.id);
  await trackEconomyServer({
    economy_code:
      invoice.billing_reason === "subscription_create" ? "CTP" : "CTG",
    slot: "billing",
    placement_id: "invoice-payment-succeeded",
    value: invoice.amount_paid ? invoice.amount_paid / 100 : undefined,
    currency: invoice.currency || undefined,
    metadata: {
      invoiceId: invoice.id,
      customerId:
        typeof invoice.customer === "string" ? invoice.customer : undefined,
      billingReason: invoice.billing_reason || undefined,
    },
  });
  // Log successful payment for analytics
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  console.log("⚠️ Payment failed:", invoice.id);
  await trackEconomyServer({
    economy_code: "CTF",
    slot: "billing",
    placement_id: "invoice-payment-failed",
    value: invoice.amount_due ? invoice.amount_due / 100 : undefined,
    currency: invoice.currency || undefined,
    metadata: {
      invoiceId: invoice.id,
      customerId:
        typeof invoice.customer === "string" ? invoice.customer : undefined,
      billingReason: invoice.billing_reason || undefined,
    },
  });
  // Send notification to user, update status
}

interface SubscriptionUpdate {
  email?: string;
  stripeCustomerId: string;
  subscriptionId: string;
  plan?: string;
  status: string;
  currentPeriodEnd?: Date;
}

interface OneTimePaymentSync {
  stripe_event_id: string;
  session_id: string;
  payment_intent_id?: string;
  stripe_customer_id?: string;
  customer_email?: string;
  amount_total?: number;
  currency?: string;
  payment_status?: string;
  product_id?: string;
  price_id?: string;
  quantity?: number;
  metadata?: Record<string, string>;
}

async function updateUserSubscription(data: SubscriptionUpdate) {
  // Call internal API to update user
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const internalApiKey = process.env.INTERNAL_API_KEY;

  if (!apiUrl || !internalApiKey) {
    console.error("Internal billing sync is not configured");
    return;
  }

  try {
    const response = await fetch(
      `${apiUrl}/api/v1/billing/internal/update-subscription`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Internal-Key": internalApiKey,
        },
        body: JSON.stringify(data),
      },
    );

    if (!response.ok) {
      throw new Error(`API responded with ${response.status}`);
    }

    console.log("✅ User subscription updated in database");
  } catch (error) {
    console.error("Failed to update user subscription:", error);
    // Don't throw - webhook should still return 200
  }
}

async function persistOneTimePayment(data: OneTimePaymentSync) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const internalApiKey = process.env.INTERNAL_API_KEY;

  if (!apiUrl || !internalApiKey) {
    console.error("Internal one-time billing sync is not configured");
    return;
  }

  try {
    const response = await fetch(
      `${apiUrl}/api/v1/billing/internal/record-one-time-payment`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Internal-Key": internalApiKey,
        },
        body: JSON.stringify(data),
      },
    );

    if (!response.ok) {
      throw new Error(`API responded with ${response.status}`);
    }

    console.log("✅ One-time payment persisted in billing DB");
  } catch (error) {
    console.error("Failed to persist one-time payment:", error);
  }
}
