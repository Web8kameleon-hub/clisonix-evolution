/**
 * EuroWeb Ultra - Advanced Mesh Network 3D Topology Visualization
 * 
 * Professional TypeScript React Component
 * Enterprise-grade mesh network visualization with real-time analytics
 * 
 * @author GitHub Copilot & EuroWeb Ultra Team
 * @version 3.0.0 - Week 2 Implementation
 */

'use client';

import {
    Activity,
    AlertTriangle,
    Bluetooth,
    CheckCircle,
    Globe,
    MapPin,
    Navigation,
    Network,
    Pause,
    Play,
    Radio,
    RotateCcw,
    Smartphone,
    TrendingUp,
    Wifi
} from 'lucide-react';
import React, { useCallback, useEffect, useState } from 'react';

// Enterprise-Grade TypeScript Interfaces
export interface MeshNetworkNode {
    id: string;
    name: string;
    type: 'gateway' | 'relay' | 'endpoint' | 'bridge';
    position: { lat: number; lon: number; alt?: number };
    status: 'online' | 'offline' | 'warning' | 'error';
    connections: string[];
    capabilities: {
        wifi_direct: boolean;
        bluetooth: boolean;
        lora: boolean;
        cellular: boolean;
        storage_mb: number;
        battery_level?: number;
    };
    traffic: {
        tx_mbps: number;
        rx_mbps: number;
        packets_sent: number;
        packets_received: number;
    };
    metrics: {
        latency: number;
        throughput: number;
        reliability: number;
        uptime: number;
    };
    last_seen: number;
}

export interface MeshNetworkLink {
    id: string;
    source: string;
    target: string;
    type: 'wifi_direct' | 'bluetooth' | 'lora' | 'cellular' | 'satellite';
    quality: {
        signal_strength: number;
        bandwidth_mbps: number;
        latency_ms: number;
        packet_loss: number;
    };
    traffic_flow: number; // 0-1
    is_active: boolean;
    error_rate: number;
}

export interface NetworkAlert {
    id: string;
    type: 'warning' | 'error' | 'info';
    message: string;
    node_id?: string;
    link_id?: string;
    timestamp: number;
    severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface MeshTopologyStats {
    total_nodes: number;
    active_nodes: number;
    total_links: number;
    active_links: number;
    network_throughput: number;
    coverage_area: number;
    fault_tolerance: number;
    avg_latency: number;
    reliability_score: number;
}

export interface VisualizationOptions {
    viewMode: '2d' | '3d';
    showTrafficFlow: boolean;
    showCoverage: boolean;
    showLabels: boolean;
    autoRefresh: boolean;
    refreshInterval: number;
}

// Main Component
const MeshTopology3D: React.FC = () => {
    // State Management
    const [nodes, setNodes] = useState<MeshNetworkNode[]>([]);
    const [links, setLinks] = useState<MeshNetworkLink[]>([]);
    const [alerts, setAlerts] = useState<NetworkAlert[]>([]);
    const [stats, setStats] = useState<MeshTopologyStats>({
        total_nodes: 0,
        active_nodes: 0,
        total_links: 0,
        active_links: 0,
        network_throughput: 0,
        coverage_area: 0,
        fault_tolerance: 0,
        avg_latency: 0,
        reliability_score: 0
    });

    const [selectedNode, setSelectedNode] = useState<MeshNetworkNode | null>(null);
    const [selectedLink, setSelectedLink] = useState<MeshNetworkLink | null>(null);
    const [options, setOptions] = useState<VisualizationOptions>({
        viewMode: '3d',
        showTrafficFlow: true,
        showCoverage: true,
        showLabels: true,
        autoRefresh: true,
        refreshInterval: 3000
    });

    const [isRunning, setIsRunning] = useState(false);

    // Sample Data Generator
    const generateSampleData = useCallback(() => {
        const sampleNodes: MeshNetworkNode[] = [
            {
                id: 'gateway-001',
                name: 'Main Gateway',
                type: 'gateway',
                position: { lat: 41.3275, lon: 19.8187, alt: 100 },
                status: 'online',
                connections: ['relay-001', 'relay-002', 'bridge-001'],
                capabilities: {
                    wifi_direct: true,
                    bluetooth: true,
                    lora: true,
                    cellular: true,
                    storage_mb: 2048,
                    battery_level: 95
                },
                traffic: {
                    tx_mbps: 15.2,
                    rx_mbps: 12.8,
                    packets_sent: 18450,
                    packets_received: 16890
                },
                metrics: {
                    latency: 8.5,
                    throughput: 28.0,
                    reliability: 0.98,
                    uptime: 99.7
                },
                last_seen: Date.now()
            },
            {
                id: 'relay-001',
                name: 'North Relay',
                type: 'relay',
                position: { lat: 41.3350, lon: 19.8300, alt: 50 },
                status: 'online',
                connections: ['gateway-001', 'endpoint-001', 'endpoint-002'],
                capabilities: {
                    wifi_direct: true,
                    bluetooth: true,
                    lora: true,
                    cellular: false,
                    storage_mb: 1024,
                    battery_level: 78
                },
                traffic: {
                    tx_mbps: 8.4,
                    rx_mbps: 9.1,
                    packets_sent: 11420,
                    packets_received: 12890
                },
                metrics: {
                    latency: 12.3,
                    throughput: 17.5,
                    reliability: 0.94,
                    uptime: 98.2
                },
                last_seen: Date.now() - 2000
            },
            {
                id: 'relay-002',
                name: 'South Relay',
                type: 'relay',
                position: { lat: 41.3200, lon: 19.8100, alt: 45 },
                status: 'warning',
                connections: ['gateway-001', 'endpoint-003'],
                capabilities: {
                    wifi_direct: true,
                    bluetooth: true,
                    lora: true,
                    cellular: true,
                    storage_mb: 1024,
                    battery_level: 45
                },
                traffic: {
                    tx_mbps: 3.2,
                    rx_mbps: 4.1,
                    packets_sent: 5420,
                    packets_received: 6150
                },
                metrics: {
                    latency: 18.7,
                    throughput: 7.3,
                    reliability: 0.87,
                    uptime: 95.1
                },
                last_seen: Date.now() - 5000
            },
            {
                id: 'bridge-001',
                name: 'Wi-Fi Bridge',
                type: 'bridge',
                position: { lat: 41.3400, lon: 19.8250, alt: 30 },
                status: 'online',
                connections: ['gateway-001', 'endpoint-004'],
                capabilities: {
                    wifi_direct: true,
                    bluetooth: false,
                    lora: false,
                    cellular: false,
                    storage_mb: 512,
                    battery_level: 88
                },
                traffic: {
                    tx_mbps: 12.8,
                    rx_mbps: 11.2,
                    packets_sent: 8920,
                    packets_received: 8150
                },
                metrics: {
                    latency: 6.2,
                    throughput: 24.0,
                    reliability: 0.96,
                    uptime: 99.1
                },
                last_seen: Date.now() - 1000
            },
            {
                id: 'endpoint-001',
                name: 'Sensor Node A',
                type: 'endpoint',
                position: { lat: 41.3380, lon: 19.8320, alt: 10 },
                status: 'online',
                connections: ['relay-001'],
                capabilities: {
                    wifi_direct: false,
                    bluetooth: true,
                    lora: true,
                    cellular: false,
                    storage_mb: 128,
                    battery_level: 67
                },
                traffic: {
                    tx_mbps: 0.8,
                    rx_mbps: 1.2,
                    packets_sent: 1420,
                    packets_received: 1890
                },
                metrics: {
                    latency: 25.4,
                    throughput: 2.0,
                    reliability: 0.91,
                    uptime: 96.8
                },
                last_seen: Date.now() - 3000
            },
            {
                id: 'endpoint-002',
                name: 'Sensor Node B',
                type: 'endpoint',
                position: { lat: 41.3360, lon: 19.8280, alt: 15 },
                status: 'error',
                connections: ['relay-001'],
                capabilities: {
                    wifi_direct: false,
                    bluetooth: true,
                    lora: false,
                    cellular: false,
                    storage_mb: 64,
                    battery_level: 12
                },
                traffic: {
                    tx_mbps: 0.1,
                    rx_mbps: 0.2,
                    packets_sent: 250,
                    packets_received: 180
                },
                metrics: {
                    latency: 45.2,
                    throughput: 0.3,
                    reliability: 0.72,
                    uptime: 78.4
                },
                last_seen: Date.now() - 15000
            }
        ];

        const sampleLinks: MeshNetworkLink[] = [
            {
                id: 'link-gw-rel1',
                source: 'gateway-001',
                target: 'relay-001',
                type: 'wifi_direct',
                quality: {
                    signal_strength: -42,
                    bandwidth_mbps: 30.0,
                    latency_ms: 8,
                    packet_loss: 0.01
                },
                traffic_flow: 0.6,
                is_active: true,
                error_rate: 0.002
            },
            {
                id: 'link-gw-rel2',
                source: 'gateway-001',
                target: 'relay-002',
                type: 'lora',
                quality: {
                    signal_strength: -68,
                    bandwidth_mbps: 0.3,
                    latency_ms: 45,
                    packet_loss: 0.08
                },
                traffic_flow: 0.3,
                is_active: true,
                error_rate: 0.015
            },
            {
                id: 'link-gw-br1',
                source: 'gateway-001',
                target: 'bridge-001',
                type: 'wifi_direct',
                quality: {
                    signal_strength: -38,
                    bandwidth_mbps: 50.0,
                    latency_ms: 5,
                    packet_loss: 0.005
                },
                traffic_flow: 0.8,
                is_active: true,
                error_rate: 0.001
            },
            {
                id: 'link-rel1-ep1',
                source: 'relay-001',
                target: 'endpoint-001',
                type: 'bluetooth',
                quality: {
                    signal_strength: -55,
                    bandwidth_mbps: 2.1,
                    latency_ms: 20,
                    packet_loss: 0.03
                },
                traffic_flow: 0.4,
                is_active: true,
                error_rate: 0.008
            },
            {
                id: 'link-rel1-ep2',
                source: 'relay-001',
                target: 'endpoint-002',
                type: 'bluetooth',
                quality: {
                    signal_strength: -78,
                    bandwidth_mbps: 0.5,
                    latency_ms: 85,
                    packet_loss: 0.15
                },
                traffic_flow: 0.1,
                is_active: false,
                error_rate: 0.12
            }
        ];

        const sampleAlerts: NetworkAlert[] = [
            {
                id: 'alert-001',
                type: 'warning',
                message: 'Low battery level on endpoint-002',
                node_id: 'endpoint-002',
                timestamp: Date.now() - 120000,
                severity: 'high'
            },
            {
                id: 'alert-002',
                type: 'error',
                message: 'High packet loss on link-rel1-ep2',
                link_id: 'link-rel1-ep2',
                timestamp: Date.now() - 180000,
                severity: 'critical'
            },
            {
                id: 'alert-003',
                type: 'warning',
                message: 'Battery degradation detected on relay-002',
                node_id: 'relay-002',
                timestamp: Date.now() - 300000,
                severity: 'medium'
            }
        ];

        setNodes(sampleNodes);
        setLinks(sampleLinks);
        setAlerts(sampleAlerts);

        // Calculate stats
        const newStats: MeshTopologyStats = {
            total_nodes: sampleNodes.length,
            active_nodes: sampleNodes.filter(n => n.status === 'online').length,
            total_links: sampleLinks.length,
            active_links: sampleLinks.filter(l => l.is_active).length,
            network_throughput: sampleNodes.reduce((sum, n) => sum + n.traffic.tx_mbps, 0),
            coverage_area: 2.8,
            fault_tolerance: 0.85,
            avg_latency: sampleLinks.reduce((sum, l) => sum + l.quality.latency_ms, 0) / sampleLinks.length,
            reliability_score: sampleNodes.reduce((sum, n) => sum + n.metrics.reliability, 0) / sampleNodes.length
        };

        setStats(newStats);
    }, []);

    // Auto-refresh functionality
    useEffect(() => {
        if (!isRunning || !options.autoRefresh) return;

        const interval = setInterval(() => {
            // Simulate real-time updates
            setNodes(prev => prev.map(node => ({
                ...node,
                traffic: {
                    ...node.traffic,
                    tx_mbps: Math.max(0, node.traffic.tx_mbps + (Math.random() - 0.5) * 2),
                    rx_mbps: Math.max(0, node.traffic.rx_mbps + (Math.random() - 0.5) * 2),
                    packets_sent: node.traffic.packets_sent + Math.floor(Math.random() * 100),
                    packets_received: node.traffic.packets_received + Math.floor(Math.random() * 100)
                },
                capabilities: {
                    ...node.capabilities,
                    battery_level: node.capabilities.battery_level ?
                        Math.max(5, node.capabilities.battery_level - Math.random() * 0.5) : undefined
                },
                last_seen: node.status === 'online' ? Date.now() : node.last_seen
            })));

            setLinks(prev => prev.map(link => ({
                ...link,
                traffic_flow: Math.max(0, Math.min(1, link.traffic_flow + (Math.random() - 0.5) * 0.2)),
                quality: {
                    ...link.quality,
                    latency_ms: Math.max(1, link.quality.latency_ms + (Math.random() - 0.5) * 5),
                    packet_loss: Math.max(0, Math.min(0.2, link.quality.packet_loss + (Math.random() - 0.5) * 0.01))
                }
            })));
        }, options.refreshInterval);

        return () => clearInterval(interval);
    }, [isRunning, options.autoRefresh, options.refreshInterval]);

    // Initialize with sample data
    useEffect(() => {
        generateSampleData();
    }, [generateSampleData]);

    // Event Handlers
    const handleToggleRunning = () => {
        setIsRunning(!isRunning);
    };

    const handleOptionChange = (key: keyof VisualizationOptions, value: any) => {
        setOptions(prev => ({ ...prev, [key]: value }));
    };

    const handleNodeSelect = (node: MeshNetworkNode) => {
        setSelectedNode(selectedNode?.id === node.id ? null : node);
        setSelectedLink(null);
    };

    const handleLinkSelect = (link: MeshNetworkLink) => {
        setSelectedLink(selectedLink?.id === link.id ? null : link);
        setSelectedNode(null);
    };

    // Utility Functions
    const getNodeColor = (node: MeshNetworkNode): string => {
        switch (node.status) {
            case 'online': return '#10B981'; // green-500
            case 'warning': return '#F59E0B'; // yellow-500
            case 'error': return '#EF4444'; // red-500
            case 'offline': return '#6B7280'; // gray-500
            default: return '#6B7280';
        }
    };

    const getLinkColor = (link: MeshNetworkLink): string => {
        if (!link.is_active) return '#6B7280';
        if (link.quality.packet_loss > 0.1) return '#EF4444';
        if (link.quality.packet_loss > 0.05) return '#F59E0B';
        return '#10B981';
    };

    const getNodeIcon = (type: string) => {
        switch (type) {
            case 'gateway': return <Globe className="w-5 h-5" />;
            case 'relay': return <Radio className="w-5 h-5" />;
            case 'bridge': return <Wifi className="w-5 h-5" />;
            case 'endpoint': return <Smartphone className="w-5 h-5" />;
            default: return <MapPin className="w-5 h-5" />;
        }
    };

    const getConnectionIcon = (type: string) => {
        switch (type) {
            case 'wifi_direct': return <Wifi className="w-4 h-4" />;
            case 'bluetooth': return <Bluetooth className="w-4 h-4" />;
            case 'lora': return <Radio className="w-4 h-4" />;
            case 'cellular': return <Smartphone className="w-4 h-4" />;
            case 'satellite': return <Globe className="w-4 h-4" />;
            default: return <Activity className="w-4 h-4" />;
        }
    };

    return (
        <div className="w-full max-w-7xl mx-auto p-6 space-y-6 bg-gray-900 text-white">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-3">
                        <Network className="w-8 h-8 text-blue-400" />
                        <div>
                            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
                                Mesh Network 3D Topology
                            </h1>
                            <p className="text-gray-400 mt-1">
                                Enterprise-grade network visualization and analytics
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={handleToggleRunning}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${isRunning
                                ? 'bg-red-600 hover:bg-red-700'
                                : 'bg-green-600 hover:bg-green-700'
                            }`}
                    >
                        {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        {isRunning ? 'Stop' : 'Start'} Network
                    </button>

                    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${isRunning ? 'bg-green-900 text-green-300' : 'bg-gray-700 text-gray-300'
                        }`}>
                        <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-green-400' : 'bg-gray-500'}`} />
                        {isRunning ? 'LIVE' : 'OFFLINE'}
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="flex items-center gap-4 p-4 bg-gray-800 rounded-xl">
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => handleOptionChange('viewMode', '2d')}
                        className={`px-3 py-1 rounded text-sm transition-colors ${options.viewMode === '2d' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                            }`}
                    >
                        2D
                    </button>
                    <button
                        onClick={() => handleOptionChange('viewMode', '3d')}
                        className={`px-3 py-1 rounded text-sm transition-colors ${options.viewMode === '3d' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                            }`}
                    >
                        3D
                    </button>
                </div>

                <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 text-sm">
                        <input
                            type="checkbox"
                            checked={options.showTrafficFlow}
                            onChange={(e) => handleOptionChange('showTrafficFlow', e.target.checked)}
                            className="rounded"
                        />
                        <TrendingUp className="w-4 h-4" />
                        Traffic Flow
                    </label>

                    <label className="flex items-center gap-2 text-sm">
                        <input
                            type="checkbox"
                            checked={options.showCoverage}
                            onChange={(e) => handleOptionChange('showCoverage', e.target.checked)}
                            className="rounded"
                        />
                        <Navigation className="w-4 h-4" />
                        Coverage
                    </label>

                    <label className="flex items-center gap-2 text-sm">
                        <input
                            type="checkbox"
                            checked={options.autoRefresh}
                            onChange={(e) => handleOptionChange('autoRefresh', e.target.checked)}
                            className="rounded"
                        />
                        <RotateCcw className="w-4 h-4" />
                        Auto Refresh
                    </label>
                </div>
            </div>

            {/* Main Visualization Area */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* 3D Topology Visualization */}
                <div className="lg:col-span-3">
                    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
                        <div className="relative w-full h-96 bg-gradient-to-br from-gray-900 via-blue-900 to-gray-800 rounded-lg overflow-hidden">
                            {/* Mock 3D Network Visualization */}
                            <div className="absolute inset-0 p-8">
                                {nodes.map((node, index) => (
                                    <div
                                        key={node.id}
                                        className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300 hover:scale-110 ${selectedNode?.id === node.id ? 'z-20 scale-125' : 'z-10'
                                            }`}
                                        style={{
                                            left: `${20 + index * 15 + Math.cos(index) * 25}%`,
                                            top: `${30 + index * 12 + Math.sin(index) * 20}%`
                                        }}
                                        onClick={() => handleNodeSelect(node)}
                                    >
                                        <div
                                            className={`relative p-3 rounded-full border-2 backdrop-blur-sm transition-all duration-300`}
                                            style={{
                                                backgroundColor: `${getNodeColor(node)}20`,
                                                borderColor: getNodeColor(node)
                                            }}
                                        >
                                            <div className="text-white">
                                                {getNodeIcon(node.type)}
                                            </div>

                                            {/* Node pulse animation */}
                                            <div
                                                className="absolute inset-0 rounded-full animate-ping"
                                                style={{
                                                    backgroundColor: getNodeColor(node),
                                                    animationDuration: '2s'
                                                }}
                                            />

                                            {/* Coverage area */}
                                            {options.showCoverage && (
                                                <div
                                                    className={`absolute inset-0 rounded-full border opacity-30 ${node.type === 'gateway' ? 'scale-[4]' :
                                                            node.type === 'relay' ? 'scale-[3]' :
                                                                node.type === 'bridge' ? 'scale-[2.5]' : 'scale-[2]'
                                                        }`}
                                                    style={{ borderColor: getNodeColor(node) }}
                                                />
                                            )}
                                        </div>

                                        {/* Node label */}
                                        {options.showLabels && (
                                            <div className="absolute top-12 left-1/2 transform -translate-x-1/2 text-white text-xs text-center whitespace-nowrap">
                                                <div className="bg-black/50 px-2 py-1 rounded backdrop-blur-sm">
                                                    {node.name}
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ))}

                                {/* Network Links */}
                                {options.showTrafficFlow && links.map((link, index) => {
                                    const sourceIndex = nodes.findIndex(n => n.id === link.source);
                                    const targetIndex = nodes.findIndex(n => n.id === link.target);

                                    if (sourceIndex === -1 || targetIndex === -1) return null;

                                    const sourcePos = {
                                        x: 20 + sourceIndex * 15 + Math.cos(sourceIndex) * 25,
                                        y: 30 + sourceIndex * 12 + Math.sin(sourceIndex) * 20
                                    };
                                    const targetPos = {
                                        x: 20 + targetIndex * 15 + Math.cos(targetIndex) * 25,
                                        y: 30 + targetIndex * 12 + Math.sin(targetIndex) * 20
                                    };

                                    const length = Math.sqrt(
                                        Math.pow(targetPos.x - sourcePos.x, 2) +
                                        Math.pow(targetPos.y - sourcePos.y, 2)
                                    );
                                    const angle = Math.atan2(targetPos.y - sourcePos.y, targetPos.x - sourcePos.x) * 180 / Math.PI;

                                    return (
                                        <div
                                            key={link.id}
                                            className="absolute cursor-pointer"
                                            style={{
                                                left: `${sourcePos.x}%`,
                                                top: `${sourcePos.y}%`,
                                                width: `${length}%`,
                                                transform: `rotate(${angle}deg)`,
                                                transformOrigin: '0 50%'
                                            }}
                                            onClick={() => handleLinkSelect(link)}
                                        >
                                            <div
                                                className={`h-1 rounded-full transition-all duration-300 ${selectedLink?.id === link.id ? 'h-2 shadow-lg' : ''
                                                    }`}
                                                style={{
                                                    backgroundColor: getLinkColor(link),
                                                    opacity: 0.3 + link.traffic_flow * 0.7
                                                }}
                                            >
                                                {/* Traffic flow animation */}
                                                <div
                                                    className="h-full bg-white/50 rounded-full animate-pulse"
                                                    style={{
                                                        width: `${link.traffic_flow * 100}%`,
                                                        animationDuration: `${2 - link.traffic_flow}s`
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Network Status Overlay */}
                            <div className="absolute top-4 left-4 bg-black/50 backdrop-blur-sm rounded-lg p-3 text-white">
                                <div className="text-sm font-medium mb-2">Network Status</div>
                                <div className="space-y-1 text-xs">
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-green-400 rounded-full" />
                                        <span>{stats.active_nodes} Online</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-yellow-400 rounded-full" />
                                        <span>{nodes.filter(n => n.status === 'warning').length} Warning</span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <div className="w-2 h-2 bg-red-400 rounded-full" />
                                        <span>{nodes.filter(n => n.status === 'error').length} Error</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Side Panel */}
                <div className="space-y-4">
                    {/* Network Statistics */}
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex items-center gap-3 mb-4">
                            <Activity className="w-6 h-6 text-blue-400" />
                            <h3 className="text-lg font-semibold">Network Stats</h3>
                        </div>
                        <div className="space-y-3 text-sm">
                            <div className="flex justify-between">
                                <span className="text-gray-400">Total Nodes:</span>
                                <span className="font-medium">{stats.total_nodes}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Active Links:</span>
                                <span className="font-medium">{stats.active_links}/{stats.total_links}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Throughput:</span>
                                <span className="font-medium">{stats.network_throughput.toFixed(1)} Mbps</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Avg Latency:</span>
                                <span className="font-medium">{stats.avg_latency.toFixed(1)} ms</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Reliability:</span>
                                <span className="font-medium">{(stats.reliability_score * 100).toFixed(1)}%</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-400">Coverage:</span>
                                <span className="font-medium">{stats.coverage_area.toFixed(1)} km²</span>
                            </div>
                        </div>
                    </div>

                    {/* Active Alerts */}
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex items-center gap-3 mb-4">
                            <AlertTriangle className="w-6 h-6 text-yellow-400" />
                            <h3 className="text-lg font-semibold">Active Alerts</h3>
                        </div>
                        <div className="space-y-2">
                            {alerts.length === 0 ? (
                                <div className="text-sm text-gray-400 text-center py-4">
                                    <CheckCircle className="w-6 h-6 text-green-400 mx-auto mb-2" />
                                    No active alerts
                                </div>
                            ) : (
                                alerts.slice(0, 3).map(alert => (
                                    <div
                                        key={alert.id}
                                        className={`p-3 rounded border-l-4 text-xs ${alert.type === 'error' ? 'bg-red-900/20 border-red-400' :
                                                alert.type === 'warning' ? 'bg-yellow-900/20 border-yellow-400' :
                                                    'bg-blue-900/20 border-blue-400'
                                            }`}
                                    >
                                        <div className="font-medium mb-1">{alert.message}</div>
                                        <div className="text-gray-400">
                                            {new Date(alert.timestamp).toLocaleTimeString()}
                                        </div>
                                    </div>
                                ))
                            )}
                        </div>
                    </div>

                    {/* Selected Node Details */}
                    {selectedNode && (
                        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                            <div className="flex items-center gap-3 mb-4">
                                {getNodeIcon(selectedNode.type)}
                                <h3 className="text-lg font-semibold">{selectedNode.name}</h3>
                            </div>
                            <div className="space-y-3 text-sm">
                                <div>
                                    <span className="text-gray-400">Status: </span>
                                    <span className={`font-medium ${selectedNode.status === 'online' ? 'text-green-400' :
                                            selectedNode.status === 'warning' ? 'text-yellow-400' :
                                                selectedNode.status === 'error' ? 'text-red-400' : 'text-gray-400'
                                        }`}>
                                        {selectedNode.status.toUpperCase()}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Type: </span>
                                    <span className="font-medium capitalize">{selectedNode.type}</span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Reliability: </span>
                                    <span className="font-medium">{(selectedNode.metrics.reliability * 100).toFixed(1)}%</span>
                                </div>
                                {selectedNode.capabilities.battery_level && (
                                    <div>
                                        <span className="text-gray-400">Battery: </span>
                                        <span className="font-medium">{selectedNode.capabilities.battery_level.toFixed(0)}%</span>
                                    </div>
                                )}
                                <div>
                                    <span className="text-gray-400">Traffic: </span>
                                    <div className="text-xs mt-1">
                                        TX: {selectedNode.traffic.tx_mbps.toFixed(1)} Mbps<br />
                                        RX: {selectedNode.traffic.rx_mbps.toFixed(1)} Mbps
                                    </div>
                                </div>
                                <div>
                                    <span className="text-gray-400">Capabilities: </span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                        {selectedNode.capabilities.wifi_direct && (
                                            <span className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-xs">WiFi</span>
                                        )}
                                        {selectedNode.capabilities.bluetooth && (
                                            <span className="px-2 py-1 bg-blue-900/50 text-blue-300 rounded text-xs">BT</span>
                                        )}
                                        {selectedNode.capabilities.lora && (
                                            <span className="px-2 py-1 bg-green-900/50 text-green-300 rounded text-xs">LoRa</span>
                                        )}
                                        {selectedNode.capabilities.cellular && (
                                            <span className="px-2 py-1 bg-purple-900/50 text-purple-300 rounded text-xs">Cell</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Selected Link Details */}
                    {selectedLink && (
                        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                            <div className="flex items-center gap-3 mb-4">
                                {getConnectionIcon(selectedLink.type)}
                                <h3 className="text-lg font-semibold">Link Details</h3>
                            </div>
                            <div className="space-y-3 text-sm">
                                <div>
                                    <span className="text-gray-400">Connection: </span>
                                    <div className="text-xs mt-1">{selectedLink.source} ↔ {selectedLink.target}</div>
                                </div>
                                <div>
                                    <span className="text-gray-400">Type: </span>
                                    <span className="font-medium capitalize">{selectedLink.type.replace('_', ' ')}</span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Signal: </span>
                                    <span className={`font-medium ${selectedLink.quality.signal_strength > -50 ? 'text-green-400' :
                                            selectedLink.quality.signal_strength > -70 ? 'text-yellow-400' : 'text-red-400'
                                        }`}>
                                        {selectedLink.quality.signal_strength} dBm
                                    </span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Bandwidth: </span>
                                    <span className="font-medium">{selectedLink.quality.bandwidth_mbps.toFixed(1)} Mbps</span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Latency: </span>
                                    <span className="font-medium">{selectedLink.quality.latency_ms.toFixed(1)} ms</span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Packet Loss: </span>
                                    <span className="font-medium">{(selectedLink.quality.packet_loss * 100).toFixed(2)}%</span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Traffic Load: </span>
                                    <div className="mt-1">
                                        <div className="w-full bg-gray-700 rounded-full h-2">
                                            <div
                                                className="bg-blue-400 h-2 rounded-full transition-all duration-300"
                                                style={{ width: `${selectedLink.traffic_flow * 100}%` }}
                                            />
                                        </div>
                                        <span className="text-xs text-gray-400 mt-1">
                                            {(selectedLink.traffic_flow * 100).toFixed(0)}% utilization
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MeshTopology3D;
