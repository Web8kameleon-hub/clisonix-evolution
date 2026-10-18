/**
 * 🚀 CYBER SECURITY COMMAND CENTER
 * Web8 Cyber Defense & Mirror Security System
 * 
 * @version 8.0.0 Ultra Industrial
 * @shqip Sistemi më i avancuar i sigurisë kibernetike në Shqipëri
 */

'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '../../lib/utils';
import { EnhancedButton } from '../../components/ui/enhanced-button';
import styles from './cyber.module.css';

// CVA Variants for styling
const threatIndicatorVariants = cva(
  "px-4 py-2 rounded-full font-bold text-sm transition-all duration-300",
  {
    variants: {
      level: {
        green: "bg-green-500/20 text-green-400 border border-green-500/30",
        yellow: "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30",
        orange: "bg-orange-500/20 text-orange-400 border border-orange-500/30",
        red: "bg-red-500/20 text-red-400 border border-red-500/30",
        black: "bg-gray-900/20 text-gray-300 border border-gray-700/30"
      },
      active: {
        true: "animate-pulse shadow-lg",
        false: "opacity-70"
      }
    },
    defaultVariants: {
      level: "green",
      active: true
    }
  }
);

const metricCardVariants = cva(
  "p-6 rounded-xl backdrop-blur-md transition-all duration-300 hover:scale-105",
  {
    variants: {
      variant: {
        default: "bg-slate-800/50 border border-slate-700/50",
        success: "bg-green-900/30 border border-green-700/50",
        warning: "bg-yellow-900/30 border border-yellow-700/50",
        danger: "bg-red-900/30 border border-red-700/50"
      }
    },
    defaultVariants: {
      variant: "default"
    }
  }
);

// CVA variants for severity badges
const severityBadgeVariants = cva(
  "px-2 py-1 rounded-full text-xs font-bold transition-all duration-300",
  {
    variants: {
      severity: {
        low: "bg-green-500 text-white",
        medium: "bg-yellow-500 text-black",
        high: "bg-orange-500 text-white",
        critical: "bg-red-500 text-white animate-pulse",
        extreme: "bg-purple-600 text-white animate-pulse"
      }
    },
    defaultVariants: {
      severity: "low"
    }
  }
);

// CVA variants for mirror status indicators
const mirrorStatusVariants = cva(
  "w-3 h-3 rounded-full mr-2 transition-all duration-300",
  {
    variants: {
      status: {
        online: "bg-green-500 shadow-lg shadow-green-500/50",
        warning: "bg-yellow-500 shadow-lg shadow-yellow-500/50 animate-pulse",
        offline: "bg-red-500 shadow-lg shadow-red-500/50 animate-pulse",
        maintenance: "bg-blue-500 shadow-lg shadow-blue-500/50"
      }
    },
    defaultVariants: {
      status: "online"
    }
  }
);

// CVA variants for control panel buttons
const controlButtonVariants = cva(
  "px-6 py-3 rounded-lg font-semibold text-sm transition-all duration-300 border-2 backdrop-blur-md",
  {
    variants: {
      variant: {
        primary: "bg-green-600/20 border-green-500 text-green-400 hover:bg-green-600/30 hover:shadow-lg hover:shadow-green-500/30",
        secondary: "bg-blue-600/20 border-blue-500 text-blue-400 hover:bg-blue-600/30 hover:shadow-lg hover:shadow-blue-500/30",
        warning: "bg-orange-600/20 border-orange-500 text-orange-400 hover:bg-orange-600/30 hover:shadow-lg hover:shadow-orange-500/30",
        danger: "bg-red-600/20 border-red-500 text-red-400 hover:bg-red-600/30 hover:shadow-lg hover:shadow-red-500/30"
      },
      size: {
        sm: "px-4 py-2 text-xs",
        md: "px-6 py-3 text-sm",
        lg: "px-8 py-4 text-base"
      },
      state: {
        normal: "",
        scanning: "animate-pulse",
        active: "shadow-lg"
      }
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
      state: "normal"
    }
  }
);

// Animation variants
const containerVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      staggerChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, x: -20 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.4 }
  }
};

const threatItemVariants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: 0.3 }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    transition: { duration: 0.2 }
  }
};

// Cyber Security Types
interface CyberThreat {
  id: string;
  type: 'ddos' | 'injection' | 'malware' | 'phishing' | 'botnet' | 'ransomware' | 'apt';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  target: string;
  timestamp: number;
  description: string;
  status: 'active' | 'blocked' | 'mitigated' | 'investigating';
  attackVector: string;
  geolocation?: {
    country: string;
    city: string;
    coords: [number, number];
  };
}

interface MirrorSecurityStatus {
  mirroringSystems: number;
  activeMirrors: number;
  mirrorHealth: number;
  dataIntegrity: number;
  syncStatus: 'synchronized' | 'syncing' | 'out_of_sync' | 'error';
  lastMirrorUpdate: number;
  mirrorLatency: number;
  redundancyLevel: number;
}

interface CyberDefenseMetrics {
  threatLevel: 'green' | 'yellow' | 'orange' | 'red' | 'black';
  activeThreats: number;
  blockedAttacks: number;
  successfulBlocks: number;
  falsePositives: number;
  systemUptime: number;
  defenseEfficiency: number;
  aiPredictions: number;
  quantumEncryptionActive: boolean;
  neuralShieldStatus: 'active' | 'learning' | 'inactive';
}

export default function CyberSecurityDashboard() {
  const [threats, setThreats] = useState<CyberThreat[]>([]);
  const [mirrorSecurity, setMirrorSecurity] = useState<MirrorSecurityStatus>({
    mirroringSystems: 12,
    activeMirrors: 11,
    mirrorHealth: 98.5,
    dataIntegrity: 99.8,
    syncStatus: 'synchronized',
    lastMirrorUpdate: Date.now() - 30000,
    mirrorLatency: 45,
    redundancyLevel: 5
  });
  const [defenseMetrics, setDefenseMetrics] = useState<CyberDefenseMetrics>({
    threatLevel: 'yellow',
    activeThreats: 0,
    blockedAttacks: 1247,
    successfulBlocks: 1243,
    falsePositives: 4,
    systemUptime: 99.97,
    defenseEfficiency: 97.8,
    aiPredictions: 34,
    quantumEncryptionActive: true,
    neuralShieldStatus: 'active'
  });
  const [isScanning, setIsScanning] = useState(false);
  const [realTimeData, setRealTimeData] = useState(true);

  // Fetch real security data from existing systems
  useEffect(() => {
    if (!realTimeData) return;

    const fetchRealSecurityData = async () => {
      try {
        // Fetch from Cyber Security API (aggregated data)
        const cyberResponse = await fetch('/api/cyber-security?action=status');
        if (cyberResponse.ok) {
          const cyberData = await cyberResponse.json();
          if (cyberData.success) {
            setDefenseMetrics(prev => ({
              ...prev,
              threatLevel: cyberData.data.threatLevel,
              activeThreats: cyberData.data.totalThreats,
              blockedAttacks: cyberData.data.totalBlocked,
              defenseEfficiency: cyberData.data.avgEfficiency,
              systemUptime: cyberData.data.onlineSystems === cyberData.data.totalSystems ? 99.97 : 95.2,
              quantumEncryptionActive: cyberData.data.quantumEncryption,
              neuralShieldStatus: cyberData.data.neuralShield
            }));

            // Update mirror security based on mesh status
            const meshSystem = cyberData.data.systems.find((s: any) => s.name === 'Continental Mesh Network');
            if (meshSystem) {
              setMirrorSecurity(prev => ({
                ...prev,
                mirrorHealth: meshSystem.efficiency,
                syncStatus: meshSystem.status === 'online' ? 'synchronized' : 'out_of_sync',
                lastMirrorUpdate: Date.now()
              }));
            }
          }
        }

        // Fetch real threats
        const threatsResponse = await fetch('/api/cyber-security?action=threats');
        if (threatsResponse.ok) {
          const threatsData = await threatsResponse.json();
          if (threatsData.success && threatsData.data.threats) {
            const realThreats: CyberThreat[] = threatsData.data.threats.map((threat: any) => ({
              id: threat.id,
              type: threat.type as CyberThreat['type'],
              severity: threat.severity as CyberThreat['severity'],
              source: threat.source,
              target: 'ultrawebthinking.com',
              timestamp: threat.timestamp,
              description: threat.description,
              status: threat.status as CyberThreat['status'],
              attackVector: threat.system || 'Security System'
            }));
            
            setThreats(prev => [...realThreats, ...prev.slice(0, 30)]);
          }
        }

      } catch (error) {
        console.error('Error fetching real security data:', error);
      }
    };

    // Initial fetch
    fetchRealSecurityData();
    
    // Real-time updates every 10 seconds
    const interval = setInterval(fetchRealSecurityData, 10000);
    return () => clearInterval(interval);
  }, [realTimeData]);

  const performDeepScan = useCallback(async () => {
    setIsScanning(true);
    
    try {
      // Real system scan - check all security APIs
      const [firewallResponse, guardianResponse, meshResponse] = await Promise.all([
        fetch('/api/advanced-firewall?action=test&ip=127.0.0.1&path=/admin').catch(() => null),
        fetch('/api/guardian').catch(() => null),
        fetch('/api/continental-mesh').catch(() => null)
      ]);

      const scanResults: CyberThreat[] = [];

      // Analyze firewall response
      if (firewallResponse && firewallResponse.ok) {
        const firewallData = await firewallResponse.json();
        if (firewallData.testResult) {
          scanResults.push({
            id: `scan-firewall-${Date.now()}`,
            type: 'injection',
            severity: firewallData.testResult.blocked ? 'medium' : 'high',
            source: 'Firewall Scan',
            target: 'System Infrastructure',
            timestamp: Date.now(),
            description: `Firewall test: ${firewallData.testResult.blocked ? 'Protected' : 'Vulnerability detected'}`,
            status: firewallData.testResult.blocked ? 'blocked' : 'investigating',
            attackVector: 'Security Assessment'
          });
        }
      }

      // Analyze Guardian response
      if (guardianResponse && guardianResponse.ok) {
        const guardianData = await guardianResponse.json();
        if (guardianData.success && guardianData.data.stats) {
          scanResults.push({
            id: `scan-guardian-${Date.now()}`,
            type: 'ddos',
            severity: guardianData.data.stats.blockedIPs > 10 ? 'high' : 'low',
            source: 'Guardian System',
            target: 'Network Infrastructure',
            timestamp: Date.now(),
            description: `Guardian scan: ${guardianData.data.stats.blockedIPs} IPs blocked`,
            status: 'mitigated',
            attackVector: 'DDoS Protection'
          });
        }
      }

      // Analyze Continental Mesh
      if (meshResponse && meshResponse.ok) {
        const meshData = await meshResponse.json();
        if (meshData.success) {
          scanResults.push({
            id: `scan-mesh-${Date.now()}`,
            type: 'botnet',
            severity: meshData.data.status === 'operational' ? 'low' : 'medium',
            source: 'Continental Mesh',
            target: 'Distributed Network',
            timestamp: Date.now(),
            description: `Mesh network status: ${meshData.data.status}`,
            status: meshData.data.status === 'operational' ? 'mitigated' : 'investigating',
            attackVector: 'Network Analysis'
          });
        }
      }

      setThreats(prev => [...scanResults, ...prev]);
      
    } catch (error) {
      console.error('Deep scan error:', error);
    }
    
    setIsScanning(false);
  }, []);

  const getThreatIcon = (type: CyberThreat['type']) => {
    const icons = {
      ddos: '💥',
      injection: '💉',
      malware: '🦠',
      phishing: '🎣',
      botnet: '🤖',
      ransomware: '🔒',
      apt: '🎯'
    };
    return icons[type];
  };

  const getSeverityColor = (severity: CyberThreat['severity']) => {
    const colors = {
      low: '#4ade80',
      medium: '#fbbf24',
      high: '#f97316',
      critical: '#dc2626'
    };
    return colors[severity];
  };

  const getThreatLevelColor = (level: CyberDefenseMetrics['threatLevel']) => {
    const colors = {
      green: '#10b981',
      yellow: '#f59e0b',
      orange: '#f97316',
      red: '#dc2626',
      black: '#1f2937'
    };
    return colors[level];
  };

  return (
    <motion.div
      className={styles['dashboard']}
      initial="hidden"
      animate="visible"
      variants={containerVariants}
    >
      <motion.div className={styles['header']} variants={itemVariants}>
        <motion.h1
          className={styles['title']}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          🚀 CYBER SECURITY COMMAND CENTER
        </motion.h1>
        <motion.p
          className={styles['subtitle']}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          Web8 Cyber Defense • Mirror Security • Quantum Protection
        </motion.p>

        <motion.div
          className={styles['statusIndicators']}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 0.6 }}
        >
          <motion.div
            className={cn(
              threatIndicatorVariants({
                level: defenseMetrics.threatLevel,
                active: true
              }),
              styles['indicator']
            )}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            🚨 Threat Level: {defenseMetrics.threatLevel.toUpperCase()}
          </motion.div>
          <motion.div
            className={cn(
              threatIndicatorVariants({
                level: defenseMetrics.quantumEncryptionActive ? 'green' : 'red',
                active: defenseMetrics.quantumEncryptionActive
              }),
              styles['indicator']
            )}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            ⚛️ Quantum: {defenseMetrics.quantumEncryptionActive ? 'ACTIVE' : 'INACTIVE'}
          </motion.div>
          <motion.div
            className={cn(
              threatIndicatorVariants({
                level: defenseMetrics.neuralShieldStatus === 'active' ? 'green' : 'yellow',
                active: defenseMetrics.neuralShieldStatus === 'active'
              }),
              styles['indicator']
            )}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            🧠 Neural Shield: {defenseMetrics.neuralShieldStatus.toUpperCase()}
          </motion.div>
        </motion.div>
      </motion.div>

      <div className={styles['metricsGrid']}>
        {/* Cyber Defense Metrics */}
        <div className={styles['metricsCard']}>
          <h3>🛡️ Cyber Defense Metrics</h3>
          <div className={styles['metricsList']}>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>Active Threats</span>
              <span className={`${styles['metricValue']} ${styles['critical']}`}>{defenseMetrics.activeThreats}</span>
            </div>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>Blocked Attacks</span>
              <span className={`${styles['metricValue']} ${styles['success']}`}>{defenseMetrics.blockedAttacks.toLocaleString()}</span>
            </div>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>Defense Efficiency</span>
              <span className={`${styles['metricValue']} ${styles['success']}`}>{defenseMetrics.defenseEfficiency}%</span>
            </div>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>System Uptime</span>
              <span className={`${styles['metricValue']} ${styles['success']}`}>{defenseMetrics.systemUptime}%</span>
            </div>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>AI Predictions</span>
              <span className={styles['metricValue']}>{defenseMetrics.aiPredictions}</span>
            </div>
          </div>
        </div>

        {/* Mirror Security Status */}
        <div className={styles['metricsCard']}>
          <h3>🪞 Mirror Security Systems</h3>
          <div className={styles['metricsList']}>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>Active Mirrors</span>
              <span className={styles['metricValue']}>{mirrorSecurity.activeMirrors}/{mirrorSecurity.mirroringSystems}</span>
            </div>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>Mirror Health</span>
              <span className={`${styles['metricValue']} ${styles['success']}`}>{mirrorSecurity.mirrorHealth.toFixed(1)}%</span>
            </div>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>Data Integrity</span>
              <span className={`${styles['metricValue']} ${styles['success']}`}>{mirrorSecurity.dataIntegrity.toFixed(1)}%</span>
            </div>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>Sync Status</span>
              <span className={`${styles['metricValue']} ${styles[mirrorSecurity.syncStatus === 'synchronized' ? 'success' : 'warning']}`}>
                {mirrorSecurity.syncStatus.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>Mirror Latency</span>
              <span className={styles['metricValue']}>{mirrorSecurity.mirrorLatency}ms</span>
            </div>
            <div className={styles['metric']}>
              <span className={styles['metricLabel']}>Redundancy Level</span>
              <span className={`${styles['metricValue']} ${styles['success']}`}>{mirrorSecurity.redundancyLevel}x</span>
            </div>
          </div>
        </div>
      </div>

      {/* Control Panel */}
      <motion.div
        className={styles['controlPanel']}
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.8 }}
      >
        <EnhancedButton
          variant="primary"
          size="lg"
          onClick={performDeepScan}
          disabled={isScanning}
          isLoading={isScanning}
          loadingText="🔍 Scanning..."
        >
          🔍 Deep System Scan
        </EnhancedButton>

        <EnhancedButton
          variant="secondary"
          size="lg"
          onClick={() => setRealTimeData(!realTimeData)}
        >
          {realTimeData ? '⏸️ Pause Monitor' : '▶️ Resume Monitor'}
        </EnhancedButton>

        <EnhancedButton
          variant="warning"
          size="lg"
          onClick={() => {
            setThreats([]);
            setDefenseMetrics(prev => ({ ...prev, activeThreats: 0, threatLevel: 'green' }));
          }}
        >
          🧹 Clear Threats
        </EnhancedButton>
      </motion.div>

      {/* Threat Feed */}
      <div className={styles['threatFeed']}>
        <h3>🚨 Real-Time Threat Intelligence</h3>

        {threats.length === 0 && (
          <div className={styles['noThreats']}>
            <span>✅ No active threats detected</span>
            <p>System is secure and operating normally</p>
          </div>
        )}

        <div className={styles['threatList']}>
          <AnimatePresence mode="popLayout">
            {threats.slice(0, 20).map((threat, index) => (
              <motion.div
                key={threat.id}
                className={`${styles['threatItem']} ${styles[`severity-${threat.severity}`]} ${styles[`status-${threat.status}`]}`}
                variants={threatItemVariants}
                initial="hidden"
                animate="visible"
                exit="exit"
                layout
                transition={{
                  duration: 0.3,
                  delay: index * 0.05
                }}
                whileHover={{
                  scale: 1.02,
                  boxShadow: "0 10px 25px rgba(0,0,0,0.2)"
                }}
              >
                <motion.div
                  className={styles['threatHeader']}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                >
                  <motion.span
                    className={styles['threatIcon']}
                    whileHover={{ scale: 1.3, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    {getThreatIcon(threat.type)}
                  </motion.span>
                  <span className={styles['threatType']}>{threat.type.toUpperCase()}</span>
                  <motion.span
                    className={cn(severityBadgeVariants({ severity: threat.severity }))}
                    whileHover={{ scale: 1.1 }}
                    transition={{ type: "spring", stiffness: 400 }}
                  >
                    {threat.severity.toUpperCase()}
                  </motion.span>
                  <span className={styles['threatStatus']}>{threat.status.toUpperCase()}</span>
                </motion.div>

                <motion.div
                  className={styles['threatDetails']}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  <p className={styles['threatDescription']}>{threat.description}</p>
                  <div className={styles['threatMeta']}>
                    <span>📍 {threat.source}</span>
                    <span>🎯 {threat.target}</span>
                    <span>⚡ {threat.attackVector}</span>
                    {threat.geolocation && (
                      <span>🌍 {threat.geolocation.country}</span>
                    )}
                    <span>⏰ {new Date(threat.timestamp).toLocaleTimeString()}</span>
                  </div>
                </motion.div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </div>

      {/* Mirror Security Details */}
      <div className={styles['mirrorDetails']}>
        <h3>🪞 Mirror Security Architecture</h3>
        <div className={styles['mirrorGrid']}>
          <div className={styles['mirrorCard']}>
            <h4>Primary Mirrors</h4>
            <div className={styles['mirrorList']}>
              <div className={styles['mirrorItem']}>
                <span className={cn(mirrorStatusVariants({ status: 'online' }))}></span>
                <span>Mirror-US-East</span>
                <span className={styles['mirrorHealth']}>99.8%</span>
              </div>
              <div className={styles['mirrorItem']}>
                <span className={cn(mirrorStatusVariants({ status: 'online' }))}></span>
                <span>Mirror-EU-Central</span>
                <span className={styles['mirrorHealth']}>99.5%</span>
              </div>
              <div className={styles['mirrorItem']}>
                <span className={cn(mirrorStatusVariants({ status: 'online' }))}></span>
                <span>Mirror-ASIA-Pacific</span>
                <span className={styles['mirrorHealth']}>98.9%</span>
              </div>
            </div>
          </div>

          <div className={styles['mirrorCard']}>
            <h4>Backup Mirrors</h4>
            <div className={styles['mirrorList']}>
              <div className={styles['mirrorItem']}>
                <span className={cn(mirrorStatusVariants({ status: 'online' }))}></span>
                <span>Backup-US-West</span>
                <span className={styles['mirrorHealth']}>99.2%</span>
              </div>
              <div className={styles['mirrorItem']}>
                <span className={cn(mirrorStatusVariants({ status: 'warning' }))}></span>
                <span>Backup-EU-North</span>
                <span className={styles['mirrorHealth']}>95.1%</span>
              </div>
              <div className={styles['mirrorItem']}>
                <span className={cn(mirrorStatusVariants({ status: 'online' }))}></span>
                <span>Backup-ASIA-South</span>
                <span className={styles['mirrorHealth']}>97.8%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
