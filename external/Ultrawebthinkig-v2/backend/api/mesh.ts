/**
 * Web8 Mesh Network Management API
 * REST endpoints për menaxhimin e rrjetit mesh
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0
 */

import express from 'express';
import { Web8MeshActivator, NetworkNode } from '../mesh/MeshActivator.js';

const router = express.Router();
const meshActivator = new Web8MeshActivator();

// Initialize mesh network on startup
let networkInitialized = false;

// Global mesh status
let meshStatus = {
  isActive: false,
  totalNodes: 0,
  activeNodes: 0,
  regions: {},
  health: 0
};

// Event listeners for mesh activator
meshActivator.on('networkActivated', (status) => {
  console.log('🌐 Mesh Network fully activated:', status);
  meshStatus = status;
  networkInitialized = true;
});

meshActivator.on('nodeActivated', (node: NetworkNode) => {
  console.log(`✅ Node activated: ${node.id} in ${node.region}`);
  meshStatus = meshActivator.getNetworkStatus();
});

meshActivator.on('nodeDisconnected', (node: NetworkNode) => {
  console.log(`📡 Node disconnected: ${node.id}`);
  meshStatus = meshActivator.getNetworkStatus();
});

meshActivator.on('telemetryUpdate', (telemetry) => {
  meshStatus = telemetry.network;
});

/**
 * GET /api/mesh/status
 * Merr statusin aktual të rrjetit mesh
 */
router.get('/status', (req, res) => {
  try {
    const status = meshActivator.getNetworkStatus();
    res.json({
      success: true,
      data: {
        ...status,
        regions: Object.entries(status.regions).map(([region, count]) => ({
          region,
          nodes: count,
          flag: getRegionFlag(region)
        })),
        lastUpdate: new Date().toISOString()
      }
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get mesh status',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * GET /api/mesh/nodes
 * Merr listën e të gjithë node-ve
 */
router.get('/nodes', (req, res) => {
  try {
    const nodes = meshActivator.getAllNodes();
    const enrichedNodes = nodes.map(node => ({
      ...node,
      flag: getRegionFlag(node.region),
      uptime: Date.now() - node.lastSeen,
      statusIcon: getStatusIcon(node.status)
    }));

    res.json({
      success: true,
      data: enrichedNodes,
      total: nodes.length,
      active: nodes.filter(n => n.status === 'online').length
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get nodes list'
    });
  }
});

/**
 * GET /api/mesh/nodes/:nodeId
 * Merr detajet e një node specifik
 */
router.get('/nodes/:nodeId', (req, res) => {
  try {
    const nodeId = req.params.nodeId;
    const node = meshActivator.getNodeDetails(nodeId);
    
    if (!node) {
      return res.status(404).json({
        success: false,
        error: 'Node not found'
      });
    }

    return res.json({
      success: true,
      data: {
        ...node,
        flag: getRegionFlag(node.region),
        uptime: Date.now() - node.lastSeen,
        statusIcon: getStatusIcon(node.status)
      }
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: 'Failed to get node details'
    });
  }
});

/**
 * POST /api/mesh/activate
 * Aktivizon rrjetin mesh
 */
router.post('/activate', async (req, res) => {
  try {
    if (networkInitialized) {
      return res.json({
        success: true,
        message: 'Mesh network is already active',
        data: meshActivator.getNetworkStatus()
      });
    }

    console.log('🚀 Starting mesh network activation...');
    await meshActivator.discoverAndActivateNodes();

    return res.json({
      success: true,
      message: 'Mesh network activation started',
      data: meshActivator.getNetworkStatus()
    });
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: 'Failed to activate mesh network',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * POST /api/mesh/nodes
 * Shton një node të ri në rrjet
 */
router.post('/nodes', async (req, res) => {
  try {
    const nodeConfig = req.body;
    
    // Validate required fields
    if (!nodeConfig.host || !nodeConfig.port) {
      return res.status(400).json({
        success: false,
        error: 'Host and port are required'
      });
    }

    const success = await meshActivator.addNode(nodeConfig);
    
    if (success) {
      return res.json({
        success: true,
        message: 'Node added successfully',
        data: meshActivator.getNetworkStatus()
      });
    } else {
      return res.status(400).json({
        success: false,
        error: 'Failed to add node - node may be unreachable'
      });
    }
  } catch (error) {
    return res.status(500).json({
      success: false,
      error: 'Failed to add node',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

/**
 * DELETE /api/mesh/nodes/:nodeId
 * Heq një node nga rrjeti
 */
router.delete('/nodes/:nodeId', (req, res) => {
  try {
    const nodeId = req.params.nodeId;
    const success = meshActivator.removeNode(nodeId);
    
    if (success) {
      res.json({
        success: true,
        message: 'Node removed successfully',
        data: meshActivator.getNetworkStatus()
      });
    } else {
      res.status(404).json({
        success: false,
        error: 'Node not found'
      });
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to remove node'
    });
  }
});

/**
 * POST /api/mesh/discover
 * Fillon një discovery të ri të node-ve
 */
router.post('/discover', async (req, res) => {
  try {
    // This will trigger a new discovery cycle
    await meshActivator.discoverAndActivateNodes();
    
    res.json({
      success: true,
      message: 'Node discovery started',
      data: meshActivator.getNetworkStatus()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to start discovery'
    });
  }
});

/**
 * GET /api/mesh/telemetry
 * Merr telemetri në kohë reale të rrjetit
 */
router.get('/telemetry', (req, res) => {
  try {
    const status = meshActivator.getNetworkStatus();
    const nodes = meshActivator.getAllNodes();
    
    const telemetry = {
      timestamp: new Date().toISOString(),
      network: status,
      nodes: nodes.length,
      regions: status.regions,
      performance: {
        totalBandwidth: status.bandwidth,
        averageLatency: status.latency,
        networkHealth: status.health
      },
      connectivity: {
        routes: status.routes,
        activeConnections: nodes.filter(n => n.status === 'online').length,
        totalCapacity: nodes.reduce((sum, n) => sum + (n.bandwidth || 100), 0)
      }
    };

    res.json({
      success: true,
      data: telemetry
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to get telemetry'
    });
  }
});

/**
 * POST /api/mesh/shutdown
 * Mbyll rrjetin mesh
 */
router.post('/shutdown', async (req, res) => {
  try {
    await meshActivator.shutdown();
    networkInitialized = false;
    meshStatus.isActive = false;
    
    res.json({
      success: true,
      message: 'Mesh network shutdown successfully'
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: 'Failed to shutdown mesh network'
    });
  }
});

// Helper functions
function getRegionFlag(region: string): string {
  const flags: Record<string, string> = {
    'germany': '🇩🇪',
    'austria': '🇦🇹',
    'slovenia': '🇸🇮',
    'croatia': '🇭🇷',
    'montenegro': '🇲🇪',
    'albania': '🇦🇱',
    'kosova': '🇽🇰'
  };
  return flags[region] || '🌐';
}

function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    'online': '🟢',
    'offline': '🔴',
    'connecting': '🟡',
    'error': '❌'
  };
  return icons[status] || '❓';
}

// Auto-start mesh network activation
setTimeout(async () => {
  if (!networkInitialized) {
    console.log('🚀 Auto-starting mesh network activation...');
    try {
      await meshActivator.discoverAndActivateNodes();
    } catch (error) {
      console.error('❌ Failed to auto-start mesh network:', error);
    }
  }
}, 5000); // Start after 5 seconds

export default router;
