'use client';

import React, { useState, useEffect } from 'react';
import styles from './gateway.module.css';

interface GatewayRoute {
  id: string;
  path: string;
  target: string;
  status: 'active' | 'inactive' | 'error';
  requests: number;
  avgLatency: number;
  lastAccess: string;
}

interface LoadBalancer {
  id: string;
  name: string;
  targets: string[];
  algorithm: 'round-robin' | 'least-connections' | 'weighted';
  health: 'healthy' | 'degraded' | 'down';
  activeConnections: number;
}

interface GatewayMetrics {
  totalRequests: number;
  requestsPerSecond: number;
  avgResponseTime: number;
  errorRate: number;
  activeConnections: number;
  cacheHitRate: number;
}

export default function APIGatewayDashboard() {
  const [routes, setRoutes] = useState<GatewayRoute[]>([]);
  const [loadBalancers, setLoadBalancers] = useState<LoadBalancer[]>([]);
  const [metrics, setMetrics] = useState<GatewayMetrics>({
    totalRequests: 0,
    requestsPerSecond: 0,
    avgResponseTime: 0,
    errorRate: 0,
    activeConnections: 0,
    cacheHitRate: 0
  });
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  useEffect(() => {
    // Set initial timestamp on client-side only
    setLastUpdated(new Date().toLocaleTimeString());
    fetchGatewayData();
    const interval = setInterval(fetchGatewayData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchGatewayData = async () => {
    setIsLoading(true);
    try {
      // Simulate API gateway data
      const mockRoutes: GatewayRoute[] = [
        {
          id: 'api-v1',
          path: '/api/v1/*',
          target: 'http://api-service:8080',
          status: 'active',
          requests: 15420,
          avgLatency: 45,
          lastAccess: new Date(Date.now() - Math.random() * 60000).toISOString()
        },
        {
          id: 'ultra-industrial',
          path: '/api/ultra-industrial/*',
          target: 'http://industrial-service:3001',
          status: 'active',
          requests: 8934,
          avgLatency: 78,
          lastAccess: new Date(Date.now() - Math.random() * 30000).toISOString()
        },
        {
          id: 'agi-core',
          path: '/api/agi/*',
          target: 'http://agi-service:9000',
          status: 'active',
          requests: 23567,
          avgLatency: 120,
          lastAccess: new Date(Date.now() - Math.random() * 10000).toISOString()
        },
        {
          id: 'mesh-network',
          path: '/api/mesh/*',
          target: 'http://mesh-service:7777',
          status: 'error',
          requests: 456,
          avgLatency: 0,
          lastAccess: new Date(Date.now() - 300000).toISOString()
        }
      ];

      const mockLoadBalancers: LoadBalancer[] = [
        {
          id: 'main-lb',
          name: 'Main Load Balancer',
          targets: ['api-1:8080', 'api-2:8080', 'api-3:8080'],
          algorithm: 'round-robin',
          health: 'healthy',
          activeConnections: 245
        },
        {
          id: 'agi-lb',
          name: 'AGI Load Balancer',
          targets: ['agi-1:9000', 'agi-2:9000'],
          algorithm: 'least-connections',
          health: 'healthy',
          activeConnections: 89
        },
        {
          id: 'industrial-lb',
          name: 'Industrial Load Balancer',
          targets: ['industrial-1:3001'],
          algorithm: 'weighted',
          health: 'degraded',
          activeConnections: 156
        }
      ];

      const mockMetrics: GatewayMetrics = {
        totalRequests: mockRoutes.reduce((sum, route) => sum + route.requests, 0),
        requestsPerSecond: Math.floor(Math.random() * 50) + 150,
        avgResponseTime: Math.floor(Math.random() * 30) + 65,
        errorRate: Math.random() * 2 + 0.5,
        activeConnections: mockLoadBalancers.reduce((sum, lb) => sum + lb.activeConnections, 0),
        cacheHitRate: Math.random() * 15 + 85
      };

      setRoutes(mockRoutes);
      setLoadBalancers(mockLoadBalancers);
      setMetrics(mockMetrics);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Error fetching gateway data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'healthy': return '#00ff88';
      case 'degraded': return '#ffa502';
      case 'inactive':
      case 'error':
      case 'down': return '#ff6b6b';
      default: return '#6c757d';
    }
  };

  const formatLatency = (latency: number) => {
    return latency > 0 ? `${latency}ms` : 'N/A';
  };

  const formatLastAccess = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>🌐 API Gateway Dashboard</h1>
        <p className={styles.subtitle}>
          Real-time API routing, load balancing, and performance monitoring
        </p>
        <div className={styles.lastUpdated}>
          Last updated: {lastUpdated || 'Loading...'}
          {isLoading && <span className={styles.loading}>⟳</span>}
        </div>
      </div>

      {/* Metrics Overview */}
      <div className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>📊</div>
          <div className={styles.metricData}>
            <div className={styles.metricValue}>{metrics.totalRequests.toLocaleString()}</div>
            <div className={styles.metricLabel}>Total Requests</div>
          </div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>⚡</div>
          <div className={styles.metricData}>
            <div className={styles.metricValue}>{metrics.requestsPerSecond}/s</div>
            <div className={styles.metricLabel}>Requests/Second</div>
          </div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>⏱️</div>
          <div className={styles.metricData}>
            <div className={styles.metricValue}>{metrics.avgResponseTime}ms</div>
            <div className={styles.metricLabel}>Avg Response Time</div>
          </div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>❌</div>
          <div className={styles.metricData}>
            <div className={styles.metricValue}>{metrics.errorRate.toFixed(2)}%</div>
            <div className={styles.metricLabel}>Error Rate</div>
          </div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>🔗</div>
          <div className={styles.metricData}>
            <div className={styles.metricValue}>{metrics.activeConnections}</div>
            <div className={styles.metricLabel}>Active Connections</div>
          </div>
        </div>
        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>💾</div>
          <div className={styles.metricData}>
            <div className={styles.metricValue}>{metrics.cacheHitRate.toFixed(1)}%</div>
            <div className={styles.metricLabel}>Cache Hit Rate</div>
          </div>
        </div>
      </div>

      {/* Routes Section */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>🛣️ API Routes</h2>
        <div className={styles.routesGrid}>
          {routes.map((route) => (
            <div key={route.id} className={styles.routeCard}>
              <div className={styles.routeHeader}>
                <div className={styles.routePath}>{route.path}</div>
                <div 
                  className={styles.routeStatus}
                  style={{ color: getStatusColor(route.status) }}
                >
                  ● {route.status.toUpperCase()}
                </div>
              </div>
              <div className={styles.routeTarget}>→ {route.target}</div>
              <div className={styles.routeMetrics}>
                <div className={styles.routeMetric}>
                  <span>Requests:</span>
                  <span>{route.requests.toLocaleString()}</span>
                </div>
                <div className={styles.routeMetric}>
                  <span>Latency:</span>
                  <span>{formatLatency(route.avgLatency)}</span>
                </div>
                <div className={styles.routeMetric}>
                  <span>Last Access:</span>
                  <span>{formatLastAccess(route.lastAccess)}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Load Balancers Section */}
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>⚖️ Load Balancers</h2>
        <div className={styles.loadBalancersGrid}>
          {loadBalancers.map((lb) => (
            <div key={lb.id} className={styles.loadBalancerCard}>
              <div className={styles.loadBalancerHeader}>
                <div className={styles.loadBalancerName}>{lb.name}</div>
                <div 
                  className={styles.loadBalancerHealth}
                  style={{ color: getStatusColor(lb.health) }}
                >
                  ● {lb.health.toUpperCase()}
                </div>
              </div>
              <div className={styles.loadBalancerInfo}>
                <div className={styles.loadBalancerAlgorithm}>
                  Algorithm: {lb.algorithm}
                </div>
                <div className={styles.loadBalancerConnections}>
                  Active Connections: {lb.activeConnections}
                </div>
              </div>
              <div className={styles.loadBalancerTargets}>
                <div className={styles.targetsLabel}>Targets:</div>
                {lb.targets.map((target, index) => (
                  <div key={index} className={styles.target}>
                    🎯 {target}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Controls */}
      <div className={styles.controls}>
        <button 
          className={styles.refreshButton}
          onClick={fetchGatewayData}
          disabled={isLoading}
        >
          {isLoading ? '⟳ Refreshing...' : '🔄 Refresh Data'}
        </button>
      </div>
    </div>
  );
}
