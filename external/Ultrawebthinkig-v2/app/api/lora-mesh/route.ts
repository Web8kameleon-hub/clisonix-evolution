/**
 * 🚀 LORA MESH NETWORK API
 * Ultra Industrial Long Range Mesh Communication System
 * 
 * @version 8.0.0
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 */

import { NextResponse } from 'next/server';

interface LoRaNode {
  id: string;
  name: string;
  type: 'gateway' | 'sensor' | 'repeater' | 'end_device';
  status: 'online' | 'offline' | 'weak_signal' | 'maintenance';
  location: {
    latitude: number;
    longitude: number;
    altitude?: number;
    address?: string;
  };
  signalStrength: number;
  batteryLevel?: number;
  lastSeen: string;
  firmware: string;
  frequency: number;
  spreadingFactor: number;
  connectedNodes: string[];
  dataPackets: {
    sent: number;
    received: number;
    failed: number;
  };
}

interface MeshNetworkMetrics {
  totalNodes: number;
  onlineNodes: number;
  networkCoverage: number;
  avgSignalStrength: number;
  totalPacketsToday: number;
  packetSuccessRate: number;
  networkHealth: number;
  meshConnectivity: number;
}

// Mock LoRa Mesh Network Data
const mockNodes: LoRaNode[] = [
  {
    id: 'lora-gateway-001',
    name: 'Primary Gateway Alpha',
    type: 'gateway',
    status: 'online',
    location: {
      latitude: 41.3275,
      longitude: 19.8187,
      altitude: 150,
      address: 'Tirana Central Hub'
    },
    signalStrength: 95,
    lastSeen: new Date().toISOString(),
    firmware: '3.2.1',
    frequency: 868.1,
    spreadingFactor: 7,
    connectedNodes: ['lora-sensor-001', 'lora-sensor-002', 'lora-repeater-001'],
    dataPackets: { sent: 15234, received: 14892, failed: 342 }
  },
  {
    id: 'lora-sensor-001',
    name: 'Environmental Sensor Beta',
    type: 'sensor',
    status: 'online',
    location: {
      latitude: 41.3285,
      longitude: 19.8197,
      altitude: 120,
      address: 'Industrial Zone A'
    },
    signalStrength: 87,
    batteryLevel: 78,
    lastSeen: new Date(Date.now() - 60000).toISOString(),
    firmware: '2.1.5',
    frequency: 868.3,
    spreadingFactor: 9,
    connectedNodes: ['lora-gateway-001'],
    dataPackets: { sent: 2847, received: 156, failed: 23 }
  },
  {
    id: 'lora-repeater-001',
    name: 'Mesh Repeater Gamma',
    type: 'repeater',
    status: 'online',
    location: {
      latitude: 41.3295,
      longitude: 19.8207,
      altitude: 180,
      address: 'Communication Tower 1'
    },
    signalStrength: 92,
    batteryLevel: 85,
    lastSeen: new Date(Date.now() - 30000).toISOString(),
    firmware: '3.1.0',
    frequency: 868.5,
    spreadingFactor: 8,
    connectedNodes: ['lora-gateway-001', 'lora-sensor-002', 'lora-end-001'],
    dataPackets: { sent: 8934, received: 9156, failed: 234 }
  },
  {
    id: 'lora-sensor-002',
    name: 'Security Monitor Delta',
    type: 'sensor',
    status: 'weak_signal',
    location: {
      latitude: 41.3305,
      longitude: 19.8217,
      altitude: 95,
      address: 'Perimeter Fence Section 3'
    },
    signalStrength: 45,
    batteryLevel: 34,
    lastSeen: new Date(Date.now() - 180000).toISOString(),
    firmware: '2.0.8',
    frequency: 868.7,
    spreadingFactor: 12,
    connectedNodes: ['lora-repeater-001'],
    dataPackets: { sent: 1234, received: 89, failed: 156 }
  },
  {
    id: 'lora-end-001',
    name: 'Mobile Unit Epsilon',
    type: 'end_device',
    status: 'offline',
    location: {
      latitude: 41.3265,
      longitude: 19.8177,
      altitude: 110,
      address: 'Mobile Asset Tracker'
    },
    signalStrength: 0,
    batteryLevel: 8,
    lastSeen: new Date(Date.now() - 900000).toISOString(),
    firmware: '1.9.3',
    frequency: 868.9,
    spreadingFactor: 10,
    connectedNodes: [],
    dataPackets: { sent: 567, received: 12, failed: 89 }
  }
];

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action') || 'dashboard';
    const nodeId = searchParams.get('nodeId');
    const type = searchParams.get('type');
    const status = searchParams.get('status');

    switch (action) {
      case 'dashboard':
        const metrics: MeshNetworkMetrics = {
          totalNodes: mockNodes.length,
          onlineNodes: mockNodes.filter(n => n.status === 'online').length,
          networkCoverage: 87.5,
          avgSignalStrength: Math.round(
            mockNodes
              .filter(n => n.status !== 'offline')
              .reduce((sum, n) => sum + n.signalStrength, 0) / 
            mockNodes.filter(n => n.status !== 'offline').length
          ),
          totalPacketsToday: mockNodes.reduce((sum, n) => sum + n.dataPackets.sent + n.dataPackets.received, 0),
          packetSuccessRate: parseFloat(
            (mockNodes.reduce((sum, n) => sum + n.dataPackets.sent + n.dataPackets.received, 0) /
             (mockNodes.reduce((sum, n) => sum + n.dataPackets.sent + n.dataPackets.received + n.dataPackets.failed, 0)) * 100
            ).toFixed(1)
          ),
          networkHealth: 91.3,
          meshConnectivity: 78.9
        };

        return NextResponse.json({
          success: true,
          data: {
            metrics,
            nodes: mockNodes,
            networkTopology: mockNodes.map(n => ({
              id: n.id,
              name: n.name,
              type: n.type,
              position: [n.location.latitude, n.location.longitude],
              connections: n.connectedNodes,
              status: n.status,
              signalStrength: n.signalStrength
            })),
            alerts: mockNodes
              .filter(n => n.status === 'offline' || n.status === 'weak_signal' || (n.batteryLevel && n.batteryLevel < 20))
              .map(n => ({
                id: `alert-${n.id}`,
                nodeId: n.id,
                nodeName: n.name,
                type: n.status === 'offline' ? 'offline' : n.status === 'weak_signal' ? 'signal' : 'battery',
                message: n.status === 'offline' 
                  ? `Node ${n.name} is offline`
                  : n.status === 'weak_signal'
                  ? `Node ${n.name} has weak signal (${n.signalStrength}%)`
                  : `Node ${n.name} has low battery (${n.batteryLevel}%)`,
                severity: n.status === 'offline' ? 'high' : 'medium',
                timestamp: n.lastSeen
              }))
          }
        });

      case 'nodes':
        let filteredNodes = mockNodes;
        
        if (type) {
          filteredNodes = filteredNodes.filter(n => n.type === type);
        }
        
        if (status) {
          filteredNodes = filteredNodes.filter(n => n.status === status);
        }

        return NextResponse.json({
          success: true,
          data: {
            nodes: filteredNodes,
            total: filteredNodes.length
          }
        });

      case 'node':
        if (!nodeId) {
          return NextResponse.json({
            success: false,
            error: 'Node ID required'
          }, { status: 400 });
        }

        const node = mockNodes.find(n => n.id === nodeId);
        if (!node) {
          return NextResponse.json({
            success: false,
            error: 'Node not found'
          }, { status: 404 });
        }

        return NextResponse.json({
          success: true,
          data: {
            node,
            connectedNodesDetails: mockNodes.filter(n => node.connectedNodes.includes(n.id)),
            signalHistory: Array.from({ length: 24 }, (_, i) => ({
              timestamp: new Date(Date.now() - i * 3600000).toISOString(),
              signalStrength: Math.max(0, node.signalStrength + Math.floor(Math.random() * 20) - 10),
              batteryLevel: node.batteryLevel ? Math.max(0, node.batteryLevel + Math.floor(Math.random() * 10) - 5) : undefined
            })).reverse(),
            packetHistory: Array.from({ length: 12 }, (_, i) => ({
              hour: new Date(Date.now() - i * 3600000).getHours(),
              sent: Math.floor(Math.random() * 100) + 50,
              received: Math.floor(Math.random() * 80) + 20,
              failed: Math.floor(Math.random() * 10)
            })).reverse()
          }
        });

      case 'coverage':
        const coverageMap = {
          zones: [
            { id: 'zone-1', name: 'Central Hub', coverage: 95, nodes: 3 },
            { id: 'zone-2', name: 'Industrial Area', coverage: 87, nodes: 2 },
            { id: 'zone-3', name: 'Perimeter', coverage: 72, nodes: 1 },
            { id: 'zone-4', name: 'Remote Locations', coverage: 45, nodes: 1 }
          ],
          overallCoverage: 87.5,
          weakSpots: [
            { location: 'Perimeter Fence Section 3', signalStrength: 45, recommendedAction: 'Add repeater' },
            { location: 'Remote Storage Area', signalStrength: 32, recommendedAction: 'Install gateway' }
          ]
        };

        return NextResponse.json({
          success: true,
          data: coverageMap
        });

      case 'stats':
        const typeStats = {
          gateways: mockNodes.filter(n => n.type === 'gateway').length,
          sensors: mockNodes.filter(n => n.type === 'sensor').length,
          repeaters: mockNodes.filter(n => n.type === 'repeater').length,
          end_devices: mockNodes.filter(n => n.type === 'end_device').length
        };

        const statusStats = {
          online: mockNodes.filter(n => n.status === 'online').length,
          offline: mockNodes.filter(n => n.status === 'offline').length,
          weak_signal: mockNodes.filter(n => n.status === 'weak_signal').length,
          maintenance: mockNodes.filter(n => n.status === 'maintenance').length
        };

        const totalPackets = mockNodes.reduce((sum, n) => sum + n.dataPackets.sent + n.dataPackets.received, 0);
        const totalFailed = mockNodes.reduce((sum, n) => sum + n.dataPackets.failed, 0);
        const successRate = parseFloat(((totalPackets / (totalPackets + totalFailed)) * 100).toFixed(1));

        return NextResponse.json({
          success: true,
          data: {
            typeStats,
            statusStats,
            networkPerformance: {
              totalPackets,
              successRate,
              avgLatency: '45ms',
              bandwidthUsage: '2.3 Mbps'
            }
          }
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action'
        }, { status: 400 });
    }

  } catch (error) {
    console.error('LoRa Mesh API Error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { action, nodeId, data } = body;

    switch (action) {
      case 'configure':
        if (!nodeId) {
          return NextResponse.json({
            success: false,
            error: 'Node ID required'
          }, { status: 400 });
        }

        return NextResponse.json({
          success: true,
          message: 'Node configuration updated',
          data: {
            nodeId,
            updatedFields: Object.keys(data),
            timestamp: new Date().toISOString()
          }
        });

      case 'reset':
        if (!nodeId) {
          return NextResponse.json({
            success: false,
            error: 'Node ID required'
          }, { status: 400 });
        }

        return NextResponse.json({
          success: true,
          message: 'Node reset command sent',
          data: {
            nodeId,
            resetType: data.resetType || 'soft',
            timestamp: new Date().toISOString(),
            estimatedDowntime: '2-5 minutes'
          }
        });

      case 'mesh_optimize':
        return NextResponse.json({
          success: true,
          message: 'Mesh network optimization initiated',
          data: {
            optimization: {
              type: 'topology',
              estimatedImprovement: '15% signal strength',
              affectedNodes: mockNodes.filter(n => n.signalStrength < 70).length,
              duration: '10-15 minutes'
            },
            timestamp: new Date().toISOString()
          }
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action'
        }, { status: 400 });
    }

  } catch (error) {
    console.error('LoRa Mesh API POST Error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 });
  }
}
