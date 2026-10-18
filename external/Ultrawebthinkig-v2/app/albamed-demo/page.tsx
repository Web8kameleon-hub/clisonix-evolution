'use client';

import React, { useState, useEffect } from 'react';
import { 
  getASIStatus, 
  getASIModules, 
  processASIRequest, 
  addASIStatusListener, 
  removeASIStatusListener,
  getASISystemHealth,
  activateASIModule,
  deactivateASIModule,
  type ASIStatus,
  type ASIResponse,
  type ASIModule
} from '../../lib/ASICore';
import styles from './albamed.module.css';

interface MedicalQuery {
  id: string;
  text: string;
  language: 'sq' | 'en';
  timestamp: number;
  response?: ASIResponse;
  status: 'pending' | 'processing' | 'completed' | 'error';
}

interface SystemMetrics {
  activePatients: number;
  processedQueries: number;
  avgResponseTime: number;
  accuracyRate: number;
  languageDistribution: { sq: number; en: number };
}

export default function AlbaMedDemo() {
  // State Management
  const [asiStatus, setASIStatus] = useState<ASIStatus | null>(null);
  const [asiModules, setASIModules] = useState<ASIModule[]>([]);
  const [currentQuery, setCurrentQuery] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState<'sq' | 'en'>('sq');
  const [medicalQueries, setMedicalQueries] = useState<MedicalQuery[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics>({
    activePatients: 247,
    processedQueries: 1842,
    avgResponseTime: 0.34,
    accuracyRate: 97.8,
    languageDistribution: { sq: 68, en: 32 }
  });
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedModules, setSelectedModules] = useState<string[]>(['asi-medical']);

  // Initialize ASI System
  useEffect(() => {
    const statusListener = (status: ASIStatus) => {
      setASIStatus(status);
    };

    // Set initial state
    setASIStatus(getASIStatus());
    setASIModules(getASIModules());

    // Add listener
    addASIStatusListener(statusListener);

    // Update metrics periodically
    const metricsInterval = setInterval(() => {
      const health = getASISystemHealth();
      setSystemMetrics(prev => ({
        ...prev,
        avgResponseTime: health.metrics.response_time,
        accuracyRate: health.metrics.accuracy * 100
      }));
    }, 2000);

    return () => {
      removeASIStatusListener(statusListener);
      clearInterval(metricsInterval);
    };
  }, []);

  // Handle Query Processing
  const handleQuerySubmit = async () => {
    if (!currentQuery.trim()) return;

    const queryId = `MED_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const newQuery: MedicalQuery = {
      id: queryId,
      text: currentQuery.trim(),
      language: selectedLanguage,
      timestamp: Date.now(),
      status: 'pending'
    };

    setMedicalQueries(prev => [newQuery, ...prev]);
    setIsProcessing(true);

    try {
      // Update query status
      setMedicalQueries(prev => 
        prev.map(q => q.id === queryId ? { ...q, status: 'processing' } : q)
      );

      // Process with ASI
      const response = await processASIRequest(currentQuery, selectedModules);
      
      // Update with response
      setMedicalQueries(prev => 
        prev.map(q => q.id === queryId ? { 
          ...q, 
          response, 
          status: 'completed' 
        } : q)
      );

      // Update metrics
      setSystemMetrics(prev => ({
        ...prev,
        processedQueries: prev.processedQueries + 1,
        languageDistribution: {
          ...prev.languageDistribution,
          [selectedLanguage]: prev.languageDistribution[selectedLanguage] + 1
        }
      }));

    } catch (error) {
      console.error('Query processing error:', error);
      setMedicalQueries(prev => 
        prev.map(q => q.id === queryId ? { ...q, status: 'error' } : q)
      );
    } finally {
      setIsProcessing(false);
      setCurrentQuery('');
    }
  };

  // Handle Module Toggle
  const toggleModule = (moduleId: string) => {
    const module = asiModules.find(m => m.id === moduleId);
    if (!module) return;

    if (module.status === 'active') {
      deactivateASIModule(moduleId);
      setSelectedModules(prev => prev.filter(id => id !== moduleId));
    } else {
      activateASIModule(moduleId);
      setSelectedModules(prev => [...prev, moduleId]);
    }

    // Refresh modules
    setTimeout(() => {
      setASIModules(getASIModules());
    }, 100);
  };

  // Predefined Medical Queries
  const sampleQueries = {
    sq: [
      "Çfarë simptomash ka gripi sezonal?",
      "Si të parandaloj infeksionet e frymëmarrjes?",
      "Çfarë ushqimi rekomandohet për diabet?",
      "Si të menaxhoj stresin dhe ankthit?",
      "Çfarë ushtrimesh janë të mira për shëndetin e zemrës?"
    ],
    en: [
      "What are the symptoms of seasonal flu?",
      "How to prevent respiratory infections?",
      "What diet is recommended for diabetes?",
      "How to manage stress and anxiety?",
      "What exercises are good for heart health?"
    ]
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.titleSection}>
            <h1 className={styles.title}>
              🏥 AlbaMed Demo - ASI Medical Intelligence
            </h1>
            <p className={styles.subtitle}>
              {selectedLanguage === 'sq' 
                ? "Sistemi Inteligjent Mjekësor Shqiptar me ASI (Albanian System Intelligence)"
                : "Albanian Intelligent Medical System with ASI (Albanian System Intelligence)"
              }
            </p>
          </div>
          
          <div className={styles.statusIndicator}>
            <div className={`${styles.statusDot} ${asiStatus?.isActive ? styles.active : styles.inactive}`}></div>
            <span className={styles.statusText}>
              ASI {asiStatus?.isActive ? 'AKTIV' : 'JOAKTIV'}
            </span>
          </div>
        </div>
      </header>

      {/* System Metrics */}
      <section className={styles.metricsSection}>
        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>👥</div>
          <div className={styles.metricContent}>
            <span className={styles.metricValue}>{systemMetrics.activePatients}</span>
            <span className={styles.metricLabel}>
              {selectedLanguage === 'sq' ? 'Pacientë Aktivë' : 'Active Patients'}
            </span>
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>📊</div>
          <div className={styles.metricContent}>
            <span className={styles.metricValue}>{systemMetrics.processedQueries}</span>
            <span className={styles.metricLabel}>
              {selectedLanguage === 'sq' ? 'Pyetje të Përpunuara' : 'Processed Queries'}
            </span>
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>⚡</div>
          <div className={styles.metricContent}>
            <span className={styles.metricValue}>{systemMetrics.avgResponseTime.toFixed(2)}s</span>
            <span className={styles.metricLabel}>
              {selectedLanguage === 'sq' ? 'Kohë Përgjigje' : 'Response Time'}
            </span>
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>🎯</div>
          <div className={styles.metricContent}>
            <span className={styles.metricValue}>{systemMetrics.accuracyRate.toFixed(1)}%</span>
            <span className={styles.metricLabel}>
              {selectedLanguage === 'sq' ? 'Saktësi' : 'Accuracy'}
            </span>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div className={styles.mainContent}>
        {/* Left Panel - Query Interface */}
        <div className={styles.leftPanel}>
          {/* Language Selector */}
          <div className={styles.languageSelector}>
            <button 
              className={`${styles.langButton} ${selectedLanguage === 'sq' ? styles.active : ''}`}
              onClick={() => setSelectedLanguage('sq')}
            >
              🇦🇱 Shqip
            </button>
            <button 
              className={`${styles.langButton} ${selectedLanguage === 'en' ? styles.active : ''}`}
              onClick={() => setSelectedLanguage('en')}
            >
              🇬🇧 English
            </button>
          </div>

          {/* Query Input */}
          <div className={styles.querySection}>
            <h3 className={styles.sectionTitle}>
              {selectedLanguage === 'sq' ? '💬 Pyetja Mjekësore' : '💬 Medical Query'}
            </h3>
            
            <textarea
              className={styles.queryInput}
              value={currentQuery}
              onChange={(e) => setCurrentQuery(e.target.value)}
              placeholder={selectedLanguage === 'sq' 
                ? "Shkruani pyetjen tuaj mjekësore këtu..."
                : "Write your medical question here..."
              }
              rows={4}
            />

            <div className={styles.queryActions}>
              <button 
                className={styles.submitButton}
                onClick={handleQuerySubmit}
                disabled={isProcessing || !currentQuery.trim()}
              >
                {isProcessing 
                  ? (selectedLanguage === 'sq' ? '🔄 Duke përpunuar...' : '🔄 Processing...')
                  : (selectedLanguage === 'sq' ? '🚀 Dërgo Pyetjen' : '🚀 Submit Query')
                }
              </button>
            </div>
          </div>

          {/* Sample Queries */}
          <div className={styles.samplesSection}>
            <h4 className={styles.samplesTitle}>
              {selectedLanguage === 'sq' ? '💡 Pyetje Shembull' : '💡 Sample Queries'}
            </h4>
            <div className={styles.samplesList}>
              {sampleQueries[selectedLanguage].map((query, index) => (
                <button
                  key={index}
                  className={styles.sampleButton}
                  onClick={() => setCurrentQuery(query)}
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Results & Modules */}
        <div className={styles.rightPanel}>
          {/* ASI Modules Status */}
          <div className={styles.modulesSection}>
            <h3 className={styles.sectionTitle}>
              {selectedLanguage === 'sq' ? '🧠 ASI Modulet' : '🧠 ASI Modules'}
            </h3>
            <div className={styles.modulesList}>
              {asiModules.map((module) => (
                <div key={module.id} className={`${styles.moduleCard} ${styles[module.status]}`}>
                  <div className={styles.moduleHeader}>
                    <span className={styles.moduleTitle}>
                      {selectedLanguage === 'sq' ? module.nameAlbanian : module.name}
                    </span>
                    <button
                      className={styles.moduleToggle}
                      onClick={() => toggleModule(module.id)}
                    >
                      {module.status === 'active' ? '🟢' : '🔴'}
                    </button>
                  </div>
                  <p className={styles.moduleDescription}>
                    {selectedLanguage === 'sq' ? module.descriptionAlbanian : module.description}
                  </p>
                  <div className={styles.moduleCapabilities}>
                    {module.capabilities.map((capability, index) => (
                      <span key={index} className={styles.capabilityTag}>
                        {capability}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Query Results */}
          <div className={styles.resultsSection}>
            <h3 className={styles.sectionTitle}>
              {selectedLanguage === 'sq' ? '📋 Përgjigjet ASI' : '📋 ASI Responses'}
            </h3>
            <div className={styles.resultsList}>
              {medicalQueries.length === 0 ? (
                <div className={styles.noResults}>
                  <p>
                    {selectedLanguage === 'sq' 
                      ? "Asnjë pyetje nuk është dërguar ende. Shkruani një pyetje mjekësore për të filluar."
                      : "No queries submitted yet. Write a medical question to get started."
                    }
                  </p>
                </div>
              ) : (
                medicalQueries.map((query) => (
                  <div key={query.id} className={`${styles.resultCard} ${styles[query.status]}`}>
                    <div className={styles.queryHeader}>
                      <span className={styles.queryTime}>
                        {new Date(query.timestamp).toLocaleTimeString()}
                      </span>
                      <span className={styles.queryLang}>
                        {query.language === 'sq' ? '🇦🇱' : '🇬🇧'}
                      </span>
                      <span className={`${styles.queryStatus} ${styles[query.status]}`}>
                        {query.status === 'pending' && '⏳'}
                        {query.status === 'processing' && '🔄'}
                        {query.status === 'completed' && '✅'}
                        {query.status === 'error' && '❌'}
                      </span>
                    </div>
                    
                    <div className={styles.queryText}>
                      <strong>Q:</strong> {query.text}
                    </div>
                    
                    {query.response && (
                      <div className={styles.responseText}>
                        <strong>ASI:</strong> {query.response.text}
                        <div className={styles.responseMetrics}>
                          <span>⚡ {query.response.processing_time}ms</span>
                          <span>🎯 {(query.response.confidence * 100).toFixed(1)}%</span>
                          <span>🧠 {query.response.intelligence_level}</span>
                          <span>📊 {query.response.modules_used.length} module(s)</span>
                        </div>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}