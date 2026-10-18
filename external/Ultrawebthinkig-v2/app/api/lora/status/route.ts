/**
 * LoRa Physical Verification API - App Router
 * EuroWeb Platform - IoT Integration for UTT-ALB
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.1.0 Ultra
 * @license MIT
 */

import { NextRequest, NextResponse } from 'next/server'
import { loraPhysicalVerification } from '../../../../backend/lora/physical-verification'

export async function GET(request: NextRequest) {
  try {
    console.log('🛰️ LoRa Status API called')
    
    const { searchParams } = new URL(request.url)
    const tokenId = searchParams.get('tokenId')
    
    const status = loraPhysicalVerification.getVerificationStatus(tokenId || undefined)
    
    const response = {
      timestamp: new Date().toISOString(),
      loraNetwork: {
        connectedNodes: status.connectedNodes,
        lastActivity: status.lastActivity,
        status: status.connectedNodes > 0 ? 'active' : 'inactive'
      },
      physicalVerification: {
        pendingVerifications: status.pendingVerifications,
        verifiedTokens: status.verifiedTokens,
        status: status.pendingVerifications > 0 || status.verifiedTokens > 0 ? 'active' : 'standby'
      },
      specificToken: status.specificToken
    }
    
    console.log('✅ LoRa Status response:', {
      nodes: status.connectedNodes,
      pending: status.pendingVerifications,
      verified: status.verifiedTokens
    })
    
    return NextResponse.json(response)
  } catch (error: any) {
    console.error('❌ LoRa Status API error:', error.message)
    
    return NextResponse.json(
      { 
        error: 'LoRa status check failed',
        details: error.message,
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    console.log('🏷️ LoRa Token Verification API called')
    
    const body = await request.json()
    const { action, tokenId, nodeId } = body
    
    if (action === 'verify' && tokenId) {
      const verified = await loraPhysicalVerification.verifyPhysicalToken(tokenId)
      
      return NextResponse.json({
        success: verified,
        tokenId,
        status: verified ? 'verified' : 'failed',
        timestamp: new Date().toISOString()
      })
    }
    
    if (action === 'simulate' && nodeId && tokenId) {
      loraPhysicalVerification.simulatePhysicalTokenEvent(nodeId, tokenId)
      
      return NextResponse.json({
        success: true,
        message: 'Physical token event simulated',
        nodeId,
        tokenId,
        timestamp: new Date().toISOString()
      })
    }
    
    return NextResponse.json(
      { error: 'Invalid action or missing parameters' },
      { status: 400 }
    )
  } catch (error: any) {
    console.error('❌ LoRa Verification API error:', error.message)
    
    return NextResponse.json(
      { 
        error: 'LoRa verification failed',
        details: error.message,
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}
