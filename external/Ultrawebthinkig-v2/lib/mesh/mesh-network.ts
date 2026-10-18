// Advanced Mesh Network System for EuroWeb Ultra
import { EventEmitter } from 'events';

// Node Types
export enum NodeType {
  GATEWAY = 'gateway',
  RELAY = 'relay',
  END_DEVICE = 'end_device',
  COORDINATOR = 'coordinator',
  BRIDGE = 'bridge',
}

export enum NodeStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  CONNECTING = 'connecting',
  ERROR = 'error',
  MAINTENANCE = 'maintenance',
}

export enum MessagePriority {
  LOW = 0,
  NORMAL = 1,
  HIGH = 2,
  CRITICAL = 3,
  EMERGENCY = 4,
}

// Network Interfaces
export interface NetworkNode {
  id: string;
  type: NodeType;
  status: NodeStatus;
  address: string;
  port: number;
  capabilities: string[];
  metadata: Record<string, any>;
  lastSeen: number;
  connectionCount: number;
  bandwidth: number;
  latency: number;
  reliability: number;
  location?: {
    latitude: number;
    longitude: number;
    altitude?: number;
  };
  routing?: {
    neighbors: string[];
    routes: Record<string, string[]>;
    metrics: Record<string, number>;
  };
}

export interface NetworkMessage {
  id: string;
  from: string;
  to: string;
  type: 'data' | 'control' | 'discovery' | 'heartbeat' | 'agi_request' | 'agi_response';
  priority: MessagePriority;
  payload: any;
  timestamp: number;
  ttl: number;
  hops: string[];
  encrypted: boolean;
  signature?: string;
  ackRequired: boolean;
  retryCount: number;
  maxRetries: number;
}

export interface QoSPolicy {
  bandwidth: {
    min: number;
    max: number;
    guaranteed: number;
  };
  latency: {
    max: number;
    target: number;
  };
  reliability: {
    min: number;
    target: number;
  };
  priority: MessagePriority;
}

export interface NetworkTopology {
  nodes: Map<string, NetworkNode>;
  connections: Map<string, Set<string>>;
  routes: Map<string, Map<string, string[]>>;
  metrics: {
    totalNodes: number;
    activeConnections: number;
    averageLatency: number;
    networkReliability: number;
    throughput: number;
  };
}

class MeshNetworkManager extends EventEmitter {
  private nodes: Map<string, NetworkNode> = new Map();
  private connections: Map<string, Set<string>> = new Map();
  private messageQueue: NetworkMessage[] = [];
  private routingTable: Map<string, Map<string, string[]>> = new Map();
  private qosPolicies: Map<string, QoSPolicy> = new Map();
  private networkMetrics: any = {};
  private discoveryInterval: NodeJS.Timeout | null = null;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private readonly maxMessageQueue = 10000;
  private readonly maxTTL = 10;
  private readonly discoveryIntervalMs = 30000; // 30 seconds
  private readonly heartbeatIntervalMs = 10000; // 10 seconds

  constructor(private nodeId: string, private nodeType: NodeType) {
    super();
    this.initializeLocalNode();
    this.startDiscovery();
    this.startHeartbeat();
  }

  // Node Management
  private initializeLocalNode(): void {
    const localNode: NetworkNode = {
      id: this.nodeId,
      type: this.nodeType,
      status: NodeStatus.ONLINE,
      address: 'localhost',
      port: 3001,
      capabilities: ['agi_processing', 'data_relay', 'mesh_routing'],
      metadata: {
        version: '2.0.0',
        created: Date.now(),
        hardware: process.platform,
        resources: {
          cpu: 'available',
          memory: process.memoryUsage(),
          storage: 'available',
        },
      },
      lastSeen: Date.now(),
      connectionCount: 0,
      bandwidth: 1000, // Mbps
      latency: 0,
      reliability: 1.0,
      routing: {
        neighbors: [],
        routes: {},
        metrics: {},
      },
    };

    this.nodes.set(this.nodeId, localNode);
    this.connections.set(this.nodeId, new Set());
    this.routingTable.set(this.nodeId, new Map());
  }

  // Node Discovery
  async discoverNodes(): Promise<NetworkNode[]> {
    const discoveryMessage: NetworkMessage = {
      id: this.generateMessageId(),
      from: this.nodeId,
      to: 'broadcast',
      type: 'discovery',
      priority: MessagePriority.NORMAL,
      payload: {
        action: 'node_announcement',
        node: this.nodes.get(this.nodeId),
        timestamp: Date.now(),
      },
      timestamp: Date.now(),
      ttl: 3,
      hops: [this.nodeId],
      encrypted: false,
      ackRequired: false,
      retryCount: 0,
      maxRetries: 3,
    };

    await this.broadcastMessage(discoveryMessage);
    return Array.from(this.nodes.values()).filter(node => node.id !== this.nodeId);
  }

  // Connection Management
  async connectToNode(nodeId: string): Promise<boolean> {
    const targetNode = this.nodes.get(nodeId);
    if (!targetNode || targetNode.status !== NodeStatus.ONLINE) {
      return false;
    }

    try {
      // Simulate connection establishment
      const localConnections = this.connections.get(this.nodeId) || new Set();
      const targetConnections = this.connections.get(nodeId) || new Set();

      localConnections.add(nodeId);
      targetConnections.add(this.nodeId);

      this.connections.set(this.nodeId, localConnections);
      this.connections.set(nodeId, targetConnections);

      // Update node connection counts
      const localNode = this.nodes.get(this.nodeId);
      const targetNodeRef = this.nodes.get(nodeId);

      if (localNode) localNode.connectionCount = localConnections.size;
      if (targetNodeRef) targetNodeRef.connectionCount = targetConnections.size;

      // Update routing information
      this.updateRoutingTable(nodeId);

      this.emit('nodeConnected', { localNode: this.nodeId, remoteNode: nodeId });
      return true;
    } catch (error) {
      console.error(`Failed to connect to node ${nodeId}:`, error);
      return false;
    }
  }

  async disconnectFromNode(nodeId: string): Promise<boolean> {
    try {
      const localConnections = this.connections.get(this.nodeId);
      const targetConnections = this.connections.get(nodeId);

      if (localConnections) localConnections.delete(nodeId);
      if (targetConnections) targetConnections.delete(this.nodeId);

      // Update node connection counts
      const localNode = this.nodes.get(this.nodeId);
      const targetNode = this.nodes.get(nodeId);

      if (localNode) localNode.connectionCount = localConnections?.size || 0;
      if (targetNode) targetNode.connectionCount = targetConnections?.size || 0;

      // Update routing table
      this.removeRoutes(nodeId);

      this.emit('nodeDisconnected', { localNode: this.nodeId, remoteNode: nodeId });
      return true;
    } catch (error) {
      console.error(`Failed to disconnect from node ${nodeId}:`, error);
      return false;
    }
  }

  // Message Routing
  async sendMessage(message: NetworkMessage): Promise<boolean> {
    if (message.ttl <= 0) {
      console.warn(`Message ${message.id} TTL expired`);
      return false;
    }

    // Add to message queue
    this.messageQueue.push(message);
    if (this.messageQueue.length > this.maxMessageQueue) {
      this.messageQueue.shift(); // Remove oldest message
    }

    // Find route to destination
    const route = await this.findRoute(message.from, message.to);
    if (!route || route.length === 0) {
      console.warn(`No route found to ${message.to}`);
      return false;
    }

    // Forward message along route
    return await this.forwardMessage(message, route);
  }

  private async forwardMessage(message: NetworkMessage, route: string[]): Promise<boolean> {
    if (route.length === 0) return false;

    const nextHop = route[0];
    const remainingRoute = route.slice(1);

    message.hops.push(nextHop);
    message.ttl--;

    // Check if this is the final destination
    if (nextHop === message.to) {
      return await this.deliverMessage(message);
    }

    // Continue forwarding
    const updatedRoute = remainingRoute;
    return await this.forwardMessage(message, updatedRoute);
  }

  private async deliverMessage(message: NetworkMessage): Promise<boolean> {
    try {
      // Process message based on type
      switch (message.type) {
        case 'agi_request':
          await this.handleAGIRequest(message);
          break;
        case 'agi_response':
          await this.handleAGIResponse(message);
          break;
        case 'discovery':
          await this.handleDiscoveryMessage(message);
          break;
        case 'heartbeat':
          await this.handleHeartbeat(message);
          break;
        case 'control':
          await this.handleControlMessage(message);
          break;
        case 'data':
          await this.handleDataMessage(message);
          break;
      }

      // Send acknowledgment if required
      if (message.ackRequired) {
        await this.sendAcknowledgment(message);
      }

      this.emit('messageDelivered', message);
      return true;
    } catch (error) {
      console.error(`Failed to deliver message ${message.id}:`, error);
      return false;
    }
  }

  // Routing Algorithm
  private async findRoute(from: string, to: string): Promise<string[]> {
    if (from === to) return [to];

    const routes = this.routingTable.get(from);
    if (routes && routes.has(to)) {
      return routes.get(to) || [];
    }

    // Use Dijkstra's algorithm for shortest path
    return this.dijkstraRoute(from, to);
  }

  private dijkstraRoute(start: string, end: string): string[] {
    const distances: Map<string, number> = new Map();
    const previous: Map<string, string | null> = new Map();
    const unvisited: Set<string> = new Set();

    // Initialize distances
    this.nodes.forEach((_, nodeId) => {
      distances.set(nodeId, nodeId === start ? 0 : Infinity);
      previous.set(nodeId, null);
      unvisited.add(nodeId);
    });

    while (unvisited.size > 0) {
      // Find node with minimum distance
      let current: string | null = null;
      let minDistance = Infinity;

      unvisited.forEach(nodeId => {
        const distance = distances.get(nodeId) || Infinity;
        if (distance < minDistance) {
          minDistance = distance;
          current = nodeId;
        }
      });

      if (!current || minDistance === Infinity) break;

      unvisited.delete(current);

      if (current === end) {
        // Reconstruct path
        const path: string[] = [];
        let node: string | null = end;
        while (node) {
          path.unshift(node);
          node = previous.get(node) || null;
        }
        return path.slice(1); // Remove start node
      }

      // Update distances to neighbors
      const neighbors = this.connections.get(current) || new Set();
      neighbors.forEach(neighbor => {
        if (unvisited.has(neighbor)) {
          const neighborNode = this.nodes.get(neighbor);
          const weight = neighborNode ? (1 / neighborNode.reliability) + (neighborNode.latency / 1000) : 1;
          const currentDistance = distances.get(current!) || 0; // current is guaranteed to be non-null here
          const newDistance = currentDistance + weight;

          if (newDistance < (distances.get(neighbor) || Infinity)) {
            distances.set(neighbor, newDistance);
            previous.set(neighbor, current);
          }
        }
      });
    }

    return []; // No route found
  }

  // QoS Management
  setQoSPolicy(nodeId: string, policy: QoSPolicy): void {
    this.qosPolicies.set(nodeId, policy);
    this.emit('qosPolicyUpdated', { nodeId, policy });
  }

  getQoSPolicy(nodeId: string): QoSPolicy | undefined {
    return this.qosPolicies.get(nodeId);
  }

  // Network Monitoring
  async measureLatency(nodeId: string): Promise<number> {
    const startTime = Date.now();
    
    const pingMessage: NetworkMessage = {
      id: this.generateMessageId(),
      from: this.nodeId,
      to: nodeId,
      type: 'control',
      priority: MessagePriority.HIGH,
      payload: { action: 'ping', timestamp: startTime },
      timestamp: startTime,
      ttl: this.maxTTL,
      hops: [this.nodeId],
      encrypted: false,
      ackRequired: true,
      retryCount: 0,
      maxRetries: 3,
    };

    try {
      await this.sendMessage(pingMessage);
      // Wait for response (simulated)
      await new Promise(resolve => setTimeout(resolve, Math.random() * 100 + 10));
      
      const latency = Date.now() - startTime;
      
      // Update node latency
      const node = this.nodes.get(nodeId);
      if (node) {
        node.latency = latency;
      }

      return latency;
    } catch (error) {
      console.error(`Failed to measure latency to ${nodeId}:`, error);
      return -1;
    }
  }

  // Network Topology
  getNetworkTopology(): NetworkTopology {
    const totalNodes = this.nodes.size;
    const activeConnections = Array.from(this.connections.values())
      .reduce((sum, connections) => sum + connections.size, 0) / 2; // Divide by 2 since connections are bidirectional

    const allLatencies = Array.from(this.nodes.values())
      .map(node => node.latency)
      .filter(latency => latency > 0);
    
    const averageLatency = allLatencies.length > 0 
      ? allLatencies.reduce((sum, latency) => sum + latency, 0) / allLatencies.length 
      : 0;

    const allReliabilities = Array.from(this.nodes.values())
      .map(node => node.reliability);
    
    const networkReliability = allReliabilities.length > 0
      ? allReliabilities.reduce((sum, reliability) => sum + reliability, 0) / allReliabilities.length
      : 0;

    return {
      nodes: this.nodes,
      connections: this.connections,
      routes: this.routingTable,
      metrics: {
        totalNodes,
        activeConnections,
        averageLatency,
        networkReliability,
        throughput: this.calculateThroughput(),
      },
    };
  }

  // Message Handlers
  private async handleAGIRequest(message: NetworkMessage): Promise<void> {
    this.emit('agiRequest', message);
  }

  private async handleAGIResponse(message: NetworkMessage): Promise<void> {
    this.emit('agiResponse', message);
  }

  private async handleDiscoveryMessage(message: NetworkMessage): Promise<void> {
    const { action, node } = message.payload;
    
    if (action === 'node_announcement' && node) {
      this.nodes.set(node.id, { ...node, lastSeen: Date.now() });
      this.emit('nodeDiscovered', node);
    }
  }

  private async handleHeartbeat(message: NetworkMessage): Promise<void> {
    const node = this.nodes.get(message.from);
    if (node) {
      node.lastSeen = Date.now();
      node.status = NodeStatus.ONLINE;
    }
  }

  private async handleControlMessage(message: NetworkMessage): Promise<void> {
    this.emit('controlMessage', message);
  }

  private async handleDataMessage(message: NetworkMessage): Promise<void> {
    this.emit('dataMessage', message);
  }

  // Utility Methods
  private generateMessageId(): string {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private async broadcastMessage(message: NetworkMessage): Promise<void> {
    const neighbors = this.connections.get(this.nodeId) || new Set();
    const promises = Array.from(neighbors).map(nodeId =>
      this.sendMessage({ ...message, to: nodeId })
    );
    await Promise.allSettled(promises);
  }

  private async sendAcknowledgment(originalMessage: NetworkMessage): Promise<void> {
    const ackMessage: NetworkMessage = {
      id: this.generateMessageId(),
      from: this.nodeId,
      to: originalMessage.from,
      type: 'control',
      priority: MessagePriority.HIGH,
      payload: { action: 'ack', originalId: originalMessage.id },
      timestamp: Date.now(),
      ttl: this.maxTTL,
      hops: [this.nodeId],
      encrypted: false,
      ackRequired: false,
      retryCount: 0,
      maxRetries: 1,
    };

    await this.sendMessage(ackMessage);
  }

  private updateRoutingTable(nodeId: string): void {
    const routes = this.routingTable.get(this.nodeId) || new Map();
    routes.set(nodeId, [nodeId]);
    this.routingTable.set(this.nodeId, routes);
  }

  private removeRoutes(nodeId: string): void {
    // Remove direct routes to the node
    this.routingTable.forEach(routes => {
      routes.delete(nodeId);
    });

    // Remove routes that go through this node
    this.routingTable.forEach(routes => {
      routes.forEach((route, destination) => {
        if (route.includes(nodeId)) {
          routes.delete(destination);
        }
      });
    });
  }

  private calculateThroughput(): number {
    // Calculate network throughput based on recent message activity
    const recentMessages = this.messageQueue.filter(
      msg => Date.now() - msg.timestamp < 60000 // Last minute
    );
    return recentMessages.length; // Messages per minute
  }

  private startDiscovery(): void {
    this.discoveryInterval = setInterval(() => {
      this.discoverNodes().catch(console.error);
    }, this.discoveryIntervalMs);
  }

  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      const heartbeatMessage: NetworkMessage = {
        id: this.generateMessageId(),
        from: this.nodeId,
        to: 'broadcast',
        type: 'heartbeat',
        priority: MessagePriority.LOW,
        payload: { timestamp: Date.now(), status: NodeStatus.ONLINE },
        timestamp: Date.now(),
        ttl: 2,
        hops: [this.nodeId],
        encrypted: false,
        ackRequired: false,
        retryCount: 0,
        maxRetries: 1,
      };

      this.broadcastMessage(heartbeatMessage).catch(console.error);
    }, this.heartbeatIntervalMs);
  }

  // Cleanup
  shutdown(): void {
    if (this.discoveryInterval) {
      clearInterval(this.discoveryInterval);
    }
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    this.removeAllListeners();
  }
}

// Export singleton instance
export const meshNetwork = new MeshNetworkManager(
  process.env.NODE_ID || `node_${Date.now()}`,
  NodeType.GATEWAY
);

export default meshNetwork;
