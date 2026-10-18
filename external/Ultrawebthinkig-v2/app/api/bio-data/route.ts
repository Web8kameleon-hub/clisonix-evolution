/**
 * Real Bio Data API - NO FAKE DATA
 * Web8 Industrial Grade Real Environmental Data Endpoint
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.0 Ultra
 */

import { NextRequest, NextResponse } from 'next/server';
import { BioNatureEngine } from '@/core/engines/BioNatureEngine';

const bioEngine = new BioNatureEngine();

export async function POST(request: NextRequest) {
  try {
    const { lat, lng, dataTypes } = await request.json();

    if (!lat || !lng) {
      return NextResponse.json(
        { error: 'Latitude and longitude are required' }, 
        { status: 400 }
      );
    }

    console.log(`🌍 Fetching REAL environmental data for coordinates: ${lat}, ${lng}`);

    // Get REAL environmental data from APIs
    const realEnvironmentalData = await bioEngine.getRealEnvironmentalData(lat, lng);
    
    // Get REAL biodiversity data
    const biodiversityData = await bioEngine.getRealBiodiversityData(lat, lng);
    
    const allData = [...realEnvironmentalData, biodiversityData];
    
    // Analyze the real data
    const analysis = await bioEngine.analyzeBioData(allData);

    return NextResponse.json({
      success: true,
      dataSource: 'REAL_APIS',
      location: { lat, lng },
      timestamp: Date.now(),
      dataPoints: allData,
      analysis: analysis,
      apiSources: [
        'OpenWeatherMap API',
        'OpenWeatherMap Air Pollution API', 
        'Open-Elevation API',
        'iNaturalist API'
      ],
      message: 'Real environmental data retrieved successfully - NO FAKE DATA'
    });

  } catch (error) {
    console.error('Real Bio Data API Error:', error);
    
    return NextResponse.json({
      success: false,
      error: 'Failed to fetch real environmental data',
      message: error instanceof Error ? error.message : 'Unknown error',
      fallback: 'Using minimal fallback data due to API limitations'
    }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  const url = new URL(request.url);
  const lat = parseFloat(url.searchParams.get('lat') || '40.7128');
  const lng = parseFloat(url.searchParams.get('lng') || '-74.0060');

  try {
    console.log(`🌍 GET: Fetching REAL environmental data for: ${lat}, ${lng}`);

    // Get real data
    const realData = await bioEngine.getRealEnvironmentalData(lat, lng);
    const biodiversityData = await bioEngine.getRealBiodiversityData(lat, lng);
    
    const allData = [...realData, biodiversityData];
    const analysis = await bioEngine.analyzeBioData(allData);

    return NextResponse.json({
      success: true,
      dataSource: 'REAL_APIS',
      location: { lat, lng },
      timestamp: Date.now(),
      dataCount: allData.length,
      analysis: {
        summary: analysis.summary,
        riskLevel: analysis.riskLevel,
        confidence: analysis.confidence
      },
      realDataSources: [
        'OpenWeatherMap Weather API',
        'OpenWeatherMap Air Pollution API',
        'Open-Elevation API', 
        'iNaturalist Biodiversity API'
      ]
    });

  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Real data fetch failed',
      message: error instanceof Error ? error.message : 'API error'
    }, { status: 500 });
  }
}
