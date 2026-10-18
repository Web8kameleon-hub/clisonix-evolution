/**
 * UTT Sign Physical Token API - App Router
 * EuroWeb Platform - Solana ALB Integration
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.1.0 Ultra
 * @license MIT
 */

import { NextRequest, NextResponse } from 'next/server'
import { signPhysicalPayload, PhysicalTokenPayload } from '../../../../backend/utt/bridge'
import { albEurValue } from '../../../../backend/utt/solana'

export async function POST(request: NextRequest) {
  try {
    console.log('🔏 UTT Sign Physical Token API called')
    
    const body = await request.json()
    
    // Validate required fields
    if (!body.tokenId || !body.serial) {
      return NextResponse.json(
        { error: 'tokenId and serial are required' },
        { status: 400 }
      )
    }
    
    const payload: PhysicalTokenPayload = {
      tokenId: body.tokenId,
      mint: process.env.SOLANA_ALB_MINT || process.env.ALB_MINT_ADDRESS || '',
      serial: body.serial,
      owner: body.owner,
      issuedAt: Date.now(),
      expiresAt: body.expiresAt,
      valueEUR: albEurValue() // Current ALB EUR value
    }
    
    console.log('📝 Signing physical token:', {
      tokenId: payload.tokenId,
      serial: payload.serial,
      valueEUR: payload.valueEUR
    })
    
    const signed = await signPhysicalPayload(payload)
    
    console.log('✅ Physical token signed successfully')
    
    return NextResponse.json(signed)
  } catch (error: any) {
    console.error('❌ UTT Sign Physical Token API error:', error)
    
    return NextResponse.json(
      { 
        error: 'Failed to sign physical token',
        details: error.message 
      },
      { status: 500 }
    )
  }
}
