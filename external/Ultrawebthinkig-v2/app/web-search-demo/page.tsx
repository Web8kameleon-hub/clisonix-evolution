/**
 * Web Search Demo Page
 * Demonstrates the WebSearchComponent functionality
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0-WEB-SEARCH-DEMO
 * @license MIT
 */

'use client';

import React from 'react';
import WebSearchComponent from '../../components/WebSearchComponent';
import { SearchResult } from '../../lib/WebSearchEngine';
import styles from './WebSearchDemo.module.css';

const WebSearchDemo: React.FC = () => {
  const handleResultSelect = (result: SearchResult) => {
    // You can implement custom logic here, like opening in a new tab
    if (result.url) {
      window.open(result.url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.contentWrapper}>
        {/* Header */}
        <div className={styles.header}>
          <h1 className={styles.title}>
            UltraWeb Search Engine
          </h1>
          <p className={styles.subtitle}>
            Powered by advanced search algorithms with TypeScript
          </p>
        </div>

        {/* Search Component */}
        <div className={styles.searchComponentWrapper}>
          <WebSearchComponent />
        </div>

        {/* Features */}
        <div className={styles.featuresGrid}>
          {[
            {
              title: 'Multi-Type Search',
              description: 'Search across web, images, videos, news, academic papers, and local content',
              icon: '🔍'
            },
            {
              title: 'Smart Suggestions',
              description: 'Real-time search suggestions with debounced input for better performance',
              icon: '💡'
            },
            {
              title: 'Search History',
              description: 'Keep track of your searches with persistent history and quick access',
              icon: '📚'
            },
            {
              title: 'TypeScript Ready',
              description: 'Built with TypeScript for type safety and better development experience',
              icon: '⚡'
            }
          ].map((feature, index) => (
            <div key={index} className={styles.featureCard}>
              <div className={styles.featureIcon}>
                {feature.icon}
              </div>
              <h3 className={styles.featureTitle}>
                {feature.title}
              </h3>
              <p className={styles.featureDescription}>
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className={styles.footer}>
          <p className={styles.footerText}>
            Built with Next.js, TypeScript, and React • Version 8.0.0
          </p>
        </div>
      </div>
    </div>
  );
};

export default WebSearchDemo;
