/**
 * EuroWeb Web8 Platform - Minimal Tab System
 * Pure CSS + CVA Implementation (No Motion)
 * 
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 * @version 8.0.0
 * @license MIT
 */

'use client'

import React, { useState } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

// Tab Interface
interface Tab {
  id: string
  title: string
  url: string
  isActive: boolean
  isLoading: boolean
}

// Tab variants using CVA
const tabVariants = cva(
  'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all cursor-pointer relative',
  {
    variants: {
      intent: {
        active: 'bg-amber-500/20 border-amber-500 text-amber-300',
        inactive: 'bg-transparent border-transparent text-slate-300',
        premium: 'bg-amber-500/10 border-amber-500/50 text-amber-200',
        loading: 'bg-slate-800/50 border-slate-600 text-slate-400'
      },
      size: {
        small: 'py-1 px-3 text-xs',
        medium: 'py-2 px-4 text-sm',
        large: 'py-3 px-6 text-base'
      }
    },
    defaultVariants: {
      intent: 'inactive',
      size: 'medium'
    }
  }
)

// Button variants
const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
  {
    variants: {
      intent: {
        primary: 'bg-amber-600 text-white hover:bg-amber-700',
        secondary: 'bg-slate-700 text-slate-200 hover:bg-slate-600',
        ghost: 'hover:bg-slate-800 hover:text-slate-100',
        danger: 'bg-red-600 text-white hover:bg-red-700'
      },
      size: {
        sm: 'h-8 px-3 text-xs',
        md: 'h-9 px-4 text-sm',
        lg: 'h-10 px-6 text-base'
      }
    },
    defaultVariants: {
      intent: 'primary',
      size: 'md'
    }
  }
)

// Main component
const Web8TabSystemMinimal: React.FC = () => {
  const [tabs, setTabs] = useState<Tab[]>([
    { id: '1', title: 'EuroWeb Dashboard', url: 'https://euroweb.dev', isActive: true, isLoading: false },
    { id: '2', title: 'GitHub Enterprise', url: 'https://github.com/enterprise', isActive: false, isLoading: false },
    { id: '3', title: 'AGI Research Portal', url: 'https://agi.research.local', isActive: false, isLoading: false },
    { id: '4', title: 'Azure DevOps', url: 'https://dev.azure.com', isActive: false, isLoading: false },
    { id: '5', title: 'Industrial Analytics', url: 'https://analytics.industrial.local', isActive: false, isLoading: false },
    { id: '6', title: 'Cloud Infrastructure', url: 'https://cloud.infra.local', isActive: false, isLoading: false },
    { id: '7', title: 'Security Center', url: 'https://security.center.local', isActive: false, isLoading: false },
    { id: '8', title: 'Documentation', url: 'https://docs.euroweb.dev', isActive: false, isLoading: false },
    { id: '9', title: 'Settings', url: 'https://settings.local', isActive: false, isLoading: false }
  ])

  const [activeTabId, setActiveTabId] = useState('1')

  const activateTab = (tabId: string) => {
    setTabs(tabs.map(tab => ({
      ...tab,
      isActive: tab.id === tabId
    })))
    setActiveTabId(tabId)
  }

  const closeTab = (tabId: string) => {
    if (tabs.length <= 1) return
    const newTabs = tabs.filter(tab => tab.id !== tabId)
    setTabs(newTabs)
    if (activeTabId === tabId) {
      const nextTab = newTabs[0]
      setActiveTabId(nextTab.id)
      activateTab(nextTab.id)
    }
  }

  const addNewTab = () => {
    const newId = (tabs.length + 1).toString()
    const newTab: Tab = {
      id: newId,
      title: 'New Tab',
      url: 'https://euroweb.dev/new',
      isActive: false,
      isLoading: false
    }
    setTabs([...tabs, newTab])
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-slate-100">
      {/* Browser Chrome */}
      <div className="border-b border-slate-700/50 bg-slate-800/90 backdrop-blur-sm">
        {/* Tab Bar */}
        <div className="flex items-center bg-slate-900/50">
          {/* Tabs Container */}
          <div className="flex-1 flex items-center overflow-x-auto scrollbar-hide">
            <div className="flex min-w-max px-2">
              {tabs.map((tab) => (
                <div
                  key={tab.id}
                  className={tabVariants({
                    intent: tab.isActive ? 'active' : tab.isLoading ? 'loading' : 'inactive'
                  })}
                  onClick={() => activateTab(tab.id)}
                >
                  {/* Tab Icon */}
                  <div className="w-4 h-4 rounded-full bg-gradient-to-br from-amber-400 to-orange-500 flex-shrink-0" />
                  
                  {/* Tab Title */}
                  <span className="truncate max-w-[200px]">
                    {tab.title}
                  </span>
                  
                  {/* Close Button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      closeTab(tab.id)
                    }}
                    className="ml-2 w-4 h-4 rounded-full hover:bg-slate-600 flex items-center justify-center text-slate-400 hover:text-slate-200"
                  >
                    ×
                  </button>
                </div>
              ))}
              
              {/* Add Tab Button */}
              <button
                onClick={addNewTab}
                className={buttonVariants({ intent: 'ghost', size: 'sm' })}
              >
                +
              </button>
            </div>
          </div>

          {/* Browser Controls */}
          <div className="flex items-center gap-2 px-4">
            <button className={buttonVariants({ intent: 'secondary', size: 'sm' })}>
              ←
            </button>
            <button className={buttonVariants({ intent: 'secondary', size: 'sm' })}>
              →
            </button>
            <button className={buttonVariants({ intent: 'secondary', size: 'sm' })}>
              ↻
            </button>
          </div>
        </div>

        {/* Address Bar */}
        <div className="px-4 py-2 border-t border-slate-700/30">
          <div className="flex items-center gap-2">
            <div className="flex-1 bg-slate-800 rounded-lg px-4 py-2 border border-slate-600">
              <input
                type="text"
                value={tabs.find(tab => tab.isActive)?.url || ''}
                className="w-full bg-transparent text-slate-200 placeholder-slate-400 outline-none"
                placeholder="Enter URL..."
              />
            </div>
            <button className={buttonVariants({ intent: 'primary', size: 'md' })}>
              Go
            </button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 p-6">
        {tabs.map((tab) => (
          tab.isActive && (
            <div key={tab.id} className="max-w-6xl mx-auto">
              <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700/50">
                <h1 className="text-3xl font-bold text-amber-400 mb-6">
                  {tab.title}
                </h1>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {/* Live Metrics */}
                  <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-600/50">
                    <h3 className="text-lg font-semibold text-amber-300 mb-3">Live Metrics</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">CPU Usage:</span>
                        <span className="text-green-400">23%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Memory:</span>
                        <span className="text-blue-400">4.2 GB</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Network:</span>
                        <span className="text-purple-400">1.2 MB/s</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Active Users:</span>
                        <span className="text-amber-400">1,247</span>
                      </div>
                    </div>
                  </div>

                  {/* Status Panel */}
                  <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-600/50">
                    <h3 className="text-lg font-semibold text-amber-300 mb-3">System Status</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-slate-300">Web Services</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-slate-300">Database</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                        <span className="text-slate-300">API Gateway</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-slate-300">CDN</span>
                      </div>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-600/50">
                    <h3 className="text-lg font-semibold text-amber-300 mb-3">Quick Actions</h3>
                    <div className="space-y-2">
                      <button className={buttonVariants({ intent: 'secondary', size: 'sm' })}>
                        Deploy Latest
                      </button>
                      <button className={buttonVariants({ intent: 'secondary', size: 'sm' })}>
                        View Logs
                      </button>
                      <button className={buttonVariants({ intent: 'secondary', size: 'sm' })}>
                        Run Tests
                      </button>
                      <button className={buttonVariants({ intent: 'secondary', size: 'sm' })}>
                        Backup Data
                      </button>
                    </div>
                  </div>
                </div>

                {/* Main Content Area */}
                <div className="mt-8 bg-slate-900/30 rounded-lg p-6 border border-slate-600/30">
                  <h2 className="text-xl font-semibold text-slate-200 mb-4">
                    Welcome to {tab.title}
                  </h2>
                  <p className="text-slate-400 leading-relaxed">
                    This is the content area for {tab.title}. The EuroWeb platform provides
                    industrial-grade web development tools and infrastructure for modern
                    applications. Built with TypeScript, Next.js, and a pure CSS module
                    architecture for maximum performance and maintainability.
                  </p>
                  
                  <div className="mt-6 flex gap-4">
                    <button className={buttonVariants({ intent: 'primary' })}>
                      Get Started
                    </button>
                    <button className={buttonVariants({ intent: 'secondary' })}>
                      Learn More
                    </button>
                    <button className={buttonVariants({ intent: 'ghost' })}>
                      Documentation
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )
        ))}
      </div>
    </div>
  )
}

// Named export only
export { Web8TabSystemMinimal }
