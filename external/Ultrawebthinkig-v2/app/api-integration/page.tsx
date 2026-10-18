/**
 * UltraWebThinking - API Integration Dashboard
 * Real-time API Status and Data Visualization
 */

'use client';

import React, { useState, useEffect } from 'react';
import { GLOBAL_API_REGISTRY, getAPIsByPriority, getFreeAPIs, getCategories } from '../../lib/global-api-registry';
import { clientAPIService, APIHealthStatus } from '../../lib/client-api-service';

export default function APIIntegrationPage() {
  const [healthStatus, setHealthStatus] = useState<APIHealthStatus[]>([]);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');

  useEffect(() => {
    loadAPIData();
  }, []);

  const loadAPIData = async () => {
    setLoading(true);
    try {
      const [health, dashboard] = await Promise.all([
        clientAPIService.healthCheck(),
        clientAPIService.getDashboardData()
      ]);
      
      setHealthStatus(health);
      setDashboardData(dashboard);
    } catch (error) {
      console.error('Failed to load API data:', error);
    } finally {
      setLoading(false);
    }
  };

  const highPriorityAPIs = getAPIsByPriority('high');
  const freeAPIs = getFreeAPIs();
  const categories = getCategories();

  const filteredAPIs = selectedCategory === 'all' 
    ? GLOBAL_API_REGISTRY 
    : GLOBAL_API_REGISTRY.filter((api: any) => api.category === selectedCategory);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-black text-white p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-cyan-400 mx-auto mb-8"></div>
            <h2 className="text-2xl font-bold mb-4">Loading API Integration Dashboard...</h2>
            <p className="text-cyan-400">Connecting to 500+ APIs...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-black text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            🌐 API Integration Center
          </h1>
          <p className="text-xl text-cyan-400 mb-6">
            500+ Free APIs • Real Data • ASI Enhanced
          </p>
          <div className="flex justify-center space-x-4 mb-8">
            <div className="bg-green-500/20 px-4 py-2 rounded-lg border border-green-500">
              <span className="text-green-400">✅ {freeAPIs.length} Free APIs</span>
            </div>
            <div className="bg-blue-500/20 px-4 py-2 rounded-lg border border-blue-500">
              <span className="text-blue-400">🚀 {highPriorityAPIs.length} High Priority</span>
            </div>
            <div className="bg-purple-500/20 px-4 py-2 rounded-lg border border-purple-500">
              <span className="text-purple-400">📊 {categories.length} Categories</span>
            </div>
          </div>
        </div>

        {/* API Health Status */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold mb-6 text-center">🔥 API Health Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {healthStatus.map((status: APIHealthStatus, index: number) => (
              <div 
                key={index}
                className={`bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border ${
                  status.status === 'healthy' ? 'border-green-500' : 'border-red-500'
                }`}
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold">{status.api}</h3>
                  <div className={`w-4 h-4 rounded-full ${
                    status.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                  }`}></div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Status:</span>
                    <span className={status.status === 'healthy' ? 'text-green-400' : 'text-red-400'}>
                      {status.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Source:</span>
                    <span className="text-cyan-400">{status.source}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Response:</span>
                    <span className="text-yellow-400">{status.duration}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">API Key:</span>
                    <span className={typeof status.hasKey === 'boolean' 
                      ? (status.hasKey ? 'text-green-400' : 'text-red-400') 
                      : 'text-gray-400'
                    }>
                      {typeof status.hasKey === 'boolean' 
                        ? (status.hasKey ? '✅ Yes' : '❌ No') 
                        : 'N/A'
                      }
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Dashboard Data Preview */}
        {dashboardData && (
          <div className="mb-12">
            <h2 className="text-3xl font-bold mb-6 text-center">📊 Live API Data</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              
              {/* Weather Data */}
              {dashboardData.weather?.data && (
                <div className="bg-blue-500/20 backdrop-blur-sm rounded-xl p-6 border border-blue-500">
                  <h3 className="text-xl font-bold mb-4 flex items-center">
                    🌤️ Weather Data
                    <span className="ml-2 text-sm bg-blue-500/30 px-2 py-1 rounded">
                      {dashboardData.weather.source}
                    </span>
                  </h3>
                  <div className="space-y-2">
                    <div>City: {dashboardData.weather.data.name}</div>
                    <div>Temperature: {dashboardData.weather.data.main?.temp}°C</div>
                    <div>Condition: {dashboardData.weather.data.weather?.[0]?.description}</div>
                  </div>
                </div>
              )}

              {/* Crypto Data */}
              {dashboardData.crypto?.data && (
                <div className="bg-yellow-500/20 backdrop-blur-sm rounded-xl p-6 border border-yellow-500">
                  <h3 className="text-xl font-bold mb-4 flex items-center">
                    ₿ Crypto Data
                    <span className="ml-2 text-sm bg-yellow-500/30 px-2 py-1 rounded">
                      {dashboardData.crypto.source}
                    </span>
                  </h3>
                  <div className="space-y-2">
                    {dashboardData.crypto.data.bitcoin && (
                      <div>Bitcoin: ${dashboardData.crypto.data.bitcoin.usd?.toLocaleString()}</div>
                    )}
                    {dashboardData.crypto.data.ethereum && (
                      <div>Ethereum: ${dashboardData.crypto.data.ethereum.usd?.toLocaleString()}</div>
                    )}
                  </div>
                </div>
              )}

              {/* NASA Data */}
              {dashboardData.nasa?.data && (
                <div className="bg-purple-500/20 backdrop-blur-sm rounded-xl p-6 border border-purple-500">
                  <h3 className="text-xl font-bold mb-4 flex items-center">
                    🚀 NASA Data
                    <span className="ml-2 text-sm bg-purple-500/30 px-2 py-1 rounded">
                      {dashboardData.nasa.source}
                    </span>
                  </h3>
                  <div className="space-y-2">
                    <div className="text-sm">{dashboardData.nasa.data.title}</div>
                    <div className="text-xs text-gray-400">{dashboardData.nasa.data.date}</div>
                  </div>
                </div>
              )}

            </div>
          </div>
        )}

        {/* API Registry */}
        <div className="mb-12">
          <h2 className="text-3xl font-bold mb-6 text-center">📚 API Registry</h2>
          
          {/* Category Filter */}
          <div className="flex flex-wrap justify-center gap-2 mb-8">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-4 py-2 rounded-lg border transition-all ${
                selectedCategory === 'all'
                  ? 'bg-cyan-500/30 border-cyan-500 text-cyan-400'
                  : 'bg-gray-800/50 border-gray-600 text-gray-400 hover:border-cyan-500'
              }`}
            >
              All APIs ({GLOBAL_API_REGISTRY.length})
            </button>
            {categories.map((category: string) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg border transition-all ${
                  selectedCategory === category
                    ? 'bg-cyan-500/30 border-cyan-500 text-cyan-400'
                    : 'bg-gray-800/50 border-gray-600 text-gray-400 hover:border-cyan-500'
                }`}
              >
                {category}
              </button>
            ))}
          </div>

          {/* API Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAPIs.map((api: any, index: number) => (
              <div key={api.id} className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-600 hover:border-cyan-500 transition-all">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold">{api.name}</h3>
                  <div className="flex space-x-2">
                    {!api.keyRequired && (
                      <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs border border-green-500">
                        FREE
                      </span>
                    )}
                    <span className={`px-2 py-1 rounded text-xs border ${
                      api.priority === 'high' ? 'bg-red-500/20 text-red-400 border-red-500' :
                      api.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500' :
                      'bg-gray-500/20 text-gray-400 border-gray-500'
                    }`}>
                      {api.priority.toUpperCase()}
                    </span>
                  </div>
                </div>
                
                <div className="space-y-2 text-sm mb-4">
                  <div className="text-gray-400">{api.description}</div>
                  <div className="text-cyan-400">{api.category}</div>
                  {api.rateLimit && (
                    <div className="text-yellow-400">Rate: {api.rateLimit}</div>
                  )}
                </div>

                <div className="flex space-x-2">
                  <a
                    href={api.documentation}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-1 bg-blue-500/20 text-blue-400 px-3 py-2 rounded border border-blue-500 hover:bg-blue-500/30 transition-all text-center text-sm"
                  >
                    📖 Docs
                  </a>
                  <button 
                    onClick={() => window.open(api.url, '_blank')}
                    className="flex-1 bg-purple-500/20 text-purple-400 px-3 py-2 rounded border border-purple-500 hover:bg-purple-500/30 transition-all text-center text-sm"
                  >
                    🔗 API
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="text-center">
          <button
            onClick={loadAPIData}
            className="bg-gradient-to-r from-cyan-500 to-purple-500 px-8 py-4 rounded-xl font-bold text-xl hover:shadow-lg hover:shadow-cyan-500/25 transition-all"
          >
            🔄 Refresh API Data
          </button>
        </div>
      </div>
    </div>
  );
}
