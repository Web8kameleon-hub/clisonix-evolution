/**
 * @author Ledjan Ahmati
 * @version 8.0.0-WEB8
 * @contact dealsjona@gmail.com
 */

'use client';

import React from 'react';
import LazyPageWrapper from '../../components/LazyPageWrapper';
import LoRaMeshNetwork from '../../components/LoRaMeshNetwork';

export default function LoRaMeshPage() {
  return (
    <LazyPageWrapper
      title="LoRa Mesh Network"
      description="Interactive mesh network topology and control"
      gradient="from-violet-600 to-purple-600"
    >
      <LoRaMeshNetwork />
    </LazyPageWrapper>
  );
}
