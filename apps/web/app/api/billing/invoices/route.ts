/**
 * Stripe Invoices API
 * GET /api/billing/invoices - Get customer invoices from Stripe
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
        invoices: [],
        message: "Stripe not configured - no invoices available",
      });
    }

    const stripe = new Stripe(stripeSecretKey, {});

    // Get customer email from session/auth (in production, get from authenticated user)
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
        invoices: [],
        message: "No customer found",
      });
    }

    const customerId = customers.data[0].id;

    // Fetch invoices for this customer
    const stripeInvoices = await stripe.invoices.list({
      customer: customerId,
      limit: 50,
    });

    // Transform to our format
    const invoices = stripeInvoices.data.map((invoice) => ({
      id: invoice.number || invoice.id,
      date: new Date((invoice.created || 0) * 1000).toISOString(),
      amount: (invoice.amount_paid || 0) / 100,
      currency: invoice.currency?.toUpperCase() || "EUR",
      status:
        invoice.status === "paid"
          ? "paid"
          : invoice.status === "open"
            ? "pending"
            : "failed",
      pdfUrl: invoice.invoice_pdf || undefined,
      hostedUrl: invoice.hosted_invoice_url || undefined,
      description:
        invoice.description ||
        invoice.lines?.data?.[0]?.description ||
        "Clisonix Subscription",
    }));

    return apiSuccess({
      invoices,
      total: stripeInvoices.data.length,
    });
  } catch (error: unknown) {
    console.error("Error fetching invoices:", error);
    const errorMessage =
      error instanceof Error ? error.message : "Failed to fetch invoices";
    return apiError("INVOICES_FETCH_FAILED", "Failed to fetch invoices", {
      status: 500,
      details: errorMessage,
    });
  }
}

