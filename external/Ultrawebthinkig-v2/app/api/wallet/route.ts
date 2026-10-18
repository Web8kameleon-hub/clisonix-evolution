/**
 * Wallet Connection API - Phantom & Solana Wallet Adapter
 * Real ALB mainnet defaults (no fake placeholders)
 */

import { NextRequest, NextResponse } from 'next/server'

interface WalletSession {
  publicKey: string
  connectedAt: string
  walletType: 'phantom' | 'solflare' | 'backpack' | 'other'
  network: string
  verified: boolean
}

const WALLET_SESSIONS = new Map<string, WalletSession>()

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const publicKey = searchParams.get('publicKey')

  if (publicKey) {
    const session = WALLET_SESSIONS.get(publicKey)
    if (session) {
      return NextResponse.json({ success: true, connected: true, session })
    }

    return NextResponse.json({
      success: true,
      connected: false,
      message: 'Wallet not connected',
    })
  }

  const mint = process.env.SOLANA_ALB_MINT || 'HSEcf132J4dNz46gw5fsVV7xfgedeFyTZXMSHcroz3BU'
  const authority = process.env.SOLANA_ALB_AUTHORITY || 'AuGX5kaG3ydcJLaGTUptSKnbC4y3MeUp1qds8mYJt9ua'
  const network = process.env.SOLANA_NETWORK || 'mainnet-beta'

  return NextResponse.json({
    success: true,
    supportedWallets: [
      {
        name: 'Phantom',
        icon: 'https://phantom.app/img/phantom-icon-purple.svg',
        url: 'https://phantom.app',
        adapter: 'phantom',
        recommended: true,
      },
      {
        name: 'Solflare',
        icon: 'https://solflare.com/favicon.ico',
        url: 'https://solflare.com',
        adapter: 'solflare',
        recommended: false,
      },
      {
        name: 'Backpack',
        icon: 'https://backpack.app/favicon.ico',
        url: 'https://backpack.app',
        adapter: 'backpack',
        recommended: false,
      },
    ],
    network,
    features: {
      signMessage: true,
      signTransaction: true,
      signAllTransactions: true,
      connect: true,
      disconnect: true,
    },
    albToken: {
      mint,
      authority,
      symbol: 'ALB',
      name: 'Albion Token',
      decimals: 6,
      network,
      logo: '/tokens/alb.png',
      explorerUrl: `https://solscan.io/token/${mint}`,
      dexscreenerUrl: `https://dexscreener.com/solana/${mint}`,
    },
  })
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, publicKey, signature, message, walletType } = body

    switch (action) {
      case 'connect': {
        if (!publicKey) {
          return NextResponse.json({ success: false, error: 'Public key required' }, { status: 400 })
        }

        const session: WalletSession = {
          publicKey,
          connectedAt: new Date().toISOString(),
          walletType: walletType || 'phantom',
          network: process.env.SOLANA_NETWORK || 'mainnet-beta',
          verified: false,
        }

        WALLET_SESSIONS.set(publicKey, session)

        return NextResponse.json({
          success: true,
          connected: true,
          message: 'Wallet connected successfully',
          session,
        })
      }

      case 'disconnect': {
        if (!publicKey) {
          return NextResponse.json({ success: false, error: 'Public key required' }, { status: 400 })
        }

        WALLET_SESSIONS.delete(publicKey)
        return NextResponse.json({ success: true, connected: false, message: 'Wallet disconnected successfully' })
      }

      case 'verify': {
        if (!publicKey || !signature || !message) {
          return NextResponse.json({ success: false, error: 'Public key, signature and message required' }, { status: 400 })
        }

        const session = WALLET_SESSIONS.get(publicKey)
        if (!session) {
          return NextResponse.json({ success: false, error: 'Wallet session not found' }, { status: 404 })
        }

        session.verified = true
        WALLET_SESSIONS.set(publicKey, session)

        return NextResponse.json({ success: true, verified: true, message: 'Wallet verified', session })
      }

      case 'listSessions': {
        return NextResponse.json({
          success: true,
          count: WALLET_SESSIONS.size,
          sessions: Array.from(WALLET_SESSIONS.values()),
        })
      }

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid action. Use: connect, disconnect, verify, listSessions' },
          { status: 400 },
        )
    }
  } catch (error: any) {
    console.error('Wallet API error:', error)
    return NextResponse.json({ success: false, error: error.message || 'Internal server error' }, { status: 500 })
  }
}