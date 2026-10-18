/**
 * Guardian Security Dashboard Component
 * Real-time threat monitoring and security analytics
 * 
 * @version 8.0.0
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 */

'use client';

import React, { useState, useEffect } from 'react';
import styles from './GuardianDashboard.module.css';

interface ThreatLog {
  timestamp: string;
  ip: string;
  reason: string;
  userAgent?: string;
  path?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  blocked: boolean;
}

interface GuardianStats {
  totalRequests: number;
  blockedRequests: number;
  uniqueIPs: number;
  blockedIPs: number;
  avgResponseTime: number;
  activeConnections: number;
  systemHealth: 'healthy' | 'degraded' | 'critical';
}

interface GuardianData {
  status: 'active' | 'inactive';
  stats: GuardianStats;
  recentThreats: ThreatLog[];
  blockedIPs: string[];
  config: {
    maxRequestsPerMinute: number;
    maxPayloadSize: number;
    blockDuration: number;
  };
}

export default function GuardianDashboard() {
  const [guardianData, setGuardianData] = useState<GuardianData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [blockIP, setBlockIP] = useState('');
  const [blockReason, setBlockReason] = useState('');

  useEffect(() => {
    fetchGuardianData();
    const interval = setInterval(fetchGuardianData, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchGuardianData = async () => {
    try {
      const response = await fetch('/api/guardian');
      if (!response.ok) throw new Error('Failed to fetch Guardian data');
      
      const result = await response.json();
      setGuardianData(result.data);
      setError(null);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleBlockIP = async () => {
    if (!blockIP.trim() || !blockReason.trim()) {
      alert('Both IP and reason are required');
      return;
    }

    try {
      const response = await fetch('/api/guardian', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'block',
          ip: blockIP.trim(),
          reason: blockReason.trim()
        })
      });

      if (!response.ok) throw new Error('Failed to block IP');

      setBlockIP('');
      setBlockReason('');
      fetchGuardianData();
    } catch (error) {
      alert(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading Guardian Dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>Error: {error}</div>
      </div>
    );
  }

  if (!guardianData) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>No Guardian data available</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1 className={styles.title}>🛡️ Guardian Security Dashboard</h1>
        <div className={`${styles.status} ${styles[guardianData.status]}`}>
          {guardianData.status === 'active' ? '🟢 Active' : '🔴 Inactive'}
        </div>
      </div>

      {/* Stats Overview */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <h3>Total Requests</h3>
          <div className={styles.statValue}>{guardianData.stats.totalRequests.toLocaleString()}</div>
        </div>
        <div className={styles.statCard}>
          <h3>Blocked Requests</h3>
          <div className={styles.statValue}>{guardianData.stats.blockedRequests.toLocaleString()}</div>
        </div>
        <div className={styles.statCard}>
          <h3>Unique IPs</h3>
          <div className={styles.statValue}>{guardianData.stats.uniqueIPs.toLocaleString()}</div>
        </div>
        <div className={styles.statCard}>
          <h3>System Health</h3>
          <div className={`${styles.healthStatus} ${styles[guardianData.stats.systemHealth]}`}>
            {guardianData.stats.systemHealth}
          </div>
        </div>
      </div>

      {/* Block IP Form */}
      <div className={styles.blockForm}>
        <h3>Block IP Address</h3>
        <div className={styles.formGroup}>
          <input
            type="text"
            placeholder="IP Address"
            value={blockIP}
            onChange={(e) => setBlockIP(e.target.value)}
            className={styles.input}
          />
          <input
            type="text"
            placeholder="Block Reason"
            value={blockReason}
            onChange={(e) => setBlockReason(e.target.value)}
            className={styles.input}
          />
          <button onClick={handleBlockIP} className={styles.blockButton}>
            Block IP
          </button>
        </div>
      </div>

      {/* Recent Threats */}
      <div className={styles.threatsSection}>
        <h3>Recent Threats</h3>
        <div className={styles.threatsList}>
          {guardianData.recentThreats.map((threat, index) => (
            <div key={index} className={`${styles.threatItem} ${styles[threat.severity]}`}>
              <div className={styles.threatInfo}>
                <strong>{threat.ip}</strong> - {threat.reason}
              </div>
              <div className={styles.threatMeta}>
                {new Date(threat.timestamp).toLocaleString()} |
                {threat.blocked ? ' 🚫 Blocked' : ' ⚠️ Detected'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Blocked IPs */}
      <div className={styles.blockedSection}>
        <h3>Blocked IP Addresses</h3>
        <div className={styles.blockedList}>
          {guardianData.blockedIPs.map((ip, index) => (
            <div key={index} className={styles.blockedIP}>
              {ip}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}