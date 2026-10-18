/**
 * Web8 Mesh Network Activator - Node Discovery & Connection Manager
 * Aktivizon dhe lidh të gjithë node-t nga Gjermania deri në Shqipëri
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0 Mesh Network Production
 * @contact dealsjona@gmail.com
 */

import net from 'net';
import { EventEmitter } from 'events';
import crypto from 'crypto';

// Node Types
interface NetworkNode {
  id: string;
  host: string;
  port: number;
  region: 'germany' | 'austria' | 'slovenia' | 'croatia' | 'montenegro' | 'albania' | 'kosova';
  type: 'supernode' | 'relay' | 'client' | 'edge';
  status: 'online' | 'offline' | 'connecting' | 'error';
  lastSeen: number;
  publicKey?: string;
  capabilities: string[];
  latency?: number;
  bandwidth?: number;
}

interface MeshHandshake {
  nodeId: string;
  publicKey: string;
  capabilities: string[];
  timestamp: number;
  signature: string;
}

interface MeshMessage {
  type: 'handshake' | 'telemetry' | 'sync' | 'broadcast' | 'route';
  from: string;
  to: string;
  payload: any;
  timestamp: number;
  signature?: string;
}

class Web8MeshActivator extends EventEmitter {
  private nodes: Map<string, NetworkNode> = new Map();
  private connections: Map<string, net.Socket> = new Map();
  private routingTable: Map<string, string[]> = new Map();
  private privateKey: string;
  private publicKey: string;
  private isActive: boolean = false;

  constructor() {
    super();
    const keyPair = crypto.generateKeyPairSync('rsa', {
      modulusLength: 2048,
      publicKeyEncoding: { type: 'spki', format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });
    
    this.privateKey = keyPair.privateKey;
    this.publicKey = keyPair.publicKey;

    console.log('🔑 Web8 Mesh Activator initialized with RSA keypair');
  }

  /**
   * Aktivizon discovery të të gjithë node-ve në rrjet
   */
  async discoverAndActivateNodes(): Promise<void> {
    console.log('🌐 Starting Web8 Mesh Network Discovery...');
    
    // Pre-configured nodes (Germany to Albania)
    const seedNodes: Partial<NetworkNode>[] = [
      // Germany - Supernodes
      { host: 'de1.euroweb.network', port: 4000, region: 'germany', type: 'supernode' },
      { host: 'de2.euroweb.network', port: 4000, region: 'germany', type: 'supernode' },
      
      // Austria - Relay nodes
      { host: 'at1.euroweb.network', port: 4000, region: 'austria', type: 'relay' },
      
      // Slovenia - Relay nodes
      { host: 'si1.euroweb.network', port: 4000, region: 'slovenia', type: 'relay' },
      
      // Croatia - Relay nodes
      { host: 'hr1.euroweb.network', port: 4000, region: 'croatia', type: 'relay' },
      
      // Montenegro - Edge nodes
      { host: 'me1.euroweb.network', port: 4000, region: 'montenegro', type: 'edge' },
      
      // Albania - Main nodes
      { host: 'al1.euroweb.network', port: 4000, region: 'albania', type: 'supernode' },
      { host: 'al2.euroweb.network', port: 4000, region: 'albania', type: 'relay' },
      
      // Kosova - Edge nodes
      { host: 'xk1.euroweb.network', port: 4000, region: 'kosova', type: 'edge' },
      
      // Local development nodes - DISABLED to avoid self-connection issues
      // { host: 'localhost', port: 3002, region: 'albania', type: 'supernode' },
      { host: '127.0.0.1', port: 4001, region: 'albania', type: 'client' },
    ];

    // Discover and activate each node
    const activationPromises = seedNodes.map(node => this.activateNode(node));
    await Promise.allSettled(activationPromises);

    // Start mesh synchronization
    this.startMeshSync();
    this.isActive = true;

    console.log(`✅ Mesh Network activated with ${this.getActiveNodes().length} nodes online`);
    this.emit('networkActivated', this.getNetworkStatus());
  }

  /**
   * Aktivizon një node të vetëm
   */
  private async activateNode(nodeConfig: Partial<NetworkNode>): Promise<NetworkNode | null> {
    const nodeId = `${nodeConfig.host}:${nodeConfig.port}`;
    
    const node: NetworkNode = {
      id: nodeId,
      host: nodeConfig.host!,
      port: nodeConfig.port!,
      region: nodeConfig.region || 'albania',
      type: nodeConfig.type || 'client',
      status: 'connecting',
      lastSeen: Date.now(),
      capabilities: ['web8', 'agi', 'mesh', 'relay']
    };

    try {
      console.log(`🔌 Connecting to node: ${nodeId}`);
      
      // Test connection
      const isReachable = await this.testNodeConnection(node.host, node.port);
      if (!isReachable) {
        node.status = 'offline';
        this.nodes.set(nodeId, node);
        console.log(`❌ Node ${nodeId} is not reachable`);
        return null;
      }

      // Perform handshake
      const handshakeSuccess = await this.performHandshake(node);
      if (!handshakeSuccess) {
        node.status = 'error';
        this.nodes.set(nodeId, node);
        console.log(`⚠️ Handshake failed with node ${nodeId}`);
        return null;
      }

      node.status = 'online';
      node.lastSeen = Date.now();
      this.nodes.set(nodeId, node);

      console.log(`✅ Node ${nodeId} activated successfully`);
      this.emit('nodeActivated', node);
      
      return node;

    } catch (error) {
      console.error(`❌ Failed to activate node ${nodeId}:`, error);
      node.status = 'error';
      this.nodes.set(nodeId, node);
      return null;
    }
  }

  /**
   * Teston nëse një node është i arritshëm
   */
  private async testNodeConnection(host: string, port: number): Promise<boolean> {
    return new Promise((resolve) => {
      const timeout = setTimeout(() => {
        resolve(false);
      }, 5000); // 5 second timeout

      const socket = net.connect(port, host, () => {
        clearTimeout(timeout);
        socket.end();
        resolve(true);
      });

      socket.on('error', () => {
        clearTimeout(timeout);
        resolve(false);
      });
    });
  }

  /**
   * Kryen handshake me një node
   */
  private async performHandshake(node: NetworkNode): Promise<boolean> {
    return new Promise((resolve) => {
      const socket = net.connect(node.port, node.host);
      let handshakeComplete = false;

      const handshake: MeshHandshake = {
        nodeId: `web8-controller-${Date.now()}`,
        publicKey: this.publicKey,
        capabilities: ['web8', 'agi', 'mesh', 'controller'],
        timestamp: Date.now(),
        signature: this.signData(JSON.stringify({ nodeId: node.id, timestamp: Date.now() }))
      };

      socket.on('connect', () => {
        console.log(`🤝 Initiating handshake with ${node.id}`);
        socket.write(JSON.stringify({
          type: 'handshake',
          payload: handshake
        }) + '\n');
      });

      socket.on('data', (data) => {
        try {
          const response = JSON.parse(data.toString());
          if (response.type === 'handshake_ack') {
            console.log(`🔐 Handshake completed with ${node.id}`);
            node.publicKey = response.payload.publicKey;
            handshakeComplete = true;
            this.connections.set(node.id, socket);
            resolve(true);
          }
        } catch (error) {
          console.error(`❌ Handshake error with ${node.id}:`, error);
          resolve(false);
        }
      });

      socket.on('error', (error) => {
        console.error(`❌ Socket error with ${node.id}:`, error);
        resolve(false);
      });

      // Timeout after 10 seconds
      setTimeout(() => {
        if (!handshakeComplete) {
          socket.destroy();
          resolve(false);
        }
      }, 10000);
    });
  }

  /**
   * Fillon sinkronizimin e mesh network
   */
  private startMeshSync(): void {
    console.log('🔄 Starting mesh network synchronization...');

    // Heartbeat every 30 seconds
    setInterval(() => {
      this.sendHeartbeat();
    }, 30000);

    // Network discovery every 5 minutes
    setInterval(() => {
      this.discoverNewNodes();
    }, 300000);

    // Route optimization every 10 minutes
    setInterval(() => {
      this.optimizeRoutes();
    }, 600000);

    // Telemetry broadcast every minute
    setInterval(() => {
      this.broadcastTelemetry();
    }, 60000);
  }

  /**
   * Dërgon heartbeat te të gjithë node-t aktivë
   */
  private sendHeartbeat(): void {
    const activeNodes = this.getActiveNodes();
    const heartbeat = {
      type: 'heartbeat',
      from: 'web8-controller',
      timestamp: Date.now(),
      networkSize: activeNodes.length,
      routing: Array.from(this.routingTable.keys())
    };

    activeNodes.forEach(node => {
      this.sendMessage(node.id, heartbeat);
    });

    console.log(`💓 Heartbeat sent to ${activeNodes.length} nodes`);
  }

  /**
   * Zbulimi i node-ve të reja
   */
  private async discoverNewNodes(): Promise<void> {
    console.log('🔍 Discovering new nodes in network...');
    
    const activeNodes = this.getActiveNodes();
    for (const node of activeNodes) {
      // Request neighbor list from each active node
      this.sendMessage(node.id, {
        type: 'discovery_request',
        from: 'web8-controller',
        timestamp: Date.now()
      });
    }
  }

  /**
   * Optimizon route-t në rrjet
   */
  private optimizeRoutes(): void {
    console.log('🗺️ Optimizing mesh network routes...');
    
    const activeNodes = this.getActiveNodes();
    const routeMap = new Map<string, number>();

    // Calculate shortest paths between all nodes
    activeNodes.forEach(fromNode => {
      activeNodes.forEach(toNode => {
        if (fromNode.id !== toNode.id) {
          const route = this.calculateRoute(fromNode, toNode);
          routeMap.set(`${fromNode.id}->${toNode.id}`, route.cost);
        }
      });
    });

    // Update routing table
    this.updateRoutingTable(routeMap);
  }

  /**
   * Broadcast telemetry të rrjetit
   */
  private broadcastTelemetry(): void {
    const telemetry = {
      type: 'telemetry',
      from: 'web8-controller',
      timestamp: Date.now(),
      network: {
        totalNodes: this.nodes.size,
        activeNodes: this.getActiveNodes().length,
        regions: this.getRegionStats(),
        bandwidth: this.calculateTotalBandwidth(),
        latency: this.calculateAverageLatency(),
        health: this.calculateNetworkHealth()
      }
    };

    this.broadcastToAll(telemetry);
    this.emit('telemetryUpdate', telemetry);
  }

  /**
   * Dërgon mesazh te një node specifik
   */
  private sendMessage(nodeId: string, message: any): void {
    const connection = this.connections.get(nodeId);
    if (connection && !connection.destroyed) {
      try {
        connection.write(JSON.stringify(message) + '\n');
      } catch (error) {
        console.error(`❌ Failed to send message to ${nodeId}:`, error);
        this.handleNodeDisconnection(nodeId);
      }
    }
  }

  /**
   * Broadcast mesazh te të gjithë node-t
   */
  private broadcastToAll(message: any): void {
    const activeNodes = this.getActiveNodes();
    activeNodes.forEach(node => {
      this.sendMessage(node.id, message);
    });
  }

  /**
   * Menaxhon shkëputjen e një node
   */
  private handleNodeDisconnection(nodeId: string): void {
    const node = this.nodes.get(nodeId);
    if (node) {
      node.status = 'offline';
      node.lastSeen = Date.now();
      console.log(`📡 Node ${nodeId} disconnected`);
      this.emit('nodeDisconnected', node);
    }

    const connection = this.connections.get(nodeId);
    if (connection) {
      connection.destroy();
      this.connections.delete(nodeId);
    }
  }

  /**
   * Utility functions
   */
  private getActiveNodes(): NetworkNode[] {
    return Array.from(this.nodes.values()).filter(node => node.status === 'online');
  }

  private getRegionStats(): Record<string, number> {
    const regions: Record<string, number> = {};
    this.getActiveNodes().forEach(node => {
      regions[node.region] = (regions[node.region] || 0) + 1;
    });
    return regions;
  }

  private calculateTotalBandwidth(): number {
    return this.getActiveNodes().reduce((total, node) => total + (node.bandwidth || 100), 0);
  }

  private calculateAverageLatency(): number {
    const nodes = this.getActiveNodes().filter(node => node.latency);
    if (nodes.length === 0) return 0;
    return nodes.reduce((sum, node) => sum + (node.latency || 0), 0) / nodes.length;
  }

  private calculateNetworkHealth(): number {
    const totalNodes = this.nodes.size;
    const activeNodes = this.getActiveNodes().length;
    return totalNodes > 0 ? Math.round((activeNodes / totalNodes) * 100) : 0;
  }

  private calculateRoute(from: NetworkNode, to: NetworkNode): { path: string[], cost: number } {
    // Simple distance-based routing (can be enhanced with actual network metrics)
    const latencyFactor = (from.latency || 50) + (to.latency || 50);
    const regionFactor = from.region === to.region ? 1 : 2;
    return {
      path: [from.id, to.id],
      cost: latencyFactor * regionFactor
    };
  }

  private updateRoutingTable(routeMap: Map<string, number>): void {
    // Update internal routing table with optimized routes
    this.routingTable.clear();
    routeMap.forEach((cost, route) => {
      const routeParts = route.split('->');
      if (routeParts.length === 2) {
        const [from, to] = routeParts;
        if (from && to) {
          if (!this.routingTable.has(from)) {
            this.routingTable.set(from, []);
          }
          const routes = this.routingTable.get(from);
          if (routes) {
            routes.push(to);
          }
        }
      }
    });
  }

  private signData(data: string): string {
    const sign = crypto.createSign('RSA-SHA256');
    sign.update(data);
    return sign.sign(this.privateKey, 'base64');
  }

  /**
   * Public API methods
   */
  public getNetworkStatus() {
    return {
      isActive: this.isActive,
      totalNodes: this.nodes.size,
      activeNodes: this.getActiveNodes().length,
      regions: this.getRegionStats(),
      bandwidth: this.calculateTotalBandwidth(),
      latency: this.calculateAverageLatency(),
      health: this.calculateNetworkHealth(),
      routes: this.routingTable.size
    };
  }

  public getNodeDetails(nodeId: string): NetworkNode | undefined {
    return this.nodes.get(nodeId);
  }

  public getAllNodes(): NetworkNode[] {
    return Array.from(this.nodes.values());
  }

  public async addNode(nodeConfig: Partial<NetworkNode>): Promise<boolean> {
    const node = await this.activateNode(nodeConfig);
    return node !== null;
  }

  public removeNode(nodeId: string): boolean {
    const node = this.nodes.get(nodeId);
    if (node) {
      this.handleNodeDisconnection(nodeId);
      this.nodes.delete(nodeId);
      return true;
    }
    return false;
  }

  public async shutdown(): Promise<void> {
    console.log('🛑 Shutting down Web8 Mesh Network...');
    
    // Notify all nodes of shutdown
    this.broadcastToAll({
      type: 'shutdown',
      from: 'web8-controller',
      timestamp: Date.now()
    });

    // Close all connections
    this.connections.forEach(connection => {
      connection.destroy();
    });

    this.connections.clear();
    this.isActive = false;
    
    console.log('✅ Web8 Mesh Network shutdown complete');
  }
}

export { Web8MeshActivator };
export type { NetworkNode, MeshMessage };
export default Web8MeshActivator;
