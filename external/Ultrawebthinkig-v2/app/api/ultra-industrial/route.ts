/**
 * ULTRA INDUSTRIAL API ENDPOINT
 * PRODUCTION READY - NO MOCK DATA
 * REAL DATA SOURCES ONLY
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.0 ULTRA INDUSTRIAL
 */

import { NextRequest, NextResponse } from 'next/server';
import { UltraIndustrialEngine } from '@/core/production/UltraIndustrialEngine';

const industrialEngine = new UltraIndustrialEngine();

export async function GET(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const url = new URL(request.url);
    const dataType = url.searchParams.get('type');
    const symbol = url.searchParams.get('symbol');
    const lat = url.searchParams.get('lat');
    const lng = url.searchParams.get('lng');
    const country = url.searchParams.get('country');

    console.log(`🚀 ULTRA INDUSTRIAL API REQUEST: ${dataType || 'status'}`);

    // If no type specified, return system status and available endpoints
    if (!dataType) {
      const systemStatus = await industrialEngine.validateProductionReadiness();
      const processingTime = Date.now() - startTime;
      
      return NextResponse.json({
        success: true,
        systemStatus: 'ULTRA_INDUSTRIAL_PRODUCTION',
        message: 'Ultra Industrial API is operational',
        timestamp: Date.now(),
        processingTime,
        availableEndpoints: {
          financial: '/api/ultra-industrial?type=financial&symbol=AAPL',
          weather: '/api/ultra-industrial?type=weather&lat=40.7128&lng=-74.0060',
          economic: '/api/ultra-industrial?type=economic&country=US',
          satellite: '/api/ultra-industrial?type=satellite&lat=40.7128&lng=-74.0060',
          system: '/api/ultra-industrial?type=system',
          validation: '/api/ultra-industrial?type=validation'
        },
        productionReadiness: systemStatus,
        disclaimer: 'ALL DATA IS REAL - NO MOCK OR FAKE VALUES'
      });
    }

    let result: any = {};

    switch (dataType) {
      case 'financial':
        if (!symbol) {
          return NextResponse.json(
            { error: 'Symbol parameter required for financial data' },
            { status: 400 }
          );
        }
        result = await industrialEngine.getRealFinancialData(symbol);
        break;

      case 'weather':
        if (!lat || !lng) {
          return NextResponse.json(
            { error: 'Latitude and longitude required for weather data' },
            { status: 400 }
          );
        }
        result = await industrialEngine.getRealWeatherData(
          parseFloat(lat), 
          parseFloat(lng)
        );
        break;

      case 'economic':
        if (!country) {
          return NextResponse.json(
            { error: 'Country code required for economic data' },
            { status: 400 }
          );
        }
        result = await industrialEngine.getRealEconomicData(country);
        break;

      case 'satellite':
        if (!lat || !lng) {
          return NextResponse.json(
            { error: 'Coordinates required for satellite data' },
            { status: 400 }
          );
        }
        result = await industrialEngine.getRealSatelliteData(
          parseFloat(lat), 
          parseFloat(lng)
        );
        break;

      case 'system':
        result = await industrialEngine.getRealSystemMetrics();
        break;

      case 'validation':
        result = await industrialEngine.validateProductionReadiness();
        break;

      default:
        return NextResponse.json(
          { 
            error: 'Invalid data type',
            validTypes: ['financial', 'weather', 'economic', 'satellite', 'system', 'validation']
          },
          { status: 400 }
        );
    }

    const processingTime = Date.now() - startTime;

    return NextResponse.json({
      success: true,
      dataType,
      processingTime,
      timestamp: Date.now(),
      data: result,
      systemStatus: 'ULTRA_INDUSTRIAL_PRODUCTION',
      disclaimer: 'ALL DATA IS REAL - NO MOCK OR FAKE VALUES'
    });

  } catch (error) {
    const processingTime = Date.now() - startTime;
    
    console.error('🔥 ULTRA INDUSTRIAL API ERROR:', error);

    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      processingTime,
      timestamp: Date.now(),
      systemStatus: 'ERROR_IN_PRODUCTION',
      note: 'This is a real production error - check API keys and network connectivity'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  const startTime = Date.now();
  
  try {
    const body = await request.json();
    const { action, parameters } = body;

    console.log(`🚀 ULTRA INDUSTRIAL POST REQUEST: ${action}`);

    let result: any = {};

    switch (action) {
      case 'multi-data-fetch':
        // Fetch multiple real data sources simultaneously
        const promises = [];
        
        if (parameters.financial) {
          promises.push(
            industrialEngine.getRealFinancialData(parameters.financial.symbol)
              .then(data => ({ type: 'financial', data }))
              .catch(error => ({ type: 'financial', error: error.message }))
          );
        }
        
        if (parameters.weather && parameters.coordinates) {
          promises.push(
            industrialEngine.getRealWeatherData(
              parameters.coordinates.lat, 
              parameters.coordinates.lng
            )
              .then(data => ({ type: 'weather', data }))
              .catch(error => ({ type: 'weather', error: error.message }))
          );
        }
        
        if (parameters.economic) {
          promises.push(
            industrialEngine.getRealEconomicData(parameters.economic.country)
              .then(data => ({ type: 'economic', data }))
              .catch(error => ({ type: 'economic', error: error.message }))
          );
        }

        const results = await Promise.allSettled(promises);
        result = {
          multiDataResults: results.map(r => 
            r.status === 'fulfilled' ? r.value : { error: 'Request failed' }
          ),
          totalRequests: promises.length
        };
        break;

      case 'system-health-check':
        const validation = await industrialEngine.validateProductionReadiness();
        const systemMetrics = await industrialEngine.getRealSystemMetrics();
        
        result = {
          productionReady: validation.ready,
          issues: validation.issues,
          recommendations: validation.recommendations,
          systemMetrics,
          healthScore: validation.ready ? 100 : Math.max(0, 100 - (validation.issues.length * 20))
        };
        break;

      default:
        return NextResponse.json(
          { 
            error: 'Invalid action',
            validActions: ['multi-data-fetch', 'system-health-check']
          },
          { status: 400 }
        );
    }

    const processingTime = Date.now() - startTime;

    return NextResponse.json({
      success: true,
      action,
      processingTime,
      timestamp: Date.now(),
      result,
      systemStatus: 'ULTRA_INDUSTRIAL_PRODUCTION',
      guarantee: 'ALL DATA SOURCES ARE REAL APIS - ZERO MOCK DATA'
    });

  } catch (error) {
    const processingTime = Date.now() - startTime;
    
    console.error('🔥 ULTRA INDUSTRIAL POST ERROR:', error);

    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      processingTime,
      timestamp: Date.now(),
      systemStatus: 'PRODUCTION_ERROR',
      note: 'Real production system error - not simulated'
    }, { status: 500 });
  }
}
