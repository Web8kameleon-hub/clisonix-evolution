import { currentUser } from "@/lib/auth/server";
import { checkoutRedirect } from "@/lib/billing/checkout";
import { apiError, apiSuccess } from "@/lib/api/response";
import { trackEconomyServer } from "@/lib/economy/track";
import Stripe from "stripe";

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
      limit: 100,
    });

    const customer = customers.data.find(candidate => candidate.metadata.user_id === user.id) ||
      customers.data.find(candidate => !candidate.metadata.user_id);
    if (!customer) {
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
      customer: customer.id,
      return_url:
        checkoutRedirect(request, body.returnUrl, "/modules/account"),
    });

    await trackEconomyServer({
      economy_code: "CTU",
      slot: "billing",
      placement_id: "billing-portal-opened",
      metadata: {
        customerId: customer.id,
      },
    });

    return apiSuccess({
      url: session.url,
      customerId: customer.id,
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
