'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface CityInfo {
  name: string;
  country: string;
  temperature: number;
  humidity: number;
  airQuality: string;
  coreAStatus: string;
  coreBStatus: string;
  asiStatus: string;
}

export const CityInfoSurprise: React.FC = () => {
  const [cities, setCities] = useState<CityInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCities = async () => {
      try {
        const res = await fetch('/api/cities/status', { cache: 'no-store' });
        const data = await res.json();
        setCities(data.cities || []);
      } catch (err) {
        console.error('City API error', err);
        setCities([
          {
            name: 'Bochum',
            country: 'DE',
            temperature: 14.2,
            humidity: 55,
            airQuality: 'Good',
            coreAStatus: 'active',
            coreBStatus: 'active',
            asiStatus: 'stable'
          },
          {
            name: 'Tirana',
            country: 'AL',
            temperature: 18.6,
            humidity: 62,
            airQuality: 'Moderate',
            coreAStatus: 'active',
            coreBStatus: 'learning',
            asiStatus: 'observing'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchCities();
    const timer = setInterval(fetchCities, 10000);
    return () => clearInterval(timer);
  }, []);

  if (loading)
    return (
      <div className="p-6 text-center text-gray-500">
        Loading city intelligence...
      </div>
    );

  return (
    <motion.div
      className="grid md:grid-cols-2 gap-4 p-4 rounded-xl shadow-lg bg-gradient-to-r from-neutral-900 to-neutral-800 text-white border border-gray-700"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1.2 }}
    >
      {cities.map((city, index) => (
        <motion.div
          key={index}
          className="p-4 rounded-lg bg-neutral-700 bg-opacity-30 backdrop-blur-lg hover:scale-105 transition-all cursor-pointer"
          whileHover={{ scale: 1.05 }}
        >
          <h2 className="text-xl font-bold mb-2">
            🌍 {city.name}, {city.country}
          </h2>
          <p>🌡️ Temperature: {city.temperature} °C</p>
          <p>💧 Humidity: {city.humidity}%</p>
          <p>🌫️ Air Quality: {city.airQuality}</p>
          <div className="mt-3 text-sm">
            <span
              className={`px-2 py-1 rounded ${
                city.coreAStatus === 'active' ? 'bg-green-600' : 'bg-gray-600'
              }`}
            >
              Core-A: {city.coreAStatus}
            </span>{' '}
            <span
              className={`px-2 py-1 rounded ${
                city.coreBStatus === 'active' ? 'bg-violet-600' : 'bg-gray-600'
              }`}
            >
              Core-B: {city.coreBStatus}
            </span>{' '}
            <span
              className={`px-2 py-1 rounded ${
                city.asiStatus === 'stable' ? 'bg-purple-600' : 'bg-gray-600'
              }`}
            >
              ASI: {city.asiStatus}
            </span>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
};

export default CityInfoSurprise;
