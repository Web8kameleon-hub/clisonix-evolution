/**
 * UTT Transfer API - App Router
 * EuroWeb Platform - Solana ALB Integration
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.1.0 Ultra
 * @license MIT
 */

import { NextRequest, NextResponse } from 'next/server'
import { uttTransfer, TransferSchema } from '../../../../backend/utt/bridge'

export async function POST(request: NextRequest) {
  try {
    console.log('💸 UTT Transfer API called')
    
    const body = await request.json()
    const parsed = TransferSchema.parse(body)
    
    console.log('📝 Transfer request:', {
      to: parsed.to.substring(0, 20) + '...',
      amount: parsed.amount,
      physicalTokenId: parsed.physicalTokenId,
      requirePhysicalVerification: parsed.requirePhysicalVerification
    })
    
    const result = await uttTransfer(parsed.to, parsed.amount, {
      physicalTokenId: parsed.physicalTokenId,
      requirePhysicalVerification: parsed.requirePhysicalVerification
    })
    
    console.log('✅ Transfer successful:', {
      signature: result.signature.substring(0, 20) + '...',
      explorer: result.explorer
    })
    
    return NextResponse.json(result)
  } catch (error: any) {
    console.error('❌ UTT Transfer API error:', error)
    
    if (error.name === 'ZodError') {
      return NextResponse.json(
        { 
          error: 'Invalid request data',
          details: error.errors 
        },
        { status: 400 }
      )
    }
    
    return NextResponse.json(
      { 
        error: 'Transfer failed',
        details: error.message 
      },
      { status: 500 }
    )
  }
}
