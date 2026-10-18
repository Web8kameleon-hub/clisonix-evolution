/**
 * App Overview - Main Dashboard Tab
 * Central hub showing all UltraWeb capabilities
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0-OVERVIEW
 * @license MIT
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { Zap, Search, Globe, Code, Rocket, Brain, Activity, Shield } from 'lucide-react';
import styles from './overview.module.css';

const AppOverview: React.FC = () => {
  const features = [
    {
      title: 'Ultra Speed Engine',
      description: 'Më i shpejti në rruzullin tokësor - Quantum performance optimization',
      href: '/ultra-speed',
      icon: Zap,
      color: '#00ff00',
      status: 'ACTIVE'
    },
    {
      title: 'Web Search Engine',
      description: 'Advanced search with AI-powered suggestions and real-time results',
      href: '/web-search-demo',
      icon: Search,
      color: '#2563eb',
      status: 'READY'
    },
    {
      title: 'AGI Neural Network',
      description: 'Artificial General Intelligence with advanced reasoning capabilities',
      href: '/agi-demo',
      icon: Brain,
      color: '#8b5cf6',
      status: 'EXPERIMENTAL'
    },
    {
      title: 'Global Browser',
      description: 'Ultra-secure browsing with quantum encryption and speed optimization',
      href: '/browser',
      icon: Globe,
      color: '#f59e0b',
      status: 'BETA'
    }
  ];

  const stats = [
    { label: 'Performance Score', value: '99.8%', icon: Activity },
    { label: 'Speed Multiplier', value: '∞x', icon: Rocket },
    { label: 'Security Level', value: 'Quantum', icon: Shield },
    { label: 'AI Efficiency', value: '100%', icon: Code }
  ];

  return (
    <div className={styles.container}>
      
      {/* Header */}
      <div className={styles.header}>
        <h1 className={styles.title}>
          ULTRAWEB
        </h1>
        <p className={styles.subtitle}>
          The Fastest Web Platform on Earth
        </p>
        
        {/* Stats Bar */}
        <div className={styles.statsGrid}>
          {stats.map((stat, index) => (
            <div key={index} className={styles.statCard}>
              <stat.icon size={20} className={styles.statIcon} />
              <div>
                <div className={styles.statLabel}>
                  {stat.label}
                </div>
                <div className={styles.statValue}>
                  {stat.value}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Features Grid */}
      <div className={styles.featuresGrid}>
        {features.map((feature, index) => (
          <Link key={index} href={feature.href} className={styles.featureLink}>
            <div 
              className={styles.featureCard}
              style={{ '--feature-color': feature.color } as React.CSSProperties}
            >
              
              {/* Status Badge */}
              <div className={styles.statusBadge}>
                {feature.status}
              </div>
              
              {/* Icon */}
              <div className={styles.featureIconContainer}>
                <div className={styles.featureIconWrapper}>
                  <feature.icon size={28} className={styles.featureIcon} />
                </div>
                <h3 className={styles.featureTitle}>
                  {feature.title}
                </h3>
              </div>
              
              {/* Description */}
              <p className={styles.featureDescription}>
                {feature.description}
              </p>
              
              {/* Launch Button */}
              <div className={styles.launchButton}>
                <span>Launch Application</span>
                <Rocket size={16} />
              </div>
            </div>
          </Link>
        ))}
      </div>

      {/* Technology Stack */}
      <div className={styles.techStackContainer}>
        <h2 className={styles.techStackTitle}>
          Technology Stack
        </h2>
        
        <div className={styles.techGrid}>
          {[
            'Next.js 14.2.30',
            'TypeScript 5.7.2',
            'React 18',
            'Yarn Berry 4.9.2',
            'CSS Modules',
            'Framer Motion',
            'Lucide Icons',
            'ESLint 8.57.1'
          ].map((tech, index) => (
            <div key={index} className={styles.techItem}>
              {tech}
            </div>
          ))}
        </div>
        
        <div className={styles.footer}>
          Built with ❤️ by Ledjan Ahmati • Version 8.0.0-ULTRA
        </div>
      </div>
    </div>
  );
};

export default AppOverview;
