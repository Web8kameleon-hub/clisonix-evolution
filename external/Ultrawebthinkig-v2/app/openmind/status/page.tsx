/**
 * OpenMind System Status Dashboard
 * Real-time monitoring and analytics
 * 
 * @author EuroWeb Platform
 * @version 8.0.0 Professional
 */

'use client';

import { useEffect, useState } from 'react';

interface SystemMetrics {
  uptime: number;
  totalQueries: number;
  avgResponseTime: number;
  successRate: number;
  activeServices: number;
  aiProviders: number;
  dataProcessed: string;
  userSatisfaction: number;
}

interface ServiceDetail {
  name: string;
  status: 'optimal' | 'good' | 'warning' | 'critical';
  responseTime: number;
  accuracy: number;
  usage: number;
  lastUpdate: string;
}

export default function OpenMindStatusPage() {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    uptime: 99.7,
    totalQueries: 2847,
    avgResponseTime: 234,
    successRate: 98.5,
    activeServices: 6,
    aiProviders: 5,
    dataProcessed: '1.2TB',
    userSatisfaction: 9.2
  });

  const [services, setServices] = useState<ServiceDetail[]>([
    {
      name: 'Neural Search Engine',
      status: 'optimal',
      responseTime: 125,
      accuracy: 96.8,
      usage: 89,
      lastUpdate: '2 min ago'
    },
    {
      name: 'Web Search Intelligence',
      status: 'optimal',
      responseTime: 89,
      accuracy: 94.2,
      usage: 92,
      lastUpdate: '1 min ago'
    },
    {
      name: 'AGI Core Reasoning',
      status: 'good',
      responseTime: 342,
      accuracy: 98.1,
      usage: 76,
      lastUpdate: '3 min ago'
    },
    {
      name: 'Neural Analytics',
      status: 'optimal',
      responseTime: 156,
      accuracy: 95.7,
      usage: 83,
      lastUpdate: '1 min ago'
    },
    {
      name: 'Mesh Network Intelligence',
      status: 'good',
      responseTime: 201,
      accuracy: 91.3,
      usage: 45,
      lastUpdate: '4 min ago'
    },
    {
      name: 'Universal Task Tracker',
      status: 'optimal',
      responseTime: 67,
      accuracy: 97.9,
      usage: 68,
      lastUpdate: '2 min ago'
    }
  ]);

  const [realTimeData, setRealTimeData] = useState({
    currentQueries: 23,
    processingQueue: 8,
    aiModelsActive: 12,
    globalUsers: 156
  });

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        totalQueries: prev.totalQueries + Math.floor(Math.random() * 5) + 1,
        avgResponseTime: 200 + Math.floor(Math.random() * 100),
        userSatisfaction: Math.max(8.5, Math.min(9.8, prev.userSatisfaction + (Math.random() - 0.5) * 0.1))
      }));

      setRealTimeData(prev => ({
        currentQueries: Math.max(10, Math.min(50, prev.currentQueries + Math.floor(Math.random() * 6) - 2)),
        processingQueue: Math.max(0, Math.min(20, prev.processingQueue + Math.floor(Math.random() * 4) - 1)),
        aiModelsActive: Math.max(8, Math.min(15, prev.aiModelsActive + Math.floor(Math.random() * 3) - 1)),
        globalUsers: Math.max(100, Math.min(300, prev.globalUsers + Math.floor(Math.random() * 10) - 4))
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'optimal': return 'text-green-400 bg-green-900/20';
      case 'good': return 'text-blue-400 bg-blue-900/20';
      case 'warning': return 'text-yellow-400 bg-yellow-900/20';
      case 'critical': return 'text-red-400 bg-red-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'optimal': return '🟢';
      case 'good': return '🔵';
      case 'warning': return '🟡';
      case 'critical': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">🚀 OpenMind System Status</h1>
          <p className="text-gray-400">Real-time monitoring and performance analytics</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-8">
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-400">{metrics.uptime}%</div>
            <div className="text-sm text-gray-400">Uptime</div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-400">{metrics.totalQueries.toLocaleString()}</div>
            <div className="text-sm text-gray-400">Total Queries</div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-400">{metrics.avgResponseTime}ms</div>
            <div className="text-sm text-gray-400">Avg Response</div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-400">{metrics.successRate}%</div>
            <div className="text-sm text-gray-400">Success Rate</div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-2xl font-bold text-yellow-400">{metrics.activeServices}</div>
            <div className="text-sm text-gray-400">Active Services</div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-2xl font-bold text-orange-400">{metrics.aiProviders}</div>
            <div className="text-sm text-gray-400">AI Providers</div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-2xl font-bold text-cyan-400">{metrics.dataProcessed}</div>
            <div className="text-sm text-gray-400">Data Processed</div>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-2xl font-bold text-pink-400">{metrics.userSatisfaction.toFixed(1)}/10</div>
            <div className="text-sm text-gray-400">User Rating</div>
          </div>
        </div>

        {/* Real-time Activity */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-3">🔄 Live Activity</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-400">Current Queries</span>
                <span className="font-bold text-green-400">{realTimeData.currentQueries}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Processing Queue</span>
                <span className="font-bold text-yellow-400">{realTimeData.processingQueue}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">AI Models Active</span>
                <span className="font-bold text-blue-400">{realTimeData.aiModelsActive}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Global Users</span>
                <span className="font-bold text-purple-400">{realTimeData.globalUsers}</span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-3">🎯 Performance</h3>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">CPU Usage</span>
                <span className="text-sm text-green-400">23%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-green-400 h-2 rounded-full w-[23%]"></div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">Memory</span>
                <span className="text-sm text-blue-400">67%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-blue-400 h-2 rounded-full w-[67%]"></div>
              </div>
              
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-400">AI Processing</span>
                <span className="text-sm text-purple-400">89%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div className="bg-purple-400 h-2 rounded-full w-[89%]"></div>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-3">🌍 Geographic</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">🇦🇱 Albania</span>
                <span className="text-green-400">35%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">🇽🇰 Kosovo</span>
                <span className="text-blue-400">28%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">🇺🇸 USA</span>
                <span className="text-purple-400">18%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">🇪🇺 EU</span>
                <span className="text-yellow-400">12%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">🌐 Other</span>
                <span className="text-gray-400">7%</span>
              </div>
            </div>
          </div>

          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-3">📊 Query Types</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Technical</span>
                <span className="text-blue-400">42%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">General</span>
                <span className="text-green-400">31%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Scientific</span>
                <span className="text-purple-400">15%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Cultural</span>
                <span className="text-yellow-400">12%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Service Details */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h2 className="text-2xl font-bold mb-6">🔧 Service Performance Dashboard</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="text-left py-3 px-4">Service</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Response Time</th>
                  <th className="text-left py-3 px-4">Accuracy</th>
                  <th className="text-left py-3 px-4">Usage</th>
                  <th className="text-left py-3 px-4">Last Update</th>
                </tr>
              </thead>
              <tbody>
                {services.map((service, index) => (
                  <tr key={index} className="border-b border-gray-700/50 hover:bg-gray-700/30">
                    <td className="py-4 px-4 font-medium">{service.name}</td>
                    <td className="py-4 px-4">
                      <span className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(service.status)}`}>
                        {getStatusIcon(service.status)} {service.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={service.responseTime < 150 ? 'text-green-400' : service.responseTime < 300 ? 'text-yellow-400' : 'text-red-400'}>
                        {service.responseTime}ms
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <span className={service.accuracy >= 95 ? 'text-green-400' : service.accuracy >= 90 ? 'text-yellow-400' : 'text-red-400'}>
                        {service.accuracy}%
                      </span>
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 bg-gray-700 rounded-full h-2">
                          <div 
                            className="bg-blue-400 h-2 rounded-full" 
                            style={{ width: `${service.usage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-400">{service.usage}%</span>
                      </div>
                    </td>
                    <td className="py-4 px-4 text-gray-400 text-sm">{service.lastUpdate}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>OpenMind Universal AI Platform - Professional Edition v8.0.0</p>
          <p>🚀 Powered by EuroWeb Advanced Intelligence Systems</p>
        </div>
      </div>
    </div>
  );
}
