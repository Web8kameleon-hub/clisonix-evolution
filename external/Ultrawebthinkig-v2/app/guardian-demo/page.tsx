/**
 * Guardian Security Demo Page
 * Demonstrates industrial-grade DDoS protection and threat monitoring
 * 
 * @version 8.0.0
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 */

import React from 'react';
import GuardianDashboard from '@/components/GuardianDashboard';

export default function GuardianDemo() {
  return (
    <div>
      <GuardianDashboard />
    </div>
  );
}

export const metadata = {
  title: 'Guardian Security Dashboard - EuroWeb Platform',
  description: 'Industrial-grade DDoS protection and threat monitoring for Web8 platform',
  keywords: 'security, ddos protection, threat monitoring, guardian, cybersecurity'
};
