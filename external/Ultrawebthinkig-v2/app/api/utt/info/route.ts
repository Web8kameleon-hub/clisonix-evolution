import { NextResponse } from "next/server";

export async function GET() {
  const cluster   = process.env.NEXT_PUBLIC_CLUSTER ?? "devnet";
  const enabled   = (process.env.UTT_BRIDGE_ENABLED ?? "false") === "true";
  const mint      = process.env.NEXT_PUBLIC_UTT_MINT ?? process.env.UTT_MINT ?? null;
  const authority = process.env.NEXT_PUBLIC_UTT_AUTHORITY ?? process.env.UTT_AUTHORITY ?? null;

  // ✅ gjithmonë kthe numër
  const bridgeBalanceALB = Number(process.env.UTT_BRIDGE_BALANCE_ALB ?? "0");

  return NextResponse.json({
    network: cluster,
    status: enabled ? "ready" : "bridge_not_configured",
    transfersEnabled: enabled,
    mint,
    authority,
    bridgeBalanceALB,
  });
}
