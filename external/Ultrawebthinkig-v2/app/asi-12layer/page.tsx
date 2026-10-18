'use client'

/**
 * ASI 12-Layer Dashboard - REAL DATA ONLY Interface
 * Vetëm të dhëna reale nga browser APIs dhe sistema
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0 Web8
 * @date 13 Tetor 2025
 */

import { useState, useEffect } from 'react';
import { 
  initializeASI12LayerSystem, 
  processRealASIRequest, 
  getRealASIStatus,
  startRealPerformanceMonitor,
  type ASI12Layer,
  type ASI12SystemContext 
} from '../../lib/ASI12LayerSystem';
import { ASIDemo } from '../../components/asi/ASIDemo';

export default function ASI12LayerDashboard() {
  const [asiSystem, setAsiSystem] = useState<ASI12SystemContext | null>(null);
  const [input, setInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [response, setResponse] = useState<string>('');
  const [processingMetrics, setProcessingMetrics] = useState<any>(null);
  const [realTimeStats, setRealTimeStats] = useState<any>(null);
  const [language, setLanguage] = useState<'sq' | 'en' | 'auto'>('auto');

  // Initialize ASI System with real data
  useEffect(() => {
    console.log('🚀 Initializing ASI 12-Layer System...');
    
    const system = initializeASI12LayerSystem();
    setAsiSystem(system);
    
    // Start real-time monitoring
    const stopMonitoring = startRealPerformanceMonitor(3000);
    
    // Update stats every 3 seconds with real data
    const statsInterval = setInterval(() => {
      const currentStatus = getRealASIStatus();
      setAsiSystem(currentStatus);
      
      // Real browser stats
      const memInfo = (performance as any).memory;
      setRealTimeStats({
        currentTime: new Date().toLocaleString('sq-AL'),
        memoryUsed: memInfo ? Math.round(memInfo.usedJSHeapSize / 1024 / 1024) : 0,
        memoryTotal: memInfo ? Math.round(memInfo.totalJSHeapSize / 1024 / 1024) : 0,
        onlineStatus: navigator.onLine ? 'Online' : 'Offline',
        browserLang: navigator.language,
        platform: navigator.platform,
        userAgent: navigator.userAgent.substring(0, 50) + '...'
      });
    }, 3000);
    
    return () => {
      stopMonitoring();
      clearInterval(statsInterval);
    };
  }, []);

  // Process ASI request with real data
  const handleProcessRequest = async () => {
    if (!input.trim() || !asiSystem) return;
    
    setIsProcessing(true);
    setResponse('');
    setProcessingMetrics(null);
    
    try {
      const startTime = Date.now();
      
      const result = await processRealASIRequest(input, language);
      
      const endTime = Date.now();
      const totalTime = endTime - startTime;
      
      setResponse(result.response);
      setProcessingMetrics({
        ...result,
        totalRealTime: totalTime,
        timestamp: new Date().toLocaleString('sq-AL')
      });
      
      // Update system status after processing
      const updatedStatus = getRealASIStatus();
      setAsiSystem(updatedStatus);
      
    } catch (error) {
      console.error('ASI Processing Error:', error);
      setResponse(`Gabim në procesim: ${error}`);
    } finally {
      setIsProcessing(false);
    }
  };

  if (!asiSystem) {
    return (
      <div style={{ 
        padding: '2rem', 
        textAlign: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #1e293b, #334155)',
        color: 'white'
      }}>
        <h2>🇦🇱 ASI 12-Layer System - Duke u ngarkuar...</h2>
        <p>Duke inicializuar sistemin me të dhëna reale...</p>
      </div>
    );
  }

  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1e293b, #334155)',
      color: 'white',
      padding: '1rem',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <div style={{ 
        textAlign: 'center', 
        marginBottom: '2rem',
        borderBottom: '2px solid #3b82f6',
        paddingBottom: '1rem'
      }}>
        <h1 style={{ 
          fontSize: '2.5rem', 
          margin: '0 0 0.5rem 0',
          color: '#60a5fa'
        }}>
          🇦🇱 ASI 12-Layer System
        </h1>
        <p style={{ 
          fontSize: '1.1rem', 
          color: '#cbd5e1',
          margin: 0
        }}>
          Albanian System Intelligence - REAL DATA ONLY
        </p>
      </div>

      {/* Real-Time Stats */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        <div style={{ 
          background: 'rgba(59, 130, 246, 0.1)', 
          padding: '1rem', 
          borderRadius: '8px',
          border: '1px solid rgba(59, 130, 246, 0.3)'
        }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#60a5fa' }}>📊 System Health</h3>
          <p>Memory: {asiSystem.systemHealth.totalMemoryMB} MB</p>
          <p>Uptime: {asiSystem.systemHealth.uptimeSeconds}s</p>
          <p>Language: {asiSystem.systemHealth.activeLanguage.toUpperCase()}</p>
          <p>Response: {asiSystem.systemHealth.responseTimeMs}ms</p>
        </div>

        <div style={{ 
          background: 'rgba(16, 185, 129, 0.1)', 
          padding: '1rem', 
          borderRadius: '8px',
          border: '1px solid rgba(16, 185, 129, 0.3)'
        }}>
          <h3 style={{ margin: '0 0 0.5rem 0', color: '#10b981' }}>📈 Analytics</h3>
          <p>Sessions: {asiSystem.realAnalytics.sessionsToday}</p>
          <p>Requests: {asiSystem.realAnalytics.requestsProcessed}</p>
          <p>Error Rate: {asiSystem.realAnalytics.errorRate.toFixed(2)}%</p>
          <p>Queue: {asiSystem.systemHealth.processingQueue}</p>
        </div>

        {realTimeStats && (
          <div style={{ 
            background: 'rgba(245, 158, 11, 0.1)', 
            padding: '1rem', 
            borderRadius: '8px',
            border: '1px solid rgba(245, 158, 11, 0.3)'
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#f59e0b' }}>🌐 Browser Real Data</h3>
            <p>Memory: {realTimeStats.memoryUsed}/{realTimeStats.memoryTotal} MB</p>
            <p>Status: {realTimeStats.onlineStatus}</p>
            <p>Platform: {realTimeStats.platform}</p>
            <p>Time: {realTimeStats.currentTime}</p>
          </div>
        )}
      </div>

      {/* Layer Status Grid */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1rem',
        marginBottom: '2rem'
      }}>
        {Array.from(asiSystem.layers.entries()).map(([id, layer]) => (
          <div key={id} style={{ 
            background: layer.status === 'active' ? 
              'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)', 
            padding: '1rem', 
            borderRadius: '8px',
            border: `1px solid ${layer.status === 'active' ? 
              'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
          }}>
            <h4 style={{ 
              margin: '0 0 0.5rem 0', 
              color: layer.status === 'active' ? '#10b981' : '#ef4444'
            }}>
              {layer.name}
            </h4>
            <p><strong>Status:</strong> {layer.status}</p>
            <p><strong>Type:</strong> {layer.moduleType}</p>
            <p><strong>Memory:</strong> {layer.realMetrics.memoryUsage} MB</p>
            <p><strong>CPU:</strong> {layer.realMetrics.cpuLoad}%</p>
            <p><strong>Accuracy:</strong> {layer.realMetrics.accuracy}%</p>
            <p><strong>Connections:</strong> {layer.realMetrics.activeConnections}</p>
            <p style={{ 
              fontSize: '0.8rem', 
              color: '#9ca3af',
              margin: '0.5rem 0 0 0'
            }}>
              Updated: {new Date(layer.realTimestamp).toLocaleTimeString('sq-AL')}
            </p>
          </div>
        ))}
      </div>

      {/* ASI Input Interface */}
      <div style={{ 
        background: 'rgba(55, 65, 81, 0.8)', 
        padding: '2rem', 
        borderRadius: '12px',
        border: '1px solid rgba(75, 85, 99, 0.5)'
      }}>
        <h3 style={{ 
          margin: '0 0 1rem 0', 
          color: '#60a5fa',
          textAlign: 'center'
        }}>
          🧠 ASI Intelligent Processing
        </h3>
        
        {/* Language Selector */}
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="language-select" style={{ display: 'block', marginBottom: '0.5rem', color: '#cbd5e1' }}>
            Gjuha / Language:
          </label>
          <select
            id="language-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value as 'sq' | 'en' | 'auto')}
            className="p-2 rounded-md border border-gray-600 bg-gray-700 text-white w-52"
          >
            <option value="auto">🔄 Auto Detection</option>
            <option value="sq">🇦🇱 Shqip</option>
            <option value="en">🇬🇧 English</option>
          </select>
        </div>
        
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Shkruani pyetjen tuaj këtu... / Write your question here..."
          style={{ 
            width: '100%',
            minHeight: '120px',
            padding: '1rem',
            borderRadius: '8px',
            border: '1px solid #4b5563',
            background: '#374151',
            color: 'white',
            fontSize: '1rem',
            resize: 'vertical',
            marginBottom: '1rem'
          }}
        />
        
        <button
          onClick={handleProcessRequest}
          disabled={!input.trim() || isProcessing}
          style={{ 
            padding: '0.75rem 2rem',
            borderRadius: '8px',
            border: 'none',
            background: isProcessing ? '#6b7280' : '#3b82f6',
            color: 'white',
            fontSize: '1rem',
            cursor: isProcessing ? 'not-allowed' : 'pointer',
            display: 'block',
            margin: '0 auto'
          }}
        >
          {isProcessing ? '⏳ Duke procesuar...' : '🚀 Procezo me ASI'}
        </button>
      </div>

      {/* Response Section */}
      {(response || processingMetrics) && (
        <div style={{ 
          marginTop: '2rem',
          background: 'rgba(55, 65, 81, 0.8)', 
          padding: '2rem', 
          borderRadius: '12px',
          border: '1px solid rgba(75, 85, 99, 0.5)'
        }}>
          <h3 style={{ 
            margin: '0 0 1rem 0', 
            color: '#10b981' 
          }}>
            ✅ ASI Response - Real Data
          </h3>
          
          {response && (
            <div style={{ 
              background: 'rgba(16, 185, 129, 0.1)', 
              padding: '1rem',
              borderRadius: '8px',
              border: '1px solid rgba(16, 185, 129, 0.3)',
              marginBottom: '1rem'
            }}>
              <p style={{ 
                fontSize: '1.1rem',
                lineHeight: '1.6',
                margin: 0
              }}>
                {response}
              </p>
            </div>
          )}
          
          {processingMetrics && (
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '1rem'
            }}>
              <div style={{ 
                background: 'rgba(59, 130, 246, 0.1)', 
                padding: '1rem',
                borderRadius: '8px'
              }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#60a5fa' }}>⏱️ Timing</h4>
                <p>Processing: {processingMetrics.processingTime}ms</p>
                <p>Total Time: {processingMetrics.totalRealTime}ms</p>
                <p>Timestamp: {processingMetrics.timestamp}</p>
              </div>
              
              <div style={{ 
                background: 'rgba(139, 92, 246, 0.1)', 
                padding: '1rem',
                borderRadius: '8px'
              }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#8b5cf6' }}>🧠 Layers</h4>
                <p>Used: {processingMetrics.layersUsed.join(', ')}</p>
                <p>Count: {processingMetrics.layersUsed.length}/12</p>
              </div>
              
              <div style={{ 
                background: 'rgba(245, 158, 11, 0.1)', 
                padding: '1rem',
                borderRadius: '8px'
              }}>
                <h4 style={{ margin: '0 0 0.5rem 0', color: '#f59e0b' }}>📊 Real Metrics</h4>
                <p>Memory: {processingMetrics.realMetrics.memoryBefore} → {processingMetrics.realMetrics.memoryAfter} MB</p>
                <p>CPU Load: {processingMetrics.realMetrics.cpuLoad}%</p>
                <p>Accuracy: {processingMetrics.realMetrics.accuracy}%</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ASI Interactive Demo Section */}
      <div style={{ 
        marginTop: '3rem',
        padding: '2rem',
        background: 'rgba(59, 130, 246, 0.05)',
        border: '1px solid rgba(59, 130, 246, 0.2)',
        borderRadius: '1rem'
      }}>
        <h2 style={{ 
          color: '#3b82f6', 
          marginBottom: '1rem',
          textAlign: 'center'
        }}>
          🎯 Live ASI Demo - Test Albanian Intelligence
        </h2>
        <ASIDemo />
      </div>

      {/* Footer */}
      <div style={{ 
        textAlign: 'center', 
        marginTop: '2rem',
        padding: '1rem',
        borderTop: '1px solid #4b5563',
        color: '#9ca3af',
        fontSize: '0.9rem'
      }}>
        <p>
          🇦🇱 ASI 12-Layer System - Albanian System Intelligence<br/>
          100% Real Data • No Fake Values • Created by Ledjan Ahmati<br/>
          Web8 Platform • Version 8.0.0 • {new Date().toLocaleDateString('sq-AL')}
        </p>
      </div>
    </div>
  );
}
