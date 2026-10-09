import React, { useState, useEffect } from 'react';
import './AbiAlbaIntegration.css';

interface NetworkStats {
  health_score: number;
  status: string;
  online_percentage: number;
  avg_latency: number;
  monitoring_time_minutes: number;
  recommendations: string[];
}

interface NetworkStatus {
  status: string;
  health_score: number;
  summary: {
    total_hosts: number;
    online_hosts: number;
    offline_hosts: number;
    avg_latency: number;
    monitoring_time: number;
    last_update: string;
  };
  top_performers: Array<{
    host: string;
    avg_latency: number;
    status: string;
    packet_loss: number;
  }>;
}

const AbiAlbaIntegration: React.FC = () => {
  const [selectedPerson, setSelectedPerson] = useState<'albi' | 'jona' | 'harmony'>('albi');
  const [networkStats, setNetworkStats] = useState<NetworkStats | null>(null);
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [loading, setLoading] = useState(false);

  const API_BASE = 'http://localhost:8000';

  // Fetch network health
  const fetchNetworkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/alba/network/health`);
      if (response.ok) {
        const data = await response.json();
        setNetworkStats(data);
      }
    } catch (error) {
      console.error('Gabim në marrjen e network health:', error);
    }
  };

  // Fetch network status
  const fetchNetworkStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/alba/network/status`);
      if (response.ok) {
        const data = await response.json();
        setNetworkStatus(data);
        setIsMonitoring(data.status === 'monitoring_active');
      }
    } catch (error) {
      console.error('Gabim në marrjen e network status:', error);
    }
  };

  // Start monitoring
  const startMonitoring = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/alba/network/start`, {
        method: 'POST'
      });
      if (response.ok) {
        setIsMonitoring(true);
        await fetchNetworkStatus();
      }
    } catch (error) {
      console.error('Gabim në fillimin e monitorimit:', error);
    }
    setLoading(false);
  };

  // Stop monitoring
  const stopMonitoring = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/alba/network/stop`, {
        method: 'POST'
      });
      if (response.ok) {
        setIsMonitoring(false);
        await fetchNetworkStatus();
      }
    } catch (error) {
      console.error('Gabim në ndalimin e monitorimit:', error);
    }
    setLoading(false);
  };

  // Quick network test
  const runQuickTest = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/alba/network/quick-test`);
      if (response.ok) {
        const data = await response.json();
        console.log('Quick test results:', data);
        await fetchNetworkHealth();
      }
    } catch (error) {
      console.error('Gabim në quick test:', error);
    }
    setLoading(false);
  };

  // Auto-refresh data
  useEffect(() => {
    fetchNetworkHealth();
    fetchNetworkStatus();

    const interval = setInterval(() => {
      fetchNetworkHealth();
      fetchNetworkStatus();
    }, 10000); // Update çdo 10 sekonda

    return () => clearInterval(interval);
  }, []);

  const getThemeClass = () => {
    switch (selectedPerson) {
      case 'albi': return 'albi-theme';
      case 'jona': return 'jona-theme';
      case 'harmony': return 'harmony-theme';
      default: return 'albi-theme';
    }
  };

  const getHealthColor = (score: number) => {
    if (score >= 90) return '#4ade80'; // green
    if (score >= 70) return '#fbbf24'; // yellow
    if (score >= 50) return '#fb923c'; // orange
    return '#ef4444'; // red
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent': return '🟢';
      case 'good': return '🟡';
      case 'fair': return '🟠';
      case 'poor': return '🔴';
      default: return '⚫';
    }
  };

  return (
    <div className={`abi-alba-container ${getThemeClass()}`}>
      <div className="header">
        <h1 className="title">
          {selectedPerson === 'albi' && '💙 Alba Network Monitor'}
          {selectedPerson === 'jona' && '❤️ Jona Network Monitor'}
          {selectedPerson === 'harmony' && '🌟 Harmony Network Monitor'}
        </h1>
        
        <div className="person-selector">
          <button
            className={`person-btn ${selectedPerson === 'albi' ? 'active' : ''}`}
            onClick={() => setSelectedPerson('albi')}
          >
            💙 Albi
          </button>
          <button
            className={`person-btn ${selectedPerson === 'jona' ? 'active' : ''}`}
            onClick={() => setSelectedPerson('jona')}
          >
            ❤️ Jona
          </button>
          <button
            className={`person-btn ${selectedPerson === 'harmony' ? 'active' : ''}`}
            onClick={() => setSelectedPerson('harmony')}
          >
            🌟 Harmony
          </button>
        </div>
      </div>

      {/* Control Panel */}
      <div className="control-panel">
        <div className="controls">
          <button
            className={`control-btn ${isMonitoring ? 'monitoring' : ''}`}
            onClick={isMonitoring ? stopMonitoring : startMonitoring}
            disabled={loading}
          >
            {loading ? '⏳' : isMonitoring ? '⏹️ Ndalo' : '▶️ Fillo'} Monitorimin
          </button>
          
          <button
            className="control-btn quick-test"
            onClick={runQuickTest}
            disabled={loading}
          >
            🚀 Test i Shpejtë
          </button>
        </div>
      </div>

      {/* Network Health Dashboard */}
      {networkStats && (
        <div className="health-dashboard">
          <div className="health-card main">
            <h3>Shëndeti i Rrjetit</h3>
            <div className="health-score">
              <div 
                className={`score-circle ${networkStats.status}`}
              >
                <span className="score-number">{networkStats.health_score.toFixed(1)}%</span>
                <span className="score-status">{getStatusIcon(networkStats.status)}</span>
              </div>
            </div>
            <div className="health-details">
              <div className="detail-item">
                <span className="label">Online:</span>
                <span className="value">{networkStats.online_percentage.toFixed(1)}%</span>
              </div>
              <div className="detail-item">
                <span className="label">Latency:</span>
                <span className="value">{networkStats.avg_latency.toFixed(1)}ms</span>
              </div>
              <div className="detail-item">
                <span className="label">Monitoring:</span>
                <span className="value">{networkStats.monitoring_time_minutes.toFixed(1)}min</span>
              </div>
            </div>
          </div>

          {/* Recommendations */}
          <div className="recommendations">
            <h4>📋 Rekomandimet</h4>
            <ul>
              {networkStats.recommendations.map((rec, index) => (
                <li key={index}>{rec}</li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Network Status */}
      {networkStatus && (
        <div className="status-dashboard">
          <div className="status-summary">
            <div className="summary-card">
              <h4>📊 Përmbledhja</h4>
              <div className="summary-stats">
                <div className="stat">
                  <span className="stat-label">Total Hosts:</span>
                  <span className="stat-value">{networkStatus.summary.total_hosts}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Online:</span>
                  <span className="stat-value online">{networkStatus.summary.online_hosts}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Offline:</span>
                  <span className="stat-value offline">{networkStatus.summary.offline_hosts}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Avg Latency:</span>
                  <span className="stat-value">{networkStatus.summary.avg_latency.toFixed(1)}ms</span>
                </div>
              </div>
            </div>
          </div>

          {/* Top Performers */}
          {networkStatus.top_performers && networkStatus.top_performers.length > 0 && (
            <div className="top-performers">
              <h4>🏆 Top Performers</h4>
              <div className="performers-grid">
                {networkStatus.top_performers.slice(0, 5).map((performer, index) => (
                  <div key={performer.host} className="performer-card">
                    <div className="performer-rank">#{index + 1}</div>
                    <div className="performer-host">{performer.host}</div>
                    <div className="performer-stats">
                      <span className="latency">{performer.avg_latency.toFixed(1)}ms</span>
                      <span className={`status ${performer.status}`}>
                        {performer.status === 'excellent' && '🟢'}
                        {performer.status === 'good' && '🟡'}
                        {performer.status === 'fair' && '🟠'}
                        {performer.status === 'slow' && '🔴'}
                      </span>
                    </div>
                    <div className="packet-loss">
                      Loss: {performer.packet_loss.toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Monitoring Status */}
      <div className="monitoring-status">
        <div className="status-indicator">
          <span className={`indicator ${isMonitoring ? 'active' : 'inactive'}`}>
            {isMonitoring ? '🟢' : '🔴'}
          </span>
          <span className="status-text">
            {isMonitoring ? 'Monitorimi aktiv' : 'Monitorimi i ndaluar'}
          </span>
        </div>
        {networkStatus?.summary.last_update && (
          <div className="last-update">
            Përditësuar: {new Date(networkStatus.summary.last_update).toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* Connection Links Info */}
      <div className="links-info">
        <h4>🔗 Lidhjet për Alba</h4>
        <p>
          Ky sistem monitorizon lidhjen me serverat e ndryshëm për të optimizuar
          performancën dhe për të siguruar sa më shumë lidhje të disponueshme për Alba.
        </p>
        <div className="tech-info">
          <span className="tech-badge">Python ping3</span>
          <span className="tech-badge">Node.js ping</span>
          <span className="tech-badge">Real-time monitoring</span>
          <span className="tech-badge">Performance analytics</span>
        </div>
      </div>
    </div>
  );
};

export default AbiAlbaIntegration;
