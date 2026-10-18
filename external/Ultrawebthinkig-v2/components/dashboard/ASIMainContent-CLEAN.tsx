"use client";

import React from "react";

interface ASIMainContentProps {
  activeView?: string;
  systemStatus?: any;
}

export function ASIMainContent({ activeView, systemStatus }: ASIMainContentProps) {
  return (
    <div className="bg-white min-h-screen p-6">
      {/* Clean Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">ASI Intelligence Hub</h1>
        <p className="text-gray-600">
          Status: <span className="text-green-600">Connected</span> · Mode: <span className="text-green-600">ACTIVE</span>
        </p>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        
        {/* System Status Card */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Active APIs</span>
              <span className="font-medium text-gray-900">247</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Real-time Sources</span>
              <span className="font-medium text-gray-900">1,834</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">AI Requests/sec</span>
              <span className="font-medium text-gray-900">156</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Global Coverage</span>
              <span className="font-medium text-green-600">99.9%</span>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Latency</span>
              <span className="font-medium text-gray-900">89ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">CPU Load</span>
              <span className="font-medium text-gray-900">41%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Memory Usage</span>
              <span className="font-medium text-gray-900">45%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Error Rate</span>
              <span className="font-medium text-green-600">0.01%</span>
            </div>
          </div>
        </div>

        {/* ASI Modules */}
        <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">ASI Modules</h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">ASI Core</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Online</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">ALBA Engine</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Online</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">ALBI System</span>
              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">Warning</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">API Producer</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Online</span>
            </div>
          </div>
        </div>

      </div>

      {/* Navigation Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        
        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="text-center">
            <div className="text-2xl mb-2">🔬</div>
            <h3 className="font-medium text-gray-900">Analytics</h3>
            <p className="text-sm text-gray-600">Data Analysis</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="text-center">
            <div className="text-2xl mb-2">🤖</div>
            <h3 className="font-medium text-gray-900">AI Agents</h3>
            <p className="text-sm text-gray-600">Intelligent Agents</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="text-center">
            <div className="text-2xl mb-2">🔌</div>
            <h3 className="font-medium text-gray-900">API Gateway</h3>
            <p className="text-sm text-gray-600">Service Management</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="text-center">
            <div className="text-2xl mb-2">📊</div>
            <h3 className="font-medium text-gray-900">Real Data</h3>
            <p className="text-sm text-gray-600">Live Information</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="text-center">
            <div className="text-2xl mb-2">🇦🇱</div>
            <h3 className="font-medium text-gray-900">ASI Core</h3>
            <p className="text-sm text-gray-600">Albanian Intelligence</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="text-center">
            <div className="text-2xl mb-2">🏛️</div>
            <h3 className="font-medium text-gray-900">Cultural</h3>
            <p className="text-sm text-gray-600">Heritage & Culture</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="text-center">
            <div className="text-2xl mb-2">🌤️</div>
            <h3 className="font-medium text-gray-900">Weather</h3>
            <p className="text-sm text-gray-600">Climate Data</p>
          </div>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
          <div className="text-center">
            <div className="text-2xl mb-2">💰</div>
            <h3 className="font-medium text-gray-900">Financial</h3>
            <p className="text-sm text-gray-600">Market Data</p>
          </div>
        </div>

      </div>

      {/* Recent Activity */}
      <div className="mt-8 bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm text-gray-900">AGI guard set mode=calm</p>
              <p className="text-xs text-gray-500">2 minutes ago</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm text-gray-900">Registry registered API Producer @3005</p>
              <p className="text-xs text-gray-500">5 minutes ago</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
            <div className="flex-1">
              <p className="text-sm text-gray-900">System performance optimized</p>
              <p className="text-xs text-gray-500">10 minutes ago</p>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
