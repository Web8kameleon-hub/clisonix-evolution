import React from 'react'
import styles from './layout.module.css'

/**
 * 🇦🇱 ASI System Layout
 * Struktura e plotë për Albanian System Intelligence
 */

export default function ASILayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className={styles.layoutContainer}>
      {/* ASI Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div>
            <h1 className={styles.headerTitle}>
              🇦🇱 ASI - Albanian System Intelligence
            </h1>
            <p className={styles.headerSubtitle}>
              Sistemi i Parë AI Shqiptar në Botë
            </p>
          </div>
          
          <div className={styles.headerInfoContainer}>
            <div className={styles.headerInfoBadge}>
              🧠 12-Layer Neural Network
            </div>
            
            <div className={styles.headerStatusBadge}>
              ✅ AKTIV
            </div>
          </div>
        </div>
      </header>

      {/* ASI Navigation */}
      <nav className={styles.nav}>
        <div className={styles.navContent}>
          <div className={styles.navLinks}>
            <a href="/asi-12layer" className={styles.navLinkActive}>
              🏠 Dashboard Kryesor
            </a>
            
            <a href="/asi-ultimate" className={`${styles.navLink} ${styles.navLinkUltimate}`}>
              🌟 Ultimate Universe
            </a>
            
            <a href="/api/asi-12layer" className={`${styles.navLink} ${styles.navLinkApi}`}>
              🔌 API Status
            </a>
          </div>
        </div>
      </nav>

      {/* ASI Sidebar + Main Content */}
      <div className={styles.mainContainer}>
        
        {/* ASI Sidebar */}
        <aside className={styles.sidebar}>
          <div className={styles.sidebarContent}>
            <h3 className={styles.sidebarTitle}>
              🧠 ASI Layers
            </h3>
            
            <div className={styles.sidebarLayersContainer}>
              <div className={`${styles.sidebarLayerBase} ${styles.sidebarLayerLanguage}`}>
                <div className={styles.sidebarLayerTitle}>Layer 1-3: Language</div>
                <div className={styles.sidebarLayerSubtitle}>Përpunimi i Gjuhës Shqipe</div>
              </div>
              
              <div className={`${styles.sidebarLayerBase} ${styles.sidebarLayerMedical}`}>
                <div className={styles.sidebarLayerTitle}>Layer 4-6: Medical</div>
              </div>
              
              <div className={`${styles.sidebarLayerBase} ${styles.sidebarLayerCultural}`}>
                <div className={styles.sidebarLayerTitle}>Layer 7-9: Cultural</div>
              </div>
              
              <div className={`${styles.sidebarLayerBase} ${styles.sidebarLayerTechnical}`}>
                <div className={styles.sidebarLayerTitle}>Layer 10-12: Technical</div>
                <div className={styles.sidebarLayerSubtitle}>Procesim Teknologjik</div>
              </div>
            </div>

            <h3 className={styles.sidebarMetricsTitle}>
              📊 Live Metrics
            </h3>
            
            <div className={styles.sidebarMetricsContainer}>
              <div>⚡ Response: &lt; 1ms</div>
              <div>🧠 Memory: Real-time</div>
              <div>🇦🇱 Language: Albanian</div>
            </div>
          </div>
        </aside>

        {/* ASI Main Content */}
        <main className={styles.mainContent}>
          {children}
        </main>
      </div>

      {/* ASI Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <p className={styles.footerText}>
            🇦🇱 ASI - Albanian System Intelligence | Sistemi i Parë AI Shqiptar | 
            <span className={styles.footerOwner}> Ledjan Ahmati</span> - 100% Pronar
          </p>
          <p className={styles.footerDate}>
            October 2025 - World's First Albanian-Centric AI System
          </p>
        </div>
      </footer>
    </div>
  )
}
