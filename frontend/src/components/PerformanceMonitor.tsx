'use client'

import { useState, useEffect } from 'react'

interface PerformanceMetrics {
  fps: number
  memory: number
  loadTime: number
}

export default function PerformanceMonitor() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 60,
    memory: 0,
    loadTime: 0
  })
  const [isMinimized, setIsMinimized] = useState(true)

  useEffect(() => {
    // Get initial load time
    if (typeof window !== 'undefined' && window.performance) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming
      if (navigation) {
        setMetrics(prev => ({
          ...prev,
          loadTime: Math.round(navigation.loadEventEnd - navigation.startTime)
        }))
      }
    }

    // FPS counter
    let frameCount = 0
    let lastTime = performance.now()
    let animationId: number

    const measureFPS = () => {
      frameCount++
      const currentTime = performance.now()
      
      if (currentTime - lastTime >= 1000) {
        setMetrics(prev => ({
          ...prev,
          fps: frameCount,
          memory: (performance as any).memory?.usedJSHeapSize 
            ? Math.round((performance as any).memory.usedJSHeapSize / 1048576) 
            : 0
        }))
        frameCount = 0
        lastTime = currentTime
      }
      
      animationId = requestAnimationFrame(measureFPS)
    }

    animationId = requestAnimationFrame(measureFPS)

    return () => {
      cancelAnimationFrame(animationId)
    }
  }, [])

  if (isMinimized) {
    return (
      <button
        onClick={() => setIsMinimized(false)}
        className="fixed bottom-4 right-4 bg-gray-800 text-white px-3 py-2 rounded-lg text-xs font-mono shadow-lg hover:bg-gray-700 transition border border-gray-600"
      >
        📊 {metrics.fps} FPS
      </button>
    )
  }

  return (
    <div className="fixed bottom-4 right-4 bg-gray-900 text-white p-4 rounded-lg shadow-xl border border-gray-700 text-xs font-mono min-w-[200px]">
      <div className="flex justify-between items-center mb-3">
        <span className="font-bold text-green-400">📊 Performance</span>
        <button 
          onClick={() => setIsMinimized(true)}
          className="text-gray-400 hover:text-white"
        >
          ✕
        </button>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-gray-400">FPS:</span>
          <span className={metrics.fps >= 50 ? 'text-green-400' : metrics.fps >= 30 ? 'text-yellow-400' : 'text-red-400'}>
            {metrics.fps}
          </span>
        </div>
        
        {metrics.memory > 0 && (
          <div className="flex justify-between">
            <span className="text-gray-400">Memory:</span>
            <span className="text-blue-400">{metrics.memory} MB</span>
          </div>
        )}
        
        <div className="flex justify-between">
          <span className="text-gray-400">Load:</span>
          <span className="text-purple-400">{metrics.loadTime}ms</span>
        </div>
      </div>
    </div>
  )
}
