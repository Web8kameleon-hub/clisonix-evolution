'use client';

import { useState, useEffect } from 'react';
import styles from './aviation.module.css';

interface AirportWeather {
  icao: string;
  name: string;
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  elevation: number;
  metar: string;
  taf: string;
  visibility: number;
  windSpeed: number;
  windDirection: number;
  temperature: number;
  dewPoint: number;
  pressure: number;
  cloudCeiling: number;
  conditions: string;
  flightCategory: 'VFR' | 'MVFR' | 'IFR' | 'LIFR';
  lastUpdated: string;
}

interface FlightConditions {
  vfr: number;
  mvfr: number;
  ifr: number;
  lifr: number;
}

interface AviationMetrics {
  totalAirports: number;
  activeReports: number;
  flightConditions: FlightConditions;
  averageVisibility: number;
  averageWindSpeed: number;
  lastUpdate: string;
}

export default function AviationWeatherDashboard() {
  const [airports, setAirports] = useState<AirportWeather[]>([]);
  const [metrics, setMetrics] = useState<AviationMetrics>({
    totalAirports: 0,
    activeReports: 0,
    flightConditions: { vfr: 0, mvfr: 0, ifr: 0, lifr: 0 },
    averageVisibility: 0,
    averageWindSpeed: 0,
    lastUpdate: ''
  });
  const [selectedAirport, setSelectedAirport] = useState<AirportWeather | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchAviationData();
    const interval = setInterval(fetchAviationData, 300000); // Update every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const fetchAviationData = async () => {
    setIsLoading(true);
    try {
      // Simulate aviation weather data
      const mockAirports: AirportWeather[] = [
        {
          icao: 'KJFK',
          name: 'John F. Kennedy International Airport',
          city: 'New York',
          country: 'USA',
          latitude: 40.6413,
          longitude: -73.7781,
          elevation: 13,
          metar: 'KJFK 121251Z 28012KT 10SM FEW250 12/M02 A3012 RMK A01',
          taf: 'KJFK 121120Z 1212/1318 28012KT P6SM FEW250 FM121400 27010KT P6SM SCT250',
          visibility: 10,
          windSpeed: 12,
          windDirection: 280,
          temperature: 12,
          dewPoint: -2,
          pressure: 30.12,
          cloudCeiling: 25000,
          conditions: 'Few Clouds',
          flightCategory: 'VFR',
          lastUpdated: new Date(Date.now() - 180000).toISOString()
        },
        {
          icao: 'KLAX',
          name: 'Los Angeles International Airport',
          city: 'Los Angeles',
          country: 'USA',
          latitude: 33.9425,
          longitude: -118.4081,
          elevation: 125,
          metar: 'KLAX 121253Z 25008KT 8SM BKN012 OVC020 18/16 A2995 RMK A01',
          taf: 'KLAX 121120Z 1212/1318 25008KT 6SM BKN012 OVC020 FM121600 26010KT P6SM SCT015',
          visibility: 8,
          windSpeed: 8,
          windDirection: 250,
          temperature: 18,
          dewPoint: 16,
          pressure: 29.95,
          cloudCeiling: 1200,
          conditions: 'Overcast',
          flightCategory: 'MVFR',
          lastUpdated: new Date(Date.now() - 120000).toISOString()
        },
        {
          icao: 'KORD',
          name: 'Chicago O\'Hare International Airport',
          city: 'Chicago',
          country: 'USA',
          latitude: 41.9786,
          longitude: -87.9048,
          elevation: 672,
          metar: 'KORD 121251Z 02015G22KT 3SM -SN OVC008 M01/M04 A2988 RMK A01',
          taf: 'KORD 121120Z 1212/1318 02015G22KT 3SM -SN OVC008 FM121500 01012KT 5SM -SN BKN015',
          visibility: 3,
          windSpeed: 15,
          windDirection: 20,
          temperature: -1,
          dewPoint: -4,
          pressure: 29.88,
          cloudCeiling: 800,
          conditions: 'Light Snow',
          flightCategory: 'IFR',
          lastUpdated: new Date(Date.now() - 300000).toISOString()
        },
        {
          icao: 'EGLL',
          name: 'London Heathrow Airport',
          city: 'London',
          country: 'UK',
          latitude: 51.4700,
          longitude: -0.4543,
          elevation: 83,
          metar: 'EGLL 121220Z 26018G28KT 2400 -RA BKN005 OVC012 06/05 Q1008 TEMPO 1500 RA',
          taf: 'EGLL 121100Z 1212/1318 26018G28KT 3000 -RA BKN005 OVC012 TEMPO 1212/1216 1500 RA BKN003',
          visibility: 2.4,
          windSpeed: 18,
          windDirection: 260,
          temperature: 6,
          dewPoint: 5,
          pressure: 29.77,
          cloudCeiling: 500,
          conditions: 'Light Rain',
          flightCategory: 'IFR',
          lastUpdated: new Date(Date.now() - 240000).toISOString()
        },
        {
          icao: 'LFPG',
          name: 'Charles de Gaulle Airport',
          city: 'Paris',
          country: 'France',
          latitude: 49.0128,
          longitude: 2.5500,
          elevation: 392,
          metar: 'LFPG 121200Z 24012KT CAVOK 08/04 Q1015 NOSIG',
          taf: 'LFPG 121100Z 1212/1318 24012KT CAVOK FM121600 25015KT 9999 FEW020',
          visibility: 10,
          windSpeed: 12,
          windDirection: 240,
          temperature: 8,
          dewPoint: 4,
          pressure: 29.97,
          cloudCeiling: 25000,
          conditions: 'Clear',
          flightCategory: 'VFR',
          lastUpdated: new Date(Date.now() - 360000).toISOString()
        },
        {
          icao: 'EDDF',
          name: 'Frankfurt Airport',
          city: 'Frankfurt',
          country: 'Germany',
          latitude: 50.0264,
          longitude: 8.5431,
          elevation: 364,
          metar: 'EDDF 121220Z 25015KT 9999 FEW030 SCT100 07/01 Q1012 NOSIG',
          taf: 'EDDF 121100Z 1212/1318 25015KT 9999 FEW030 SCT100 FM121400 26018KT 9999 SCT025',
          visibility: 10,
          windSpeed: 15,
          windDirection: 250,
          temperature: 7,
          dewPoint: 1,
          pressure: 29.88,
          cloudCeiling: 3000,
          conditions: 'Few Clouds',
          flightCategory: 'VFR',
          lastUpdated: new Date(Date.now() - 200000).toISOString()
        },
        {
          icao: 'RJAA',
          name: 'Narita International Airport',
          city: 'Tokyo',
          country: 'Japan',
          latitude: 35.7647,
          longitude: 140.3864,
          elevation: 141,
          metar: 'RJAA 121200Z 30018KT 9999 FEW020 BKN100 15/08 Q1018 NOSIG',
          taf: 'RJAA 121100Z 1212/1318 30018KT 9999 FEW020 BKN100 FM121500 32020KT 9999 SCT025',
          visibility: 10,
          windSpeed: 18,
          windDirection: 300,
          temperature: 15,
          dewPoint: 8,
          pressure: 30.06,
          cloudCeiling: 2000,
          conditions: 'Few Clouds',
          flightCategory: 'VFR',
          lastUpdated: new Date(Date.now() - 480000).toISOString()
        },
        {
          icao: 'KBOS',
          name: 'Logan International Airport',
          city: 'Boston',
          country: 'USA',
          latitude: 42.3656,
          longitude: -71.0096,
          elevation: 20,
          metar: 'KBOS 121254Z 06020G28KT 1/2SM R04R/1800V6000FT +SN BLSN FEW008 BKN015 OVC025 M05/M08 A2975',
          taf: 'KBOS 121126Z 1212/1318 06020G28KT 1/2SM +SN BLSN BKN010 OVC020 TEMPO 1212/1218 1/4SM +SN BLSN',
          visibility: 0.5,
          windSpeed: 20,
          windDirection: 60,
          temperature: -5,
          dewPoint: -8,
          pressure: 29.75,
          cloudCeiling: 800,
          conditions: 'Heavy Snow',
          flightCategory: 'LIFR',
          lastUpdated: new Date(Date.now() - 60000).toISOString()
        }
      ];

      // Calculate metrics
      const vfrCount = mockAirports.filter(a => a.flightCategory === 'VFR').length;
      const mvfrCount = mockAirports.filter(a => a.flightCategory === 'MVFR').length;
      const ifrCount = mockAirports.filter(a => a.flightCategory === 'IFR').length;
      const lifrCount = mockAirports.filter(a => a.flightCategory === 'LIFR').length;
      
      const avgVisibility = mockAirports.reduce((sum, a) => sum + a.visibility, 0) / mockAirports.length;
      const avgWindSpeed = mockAirports.reduce((sum, a) => sum + a.windSpeed, 0) / mockAirports.length;

      const mockMetrics: AviationMetrics = {
        totalAirports: mockAirports.length,
        activeReports: mockAirports.length,
        flightConditions: {
          vfr: vfrCount,
          mvfr: mvfrCount,
          ifr: ifrCount,
          lifr: lifrCount
        },
        averageVisibility: Math.round(avgVisibility * 100) / 100,
        averageWindSpeed: Math.round(avgWindSpeed),
        lastUpdate: new Date().toISOString()
      };

      setAirports(mockAirports);
      setMetrics(mockMetrics);
    } catch (error) {
      console.error('Error fetching aviation data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getFlightCategoryColor = (category: string) => {
    switch (category) {
      case 'VFR': return '#00ff88';    // Green - Visual Flight Rules
      case 'MVFR': return '#00d4ff';   // Blue - Marginal VFR
      case 'IFR': return '#ffa502';    // Orange - Instrument Flight Rules
      case 'LIFR': return '#ff6b6b';   // Red - Low IFR
      default: return '#6c757d';
    }
  };

  const getWindDirection = (degrees: number) => {
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    return directions[Math.round(degrees / 22.5) % 16];
  };

  const formatLastUpdated = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    return `${diffHours}h ${diffMins % 60}m ago`;
  };

  const filteredAirports = airports.filter(airport => {
    const matchesSearch = airport.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         airport.icao.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         airport.city.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = filterCategory === 'all' || airport.flightCategory === filterCategory;
    
    return matchesSearch && matchesCategory;
  });

  return (
    <div className={styles['container']}>
      <div className={styles['header']}>
        <h1 className={styles['title']}>✈️ Aviation Weather Center</h1>
        <p className={styles['subtitle']}>
          Real-time METAR/TAF reports and flight conditions for major airports
        </p>
        <div className={styles['last-updated']}>
          Last updated: {new Date().toLocaleTimeString()}
          {isLoading && <span className={styles['loading']}>⟳</span>}
        </div>
      </div>

      {/* Metrics Overview */}
      <div className={styles['metrics-grid']}>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>🛩️</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.totalAirports}</div>
            <div className={styles['metric-label']}>Total Airports</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>📡</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.activeReports}</div>
            <div className={styles['metric-label']}>Active Reports</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>👁️</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.averageVisibility} SM</div>
            <div className={styles['metric-label']}>Avg Visibility</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>💨</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.averageWindSpeed} kt</div>
            <div className={styles['metric-label']}>Avg Wind Speed</div>
          </div>
        </div>
      </div>

      {/* Flight Conditions Overview */}
      <div className={styles['conditions-section']}>
        <h2 className={styles['section-title']}>🌤️ Flight Conditions Overview</h2>
        <div className={styles['conditions-grid']}>
          <div className={styles['condition-card']} style={{ borderColor: getFlightCategoryColor('VFR') }}>
            <div className={styles['condition-header']}>
              <span style={{ color: getFlightCategoryColor('VFR') }}>● VFR</span>
              <span className={styles['condition-count']}>{metrics.flightConditions.vfr}</span>
            </div>
            <div className={styles['condition-desc']}>Visual Flight Rules</div>
            <div className={styles['condition-details']}>Visibility ≥ 3 SM, Ceiling ≥ 1000 ft</div>
          </div>
          <div className={styles['condition-card']} style={{ borderColor: getFlightCategoryColor('MVFR') }}>
            <div className={styles['condition-header']}>
              <span style={{ color: getFlightCategoryColor('MVFR') }}>● MVFR</span>
              <span className={styles['condition-count']}>{metrics.flightConditions.mvfr}</span>
            </div>
            <div className={styles['condition-desc']}>Marginal VFR</div>
            <div className={styles['condition-details']}>Visibility 1-3 SM, Ceiling 500-1000 ft</div>
          </div>
          <div className={styles['condition-card']} style={{ borderColor: getFlightCategoryColor('IFR') }}>
            <div className={styles['condition-header']}>
              <span style={{ color: getFlightCategoryColor('IFR') }}>● IFR</span>
              <span className={styles['condition-count']}>{metrics.flightConditions.ifr}</span>
            </div>
            <div className={styles['condition-desc']}>Instrument Flight Rules</div>
            <div className={styles['condition-details']}>Visibility 1-3 SM, Ceiling 200-500 ft</div>
          </div>
          <div className={styles['condition-card']} style={{ borderColor: getFlightCategoryColor('LIFR') }}>
            <div className={styles['condition-header']}>
              <span style={{ color: getFlightCategoryColor('LIFR') }}>● LIFR</span>
              <span className={styles['condition-count']}>{metrics.flightConditions.lifr}</span>
            </div>
            <div className={styles['condition-desc']}>Low IFR</div>
            <div className={styles['condition-details']}>Visibility &lt; 1 SM, Ceiling &lt; 200 ft</div>
          </div>
        </div>
      </div>

      {/* Search and Filter */}
      <div className={styles['filter-section']}>
        <h2 className={styles['section-title']}>🔍 Airport Search & Filter</h2>
        <div className={styles['search-controls']}>
          <input
            type="text"
            placeholder="Search airports (ICAO, name, city)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={styles['search-input']}
          />
          <div className={styles['category-filters']}>
            <button 
              className={`${styles['filter-button']} ${filterCategory === 'all' ? styles['active'] : ''}`}
              onClick={() => setFilterCategory('all')}
            >
              All ({airports.length})
            </button>
            <button 
              className={`${styles['filter-button']} ${filterCategory === 'VFR' ? styles['active'] : ''}`}
              onClick={() => setFilterCategory('VFR')}
              style={{ color: filterCategory === 'VFR' ? getFlightCategoryColor('VFR') : undefined }}
            >
              VFR ({metrics.flightConditions.vfr})
            </button>
            <button 
              className={`${styles['filter-button']} ${filterCategory === 'MVFR' ? styles['active'] : ''}`}
              onClick={() => setFilterCategory('MVFR')}
              style={{ color: filterCategory === 'MVFR' ? getFlightCategoryColor('MVFR') : undefined }}
            >
              MVFR ({metrics.flightConditions.mvfr})
            </button>
            <button 
              className={`${styles['filter-button']} ${filterCategory === 'IFR' ? styles['active'] : ''}`}
              onClick={() => setFilterCategory('IFR')}
              style={{ color: filterCategory === 'IFR' ? getFlightCategoryColor('IFR') : undefined }}
            >
              IFR ({metrics.flightConditions.ifr})
            </button>
            <button 
              className={`${styles['filter-button']} ${filterCategory === 'LIFR' ? styles['active'] : ''}`}
              onClick={() => setFilterCategory('LIFR')}
              style={{ color: filterCategory === 'LIFR' ? getFlightCategoryColor('LIFR') : undefined }}
            >
              LIFR ({metrics.flightConditions.lifr})
            </button>
          </div>
        </div>
      </div>

      {/* Airports Grid */}
      <div className={styles['airports-section']}>
        <h2 className={styles['section-title']}>
          🏁 Airports ({filteredAirports.length})
        </h2>
        <div className={styles['airports-grid']}>
          {filteredAirports.map((airport) => (
            <div 
              key={airport.icao} 
              className={styles['airport-card']}
              onClick={() => setSelectedAirport(airport)}
              style={{ borderLeftColor: getFlightCategoryColor(airport.flightCategory) }}
            >
              <div className={styles['airport-header']}>
                <div className={styles['airport-title']}>
                  <span className={styles['icao-code']}>{airport.icao}</span>
                  <span 
                    className={styles['flight-category']}
                    style={{ color: getFlightCategoryColor(airport.flightCategory) }}
                  >
                    {airport.flightCategory}
                  </span>
                </div>
                <div className={styles['airport-location']}>
                  {airport.city}, {airport.country}
                </div>
              </div>
              
              <div className={styles['airport-name']}>{airport.name}</div>
              
              <div className={styles['weather-summary']}>
                <div className={styles['weather-item']}>
                  <span>🌡️ {airport.temperature}°C</span>
                </div>
                <div className={styles['weather-item']}>
                  <span>👁️ {airport.visibility} SM</span>
                </div>
                <div className={styles['weather-item']}>
                  <span>💨 {getWindDirection(airport.windDirection)} {airport.windSpeed} kt</span>
                </div>
                <div className={styles['weather-item']}>
                  <span>📊 {(airport.pressure * 33.8639).toFixed(0)} hPa</span>
                </div>
              </div>
              
              <div className={styles['conditions']}>{airport.conditions}</div>
              <div className={styles['last-update']}>
                Updated: {formatLastUpdated(airport.lastUpdated)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Airport Details Modal */}
      {selectedAirport && (
        <div className={styles['modal-overlay']} onClick={() => setSelectedAirport(null)}>
          <div className={styles['modal-content']} onClick={(e) => e.stopPropagation()}>
            <div className={styles['modal-header']}>
              <h3 className={styles['modal-title']}>
                ✈️ {selectedAirport.icao} - {selectedAirport.name}
              </h3>
              <button 
                className={styles['modal-close']}
                onClick={() => setSelectedAirport(null)}
              >
                ✕
              </button>
            </div>
            
            <div className={styles['modal-body']}>
              <div className={styles['airport-details']}>
                <div className={styles['detail-section']}>
                  <h4>Airport Information</h4>
                  <div className={styles['detail-grid']}>
                    <div className={styles['detail-item']}>
                      <span>ICAO Code:</span>
                      <span>{selectedAirport.icao}</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Location:</span>
                      <span>{selectedAirport.city}, {selectedAirport.country}</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Elevation:</span>
                      <span>{selectedAirport.elevation} ft</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Coordinates:</span>
                      <span>{selectedAirport.latitude.toFixed(4)}, {selectedAirport.longitude.toFixed(4)}</span>
                    </div>
                  </div>
                </div>
                
                <div className={styles['detail-section']}>
                  <h4>Current Weather</h4>
                  <div className={styles['detail-grid']}>
                    <div className={styles['detail-item']}>
                      <span>Flight Category:</span>
                      <span style={{ color: getFlightCategoryColor(selectedAirport.flightCategory) }}>
                        {selectedAirport.flightCategory}
                      </span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Temperature:</span>
                      <span>{selectedAirport.temperature}°C</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Dew Point:</span>
                      <span>{selectedAirport.dewPoint}°C</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Visibility:</span>
                      <span>{selectedAirport.visibility} SM</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Wind:</span>
                      <span>{getWindDirection(selectedAirport.windDirection)} {selectedAirport.windSpeed} kt</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Pressure:</span>
                      <span>{selectedAirport.pressure} inHg ({(selectedAirport.pressure * 33.8639).toFixed(0)} hPa)</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Cloud Ceiling:</span>
                      <span>{selectedAirport.cloudCeiling} ft</span>
                    </div>
                    <div className={styles['detail-item']}>
                      <span>Conditions:</span>
                      <span>{selectedAirport.conditions}</span>
                    </div>
                  </div>
                </div>
                
                <div className={styles['detail-section']}>
                  <h4>METAR Report</h4>
                  <div className={styles['metar-code']}>
                    {selectedAirport.metar}
                  </div>
                </div>
                
                <div className={styles['detail-section']}>
                  <h4>TAF Forecast</h4>
                  <div className={styles['taf-code']}>
                    {selectedAirport.taf}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className={styles['controls']}>
        <button 
          className={styles['refresh-button']}
          onClick={fetchAviationData}
          disabled={isLoading}
        >
          {isLoading ? '⟳ Refreshing...' : '🔄 Refresh Weather Data'}
        </button>
      </div>
    </div>
  );
}
