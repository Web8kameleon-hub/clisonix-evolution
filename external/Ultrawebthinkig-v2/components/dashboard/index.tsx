'use client'

import React, { useState, useEffect } from 'react'
import { ASIHeader } from './ASIHeader'
import { ASISidebar } from './ASISidebar'
import { ASIMainContent } from './ASIMainContent'
import { ASIFooter } from './ASIFooter'
import { useASIData } from '@/lib/hooks/useASIData'

export function ASIDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [activeView, setActiveView] = useState('analytics')
  const { data: systemStatus, isLoading } = useASIData()

  // 📱 Handle mobile sidebar
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 1024) {
        setSidebarOpen(false)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div className="min-h-screen bg-white">
      {/* 🎨 Clean White Dashboard Layout */}
      <div className="w-full">
        
        {/* 🎯 Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">ASI Ultimate Dashboard</h1>
            <div className="text-sm text-gray-600">
              {systemStatus?.status || 'Loading...'}
            </div>
          </div>
        </header>
        
        {/* 🎨 Main Content - Centered */}
        <main className="max-w-7xl mx-auto px-6 py-8">
          <ASIMainContent 
            activeView={activeView}
            systemStatus={systemStatus}
          />
        </main>
        
        {/* 📊 Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <ASIFooter systemStatus={systemStatus} />
        </footer>
      </div>
    </div>
  )
}
