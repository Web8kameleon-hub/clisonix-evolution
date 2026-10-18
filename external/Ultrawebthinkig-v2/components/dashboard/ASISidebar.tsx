'use client'

import React from 'react'
import { 
  HomeIcon,
  ChartBarIcon,
  GlobeAltIcon,
  CurrencyDollarIcon,
  NewspaperIcon,
  HeartIcon,
  BookOpenIcon,
  BuildingLibraryIcon,
  Cog6ToothIcon,
  CpuChipIcon,
  CloudIcon,
  MapIcon
} from '@heroicons/react/24/outline'

interface ASISidebarProps {
  isOpen: boolean
  activeView: string
  onViewChange: (view: string) => void
  onClose: () => void
}

const sidebarItems = [
  { id: 'overview', name: 'Overview', icon: HomeIcon, gradient: 'from-blue-400 to-purple-500' },
  { id: 'analytics', name: '📊 Ultra Analytics', icon: ChartBarIcon, gradient: 'from-green-400 to-blue-500' },
  { id: 'all-services', name: '🌐 All Services (60+)', icon: GlobeAltIcon, gradient: 'from-pink-500 to-rose-500' },
  
  // === CORE MODULES ===
  { id: 'agent-demo', name: '🤖 Agent Demo', icon: CpuChipIcon, gradient: 'from-emerald-400 to-blue-500' },
  { id: 'api-gateway', name: '🚪 API Gateway', icon: Cog6ToothIcon, gradient: 'from-purple-500 to-pink-500' },
  { id: 'api-producer', name: '⚡ API Producer', icon: CloudIcon, gradient: 'from-orange-500 to-red-500' },
  
  // === ASI INTELLIGENCE SYSTEMS ===
  { id: 'asi-core', name: '🇦🇱 ASI Core Engine', icon: CpuChipIcon, gradient: 'from-red-500 via-yellow-500 to-green-500' },
  { id: 'asi-cultural', name: '🎨 ASI Cultural', icon: BuildingLibraryIcon, gradient: 'from-red-400 to-yellow-500' },
  { id: 'asi-alba', name: '🤖 ALBA Intelligence', icon: Cog6ToothIcon, gradient: 'from-purple-500 to-pink-500' },
  { id: 'asi-albi', name: '🧠 ALBI Processing', icon: ChartBarIcon, gradient: 'from-cyan-400 to-blue-500' },
  
  // === DATA & APIs ===
  { id: 'api-registry', name: '📋 API Registry', icon: BookOpenIcon, gradient: 'from-indigo-500 to-purple-500' },
  { id: 'real-data-apis', name: '� Real Data APIs', icon: CloudIcon, gradient: 'from-green-500 to-teal-500' },
  { id: 'weather-data', name: '🌤️ Weather Intelligence', icon: CloudIcon, gradient: 'from-cyan-400 to-blue-500' },
  { id: 'financial-data', name: '� Financial Markets', icon: CurrencyDollarIcon, gradient: 'from-yellow-400 to-green-500' },
  
  // === GLOBAL INTELLIGENCE ===
  { id: 'cultural', name: '🌍 Cultural Intelligence', icon: MapIcon, gradient: 'from-red-400 to-yellow-500' },
  { id: 'blockchain', name: '₿ Blockchain & Trading', icon: CurrencyDollarIcon, gradient: 'from-yellow-400 to-green-500' },
  { id: 'news', name: '📰 News Intelligence', icon: NewspaperIcon, gradient: 'from-purple-400 to-pink-500' },
  { id: 'financial', name: '💰 Financial Markets', icon: CurrencyDollarIcon, gradient: 'from-green-400 to-emerald-500' },
  
  // === SYSTEM MANAGEMENT ===
  { id: 'health', name: '❤️ System Health', icon: HeartIcon, gradient: 'from-pink-400 to-red-500' },
  { id: 'library', name: '📚 Global Libraries', icon: BookOpenIcon, gradient: 'from-indigo-400 to-purple-500' },
  { id: 'museum', name: '🏛️ Museums & Culture', icon: BuildingLibraryIcon, gradient: 'from-orange-400 to-red-500' },
]

export function ASISidebar({ isOpen, activeView, onViewChange, onClose }: ASISidebarProps) {
  return (
    <>
      {/* 🗂️ Sidebar */}
      <div className={`
        fixed lg:static inset-y-0 left-0 z-50 w-64 
        bg-white/10 backdrop-blur-md border-r border-white/20
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        
        {/* 🎨 Sidebar Header */}
        <div className="p-4 border-b border-white/20">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-red-500 to-yellow-500 flex items-center justify-center">
              <span className="text-white font-bold">🇦🇱</span>
            </div>
            <div>
              <h2 className="font-bold text-white">ASI Dashboard</h2>
              <p className="text-xs text-gray-300">Intelligence Hub</p>
            </div>
          </div>
        </div>

        {/* 🗂️ Navigation Menu */}
        <nav className="p-4 space-y-2">
          {sidebarItems.map((item) => {
            const IconComponent = item.icon
            const isActive = activeView === item.id
            
            return (
              <button
                key={item.id}
                onClick={() => {
                  onViewChange(item.id)
                  onClose()
                }}
                className={`
                  w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg
                  transition-all duration-200 text-left
                  ${isActive 
                    ? `bg-gradient-to-r ${item.gradient} text-white shadow-lg` 
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'
                  }
                `}
              >
                <IconComponent className="h-5 w-5 flex-shrink-0 opacity-0" />
                <span className="font-medium truncate">{item.name}</span>
                
                {/* ✨ Active Indicator */}
                {isActive && (
                  <div className="ml-auto w-2 h-2 bg-white rounded-full animate-pulse" />
                )}
              </button>
            )
          })}
        </nav>

        {/* ⚙️ Settings & Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/20">
          <button className="w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-white/10 hover:text-white transition-colors">
            <Cog6ToothIcon className="h-5 w-5" />
            <span className="font-medium">Settings</span>
          </button>
          
          <div className="mt-3 pt-3 border-t border-white/20">
            <div className="text-xs text-gray-400 text-center">
              <p>🇦🇱 Albanian System Intelligence</p>
              <p className="mt-1">v2.0.0 - Global Edition</p>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
