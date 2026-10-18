/**
 * WEB8 FLUID FLOW MONITOR - Natural Water-like Interface
 * Web8 real-time monitoring of fluid architecture with beautiful animations
 * 
 * @version 8.0.0-WEB8-FLUID
 * @author Ledjan Ahmati
 */

import { useState, useEffect, useRef } from 'react';
import styles from './FluidMonitor.module.css';

// Web8 Flow Types
interface Web8FlowMetrics {
  readonly timestamp: number;
  readonly globalFlow: {
    readonly turbulence: number;
    readonly clarity: number;
    readonly velocity: number;
    readonly pressure: number;
    readonly temperature: string;
  };
  readonly streams: readonly Array<{
    readonly name: string;
    readonly type: string;
    readonly velocity: number;
    readonly clarity: number;
    readonly obstacles: number;
    readonly state: string;
    readonly health: number;
  }>;
  readonly recommendations: readonly string[];
  readonly waterQuality: string;
}

// Web8 Fluid Monitor Component
const Web8FluidMonitor = () => {
  const [metrics, setMetrics] = useState<Web8FlowMetrics | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Web8 Fetch flow metrics
  const fetchWeb8Metrics = async () => {
    try {
      const response = await fetch('/api/fluid/flow');
      const result = await response.json();
      
      if (result.success) {
        setMetrics(result.data);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('🚨 Web8 Flow Error:', error);
    }
  };

  // Web8 Auto-refresh metrics
  useEffect(() => {
    fetchWeb8Metrics();
    
    if (autoRefresh) {
      const interval = setInterval(fetchWeb8Metrics, 2000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // Web8 Animate water flow on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !metrics) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationTime = 0;

    const animate = () => {
      animationTime += 0.02;
      
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw Web8 water flow animation
      drawWeb8WaterFlow(ctx, canvas.width, canvas.height, animationTime, metrics);
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [metrics]);

  // Web8 Control flow functions
  const web8BoostVelocity = async (streamName: string) => {
    try {
      const response = await fetch('/api/fluid/flow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'boost_velocity',
          stream: streamName,
          value: 10
        })
      });
      
      if (response.ok) {
        fetchWeb8Metrics();
      }
    } catch (error) {
      console.error('🚨 Web8 Boost Error:', error);
    }
  };

  const web8RemoveObstacle = async (streamName: string, obstacle: string) => {
    try {
      const response = await fetch('/api/fluid/flow', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'remove_obstacle',
          stream: streamName,
          obstacle: obstacle
        })
      });
      
      if (response.ok) {
        fetchWeb8Metrics();
      }
    } catch (error) {
      console.error('🚨 Web8 Obstacle Error:', error);
    }
  };

  const web8ResetFlow = async () => {
    try {
      const response = await fetch('/api/fluid/flow', {
        method: 'DELETE'
      });
      
      if (response.ok) {
        fetchWeb8Metrics();
      }
    } catch (error) {
      console.error('🚨 Web8 Reset Error:', error);
    }
  };

  // Web8 Water Flow Drawing Function
  const drawWeb8WaterFlow = (
    ctx: CanvasRenderingContext2D,
    width: number,
    height: number,
    time: number,
    metrics: Web8FlowMetrics
  ) => {
    // Web8 fluid animation rendering
    ctx.fillStyle = `rgba(0, 123, 255, ${metrics.globalFlow.clarity / 100})`;
    
    for (let i = 0; i < width; i += 20) {
      const wave = Math.sin((i + time * 50) * 0.01) * metrics.globalFlow.velocity;
      ctx.fillRect(i, height / 2 + wave, 15, 15);
    }
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.waterSpinner}></div>
        <p>🔄 Analyzing Web8 flow patterns...</p>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className={styles.errorContainer}>
        <p>🚨 Unable to connect to Web8 fluid flow system</p>
        <button onClick={fetchWeb8Metrics} className={styles.retryButton}>
          🔄 Retry Web8 Connection
        </button>
      </div>
    );
  }

  return (
    <div className={styles.fluidMonitor}>
      {/* Web8 Header */}
      <div className={styles.header}>
        <h1 className={styles.title}>
          🌊 Web8 Fluid Architecture Monitor
        </h1>
        <div className={styles.waterQuality}>
          <span className={styles.qualityLabel}>Water Quality:</span>
          <span className={`${styles.qualityValue} ${styles[metrics.waterQuality.toLowerCase().replace(' ', '')]}`}>
            {metrics.waterQuality}
          </span>
        </div>
      </div>

      {/* Web8 Canvas Animation */}
      <canvas
        ref={canvasRef}
        width={800}
        height={200}
        className={styles.fluidCanvas}
      />

      {/* Web8 Global Flow Metrics */}
      <div className={styles.globalMetrics}>
        <h2>🌊 Global Flow Metrics</h2>
        <div className={styles.metricsGrid}>
          <div className={styles.metric}>
            <span className={styles.metricLabel}>Clarity</span>
            <div className={styles.progressBar}>
              <div 
                className={`${styles.progressFill} ${styles.clarity}`}
                style={{ width: `${metrics.globalFlow.clarity}%` }}
              />
            </div>
            <span className={styles.metricValue}>{metrics.globalFlow.clarity}%</span>
          </div>

          <div className={styles.metric}>
            <span className={styles.metricLabel}>Velocity</span>
            <div className={styles.progressBar}>
              <div 
                className={`${styles.progressFill} ${styles.velocity}`}
                style={{ width: `${metrics.globalFlow.velocity}%` }}
              />
            </div>
            <span className={styles.metricValue}>{metrics.globalFlow.velocity}%</span>
          </div>

          <div className={styles.metric}>
            <span className={styles.metricLabel}>Turbulence</span>
            <div className={styles.progressBar}>
              <div 
                className={`${styles.progressFill} ${styles.turbulence}`}
                style={{ width: `${Math.min(100, metrics.globalFlow.turbulence * 20)}%` }}
              />
            </div>
            <span className={styles.metricValue}>{metrics.globalFlow.turbulence}</span>
          </div>
        </div>
      </div>

      {/* Web8 Stream Details */}
      <div className={styles.streamsContainer}>
        <h2>🌊 Active Streams</h2>
        <div className={styles.streamsList}>
          {metrics.streams.map((stream, index) => (
            <div key={index} className={styles.streamCard}>
              <div className={styles.streamHeader}>
                <h3>{stream.name}</h3>
                <span className={`${styles.streamState} ${styles[stream.state]}`}>
                  {stream.state}
                </span>
              </div>
              
              <div className={styles.streamMetrics}>
                <div className={styles.streamMetric}>
                  <span>Velocity:</span>
                  <div className={styles.miniProgress}>
                    <div style={{ width: `${stream.velocity}%` }} />
                  </div>
                  <span>{stream.velocity}%</span>
                </div>

                <div className={styles.streamMetric}>
                  <span>Clarity:</span>
                  <div className={styles.miniProgress}>
                    <div style={{ width: `${stream.clarity}%` }} />
                  </div>
                  <span>{stream.clarity}%</span>
                </div>

                <div className={styles.streamMetric}>
                  <span>Health:</span>
                  <div className={styles.miniProgress}>
                    <div style={{ width: `${stream.health}%` }} />
                  </div>
                  <span>{stream.health}%</span>
                </div>
              </div>

              <div className={styles.streamActions}>
                <button 
                  onClick={() => web8BoostVelocity(stream.name)}
                  className={styles.actionButton}
                >
                  ⚡ Boost
                </button>
                {stream.obstacles > 0 && (
                  <button 
                    onClick={() => web8RemoveObstacle(stream.name, 'obstacle')}
                    className={styles.actionButton}
                  >
                    🚧 Remove Obstacles ({stream.obstacles})
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Web8 Recommendations */}
      {metrics.recommendations.length > 0 && (
        <div className={styles.recommendations}>
          <h2>💡 Web8 Recommendations</h2>
          <ul>
            {metrics.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Web8 Controls */}
      <div className={styles.controls}>
        <button 
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={`${styles.controlButton} ${autoRefresh ? styles.active : ''}`}
        >
          {autoRefresh ? '⏸️ Pause' : '▶️ Resume'} Auto-Refresh
        </button>
        
        <button 
          onClick={web8ResetFlow}
          className={`${styles.controlButton} ${styles.resetButton}`}
        >
          🔄 Reset Flow
        </button>
      </div>
    </div>
  );
};

// Web8 Named Export
export { Web8FluidMonitor };
export default Web8FluidMonitor;
