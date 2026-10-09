/**
 * ⚙️ Functions Registry Module
 * Complete registry of all Python and Office Script functions
 */

"use client"

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface FunctionEntry {
  name: string
  module: string
  type: 'python' | 'office-script' | 'hybrid'
  parameters: string[]
  returnType: string
  status: 'active' | 'deprecated' | 'experimental'
  description: string
}

export default function FunctionsRegistryPage() {
  const [functions, setFunctions] = useState<FunctionEntry[]>([
    // Python Functions
    { name: 'get_asi_metrics', module: 'asi_core', type: 'python', parameters: ['trinity_id?'], returnType: 'dict', status: 'active', description: 'Get ASI Trinity real-time metrics' },
    { name: 'run_kitchen_pipeline', module: 'protocol_kitchen', type: 'python', parameters: ['input_data', 'layers[]'], returnType: 'ProcessedData', status: 'active', description: 'Run Protocol Kitchen AI pipeline' },
    { name: 'generate_excel_dashboard', module: 'excel_module', type: 'python', parameters: ['api_list', 'output_path'], returnType: 'str', status: 'active', description: 'Generate Excel dashboard with API tracking' },
    { name: 'calculate_health_score', module: 'health_monitor', type: 'python', parameters: ['metrics: dict'], returnType: 'float', status: 'active', description: 'Calculate system health 0-100' },
    { name: 'parse_eeg_signal', module: 'albi_core', type: 'python', parameters: ['signal_data', 'sample_rate'], returnType: 'FrequencyData', status: 'active', description: 'Parse and analyze EEG signals' },
    { name: 'create_neural_pattern', module: 'alba_core', type: 'python', parameters: ['pattern_type', 'intensity'], returnType: 'NeuralPattern', status: 'active', description: 'Create neural pattern for synthesis' },
    { name: 'synthesize_audio', module: 'jona_core', type: 'python', parameters: ['neural_data', 'format'], returnType: 'AudioBuffer', status: 'active', description: 'Synthesize audio from neural data' },
    
    // Office Script Functions  
    { name: 'colorizeAPIRow', module: 'OfficeScripts', type: 'office-script', parameters: ['row: ExcelRow', 'method: string'], returnType: 'void', status: 'active', description: 'Apply color formatting to API row' },
    { name: 'createDropdownList', module: 'OfficeScripts', type: 'office-script', parameters: ['range: string', 'options[]'], returnType: 'void', status: 'active', description: 'Create dropdown validation list' },
    { name: 'syncWithAPI', module: 'OfficeScripts', type: 'office-script', parameters: ['endpoint: string'], returnType: 'ApiResponse', status: 'active', description: 'Sync Excel data with API endpoint' },
    { name: 'generateCurlCommand', module: 'OfficeScripts', type: 'office-script', parameters: ['method', 'url', 'body?'], returnType: 'string', status: 'active', description: 'Generate cURL command from row data' },
    
    // Hybrid Functions
    { name: 'PY_API_CALL', module: 'Excel=PY()', type: 'hybrid', parameters: ['endpoint', 'method', 'params?'], returnType: 'DataFrame', status: 'active', description: 'Excel =PY() formula for API calls' },
    { name: 'PY_HEALTH_CHECK', module: 'Excel=PY()', type: 'hybrid', parameters: ['service_name'], returnType: 'HealthStatus', status: 'active', description: 'Check service health from Excel' },
  ])

  const [filter, setFilter] = useState<'all' | 'python' | 'office-script' | 'hybrid'>('all')
  const [searchTerm, setSearchTerm] = useState('')

  const filteredFunctions = functions.filter(f => {
    const matchesType = filter === 'all' || f.type === filter
    const matchesSearch = f.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         f.description.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesType && matchesSearch
  })

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'python': return 'bg-violet-500'
      case 'office-script': return 'bg-green-500'
      case 'hybrid': return 'bg-purple-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400'
      case 'deprecated': return 'text-red-400'
      case 'experimental': return 'text-yellow-400'
      default: return 'text-gray-400'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <Link href="/modules" className="text-violet-400 hover:text-violet-300 mb-4 inline-block">
          ← Back to Modules
        </Link>
        <h1 className="text-5xl font-bold text-white mb-4 flex items-center justify-center gap-4">
          <span className="text-6xl">⚙️</span>
          Functions Registry
        </h1>
        <p className="text-xl text-gray-300">
          Complete catalog of Python, Office Scripts & Hybrid functions
        </p>
      </div>

      {/* Stats Bar */}
      <div className="max-w-6xl mx-auto mb-8 grid grid-cols-4 gap-4">
        <div className="bg-slate-900/30 rounded-xl p-4 text-center border border-violet-500/30">
          <div className="text-3xl font-bold text-violet-400">{functions.filter(f => f.type === 'python').length}</div>
          <div className="text-sm text-gray-400">Python Functions</div>
        </div>
        <div className="bg-green-900/30 rounded-xl p-4 text-center border border-green-500/30">
          <div className="text-3xl font-bold text-green-400">{functions.filter(f => f.type === 'office-script').length}</div>
          <div className="text-sm text-gray-400">Office Scripts</div>
        </div>
        <div className="bg-purple-900/30 rounded-xl p-4 text-center border border-purple-500/30">
          <div className="text-3xl font-bold text-purple-400">{functions.filter(f => f.type === 'hybrid').length}</div>
          <div className="text-sm text-gray-400">Hybrid =PY()</div>
        </div>
        <div className="bg-slate-900/30 rounded-xl p-4 text-center border border-violet-500/30">
          <div className="text-3xl font-bold text-violet-400">{functions.length}</div>
          <div className="text-sm text-gray-400">Total Functions</div>
        </div>
      </div>

      {/* Filter & Search */}
      <div className="max-w-6xl mx-auto mb-6 flex gap-4">
        <div className="flex gap-2">
          {(['all', 'python', 'office-script', 'hybrid'] as const).map(type => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                filter === type 
                  ? 'bg-violet-600 text-white' 
                  : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
              }`}
            >
              {type === 'all' ? '📋 All' : type === 'python' ? '🐍 Python' : type === 'office-script' ? '📊 Office' : '⚡ Hybrid'}
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="Search functions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 bg-slate-700 text-white px-4 py-2 rounded-lg border border-slate-600 focus:border-violet-500 focus:outline-none"
        />
      </div>

      {/* Functions Table */}
      <div className="max-w-6xl mx-auto bg-slate-800/50 rounded-2xl border border-slate-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-slate-700/50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Function</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Module</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Type</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Parameters</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Return</th>
              <th className="px-4 py-3 text-left text-sm font-semibold text-gray-300">Status</th>
            </tr>
          </thead>
          <tbody>
            {filteredFunctions.map((func, idx) => (
              <tr key={idx} className="border-t border-slate-700 hover:bg-slate-700/30 transition-colors">
                <td className="px-4 py-3">
                  <div className="font-mono text-violet-400">{func.name}()</div>
                  <div className="text-xs text-gray-500 mt-1">{func.description}</div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-400">{func.module}</td>
                <td className="px-4 py-3">
                  <span className={`${getTypeColor(func.type)} text-white text-xs px-2 py-1 rounded-full`}>
                    {func.type}
                  </span>
                </td>
                <td className="px-4 py-3 font-mono text-xs text-gray-400">
                  {func.parameters.join(', ')}
                </td>
                <td className="px-4 py-3 font-mono text-xs text-purple-400">{func.returnType}</td>
                <td className={`px-4 py-3 text-sm ${getStatusColor(func.status)}`}>
                  {func.status === 'active' && '✅'} 
                  {func.status === 'deprecated' && '⚠️'}
                  {func.status === 'experimental' && '🧪'}
                  {' '}{func.status}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Quick Actions */}
      <div className="max-w-6xl mx-auto mt-8 flex justify-center gap-4">
        <button className="px-6 py-3 bg-violet-600 hover:bg-violet-500 text-white rounded-lg font-semibold transition-all flex items-center gap-2">
          🐍 Export Python Stubs
        </button>
        <button className="px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-semibold transition-all flex items-center gap-2">
          📊 Generate TypeScript
        </button>
        <Link 
          href="/modules/excel-dashboard"
          className="px-6 py-3 bg-slate-600 hover:bg-slate-500 text-white rounded-lg font-semibold transition-all flex items-center gap-2"
        >
          📗 Excel Dashboard
        </Link>
      </div>
    </div>
  )
}







