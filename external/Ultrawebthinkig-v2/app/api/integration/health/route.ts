/**
 * UltraWebThinking - API Integration Routes
 * Real-time API data endpoints for frontend
 */

import { NextRequest, NextResponse } from 'next/server';
import { realAPIService } from '../../../../lib/real-api-service';

export async function GET() {
  try {
    const health = await realAPIService.healthCheck();
    
    return NextResponse.json({
      success: true,
      data: health,
      timestamp: Date.now(),
      message: 'API health check completed'
    });
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Failed to check API health',
      timestamp: Date.now()
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { action, params } = await request.json();
    
    let result;
    
    switch (action) {
      case 'dashboard':
        result = await realAPIService.getDashboardData();
        break;
        
      case 'weather':
        result = await realAPIService.getWeather(params?.city || 'London');
        break;
        
      case 'crypto':
        result = await realAPIService.getCryptoData(params?.symbols);
        break;
        
      case 'news':
        result = await realAPIService.getNews(params?.category, params?.pageSize);
        break;
        
      case 'nasa':
        result = await realAPIService.getNASAData();
        break;
        
      case 'spacex':
        result = await realAPIService.getSpaceXData();
        break;
        
      case 'covid':
        result = await realAPIService.getCovidData(params?.country);
        break;
        
      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action',
          timestamp: Date.now()
        }, { status: 400 });
    }
    
    return NextResponse.json({
      success: true,
      data: result,
      timestamp: Date.now(),
      action
    });
    
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: `API call failed: ${error}`,
      timestamp: Date.now()
    }, { status: 500 });
  }
}
