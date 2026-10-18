/**
 * UTT System Test Dashboard
 * EuroWeb Platform - Test Universal Token Transfer system
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.1.0 Ultra
 * @license MIT
 */

'use client'

import React, { useState } from 'react'

export default function TestUTTPage() {
  const [results, setResults] = useState<Record<string, any>>({})
  const [loading, setLoading] = useState<Record<string, boolean>>({})

  const testUTTAPI = async (endpoint: string, name: string, method = 'GET', body?: any) => {
    setLoading(prev => ({ ...prev, [name]: true }))
    try {
      const options: RequestInit = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
      }
      if (body) {
        options.body = JSON.stringify(body)
      }

      const response = await fetch(`/api/utt/${endpoint}`, options)
      const data = await response.json()
      setResults(prev => ({ ...prev, [name]: { success: true, data, status: response.status } }))
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      setResults(prev => ({ ...prev, [name]: { success: false, error: errorMessage } }))
    } finally {
      setLoading(prev => ({ ...prev, [name]: false }))
    }
  }

  const uttTests = [
    { endpoint: 'info', name: 'UTT Info', method: 'GET' },
    { endpoint: 'status', name: 'UTT Status', method: 'GET' },
    { endpoint: 'bridge/status', name: 'Bridge Status', method: 'GET' },
    { endpoint: 'tokens', name: 'Token List', method: 'GET' }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🔗 UTT System Test Dashboard
          </h1>
          <p className="text-xl text-gray-600">
            Universal Token Transfer - System Testing & Validation
          </p>
        </div>
        
        {/* UTT System Info */}
        <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">🏗️ System Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-2xl mb-2">🌉</div>
              <h3 className="font-semibold">Bridge Network</h3>
              <p className="text-sm text-gray-600">Cross-chain token transfers</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl mb-2">🔐</div>
              <h3 className="font-semibold">Security Layer</h3>
              <p className="text-sm text-gray-600">Multi-signature validation</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-2xl mb-2">⚡</div>
              <h3 className="font-semibold">Speed Engine</h3>
              <p className="text-sm text-gray-600">Lightning-fast processing</p>
            </div>
          </div>
        </div>
        
        {/* API Tests */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {uttTests.map(({ endpoint, name, method }) => (
            <div key={name} className="bg-white p-6 rounded-xl shadow-lg">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-800">{name}</h3>
                <button
                  onClick={() => testUTTAPI(endpoint, name, method)}
                  disabled={loading[name]}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                >
                  {loading[name] ? '⏳ Testing...' : '🧪 Test'}
                </button>
              </div>
              
              <div className="mb-4">
                <code className="text-sm bg-gray-100 px-3 py-1 rounded">
                  {method} /api/utt/{endpoint}
                </code>
              </div>
              
              {results[name] && (
                <div className={`p-4 rounded-lg ${results[name].success ? 'bg-green-50 border-l-4 border-green-400' : 'bg-red-50 border-l-4 border-red-400'}`}>
                  <div className="flex items-center mb-2">
                    <span className={`text-sm font-semibold ${results[name].success ? 'text-green-700' : 'text-red-700'}`}>
                      {results[name].success ? '✅ Success' : '❌ Error'}
                    </span>
                    {results[name].status && (
                      <span className="ml-2 text-xs bg-gray-200 px-2 py-1 rounded">
                        HTTP {results[name].status}
                      </span>
                    )}
                  </div>
                  <pre className="text-xs overflow-auto bg-gray-50 p-2 rounded">
                    {JSON.stringify(results[name].data || results[name].error, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
        
        {/* Actions */}
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h3 className="text-xl font-semibold mb-4 text-gray-800">🚀 Bulk Operations</h3>
          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => uttTests.forEach(({ endpoint, name, method }) => testUTTAPI(endpoint, name, method))}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 font-semibold transition-colors"
            >
              🧪 Run All Tests
            </button>
            <button
              onClick={() => setResults({})}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-semibold transition-colors"
            >
              🗑️ Clear Results
            </button>
            <a
              href="/api/utt/docs"
              target="_blank"
              rel="noopener noreferrer"
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-colors"
            >
              📚 API Documentation
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
