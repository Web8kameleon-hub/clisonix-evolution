'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'

interface SystemStats {
  uptime: string
  modules: number
  apis: number
  labs: number
}

export default function HomePage() {
  const [stats, setStats] = useState<SystemStats>({
    uptime: '0h',
    modules: 4,
    apis: 10,
    labs: 23
  })

  useEffect(() => {
    // Calculate uptime
    const startTime = Date.now()
    const interval = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000)
      const hours = Math.floor(elapsed / 3600)
      const minutes = Math.floor((elapsed % 3600) / 60)
      setStats(prev => ({
        ...prev,
        uptime: `${hours}h ${minutes}m`
      }))
    }, 60000)

    return () => clearInterval(interval)
  }, [])

  const modules = [
    { name: 'EEG Analysis', path: '/modules/eeg-analysis', icon: '🧠', status: 'active' },
    { name: 'Neural Synthesis', path: '/modules/neural-synthesis', icon: '⚡', status: 'active' },
    { name: 'Spectrum Analyzer', path: '/modules/spectrum-analyzer', icon: '📊', status: 'active' },
    { name: 'Neuroacoustic Converter', path: '/modules/neuroacoustic-converter', icon: '🔊', status: 'active' },
  ]

  return (
    <div className="min-h-screen text-white">
      {/* Hero Section */}
      <div className="text-center py-12">
        <h1 className="text-5xl font-black mb-4 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          Clisonix Cloud
        </h1>
        <p className="text-xl text-gray-400 mb-8">
          Advanced Neural & Audio Intelligence Platform
        </p>
        <p className="text-sm text-gray-500">
          By Ledjan Ahmati • 14 months of development
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
        <div className="bg-gradient-to-br from-blue-900 to-blue-800 p-6 rounded-xl border border-blue-700">
          <div className="text-3xl font-bold text-blue-300">{stats.modules}</div>
          <div className="text-sm text-blue-400">Modules</div>
        </div>
        <div className="bg-gradient-to-br from-green-900 to-green-800 p-6 rounded-xl border border-green-700">
          <div className="text-3xl font-bold text-green-300">{stats.apis}</div>
          <div className="text-sm text-green-400">Public APIs</div>
        </div>
        <div className="bg-gradient-to-br from-purple-900 to-purple-800 p-6 rounded-xl border border-purple-700">
          <div className="text-3xl font-bold text-purple-300">{stats.labs}</div>
          <div className="text-sm text-purple-400">Laboratories</div>
        </div>
        <div className="bg-gradient-to-br from-orange-900 to-orange-800 p-6 rounded-xl border border-orange-700">
          <div className="text-3xl font-bold text-orange-300">61</div>
          <div className="text-sm text-orange-400">Alphabet Layers</div>
        </div>
      </div>

      {/* Quick Access Modules */}
      <div className="mb-12">
        <h2 className="text-2xl font-bold mb-6">🚀 Quick Access</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {modules.map((module) => (
            <Link
              key={module.path}
              href={module.path}
              className="bg-gray-800 hover:bg-gray-700 p-6 rounded-xl border border-gray-700 transition-all hover:scale-105"
            >
              <div className="text-3xl mb-3">{module.icon}</div>
              <div className="font-bold text-lg">{module.name}</div>
              <div className="text-xs text-green-400 mt-2">● {module.status}</div>
            </Link>
          ))}
        </div>
      </div>

      {/* System Components */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="font-bold text-lg mb-4">🧠 Ocean Core</h3>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>✅ 14 Expert Personas</li>
            <li>✅ 23 Laboratories</li>
            <li>✅ Auto-Learning Engine</li>
            <li>✅ Response Orchestrator</li>
          </ul>
          <a href="http://localhost:8030/api/docs" target="_blank" className="mt-4 inline-block text-blue-400 hover:text-blue-300 text-sm">
            Open API Docs →
          </a>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="font-bold text-lg mb-4">🔤 Alphabet Layers</h3>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>✅ Greek: 24 letters (α-ω)</li>
            <li>✅ Albanian: 36 letters</li>
            <li>✅ Mathematical functions</li>
            <li>✅ Phonetic properties</li>
          </ul>
        </div>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
          <h3 className="font-bold text-lg mb-4">⚡ ASI Trinity</h3>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>✅ ALBA - EEG Processing</li>
            <li>✅ ALBI - Intelligence</li>
            <li>✅ JONA - Ethics & Coordination</li>
          </ul>
        </div>
      </div>

      {/* Links */}
      <div className="text-center py-8 border-t border-gray-700">
        <div className="flex justify-center gap-6 text-sm">
          <Link href="/modules" className="text-blue-400 hover:text-blue-300">
            All Modules
          </Link>
          <a href="https://clisonix.com" target="_blank" className="text-purple-400 hover:text-purple-300">
            Clisonix.com
          </a>
          <a href="https://vilsonit.com" target="_blank" className="text-green-400 hover:text-green-300">
            Vilsonit.com
          </a>
        </div>
      </div>
    </div>
  )
}
