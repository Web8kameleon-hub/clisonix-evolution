import { currentUser } from "@/lib/auth/server";
import { apiError, apiSuccess } from "@/lib/api/response";
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
    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey || !stripeSecretKey.startsWith("sk_")) {
      return apiError(
        "STRIPE_NOT_CONFIGURED",
        "Stripe billing portal is not configured",
        {
          status: 503,
        },
      );
    }

    const stripe = new Stripe(stripeSecretKey, {});
    const body = await request.json().catch(() => ({}));
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

    const customers = await stripe.customers.list({
      email: customerEmail,
      limit: 1,
    });

    if (customers.data.length === 0) {
      return apiError(
        "CUSTOMER_NOT_FOUND",
        "No Stripe customer was found for this account",
        {
          status: 404,
          details: { customerEmail },
        },
      );
    }

    const session = await stripe.billingPortal.sessions.create({
      customer: customers.data[0].id,
      return_url:
        body.returnUrl || `${resolveBaseUrl(request)}/modules/account`,
    });

    await trackEconomyServer({
      economy_code: "CTU",
      slot: "billing",
      placement_id: "billing-portal-opened",
      metadata: {
        customerId: customers.data[0].id,
      },
    });

    return apiSuccess({
      url: session.url,
      customerId: customers.data[0].id,
    });
  } catch (error: unknown) {
    await trackEconomyServer({
      economy_code: "CTF",
      slot: "billing",
      placement_id: "billing-portal-error",
      metadata: {
        message: error instanceof Error ? error.message : String(error),
      },
    });
    return apiError(
      "BILLING_PORTAL_ERROR",
      "Failed to create billing portal session",
      {
        status: 500,
        details: error instanceof Error ? error.message : String(error),
      },
    );
  }
}
