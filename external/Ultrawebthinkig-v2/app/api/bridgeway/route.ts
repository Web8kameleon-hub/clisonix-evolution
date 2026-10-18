/**
 * Bridgeway API - Fiat ↔ Crypto Conversion Bridge
 * EuroWeb Platform - Solana + Stripe Integration
 *
 * Features:
 * - EUR/USD → ALB Token conversion
 * - ALB → EUR/USD offramp
 * - Real-time exchange rates
 * - Phantom wallet integration
 * - Transaction history
 *
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.1.0 Ultra
 * @license MIT
 */

import { NextRequest, NextResponse } from 'next/server'

// Bridge Configuration
const BRIDGE_CONFIG = {
  enabled: true,
  version: '1.0.0',
  name: 'Bridgeway',
  supportedPairs: [
    { from: 'EUR', to: 'ALB', enabled: true },
    { from: 'USD', to: 'ALB', enabled: true },
    { from: 'ALB', to: 'EUR', enabled: true },
    { from: 'ALB', to: 'USD', enabled: true },
    { from: 'EUR', to: 'SOL', enabled: true },
    { from: 'SOL', to: 'EUR', enabled: true }
  ],
  fees: {
    onramp: 0.015,    // 1.5% fiat → crypto
    offramp: 0.02,    // 2.0% crypto → fiat
    express: 0.025    // 2.5% express processing
  },
  limits: {
    minEUR: 10,
    maxEUR: 50000,
    minALB: 0.1,
    maxALB: 500,
    dailyLimitEUR: 10000
  }
}

// Live exchange rates (would connect to oracle/aggregator)
interface ExchangeRates {
  ALB_EUR: number
  ALB_USD: number
  SOL_EUR: number
  SOL_USD: number
  EUR_USD: number
  lastUpdated: string
}

function getExchangeRates(): ExchangeRates {
  // In production: fetch from Pyth, Chainlink, or custom oracle
  return {
    ALB_EUR: 100.00,
    ALB_USD: 108.50,
    SOL_EUR: 145.00,
    SOL_USD: 157.25,
    EUR_USD: 1.085,
    lastUpdated: new Date().toISOString()
  }
}

// Quote calculation
interface QuoteRequest {
  fromCurrency: string
  toCurrency: string
  amount: number
  expressProcessing?: boolean
}

interface Quote {
  fromCurrency: string
  toCurrency: string
  inputAmount: number
  outputAmount: number
  exchangeRate: number
  fee: number
  feePercentage: number
  expiresAt: string
  quoteId: string
}

function calculateQuote(request: QuoteRequest): Quote {
  const rates = getExchangeRates()
  const { fromCurrency, toCurrency, amount, expressProcessing } = request

  let rate: number
  let feePercentage: number

  // Determine rate
  if (fromCurrency === 'EUR' && toCurrency === 'ALB') {
    rate = 1 / rates.ALB_EUR
    feePercentage = BRIDGE_CONFIG.fees.onramp
  } else if (fromCurrency === 'USD' && toCurrency === 'ALB') {
    rate = 1 / rates.ALB_USD
    feePercentage = BRIDGE_CONFIG.fees.onramp
  } else if (fromCurrency === 'ALB' && toCurrency === 'EUR') {
    rate = rates.ALB_EUR
    feePercentage = BRIDGE_CONFIG.fees.offramp
  } else if (fromCurrency === 'ALB' && toCurrency === 'USD') {
    rate = rates.ALB_USD
    feePercentage = BRIDGE_CONFIG.fees.offramp
  } else if (fromCurrency === 'EUR' && toCurrency === 'SOL') {
    rate = 1 / rates.SOL_EUR
    feePercentage = BRIDGE_CONFIG.fees.onramp
  } else if (fromCurrency === 'SOL' && toCurrency === 'EUR') {
    rate = rates.SOL_EUR
    feePercentage = BRIDGE_CONFIG.fees.offramp
  } else {
    throw new Error(`Unsupported pair: ${fromCurrency}/${toCurrency}`)
  }

  if (expressProcessing) {
    feePercentage = BRIDGE_CONFIG.fees.express
  }

  const grossOutput = amount * rate
  const fee = grossOutput * feePercentage
  const outputAmount = grossOutput - fee

  return {
    fromCurrency,
    toCurrency,
    inputAmount: amount,
    outputAmount: Math.round(outputAmount * 1000000) / 1000000,
    exchangeRate: rate,
    fee: Math.round(fee * 100) / 100,
    feePercentage,
    expiresAt: new Date(Date.now() + 5 * 60 * 1000).toISOString(), // 5 min validity
    quoteId: `quote_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
}

// GET - Bridge info and rates
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const action = searchParams.get('action')

  // Get quote
  if (action === 'quote') {
    const from = searchParams.get('from') || 'EUR'
    const to = searchParams.get('to') || 'ALB'
    const amount = parseFloat(searchParams.get('amount') || '100')
    const express = searchParams.get('express') === 'true'

    try {
      const quote = calculateQuote({
        fromCurrency: from,
        toCurrency: to,
        amount,
        expressProcessing: express
      })
      return NextResponse.json({ success: true, quote })
    } catch (error: any) {
      return NextResponse.json(
        { success: false, error: error.message },
        { status: 400 }
      )
    }
  }

  // Get rates
  if (action === 'rates') {
    return NextResponse.json({
      success: true,
      rates: getExchangeRates()
    })
  }

  // Default: Bridge info
  return NextResponse.json({
    success: true,
    bridge: {
      ...BRIDGE_CONFIG,
      rates: getExchangeRates(),
      network: process.env.SOLANA_NETWORK || 'devnet',
      status: 'operational',
      timestamp: new Date().toISOString()
    }
  })
}

// POST - Execute bridge transaction
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { quoteId, fromCurrency, toCurrency, amount, walletAddress, paymentMethod } = body

    // Validate
    if (!fromCurrency || !toCurrency || !amount) {
      return NextResponse.json(
        { success: false, error: 'Missing required fields' },
        { status: 400 }
      )
    }

    // Calculate quote
    const quote = calculateQuote({
      fromCurrency,
      toCurrency,
      amount,
      expressProcessing: body.expressProcessing
    })

    // Check limits
    if (fromCurrency === 'EUR' || fromCurrency === 'USD') {
      if (amount < BRIDGE_CONFIG.limits.minEUR) {
        return NextResponse.json(
          { success: false, error: `Minimum amount is €${BRIDGE_CONFIG.limits.minEUR}` },
          { status: 400 }
        )
      }
      if (amount > BRIDGE_CONFIG.limits.maxEUR) {
        return NextResponse.json(
          { success: false, error: `Maximum amount is €${BRIDGE_CONFIG.limits.maxEUR}` },
          { status: 400 }
        )
      }
    }

    // Determine transaction type
    const isFiatToCrypto = ['EUR', 'USD'].includes(fromCurrency)
    const isCryptoToFiat = ['EUR', 'USD'].includes(toCurrency)

    let transaction: any = {
      id: `bridge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: isFiatToCrypto ? 'onramp' : 'offramp',
      status: 'pending',
      quote,
      walletAddress,
      paymentMethod,
      createdAt: new Date().toISOString()
    }

    if (isFiatToCrypto) {
      // ONRAMP: Fiat → Crypto
      // 1. Process fiat payment (Stripe)
      // 2. Mint/transfer crypto tokens

      transaction.steps = [
        { step: 1, name: 'Payment Processing', status: 'pending' },
        { step: 2, name: 'Token Transfer', status: 'waiting' },
        { step: 3, name: 'Confirmation', status: 'waiting' }
      ]

      // Simulate processing
      transaction.status = 'processing'
      transaction.steps[0].status = 'completed'
      transaction.steps[1].status = 'pending'

      // In production: actually transfer tokens via UTT API
      if (walletAddress && toCurrency === 'ALB') {
        transaction.tokenTransfer = {
          to: walletAddress,
          amount: quote.outputAmount,
          token: 'ALB',
          network: process.env.SOLANA_NETWORK || 'devnet',
          explorer: `https://explorer.solana.com/address/${walletAddress}?cluster=${process.env.SOLANA_NETWORK || 'devnet'}`
        }
      }

    } else if (isCryptoToFiat) {
      // OFFRAMP: Crypto → Fiat
      // 1. Receive crypto tokens
      // 2. Process fiat payout

      transaction.steps = [
        { step: 1, name: 'Token Receipt', status: 'pending' },
        { step: 2, name: 'Conversion', status: 'waiting' },
        { step: 3, name: 'Fiat Payout', status: 'waiting' }
      ]

      transaction.status = 'awaiting_deposit'
      transaction.depositAddress = process.env.BRIDGE_DEPOSIT_ADDRESS || 'BridgeDepositAddress123...'
      transaction.depositMemo = transaction.id
    }

    return NextResponse.json({
      success: true,
      transaction
    })

  } catch (error: any) {
    console.error('Bridge error:', error)
    return NextResponse.json(
      { success: false, error: 'Bridge transaction failed', details: error.message },
      { status: 500 }
    )
  }
}
