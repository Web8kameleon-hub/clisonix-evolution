// mock-services.js - Mock services për testing
import express from 'express';
import cors from 'cors';

const apps = {
  agi: express(),
  security: express(), 
  mesh: express(),
  iot: express(),
  gateway: express()
};

// Enable CORS për të gjitha
Object.values(apps).forEach(app => app.use(cors()));

// AGI Mock Service (port 9000)
apps.agi.get('/status', (req, res) => {
  const load = 0.3 + Math.random() * 0.4; // 0.3-0.7
  res.json({
    status: 'active',
    load: load,
    processing_units: 8,
    neural_networks: 12,
    quantum_cores: 4,
    learning_rate: 'exponential',
    timestamp: new Date().toISOString()
  });
});

// Security Mock Service (port 7000)
apps.security.get('/status', (req, res) => {
  const threats = Math.random() > 0.9 ? Math.floor(Math.random() * 2) + 1 : 0;
  res.json({
    status: 'active',
    threats: threats,
    threats_blocked: Math.floor(Math.random() * 50) + 200,
    firewall_rules: 1247,
    intrusion_attempts: Math.floor(Math.random() * 10),
    last_scan: new Date(Date.now() - Math.random() * 300000).toISOString(),
    security_level: threats === 0 ? 'HIGH' : 'MEDIUM',
    timestamp: new Date().toISOString()
  });
});

// Mesh Network Mock Service (port 5000)
apps.mesh.get('/mesh/status', (req, res) => {
  const baseSignal = 85 + Math.random() * 15; // 85-100%
  const baseEnergy = 70 + Math.random() * 25;  // 70-95%
  res.json({
    status: 'active',
    connectedNodes: Math.floor(Math.random() * 5) + 5, // 5-10 nodes
    signalStrength: baseSignal.toFixed(1),
    energyLevel: baseEnergy.toFixed(1),
    frequency: '868 MHz',
    bandwidth: '125 kHz',
    spreading_factor: 7,
    coding_rate: '4/5',
    tx_power: '14 dBm',
    packet_loss: (Math.random() * 2).toFixed(2) + '%',
    timestamp: new Date().toISOString()
  });
});

// IoT Mock Service (port 6000)
apps.iot.get('/api/devices', (req, res) => {
  const devices = Array.from({ length: Math.floor(Math.random() * 8) + 12 }, (_, i) => ({
    id: `device_${String(i + 1).padStart(3, '0')}`,
    type: ['sensor', 'actuator', 'gateway', 'controller'][Math.floor(Math.random() * 4)],
    status: Math.random() > 0.1 ? 'online' : 'offline',
    battery: Math.floor(Math.random() * 100),
    signal_strength: Math.floor(Math.random() * 40) + 60,
    last_seen: new Date(Date.now() - Math.random() * 3600000).toISOString()
  }));

  res.json({
    total_devices: devices.length,
    online_devices: devices.filter(d => d.status === 'online').length,
    devices: devices,
    timestamp: new Date().toISOString()
  });
});

// API Gateway Mock Service (port 4000)
apps.gateway.get('/api/stats', (req, res) => {
  res.json({
    status: 'active',
    total_requests: Math.floor(Math.random() * 10000) + 50000,
    requests_per_second: Math.floor(Math.random() * 50) + 25,
    active_connections: Math.floor(Math.random() * 200) + 100,
    response_time_avg: (Math.random() * 50 + 10).toFixed(1) + 'ms',
    error_rate: (Math.random() * 2).toFixed(2) + '%',
    uptime: Math.floor(Math.random() * 86400) + 86400, // 1-2 days
    routes: [
      { path: '/api/agi', hits: Math.floor(Math.random() * 1000) + 500 },
      { path: '/api/security', hits: Math.floor(Math.random() * 800) + 300 },
      { path: '/api/mesh', hits: Math.floor(Math.random() * 600) + 200 },
      { path: '/api/iot', hits: Math.floor(Math.random() * 400) + 150 }
    ],
    timestamp: new Date().toISOString()
  });
});

// Start all mock services
const ports = { agi: 9000, security: 7000, mesh: 5000, iot: 6000, gateway: 4000 };

Object.entries(apps).forEach(([name, app]) => {
  const port = ports[name];
  app.listen(port, () => {
    console.log(`✅ Mock ${name.toUpperCase()} service → http://localhost:${port}`);
  });
});

console.log('\n🚀 All mock services started for EuroWeb Revolution Dashboard');
console.log('📊 Ready for 100% real data testing');
