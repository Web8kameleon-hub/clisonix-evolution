// Beta Banner - Subtle, dismissible, non-intrusive
'use client';

import { useState, useEffect } from 'react';

export function BetaBanner() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Check if user dismissed it before
    const dismissed = localStorage.getItem('beta-banner-dismissed');
    if (!dismissed) {
      setVisible(true);
    }
  }, []);

  const handleDismiss = () => {
    setVisible(false);
    localStorage.setItem('beta-banner-dismissed', 'true');
  };

  if (!visible) return null;

  return (
    <div className="beta-banner">
      <span className="beta-tag">BETA</span>
      <span>Platform under development. Features coming soon.</span>
      <button className="beta-close" onClick={handleDismiss} aria-label="Dismiss">
        ✕
      </button>
    </div>
  );
}

export default BetaBanner;
