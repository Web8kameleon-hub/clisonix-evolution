/**
 * ASI Real Data Dashboard - Statistical Integration
 * Live dashboard with real statistical data
 */

'use client';

import React, { useState, useEffect } from 'react';
import { StatisticalDataService, EconomicIndicators, StatisticalDataPoint } from '../../lib/dataIntegration/StatisticalDataService';

export function ASIRealDataDashboard() {
  const [albanianData, setAlbanianData] = useState<EconomicIndicators | null>(null);
  const [marketData, setMarketData] = useState<StatisticalDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const [error, setError] = useState<string | null>(null);

  const statsService = StatisticalDataService.getInstance();

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch Albanian economic data and market data in parallel
        const [albData, markets] = await Promise.all([
          statsService.getAlbanianEconomicData(),
          statsService.getLiveMarketData()
        ]);

        setAlbanianData(albData);
        setMarketData(markets);
        setLastUpdate(new Date().toLocaleString());
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data');
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Auto-refresh every 15 minutes
    const interval = setInterval(fetchData, 15 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  const formatValue = (value: number, unit: string): string => {
    if (unit.includes('billions')) {
      return `$${(value / 1e9).toFixed(1)}B`;
    }
    if (unit === '%') {
      return `${value.toFixed(2)}%`;
    }
    if (unit.includes('USD')) {
      return `$${value.toLocaleString()}`;
    }
    return `${value.toLocaleString()} ${unit}`;
  };

  if (loading) {
    return (
      <div className="real-data-dashboard loading">
        <div className="loading-spinner">🔄</div>
        <p>Loading real statistical data...</p>
        <style jsx>{`
          .loading {
            text-align: center;
            padding: 2rem;
            color: #64748b;
          }
          .loading-spinner {
            font-size: 2rem;
            animation: spin 2s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  if (error) {
    return (
      <div className="real-data-dashboard error">
        <div className="error-icon">⚠️</div>
        <h3>Data Fetch Error</h3>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          🔄 Retry
        </button>
        <style jsx>{`
          .error {
            text-align: center;
            padding: 2rem;
            background: #fee2e2;
            border-radius: 0.5rem;
            color: #dc2626;
          }
          .error-icon { font-size: 2rem; margin-bottom: 1rem; }
          button {
            background: #dc2626;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            cursor: pointer;
            margin-top: 1rem;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="real-data-dashboard">
      <div className="dashboard-header">
        <h2>🇦🇱 ASI Real Data Intelligence</h2>
        <p>Live statistical data integration • Last update: {lastUpdate}</p>
      </div>

      {/* Albanian Economic Data */}
      {albanianData && (
        <div className="data-section">
          <h3>🏛️ Albania Economic Indicators</h3>
          <div className="data-grid">
            <div className="data-card gdp">
              <div className="data-icon">💰</div>
              <div className="data-content">
                <h4>GDP</h4>
                <div className="data-value">
                  {formatValue(albanianData.gdp.value, albanianData.gdp.unit)}
                </div>
                <div className="data-source">{albanianData.gdp.date}</div>
              </div>
            </div>
            
            <div className="data-card inflation">
              <div className="data-icon">📈</div>
              <div className="data-content">
                <h4>Inflation Rate</h4>
                <div className="data-value">
                  {formatValue(albanianData.inflation.value, albanianData.inflation.unit)}
                </div>
                <div className="data-source">{albanianData.inflation.date}</div>
              </div>
            </div>

            <div className="data-card unemployment">
              <div className="data-icon">👥</div>
              <div className="data-content">
                <h4>Unemployment</h4>
                <div className="data-value">
                  {formatValue(albanianData.unemployment.value, albanianData.unemployment.unit)}
                </div>
                <div className="data-source">{albanianData.unemployment.date}</div>
              </div>
            </div>

            <div className="data-card population">
              <div className="data-icon">🏙️</div>
              <div className="data-content">
                <h4>Population</h4>
                <div className="data-value">
                  {(albanianData.population.value / 1e6).toFixed(2)}M
                </div>
                <div className="data-source">{albanianData.population.date}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Live Market Data */}
      {marketData.length > 0 && (
        <div className="data-section">
          <h3>📊 Live Financial Markets</h3>
          <div className="market-grid">
            {marketData.map((item, index) => (
              <div key={index} className="market-card">
                <div className="market-symbol">{item.indicator}</div>
                <div className="market-value">
                  {formatValue(item.value, item.unit)}
                </div>
                <div className="market-source">{item.source}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ASI Integration Status */}
      <div className="asi-status">
        <h4>🧠 ASI Data Integration Status</h4>
        <div className="status-indicators">
          <div className="status-item active">
            <span className="status-dot"></span>
            World Bank API: Connected
          </div>
          <div className="status-item active">
            <span className="status-dot"></span>
            Yahoo Finance: Live
          </div>
          <div className="status-item">
            <span className="status-dot inactive"></span>
            FRED API: Demo Mode
          </div>
        </div>
      </div>

      <style jsx>{`
        .real-data-dashboard {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }
        
        .dashboard-header {
          text-align: center;
          margin-bottom: 2rem;
        }
        
        .dashboard-header h2 {
          color: #1e40af;
          margin-bottom: 0.5rem;
        }
        
        .dashboard-header p {
          color: #64748b;
          font-size: 0.875rem;
        }
        
        .data-section {
          margin-bottom: 2rem;
        }
        
        .data-section h3 {
          color: #1e293b;
          margin-bottom: 1rem;
        }
        
        .data-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1rem;
        }
        
        .data-card {
          background: white;
          border-radius: 0.75rem;
          padding: 1.5rem;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          border-left: 4px solid #3b82f6;
          display: flex;
          align-items: center;
          gap: 1rem;
        }
        
        .data-card.gdp { border-left-color: #10b981; }
        .data-card.inflation { border-left-color: #f59e0b; }
        .data-card.unemployment { border-left-color: #ef4444; }
        .data-card.population { border-left-color: #8b5cf6; }
        
        .data-icon {
          font-size: 2rem;
          opacity: 0.8;
        }
        
        .data-content h4 {
          margin: 0 0 0.5rem 0;
          color: #374151;
          font-size: 0.875rem;
          font-weight: 600;
        }
        
        .data-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 0.25rem;
        }
        
        .data-source {
          font-size: 0.75rem;
          color: #9ca3af;
        }
        
        .market-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }
        
        .market-card {
          background: linear-gradient(135deg, #f8fafc, #e2e8f0);
          border-radius: 0.5rem;
          padding: 1rem;
          text-align: center;
        }
        
        .market-symbol {
          font-weight: 700;
          color: #1e40af;
          margin-bottom: 0.5rem;
        }
        
        .market-value {
          font-size: 1.25rem;
          font-weight: 600;
          color: #1e293b;
          margin-bottom: 0.25rem;
        }
        
        .market-source {
          font-size: 0.75rem;
          color: #64748b;
        }
        
        .asi-status {
          background: #f1f5f9;
          border-radius: 0.5rem;
          padding: 1rem;
          margin-top: 2rem;
        }
        
        .asi-status h4 {
          color: #1e293b;
          margin-bottom: 1rem;
        }
        
        .status-indicators {
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
        }
        
        .status-item {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;
        }
        
        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: #10b981;
        }
        
        .status-dot.inactive {
          background: #94a3b8;
        }
        
        .status-item.active {
          color: #059669;
        }
      `}</style>
    </div>
  );
}
