/**
 * Stripe Payment Methods API
 * GET /api/billing/payment-methods - Get customer's saved payment methods
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
        paymentMethods: [],
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
        paymentMethods: [],
        message: "No customer found",
      });
    }

    const customer = customers.data[0];
    const customerId = customer.id;

    // Fetch payment methods for this customer
    const stripeMethods = await stripe.paymentMethods.list({
      customer: customerId,
      type: "card",
    });

    // Get default payment method
    const defaultMethodId =
      typeof customer.invoice_settings?.default_payment_method === "string"
        ? customer.invoice_settings.default_payment_method
        : customer.invoice_settings?.default_payment_method?.id;

    // Transform to our format
    const paymentMethods = stripeMethods.data.map((method) => ({
      id: method.id,
      type: "card" as const,
      last4: method.card?.last4 || "****",
      brand: method.card?.brand || "unknown",
      expiryMonth: method.card?.exp_month,
      expiryYear: method.card?.exp_year,
      isDefault: method.id === defaultMethodId,
    }));

    return apiSuccess({
      paymentMethods,
      total: paymentMethods.length,
    });
  } catch (error: unknown) {
    console.error("Error fetching payment methods:", error);
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to fetch payment methods";
    return apiError(
      "PAYMENT_METHODS_FETCH_FAILED",
      "Failed to fetch payment methods",
      {
        status: 500,
        details: errorMessage,
      },
    );
  }
}

// Set default payment method
export async function PUT(request: Request) {
  try {
    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey || !stripeSecretKey.startsWith("sk_")) {
      return apiError("STRIPE_NOT_CONFIGURED", "Stripe not configured", {
        status: 400,
      });
    }

    const stripe = new Stripe(stripeSecretKey, {});

    const { paymentMethodId } = await request.json();

    if (!paymentMethodId) {
      return apiError("VALIDATION_ERROR", "Payment method ID required", {
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

    // Set as default payment method
    await stripe.customers.update(customerId, {
      invoice_settings: {
        default_payment_method: paymentMethodId,
      },
    });

    return apiSuccess({
      message: "Default payment method updated",
    });
  } catch (error: unknown) {
    console.error("Error updating default payment method:", error);
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to update payment method";
    return apiError(
      "PAYMENT_METHOD_UPDATE_FAILED",
      "Failed to update payment method",
      {
        status: 500,
        details: errorMessage,
      },
    );
  }
}

// Delete payment method
export async function DELETE(request: Request) {
  try {
    const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
    if (!stripeSecretKey || !stripeSecretKey.startsWith("sk_")) {
      return apiError("STRIPE_NOT_CONFIGURED", "Stripe not configured", {
        status: 400,
      });
    }

    const stripe = new Stripe(stripeSecretKey, {});

    const { paymentMethodId } = await request.json();

    if (!paymentMethodId) {
      return apiError("VALIDATION_ERROR", "Payment method ID required", {
        status: 400,
      });
    }

    // Detach payment method from customer
    await stripe.paymentMethods.detach(paymentMethodId);

    return apiSuccess({
      message: "Payment method removed",
    });
  } catch (error: unknown) {
    console.error("Error removing payment method:", error);
    const errorMessage =
      error instanceof Error
        ? error.message
        : "Failed to remove payment method";
    return apiError(
      "PAYMENT_METHOD_DELETE_FAILED",
      "Failed to remove payment method",
      {
        status: 500,
        details: errorMessage,
      },
    );
  }
}

