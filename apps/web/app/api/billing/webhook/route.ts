import { forwardStripeWebhook } from "@/lib/billing/stripe-webhook";

export const runtime = "nodejs";

export async function POST(request: Request) {
  return forwardStripeWebhook(request);
}
