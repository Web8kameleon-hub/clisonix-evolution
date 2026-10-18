'use client';

import * as React from 'react';
import { 
  getASIStatus, 
  getASIModules, 
  getASISystemHealth,
  getASIMemory,
  activateASI,
  deactivateASI,
  activateASIModule,
  deactivateASIModule,
  addASIStatusListener,
  removeASIStatusListener,
  processASIRequest,
  type ASIStatus,
  type ASIModule,
  type ASIMemory
} from '../../lib/ASICore';
import styles from './asi-dashboard.module.css';

interface SystemAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  title: string;
  message: string;
  timestamp: number;
}

interface PerformanceMetrics {
  cpu: number;
  memory: number;
  network: number;
  responseTime: number;
  throughput: number;
  uptime: number;
}

export default function ASIDashboard() {
  // State Management
  const [asiStatus, setASIStatus] = React.useState<ASIStatus | null>(null);
  const [asiModules, setASIModules] = React.useState<ASIModule[]>([]);
  const [asiMemory, setASIMemory] = React.useState<ASIMemory | null>(null);
  const [systemHealth, setSystemHealth] = React.useState<any>(null);
  const [alerts, setAlerts] = React.useState<SystemAlert[]>([]);
  const [selectedLanguage, setSelectedLanguage] = React.useState<'sq' | 'en'>('sq');
  const [activeView, setActiveView] = React.useState<'overview' | 'modules' | 'memory' | 'health'>('overview');
  const [testQuery, setTestQuery] = React.useState('');
  const [isTestingASI, setIsTestingASI] = React.useState(false);
  const [performanceMetrics, setPerformanceMetrics] = React.useState<PerformanceMetrics>({
    cpu: 0,
    memory: 0,
    network: 0,
    responseTime: 0,
    throughput: 0,
    uptime: 0
  });

  // Real-time system monitoring
  React.useEffect(() => {
    const statusListener = (status: ASIStatus) => {
      setASIStatus(status);
    };

    // Initialize system state
    const initializeSystem = () => {
      setASIStatus(getASIStatus());
      setASIModules(getASIModules());
      setASIMemory(getASIMemory());
      setSystemHealth(getASISystemHealth());
    };

    initializeSystem();
    addASIStatusListener(statusListener);

    // Performance monitoring
    const performanceInterval = setInterval(() => {
      // Simulate real performance metrics
      setPerformanceMetrics(prev => ({
        cpu: Math.random() * 100,
        memory: Math.random() * 100,
        network: Math.random() * 1000,
        responseTime: Math.random() * 500 + 100,
        throughput: Math.random() * 1000 + 500,
        uptime: Date.now() - (asiStatus?.timestamp || Date.now())
      }));
    }, 2000);

    // System health check
    const healthInterval = setInterval(() => {
      setSystemHealth(getASISystemHealth());
      setASIMemory(getASIMemory());
    }, 5000);

    return () => {
      removeASIStatusListener(statusListener);
      clearInterval(performanceInterval);
      clearInterval(healthInterval);
    };
  }, [asiStatus?.timestamp]);

  // Handle System Control
  const handleSystemToggle = () => {
    if (asiStatus?.isActive) {
      deactivateASI();
      addAlert('warning', 'Sistem ndërprerë', 'ASI sistemi është çaktivizuar');
    } else {
      activateASI();
      addAlert('success', 'Sistem aktivizuar', 'ASI sistemi është aktivizuar me sukses');
    }
  };

  const handleModuleToggle = (moduleId: string) => {
    const module = asiModules.find(m => m.id === moduleId);
    if (!module) return;

    if (module.status === 'active') {
      deactivateASIModule(moduleId);
      addAlert('info', 'Modul çaktivizuar', `${module.nameAlbanian} është çaktivizuar`);
    } else {
      activateASIModule(moduleId);
      addAlert('success', 'Modul aktivizuar', `${module.nameAlbanian} është aktivizuar`);
    }

    // Refresh modules
    setTimeout(() => {
      setASIModules(getASIModules());
    }, 100);
  };

  const handleTestASI = async () => {
    if (!testQuery.trim()) return;

    setIsTestingASI(true);
    try {
      const response = await processASIRequest(testQuery);
      addAlert('success', 'Test i suksesshëm', `ASI përgjigja: ${response.text.substring(0, 100)}...`);
      setTestQuery('');
    } catch (error) {
      addAlert('error', 'Test dështoi', 'Ndodhi një gabim gjatë testimit të ASI');
    } finally {
      setIsTestingASI(false);
    }
  };

  const addAlert = (type: SystemAlert['type'], title: string, message: string) => {
    const alert: SystemAlert = {
      id: `alert_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      title,
      message,
      timestamp: Date.now()
    };

    setAlerts(prev => [alert, ...prev.slice(0, 9)]); // Keep only 10 latest alerts

    // Auto-remove after 5 seconds
    setTimeout(() => {
      setAlerts(prev => prev.filter(a => a.id !== alert.id));
    }, 5000);
  };

  const formatUptime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  };

  const t = (key: string) => {
    const translations: Record<string, Record<string, string>> = {
      sq: {
        title: '🇦🇱 ASI Dashboard - Albanian System Intelligence',
        subtitle: 'Paneli i kontrollit për ASI (Albanian System Intelligence)',
        systemStatus: 'Statusi i Sistemit',
        active: 'AKTIV',
        inactive: 'JOAKTIV',
        overview: 'Pamje e Përgjithshme',
        modules: 'Modulet',
        memory: 'Memoria',
        health: 'Shëndeti',
        toggleSystem: 'Ndrysho Sistemin',
        testASI: 'Testo ASI',
        performanceMetrics: 'Metrikat e Performancës',
        systemAlerts: 'Sinjalizimet e Sistemit',
        moduleManagement: 'Menaxhimi i Moduleve',
        memoryAnalysis: 'Analiza e Memorias',
        healthMonitoring: 'Monitorimi i Shëndetit'
      },
      en: {
        title: '🇦🇱 ASI Dashboard - Albanian System Intelligence',
        subtitle: 'Control panel for ASI (Albanian System Intelligence)',
        systemStatus: 'System Status',
        active: 'ACTIVE',
        inactive: 'INACTIVE',
        overview: 'Overview',
        modules: 'Modules',
        memory: 'Memory',
        health: 'Health',
        toggleSystem: 'Toggle System',
        testASI: 'Test ASI',
        performanceMetrics: 'Performance Metrics',
        systemAlerts: 'System Alerts',
        moduleManagement: 'Module Management',
        memoryAnalysis: 'Memory Analysis',
        healthMonitoring: 'Health Monitoring'
      }
    };
    return translations[selectedLanguage]?.[key] || key;
  };

  return (
    <div className={styles['container']}>
      {/* Header */}
      <header className={styles['header']}>
        <div className={styles['headerContent']}>
          <div className={styles['titleSection']}>
            <h1 className={styles['title']}>{t('title')}</h1>
            <p className={styles['subtitle']}>{t('subtitle')}</p>
          </div>

          <div className={styles['headerControls']}>
            {/* Language Toggle */}
            <div className={styles['languageToggle']}>
              <button 
                className={`${styles['langBtn']} ${selectedLanguage === 'sq' ? styles['active'] : ''}`}
                onClick={() => setSelectedLanguage('sq')}
              >
                🇦🇱 SQ
              </button>
              <button 
                className={`${styles['langBtn']} ${selectedLanguage === 'en' ? styles['active'] : ''}`}
                onClick={() => setSelectedLanguage('en')}
              >
                🇬🇧 EN
              </button>
            </div>

            {/* System Status */}
            <div className={styles['systemStatus']}>
              <div className={`${styles['statusIndicator']} ${asiStatus?.isActive ? styles['active'] : styles['inactive']}`}>
                <div className={styles['statusDot']}></div>
                <span className={styles['statusText']}>
                  ASI {asiStatus?.isActive ? t('active') : t('inactive')}
                </span>
              </div>
              <button 
                className={styles['toggleButton']}
                onClick={handleSystemToggle}
              >
                {t('toggleSystem')}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className={styles['navigation']}>
        <div className={styles['navContainer']}>
          {(['overview', 'modules', 'memory', 'health'] as const).map((view) => (
            <button
              key={view}
              className={`${styles['navButton']} ${activeView === view ? styles['active'] : ''}`}
              onClick={() => setActiveView(view)}
            >
              {view === 'overview' && '📊'}
              {view === 'modules' && '🧠'}
              {view === 'memory' && '💾'}
              {view === 'health' && '🔍'}
              <span>{t(view)}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content */}
      <main className={styles['mainContent']}>
        {/* Alerts Bar */}
        {alerts.length > 0 && (
          <div className={styles['alertsBar']}>
            {alerts.slice(0, 3).map((alert) => (
              <div key={alert.id} className={`${styles['alert']} ${styles[alert.type]}`}>
                <div className={styles['alertContent']}>
                  <strong>{alert.title}</strong>
                  <span>{alert.message}</span>
                </div>
                <button 
                  className={styles['alertClose']}
                  onClick={() => setAlerts(prev => prev.filter(a => a.id !== alert.id))}
                >
                  ✕
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Overview View */}
        {activeView === 'overview' && (
          <div className={styles['overviewGrid']}>
            {/* Performance Metrics */}
            <div className={styles['metricsCard']}>
              <h3 className={styles['cardTitle']}>{t('performanceMetrics')}</h3>
              <div className={styles['metricsGrid']}>
                <div className={styles['metric']}>
                  <div className={styles['metricIcon']}>🖥️</div>
                  <div className={styles['metricData']}>
                    <span className={styles['metricValue']}>{performanceMetrics.cpu.toFixed(1)}%</span>
                    <span className={styles['metricLabel']}>CPU</span>
                  </div>
                </div>
                <div className={styles['metric']}>
                  <div className={styles['metricIcon']}>🧠</div>
                  <div className={styles['metricData']}>
                    <span className={styles['metricValue']}>{performanceMetrics.memory.toFixed(1)}%</span>
                    <span className={styles['metricLabel']}>Memory</span>
                  </div>
                </div>
                <div className={styles['metric']}>
                  <div className={styles['metricIcon']}>🌐</div>
                  <div className={styles['metricData']}>
                    <span className={styles['metricValue']}>{performanceMetrics.network.toFixed(0)}ms</span>
                    <span className={styles['metricLabel']}>Network</span>
                  </div>
                </div>
                <div className={styles['metric']}>
                  <div className={styles['metricIcon']}>⚡</div>
                  <div className={styles['metricData']}>
                    <span className={styles['metricValue']}>{performanceMetrics.responseTime.toFixed(0)}ms</span>
                    <span className={styles['metricLabel']}>Response</span>
                  </div>
                </div>
                <div className={styles['metric']}>
                  <div className={styles['metricIcon']}>📊</div>
                  <div className={styles['metricData']}>
                    <span className={styles['metricValue']}>{performanceMetrics.throughput.toFixed(0)}</span>
                    <span className={styles['metricLabel']}>Throughput</span>
                  </div>
                </div>
                <div className={styles['metric']}>
                  <div className={styles['metricIcon']}>⏱️</div>
                  <div className={styles['metricData']}>
                    <span className={styles['metricValue']}>{formatUptime(performanceMetrics.uptime)}</span>
                    <span className={styles['metricLabel']}>Uptime</span>
                  </div>
                </div>
              </div>
            </div>

            {/* ASI Test Console */}
            <div className={styles['testCard']}>
              <h3 className={styles['cardTitle']}>{t('testASI')}</h3>
              <div className={styles['testConsole']}>
                <textarea
                  className={styles['testInput']}
                  value={testQuery}
                  onChange={(e) => setTestQuery(e.target.value)}
                  placeholder={selectedLanguage === 'sq' 
                    ? "Shkruani një pyetje për të testuar ASI..."
                    : "Write a question to test ASI..."
                  }
                  rows={3}
                />
                <button
                  className={styles['testButton']}
                  onClick={handleTestASI}
                  disabled={isTestingASI || !testQuery.trim()}
                >
                  {isTestingASI ? '🔄 Duke testuar...' : '🚀 Testo'}
                </button>
              </div>
            </div>

            {/* Quick Stats */}
            <div className={styles['statsCard']}>
              <h3 className={styles['cardTitle']}>📈 Statistikat e Shpejta</h3>
              <div className={styles['statsList']}>
                <div className={styles['statItem']}>
                  <span className={styles['statLabel']}>Module Aktive:</span>
                  <span className={styles['statValue']}>{asiStatus?.activeModules.length || 0}/4</span>
                </div>
                <div className={styles['statItem']}>
                  <span className={styles['statLabel']}>Processed Total:</span>
                  <span className={styles['statValue']}>{asiMemory?.processing_stats.total_processed || 0}</span>
                </div>
                <div className={styles['statItem']}>
                  <span className={styles['statLabel']}>Accuracy Rate:</span>
                  <span className={styles['statValue']}>{((asiMemory?.processing_stats.accuracy_rate || 0) * 100).toFixed(1)}%</span>
                </div>
                <div className={styles['statItem']}>
                  <span className={styles['statLabel']}>Language Dist:</span>
                  <span className={styles['statValue']}>
                    SQ: {asiMemory?.processing_stats.language_distribution?.sq || 0} | 
                    EN: {asiMemory?.processing_stats.language_distribution?.en || 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Modules View */}
        {activeView === 'modules' && (
          <div className={styles['modulesView']}>
            <h3 className={styles['viewTitle']}>{t('moduleManagement')}</h3>
            <div className={styles['modulesList']}>
              {asiModules.map((module) => (
                <div key={module.id} className={`${styles['moduleCard']} ${styles[module.status]}`}>
                  <div className={styles['moduleHeader']}>
                    <div className={styles['moduleInfo']}>
                      <h4 className={styles['moduleTitle']}>
                        {selectedLanguage === 'sq' ? module.nameAlbanian : module.name}
                      </h4>
                      <p className={styles['moduleDescription']}>
                        {selectedLanguage === 'sq' ? module.descriptionAlbanian : module.description}
                      </p>
                      <div className={styles['moduleType']}>
                        Type: {module.type} | Status: {module.status}
                      </div>
                    </div>
                    <div className={styles['moduleControls']}>
                      <button
                        className={`${styles['moduleToggle']} ${styles[module.status]}`}
                        onClick={() => handleModuleToggle(module.id)}
                      >
                        {module.status === 'active' ? '🟢 ON' : '🔴 OFF'}
                      </button>
                    </div>
                  </div>
                  <div className={styles['moduleCapabilities']}>
                    <strong>Capabilities:</strong>
                    <div className={styles['capabilityTags']}>
                      {module.capabilities.map((capability, index) => (
                        <span key={index} className={styles['capabilityTag']}>
                          {capability}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Memory View */}
        {activeView === 'memory' && asiMemory && (
          <div className={styles['memoryView']}>
            <h3 className={styles['viewTitle']}>{t('memoryAnalysis')}</h3>
            <div className={styles['memoryGrid']}>
              <div className={styles['memoryCard']}>
                <h4>📊 Processing Statistics</h4>
                <div className={styles['memoryStats']}>
                  <div>Total Processed: {asiMemory.processing_stats.total_processed}</div>
                  <div>Avg Response Time: {asiMemory.processing_stats.avg_response_time}ms</div>
                  <div>Accuracy Rate: {(asiMemory.processing_stats.accuracy_rate * 100).toFixed(2)}%</div>
                </div>
              </div>
              
              <div className={styles['memoryCard']}>
                <h4>🌐 Language Distribution</h4>
                <div className={styles['languageChart']}>
                  <div className={styles['langStat']}>
                    <span>🇦🇱 Albanian:</span>
                    <span>{asiMemory.processing_stats.language_distribution?.sq || 0}</span>
                  </div>
                  <div className={styles['langStat']}>
                    <span>🇬🇧 English:</span>
                    <span>{asiMemory.processing_stats.language_distribution?.en || 0}</span>
                  </div>
                  <div className={styles['langStat']}>
                    <span>🌍 Mixed:</span>
                    <span>{asiMemory.processing_stats.language_distribution?.mixed || 0}</span>
                  </div>
                </div>
              </div>

              <div className={styles['memoryCard']}>
                <h4>💭 Recent Responses</h4>
                <div className={styles['recentResponses']}>
                  {asiMemory.responses.slice(0, 5).map((response, index) => (
                    <div key={response.id} className={styles['responseItem']}>
                      <div className={styles['responseHeader']}>
                        <span className={styles['responseTime']}>
                          {new Date(response.timestamp).toLocaleTimeString()}
                        </span>
                        <span className={styles['responseLang']}>
                          {response.language === 'sq' ? '🇦🇱' : '🇬🇧'}
                        </span>
                      </div>
                      <div className={styles['responseText']}>
                        {response.text.substring(0, 100)}...
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Health View */}
        {activeView === 'health' && systemHealth && (
          <div className={styles['healthView']}>
            <h3 className={styles['viewTitle']}>{t('healthMonitoring')}</h3>
            <div className={styles['healthGrid']}>
              <div className={styles['healthCard']}>
                <h4>🎯 System Health Status</h4>
                <div className={`${styles['healthStatus']} ${styles[systemHealth.status]}`}>
                  {systemHealth.status.toUpperCase()}
                </div>
                <div className={styles['healthMetrics']}>
                  <div>Uptime: {formatUptime(systemHealth.metrics.uptime)}</div>
                  <div>Response Time: {systemHealth.metrics.response_time.toFixed(2)}ms</div>
                  <div>Accuracy: {(systemHealth.metrics.accuracy * 100).toFixed(1)}%</div>
                </div>
              </div>

              <div className={styles['healthCard']}>
                <h4>🔧 Module Health</h4>
                <div className={styles['moduleHealth']}>
                  {Object.entries(systemHealth.metrics.module_health).map(([moduleId, status]) => (
                    <div key={moduleId} className={styles['moduleHealthItem']}>
                      <span className={styles['moduleHealthName']}>
                        {asiModules.find(m => m.id === moduleId)?.nameAlbanian || moduleId}
                      </span>
                      <span className={`${styles['moduleHealthStatus']} ${styles[status as string]}`}>
                        {status === 'ok' ? '✅' : status === 'warning' ? '⚠️' : '❌'}
                        {(status as string).toUpperCase()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
