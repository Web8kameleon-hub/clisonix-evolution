/**
 * UTT-Albion Solana Connection Manager
 * Real RPC-based implementation (no mock / no random)
 */

export const SOLANA_CONFIG = {
  mainnet: 'https://api.mainnet-beta.solana.com',
  testnet: 'https://api.testnet.solana.com',
  devnet: 'https://api.devnet.solana.com',
  primary: process.env.SOLANA_RPC_URL || 'https://api.mainnet-beta.solana.com',
  commitment: 'confirmed' as const,
  timeout: 30000,
  maxRetries: 3,
  retryDelay: 1000,
}

export const ALB_MINT = 'HSEcf132J4dNz46gw5fsVV7xfgedeFyTZXMSHcroz3BU'
const ALB_DECIMALS = 6

interface SolanaTransaction {
  signature: string
  slot: number
  blockTime: number
  err: any
  memo?: string
  meta: {
    fee: number
    preBalances: number[]
    postBalances: number[]
    preTokenBalances: any[]
    postTokenBalances: any[]
  }
}

interface ALBBalance {
  address: string
  balance: number
  balanceLamports: number
  balanceEUR: number
  balanceUSD: number
  lastUpdated: Date
  isValid: boolean
}

export class AlbionConnection {
  private endpoint: string
  private isConnected = false
  private connectionAttempts = 0
  private maxConnectionAttempts = 5

  constructor(network: 'mainnet' | 'testnet' | 'devnet' = 'mainnet') {
    this.endpoint = process.env.SOLANA_RPC_URL || SOLANA_CONFIG[network]
    this.initializeConnection()
  }

  private async rpcCall<T = any>(method: string, params: any[] = []): Promise<T> {
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), SOLANA_CONFIG.timeout)

    try {
      const response = await fetch(this.endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }),
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new Error(`RPC HTTP ${response.status}`)
      }

      const json = await response.json()
      if (json.error) {
        throw new Error(json.error.message || 'RPC error')
      }

      return json.result as T
    } finally {
      clearTimeout(timeout)
    }
  }

  private async initializeConnection(): Promise<void> {
    try {
      await this.rpcCall('getHealth', [])
      this.isConnected = true
      this.connectionAttempts = 0
    } catch (error) {
      this.connectionAttempts++
      if (this.connectionAttempts < this.maxConnectionAttempts) {
        setTimeout(() => this.initializeConnection(), SOLANA_CONFIG.retryDelay)
      } else {
        console.error('Solana connection failed:', error)
      }
    }
  }

  async getALBBalance(address: string): Promise<ALBBalance> {
    this.ensureConnected()

    try {
      const result: any = await this.rpcCall('getTokenAccountsByOwner', [
        address,
        { mint: ALB_MINT },
        { encoding: 'jsonParsed' },
      ])

      const account = result?.value?.[0]
      const uiAmount = Number(account?.account?.data?.parsed?.info?.tokenAmount?.uiAmount || 0)
      const balanceLamports = Math.round(uiAmount * 10 ** ALB_DECIMALS)
      const eurRate = Number(process.env.ALB_EUR_RATE || 100)
      const usdRate = Number(process.env.ALB_USD_RATE || 108.5)

      return {
        address,
        balance: uiAmount,
        balanceLamports,
        balanceEUR: uiAmount * eurRate,
        balanceUSD: uiAmount * usdRate,
        lastUpdated: new Date(),
        isValid: true,
      }
    } catch (error) {
      console.error('Failed to get ALB balance:', error)
      return {
        address,
        balance: 0,
        balanceLamports: 0,
        balanceEUR: 0,
        balanceUSD: 0,
        lastUpdated: new Date(),
        isValid: false,
      }
    }
  }

  async getRecentTransactions(address: string, limit = 10): Promise<SolanaTransaction[]> {
    this.ensureConnected()

    try {
      const signatures: any[] = await this.rpcCall('getSignaturesForAddress', [
        address,
        { limit: Math.min(limit, 20) },
      ])

      return signatures.map((tx) => ({
        signature: tx.signature,
        slot: Number(tx.slot || 0),
        blockTime: Number(tx.blockTime || 0) * 1000,
        err: tx.err ?? null,
        memo: tx.memo || undefined,
        meta: {
          fee: 0,
          preBalances: [],
          postBalances: [],
          preTokenBalances: [],
          postTokenBalances: [],
        },
      }))
    } catch (error) {
      console.error('Failed to get recent transactions:', error)
      return []
    }
  }

  async monitorTransaction(txHash: string): Promise<{ status: string; confirmations: number }> {
    this.ensureConnected()

    try {
      const result: any = await this.rpcCall('getSignatureStatuses', [[txHash], { searchTransactionHistory: true }])
      const statusInfo = result?.value?.[0]

      if (!statusInfo) {
        return { status: 'not_found', confirmations: 0 }
      }

      const confirmations = Number(statusInfo.confirmations ?? 0)
      const status = statusInfo.err ? 'failed' : (statusInfo.confirmationStatus || 'processed')
      return { status, confirmations }
    } catch (error) {
      console.error('Failed to monitor transaction:', error)
      return { status: 'failed', confirmations: 0 }
    }
  }

  async getNetworkStatus(): Promise<{
    slot: number
    blockHeight: number
    blockhash: string
    feeCalculator: { lamportsPerSignature: number }
    health: string
    tps: number
  }> {
    this.ensureConnected()

    const [slot, blockHeight, latestBlockhash] = await Promise.all([
      this.rpcCall<number>('getSlot', []),
      this.rpcCall<number>('getBlockHeight', []),
      this.rpcCall<any>('getLatestBlockhash', []),
    ])

    return {
      slot: Number(slot || 0),
      blockHeight: Number(blockHeight || 0),
      blockhash: latestBlockhash?.value?.blockhash || '',
      feeCalculator: { lamportsPerSignature: 5000 },
      health: 'ok',
      tps: 0,
    }
  }

  async hasALBTokens(address: string): Promise<boolean> {
    const balance = await this.getALBBalance(address)
    return balance.balance > 0
  }

  async getALBPrice(): Promise<{ eur: number; usd: number; lastUpdated: Date }> {
    return {
      eur: Number(process.env.ALB_EUR_RATE || 100),
      usd: Number(process.env.ALB_USD_RATE || 108.5),
      lastUpdated: new Date(),
    }
  }

  private ensureConnected(): void {
    if (!this.isConnected) {
      throw new Error('Not connected to Solana network')
    }
  }

  disconnect(): void {
    this.isConnected = false
  }

  getStatus(): { connected: boolean; endpoint: string; attempts: number } {
    return {
      connected: this.isConnected,
      endpoint: this.endpoint,
      attempts: this.connectionAttempts,
    }
  }
}

let globalConnection: AlbionConnection | null = null

export function getAlbionConnection(network?: 'mainnet' | 'testnet' | 'devnet'): AlbionConnection {
  globalConnection ??= new AlbionConnection(network)
  return globalConnection
}

export async function checkALBBalance(address: string): Promise<number> {
  const connection = getAlbionConnection()
  const balance = await connection.getALBBalance(address)
  return balance.balance
}

export async function monitorALBTransaction(txHash: string): Promise<boolean> {
  const connection = getAlbionConnection()
  const result = await connection.monitorTransaction(txHash)
  return result.status === 'confirmed' || result.status === 'finalized'
}

export default AlbionConnection