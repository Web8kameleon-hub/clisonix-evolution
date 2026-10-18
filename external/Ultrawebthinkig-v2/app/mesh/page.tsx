/**
 * Mesh Network Dashboard Route
 * @author Ledjan Ahmati
 */

import React from 'react'
import LazyPageWrapper from '@/components/LazyPageWrapper'
import { LazyLoader } from '@/components/LazyLoader'

export default function MeshPage() {
  return (
    <LazyPageWrapper 
      title="🌐 Mesh Network Control"
      description="LoRa IoT Network • Node Management • Signal Analysis • Topology Visualization"
      gradient="from-green-600 to-emerald-600"
    >
      <LazyLoader 
        component="LoRaMeshNetwork"
        variant="industrial"
        priority="high"
        preload={true}
      />
    </LazyPageWrapper>
  )
}
