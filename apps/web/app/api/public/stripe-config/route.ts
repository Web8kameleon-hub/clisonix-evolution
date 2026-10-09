import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

function looksLikeRealValue(value: string, prefix: string): boolean {
  if (!value) return false;
  if (!value.startsWith(prefix)) return false;
  if (/replace_me|your_|example|placeholder/i.test(value)) return false;
  return true;
}

export async function GET() {
  const publishableKey = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || "";
  const pricingTableId = process.env.NEXT_PUBLIC_STRIPE_PRICING_TABLE_ID || "";

  const configured =
    looksLikeRealValue(publishableKey, "pk_") &&
    looksLikeRealValue(pricingTableId, "prctbl_");

  return NextResponse.json(
    {
      configured,
      publishableKey,
      pricingTableId,
      source: "runtime-env",
    },
    {
      headers: {
        "Cache-Control": "no-store",
      },
    },
  );
}
