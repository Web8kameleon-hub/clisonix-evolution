'use client';

import { useState, useEffect } from 'react';

interface BiologicalData {
  ecosystems: {
    name: string;
    biodiversity: number;
    health: number;
    species: number;
  }[];
  climate: {
    temperature: number;
    humidity: number;
    carbonLevel: number;
    oxygenLevel: number;
  };
  wildlife: {
    endangered: number;
    protected: number;
    migrating: number;
  };
}

export default function AgixBioNaturePage() {
  const [biologicalData, setBiologicalData] = useState<BiologicalData>({
    ecosystems: [],
    climate: {
      temperature: 0,
      humidity: 0,
      carbonLevel: 0,
      oxygenLevel: 0,
    },
    wildlife: {
      endangered: 0,
      protected: 0,
      migrating: 0,
    },
  });

  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchBioData = async () => {
      try {
        // Simulate biological data collection
        const ecosystems = [
          { name: 'Tropical Rainforest', biodiversity: 95, health: 78, species: 50000 },
          { name: 'Coral Reefs', biodiversity: 88, health: 65, species: 25000 },
          { name: 'Temperate Forests', biodiversity: 82, health: 85, species: 15000 },
          { name: 'Grasslands', biodiversity: 75, health: 90, species: 8000 },
          { name: 'Wetlands', biodiversity: 90, health: 72, species: 12000 },
        ];

        const climate = {
          temperature: 15.2 + Math.sin(Date.now() / 100000) * 5,
          humidity: 65 + Math.cos(Date.now() / 80000) * 15,
          carbonLevel: 415 + Math.sin(Date.now() / 120000) * 10,
          oxygenLevel: 20.95 + Math.cos(Date.now() / 90000) * 0.5,
        };

        const wildlife = {
          endangered: 41415,
          protected: 238000,
          migrating: Math.floor(50000 + Math.sin(Date.now() / 200000) * 20000),
        };

        setBiologicalData({
          ecosystems,
          climate,
          wildlife,
        });
      } catch (error) {
        console.error('Failed to fetch biological data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchBioData();
    const interval = setInterval(fetchBioData, 10000);

    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="text-center text-green-400">
          <div className="text-6xl mb-4">🌍</div>
          <h1 className="text-4xl font-bold mb-4">AGIX BioNature</h1>
          <p className="text-xl mb-6">AI-Powered Biological Intelligence</p>
          <div className="animate-pulse">Loading ecosystem data...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-black text-white p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 via-emerald-500 to-teal-500 mb-4">
            🌍 AGIX BioNature
          </h1>
          <p className="text-2xl text-gray-300 mb-2">AI-Powered Biological Intelligence Platform</p>
          <p className="text-lg text-gray-400">Real-time Ecosystem Monitoring & Analysis</p>
        </div>

        {/* Climate Monitoring */}
        <section className="border border-green-500 rounded-lg p-6 mb-6 bg-gradient-to-br from-green-900/20 to-emerald-900/20">
          <h2 className="text-3xl mb-4 text-green-400 text-center">🌡️ Global Climate Status</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-900 border border-blue-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400">Temperature</div>
              <div className="text-3xl font-bold text-blue-400">
                {biologicalData.climate.temperature.toFixed(1)}°C
              </div>
            </div>
            <div className="bg-gray-900 border border-cyan-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400">Humidity</div>
              <div className="text-3xl font-bold text-cyan-400">
                {biologicalData.climate.humidity.toFixed(1)}%
              </div>
            </div>
            <div className="bg-gray-900 border border-orange-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400">CO₂ Level</div>
              <div className="text-3xl font-bold text-orange-400">
                {biologicalData.climate.carbonLevel.toFixed(1)} ppm
              </div>
            </div>
            <div className="bg-gray-900 border border-green-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400">O₂ Level</div>
              <div className="text-3xl font-bold text-green-400">
                {biologicalData.climate.oxygenLevel.toFixed(2)}%
              </div>
            </div>
          </div>
        </section>

        {/* Ecosystem Health */}
        <section className="border border-emerald-500 rounded-lg p-6 mb-6 bg-gradient-to-br from-emerald-900/20 to-teal-900/20">
          <h2 className="text-3xl mb-4 text-emerald-400 text-center">🌳 Ecosystem Health Monitor</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {biologicalData.ecosystems.map((ecosystem, index) => (
              <div key={index} className="bg-gray-900 border border-emerald-400 p-4 rounded-lg">
                <h3 className="text-lg font-bold text-emerald-400 mb-2">{ecosystem.name}</h3>
                <div className="space-y-2">
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Biodiversity</span>
                      <span className="text-green-400">{ecosystem.biodiversity}%</span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full">
                      <div 
                        className="h-full bg-green-500 rounded-full"
                        style={{ width: `${ecosystem.biodiversity}%` }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm">
                      <span>Health Score</span>
                      <span className={`${ecosystem.health > 80 ? 'text-green-400' : ecosystem.health > 60 ? 'text-yellow-400' : 'text-red-400'}`}>
                        {ecosystem.health}%
                      </span>
                    </div>
                    <div className="h-2 bg-gray-800 rounded-full">
                      <div 
                        className={`h-full rounded-full ${ecosystem.health > 80 ? 'bg-green-500' : ecosystem.health > 60 ? 'bg-yellow-500' : 'bg-red-500'}`}
                        style={{ width: `${ecosystem.health}%` }}
                      />
                    </div>
                  </div>
                  <div className="text-sm text-gray-400">
                    Species Count: <span className="text-cyan-400">{ecosystem.species.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Wildlife Status */}
        <section className="border border-yellow-500 rounded-lg p-6 mb-6 bg-gradient-to-br from-yellow-900/20 to-orange-900/20">
          <h2 className="text-3xl mb-4 text-yellow-400 text-center">🦁 Wildlife Conservation Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-900 border border-red-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400">Endangered Species</div>
              <div className="text-4xl font-bold text-red-400 mb-2">
                {biologicalData.wildlife.endangered.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">Critical conservation needed</div>
            </div>
            <div className="bg-gray-900 border border-green-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400">Protected Areas</div>
              <div className="text-4xl font-bold text-green-400 mb-2">
                {biologicalData.wildlife.protected.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">Species under protection</div>
            </div>
            <div className="bg-gray-900 border border-blue-400 p-4 rounded-lg text-center">
              <div className="text-sm text-gray-400">Migrating Now</div>
              <div className="text-4xl font-bold text-blue-400 mb-2">
                {biologicalData.wildlife.migrating.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">Seasonal migration patterns</div>
            </div>
          </div>
        </section>

        {/* AI Analysis */}
        <section className="border border-purple-500 rounded-lg p-6 bg-gradient-to-br from-purple-900/20 to-pink-900/20">
          <h2 className="text-3xl mb-4 text-purple-400 text-center">🤖 AI Biological Analysis</h2>
          <div className="bg-gray-950 p-6 rounded-lg">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-xl font-bold text-purple-400 mb-3">🎯 Key Insights</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span>Tropical rainforests show highest biodiversity</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                    <span>Coral reefs experiencing stress conditions</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span>Migration patterns within normal range</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                    <span>Endangered species require immediate action</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-xl font-bold text-purple-400 mb-3">📊 Predictions</h3>
                <div className="space-y-2 text-sm">
                  <div>🌡️ Temperature trends: <span className="text-orange-400">Gradual increase</span></div>
                  <div>🌊 Ocean health: <span className="text-yellow-400">Moderate concern</span></div>
                  <div>🌳 Forest coverage: <span className="text-green-400">Stable</span></div>
                  <div>🦋 Species diversity: <span className="text-blue-400">Monitoring required</span></div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}