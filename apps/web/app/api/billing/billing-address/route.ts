/**
 * Stripe Billing Address API
 * GET/PUT /api/billing/billing-address - Manage customer billing address
 */

import { currentUser } from "@/lib/auth/server";
import { apiError, apiSuccess } from "@/lib/api/response";
import Stripe from "stripe";

interface BillingAddress {
  line1: string;
  line2?: string;
  city: string;
  state?: string;
  postal_code: string;
  country: string;
  name?: string;
  phone?: string;
}

export async function GET() {
  try {
    // Check if Stripe is configured
    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey || !stripeSecretKey.startsWith("sk_")) {
      return apiSuccess({
        billingAddress: null,
        message: "Stripe not configured",
      });
    }

    const stripe = new Stripe(stripeSecretKey, {});

    // Get customer email from session/auth
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
        billingAddress: null,
        message: "No customer found",
      });
    }

    const customer = customers.data[0];
    const address = customer.address;

    if (!address || !address.line1) {
      return apiSuccess({
        billingAddress: null,
        message: "No billing address set",
      });
    }

    const billingAddress: BillingAddress = {
      line1: address.line1,
      line2: address.line2 || undefined,
      city: address.city || "",
      state: address.state || undefined,
      postal_code: address.postal_code || "",
      country: address.country || "",
      name: customer.name || undefined,
      phone: customer.phone || undefined,
    };

    return apiSuccess({
      billingAddress,
    });
  } catch (error: unknown) {
    console.error("Error fetching billing address:", error);
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to fetch billing address";
    return apiError(
      "BILLING_ADDRESS_FETCH_FAILED",
      "Failed to fetch billing address",
      {
        status: 500,
        details: errorMessage,
      },
    );
  }
}

export async function PUT(request: Request) {
  try {
    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey || !stripeSecretKey.startsWith("sk_")) {
      return apiError("STRIPE_NOT_CONFIGURED", "Stripe not configured", {
        status: 400,
      });
    }

    const stripe = new Stripe(stripeSecretKey, {});

    const billingAddress: BillingAddress = await request.json();

    // Validate required fields
    if (
      !billingAddress.line1 ||
      !billingAddress.city ||
      !billingAddress.postal_code ||
      !billingAddress.country
    ) {
      return apiError("VALIDATION_ERROR", "Missing required address fields", {
        status: 400,
      });
    }

    // Get customer
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
      return apiError("CUSTOMER_NOT_FOUND", "Customer not found", {
        status: 404,
      });
    }

    const customerId = customers.data[0].id;

    // Update customer address
    await stripe.customers.update(customerId, {
      address: {
        line1: billingAddress.line1,
        line2: billingAddress.line2 || undefined,
        city: billingAddress.city,
        state: billingAddress.state || undefined,
        postal_code: billingAddress.postal_code,
        country: billingAddress.country,
      },
      name: billingAddress.name || undefined,
      phone: billingAddress.phone || undefined,
    });

    return apiSuccess({
      message: "Billing address updated",
    });
  } catch (error: unknown) {
    console.error("Error updating billing address:", error);
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to update billing address";
    return apiError(
      "BILLING_ADDRESS_UPDATE_FAILED",
      "Failed to update billing address",
      {
        status: 500,
        details: errorMessage,
      },
    );
  }
}

