import { NextRequest, NextResponse } from 'next/server';
import { 
  initializeASI12LayerSystem, 
  processRealASIRequest, 
  getRealASIStatus 
} from '../../../lib/ASI12LayerSystem';

// Initialize ASI system
const asiSystem = initializeASI12LayerSystem();

export async function GET(request: NextRequest) {
  try {
    const status = getRealASIStatus();
    
    return NextResponse.json({
      success: true,
      timestamp: new Date().toISOString(),
      message: "ASI 12-Layer System Status - REAL DATA ONLY",
      data: {
        systemHealth: status.systemHealth,
        realAnalytics: status.realAnalytics,
        layerCount: status.layers.size,
        activeLayers: Array.from(status.layers.values()).filter(l => l.status === 'active').length,
        memoryUsage: status.systemHealth.totalMemoryMB,
        uptime: status.systemHealth.uptimeSeconds,
        language: status.systemHealth.activeLanguage,
        responseTime: status.systemHealth.responseTimeMs
      }
    });
  } catch (error) {
    console.error('ASI API Error:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to get ASI system status',
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { input, language = 'auto' } = body;
    
    if (!input || typeof input !== 'string') {
      return NextResponse.json({
        success: false,
        error: 'Input is required and must be a string'
      }, { status: 400 });
    }
    
    const startTime = Date.now();
    
    const result = await processRealASIRequest(input, language);
    
    const endTime = Date.now();
    
    return NextResponse.json({
      success: true,
      timestamp: new Date().toISOString(),
      message: "ASI Processing Complete - REAL DATA",
      data: {
        input,
        response: result.response,
        processingTime: result.processingTime,
        totalTime: endTime - startTime,
        layersUsed: result.layersUsed,
        realMetrics: result.realMetrics,
        detectedLanguage: input.match(/[ëçshqiptar]/gi) ? 'sq' : 'en'
      }
    });
    
  } catch (error) {
    console.error('ASI Processing Error:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to process ASI request',
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}
