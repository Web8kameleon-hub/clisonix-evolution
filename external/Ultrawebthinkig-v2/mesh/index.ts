/**
 * Mesh Network Module - P2P Communication
 * EuroWeb Platform v8.0.0
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0
 */

export interface MeshNode {
  id: string;
  name: string;
  ip: string;
  port: number;
  status: 'active' | 'inactive' | 'connecting';
  connections: string[];
  bandwidth: number;
  latency: number;
  lastPing: Date;
}

export interface MeshNetwork {
  id: string;
  name: string;
  nodes: MeshNode[];
  topology: 'star' | 'ring' | 'mesh' | 'hybrid';
  totalBandwidth: number;
  activeConnections: number;
}

export interface MeshMessage {
  id: string;
  from: string;
  to: string;
  content: any;
  type: 'data' | 'control' | 'ping' | 'discovery';
  timestamp: Date;
  route: string[];
}

export const MeshManager = {
  // Static implementation for industrial architecture
  networks: [] as MeshNetwork[],
  messages: [] as MeshMessage[],
  
  createNetwork: (name: string, topology: MeshNetwork['topology']): MeshNetwork => {
    const network: MeshNetwork = {
      id: `mesh_${Date.now()}`,
      name,
      nodes: [],
      topology,
      totalBandwidth: 0,
      activeConnections: 0
    };
    MeshManager.networks.push(network);
    return network;
  },
  
  addNode: (networkId: string, node: Omit<MeshNode, 'id' | 'connections' | 'lastPing'>): MeshNode => {
    const newNode: MeshNode = {
      ...node,
      id: `node_${Date.now()}`,
      connections: [],
      lastPing: new Date()
    };
    
    const network = MeshManager.networks.find(n => n.id === networkId);
    if (network) {
      network.nodes.push(newNode);
      network.activeConnections = network.nodes.filter(n => n.status === 'active').length;
      network.totalBandwidth = network.nodes.reduce((sum, n) => sum + (n.status === 'active' ? n.bandwidth : 0), 0);
    }
    
    return newNode;
  },
  
  connectNodes: (networkId: string, nodeId1: string, nodeId2: string): boolean => {
    const network = MeshManager.networks.find(n => n.id === networkId);
    if (!network) return false;
    
    const node1 = network.nodes.find(n => n.id === nodeId1);
    const node2 = network.nodes.find(n => n.id === nodeId2);
    
    if (node1 && node2) {
      if (!node1.connections.includes(nodeId2)) {
        node1.connections.push(nodeId2);
      }
      if (!node2.connections.includes(nodeId1)) {
        node2.connections.push(nodeId1);
      }
      return true;
    }
    
    return false;
  },
  
  sendMessage: (message: Omit<MeshMessage, 'id' | 'timestamp' | 'route'>): MeshMessage => {
    const newMessage: MeshMessage = {
      ...message,
      id: `msg_${Date.now()}`,
      timestamp: new Date(),
      route: [message.from]
    };
    
    MeshManager.messages.push(newMessage);
    return newMessage;
  },
  
  getNetworkHealth: (networkId: string) => {
    const network = MeshManager.networks.find(n => n.id === networkId);
    if (!network) return null;
    
    const activeNodes = network.nodes.filter(n => n.status === 'active').length;
    const totalNodes = network.nodes.length;
    const avgLatency = network.nodes.reduce((sum, n) => sum + n.latency, 0) / totalNodes || 0;
    
    return {
      health: totalNodes > 0 ? (activeNodes / totalNodes) * 100 : 0,
      activeNodes,
      totalNodes,
      avgLatency,
      totalBandwidth: network.totalBandwidth,
      topology: network.topology
    };
  }
};

export default MeshManager;
