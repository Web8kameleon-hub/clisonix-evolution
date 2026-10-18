/**
 * AGI Core Page
 * Main interface for AGI Core system management
 * 
 * @version 8.0.0
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 */

import React from 'react';
import { AGICoreComponent } from '@/lib/AGICoreComponent';

export default function AGIPage() {
  return (
    <div style={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
      padding: '1rem'
    }}>
      <AGICoreComponent />
    </div>
  );
}

export const metadata = {
  title: 'AGI Core - EuroWeb Platform',
  description: 'Advanced AGI Core system management and monitoring interface',
  keywords: 'agi, artificial intelligence, core system, management, monitoring'
};
