import React from 'react'
import dynamic from 'next/dynamic'

type LazyLoaderProps = {
  component: 'LoRaMeshNetwork' | string
  variant?: 'industrial' | 'default' | string
  priority?: 'high' | 'normal' | string
  preload?: boolean
}

const LoRaMeshNetwork = dynamic(() => import('./LoRaMeshNetwork'), {
  ssr: false,
  loading: () => <div className="text-sm text-gray-300">Loading component...</div>,
})

export function LazyLoader({ component }: LazyLoaderProps) {
  if (component === 'LoRaMeshNetwork') {
    return <LoRaMeshNetwork />
  }

  return <div className="text-sm text-yellow-300">Component not registered: {component}</div>
}
