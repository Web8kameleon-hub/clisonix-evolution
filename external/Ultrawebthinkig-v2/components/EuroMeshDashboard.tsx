/**
 * EuroMesh Network Dashboard - 12 Layer Visualization
 * Dashboard i Rrjetit EuroMesh - Vizualizim 12 Shtresash
 * 
 * Advanced mesh network monitoring and control interface
 * Ndërfaqe e avancuar për monitorim dhe kontroll rrjeti mesh
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import EuroMeshEngine, { 
  NetworkTopology, 
  MeshNode, 
  NetworkLayer, 
  Connection, 
  NetworkEvent 
} from '../lib/euroMeshEngine';

interface LayerVisualization {
  layer: NetworkLayer;
  isExpanded: boolean;
  nodes: MeshNode[];
}

const EuroMeshDashboard: React.FC = () => {
  const [topology, setTopology] = useState<NetworkTopology | null>(null);
  const [selectedLayer, setSelectedLayer] = useState<number>(1);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);
  const [isEngineRunning, setIsEngineRunning] = useState(false);
  const [events, setEvents] = useState<NetworkEvent[]>([]);
  const [layerVisibility, setLayerVisibility] = useState<Record<number, boolean>>({});
  const [networkView, setNetworkView] = useState<'layers' | 'topology' | 'performance'>('layers');
  const [autoOptimize, setAutoOptimize] = useState(false);
  const [agiStatus, setAgiStatus] = useState<{
    active: boolean;
    optimizing: boolean;
    overall: number;
    lastOptimization: string | null;
  }>({
    active: false,
    optimizing: false,
    overall: 0,
    lastOptimization: null
  });
  
  const engineRef = useRef<EuroMeshEngine | null>(null);

  useEffect(() => {
    // Initialize EuroMesh Engine
    engineRef.current = new EuroMeshEngine();
    
    // Set up event listeners
    engineRef.current.on('network_update', (newTopology: NetworkTopology) => {
      setTopology(newTopology);
    });

    engineRef.current.on('network_event', (event: NetworkEvent) => {
      setEvents(prev => [event, ...prev].slice(0, 50));
    });

    engineRef.current.on('engine_started', () => {
      setIsEngineRunning(true);
    });

    engineRef.current.on('engine_stopped', () => {
      setIsEngineRunning(false);
    });

    // Initialize layer visibility
    const initialVisibility: Record<number, boolean> = {};
    for (let i = 1; i <= 12; i++) {
      initialVisibility[i] = true;
    }
    setLayerVisibility(initialVisibility);

    // Get initial topology
    setTopology(engineRef.current.getTopology());

    return () => {
      if (engineRef.current) {
        engineRef.current.stop();
        engineRef.current.removeAllListeners();
      }
    };
  }, []);

  const toggleEngine = () => {
    if (!engineRef.current) return;
    
    if (isEngineRunning) {
      engineRef.current.stop();
    } else {
      engineRef.current.start();
    }
  };

  const optimizeNetwork = async () => {
    if (!engineRef.current) return;
    
    try {
      await engineRef.current.optimizeNetwork();
    } catch (error) {
      console.error('Network optimization failed:', error);
    }
  };

  const activateAllNodes = async () => {
    if (!engineRef.current) return;
    
    try {
      await engineRef.current.activateAllNodes();
    } catch (error) {
      console.error('Node activation failed:', error);
    }
  };

  const activateAGI = async () => {
    if (agiStatus.optimizing) return;
    
    setAgiStatus(prev => ({ ...prev, optimizing: true }));
    
    try {
      console.log('🚀 Starting AGI Ultra activation...');
      
      const response = await fetch('/api/agi/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        setAgiStatus({
          active: true,
          optimizing: false,
          overall: result.status.overall,
          lastOptimization: result.timestamp
        });
        
        // Add AGI activation event to network events
        const agiEvent: NetworkEvent = {
          id: `agi-activation-${Date.now()}`,
          type: 'route_change',
          severity: 'info',
          message: 'AGI Ultra activated - All systems optimized and enhanced',
          timestamp: new Date(),
          affectedNodes: []
        };
        
        setEvents(prev => [agiEvent, ...prev].slice(0, 50));
        
        console.log('✅ AGI Ultra activated successfully!');
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('AGI activation failed:', error);
      setAgiStatus(prev => ({ ...prev, optimizing: false }));
    }
  };

  const runRealAnalysis = async () => {
    try {
      console.log('🔍 Starting real system analysis...');
      
      const response = await fetch('/api/agi/real-analysis', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const result = await response.json();
      
      if (result.success) {
        // Add analysis event to network events
        const analysisEvent: NetworkEvent = {
          id: `real-analysis-${Date.now()}`,
          type: 'performance_alert',
          severity: 'info',
          message: `Real analysis complete: ${result.analysis.healthyModules}/${result.analysis.totalModules} modules healthy, ${result.data.systemHealth}% system health`,
          timestamp: new Date(),
          affectedNodes: []
        };
        
        setEvents(prev => [analysisEvent, ...prev].slice(0, 50));
        
        console.log('✅ Real analysis completed:', result.data);
        console.log('📊 System Health:', result.data.systemHealth + '%');
        console.log('📈 Average Performance:', result.analysis.averagePerformance + '%');
        console.log('⚡ Optimizations:', result.data.optimizations);
        
        // Show alert with key metrics
        alert(`🔍 Real System Analysis Complete!\n\n` +
              `System Health: ${result.data.systemHealth}%\n` +
              `Healthy Modules: ${result.analysis.healthyModules}/${result.analysis.totalModules}\n` +
              `Average Performance: ${result.analysis.averagePerformance}%\n` +
              `Memory Efficiency: ${result.analysis.memoryEfficiency}%\n` +
              `Uptime: ${Math.round(result.analysis.systemUptime)}s\n\n` +
              `Optimizations Found: ${result.data.optimizations.length}\n` +
              `Recommendations: ${result.data.recommendations.length}`);
      } else {
        throw new Error(result.message);
      }
    } catch (error) {
      console.error('Real analysis failed:', error);
      alert('❌ Real analysis failed: ' + error);
    }
  };

  const sendNodeCommand = async (nodeId: string, command: any) => {
    if (!engineRef.current) return;
    
    try {
      await engineRef.current.sendCommand(nodeId, command);
    } catch (error) {
      console.error('Command failed:', error);
    }
  };

  const getLayerColor = (layerNum: number): string => {
    const colors = [
      'from-red-500 to-red-700',      // Physical
      'from-orange-500 to-orange-700', // Data Link
      'from-yellow-500 to-yellow-700', // Network
      'from-green-500 to-green-700',   // Transport
      'from-teal-500 to-teal-700',     // Session
      'from-blue-500 to-blue-700',     // Presentation
      'from-indigo-500 to-indigo-700', // Application
      'from-purple-500 to-purple-700', // Mesh
      'from-pink-500 to-pink-700',     // Analytics
      'from-rose-500 to-rose-700',     // Management
      'from-cyan-500 to-cyan-700',     // Security
      'from-emerald-500 to-emerald-700' // AI Intelligence
    ];
    return colors[layerNum - 1] || 'from-gray-500 to-gray-700';
  };

  const getNodeStatusColor = (status: string): string => {
    switch (status) {
      case 'online': return 'text-green-400 bg-green-900/30';
      case 'offline': return 'text-red-400 bg-red-900/30';
      case 'degraded': return 'text-yellow-400 bg-yellow-900/30';
      case 'maintenance': return 'text-blue-400 bg-blue-900/30';
      default: return 'text-gray-400 bg-gray-900/30';
    }
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderLayerView = () => {
    if (!topology) return null;

    return (
      <div className="space-y-4">
        {topology.layers.map((layer, index) => {
          const layerNum = index + 1;
          const isVisible = layerVisibility[layerNum];
          const colorGradient = getLayerColor(layerNum);

          return (
            <motion.div
              key={layer.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800"
            >
              {/* Layer Header */}
              <div 
                className={`p-4 bg-gradient-to-r ${colorGradient} rounded-t-xl cursor-pointer`}
                onClick={() => setLayerVisibility(prev => ({ ...prev, [layerNum]: !isVisible }))}
              >
                <div className="flex items-center justify-between text-white">
                  <div className="flex items-center space-x-3">
                    <div className="text-xl font-bold">L{layerNum}</div>
                    <div>
                      <div className="font-semibold">{layer.name}</div>
                      <div className="text-sm opacity-90">{layer.description}</div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <div className="text-sm">Nodes: {layer.performance.activeNodes}/{layer.performance.totalNodes}</div>
                      <div className="text-sm">Reliability: {layer.performance.reliability.toFixed(1)}%</div>
                    </div>
                    <div className={`transform transition-transform ${isVisible ? 'rotate-180' : ''}`}>
                      ▼
                    </div>
                  </div>
                </div>
              </div>

              {/* Layer Content */}
              <AnimatePresence>
                {isVisible && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="p-4"
                  >
                    {/* Layer Metrics */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                      <div className="bg-gray-800/50 p-3 rounded-lg">
                        <div className="text-sm text-gray-400">Latency</div>
                        <div className="text-lg font-semibold text-white">
                          {layer.performance.averageLatency.toFixed(1)}ms
                        </div>
                      </div>
                      <div className="bg-gray-800/50 p-3 rounded-lg">
                        <div className="text-sm text-gray-400">Throughput</div>
                        <div className="text-lg font-semibold text-white">
                          {layer.performance.totalThroughput.toFixed(1)} Mbps
                        </div>
                      </div>
                      <div className="bg-gray-800/50 p-3 rounded-lg">
                        <div className="text-sm text-gray-400">Coverage</div>
                        <div className="text-lg font-semibold text-white">
                          {layer.performance.coverage.toFixed(1)} km²
                        </div>
                      </div>
                      <div className="bg-gray-800/50 p-3 rounded-lg">
                        <div className="text-sm text-gray-400">Protocol</div>
                        <div className="text-sm font-semibold text-white">
                          {layer.protocol}
                        </div>
                      </div>
                    </div>

                    {/* Nodes Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {layer.nodes.map(node => (
                        <motion.div
                          key={node.id}
                          className={`p-3 rounded-lg border cursor-pointer transition-all ${
                            selectedNode === node.id 
                              ? 'border-blue-500 bg-blue-900/20' 
                              : 'border-gray-700 bg-gray-800/30 hover:border-gray-600'
                          }`}
                          onClick={() => setSelectedNode(node.id)}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <div className="font-medium text-white text-sm">{node.name}</div>
                            <div className={`px-2 py-1 rounded text-xs ${getNodeStatusColor(node.status)}`}>
                              {node.status}
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                            <div>CPU: {node.metrics.cpuUsage.toFixed(1)}%</div>
                            <div>RAM: {node.metrics.memoryUsage.toFixed(1)}%</div>
                            <div>Connections: {node.connections.length}</div>
                            <div>Signal: {node.metrics.signalStrength.toFixed(0)} dBm</div>
                          </div>

                          {node.capabilities.batteryLevel !== undefined && (
                            <div className="mt-2">
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-gray-400">Battery</span>
                                <span className="text-white">{node.capabilities.batteryLevel.toFixed(0)}%</span>
                              </div>
                              <div className="w-full bg-gray-700 rounded-full h-1.5 mt-1">
                                <div 
                                  className={`h-1.5 rounded-full ${
                                    node.capabilities.batteryLevel > 50 ? 'bg-green-500' :
                                    node.capabilities.batteryLevel > 20 ? 'bg-yellow-500' : 'bg-red-500'
                                  }`}
                                  style={{ width: `${node.capabilities.batteryLevel}%` }}
                                />
                              </div>
                            </div>
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    );
  };

  const renderGlobalMetrics = () => {
    if (!topology) return null;

    return (
      <div className="space-y-4">
        {/* Network Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div className="bg-gradient-to-br from-blue-900/50 to-blue-800/30 p-4 rounded-lg border border-blue-700/30">
            <div className="text-sm text-blue-300">Total Nodes</div>
            <div className="text-2xl font-bold text-white">{topology.globalMetrics.totalNodes}</div>
          </div>
          <div className="bg-gradient-to-br from-green-900/50 to-green-800/30 p-4 rounded-lg border border-green-700/30">
            <div className="text-sm text-green-300">Connections</div>
            <div className="text-2xl font-bold text-white">{topology.globalMetrics.totalConnections}</div>
          </div>
          <div className="bg-gradient-to-br from-purple-900/50 to-purple-800/30 p-4 rounded-lg border border-purple-700/30">
            <div className="text-sm text-purple-300">Reliability</div>
            <div className="text-2xl font-bold text-white">{topology.globalMetrics.networkReliability.toFixed(1)}%</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-900/50 to-yellow-800/30 p-4 rounded-lg border border-yellow-700/30">
            <div className="text-sm text-yellow-300">Avg Latency</div>
            <div className="text-2xl font-bold text-white">{topology.globalMetrics.averageLatency.toFixed(1)}ms</div>
          </div>
          <div className="bg-gradient-to-br from-cyan-900/50 to-cyan-800/30 p-4 rounded-lg border border-cyan-700/30">
            <div className="text-sm text-cyan-300">Coverage</div>
            <div className="text-2xl font-bold text-white">{topology.globalMetrics.totalCoverage.toFixed(1)} km²</div>
          </div>
          <div className="bg-gradient-to-br from-emerald-900/50 to-emerald-800/30 p-4 rounded-lg border border-emerald-700/30">
            <div className="text-sm text-emerald-300">Data Flow</div>
            <div className="text-2xl font-bold text-white">{topology.globalMetrics.dataFlow.toFixed(1)} MB/s</div>
          </div>
        </div>

        {/* AGI Status Panel */}
        {agiStatus.active && (
          <div className="bg-gradient-to-r from-purple-900/50 to-pink-900/50 p-6 rounded-lg border border-purple-700/30">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-white flex items-center">
                🧠 AGI Ultra Status
                <span className="ml-2 px-2 py-1 bg-green-600 text-xs rounded-full">ACTIVE</span>
              </h3>
              <div className="text-2xl font-bold text-purple-300">{agiStatus.overall}%</div>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 text-sm">
              <div className="text-center">
                <div className="text-green-400">🧠 DualMind</div>
                <div className="text-green-300 font-medium">✅ Active</div>
              </div>
              <div className="text-center">
                <div className="text-blue-400">💾 Memory</div>
                <div className="text-blue-300 font-medium">✅ Optimized</div>
              </div>
              <div className="text-center">
                <div className="text-yellow-400">🌐 Translator</div>
                <div className="text-yellow-300 font-medium">✅ Enhanced</div>
              </div>
              <div className="text-center">
                <div className="text-cyan-400">📡 LoRa</div>
                <div className="text-cyan-300 font-medium">✅ Connected</div>
              </div>
              <div className="text-center">
                <div className="text-purple-400">🕸️ Mesh</div>
                <div className="text-purple-300 font-medium">✅ Optimized</div>
              </div>
              <div className="text-center">
                <div className="text-emerald-400">🔗 Registry</div>
                <div className="text-emerald-300 font-medium">✅ Synced</div>
              </div>
            </div>
            {agiStatus.lastOptimization && (
              <div className="mt-4 text-sm text-gray-400">
                Last optimization: {new Date(agiStatus.lastOptimization).toLocaleString()}
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="p-6 space-y-6 min-h-screen">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">EuroMesh Network Dashboard</h1>
          <p className="text-gray-400">12-Layer Advanced Mesh Network Architecture</p>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* Engine Control */}
          <button
            onClick={toggleEngine}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              isEngineRunning 
                ? 'bg-red-600 hover:bg-red-700 text-white' 
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {isEngineRunning ? '🛑 Stop Engine' : '🚀 Start Engine'}
          </button>

          {/* Optimize Button */}
          <button
            onClick={optimizeNetwork}
            disabled={!isEngineRunning}
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors"
          >
            🔧 Optimize Network
          </button>

          {/* Activate All Nodes Button */}
          <button
            onClick={activateAllNodes}
            disabled={!isEngineRunning}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition-colors"
          >
            ⚡ Activate All Nodes
          </button>

          {/* AGI Ultra Activation Button */}
          <button
            onClick={activateAGI}
            disabled={agiStatus.optimizing}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              agiStatus.active 
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white' 
                : 'bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white'
            } ${agiStatus.optimizing ? 'animate-pulse cursor-not-allowed opacity-75' : ''}`}
          >
            {agiStatus.optimizing ? '🔄 Optimizing...' : 
             agiStatus.active ? '🧠 AGI Active' : '🚀 Activate AGI'}
          </button>

          {/* Real Analysis Button */}
          <button
            onClick={runRealAnalysis}
            className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white rounded-lg font-medium transition-colors"
          >
            🔍 Real Analysis
          </button>

          {/* View Selector */}
          <select
            value={networkView}
            onChange={(e) => setNetworkView(e.target.value as any)}
            className="px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white"
          >
            <option value="layers">Layer View</option>
            <option value="topology">Topology View</option>
            <option value="performance">Performance View</option>
          </select>
        </div>
      </div>

      {/* Status Indicator */}
      <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg ${
        isEngineRunning 
          ? 'bg-green-900/30 text-green-400' 
          : 'bg-red-900/30 text-red-400'
      }`}>
        <div className={`w-2 h-2 rounded-full ${
          isEngineRunning ? 'bg-green-400 animate-pulse' : 'bg-red-400'
        }`} />
        <span className="text-sm font-medium">
          Engine: {isEngineRunning ? 'ACTIVE' : 'STOPPED'}
        </span>
        {topology && (
          <span className="text-sm text-gray-400 ml-4">
            Last Update: {new Date().toLocaleTimeString()}
          </span>
        )}
      </div>

      {/* Global Metrics */}
      <div className="mb-6">
        {renderGlobalMetrics()}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Network Visualization */}
        <div className="lg:col-span-3">
          {networkView === 'layers' && renderLayerView()}
          {networkView === 'topology' && (
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Network Topology</h3>
              <div className="text-gray-400">Topology visualization coming soon...</div>
            </div>
          )}
          {networkView === 'performance' && (
            <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 p-6">
              <h3 className="text-xl font-semibold text-white mb-4">Performance Analytics</h3>
              <div className="text-gray-400">Performance charts coming soon...</div>
            </div>
          )}
        </div>

        {/* Events Panel */}
        <div className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 p-6">
          <h3 className="text-xl font-semibold text-white mb-4">Network Events</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            <AnimatePresence>
              {events.map((event, index) => (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className={`p-3 rounded-lg border-l-4 ${
                    event.severity === 'critical' ? 'border-red-500 bg-red-900/20' :
                    event.severity === 'error' ? 'border-orange-500 bg-orange-900/20' :
                    event.severity === 'warning' ? 'border-yellow-500 bg-yellow-900/20' :
                    'border-blue-500 bg-blue-900/20'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className={`text-sm font-medium ${
                      event.severity === 'critical' ? 'text-red-400' :
                      event.severity === 'error' ? 'text-orange-400' :
                      event.severity === 'warning' ? 'text-yellow-400' :
                      'text-blue-400'
                    }`}>
                      {event.type.replace('_', ' ').toUpperCase()}
                    </div>
                    <div className="text-xs text-gray-500">
                      {event.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                  <div className="text-sm text-gray-300">{event.message}</div>
                  {event.affectedNodes.length > 0 && (
                    <div className="text-xs text-gray-500 mt-1">
                      Nodes: {event.affectedNodes.slice(0, 3).join(', ')}
                      {event.affectedNodes.length > 3 && ` +${event.affectedNodes.length - 3} more`}
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
            {events.length === 0 && (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">📡</div>
                <div>No events yet</div>
                <div className="text-sm mt-1">Start the engine to see network activity</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Selected Node Details */}
      {selectedNode && topology && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gray-900/50 backdrop-blur-sm rounded-xl border border-gray-800 p-6"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-white">Node Details</h3>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
          
          {(() => {
            const node = topology.layers.flatMap(l => l.nodes).find(n => n.id === selectedNode);
            if (!node) return <div className="text-gray-400">Node not found</div>;
            
            return (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-white mb-3">Basic Information</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Name:</span>
                      <span className="text-white">{node.name}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Type:</span>
                      <span className="text-white">{node.type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Layer:</span>
                      <span className="text-white">L{node.layer}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Status:</span>
                      <span className={getNodeStatusColor(node.status).split(' ')[0]}>{node.status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Last Seen:</span>
                      <span className="text-white">{node.lastSeen.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-white mb-3">Performance Metrics</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-400">CPU Usage:</span>
                      <span className="text-white">{node.metrics.cpuUsage.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Memory Usage:</span>
                      <span className="text-white">{node.metrics.memoryUsage.toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Network RX:</span>
                      <span className="text-white">{formatBytes(node.metrics.networkTraffic.rx)}/s</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Network TX:</span>
                      <span className="text-white">{formatBytes(node.metrics.networkTraffic.tx)}/s</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Signal Strength:</span>
                      <span className="text-white">{node.metrics.signalStrength.toFixed(0)} dBm</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })()}
        </motion.div>
      )}
    </div>
  );
};

export default EuroMeshDashboard;
