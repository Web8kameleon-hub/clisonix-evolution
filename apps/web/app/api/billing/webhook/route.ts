/**
 * Stripe Webhook Handler
 * POST /api/billing/webhook - Handle Stripe events
 */

import { NextResponse } from "next/server";
import { headers } from "next/headers";
import Stripe from "stripe";

// Helper: Extract plan from Stripe subscription items
function extractPlanFromItems(
  items:
    | Stripe.SubscriptionItem[]
    | Stripe.ApiListPromise<Stripe.SubscriptionItem>
    | { data: Stripe.SubscriptionItem[] },
): string | undefined {
  let itemsArray: Stripe.SubscriptionItem[] = [];

  if (Array.isArray(items)) {
    itemsArray = items;
  } else if ('data' in items) {
    itemsArray = items.data;
  }

  if (itemsArray.length === 0) return undefined;

  const priceId = itemsArray[0].price?.id;
  if (!priceId) return undefined;

  // Map common price IDs to plans
  const priceMapping: Record<string, string> = {};
  const starterPrice = process.env.STRIPE_PRICE_STARTER_MONTHLY;
  const professionalPrice = process.env.STRIPE_PRICE_PROFESSIONAL_MONTHLY;
  const enterprisePrice = process.env.STRIPE_PRICE_ENTERPRISE_MONTHLY;

  if (starterPrice) priceMapping[starterPrice] = "starter";
  if (professionalPrice) priceMapping[professionalPrice] = "professional";
  if (enterprisePrice) priceMapping[enterprisePrice] = "enterprise";

  return priceMapping[priceId] || undefined;
}

// Helper: Call internal API to sync subscription state
async function notifyInternalAPI(data: Record<string, unknown>) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const internalKey = process.env.INTERNAL_API_KEY;

  if (!apiUrl || !internalKey) {
    console.error("Internal billing sync not configured");
    return false;
  }

  try {
    const response = await fetch(
      `${apiUrl}/api/v1/billing/internal/update-subscription`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Internal-Key": internalKey,
        },
        body: JSON.stringify(data),
      },
    );

    if (!response.ok) {
      console.error(
        `Internal API error: ${response.status}`,
        await response.text(),
      );
      return false;
    }

    console.log("✅ Subscription synced to internal API");
    return true;
  } catch (error) {
    console.error("Failed to notify internal API:", error);
    return false;
  }
}

async function notifyInternalOneTimeAPI(data: Record<string, unknown>) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  const internalKey = process.env.INTERNAL_API_KEY;

  if (!apiUrl || !internalKey) {
    console.error("Internal one-time billing sync not configured");
    return false;
  }

  try {
    const response = await fetch(
      `${apiUrl}/api/v1/billing/internal/record-one-time-payment`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Internal-Key": internalKey,
        },
        body: JSON.stringify(data),
      },
    );

    if (!response.ok) {
      console.error(
        `Internal one-time API error: ${response.status}`,
        await response.text(),
      );
      return false;
    }

    console.log("✅ One-time payment synced to internal API");
    return true;
  } catch (error) {
    console.error("Failed to notify internal one-time API:", error);
    return false;
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.text();
    const headersList = await headers();
    const signature = headersList.get("stripe-signature");

    if (
      !process.env.STRIPE_SECRET_KEY ||
      !process.env.STRIPE_WEBHOOK_SECRET ||
      !process.env.STRIPE_SECRET_KEY.startsWith("sk_")
    ) {
      console.error("Stripe not configured");
      return NextResponse.json(
        { error: "Stripe not configured" },
        { status: 400 },
      );
    }

    const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {});

    let event;

    try {
      event = stripe.webhooks.constructEvent(
        body,
        signature!,
        process.env.STRIPE_WEBHOOK_SECRET,
      );
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Webhook signature verification failed";
      console.error("Webhook signature verification failed:", errorMessage);
      return NextResponse.json({ error: errorMessage }, { status: 400 });
    }

    // Handle the event
    switch (event.type) {
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;
        console.log("✅ Checkout completed:", session.id);

        if (session.mode === "payment") {
          await notifyInternalOneTimeAPI({
            stripe_event_id: event.id,
            session_id: session.id,
            payment_intent_id:
              typeof session.payment_intent === "string"
                ? session.payment_intent
                : undefined,
            stripe_customer_id:
              typeof session.customer === "string" ? session.customer : undefined,
            customer_email: session.customer_email || undefined,
            amount_total: session.amount_total || undefined,
            currency: session.currency || undefined,
            payment_status: session.payment_status || undefined,
            product_id:
              typeof session.metadata?.product_id === "string"
                ? session.metadata.product_id
                : undefined,
            price_id:
              typeof session.metadata?.price_id === "string"
                ? session.metadata.price_id
                : undefined,
            quantity:
              typeof session.metadata?.quantity === "string"
                ? Number(session.metadata.quantity)
                : undefined,
            metadata: session.metadata || undefined,
          });
          break;
        }

        await notifyInternalAPI({
          stripeCustomerId: session.customer,
          subscriptionId: session.subscription,
          status: "active",
        });
        break;
      }

      case "customer.subscription.created": {
        const subscription = event.data.object;
        console.log("✅ Subscription created:", subscription.id);
        await notifyInternalAPI({
          stripeCustomerId: subscription.customer,
          subscriptionId: subscription.id,
          plan: extractPlanFromItems(subscription.items),
          status: "active",
          currentPeriodEnd: new Date(subscription.current_period_end * 1000),
        });
        break;
      }

      case "customer.subscription.updated": {
        const subscription = event.data.object;
        console.log("📝 Subscription updated:", subscription.id);
        await notifyInternalAPI({
          stripeCustomerId: subscription.customer,
          subscriptionId: subscription.id,
          plan: extractPlanFromItems(subscription.items),
          status: subscription.status,
          currentPeriodEnd: new Date(subscription.current_period_end * 1000),
        });
        break;
      }

      case "customer.subscription.deleted": {
        const subscription = event.data.object;
        console.log("❌ Subscription canceled:", subscription.id);
        await notifyInternalAPI({
          stripeCustomerId: subscription.customer,
          subscriptionId: subscription.id,
          plan: "free",
          status: "cancelled",
        });
        break;
      }

      case "invoice.paid": {
        const invoice = event.data.object;
        console.log("💰 Invoice paid:", invoice.id);
        await notifyInternalAPI({
          stripeCustomerId: invoice.customer,
          subscriptionId: invoice.subscription,
          status: "active",
        });
        break;
      }

      case "invoice.payment_failed": {
        const invoice = event.data.object;
        console.log("⚠️ Payment failed:", invoice.id);
        await notifyInternalAPI({
          stripeCustomerId: invoice.customer,
          subscriptionId: invoice.subscription,
          status: "past_due",
        });
        break;
      }

      default:
        console.log(`Unhandled event type: ${event.type}`);
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error("Webhook error:", error);
    return NextResponse.json(
      { error: "Webhook handler failed" },
      { status: 500 },
    );
  }
}

// Next.js 13+ App Router: body parsing is disabled by default for route handlers
// No config needed - raw body is available via request.text() or request.arrayBuffer()
