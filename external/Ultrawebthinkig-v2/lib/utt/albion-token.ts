/**
 * UTT-Albion Token Definition
 * Industrial-Grade Blockchain Token Configuration
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 1.0.0 Industrial
 * @license MIT
 * @created August 25, 2025
 */

// Mock Solana PublicKey for development (will be replaced when @solana/web3.js is available)
class MockPublicKey {
  constructor(private value: string) {}
  toString(): string { return this.value }
  toBase58(): string { return this.value }
}

// Use mock or real PublicKey depending on availability
const PublicKey = (() => {
  try {
    // Try to import from @solana/web3.js
    // eslint-disable-next-line @typescript-eslint/no-var-requires
    return require('@solana/web3.js').PublicKey
  } catch {
    // Fallback to mock implementation
    return MockPublicKey
  }
})()

// ALB Token Configuration - Production Ready
export const ALB_TOKEN = {
  // Main token configuration
  mint: "HSEcf132J4dNz46gw5fsVV7xfgedeFyTZXMSHcroz3BU",
  symbol: "ALB",
  name: "Albion Token",
  decimals: 6,
  authority: "AuGX5kaG3ydcJLaGTUptSKnbC4y3MeUp1qds8mYJt9ua",
  
  // Economic configuration
  valueEUR: 1000, // 1 ALB = 1000 EUR
  valueUSD: 1100, // 1 ALB = 1100 USD (approximate)
  maxSupply: 1000000, // 1M ALB total supply
  circulatingSupply: 250000, // 250K ALB in circulation
  
  // Industrial metadata
  standard: "SPL", // Solana Program Library
  network: "mainnet-beta", // Solana mainnet
  launchDate: "2025-08-25",
  category: "Utility Token",
  
  // Technical specifications
  mintAuthority: new PublicKey("AuGX5kaG3ydcJLaGTUptSKnbC4y3MeUp1qds8mYJt9ua"),
  freezeAuthority: new PublicKey("AuGX5kaG3ydcJLaGTUptSKnbC4y3MeUp1qds8mYJt9ua"),
  
  // Transaction configuration
  minTransferAmount: 0.001, // 0.001 ALB minimum
  maxTransferAmount: 10000, // 10K ALB maximum per transaction
  transferFee: 0.0001, // 0.0001 ALB transfer fee
  
  // Physical token properties
  physicalToken: {
    diameter: "6cm",
    material: "Titanium-Alloy",
    nfcChip: "NTAG216",
    qrCodeFormat: "solana:{mint}?amount={amount}",
    antiCounterfeit: true,
    serialNumber: true
  }
} as const

// Token utility functions
export class ALBTokenUtils {
  /**
   * Convert ALB amount to EUR value
   */
  static toEUR(albAmount: number): number {
    return albAmount * ALB_TOKEN.valueEUR
  }

  /**
   * Convert EUR value to ALB amount
   */
  static fromEUR(eurAmount: number): number {
    return eurAmount / ALB_TOKEN.valueEUR
  }

  /**
   * Convert ALB amount to USD value
   */
  static toUSD(albAmount: number): number {
    return albAmount * ALB_TOKEN.valueUSD
  }

  /**
   * Convert USD value to ALB amount
   */
  static fromUSD(usdAmount: number): number {
    return usdAmount / ALB_TOKEN.valueUSD
  }

  /**
   * Format ALB amount for display
   */
  static formatALB(amount: number, precision = 6): string {
    return `${amount.toFixed(precision)} ALB`
  }

  /**
   * Format EUR value for display
   */
  static formatEUR(amount: number, precision = 2): string {
    return `€${amount.toFixed(precision)}`
  }

  /**
   * Format USD value for display
   */
  static formatUSD(amount: number, precision = 2): string {
    return `$${amount.toFixed(precision)}`
  }

  /**
   * Validate ALB amount
   */
  static isValidAmount(amount: number): boolean {
    return amount >= ALB_TOKEN.minTransferAmount && 
           amount <= ALB_TOKEN.maxTransferAmount &&
           amount > 0
  }

  /**
   * Calculate transfer fee
   */
  static calculateFee(amount: number): number {
    return Math.max(ALB_TOKEN.transferFee, amount * 0.001) // 0.1% or minimum fee
  }

  /**
   * Generate QR code data for physical token
   */
  static generateQRCode(amount: number): string {
    return `solana:${ALB_TOKEN.mint}?amount=${amount}`
  }

  /**
   * Parse QR code data
   */
  static parseQRCode(qrData: string): { mint: string; amount: number } | null {
    const match = qrData.match(/solana:([A-Za-z0-9]+)\?amount=([0-9.]+)/)
    if (match) {
      return {
        mint: match[1],
        amount: parseFloat(match[2])
      }
    }
    return null
  }

  /**
   * Validate token mint address
   */
  static isValidMint(mint: string): boolean {
    return mint === ALB_TOKEN.mint
  }

  /**
   * Get token supply statistics
   */
  static getSupplyStats() {
    return {
      total: ALB_TOKEN.maxSupply,
      circulating: ALB_TOKEN.circulatingSupply,
      locked: ALB_TOKEN.maxSupply - ALB_TOKEN.circulatingSupply,
      circulatingPercentage: (ALB_TOKEN.circulatingSupply / ALB_TOKEN.maxSupply) * 100
    }
  }

  /**
   * Convert lamports to ALB (considering decimals)
   */
  static lamportsToALB(lamports: number): number {
    return lamports / Math.pow(10, ALB_TOKEN.decimals)
  }

  /**
   * Convert ALB to lamports (considering decimals)
   */
  static albToLamports(alb: number): number {
    return Math.floor(alb * Math.pow(10, ALB_TOKEN.decimals))
  }
}

// Token event types for tracking
export interface ALBTokenEvent {
  type: 'transfer' | 'mint' | 'burn' | 'freeze' | 'thaw'
  from?: string
  to?: string
  amount: number
  timestamp: Date
  signature: string
  fee?: number
  memo?: string
}

// Token holder interface
export interface ALBTokenHolder {
  address: string
  balance: number
  balanceEUR: number
  balanceUSD: number
  firstTransactionDate: Date
  lastTransactionDate: Date
  transactionCount: number
  isPhysicalTokenHolder: boolean
  physicalTokenSerials?: string[]
}

// Export default configuration
export default ALB_TOKEN
