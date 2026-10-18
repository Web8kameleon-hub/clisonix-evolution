/**
 * 🚀 AVIATION WEATHER API
 * Ultra Industrial Aviation Weather Information System
 * 
 * @version 8.0.0
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 */

import { NextResponse } from 'next/server';

interface WeatherStation {
  id: string;
  icao: string;
  name: string;
  location: {
    latitude: number;
    longitude: number;
    elevation: number;
    country: string;
    city: string;
  };
  status: 'active' | 'inactive' | 'maintenance';
  lastUpdate: string;
  conditions: {
    temperature: number;
    dewPoint: number;
    humidity: number;
    pressure: number;
    windSpeed: number;
    windDirection: number;
    visibility: number;
    cloudCover: string;
    precipitation: string;
    weatherConditions: string[];
  };
  runway?: {
    condition: 'dry' | 'wet' | 'icy' | 'contaminated';
    visibility: number;
    windShear: boolean;
  };
}

interface AviationForecast {
  id: string;
  stationId: string;
  type: 'TAF' | 'METAR' | 'TREND';
  validFrom: string;
  validTo: string;
  forecast: {
    periods: Array<{
      time: string;
      conditions: {
        windSpeed: number;
        windDirection: number;
        visibility: number;
        cloudCover: string;
        precipitation?: string;
        temperature?: number;
      };
      probability?: number;
    }>;
  };
  reliability: number;
}

// Mock Aviation Weather Data
const mockStations: WeatherStation[] = [
  {
    id: 'station-001',
    icao: 'LATI',
    name: 'Tirana International Airport',
    location: {
      latitude: 41.4147,
      longitude: 19.7206,
      elevation: 38,
      country: 'Albania',
      city: 'Tirana'
    },
    status: 'active',
    lastUpdate: new Date().toISOString(),
    conditions: {
      temperature: 18.5,
      dewPoint: 12.3,
      humidity: 68,
      pressure: 1015.2,
      windSpeed: 12,
      windDirection: 240,
      visibility: 10000,
      cloudCover: 'SCT020 BKN050',
      precipitation: 'none',
      weatherConditions: ['Partly Cloudy']
    },
    runway: {
      condition: 'dry',
      visibility: 10000,
      windShear: false
    }
  },
  {
    id: 'station-002',
    icao: 'LYPG',
    name: 'Podgorica Airport',
    location: {
      latitude: 42.3594,
      longitude: 19.2519,
      elevation: 40,
      country: 'Montenegro',
      city: 'Podgorica'
    },
    status: 'active',
    lastUpdate: new Date(Date.now() - 300000).toISOString(),
    conditions: {
      temperature: 16.2,
      dewPoint: 10.8,
      humidity: 72,
      pressure: 1012.8,
      windSpeed: 8,
      windDirection: 180,
      visibility: 8000,
      cloudCover: 'BKN030 OVC080',
      precipitation: 'light rain',
      weatherConditions: ['Light Rain', 'Overcast']
    },
    runway: {
      condition: 'wet',
      visibility: 8000,
      windShear: false
    }
  },
  {
    id: 'station-003',
    icao: 'LYPR',
    name: 'Pristina International Airport',
    location: {
      latitude: 42.5728,
      longitude: 21.0358,
      elevation: 538,
      country: 'Kosovo',
      city: 'Pristina'
    },
    status: 'active',
    lastUpdate: new Date(Date.now() - 180000).toISOString(),
    conditions: {
      temperature: 14.8,
      dewPoint: 8.2,
      humidity: 65,
      pressure: 1018.5,
      windSpeed: 15,
      windDirection: 320,
      visibility: 12000,
      cloudCover: 'FEW025 SCT080',
      precipitation: 'none',
      weatherConditions: ['Clear Sky']
    }
  },
  {
    id: 'station-004',
    icao: 'LWSK',
    name: 'Skopje International Airport',
    location: {
      latitude: 41.9614,
      longitude: 21.6214,
      elevation: 238,
      country: 'North Macedonia',
      city: 'Skopje'
    },
    status: 'maintenance',
    lastUpdate: new Date(Date.now() - 900000).toISOString(),
    conditions: {
      temperature: 17.3,
      dewPoint: 11.5,
      humidity: 70,
      pressure: 1014.1,
      windSpeed: 6,
      windDirection: 90,
      visibility: 9000,
      cloudCover: 'SCT040 BKN100',
      precipitation: 'none',
      weatherConditions: ['Partly Cloudy']
    }
  }
];

const mockForecasts: AviationForecast[] = [
  {
    id: 'forecast-001',
    stationId: 'station-001',
    type: 'TAF',
    validFrom: new Date().toISOString(),
    validTo: new Date(Date.now() + 24 * 3600000).toISOString(),
    forecast: {
      periods: [
        {
          time: new Date(Date.now() + 6 * 3600000).toISOString(),
          conditions: {
            windSpeed: 10,
            windDirection: 250,
            visibility: 10000,
            cloudCover: 'FEW030',
            temperature: 20
          }
        },
        {
          time: new Date(Date.now() + 12 * 3600000).toISOString(),
          conditions: {
            windSpeed: 8,
            windDirection: 230,
            visibility: 8000,
            cloudCover: 'SCT025 BKN060',
            precipitation: 'light rain',
            temperature: 17
          },
          probability: 30
        }
      ]
    },
    reliability: 85
  }
];

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action') || 'dashboard';
    const stationId = searchParams.get('stationId');
    const icao = searchParams.get('icao');
    const type = searchParams.get('type');

    switch (action) {
      case 'dashboard':
        const activeStations = mockStations.filter(s => s.status === 'active');
        const avgConditions = {
          temperature: parseFloat((activeStations.reduce((sum, s) => sum + s.conditions.temperature, 0) / activeStations.length).toFixed(1)),
          pressure: parseFloat((activeStations.reduce((sum, s) => sum + s.conditions.pressure, 0) / activeStations.length).toFixed(1)),
          windSpeed: parseFloat((activeStations.reduce((sum, s) => sum + s.conditions.windSpeed, 0) / activeStations.length).toFixed(1)),
          visibility: Math.round(activeStations.reduce((sum, s) => sum + s.conditions.visibility, 0) / activeStations.length)
        };

        return NextResponse.json({
          success: true,
          data: {
            summary: {
              totalStations: mockStations.length,
              activeStations: activeStations.length,
              lastUpdate: new Date().toISOString(),
              avgConditions
            },
            stations: mockStations,
            recentForecasts: mockForecasts.slice(0, 5),
            alerts: mockStations
              .filter(s => s.status === 'maintenance' || 
                         s.conditions.visibility < 5000 || 
                         s.conditions.windSpeed > 25 ||
                         s.runway?.windShear)
              .map(s => ({
                id: `alert-${s.id}`,
                stationId: s.id,
                stationName: s.name,
                type: s.status === 'maintenance' ? 'maintenance' : 
                      s.conditions.visibility < 5000 ? 'visibility' :
                      s.conditions.windSpeed > 25 ? 'wind' : 'windshear',
                message: s.status === 'maintenance' 
                  ? `Station ${s.name} is under maintenance`
                  : s.conditions.visibility < 5000
                  ? `Low visibility at ${s.name}: ${s.conditions.visibility}m`
                  : s.conditions.windSpeed > 25
                  ? `High winds at ${s.name}: ${s.conditions.windSpeed} knots`
                  : `Wind shear detected at ${s.name}`,
                severity: s.runway?.windShear ? 'critical' : s.conditions.visibility < 1000 ? 'high' : 'medium',
                timestamp: s.lastUpdate
              }))
          }
        });

      case 'stations':
        let filteredStations = mockStations;
        
        if (icao) {
          filteredStations = filteredStations.filter(s => s.icao.toLowerCase() === icao.toLowerCase());
        }

        return NextResponse.json({
          success: true,
          data: {
            stations: filteredStations,
            total: filteredStations.length
          }
        });

      case 'station':
        if (!stationId && !icao) {
          return NextResponse.json({
            success: false,
            error: 'Station ID or ICAO code required'
          }, { status: 400 });
        }

        const station = mockStations.find(s => 
          s.id === stationId || s.icao.toLowerCase() === icao?.toLowerCase()
        );
        
        if (!station) {
          return NextResponse.json({
            success: false,
            error: 'Station not found'
          }, { status: 404 });
        }

        return NextResponse.json({
          success: true,
          data: {
            station,
            forecast: mockForecasts.find(f => f.stationId === station.id),
            history: Array.from({ length: 24 }, (_, i) => ({
              timestamp: new Date(Date.now() - i * 3600000).toISOString(),
              temperature: station.conditions.temperature + Math.floor(Math.random() * 10) - 5,
              pressure: station.conditions.pressure + Math.floor(Math.random() * 20) - 10,
              windSpeed: Math.max(0, station.conditions.windSpeed + Math.floor(Math.random() * 10) - 5),
              visibility: Math.max(1000, station.conditions.visibility + Math.floor(Math.random() * 2000) - 1000)
            })).reverse()
          }
        });

      case 'forecasts':
        let filteredForecasts = mockForecasts;
        
        if (type) {
          filteredForecasts = filteredForecasts.filter(f => f.type === type);
        }
        
        if (stationId) {
          filteredForecasts = filteredForecasts.filter(f => f.stationId === stationId);
        }

        return NextResponse.json({
          success: true,
          data: {
            forecasts: filteredForecasts,
            total: filteredForecasts.length
          }
        });

      case 'metar':
        if (!icao) {
          return NextResponse.json({
            success: false,
            error: 'ICAO code required for METAR'
          }, { status: 400 });
        }

        const metarStation = mockStations.find(s => s.icao.toLowerCase() === icao.toLowerCase());
        if (!metarStation) {
          return NextResponse.json({
            success: false,
            error: 'Station not found'
          }, { status: 404 });
        }

        // Generate METAR format
        const metar = `METAR ${metarStation.icao} ${new Date().toISOString().slice(8, 10)}${new Date().getHours().toString().padStart(2, '0')}${new Date().getMinutes().toString().padStart(2, '0')}Z ${Math.round(metarStation.conditions.windDirection).toString().padStart(3, '0')}${Math.round(metarStation.conditions.windSpeed).toString().padStart(2, '0')}KT ${Math.round(metarStation.conditions.visibility / 1000)}SM ${metarStation.conditions.cloudCover} ${Math.round(metarStation.conditions.temperature).toString().padStart(2, '0')}/${Math.round(metarStation.conditions.dewPoint).toString().padStart(2, '0')} A${Math.round(metarStation.conditions.pressure * 0.02953).toString().padStart(4, '0')}`;

        return NextResponse.json({
          success: true,
          data: {
            station: metarStation,
            metar,
            decoded: {
              airport: metarStation.icao,
              time: new Date().toISOString(),
              wind: {
                direction: metarStation.conditions.windDirection,
                speed: metarStation.conditions.windSpeed,
                unit: 'knots'
              },
              visibility: {
                value: metarStation.conditions.visibility,
                unit: 'meters'
              },
              clouds: metarStation.conditions.cloudCover,
              temperature: metarStation.conditions.temperature,
              dewPoint: metarStation.conditions.dewPoint,
              pressure: metarStation.conditions.pressure
            }
          }
        });

      case 'stats':
        const conditionStats = {
          clear: mockStations.filter(s => s.conditions.weatherConditions.includes('Clear Sky')).length,
          cloudy: mockStations.filter(s => s.conditions.weatherConditions.some(c => c.includes('Cloud'))).length,
          rainy: mockStations.filter(s => s.conditions.precipitation !== 'none').length,
          windy: mockStations.filter(s => s.conditions.windSpeed > 15).length
        };

        const statusStats = {
          active: mockStations.filter(s => s.status === 'active').length,
          inactive: mockStations.filter(s => s.status === 'inactive').length,
          maintenance: mockStations.filter(s => s.status === 'maintenance').length
        };

        return NextResponse.json({
          success: true,
          data: {
            conditionStats,
            statusStats,
            extremes: {
              highestTemp: Math.max(...mockStations.map(s => s.conditions.temperature)),
              lowestTemp: Math.min(...mockStations.map(s => s.conditions.temperature)),
              highestWind: Math.max(...mockStations.map(s => s.conditions.windSpeed)),
              lowestVisibility: Math.min(...mockStations.map(s => s.conditions.visibility))
            }
          }
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action'
        }, { status: 400 });
    }

  } catch (error) {
    console.error('Aviation Weather API Error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action, stationId, data } = body;

    switch (action) {
      case 'update_station':
        if (!stationId) {
          return NextResponse.json({
            success: false,
            error: 'Station ID required'
          }, { status: 400 });
        }

        return NextResponse.json({
          success: true,
          message: 'Station data updated',
          data: {
            stationId,
            updatedFields: Object.keys(data),
            timestamp: new Date().toISOString()
          }
        });

      case 'maintenance':
        if (!stationId) {
          return NextResponse.json({
            success: false,
            error: 'Station ID required'
          }, { status: 400 });
        }

        return NextResponse.json({
          success: true,
          message: 'Station maintenance scheduled',
          data: {
            stationId,
            maintenanceType: data.type || 'routine',
            scheduledFor: data.scheduledFor || new Date(Date.now() + 24 * 3600000).toISOString(),
            estimatedDuration: data.duration || '2 hours'
          }
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action'
        }, { status: 400 });
    }

  } catch (error) {
    console.error('Aviation Weather API POST Error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 });
  }
}
