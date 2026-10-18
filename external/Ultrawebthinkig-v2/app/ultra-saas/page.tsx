'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import styles from './ultra-saas.module.css';

// Module Categories
interface ModuleCategory {
  id: string;
  title: string;
  icon: string;
  modules: ModuleItem[];
  color: string;
}

interface ModuleItem {
  id: string;
  title: string;
  path: string;
  description: string;
  status: 'active' | 'beta' | 'new';
  icon: string;
}

const moduleCategories: ModuleCategory[] = [
  {
    id: 'agi',
    title: 'AGI System',
    icon: '🧠',
    color: '#00ff88',
    modules: [
      { id: 'agi-core', title: 'AGI Core Ultra', path: '/agi', description: 'Advanced General Intelligence Core', status: 'active', icon: '🧠' },
      { id: 'agi-tunnel', title: 'AGI Tunnel', path: '/agi-tunnel', description: 'Neural Processing Tunnel', status: 'active', icon: '🌀' },
      { id: 'agi-med', title: 'Medical AGI', path: '/agimed-professional', description: 'Professional Medical AI', status: 'active', icon: '🏥' },
      { id: 'agi-eco', title: 'Eco AGI', path: '/agixeco-demo', description: 'Environmental Intelligence', status: 'active', icon: '🌿' },
      { id: 'agi-bio', title: 'Bio Nature AGI', path: '/agixbionature-demo', description: 'Biological Systems AI', status: 'active', icon: '🦋' },
      { id: 'agi-alba', title: 'Alba Med AGI', path: '/albamed-demo', description: 'Albanian Medical System', status: 'active', icon: '🇦🇱' },
      { id: 'ai-manager', title: 'AI Manager Dashboard', path: '/ai-manager', description: 'Neural Network Communication Interface', status: 'new', icon: '🤖' },
      { id: 'asi-dashboard', title: 'ASI Dashboard', path: '/asi-dashboard', description: 'Albanian System Intelligence Control Panel', status: 'new', icon: '🎛️' }
    ]
  },
  {
    id: 'asi',
    title: 'ASI (Albanian System Intelligence)',
    icon: '🇦🇱',
    color: '#ff6b6b',
    modules: [
      { id: 'asi-dashboard', title: 'ASI Dashboard', path: '/ultra-saas/asi-dashboard', description: 'Complete ASI Dashboard with WebSocket + 60+ API endpoints + Real-time Analytics', status: 'active', icon: '🎯' },
      { id: 'asi-core', title: 'ASI Core Engine', path: '/asi-dashboard', description: 'Albanian System Intelligence Core', status: 'active', icon: '🧠' },
      { id: 'asi-medical', title: 'ASI Medical', path: '/albamed-demo', description: 'Albanian Medical Intelligence', status: 'active', icon: '🏥' },
      { id: 'asi-cultural', title: 'ASI Cultural', path: '/asi-dashboard', description: 'Albanian Cultural Intelligence', status: 'active', icon: '🏛️' },
      { id: 'asi-technical', title: 'ASI Technical', path: '/asi-dashboard', description: 'Albanian Technical Intelligence', status: 'active', icon: '⚙️' }
    ]
  },
  {
    id: 'chat',
    title: 'Chat Systems',
    icon: '💬',
    color: '#00ccff',
    modules: [
      { id: 'openmind', title: 'OpenMind Chat', path: '/openmind-chat', description: 'Advanced AI Chat System', status: 'active', icon: '🤖' },
      { id: 'openmind-enhanced', title: 'Enhanced Chat', path: '/openmind-enhanced', description: 'Ultra Enhanced Chat Interface', status: 'new', icon: '⚡' },
      { id: 'openmind-demo', title: 'Chat Demo', path: '/openmind-demo', description: 'Interactive Chat Demonstration', status: 'active', icon: '🎯' }
    ]
  },
  {
    id: 'search',
    title: 'Search Engines',
    icon: '🔍',
    color: '#ff6b6b',
    modules: [
      { id: 'neural-search', title: 'Neural Search', path: '/neural-search-demo', description: 'AI-Powered Search Engine', status: 'active', icon: '🧠' },
      { id: 'real-search', title: 'Real Search', path: '/real-search-demo', description: 'Real-time Search System', status: 'active', icon: '⚡' },
      { id: 'web-search', title: 'Web Search', path: '/web-search-demo', description: 'Advanced Web Search', status: 'active', icon: '🌐' },
      { id: 'neural-dev', title: 'Neural Dev', path: '/neural-dev', description: 'Neural Development Environment', status: 'beta', icon: '🔬' }
    ]
  },
  {
    id: 'industrial',
    title: 'Ultra Industrial',
    icon: '🏭',
    color: '#ffa502',
    modules: [

      { id: 'main-dashboard', title: 'Main Dashboard', path: '/ultra-industrial', description: 'EXTREME Analytics Platform', status: 'active', icon: '🎛️' },
      { id: 'best', title: 'BEST Analytics', path: '/best', description: 'Born Enhanced Tech Safe - Leadership Assessment', status: 'new', icon: '🧠' },
      { id: 'weather', title: 'Weather System', path: '/ultra-industrial/weather', description: '500+ Global Locations', status: 'active', icon: '🌍' },
      { id: 'financial', title: 'Financial Markets', path: '/ultra-industrial/financial', description: 'Real-time Stock Data', status: 'active', icon: '💰' },
      { id: 'economic', title: 'Economic Data', path: '/ultra-industrial/economic', description: 'Global Economic Metrics', status: 'active', icon: '📊' },
      { id: 'satellite', title: 'Satellite Monitor', path: '/ultra-industrial/satellite', description: 'NASA Earth Data', status: 'active', icon: '🛰️' },
      { id: 'system', title: 'System Monitor', path: '/ultra-industrial/system', description: 'Infrastructure Monitoring', status: 'active', icon: '🖥️' }
    ]
  },
  {
    id: 'security',
    title: 'Security Systems',
    icon: '🛡️',
    color: '#e74c3c',
    modules: [
      { id: 'guardian', title: 'Guardian System', path: '/guardian-demo', description: 'Advanced Security Monitoring', status: 'active', icon: '👮' },
      { id: 'ultra-speed', title: 'Ultra Speed', path: '/ultra-speed', description: 'Performance Optimization', status: 'active', icon: '⚡' }
    ]
  },
  {
    id: 'performance',
    title: 'Performance & UI',
    icon: '🌊',
    color: '#9b59b6',
    modules: [
      { id: 'fluid', title: 'Fluid Demo', path: '/fluid-demo', description: 'Fluid Interface System', status: 'active', icon: '🌊' },
      { id: 'lazy', title: 'Lazy Loading', path: '/lazy-demo', description: 'Advanced Lazy Loading', status: 'active', icon: '⏳' },
      { id: 'cva', title: 'CVA System', path: '/cva-demo', description: 'Component Variant System', status: 'beta', icon: '🎨' }
    ]
  },
  {
    id: 'revolution',
    title: 'Revolution Platform',
    icon: '🚀',
    color: '#ff0080',
    modules: [
      { id: 'revolution-core', title: 'Revolution Core', path: '/revolution', description: 'Ultra Advanced Revolutionary Technology Platform', status: 'new', icon: '🚀' },
      { id: 'revolution-agi', title: 'Revolution AGI', path: '/revolution', description: 'Revolutionary AGI with quantum processing', status: 'new', icon: '🧠' },
      { id: 'revolution-quantum', title: 'Quantum Engine', path: '/revolution', description: 'Quantum-enhanced processing system', status: 'new', icon: '⚛️' },
      { id: 'revolution-neural', title: 'Neural Mesh', path: '/revolution', description: 'Revolutionary neural network architecture', status: 'new', icon: '🕸️' }
    ]
  },
  {
    id: 'infrastructure',
    title: 'Infrastructure & Networks',
    icon: '🌐',
    color: '#00d4ff',
    modules: [
      { id: 'api-gateway', title: 'API Gateway', path: '/api-gateway', description: 'API routing and load balancing dashboard', status: 'new', icon: '🚪' },
      { id: 'lora-mesh', title: 'LoRa Mesh Network', path: '/lora-mesh', description: 'LoRa mesh network topology visualization', status: 'new', icon: '📡' },
      { id: 'iot-manager', title: 'IoT Device Manager', path: '/iot-manager', description: 'IoT device connectivity and monitoring', status: 'new', icon: '🔌' },
      { id: 'aviation-weather', title: 'Aviation Weather', path: '/aviation-weather', description: 'Specialized aviation weather system', status: 'new', icon: '✈️' },
      { id: 'radio-propaganda', title: 'Radio Propaganda', path: '/radio-propaganda', description: 'Radio broadcast management system', status: 'new', icon: '📻' },
      { id: 'utt-tools', title: 'Ultra Tech Tools', path: '/utt-tools', description: 'Advanced technical tools suite', status: 'new', icon: '🛠️' },
      { id: 'albion-utt', title: 'Albion UTT', path: '/albion-utt', description: 'Albanian Ultra Tech Tools - Specialized Albanian technical operations platform', status: 'new', icon: '🇦🇱' },
      { id: 'advanced-security', title: 'Advanced Security', path: '/advanced-security', description: 'Advanced security firewall with real-time threat monitoring', status: 'new', icon: '🛡️' },
      { id: 'cyber-security', title: 'Cyber Security Center', path: '/cyber-security', description: 'Real-time cyber defense and mirror security command center', status: 'new', icon: '🚀' }
    ]
  }
];

export default function UltraSaasDashboard() {
  const [activeCategory, setActiveCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [systemStats, setSystemStats] = useState({
    totalModules: 0,
    activeModules: 0,
    systemLoad: 0,
    uptime: '0h 0m'
  });

  useEffect(() => {
    // Calculate system statistics
    const totalModules = moduleCategories.reduce((acc, cat) => acc + cat.modules.length, 0);
    const activeModules = moduleCategories.reduce((acc, cat) =>
      acc + cat.modules.filter(mod => mod.status === 'active').length, 0);

    setSystemStats({
      totalModules,
      activeModules,
      systemLoad: Math.round(Math.random() * 30 + 70), // Simulated load 70-100%
      uptime: '24h 35m'
    });
  }, []);

  const filteredCategories = moduleCategories.filter(category => {
    if (activeCategory !== 'all' && category.id !== activeCategory) return false;
    if (searchTerm) {
      return category.modules.some(module =>
        module.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        module.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    return true;
  });

  return (
    <div className={styles['container']}>
      {/* Header */}
      <header className={styles['header']}>
        <div className={styles['headerContent']}>
          <div className={styles['titleSection']}>
            <h1 className={styles['title']}>
              🏭 ULTRA SAAS PLATFORM
            </h1>
            <p className={styles['subtitle']}>
              Complete AI-Powered SaaS Platform • 50+ Active Modules • Albanian System Integration
            </p>
            <Link href="/ultra-saas/dashboard" className={styles['dashboardLink']}>
              🎛️ Main Dashboard →
            </Link>
            <Link href="/ask" className={styles['askAgiLink']}>
              Ask AGI
            </Link>
          </div>

          <div className={styles['systemStats']}>
            <div className={styles['statItem']}>
              <span className={styles['statLabel']}>Total Modules</span>
              <span className={styles['statValue']}>{systemStats.totalModules}</span>
            </div>
            <div className={styles['statItem']}>
              <span className={styles['statLabel']}>Active</span>
              <span className={styles['statValue']}>{systemStats.activeModules}</span>
            </div>
            <div className={styles['statItem']}>
              <span className={styles['statLabel']}>System Load</span>
              <span className={styles['statValue']}>{systemStats.systemLoad}%</span>
            </div>
            <div className={styles['statItem']}>
              <span className={styles['statLabel']}>Uptime</span>
              <span className={styles['statValue']}>{systemStats.uptime}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Controls */}
      <section className={styles['controls']}>
        <div className={styles['searchContainer']}>
          <input
            type="text"
            placeholder="🔍 Search modules..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className={styles['searchInput']}
          />
        </div>

        <div className={styles['categoryFilter']}>
          <button
            onClick={() => setActiveCategory('all')}
            className={`${styles['categoryBtn']} ${activeCategory === 'all' ? styles['active'] : ''}`}
          >
            🌟 All Modules
          </button>
          {moduleCategories.map(category => (
            <button
              key={category.id}
              onClick={() => setActiveCategory(category.id)}
              className={`${styles['categoryBtn']} ${activeCategory === category.id ? styles['active'] : ''}`}
              style={{ '--category-color': category.color } as React.CSSProperties}
            >
              {category.icon} {category.title}
            </button>
          ))}
        </div>
      </section>

      {/* Module Categories */}
      <main className={styles['main']}>
        {filteredCategories.map(category => (
          <section key={category.id} className={styles['categorySection']}>
            <h2 className={styles['categoryTitle']} style={{ color: category.color }}>
              {category.icon} {category.title}
              <span className={styles['moduleCount']}>({category.modules.length} modules)</span>
            </h2>

            <div className={styles['moduleGrid']}>
              {category.modules
                .filter(module =>
                  !searchTerm ||
                  module.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                  module.description.toLowerCase().includes(searchTerm.toLowerCase())
                )
                .map(module => (
                <Link
                  key={module.id}
                  href={module.path}
                  className={styles['moduleCard']}
                  style={{ '--module-color': category.color } as React.CSSProperties}
                >
                  <div className={styles['moduleIcon']}>
                    {module.icon}
                  </div>
                  <div className={styles['moduleContent']}>
                    <h3 className={styles['moduleTitle']}>
                      {module.title}
                      <span className={`${styles['statusBadge']} ${styles[module.status]}`}>
                        {module.status}
                      </span>
                    </h3>
                    <p className={styles['moduleDescription']}>
                      {module.description}
                    </p>
                  </div>
                  <div className={styles['moduleAction']}>
                    <span>Launch →</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        ))}
      </main>

      {/* Footer */}
      <footer className={styles['footer']}>
        <div className={styles['footerContent']}>
          <div className={styles['footerSection']}>
            <h4>🇦🇱 Albanian Integration</h4>
            <p>Complete Albanian language support and local system integration</p>
          </div>
          <div className={styles['footerSection']}>
            <h4>🚀 SaaS Ready</h4>
            <p>Production-ready platform with 50+ active modules</p>
          </div>
          <div className={styles['footerSection']}>
            <h4>🔗 API Access</h4>
            <p>RESTful APIs for all modules and services</p>
          </div>
        </div>
        <div className={styles['footerBottom']}>
          <p>© 2025 Ultra SaaS Platform • Made with ❤️ in Albania • All Rights Reserved</p>
        </div>
      </footer>
    </div>
  );
}
