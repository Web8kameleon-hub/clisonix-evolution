/**
 * Label UI Component
 * Reusable label component for EuroWeb platform
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Industrial
 * @license MIT
 */

'use client'

import React from 'react'

interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  className?: string
  children: React.ReactNode
}

export const Label: React.FC<LabelProps> = ({ className = '', children, ...props }) => {
  const baseStyles = 'text-sm font-medium text-gray-700'
  
  return (
    <label className={`${baseStyles} ${className}`} {...props}>
      {children}
    </label>
  );
};