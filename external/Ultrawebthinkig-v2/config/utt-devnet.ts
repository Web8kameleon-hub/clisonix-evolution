/**
 * ALB Token - Solana Mainnet Configuration
 * Real production values - no devnet, no mocks, no random keypairs
 *
 * Mint verified: https://solscan.io/token/HSEcf132J4dNz46gw5fsVV7xfgedeFyTZXMSHcroz3BU
 * DexScreener: https://dexscreener.com/solana/HSEcf132J4dNz46gw5fsVV7xfgedeFyTZXMSHcroz3BU
 *
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.2.0
 * @license MIT
 */

// Real ALB Token mainnet mint (verified on Solana Explorer & DexScreener)
export const ALB_MINT = 'HSEcf132J4dNz46gw5fsVV7xfgedeFyTZXMSHcroz3BU'

// Real mainnet authority wallet
export const ALB_AUTHORITY = 'AuGX5kaG3ydcJLaGTUptSKnbC4y3MeUp1qds8mYJt9ua'

// Real mainnet configuration - loaded from env, no hardcoded placeholders
export const ALB_CONFIG = {
  network: (process.env.SOLANA_NETWORK || 'mainnet-beta') as 'mainnet-beta' | 'devnet' | 'testnet',
  rpcUrl: process.env.SOLANA_RPC_URL || 'https://api.mainnet-beta.solana.com',
  mintAddress: process.env.SOLANA_ALB_MINT || ALB_MINT,
  authority: process.env.SOLANA_ALB_AUTHORITY || ALB_AUTHORITY,
  decimals: 6,
  symbol: 'ALB',
  name: 'Albion Token',
  explorerUrl: `https://solscan.io/token/${ALB_MINT}`,
  dexscreenerUrl: `https://dexscreener.com/solana/${ALB_MINT}`,
  euroPerALB: Number(process.env.ALB_EUR_RATE) || 100.0,
  usdPerALB: Number(process.env.ALB_USD_RATE) || 108.5,
  mainnetTransfersEnabled: process.env.UTT_MAINNET_TRANSFERS === 'on',
  rateLimitPerDay: Number(process.env.UTT_RATE_LIMIT_PER_DAY) || 10,
  // Bridge keypair must be set via SOLANA_BRIDGE_KEYPAIR_B58 env var - never generated randomly
  bridgeKeypairConfigured: !!process.env.SOLANA_BRIDGE_KEYPAIR_B58,
}

export default ALB_CONFIG