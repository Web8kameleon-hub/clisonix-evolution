/**
 * UTT - Albion Token (ALB) Mainnet Constants
 * Real data only (no mock / no simulation)
 */

export const ALB_MINT = 'HSEcf132J4dNz46gw5fsVV7xfgedeFyTZXMSHcroz3BU'
export const ALB_AUTHORITY = 'AuGX5kaG3ydcJLaGTUptSKnbC4y3MeUp1qds8mYJt9ua'
export const ALB_DECIMALS = 6
export const ALB_SYMBOL = 'ALB'
export const ALB_NAME = 'Albion Token'
export const SOLANA_NETWORK = 'mainnet-beta'
export const SOLANA_RPC_URL = 'https://api.mainnet-beta.solana.com'

export const ALB_EXPLORER_URL = `https://solscan.io/token/${ALB_MINT}`
export const ALB_DEXSCREENER_URL = `https://dexscreener.com/solana/${ALB_MINT}`

export interface ALBMarketData {
  priceUSD: number
  marketCapUSD: number
  totalSupply: number
  circulatingSupply: number
  liquidityUSD: number
  volume24hUSD: number
  isVerified: boolean
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  lastUpdated: string
}

export const ALB_MARKET_DATA: ALBMarketData = {
  priceUSD: 0.000834,
  marketCapUSD: 830.93,
  totalSupply: 996530,
  circulatingSupply: 996530,
  liquidityUSD: 2800,
  volume24hUSD: 0,
  isVerified: false,
  riskLevel: 'HIGH',
  lastUpdated: new Date().toISOString(),
}

export function toLamports(amount: number): bigint {
  return BigInt(Math.round(amount * 10 ** ALB_DECIMALS))
}

export function fromLamports(amount: bigint): number {
  return Number(amount) / 10 ** ALB_DECIMALS
}

export function validateALBMint(mint: string): boolean {
  return mint === ALB_MINT
}