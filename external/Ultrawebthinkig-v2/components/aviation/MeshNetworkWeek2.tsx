/**
 * Mesh Network Week 2 Demo - Advanced Features
 * 
 * DTN (Delay-Tolerant Networking) + Wi-Fi Direct + 3D Topology
 * Enterprise-grade mesh networking demonstration
 */

'use client';

import {
    Activity,
    AlertTriangle,
    CheckCircle,
    Globe,
    Network,
    Pause,
    Play,
    Radio,
    Send,
    Wifi
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

interface DTNMessage {
    id: string;
    source: string;
    destination: string;
    payload: any;
    status: 'pending' | 'routing' | 'delivered' | 'failed';
    hops: string[];
    timestamp: number;
}

interface WiFiPeer {
    deviceId: string;
    deviceName: string;
    signalStrength: number;
    isConnected: boolean;
    bandwidth: number;
}

interface NetworkStats {
    mesh: {
        totalNodes: number;
        activeNodes: number;
        coverage: number;
        averageLatency: number;
    };
    dtn: {
        storedMessages: number;
        queuedMessages: number;
        totalRoutes: number;
    };
    wifi: {
        connectedPeers: number;
        activeTransfers: number;
        averageBandwidth: number;
    };
}

export default function MeshNetworkWeek2Demo() {
    const [isRunning, setIsRunning] = useState(false);
    const [stats, setStats] = useState<NetworkStats>({
        mesh: { totalNodes: 0, activeNodes: 0, coverage: 0, averageLatency: 0 },
        dtn: { storedMessages: 0, queuedMessages: 0, totalRoutes: 0 },
        wifi: { connectedPeers: 0, activeTransfers: 0, averageBandwidth: 0 }
    });
    const [dtnMessages, setDtnMessages] = useState<DTNMessage[]>([]);
    const [wifiPeers, setWifiPeers] = useState<WiFiPeer[]>([]);
    const [selectedTab, setSelectedTab] = useState<'overview' | 'dtn' | 'wifi' | 'topology'>('overview');
    const [messageText, setMessageText] = useState('');
    const [selectedDestination, setSelectedDestination] = useState('');
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        if (isRunning) {
            const interval = setInterval(updateNetworkData, 2000);
            return () => clearInterval(interval);
        }
    }, [isRunning]);

    const updateNetworkData = async () => {
        try {
            // Simulate API calls to our mesh network endpoints
            const response = await fetch('/api/mesh/advanced?action=status');
            if (response.ok) {
                const data = await response.json();
                setStats({
                    mesh: data.mesh,
                    dtn: data.dtn,
                    wifi: data.wifi
                });
            }

            // Update DTN messages
            setDtnMessages(prev => [
                ...prev.slice(-10), // Keep last 10 messages
                generateMockDTNMessage()
            ]);

            // Update Wi-Fi peers
            setWifiPeers(generateMockWiFiPeers());

        } catch (error) {
            console.error('Network update error:', error);
        }
    };

    const generateMockDTNMessage = (): DTNMessage => ({
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
        source: `node-${Math.floor(Math.random() * 10)}`,
        destination: `node-${Math.floor(Math.random() * 10)}`,
        payload: { type: 'sensor_data', value: Math.random() * 100 },
        status: ['pending', 'routing', 'delivered'][Math.floor(Math.random() * 3)] as any,
        hops: [`node-${Math.floor(Math.random() * 5)}`],
        timestamp: Date.now()
    });

    const generateMockWiFiPeers = (): WiFiPeer[] => {
        return Array.from({ length: Math.floor(Math.random() * 5) + 1 }, (_, i) => ({
            deviceId: `device-${i}`,
            deviceName: `Device ${i}`,
            signalStrength: -30 - Math.random() * 40,
            isConnected: Math.random() > 0.5,
            bandwidth: Math.random() * 100 + 50
        }));
    };

    const sendDTNMessage = async () => {
        if (!messageText || !selectedDestination) return;

        try {
            const response = await fetch('/api/mesh/advanced?action=send_message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    destination: selectedDestination,
                    payload: { text: messageText, type: 'user_message' },
                    options: { priority: 'medium', requiresAck: true }
                })
            });

            if (response.ok) {
                setMessageText('');
                alert('DTN message sent successfully!');
            }
        } catch (error) {
            console.error('Send message error:', error);
        }
    };

    const toggleNetworkOperation = () => {
        setIsRunning(!isRunning);
    };

    const getStatusColor = (value: number, good: number, warn: number) => {
        if (value >= good) return 'text-green-400';
        if (value >= warn) return 'text-yellow-400';
        return 'text-red-400';
    };

    return (
        <div className="w-full max-w-7xl mx-auto p-6 space-y-6 bg-gray-900 text-white">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
                        Mesh Network Week 2
                    </h1>
                    <p className="text-gray-400 mt-2">
                        DTN + Wi-Fi Direct + Advanced Topology Analytics
                    </p>
                </div>

                <div className="flex items-center gap-4">
                    <button
                        onClick={toggleNetworkOperation}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${isRunning
                                ? 'bg-red-600 hover:bg-red-700'
                                : 'bg-green-600 hover:bg-green-700'
                            }`}
                    >
                        {isRunning ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        {isRunning ? 'Stop Network' : 'Start Network'}
                    </button>

                    <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-sm ${isRunning ? 'bg-green-900 text-green-300' : 'bg-gray-700 text-gray-300'
                        }`}>
                        <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-green-400' : 'bg-gray-500'}`} />
                        {isRunning ? 'OPERATIONAL' : 'OFFLINE'}
                    </div>
                </div>
            </div>

            {/* Stats Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <div className="flex items-center gap-3 mb-4">
                        <Network className="w-8 h-8 text-blue-400" />
                        <h3 className="text-xl font-semibold">Mesh Network</h3>
                    </div>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Nodes:</span>
                            <span className={getStatusColor(stats.mesh.activeNodes, 15, 10)}>
                                {stats.mesh.activeNodes}/{stats.mesh.totalNodes}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Coverage:</span>
                            <span className={getStatusColor(stats.mesh.coverage, 80, 60)}>
                                {stats.mesh.coverage.toFixed(1)}%
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Latency:</span>
                            <span className={getStatusColor(100 - stats.mesh.averageLatency, 80, 60)}>
                                {stats.mesh.averageLatency.toFixed(1)}ms
                            </span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <div className="flex items-center gap-3 mb-4">
                        <Radio className="w-8 h-8 text-orange-400" />
                        <h3 className="text-xl font-semibold">DTN System</h3>
                    </div>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Stored:</span>
                            <span className="text-white">{stats.dtn.storedMessages}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Queued:</span>
                            <span className={getStatusColor(100 - stats.dtn.queuedMessages, 80, 60)}>
                                {stats.dtn.queuedMessages}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Routes:</span>
                            <span className="text-white">{stats.dtn.totalRoutes}</span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                    <div className="flex items-center gap-3 mb-4">
                        <Wifi className="w-8 h-8 text-green-400" />
                        <h3 className="text-xl font-semibold">Wi-Fi Direct</h3>
                    </div>
                    <div className="space-y-3">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Peers:</span>
                            <span className="text-white">{stats.wifi.connectedPeers}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Transfers:</span>
                            <span className="text-white">{stats.wifi.activeTransfers}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Bandwidth:</span>
                            <span className="text-white">{stats.wifi.averageBandwidth.toFixed(1)} Mbps</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tab Navigation */}
            <div className="flex space-x-1 bg-gray-800 p-1 rounded-lg">
                {[
                    { id: 'overview', label: 'Overview', icon: Activity },
                    { id: 'dtn', label: 'DTN Messages', icon: Radio },
                    { id: 'wifi', label: 'Wi-Fi Direct', icon: Wifi },
                    { id: 'topology', label: '3D Topology', icon: Globe }
                ].map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setSelectedTab(tab.id as any)}
                        className={`flex items-center gap-2 px-4 py-2 rounded-md transition-colors ${selectedTab === tab.id
                                ? 'bg-blue-600 text-white'
                                : 'text-gray-400 hover:text-white hover:bg-gray-700'
                            }`}
                    >
                        <tab.icon className="w-4 h-4" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
                {selectedTab === 'overview' && (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold">Network Overview</h2>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold">System Status</h3>
                                <div className="space-y-3">
                                    <div className="flex items-center gap-3">
                                        <CheckCircle className="w-5 h-5 text-green-400" />
                                        <span>DTN Engine operational</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <CheckCircle className="w-5 h-5 text-green-400" />
                                        <span>Wi-Fi Direct bridge active</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <CheckCircle className="w-5 h-5 text-green-400" />
                                        <span>Mesh topology stable</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <AlertTriangle className="w-5 h-5 text-yellow-400" />
                                        <span>Some nodes reporting high latency</span>
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold">Performance Metrics</h3>
                                <div className="space-y-3">
                                    <div>
                                        <div className="flex justify-between mb-1">
                                            <span>Network Reliability</span>
                                            <span>87%</span>
                                        </div>
                                        <div className="w-full bg-gray-700 rounded-full h-2">
                                            <div className="bg-green-400 h-2 rounded-full" style={{ width: '87%' }} />
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between mb-1">
                                            <span>DTN Efficiency</span>
                                            <span>92%</span>
                                        </div>
                                        <div className="w-full bg-gray-700 rounded-full h-2">
                                            <div className="bg-blue-400 h-2 rounded-full" style={{ width: '92%' }} />
                                        </div>
                                    </div>
                                    <div>
                                        <div className="flex justify-between mb-1">
                                            <span>Wi-Fi Direct Utilization</span>
                                            <span>65%</span>
                                        </div>
                                        <div className="w-full bg-gray-700 rounded-full h-2">
                                            <div className="bg-purple-400 h-2 rounded-full" style={{ width: '65%' }} />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {selectedTab === 'dtn' && (
                    <div className="space-y-6">
                        <div className="flex items-center justify-between">
                            <h2 className="text-2xl font-bold">DTN Message System</h2>
                            <div className="flex gap-3">
                                <input
                                    type="text"
                                    placeholder="Message text..."
                                    value={messageText}
                                    onChange={(e) => setMessageText(e.target.value)}
                                    className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                />
                                <select
                                    value={selectedDestination}
                                    onChange={(e) => setSelectedDestination(e.target.value)}
                                    className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                                >
                                    <option value="">Select destination...</option>
                                    {Array.from({ length: 10 }, (_, i) => (
                                        <option key={i} value={`node-${i}`}>Node {i}</option>
                                    ))}
                                </select>
                                <button
                                    onClick={sendDTNMessage}
                                    className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 rounded-lg transition-colors"
                                >
                                    <Send className="w-4 h-4" />
                                    Send
                                </button>
                            </div>
                        </div>

                        <div className="space-y-3">
                            <h3 className="text-lg font-semibold">Recent Messages</h3>
                            <div className="space-y-2 max-h-96 overflow-y-auto">
                                {dtnMessages.map(msg => (
                                    <div key={msg.id} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                                        <div>
                                            <div className="font-medium">{msg.source} → {msg.destination}</div>
                                            <div className="text-sm text-gray-400">
                                                {typeof msg.payload === 'object' ? JSON.stringify(msg.payload) : msg.payload}
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <div className={`px-2 py-1 rounded text-xs ${msg.status === 'delivered' ? 'bg-green-900 text-green-300' :
                                                    msg.status === 'routing' ? 'bg-blue-900 text-blue-300' :
                                                        msg.status === 'failed' ? 'bg-red-900 text-red-300' :
                                                            'bg-yellow-900 text-yellow-300'
                                                }`}>
                                                {msg.status}
                                            </div>
                                            <div className="text-xs text-gray-400 mt-1">
                                                {msg.hops.length} hops
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {selectedTab === 'wifi' && (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold">Wi-Fi Direct Network</h2>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold">Discovered Peers</h3>
                                <div className="space-y-2">
                                    {wifiPeers.map(peer => (
                                        <div key={peer.deviceId} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                                            <div>
                                                <div className="font-medium">{peer.deviceName}</div>
                                                <div className="text-sm text-gray-400">{peer.deviceId}</div>
                                            </div>
                                            <div className="text-right">
                                                <div className={`px-2 py-1 rounded text-xs ${peer.isConnected ? 'bg-green-900 text-green-300' : 'bg-gray-600 text-gray-300'
                                                    }`}>
                                                    {peer.isConnected ? 'Connected' : 'Available'}
                                                </div>
                                                <div className="text-xs text-gray-400 mt-1">
                                                    {peer.signalStrength} dBm • {peer.bandwidth.toFixed(0)} Mbps
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="space-y-4">
                                <h3 className="text-lg font-semibold">Transfer Statistics</h3>
                                <div className="space-y-3">
                                    <div className="p-3 bg-gray-700 rounded-lg">
                                        <div className="text-sm text-gray-400">Total Data Transferred</div>
                                        <div className="text-2xl font-bold">2.3 GB</div>
                                    </div>
                                    <div className="p-3 bg-gray-700 rounded-lg">
                                        <div className="text-sm text-gray-400">Average Speed</div>
                                        <div className="text-2xl font-bold">85.4 Mbps</div>
                                    </div>
                                    <div className="p-3 bg-gray-700 rounded-lg">
                                        <div className="text-sm text-gray-400">Success Rate</div>
                                        <div className="text-2xl font-bold">98.2%</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {selectedTab === 'topology' && (
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold">3D Network Topology</h2>

                        <div className="bg-gray-900 rounded-lg border border-gray-600 p-4">
                            <canvas
                                ref={canvasRef}
                                width={800}
                                height={400}
                                className="w-full h-96 border border-gray-600 rounded"
                                style={{ background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)' }}
                            />
                            <div className="flex justify-center gap-4 mt-4 text-sm">
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 bg-green-400 rounded-full" />
                                    <span>Gateway Nodes</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 bg-blue-400 rounded-full" />
                                    <span>Relay Nodes</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-3 bg-purple-400 rounded-full" />
                                    <span>Endpoint Nodes</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <div className="w-3 h-1 bg-orange-400" />
                                    <span>Active Links</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
