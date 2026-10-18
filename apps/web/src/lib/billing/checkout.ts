import Stripe from "stripe";

export function stripeClient() {
  const key = process.env.STRIPE_SECRET_KEY || process.env.STRIPE_API_KEY;
  if (!key?.startsWith("sk_")) throw new Error("STRIPE_NOT_CONFIGURED");
  return new Stripe(key);
}

export function checkoutOrigin(request: Request): string {
  return new URL(process.env.NEXT_PUBLIC_APP_URL || request.url).origin;
}

export function checkoutRedirect(request: Request, value: unknown, fallback: string): string {
  const origin = checkoutOrigin(request);
  const result = new URL(typeof value === "string" && value ? value : fallback, origin);
  if (result.origin !== origin || !["http:", "https:"].includes(result.protocol)) {
    throw new Error("INVALID_CHECKOUT_REDIRECT");
  }
  return result.toString();
}

export function planForPrice(priceId: string): string | undefined {
  for (const [key, value] of Object.entries(process.env)) {
    if (key.startsWith("STRIPE_PRICE_") && value && value === priceId) {
      const name = key.slice("STRIPE_PRICE_".length).split("_")[0].toLowerCase();
      const plan = name === "pro" ? "professional" : name;
      if (["starter", "standard", "professional", "enterprise", "free"].includes(plan)) return plan;
    }
  }
  return undefined;
}
