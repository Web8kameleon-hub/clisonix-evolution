/**
 * 🏥 AGI×MED PROFESSIONAL PORTAL LAYOUT - SIMPLE VERSION
 * UltraWeb Thinking AGI Medical Systems
 */

import * as React from 'react';
import type { Metadata } from 'next';

// Simple layout component
export default function AGIMedProfessionalLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="agimed-layout">
      {/* Header */}
      <header className="medical-header">
        <h1>🏥 AGI×Med Professional Portal</h1>
        <p>Medical Grade AI Systems</p>
      </header>

      {/* Main Content */}
      <main className="medical-content">
        {children}
      </main>

      {/* Footer */}
      <footer className="medical-footer">
        <p>© 2024 AGI×Med Systems - HIPAA Compliant</p>
      </footer>

      {/* Pure inline styles without styled-jsx */}
      <style dangerouslySetInnerHTML={{
        __html: `
        .agimed-layout {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          background: linear-gradient(135deg, #f0f4f8 0%, #e3e8f0 100%);
          font-family: system-ui, sans-serif;
        }

        .medical-header {
          background: #1a365d;
          color: white;
          padding: 2rem;
          text-align: center;
          box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        .medical-header h1 {
          margin: 0 0 0.5rem 0;
          font-size: 2rem;
        }

        .medical-header p {
          margin: 0;
          opacity: 0.8;
        }

        .medical-content {
          flex: 1;
          padding: 2rem;
          max-width: 1200px;
          margin: 0 auto;
          width: 100%;
        }

        .medical-footer {
          background: #2d3748;
          color: white;
          padding: 1rem;
          text-align: center;
        }

        .medical-footer p {
          margin: 0;
          font-size: 0.9rem;
        }

        @media (max-width: 768px) {
          .medical-header {
            padding: 1rem;
          }
          
          .medical-header h1 {
            font-size: 1.5rem;
          }
          
          .medical-content {
            padding: 1rem;
          }
        }
      `
      }} />
    </div>
  );
}

// Metadata
export const metadata: Metadata = {
  title: '🏥 AGI×Med - Professional Medical Portal',
  description: 'Medical Grade AI Systems for Healthcare Professionals',
};
