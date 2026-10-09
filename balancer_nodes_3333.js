#!/usr/bin/env node
/**
 * BALANCER NODES SERVICE (Port 3333)
 * Node.js-based load balancer node discovery and management
 */

const express = require('express');
const http = require('http');
const os = require('os');

const app = express();
app.use(express.json());

// Configuration
const PORT = process.env.BALANCER_NODES_PORT || 3333;
const HOST = process.env.BALANCER_NODES_HOST || '0.0.0.0';

// Node registry
const nodeRegistry = new Map();
const requestLog = [];

// Track service start time
const SERVICE_START = new Date().toISOString();
let REQUEST_COUNT = 0;

/**
 * Register a new node
 */
app.post('/api/nodes/register', (req, res) => {
  REQUEST_COUNT++;
  const { nodeId, type, port, host, metadata } = req.body;

  if (!nodeId) {
    return res.status(400).json({ error: 'nodeId required' });
  }

  const nodeData = {
    nodeId,
    type: type || 'unknown',
    port,
    host: host || os.hostname(),
    status: 'active',
    registeredAt: new Date().toISOString(),
    lastHeartbeat: new Date().toISOString(),
    metadata: metadata || {},
    requestCount: 0
  };

  nodeRegistry.set(nodeId, nodeData);

  console.log(`[${new Date().toISOString()}] Node registered: ${nodeId}`);

  res.json({
    success: true,
    message: `Node ${nodeId} registered`,
    node: nodeData
  });
});

/**
 * Get all registered nodes
 */
app.get('/api/nodes', (req, res) => {
  REQUEST_COUNT++;
  const nodes = Array.from(nodeRegistry.values());

  res.json({
    timestamp: new Date().toISOString(),
    totalNodes: nodes.length,
    nodes: nodes
  });
});

/**
 * Get specific node
 */
app.get('/api/nodes/:nodeId', (req, res) => {
  REQUEST_COUNT++;
  const { nodeId } = req.params;
  const node = nodeRegistry.get(nodeId);

  if (!node) {
    return res.status(404).json({ error: `Node ${nodeId} not found` });
  }

  res.json({
    timestamp: new Date().toISOString(),
    node: node
  });
});

/**
 * Update node status
 */
app.put('/api/nodes/:nodeId/status', (req, res) => {
  REQUEST_COUNT++;
  const { nodeId } = req.params;
  const { status } = req.body;

  const node = nodeRegistry.get(nodeId);
  if (!node) {
    return res.status(404).json({ error: `Node ${nodeId} not found` });
  }

  node.status = status || 'active';
  node.lastHeartbeat = new Date().toISOString();
  node.requestCount++;

  res.json({
    timestamp: new Date().toISOString(),
    message: `Node ${nodeId} status updated`,
    node: node
  });
});

/**
 * Health check
 */
app.get('/health', (req, res) => {
  REQUEST_COUNT++;
  res.json({
    status: 'healthy',
    service: 'balancer-nodes-3333',
    timestamp: new Date().toISOString(),
    uptime_since: SERVICE_START,
    requests_served: REQUEST_COUNT,
    activeNodes: nodeRegistry.size
  });
});

/**
 * Service info
 */
app.get('/info', (req, res) => {
  REQUEST_COUNT++;
  res.json({
    service: 'Balancer Nodes (JavaScript)',
    port: PORT,
    type: 'node-discovery',
    version: '1.0.0',
    started_at: SERVICE_START,
    timestamp: new Date().toISOString(),
    endpoints: {
      'POST /api/nodes/register': 'Register new node',
      'GET /api/nodes': 'List all nodes',
      'GET /api/nodes/:nodeId': 'Get specific node',
      'PUT /api/nodes/:nodeId/status': 'Update node status',
      'GET /health': 'Health check',
      'GET /info': 'Service info'
    }
  });
});

// Start server
const server = http.createServer(app);
server.listen(PORT, HOST, () => {
  console.log('\n' + '='.repeat(60));
  console.log('  BALANCER NODES SERVICE (JavaScript)');
  console.log(`  Listening on ${HOST}:${PORT}`);
  console.log('  Node discovery & load balancer management');
  console.log('='.repeat(60) + '\n');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully...');
  server.close(() => {
    process.exit(0);
  });
});
