"use client";

import { useEffect, useState } from 'react';

interface RealData {
  stripe: Array<{
    id: string;
    amount: number;
    currency: string;
    status: string;
    created: number;
  }>;
  db: {
    totalUsers: number;
    totalSales7d: number;
    revenueCents7d: number;
  };
  weather: {
    name?: string;
    main?: { temp: number };
    weather?: Array<{ description: string }>;
    error?: string;
  };
  crypto: {
    bitcoin?: { eur: number; usd: number };
    ethereum?: { eur: number; usd: number };
  };
  lastUpdated: string;
}

interface ASIMainContentProps {
  activeView?: string;
  systemStatus?: any;
}

export function ASIMainContent({ activeView, systemStatus }: ASIMainContentProps) {
  const [data, setData] = useState<RealData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const loadRealData = async () => {
    try {
      const response = await fetch('/api/aggregate');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const realData = await response.json();
      setData(realData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRealData();
    // Refresh every 30 seconds
    const interval = setInterval(loadRealData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-white min-h-screen p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-pulse text-2xl font-bold text-gray-900 mb-2">🚀 Loading Real Data...</div>
          <p className="text-gray-600">Connecting to live APIs</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white min-h-screen p-6 flex items-center justify-center">
        <div className="text-center text-red-600">
          <div className="text-xl font-bold mb-2">⚠️ API Error</div>
          <p>{error}</p>
          <button 
            onClick={loadRealData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white min-h-screen p-6">
      {/* Real Data Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🔴 ASI Real Dashboard</h1>
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <span>Status: <span className="text-green-600 font-medium">LIVE DATA</span></span>
          <span>•</span>
          <span>Last updated: {data ? new Date(data.lastUpdated).toLocaleTimeString() : '--'}</span>
          <span>•</span>
          <span className="text-blue-600">No more fake data!</span>
        </div>
      </div>

      {/* Revenue & Payments Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        
        {/* Stripe Payments */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">💳 Real Payments (Stripe)</h2>
          {data?.stripe && data.stripe.length > 0 ? (
            <div className="space-y-3">
              {data.stripe.slice(0, 5).map((payment) => (
                <div key={payment.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                  <div>
                    <div className="font-medium text-gray-900">€{(payment.amount / 100).toFixed(2)}</div>
                    <div className="text-xs text-gray-500">{payment.id}</div>
                  </div>
                  <div className="text-right">
                    <div className={`text-xs px-2 py-1 rounded ${ 
                      payment.status === 'succeeded' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {payment.status}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {new Date(payment.created * 1000).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500">No recent payments</p>
          )}
        </div>

        {/* Database Stats */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">📊 Database Stats</h2>
          <div className="space-y-4">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Users</span>
              <span className="font-bold text-2xl text-blue-600">{data?.db.totalUsers || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Sales (7 days)</span>
              <span className="font-bold text-2xl text-green-600">{data?.db.totalSales7d || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Revenue (7 days)</span>
              <span className="font-bold text-2xl text-green-600">
                €{data?.db.revenueCents7d ? (data.db.revenueCents7d / 100).toFixed(2) : '0.00'}
              </span>
            </div>
          </div>
        </div>

      </div>

      {/* Weather & Crypto Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        
        {/* Weather */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">🌤️ Live Weather</h2>
          {data?.weather?.error ? (
            <div className="text-orange-600">
              API Key needed: {data.weather.error}
            </div>
          ) : data?.weather?.name ? (
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {data.weather.main?.temp}°C
              </div>
              <div className="text-gray-600">{data.weather.name}</div>
              <div className="text-sm text-gray-500 capitalize">
                {data.weather.weather?.[0]?.description}
              </div>
            </div>
          ) : (
            <div className="text-gray-500">Loading weather...</div>
          )}
        </div>

        {/* Crypto */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">₿ Live Crypto Prices</h2>
          <div className="space-y-3">
            {data?.crypto?.bitcoin && (
              <div className="flex justify-between">
                <span className="text-gray-600">Bitcoin</span>
                <div className="text-right">
                  <div className="font-bold text-orange-600">€{data.crypto.bitcoin.eur.toLocaleString()}</div>
                  <div className="text-xs text-gray-500">${data.crypto.bitcoin.usd.toLocaleString()}</div>
                </div>
              </div>
            )}
            {data?.crypto?.ethereum && (
              <div className="flex justify-between">
                <span className="text-gray-600">Ethereum</span>
                <div className="text-right">
                  <div className="font-bold text-blue-600">€{data.crypto.ethereum.eur.toLocaleString()}</div>
                  <div className="text-xs text-gray-500">${data.crypto.ethereum.usd.toLocaleString()}</div>
                </div>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Actions Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center hover:bg-blue-100 cursor-pointer transition-colors">
          <div className="text-2xl mb-2">💳</div>
          <h3 className="font-medium text-gray-900">Payments</h3>
          <p className="text-sm text-gray-600">Stripe Integration</p>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center hover:bg-green-100 cursor-pointer transition-colors">
          <div className="text-2xl mb-2">📊</div>
          <h3 className="font-medium text-gray-900">Analytics</h3>
          <p className="text-sm text-gray-600">Real Metrics</p>
        </div>

        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center hover:bg-purple-100 cursor-pointer transition-colors">
          <div className="text-2xl mb-2">🔐</div>
          <h3 className="font-medium text-gray-900">Authentication</h3>
          <p className="text-sm text-gray-600">JWT Security</p>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 text-center hover:bg-orange-100 cursor-pointer transition-colors">
          <div className="text-2xl mb-2">🏭</div>
          <h3 className="font-medium text-gray-900">Products</h3>
          <p className="text-sm text-gray-600">Real Business</p>
        </div>

      </div>

      {/* API Status Footer */}
      <div className="mt-8 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <span className="text-gray-700">APIs Connected</span>
          </div>
          <div className="text-gray-500">
            Next refresh in 30s
          </div>
        </div>
      </div>

    </div>
  );
}
