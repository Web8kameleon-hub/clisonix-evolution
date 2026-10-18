/**
 * EuroWeb Web8 Platform - Client Component Wrapper
 * Ensures proper hydration for dynamic AGI interface
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Industrial
 * @license MIT
 */

'use client';

import React from 'react';
import { SimpleDemo } from './SimpleDemo';

/**
 * Web8 Client Wrapper with Static Import
 */
const Web8ClientWrapper: React.FC = () => {
  return (
    <div>
      <SimpleDemo />
    </div>
  );
};

export { Web8ClientWrapper };

