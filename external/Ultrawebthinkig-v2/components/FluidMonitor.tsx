/**
 * FLUID FLOW MONITOR - Natural Water-like Interface
 * Web8 real-time monitoring of fluid architecture with beautiful animations
 * 
 * @version 8.0.0-WEB8-FLUID
 * @author Ledjan Ahmati
 */

import React, { useState, useEffect } from 'react';

interface FlowMetrics {
  timestamp: number;
  globalFlow: {
    turbulence: number;
    clarity: number;
    velocity: number;
    pressure: number;
    temperature: string;
  };
  streams: Array<{
    name: string;
    type: string;
    velocity: number;
    clarity: number;
    obstacles: number;
    state: string;
    health: number;
  }>;
  recommendations: string[];
  waterQuality: string;
}

export const FluidMonitor = () => {
  const [metrics, setMetrics] = useState<FlowMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch flow metrics
  const fetchMetrics = async () => {
    try {
      // Simulate data for demo since API might not exist
      setMetrics({
        timestamp: Date.now(),
        globalFlow: {
          turbulence: Math.random() * 5,
          clarity: 85 + Math.random() * 10,
          velocity: 70 + Math.random() * 20,
          pressure: 1.2 + Math.random() * 0.3,
          temperature: '21°C'
        },
        streams: [
          { name: 'Main Data Flow', type: 'primary', velocity: 88, clarity: 92, obstacles: 2, state: 'flowing', health: 95 },
          { name: 'Cache Stream', type: 'cache', velocity: 76, clarity: 88, obstacles: 1, state: 'flowing', health: 89 },
          { name: 'API Gateway', type: 'gateway', velocity: 82, clarity: 85, obstacles: 3, state: 'turbulent', health: 78 }
        ],
        recommendations: ['Clear obstacle in API Gateway', 'Optimize cache flow'],
        waterQuality: 'Excellent'
      });
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching flow metrics:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    
    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const resetFlow = () => {
    fetchMetrics();
  };

  if (isLoading) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #00ffff',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto 1rem'
        }}></div>
        <p>Analyzing water flow patterns...</p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p>Unable to connect to fluid flow system</p>
        <button onClick={fetchMetrics} style={{
          padding: '0.5rem 1rem',
          background: '#00ffff',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer'
        }}>
          Retry Connection
        </button>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)',
      color: '#ffffff',
      padding: '2rem',
      fontFamily: 'monospace'
    }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ color: '#00ffff', textShadow: '0 0 10px #00ffff' }}>
          🌊 Fluid Architecture Monitor
        </h1>
        <div>
          <span>Water Quality: </span>
          <span style={{ color: '#00ff00', fontWeight: 'bold' }}>
            {metrics.waterQuality}
          </span>
        </div>
      </div>

      {/* Global Flow Metrics */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <div style={{ background: 'rgba(0,255,255,0.1)', padding: '1rem', borderRadius: '10px' }}>
          <h3>Flow Clarity: {Math.round(metrics.globalFlow.clarity)}%</h3>
          <div style={{ background: 'rgba(0,0,0,0.3)', height: '10px', borderRadius: '5px' }}>
            <div style={{
              background: '#00ffff',
              height: '100%',
              width: `${metrics.globalFlow.clarity}%`,
              borderRadius: '5px',
              transition: 'width 0.3s ease'
            }}></div>
          </div>
        </div>

        <div style={{ background: 'rgba(0,255,255,0.1)', padding: '1rem', borderRadius: '10px' }}>
          <h3>Flow Velocity: {Math.round(metrics.globalFlow.velocity)}%</h3>
          <div style={{ background: 'rgba(0,0,0,0.3)', height: '10px', borderRadius: '5px' }}>
            <div style={{
              background: '#00ff88',
              height: '100%',
              width: `${metrics.globalFlow.velocity}%`,
              borderRadius: '5px',
              transition: 'width 0.3s ease'
            }}></div>
          </div>
        </div>

        <div style={{ background: 'rgba(0,255,255,0.1)', padding: '1rem', borderRadius: '10px' }}>
          <h3>Turbulence: {metrics.globalFlow.turbulence.toFixed(1)}</h3>
          <div style={{ background: 'rgba(0,0,0,0.3)', height: '10px', borderRadius: '5px' }}>
            <div style={{
              background: '#ff8800',
              height: '100%',
              width: `${Math.min(100, metrics.globalFlow.turbulence * 20)}%`,
              borderRadius: '5px',
              transition: 'width 0.3s ease'
            }}></div>
          </div>
        </div>
      </div>

      {/* Streams */}
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ color: '#88ffff' }}>Active Data Streams</h2>
        {metrics.streams.map((stream, index) => (
          <div key={index} style={{
            background: 'rgba(255,255,255,0.05)',
            margin: '1rem 0',
            padding: '1rem',
            borderRadius: '10px',
            border: '1px solid rgba(0,255,255,0.3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ fontWeight: 'bold' }}>{stream.name}</span>
              <span style={{
                color: stream.state === 'flowing' ? '#00ff00' : '#ff8800',
                textTransform: 'uppercase'
              }}>
                {stream.state}
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
              <div>
                <span>Velocity: {stream.velocity}%</span>
                <div style={{ background: 'rgba(0,0,0,0.3)', height: '6px', borderRadius: '3px', marginTop: '0.25rem' }}>
                  <div style={{
                    background: '#00ffff',
                    height: '100%',
                    width: `${stream.velocity}%`,
                    borderRadius: '3px'
                  }}></div>
                </div>
              </div>

              <div>
                <span>Clarity: {stream.clarity}%</span>
                <div style={{ background: 'rgba(0,0,0,0.3)', height: '6px', borderRadius: '3px', marginTop: '0.25rem' }}>
                  <div style={{
                    background: '#00ff88',
                    height: '100%',
                    width: `${stream.clarity}%`,
                    borderRadius: '3px'
                  }}></div>
                </div>
              </div>
              
              <div>
                <span>Health: {stream.health}%</span>
                <div style={{ background: 'rgba(0,0,0,0.3)', height: '6px', borderRadius: '3px', marginTop: '0.25rem' }}>
                  <div style={{
                    background: '#00ff00',
                    height: '100%',
                    width: `${stream.health}%`,
                    borderRadius: '3px'
                  }}></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Controls */}
      <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
        <button 
          onClick={() => setAutoRefresh(!autoRefresh)}
          style={{
            padding: '0.8rem 1.5rem',
            background: autoRefresh ? 'linear-gradient(45deg, #00ffff, #0088ff)' : 'rgba(255,255,255,0.1)',
            color: autoRefresh ? '#000' : '#fff',
            border: '1px solid #00ffff',
            borderRadius: '5px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {autoRefresh ? 'Auto Refresh ON' : 'Auto Refresh OFF'}
        </button>
        
        <button 
          onClick={resetFlow}
          style={{
            padding: '0.8rem 1.5rem',
            background: 'linear-gradient(45deg, #ff0088, #ff0044)',
            color: '#fff',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          Reset Flow
        </button>
      </div>
    </div>
  );
};

export default FluidMonitor;