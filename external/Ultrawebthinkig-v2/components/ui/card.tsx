/**
 * Card UI Components
 * Reusable card components for EuroWeb platform
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Industrial
 * @license MIT
 */

'use client'

import * as React from 'react'

interface CardProps {
  className?: string
  children: React.ReactNode
}

export const Card: React.FC<CardProps> = ({ className = '', children }: CardProps) => {
  const baseStyles = 'bg-white border border-gray-200 rounded-lg shadow-sm'
  
  return (
    <div className={`${baseStyles} ${className}`}>
      {children}
    </div>
  );
};