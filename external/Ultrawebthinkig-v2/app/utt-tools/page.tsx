'use client';

import { useState, useEffect } from 'react';
import styles from './utt.module.css';

interface TechTool {
  id: string;
  name: string;
  category: 'network' | 'security' | 'monitoring' | 'analysis' | 'automation' | 'development';
  description: string;
  status: 'active' | 'idle' | 'processing' | 'error';
  lastUsed: string;
  usage: number;
  performance: number;
  icon: string;
  features: string[];
}

interface SystemStatus {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  temperature: number;
  uptime: string;
}

interface UTTMetrics {
  totalTools: number;
  activeTools: number;
  systemLoad: number;
  totalUsage: number;
  averagePerformance: number;
  criticalAlerts: number;
}

export default function UTTDashboard() {
  const [tools, setTools] = useState<TechTool[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
    temperature: 0,
    uptime: ''
  });
  const [metrics, setMetrics] = useState<UTTMetrics>({
    totalTools: 0,
    activeTools: 0,
    systemLoad: 0,
    totalUsage: 0,
    averagePerformance: 0,
    criticalAlerts: 0
  });
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedTool, setSelectedTool] = useState<TechTool | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchUTTData();
    const interval = setInterval(fetchUTTData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchUTTData = async () => {
    setIsLoading(true);
    try {
      // Simulate Ultra Tech Tools data
      const mockTools: TechTool[] = [
        {
          id: 'network-scanner',
          name: 'Network Discovery Scanner',
          category: 'network',
          description: 'Advanced network topology discovery and port scanning',
          status: 'active',
          lastUsed: new Date(Date.now() - 120000).toISOString(),
          usage: 87,
          performance: 94,
          icon: '🔍',
          features: ['Port Scanning', 'Service Detection', 'OS Fingerprinting', 'Vulnerability Assessment']
        },
        {
          id: 'security-analyzer',
          name: 'Security Vulnerability Analyzer',
          category: 'security',
          description: 'Real-time security assessment and threat detection',
          status: 'processing',
          lastUsed: new Date().toISOString(),
          usage: 76,
          performance: 91,
          icon: '🛡️',
          features: ['Vulnerability Scanning', 'Threat Detection', 'Risk Assessment', 'Compliance Checking']
        },
        {
          id: 'system-monitor',
          name: 'Advanced System Monitor',
          category: 'monitoring',
          description: 'Comprehensive system performance monitoring',
          status: 'active',
          lastUsed: new Date(Date.now() - 30000).toISOString(),
          usage: 92,
          performance: 96,
          icon: '📊',
          features: ['Real-time Metrics', 'Performance Graphs', 'Alert System', 'Resource Tracking']
        },
        {
          id: 'log-analyzer',
          name: 'Intelligent Log Analyzer',
          category: 'analysis',
          description: 'AI-powered log analysis and pattern recognition',
          status: 'active',
          lastUsed: new Date(Date.now() - 60000).toISOString(),
          usage: 68,
          performance: 88,
          icon: '📝',
          features: ['Pattern Recognition', 'Anomaly Detection', 'Trend Analysis', 'Automated Reporting']
        },
        {
          id: 'automation-engine',
          name: 'Task Automation Engine',
          category: 'automation',
          description: 'Intelligent workflow automation and orchestration',
          status: 'idle',
          lastUsed: new Date(Date.now() - 300000).toISOString(),
          usage: 45,
          performance: 85,
          icon: '⚙️',
          features: ['Workflow Automation', 'Task Scheduling', 'Process Orchestration', 'Event Triggers']
        },
        {
          id: 'code-analyzer',
          name: 'Code Quality Analyzer',
          category: 'development',
          description: 'Advanced static code analysis and quality metrics',
          status: 'active',
          lastUsed: new Date(Date.now() - 90000).toISOString(),
          usage: 72,
          performance: 89,
          icon: '💻',
          features: ['Static Analysis', 'Code Metrics', 'Security Scanning', 'Best Practices']
        },
        {
          id: 'network-sniffer',
          name: 'Network Traffic Sniffer',
          category: 'network',
          description: 'Deep packet inspection and traffic analysis',
          status: 'active',
          lastUsed: new Date(Date.now() - 45000).toISOString(),
          usage: 83,
          performance: 92,
          icon: '🌐',
          features: ['Packet Capture', 'Protocol Analysis', 'Traffic Monitoring', 'Bandwidth Analysis']
        },
        {
          id: 'crypto-toolkit',
          name: 'Cryptographic Toolkit',
          category: 'security',
          description: 'Advanced encryption, hashing, and cryptographic operations',
          status: 'idle',
          lastUsed: new Date(Date.now() - 600000).toISOString(),
          usage: 31,
          performance: 95,
          icon: '🔐',
          features: ['Encryption/Decryption', 'Hash Functions', 'Digital Signatures', 'Key Management']
        },
        {
          id: 'database-optimizer',
          name: 'Database Performance Optimizer',
          category: 'analysis',
          description: 'Database query optimization and performance tuning',
          status: 'processing',
          lastUsed: new Date(Date.now() - 15000).toISOString(),
          usage: 89,
          performance: 87,
          icon: '🗄️',
          features: ['Query Optimization', 'Index Analysis', 'Performance Tuning', 'Resource Monitoring']
        },
        {
          id: 'ai-assistant',
          name: 'AI Development Assistant',
          category: 'development',
          description: 'AI-powered code generation and development assistance',
          status: 'error',
          lastUsed: new Date(Date.now() - 900000).toISOString(),
          usage: 15,
          performance: 65,
          icon: '🤖',
          features: ['Code Generation', 'Bug Detection', 'Documentation', 'Refactoring Suggestions']
        }
      ];

      const mockSystemStatus: SystemStatus = {
        cpu: Math.floor(Math.random() * 30) + 45, // 45-75%
        memory: Math.floor(Math.random() * 25) + 60, // 60-85%
        disk: Math.floor(Math.random() * 20) + 35, // 35-55%
        network: Math.floor(Math.random() * 40) + 30, // 30-70%
        temperature: Math.floor(Math.random() * 15) + 45, // 45-60°C
        uptime: '7d 14h 23m'
      };

      const activeTools = mockTools.filter(t => t.status === 'active' || t.status === 'processing').length;
      const totalUsage = mockTools.reduce((sum, t) => sum + t.usage, 0);
      const avgPerformance = mockTools.reduce((sum, t) => sum + t.performance, 0) / mockTools.length;
      const criticalAlerts = mockTools.filter(t => t.status === 'error').length;

      const mockMetrics: UTTMetrics = {
        totalTools: mockTools.length,
        activeTools,
        systemLoad: Math.max(mockSystemStatus.cpu, mockSystemStatus.memory),
        totalUsage: Math.round(totalUsage / mockTools.length),
        averagePerformance: Math.round(avgPerformance),
        criticalAlerts
      };

      setTools(mockTools);
      setSystemStatus(mockSystemStatus);
      setMetrics(mockMetrics);
    } catch (error) {
      console.error('Error fetching UTT data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#00ff88';
      case 'processing': return '#00d4ff';
      case 'idle': return '#ffa502';
      case 'error': return '#ff6b6b';
      default: return '#6c757d';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'network': return '#00d4ff';
      case 'security': return '#ff6b6b';
      case 'monitoring': return '#00ff88';
      case 'analysis': return '#ffa502';
      case 'automation': return '#9b59b6';
      case 'development': return '#00ff88';
      default: return '#6c757d';
    }
  };

  const getPerformanceClass = (performance: number) => {
    if (performance >= 90) return 'excellent';
    if (performance >= 80) return 'good';
    if (performance >= 70) return 'fair';
    return 'poor';
  };

  const getSystemStatusClass = (value: number, type: string) => {
    const thresholds = {
      cpu: { warning: 70, critical: 85 },
      memory: { warning: 80, critical: 90 },
      disk: { warning: 75, critical: 90 },
      network: { warning: 80, critical: 95 },
      temperature: { warning: 65, critical: 80 }
    };

    const threshold = thresholds[type as keyof typeof thresholds];
    if (value >= threshold.critical) return 'critical';
    if (value >= threshold.warning) return 'warning';
    return 'normal';
  };

  const formatLastUsed = (timestamp: string) => {
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

  const filteredTools = selectedCategory === 'all' 
    ? tools 
    : tools.filter(tool => tool.category === selectedCategory);

  return (
    <div className={styles['container']}>
      <div className={styles['header']}>
        <h1 className={styles['title']}>🛠️ Ultra Tech Tools (UTT)</h1>
        <p className={styles['subtitle']}>
          Advanced technical tools suite for system administration and development
        </p>
        <div className={styles['last-updated']}>
          Last updated: {new Date().toLocaleTimeString()}
          {isLoading && <span className={styles['loading']}>⟳</span>}
        </div>
      </div>

      {/* System Status Overview */}
      <div className={styles['system-section']}>
        <h2 className={styles['section-title']}>🖥️ System Status</h2>
        <div className={styles['system-grid']}>
          <div className={styles['system-card']}>
            <div className={styles['system-icon']}>🧠</div>
            <div className={styles['system-data']}>
              <div className={styles['system-label']}>CPU Usage</div>
              <div className={`${styles['system-value']} ${styles[getSystemStatusClass(systemStatus.cpu, 'cpu')]}`}>
                {systemStatus.cpu}%
              </div>
              <div className={styles['system-bar']}>
                <div 
                  className={`${styles['system-bar-fill']} ${styles[getSystemStatusClass(systemStatus.cpu, 'cpu')]}`}
                  style={{ width: `${systemStatus.cpu}%` }}
                />
              </div>
            </div>
          </div>
          
          <div className={styles['system-card']}>
            <div className={styles['system-icon']}>💾</div>
            <div className={styles['system-data']}>
              <div className={styles['system-label']}>Memory Usage</div>
              <div className={`${styles['system-value']} ${styles[getSystemStatusClass(systemStatus.memory, 'memory')]}`}>
                {systemStatus.memory}%
              </div>
              <div className={styles['system-bar']}>
                <div 
                  className={`${styles['system-bar-fill']} ${styles[getSystemStatusClass(systemStatus.memory, 'memory')]}`}
                  style={{ width: `${systemStatus.memory}%` }}
                />
              </div>
            </div>
          </div>
          
          <div className={styles['system-card']}>
            <div className={styles['system-icon']}>💽</div>
            <div className={styles['system-data']}>
              <div className={styles['system-label']}>Disk Usage</div>
              <div className={`${styles['system-value']} ${styles[getSystemStatusClass(systemStatus.disk, 'disk')]}`}>
                {systemStatus.disk}%
              </div>
              <div className={styles['system-bar']}>
                <div 
                  className={`${styles['system-bar-fill']} ${styles[getSystemStatusClass(systemStatus.disk, 'disk')]}`}
                  style={{ width: `${systemStatus.disk}%` }}
                />
              </div>
            </div>
          </div>
          
          <div className={styles['system-card']}>
            <div className={styles['system-icon']}>🌐</div>
            <div className={styles['system-data']}>
              <div className={styles['system-label']}>Network Load</div>
              <div className={`${styles['system-value']} ${styles[getSystemStatusClass(systemStatus.network, 'network')]}`}>
                {systemStatus.network}%
              </div>
              <div className={styles['system-bar']}>
                <div 
                  className={`${styles['system-bar-fill']} ${styles[getSystemStatusClass(systemStatus.network, 'network')]}`}
                  style={{ width: `${systemStatus.network}%` }}
                />
              </div>
            </div>
          </div>
          
          <div className={styles['system-card']}>
            <div className={styles['system-icon']}>🌡️</div>
            <div className={styles['system-data']}>
              <div className={styles['system-label']}>Temperature</div>
              <div className={`${styles['system-value']} ${styles[getSystemStatusClass(systemStatus.temperature, 'temperature')]}`}>
                {systemStatus.temperature}°C
              </div>
              <div className={styles['system-info']}>
                Uptime: {systemStatus.uptime}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metrics Overview */}
      <div className={styles['metrics-grid']}>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>🛠️</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.totalTools}</div>
            <div className={styles['metric-label']}>Total Tools</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>⚡</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.activeTools}</div>
            <div className={styles['metric-label']}>Active Tools</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>📊</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.systemLoad}%</div>
            <div className={styles['metric-label']}>System Load</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>📈</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.totalUsage}%</div>
            <div className={styles['metric-label']}>Avg Usage</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>🎯</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.averagePerformance}%</div>
            <div className={styles['metric-label']}>Performance</div>
          </div>
        </div>
        <div className={styles['metric-card']}>
          <div className={styles['metric-icon']}>🚨</div>
          <div className={styles['metric-data']}>
            <div className={styles['metric-value']}>{metrics.criticalAlerts}</div>
            <div className={styles['metric-label']}>Critical Alerts</div>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className={styles['filter-section']}>
        <h2 className={styles['section-title']}>🗂️ Tool Categories</h2>
        <div className={styles['category-filters']}>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'all' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('all')}
          >
            🌐 All Tools ({tools.length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'network' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('network')}
          >
            🔗 Network ({tools.filter(t => t.category === 'network').length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'security' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('security')}
          >
            🛡️ Security ({tools.filter(t => t.category === 'security').length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'monitoring' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('monitoring')}
          >
            📊 Monitoring ({tools.filter(t => t.category === 'monitoring').length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'analysis' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('analysis')}
          >
            🔍 Analysis ({tools.filter(t => t.category === 'analysis').length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'automation' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('automation')}
          >
            ⚙️ Automation ({tools.filter(t => t.category === 'automation').length})
          </button>
          <button 
            className={`${styles['category-button']} ${selectedCategory === 'development' ? styles['active'] : ''}`}
            onClick={() => setSelectedCategory('development')}
          >
            💻 Development ({tools.filter(t => t.category === 'development').length})
          </button>
        </div>
      </div>

      {/* Tools Grid */}
      <div className={styles['tools-section']}>
        <h2 className={styles['section-title']}>
          🔧 Available Tools ({filteredTools.length})
        </h2>
        <div className={styles['tools-grid']}>
          {filteredTools.map((tool) => (
            <div 
              key={tool.id} 
              className={styles['tool-card']}
              onClick={() => setSelectedTool(tool)}
            >
              <div className={styles['tool-header']}>
                <div className={styles['tool-icon-title']}>
                  <span className={styles['tool-icon']}>{tool.icon}</span>
                  <div className={styles['tool-title']}>{tool.name}</div>
                </div>
                <div 
                  className={styles['tool-status']}
                  style={{ color: getStatusColor(tool.status) }}
                >
                  ● {tool.status.toUpperCase()}
                </div>
              </div>
              
              <div className={styles['tool-category']} style={{ color: getCategoryColor(tool.category) }}>
                {tool.category.toUpperCase()}
              </div>
              
              <div className={styles['tool-description']}>{tool.description}</div>
              
              <div className={styles['tool-metrics']}>
                <div className={styles['tool-metric']}>
                  <span>Usage:</span>
                  <div className={styles['usage-bar']}>
                    <div 
                      className={styles['usage-fill']}
                      style={{ width: `${tool.usage}%` }}
                    />
                    <span className={styles['usage-text']}>{tool.usage}%</span>
                  </div>
                </div>
                <div className={styles['tool-metric']}>
                  <span>Performance:</span>
                  <span className={`${styles['performance-value']} ${styles[getPerformanceClass(tool.performance)]}`}>
                    {tool.performance}%
                  </span>
                </div>
                <div className={styles['tool-metric']}>
                  <span>Last Used:</span>
                  <span>{formatLastUsed(tool.lastUsed)}</span>
                </div>
              </div>
              
              <div className={styles['tool-features']}>
                <div className={styles['features-label']}>Features:</div>
                <div className={styles['features-count']}>
                  {tool.features.length} available
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tool Details Modal */}
      {selectedTool && (
        <div className={styles['modal-overlay']} onClick={() => setSelectedTool(null)}>
          <div className={styles['modal-content']} onClick={(e) => e.stopPropagation()}>
            <div className={styles['modal-header']}>
              <h3 className={styles['modal-title']}>
                {selectedTool.icon} {selectedTool.name}
              </h3>
              <button 
                className={styles['modal-close']}
                onClick={() => setSelectedTool(null)}
              >
                ✕
              </button>
            </div>
            
            <div className={styles['modal-body']}>
              <div className={styles['tool-details']}>
                <div className={styles['detail-section']}>
                  <h4>Tool Information</h4>
                  <div className={styles['detail-item']}>
                    <span>Category:</span>
                    <span style={{ color: getCategoryColor(selectedTool.category) }}>
                      {selectedTool.category.toUpperCase()}
                    </span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Status:</span>
                    <span style={{ color: getStatusColor(selectedTool.status) }}>
                      {selectedTool.status.toUpperCase()}
                    </span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Description:</span>
                    <span>{selectedTool.description}</span>
                  </div>
                </div>
                
                <div className={styles['detail-section']}>
                  <h4>Performance Metrics</h4>
                  <div className={styles['detail-item']}>
                    <span>Usage:</span>
                    <span>{selectedTool.usage}%</span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Performance:</span>
                    <span className={styles[getPerformanceClass(selectedTool.performance)]}>
                      {selectedTool.performance}%
                    </span>
                  </div>
                  <div className={styles['detail-item']}>
                    <span>Last Used:</span>
                    <span>{new Date(selectedTool.lastUsed).toLocaleString()}</span>
                  </div>
                </div>
                
                <div className={styles['detail-section']}>
                  <h4>Available Features</h4>
                  <div className={styles['features-list']}>
                    {selectedTool.features.map((feature, index) => (
                      <div key={index} className={styles['feature-item']}>
                        ✓ {feature}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Controls */}
      <div className={styles['controls']}>
        <button 
          className={styles['refresh-button']}
          onClick={fetchUTTData}
          disabled={isLoading}
        >
          {isLoading ? '⟳ Refreshing...' : '🔄 Refresh Tools'}
        </button>
      </div>
    </div>
  );
}
