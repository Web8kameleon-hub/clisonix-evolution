'use client';

import dynamic from 'next/dynamic';
import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

/**
 * COGNITIVE IMPACT MONITOR
 * Clisonix Neural Performance Module
 * 
 * Real-time weather data with cognitive impact analysis
 * How environment affects your brain performance
 */

interface WeatherData {
    city: string;
    country: string;
    temperature: number;
    humidity: number;
    windSpeed: number;
    windDirection: number;
    pressure: number;
    weatherCode: number;
    uvIndex: number;
    visibility: number;
    cloudCover: number;
}

interface AviationData {
    flightConditions: 'VFR' | 'MVFR' | 'IFR' | 'LIFR';
    ceilingFt: number;
    visibilityMi: number;
    windKnots: number;
    crosswindComponent: number;
    turbulenceProbability: number;
    icingRisk: 'none' | 'light' | 'moderate' | 'severe';
}

interface CognitiveImpact {
    overall: 'optimal' | 'moderate' | 'challenging';
    score: number;
    factors: {
        temperature: { impact: string; recommendation: string };
        pressure: { impact: string; migraineRisk: number };
        humidity: { impact: string; recommendation: string };
    };
    neurofeedbackAdvice: string;
    sessionQuality: string;
}

interface APIResponse {
    weather: WeatherData[];
    aviation: AviationData;
    cognitive: CognitiveImpact;
    alertActive: boolean;
    timestamp: string;
    responseTime: number;
}

// Weather code descriptions
const weatherCodes: Record<number, { icon: string; desc: string }> = {
    0: { icon: '☀️', desc: 'Clear sky' },
    1: { icon: '🌤️', desc: 'Mainly clear' },
    2: { icon: '⛅', desc: 'Partly cloudy' },
    3: { icon: '☁️', desc: 'Overcast' },
    45: { icon: '🌫️', desc: 'Fog' },
    48: { icon: '🌫️', desc: 'Depositing rime fog' },
    51: { icon: '🌧️', desc: 'Light drizzle' },
    53: { icon: '🌧️', desc: 'Moderate drizzle' },
    55: { icon: '🌧️', desc: 'Dense drizzle' },
    61: { icon: '🌧️', desc: 'Slight rain' },
    63: { icon: '🌧️', desc: 'Moderate rain' },
    65: { icon: '🌧️', desc: 'Heavy rain' },
    71: { icon: '🌨️', desc: 'Slight snow' },
    73: { icon: '🌨️', desc: 'Moderate snow' },
    75: { icon: '❄️', desc: 'Heavy snow' },
    80: { icon: '🌦️', desc: 'Rain showers' },
    95: { icon: '⛈️', desc: 'Thunderstorm' },
};

const albanianCities = [
    { name: 'Tirana', lat: 41.3275, lon: 19.8187, icao: 'LATI' },
    { name: 'Durrës', lat: 41.3246, lon: 19.4565, icao: 'LADR' },
    { name: 'Vlorë', lat: 40.4667, lon: 19.4897, icao: 'LAVL' },
    { name: 'Shkodër', lat: 42.0693, lon: 19.5033, icao: 'LASK' },
    { name: 'Elbasan', lat: 41.1125, lon: 20.0822, icao: 'LAEL' },
    { name: 'Korçë', lat: 40.6186, lon: 20.7808, icao: 'LAKR' },
    { name: 'Kukës', lat: 42.0769, lon: 20.4219, icao: 'LAKU' },
    { name: 'Gjirokastër', lat: 40.0758, lon: 20.1389, icao: 'LAGJ' },
];

export default function WeatherDashboard() {
    const [data, setData] = useState<APIResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedCity, setSelectedCity] = useState<string>('Tirana');
    const [viewMode, setViewMode] = useState<'weather' | 'aviation' | 'cognitive'>('weather');

    const fetchWeatherData = useCallback(async () => {
        const startTime = performance.now();
        setLoading(true);

        try {
            // Fetch real weather from Open-Meteo for all cities
            const weatherPromises = albanianCities.map(async (city) => {
                const response = await fetch(
                    `https://api.open-meteo.com/v1/forecast?latitude=${city.lat}&longitude=${city.lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,surface_pressure,weather_code,cloud_cover&timezone=Europe/Tirane`
                );
                const result = await response.json();
                return {
                    city: city.name,
                    country: 'Albania',
                    icao: city.icao,
                    temperature: result.current?.temperature_2m || 0,
                    humidity: result.current?.relative_humidity_2m || 0,
                    windSpeed: result.current?.wind_speed_10m || 0,
                    windDirection: result.current?.wind_direction_10m || 0,
                    pressure: result.current?.surface_pressure || 1013,
                    weatherCode: result.current?.weather_code || 0,
                    uvIndex: 0,
                    visibility: 10000,
                    cloudCover: result.current?.cloud_cover || 0,
                };
            });

            const weatherData = await Promise.all(weatherPromises);
            const endTime = performance.now();

            const currentCity = weatherData.find(w => w.city === selectedCity) || weatherData[0];
            
            // Calculate aviation data
            const aviation = calculateAviationData(currentCity);
            
            // Calculate cognitive impact
            const cognitive = calculateCognitiveImpact(currentCity);

            setData({
                weather: weatherData,
                aviation,
                cognitive,
                alertActive: cognitive.factors.pressure.migraineRisk > 60 || aviation.flightConditions === 'IFR' || aviation.flightConditions === 'LIFR',
                timestamp: new Date().toISOString(),
                responseTime: Math.round(endTime - startTime)
            });
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch weather data');
        } finally {
            setLoading(false);
        }
    }, [selectedCity]);

    const calculateAviationData = (weather: WeatherData): AviationData => {
        // Calculate ceiling based on cloud cover and weather code
        const ceilingFt = weather.cloudCover > 80 ? 1000 : 
                         weather.cloudCover > 50 ? 3000 : 
                         weather.cloudCover > 25 ? 5000 : 10000;
        
        // Visibility based on weather code
        const visibilityMi = weather.weatherCode >= 45 && weather.weatherCode <= 48 ? 0.5 :
                            weather.weatherCode >= 61 ? 3 :
                            weather.weatherCode >= 51 ? 5 : 10;
        
        // Wind in knots
        const windKnots = Math.round(weather.windSpeed * 0.539957);
        
        // Flight conditions
        let flightConditions: 'VFR' | 'MVFR' | 'IFR' | 'LIFR';
        if (ceilingFt >= 3000 && visibilityMi >= 5) {
            flightConditions = 'VFR';
        } else if (ceilingFt >= 1000 && visibilityMi >= 3) {
            flightConditions = 'MVFR';
        } else if (ceilingFt >= 500 && visibilityMi >= 1) {
            flightConditions = 'IFR';
        } else {
            flightConditions = 'LIFR';
        }

        // Turbulence probability based on wind
        const turbulenceProbability = windKnots > 25 ? 80 : windKnots > 15 ? 40 : windKnots > 10 ? 20 : 5;

        // Icing risk based on temperature and weather
        const icingRisk: 'none' | 'light' | 'moderate' | 'severe' = 
            weather.temperature < 0 && weather.cloudCover > 50 ? 'moderate' :
            weather.temperature < 5 && weather.humidity > 80 ? 'light' : 'none';

        return {
            flightConditions,
            ceilingFt,
            visibilityMi,
            windKnots,
            crosswindComponent: Math.round(windKnots * 0.3), // Simplified
            turbulenceProbability,
            icingRisk,
        };
    };

    const calculateCognitiveImpact = (weather: WeatherData): CognitiveImpact => {
        const tempOptimal = weather.temperature >= 18 && weather.temperature <= 24;
        const tempImpact = tempOptimal ? 'Optimal' : weather.temperature < 18 ? 'Cool - may reduce alertness' : 'Warm - may cause fatigue';
        const tempScore = tempOptimal ? 100 : Math.max(0, 100 - Math.abs(weather.temperature - 21) * 5);

        const pressureNormal = weather.pressure >= 1000 && weather.pressure <= 1025;
        const migraineRisk = weather.pressure < 1000 ? Math.min(100, (1000 - weather.pressure) * 2) :
            weather.pressure > 1025 ? Math.min(50, (weather.pressure - 1025)) : 0;
        const pressureImpact = pressureNormal ? 'Stable' : weather.pressure < 1000 ? 'Low - potential headache trigger' : 'High - generally favorable';
        const pressureScore = 100 - migraineRisk;

        const humidityOptimal = weather.humidity >= 40 && weather.humidity <= 60;
        const humidityImpact = humidityOptimal ? 'Optimal' : weather.humidity < 40 ? 'Dry - may cause discomfort' : 'Humid - may feel sluggish';
        const humidityScore = humidityOptimal ? 100 : Math.max(0, 100 - Math.abs(weather.humidity - 50));

        const overallScore = Math.round((tempScore + pressureScore + humidityScore) / 3);
        const overall: 'optimal' | 'moderate' | 'challenging' =
            overallScore >= 70 ? 'optimal' : overallScore >= 40 ? 'moderate' : 'challenging';

        const sessionQuality = overallScore >= 70 ? 'Excellent - ideal conditions' :
            overallScore >= 50 ? 'Good - minor environmental factors' :
            'Consider rescheduling - suboptimal conditions';

        const neurofeedbackAdvice = overall === 'optimal'
            ? '✅ Excellent conditions for cognitive tasks.'
            : overall === 'moderate'
                ? '⚡ Moderate conditions. Take breaks as needed.'
                : '⚠️ Challenging conditions. Consider postponing intensive tasks.';

        return {
            overall,
            score: overallScore,
            factors: {
                temperature: { impact: tempImpact, recommendation: tempOptimal ? 'Maintain current conditions' : 'Adjust temperature if possible' },
                pressure: { impact: pressureImpact, migraineRisk },
                humidity: { impact: humidityImpact, recommendation: humidityOptimal ? 'Good air quality' : 'Consider humidity adjustment' }
            },
            neurofeedbackAdvice,
            sessionQuality
        };
    };

    useEffect(() => {
        fetchWeatherData();
        const interval = setInterval(fetchWeatherData, 300000); // Update every 5 minutes
        return () => clearInterval(interval);
    }, [fetchWeatherData]);

    const currentWeather = data?.weather.find(w => w.city === selectedCity) || data?.weather[0];
    const weatherInfo = currentWeather ? weatherCodes[currentWeather.weatherCode] || { icon: '🌡️', desc: 'Unknown' } : null;

    const getFlightConditionColor = (condition: string) => {
        switch (condition) {
            case 'VFR': return 'bg-green-500 text-white';
            case 'MVFR': return 'bg-blue-500 text-white';
            case 'IFR': return 'bg-red-500 text-white';
            case 'LIFR': return 'bg-purple-500 text-white';
            default: return 'bg-gray-500 text-white';
        }
    };

    const getImpactColor = (impact: string) => {
        if (impact === 'optimal') return 'text-green-400 bg-green-500/20';
        if (impact === 'moderate') return 'text-yellow-400 bg-yellow-500/20';
        return 'text-red-400 bg-red-500/20';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <Link href="/modules" className="text-blue-400 hover:text-blue-300 mb-4 inline-flex items-center gap-2">
                    ← Back to Modules
                </Link>

                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                            ✈️ Aviation Weather Dashboard
                        </h1>
                        <p className="text-gray-400 mt-1">
                            Real-time Weather • Aviation Conditions • Cognitive Analysis
                        </p>
                    </div>

                    <div className="flex items-center gap-3">
                        {/* View Mode Tabs */}
                        <div className="flex bg-white/10 rounded-lg p-1">
                            {(['weather', 'aviation', 'cognitive'] as const).map((mode) => (
                                <button
                                    key={mode}
                                    onClick={() => setViewMode(mode)}
                                    className={`px-4 py-2 rounded-md text-sm transition-colors capitalize ${
                                        viewMode === mode 
                                            ? 'bg-blue-600 text-white' 
                                            : 'text-gray-400 hover:text-white'
                                    }`}
                                >
                                    {mode === 'weather' ? '🌤️ Weather' : mode === 'aviation' ? '✈️ Aviation' : '🧠 Cognitive'}
                                </button>
                            ))}
                        </div>

                        <button
                            onClick={fetchWeatherData}
                            disabled={loading}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 text-white"
                        >
                            {loading ? '⏳' : '🔄'} Refresh
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-4 mb-6">
                        <div className="flex items-center gap-2 text-red-400">
                            ⚠️ <span>{error}</span>
                        </div>
                    </div>
                )}

                {/* Alert Banner */}
                {data?.alertActive && (
                    <div className="bg-orange-500/20 border border-orange-500/50 rounded-xl p-4 mb-6 animate-pulse">
                        <div className="flex items-center gap-3">
                            <span className="text-2xl">⚠️</span>
                            <div>
                                <p className="text-orange-400 font-semibold">Weather Alert Active</p>
                                <p className="text-orange-300 text-sm">
                                    {data.aviation.flightConditions === 'IFR' || data.aviation.flightConditions === 'LIFR' 
                                        ? `Instrument conditions detected (${data.aviation.flightConditions}). Reduced visibility.`
                                        : `Barometric pressure alert (${currentWeather?.pressure.toFixed(0)} hPa). Migraine risk elevated.`}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* City Selector */}
                <div className="flex gap-2 mb-6 flex-wrap">
                    {albanianCities.map((city) => (
                        <button
                            key={city.name}
                            onClick={() => setSelectedCity(city.name)}
                            className={`px-4 py-2 rounded-lg text-sm transition-colors ${
                                selectedCity === city.name
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                            }`}
                        >
                            {city.name}
                        </button>
                    ))}
                </div>

                {/* Main Content */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Panel - Current Conditions */}
                    <div className="lg:col-span-2">
                        {viewMode === 'weather' && currentWeather && (
                            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
                                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                                    🌤️ Current Weather - {selectedCity}
                                </h2>

                                <div className="bg-gradient-to-br from-blue-600/20 to-purple-600/20 rounded-xl p-6 mb-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h3 className="text-3xl font-bold text-white">{selectedCity}</h3>
                                            <p className="text-gray-400">Albania • {albanianCities.find(c => c.name === selectedCity)?.icao}</p>
                                        </div>
                                        <div className="text-right">
                                            <span className="text-6xl">{weatherInfo?.icon}</span>
                                            <p className="text-4xl font-bold text-white mt-2">
                                                {currentWeather.temperature.toFixed(1)}°C
                                            </p>
                                            <p className="text-gray-400">{weatherInfo?.desc}</p>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-4 gap-4 mt-6">
                                        <div className="text-center bg-white/5 rounded-lg p-3">
                                            <span className="text-2xl">💧</span>
                                            <p className="text-white font-medium">{currentWeather.humidity}%</p>
                                            <p className="text-gray-500 text-xs">Humidity</p>
                                        </div>
                                        <div className="text-center bg-white/5 rounded-lg p-3">
                                            <span className="text-2xl">💨</span>
                                            <p className="text-white font-medium">{currentWeather.windSpeed.toFixed(1)} km/h</p>
                                            <p className="text-gray-500 text-xs">Wind</p>
                                        </div>
                                        <div className="text-center bg-white/5 rounded-lg p-3">
                                            <span className="text-2xl">📊</span>
                                            <p className="text-white font-medium">{currentWeather.pressure.toFixed(0)} hPa</p>
                                            <p className="text-gray-500 text-xs">Pressure</p>
                                        </div>
                                        <div className="text-center bg-white/5 rounded-lg p-3">
                                            <span className="text-2xl">☁️</span>
                                            <p className="text-white font-medium">{currentWeather.cloudCover}%</p>
                                            <p className="text-gray-500 text-xs">Cloud Cover</p>
                                        </div>
                                    </div>
                                </div>

                                {/* All Cities Grid */}
                                <h3 className="text-lg font-semibold text-white mb-3">Other Locations</h3>
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                    {data?.weather.filter(w => w.city !== selectedCity).map((city) => (
                                        <button
                                            key={city.city}
                                            onClick={() => setSelectedCity(city.city)}
                                            className="bg-white/5 rounded-lg p-3 text-left hover:bg-white/10 transition-colors"
                                        >
                                            <div className="flex items-center justify-between mb-1">
                                                <span className="text-white font-medium">{city.city}</span>
                                                <span>{weatherCodes[city.weatherCode]?.icon || '🌡️'}</span>
                                            </div>
                                            <p className="text-xl font-bold text-white">{city.temperature.toFixed(1)}°C</p>
                                            <p className="text-gray-500 text-xs">{city.humidity}% • {city.pressure.toFixed(0)} hPa</p>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        )}

                        {viewMode === 'aviation' && data?.aviation && (
                            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
                                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                                    ✈️ Aviation Weather - {selectedCity}
                                </h2>

                                <div className="grid grid-cols-2 gap-4 mb-6">
                                    {/* Flight Conditions */}
                                    <div className="bg-white/5 rounded-xl p-4">
                                        <p className="text-gray-400 text-sm mb-2">Flight Conditions</p>
                                        <div className={`inline-block px-4 py-2 rounded-lg font-bold ${getFlightConditionColor(data.aviation.flightConditions)}`}>
                                            {data.aviation.flightConditions}
                                        </div>
                                        <p className="text-gray-500 text-xs mt-2">
                                            {data.aviation.flightConditions === 'VFR' ? 'Visual Flight Rules - Good visibility' :
                                             data.aviation.flightConditions === 'MVFR' ? 'Marginal VFR - Reduced visibility' :
                                             data.aviation.flightConditions === 'IFR' ? 'Instrument Flight Rules - Low visibility' :
                                             'Low IFR - Very poor conditions'}
                                        </p>
                                    </div>

                                    {/* Ceiling */}
                                    <div className="bg-white/5 rounded-xl p-4">
                                        <p className="text-gray-400 text-sm mb-2">Ceiling</p>
                                        <p className="text-2xl font-bold text-white">{data.aviation.ceilingFt.toLocaleString()} ft</p>
                                        <p className="text-gray-500 text-xs mt-1">Cloud base height</p>
                                    </div>

                                    {/* Visibility */}
                                    <div className="bg-white/5 rounded-xl p-4">
                                        <p className="text-gray-400 text-sm mb-2">Visibility</p>
                                        <p className="text-2xl font-bold text-white">{data.aviation.visibilityMi} SM</p>
                                        <p className="text-gray-500 text-xs mt-1">Statute miles</p>
                                    </div>

                                    {/* Wind */}
                                    <div className="bg-white/5 rounded-xl p-4">
                                        <p className="text-gray-400 text-sm mb-2">Wind</p>
                                        <p className="text-2xl font-bold text-white">{currentWeather?.windDirection}° @ {data.aviation.windKnots} kt</p>
                                        <p className="text-gray-500 text-xs mt-1">Crosswind: ~{data.aviation.crosswindComponent} kt</p>
                                    </div>
                                </div>

                                {/* Hazards */}
                                <div className="bg-white/5 rounded-xl p-4">
                                    <h3 className="text-lg font-semibold text-white mb-3">⚠️ Hazard Assessment</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p className="text-gray-400 text-sm">Turbulence Probability</p>
                                            <div className="flex items-center gap-2 mt-1">
                                                <div className="flex-1 bg-gray-700 rounded-full h-2">
                                                    <div 
                                                        className={`h-2 rounded-full ${data.aviation.turbulenceProbability > 50 ? 'bg-red-500' : 'bg-green-500'}`}
                                                        style={{ width: `${data.aviation.turbulenceProbability}%` }}
                                                    />
                                                </div>
                                                <span className="text-white text-sm">{data.aviation.turbulenceProbability}%</span>
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-gray-400 text-sm">Icing Risk</p>
                                            <p className={`text-lg font-medium capitalize ${
                                                data.aviation.icingRisk === 'none' ? 'text-green-400' :
                                                data.aviation.icingRisk === 'light' ? 'text-yellow-400' :
                                                'text-red-400'
                                            }`}>
                                                {data.aviation.icingRisk}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {viewMode === 'cognitive' && data?.cognitive && (
                            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6">
                                <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                                    🧠 Cognitive Impact Analysis
                                </h2>

                                <div className={`rounded-xl p-6 text-center mb-6 ${getImpactColor(data.cognitive.overall)}`}>
                                    <p className="text-5xl font-bold">{data.cognitive.score}</p>
                                    <p className="text-lg capitalize mt-1">{data.cognitive.overall} Conditions</p>
                                </div>

                                <div className="space-y-4">
                                    <div className="bg-white/5 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-gray-400">🌡️ Temperature</span>
                                            <span className="text-white">{currentWeather?.temperature.toFixed(1)}°C</span>
                                        </div>
                                        <p className="text-sm text-gray-500">{data.cognitive.factors.temperature.impact}</p>
                                        <p className="text-xs text-blue-400 mt-1">{data.cognitive.factors.temperature.recommendation}</p>
                                    </div>

                                    <div className="bg-white/5 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-gray-400">📊 Pressure</span>
                                            <span className="text-white">{currentWeather?.pressure.toFixed(0)} hPa</span>
                                        </div>
                                        <p className="text-sm text-gray-500">{data.cognitive.factors.pressure.impact}</p>
                                        <div className="mt-2">
                                            <div className="flex justify-between text-xs mb-1">
                                                <span className="text-gray-500">Migraine Risk</span>
                                                <span className={data.cognitive.factors.pressure.migraineRisk > 50 ? 'text-red-400' : 'text-green-400'}>
                                                    {data.cognitive.factors.pressure.migraineRisk}%
                                                </span>
                                            </div>
                                            <div className="w-full bg-gray-700 rounded-full h-2">
                                                <div
                                                    className={`h-2 rounded-full ${data.cognitive.factors.pressure.migraineRisk > 50 ? 'bg-red-500' : 'bg-green-500'}`}
                                                    style={{ width: `${data.cognitive.factors.pressure.migraineRisk}%` }}
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    <div className="bg-white/5 rounded-lg p-4">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-gray-400">💧 Humidity</span>
                                            <span className="text-white">{currentWeather?.humidity}%</span>
                                        </div>
                                        <p className="text-sm text-gray-500">{data.cognitive.factors.humidity.impact}</p>
                                        <p className="text-xs text-blue-400 mt-1">{data.cognitive.factors.humidity.recommendation}</p>
                                    </div>
                                </div>

                                <div className="bg-purple-500/20 rounded-lg p-4 mt-4">
                                    <p className="text-purple-300 font-medium mb-1">Session Recommendation</p>
                                    <p className="text-purple-200 text-sm">{data.cognitive.neurofeedbackAdvice}</p>
                                    <p className="text-purple-400 text-xs mt-2">Quality: {data.cognitive.sessionQuality}</p>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right Panel - Quick Stats */}
                    <div className="lg:col-span-1 space-y-4">
                        {/* Flight Conditions Badge */}
                        {data?.aviation && (
                            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4">
                                <h3 className="text-sm font-medium text-gray-400 mb-3">Flight Conditions</h3>
                                <div className={`text-center py-4 rounded-lg ${getFlightConditionColor(data.aviation.flightConditions)}`}>
                                    <p className="text-3xl font-bold">{data.aviation.flightConditions}</p>
                                    <p className="text-sm opacity-80">
                                        {data.aviation.ceilingFt.toLocaleString()} ft / {data.aviation.visibilityMi} SM
                                    </p>
                                </div>
                            </div>
                        )}

                        {/* Cognitive Score */}
                        {data?.cognitive && (
                            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4">
                                <h3 className="text-sm font-medium text-gray-400 mb-3">Cognitive Score</h3>
                                <div className={`text-center py-4 rounded-lg ${getImpactColor(data.cognitive.overall)}`}>
                                    <p className="text-3xl font-bold">{data.cognitive.score}/100</p>
                                    <p className="text-sm opacity-80 capitalize">{data.cognitive.overall}</p>
                                </div>
                            </div>
                        )}

                        {/* Wind Rose */}
                        {currentWeather && (
                            <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4">
                                <h3 className="text-sm font-medium text-gray-400 mb-3">Wind</h3>
                                <div className="text-center">
                                    <div className="relative inline-block">
                                        <div className="w-20 h-20 rounded-full border-2 border-gray-600 flex items-center justify-center">
                                            <div 
                                                className="text-2xl transform"
                                                style={{ transform: `rotate(${currentWeather.windDirection}deg)` }}
                                            >
                                                ⬆️
                                            </div>
                                        </div>
                                    </div>
                                    <p className="text-white font-medium mt-2">{currentWeather.windDirection}°</p>
                                    <p className="text-gray-400 text-sm">{currentWeather.windSpeed.toFixed(1)} km/h</p>
                                </div>
                            </div>
                        )}

                        {/* API Status */}
                        <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-4">
                            <h3 className="text-sm font-medium text-gray-400 mb-3">Data Source</h3>
                            <div className="flex items-center gap-2 text-green-400">
                                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                                <span className="text-sm">Open-Meteo API</span>
                            </div>
                            {data && (
                                <div className="mt-2 text-xs text-gray-500">
                                    <p>Response: {data.responseTime}ms</p>
                                    <p>Updated: {new Date(data.timestamp).toLocaleTimeString()}</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="mt-8 text-center text-xs text-gray-600">
                    Cognitive Impact Monitor - Clisonix Cloud - Real-time Open-Meteo Data
                </div>
            </div>
        </div>
    );
}

// Dynamic export to prevent SSR hydration issues
export default dynamic(() => Promise.resolve(CognitiveImpactDashboard), { ssr: false });

function CognitiveImpactDashboard() {
    return <WeatherDashboard />;
}
