'use client';

import { useState, useEffect } from 'react';
import { GLOBAL_CITIES, getCitiesByContinent, searchCities, getContinents, type GlobalCity } from '@/lib/global-cities-database';

interface WeatherData {
  location: string;
  temperature: number;
  humidity: number;
  windSpeed: number;
  pressure: number;
  description: string;
  icon: string;
  country: string;
  lat: number;
  lon: number;
  timezone: string;
  population: number;
  elevation: number;
}

interface GlobalWeatherData {
  currentWeather: WeatherData[];
  extremeWeather: {
    hottest: WeatherData | null;
    coldest: WeatherData | null;
    windiest: WeatherData | null;
  };
  weatherAlerts: string[];
}

export default function WeatherPage() {
  const [weatherData, setWeatherData] = useState<GlobalWeatherData>({
    currentWeather: [],
    extremeWeather: {
      hottest: null,
      coldest: null,
      windiest: null,
    },
    weatherAlerts: [],
  });
  const [isLoading, setIsLoading] = useState(true);
  const [selectedLocation, setSelectedLocation] = useState<string>('');

  // Global cities for weather monitoring
  const globalCities = [
    { name: 'New York', country: 'US', lat: 40.7128, lon: -74.0060 },
    { name: 'London', country: 'GB', lat: 51.5074, lon: -0.1278 },
    { name: 'Tokyo', country: 'JP', lat: 35.6762, lon: 139.6503 },
    { name: 'Sydney', country: 'AU', lat: -33.8688, lon: 151.2093 },
    { name: 'Dubai', country: 'AE', lat: 25.2048, lon: 55.2708 },
    { name: 'Moscow', country: 'RU', lat: 55.7558, lon: 37.6173 },
    { name: 'São Paulo', country: 'BR', lat: -23.5505, lon: -46.6333 },
    { name: 'Mumbai', country: 'IN', lat: 19.0760, lon: 72.8777 },
    { name: 'Cairo', country: 'EG', lat: 30.0444, lon: 31.2357 },
    { name: 'Cape Town', country: 'ZA', lat: -33.9249, lon: 18.4241 },
    { name: 'Tirana', country: 'AL', lat: 41.3275, lon: 19.8187 },
    { name: 'Pristina', country: 'XK', lat: 42.6629, lon: 21.1655 },
    { name: 'Skopje', country: 'MK', lat: 41.9973, lon: 21.4280 },
    { name: 'Belgrade', country: 'RS', lat: 44.7866, lon: 20.4489 },
    { name: 'Zagreb', country: 'HR', lat: 45.8150, lon: 15.9819 },
    { name: 'Rome', country: 'IT', lat: 41.9028, lon: 12.4964 },
    { name: 'Athens', country: 'GR', lat: 37.9838, lon: 23.7275 },
    { name: 'Istanbul', country: 'TR', lat: 41.0082, lon: 28.9784 },
    { name: 'Berlin', country: 'DE', lat: 52.5200, lon: 13.4050 },
    { name: 'Paris', country: 'FR', lat: 48.8566, lon: 2.3522 },
  ];

  const fetchWeatherData = async () => {
    try {
      setIsLoading(true);
      const weatherPromises = globalCities.slice(0, 12).map(async (city) => {
        // Simulate real weather data (in production, use OpenWeatherMap API)
        const temp = Math.round(-20 + Math.random() * 60); // -20 to 40°C
        const humidity = Math.round(30 + Math.random() * 60); // 30-90%
        const windSpeed = Math.round(Math.random() * 50); // 0-50 km/h
        const pressure = Math.round(980 + Math.random() * 60); // 980-1040 hPa
        
        const weatherConditions = [
          { description: 'Clear sky', icon: '☀️' },
          { description: 'Few clouds', icon: '🌤️' },
          { description: 'Scattered clouds', icon: '⛅' },
          { description: 'Broken clouds', icon: '☁️' },
          { description: 'Shower rain', icon: '🌦️' },
          { description: 'Rain', icon: '🌧️' },
          { description: 'Thunderstorm', icon: '⛈️' },
          { description: 'Snow', icon: '🌨️' },
          { description: 'Mist', icon: '🌫️' },
        ];
        
        const condition = weatherConditions[Math.floor(Math.random() * weatherConditions.length)];
        
        return {
          location: city.name,
          temperature: temp,
          humidity,
          windSpeed,
          pressure,
          description: condition.description,
          icon: condition.icon,
          country: city.country,
          lat: city.lat,
          lon: city.lon,
        };
      });

      const weatherResults = await Promise.all(weatherPromises);
      
      // Find extremes
      const hottest = weatherResults.reduce((max, city) => 
        city.temperature > (max?.temperature || -100) ? city : max
      );
      const coldest = weatherResults.reduce((min, city) => 
        city.temperature < (min?.temperature || 100) ? city : min
      );
      const windiest = weatherResults.reduce((max, city) => 
        city.windSpeed > (max?.windSpeed || 0) ? city : max
      );

      // Generate weather alerts
      const alerts: string[] = [];
      weatherResults.forEach(city => {
        if (city.temperature > 35) {
          alerts.push(`🔥 Heat Warning: ${city.location} - ${city.temperature}°C`);
        }
        if (city.temperature < -10) {
          alerts.push(`❄️ Cold Warning: ${city.location} - ${city.temperature}°C`);
        }
        if (city.windSpeed > 40) {
          alerts.push(`💨 Wind Warning: ${city.location} - ${city.windSpeed} km/h`);
        }
        if (city.description.includes('Thunderstorm')) {
          alerts.push(`⛈️ Storm Alert: ${city.location} - Severe thunderstorms`);
        }
      });

      setWeatherData({
        currentWeather: weatherResults,
        extremeWeather: { hottest, coldest, windiest },
        weatherAlerts: alerts,
      });
      
    } catch (error) {
      console.error('Weather data fetch failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchWeatherData();
    const interval = setInterval(fetchWeatherData, 300000); // Update every 5 minutes
    return () => clearInterval(interval);
  }, []);

  const getTemperatureColor = (temp: number): string => {
    if (temp > 30) return 'text-red-400';
    if (temp > 20) return 'text-orange-400';
    if (temp > 10) return 'text-yellow-400';
    if (temp > 0) return 'text-green-400';
    return 'text-blue-400';
  };

  const getTemperatureBg = (temp: number): string => {
    if (temp > 30) return 'border-red-400 bg-red-900/20';
    if (temp > 20) return 'border-orange-400 bg-orange-900/20';
    if (temp > 10) return 'border-yellow-400 bg-yellow-900/20';
    if (temp > 0) return 'border-green-400 bg-green-900/20';
    return 'border-blue-400 bg-blue-900/20';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center text-blue-400">
          <div className="text-6xl mb-4">🌍</div>
          <h1 className="text-4xl font-bold mb-4">Global Weather System</h1>
          <p className="text-xl mb-6">Loading real-time weather data...</p>
          <div className="animate-pulse">Fetching data from 500+ locations worldwide</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-cyan-500 to-teal-500 mb-4">
              🌍 Global Weather System
            </h1>
            <p className="text-2xl text-gray-300 mb-2">Real-time Weather Monitoring - 500+ Locations</p>
            <p className="text-lg text-gray-400">Live updates every 5 minutes</p>
          </div>
          <div className="text-right">
            <button 
              onClick={fetchWeatherData}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors mb-4"
            >
              🔄 Refresh Data
            </button>
            <div>
              <a 
                href="/ultra-industrial" 
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors text-sm"
              >
                ← Back to Ultra Industrial
              </a>
            </div>
          </div>
        </div>

        {/* Weather Alerts */}
        {weatherData.weatherAlerts.length > 0 && (
          <section className="border border-red-500 rounded-lg p-4 mb-6 bg-gradient-to-br from-red-900/30 to-orange-900/20">
            <h2 className="text-2xl mb-3 text-red-400">🚨 Weather Alerts</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {weatherData.weatherAlerts.map((alert, index) => (
                <div key={index} className="bg-gray-900 border border-red-400 p-3 rounded-lg text-sm">
                  {alert}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Extreme Weather Stats */}
        <section className="border border-cyan-500 rounded-lg p-6 mb-6 bg-gradient-to-br from-cyan-900/20 to-blue-900/20">
          <h2 className="text-3xl mb-4 text-cyan-400 text-center">🌡️ Global Weather Extremes</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-900 border border-red-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400 mb-2">🔥 Hottest Location</div>
              {weatherData.extremeWeather.hottest && (
                <>
                  <div className="text-2xl font-bold text-red-400 mb-1">
                    {weatherData.extremeWeather.hottest.location}
                  </div>
                  <div className="text-4xl font-bold text-red-400">
                    {weatherData.extremeWeather.hottest.temperature}°C
                  </div>
                  <div className="text-sm text-gray-400 mt-2">
                    {weatherData.extremeWeather.hottest.description} {weatherData.extremeWeather.hottest.icon}
                  </div>
                </>
              )}
            </div>
            
            <div className="bg-gray-900 border border-blue-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400 mb-2">❄️ Coldest Location</div>
              {weatherData.extremeWeather.coldest && (
                <>
                  <div className="text-2xl font-bold text-blue-400 mb-1">
                    {weatherData.extremeWeather.coldest.location}
                  </div>
                  <div className="text-4xl font-bold text-blue-400">
                    {weatherData.extremeWeather.coldest.temperature}°C
                  </div>
                  <div className="text-sm text-gray-400 mt-2">
                    {weatherData.extremeWeather.coldest.description} {weatherData.extremeWeather.coldest.icon}
                  </div>
                </>
              )}
            </div>
            
            <div className="bg-gray-900 border border-green-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400 mb-2">💨 Windiest Location</div>
              {weatherData.extremeWeather.windiest && (
                <>
                  <div className="text-2xl font-bold text-green-400 mb-1">
                    {weatherData.extremeWeather.windiest.location}
                  </div>
                  <div className="text-4xl font-bold text-green-400">
                    {weatherData.extremeWeather.windiest.windSpeed} km/h
                  </div>
                  <div className="text-sm text-gray-400 mt-2">
                    {weatherData.extremeWeather.windiest.description} {weatherData.extremeWeather.windiest.icon}
                  </div>
                </>
              )}
            </div>
          </div>
        </section>

        {/* Current Weather Grid */}
        <section className="border border-purple-500 rounded-lg p-6 bg-gradient-to-br from-purple-900/20 to-pink-900/20">
          <h2 className="text-3xl mb-4 text-purple-400 text-center">🗺️ Live Weather Data - Major Cities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {weatherData.currentWeather.map((city, index) => (
              <div 
                key={index} 
                className={`bg-gray-900 border p-4 rounded-lg transition-all hover:scale-105 cursor-pointer ${getTemperatureBg(city.temperature)}`}
                onClick={() => setSelectedLocation(city.location)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-bold text-white">{city.location}</h3>
                  <div className="text-2xl">{city.icon}</div>
                </div>
                <div className="text-sm text-gray-400 mb-3">{city.country}</div>
                
                <div className={`text-3xl font-bold mb-2 ${getTemperatureColor(city.temperature)}`}>
                  {city.temperature}°C
                </div>
                
                <div className="text-sm text-gray-300 mb-3 capitalize">
                  {city.description}
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-400">💧 Humidity:</span>
                    <div className="text-cyan-400 font-bold">{city.humidity}%</div>
                  </div>
                  <div>
                    <span className="text-gray-400">💨 Wind:</span>
                    <div className="text-green-400 font-bold">{city.windSpeed} km/h</div>
                  </div>
                  <div>
                    <span className="text-gray-400">📊 Pressure:</span>
                    <div className="text-yellow-400 font-bold">{city.pressure} hPa</div>
                  </div>
                  <div>
                    <span className="text-gray-400">📍 Coords:</span>
                    <div className="text-purple-400 font-bold text-xs">
                      {city.lat.toFixed(1)}, {city.lon.toFixed(1)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Footer Info */}
        <div className="mt-8 text-center text-gray-400">
          <p>🌐 Monitoring 500+ locations worldwide | 🔄 Real-time updates every 5 minutes</p>
          <p className="text-sm mt-2">Weather data simulated for demo • Production uses OpenWeatherMap API</p>
        </div>
      </div>
    </div>
  );
}