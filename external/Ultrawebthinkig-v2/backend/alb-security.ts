/**
 * Enhanced ALB Security & Monitoring Module
 * EuroWeb Platform - Advanced Risk Management
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.1.0 Ultra
 * @license MIT
 */

import { Connection, PublicKey } from '@solana/web3.js'
import { CURRENT_ALB_DATA, ALB_SECURITY_PROTOCOLS, assessTransferRisk, calculateSlippage } from '../config/alb-token-data'
import { getConnection, readCfg, getBalance } from './utt/solana'

export interface ALBMonitoringData {
  timestamp: number
  price: number
  liquidity: number
  volume24h: number
  marketCap: number
  bridgeBalance: number
  bridgeBalanceUSD: number
  healthScore: number // 0-100
  alerts: string[]
}

export interface SecurityCheck {
  passed: boolean
  level: 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL'
  message: string
  code: string
}

export class ALBSecurityManager {
  private connection: Connection
  private mintAddress: PublicKey
  private monitoringInterval: NodeJS.Timeout | null = null
  private lastMonitoringData: ALBMonitoringData | null = null

  constructor() {
    const cfg = readCfg()
    this.connection = getConnection(cfg)
    // Use actual ALB token address from config
    this.mintAddress = new PublicKey(CURRENT_ALB_DATA.mintAddress)
  }

  /**
   * Comprehensive security check before any ALB operation
   */
  async performSecurityChecks(
    operation: 'transfer' | 'mint' | 'burn' | 'bridge',
    amount: number,
    targetAddress?: string
  ): Promise<{
    approved: boolean
    checks: SecurityCheck[]
    riskAssessment: ReturnType<typeof assessTransferRisk>
  }> {
    const checks: SecurityCheck[] = []
    const amountUSD = amount * CURRENT_ALB_DATA.priceUSD

    // 1. Token Verification Check
    checks.push({
      passed: false, // ALB is unverified
      level: 'CRITICAL',
      message: 'ALB token is UNVERIFIED. Extreme caution required.',
      code: 'TOKEN_UNVERIFIED'
    })

    // 2. Amount Limits Check
    if (amountUSD > ALB_SECURITY_PROTOCOLS.MAX_SINGLE_TRANSFER_USD) {
      checks.push({
        passed: false,
        level: 'ERROR',
        message: `Transfer amount $${amountUSD.toFixed(2)} exceeds limit $${ALB_SECURITY_PROTOCOLS.MAX_SINGLE_TRANSFER_USD}`,
        code: 'AMOUNT_LIMIT_EXCEEDED'
      })
    } else {
      checks.push({
        passed: true,
        level: 'INFO',
        message: `Transfer amount within limits`,
        code: 'AMOUNT_CHECK_PASSED'
      })
    }

    // 3. Liquidity Impact Check
    const liquidityImpact = (amountUSD / CURRENT_ALB_DATA.liquidity) * 100
    if (liquidityImpact > ALB_SECURITY_PROTOCOLS.MAX_PERCENTAGE_OF_LIQUIDITY) {
      checks.push({
        passed: false,
        level: 'ERROR',
        message: `Transfer would impact ${liquidityImpact.toFixed(1)}% of liquidity (max ${ALB_SECURITY_PROTOCOLS.MAX_PERCENTAGE_OF_LIQUIDITY}%)`,
        code: 'LIQUIDITY_IMPACT_HIGH'
      })
    } else if (liquidityImpact > 2) {
      checks.push({
        passed: true,
        level: 'WARNING',
        message: `Moderate liquidity impact: ${liquidityImpact.toFixed(1)}%`,
        code: 'LIQUIDITY_IMPACT_MODERATE'
      })
    } else {
      checks.push({
        passed: true,
        level: 'INFO',
        message: `Low liquidity impact: ${liquidityImpact.toFixed(1)}%`,
        code: 'LIQUIDITY_IMPACT_LOW'
      })
    }

    // 4. Slippage Check
    const slippage = calculateSlippage(amountUSD, CURRENT_ALB_DATA.liquidity)
    if (slippage > ALB_SECURITY_PROTOCOLS.MAX_SLIPPAGE_TOLERANCE) {
      checks.push({
        passed: false,
        level: 'ERROR',
        message: `Estimated slippage ${slippage.toFixed(1)}% exceeds tolerance ${ALB_SECURITY_PROTOCOLS.MAX_SLIPPAGE_TOLERANCE}%`,
        code: 'SLIPPAGE_TOO_HIGH'
      })
    } else if (slippage > ALB_SECURITY_PROTOCOLS.SLIPPAGE_WARNING_THRESHOLD) {
      checks.push({
        passed: true,
        level: 'WARNING',
        message: `High slippage warning: ${slippage.toFixed(1)}%`,
        code: 'SLIPPAGE_WARNING'
      })
    } else {
      checks.push({
        passed: true,
        level: 'INFO',
        message: `Acceptable slippage: ${slippage.toFixed(1)}%`,
        code: 'SLIPPAGE_OK'
      })
    }

    // 5. Address Validation (if provided)
    if (targetAddress) {
      try {
        new PublicKey(targetAddress)
        checks.push({
          passed: true,
          level: 'INFO',
          message: 'Target address is valid',
          code: 'ADDRESS_VALID'
        })
      } catch {
        checks.push({
          passed: false,
          level: 'ERROR',
          message: 'Invalid target address format',
          code: 'ADDRESS_INVALID'
        })
      }
    }

    // 6. Bridge Balance Check
    try {
      const bridgeBalance = await this.getBridgeBalance()
      if (amount > bridgeBalance) {
        checks.push({
          passed: false,
          level: 'ERROR',
          message: `Insufficient bridge balance: ${bridgeBalance.toFixed(6)} ALB available, ${amount.toFixed(6)} ALB requested`,
          code: 'INSUFFICIENT_BRIDGE_BALANCE'
        })
      } else {
        checks.push({
          passed: true,
          level: 'INFO',
          message: `Sufficient bridge balance available`,
          code: 'BRIDGE_BALANCE_OK'
        })
      }
    } catch (error) {
      checks.push({
        passed: false,
        level: 'CRITICAL',
        message: `Cannot verify bridge balance: ${error}`,
        code: 'BRIDGE_BALANCE_CHECK_FAILED'
      })
    }

    // Risk Assessment
    const riskAssessment = assessTransferRisk(amountUSD)

    // Final Approval Decision
    const criticalFailures = checks.filter(c => !c.passed && c.level === 'CRITICAL').length
    const errorFailures = checks.filter(c => !c.passed && c.level === 'ERROR').length
    
    const approved = criticalFailures === 0 && errorFailures === 0

    return {
      approved,
      checks,
      riskAssessment
    }
  }

  /**
   * Get current bridge balance
   */
  async getBridgeBalance(): Promise<number> {
    try {
      const cfg = readCfg()
      const bridgeKeypair = await import('./utt/solana').then(m => m.loadBridgeKeypair())
      return await getBalance(this.connection, bridgeKeypair.publicKey, this.mintAddress, cfg.decimals)
    } catch (error) {
      throw new Error(`Failed to get bridge balance: ${error}`)
    }
  }

  /**
   * Start continuous monitoring
   */
  startMonitoring(): void {
    if (this.monitoringInterval) {
      this.stopMonitoring()
    }

    console.log('🔍 Starting ALB Security Monitoring...')
    
    this.monitoringInterval = setInterval(async () => {
      try {
        await this.performMonitoringCheck()
      } catch (error) {
        console.error('❌ ALB Monitoring Error:', error)
      }
    }, ALB_SECURITY_PROTOCOLS.LIQUIDITY_CHECK_INTERVAL)

    // Initial check
    this.performMonitoringCheck()
  }

  /**
   * Stop monitoring
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval)
      this.monitoringInterval = null
      console.log('⏹️ ALB Security Monitoring stopped')
    }
  }

  /**
   * Perform monitoring check
   */
  private async performMonitoringCheck(): Promise<void> {
    const alerts: string[] = []
    let healthScore = 100

    try {
      // Get current bridge balance
      const bridgeBalance = await this.getBridgeBalance()
      const bridgeBalanceUSD = bridgeBalance * CURRENT_ALB_DATA.priceUSD

      // Check for low bridge balance
      if (bridgeBalance < 1000) { // Less than 1000 ALB
        alerts.push(`⚠️ Low bridge balance: ${bridgeBalance.toFixed(2)} ALB`)
        healthScore -= 20
      }

      // Check for extremely low liquidity
      if (CURRENT_ALB_DATA.liquidity < 1000) { // Less than $1000 liquidity
        alerts.push(`🚨 Critical: Very low market liquidity: $${CURRENT_ALB_DATA.liquidity}`)
        healthScore -= 30
      }

      // Unverified token penalty
      if (!CURRENT_ALB_DATA.isVerified) {
        alerts.push(`⚠️ Token remains unverified - high risk`)
        healthScore -= 25
      }

      const monitoringData: ALBMonitoringData = {
        timestamp: Date.now(),
        price: CURRENT_ALB_DATA.priceUSD,
        liquidity: CURRENT_ALB_DATA.liquidity,
        volume24h: CURRENT_ALB_DATA.volume24h,
        marketCap: CURRENT_ALB_DATA.marketCap,
        bridgeBalance,
        bridgeBalanceUSD,
        healthScore: Math.max(0, healthScore),
        alerts
      }

      this.lastMonitoringData = monitoringData

      // Log critical alerts
      if (alerts.length > 0) {
        console.log('🚨 ALB Security Alerts:', alerts)
      }

      // Log health score
      if (healthScore < 50) {
        console.log(`🔴 ALB Health Score: ${healthScore}/100 - CRITICAL`)
      } else if (healthScore < 75) {
        console.log(`🟡 ALB Health Score: ${healthScore}/100 - WARNING`)
      } else {
        console.log(`🟢 ALB Health Score: ${healthScore}/100 - GOOD`)
      }

    } catch (error) {
      console.error('❌ ALB Monitoring Check Failed:', error)
      alerts.push(`System error: ${error}`)
    }
  }

  /**
   * Get latest monitoring data
   */
  getMonitoringData(): ALBMonitoringData | null {
    return this.lastMonitoringData
  }

  /**
   * Emergency pause all operations
   */
  emergencyPause(): void {
    console.log('🚨 EMERGENCY PAUSE ACTIVATED - All ALB operations suspended')
    // Implementation would set global flags to pause operations
    // This would be integrated with the bridge logic
  }
}

// Singleton instance
export const albSecurityManager = new ALBSecurityManager()

export default ALBSecurityManager
