const express = require('express');
const WebSocket = require('ws');
const { Server } = require('socket.io');
const http = require('http');
const cluster = require('cluster');
const os = require('os');

/**
 * 🤖 ASI HELPER AGENTS CLUSTER
 * 7 Helper Agents që aktivizohen automatikisht në mbingarkese
 * Me sistem ping-pong për komunikim real-time
 */

class ASIHelperAgentsCluster {
    constructor() {
        this.app = express();
        this.server = http.createServer(this.app);
        this.io = new Server(this.server, {
            cors: {
                origin: "*",
                methods: ["GET", "POST"]
            }
        });
        this.port = 3012;
        
        // 7 Helper Agents Configuration
        this.helperAgents = new Map([
            ['albi-helper-1', { 
                id: 'albi-helper-1', 
                name: 'ALBI Helper Alpha', 
                specialty: 'Load Balancing & Traffic Management',
                threshold: 70, // activates at 70% load
                status: 'standby',
                load: 0,
                connections: 0,
                priority: 'HIGH'
            }],
            ['albi-helper-2', { 
                id: 'albi-helper-2', 
                name: 'ALBI Helper Beta', 
                specialty: 'Database Optimization & Caching',
                threshold: 60,
                status: 'standby',
                load: 0,
                connections: 0,
                priority: 'HIGH'
            }],
            ['albi-helper-3', { 
                id: 'albi-helper-3', 
                name: 'ALBI Helper Gamma', 
                specialty: 'Memory Management & Cleanup',
                threshold: 80,
                status: 'standby',
                load: 0,
                connections: 0,
                priority: 'MEDIUM'
            }],
            ['albi-helper-4', { 
                id: 'albi-helper-4', 
                name: 'ALBI Helper Delta', 
                specialty: 'API Rate Limiting & Security',
                threshold: 50,
                status: 'standby',
                load: 0,
                connections: 0,
                priority: 'HIGH'
            }],
            ['albi-helper-5', { 
                id: 'albi-helper-5', 
                name: 'ALBI Helper Epsilon', 
                specialty: 'Error Recovery & System Restart',
                threshold: 90,
                status: 'standby',
                load: 0,
                connections: 0,
                priority: 'CRITICAL'
            }],
            ['albi-helper-6', { 
                id: 'albi-helper-6', 
                name: 'ALBI Helper Zeta', 
                specialty: 'Performance Monitoring & Analytics',
                threshold: 30,
                status: 'active', // Always active
                load: 0,
                connections: 0,
                priority: 'MEDIUM'
            }],
            ['albi-helper-7', { 
                id: 'albi-helper-7', 
                name: 'ALBI Helper Eta', 
                specialty: 'Backup Coordination & Data Sync',
                threshold: 75,
                status: 'standby',
                load: 0,
                connections: 0,
                priority: 'HIGH'
            }]
        ]);

        // Ping-Pong System
        this.pingPongSystem = {
            interval: 5000, // 5 seconds
            timeout: 15000, // 15 seconds
            connections: new Map(),
            metrics: {
                totalPings: 0,
                totalPongs: 0,
                avgResponseTime: 0,
                lastPing: null
            }
        };

        this.systemMetrics = {
            totalLoad: 0,
            activeAgents: 1, // albi-helper-6 është gjithmonë aktiv
            totalConnections: 0,
            autoActivations: 0,
            lastActivation: null
        };

        this.setupMiddleware();
        this.setupRoutes();
        this.setupWebSocket();
        this.startPingPongSystem();
        this.startLoadMonitoring();
    }

    setupMiddleware() {
        this.app.use(express.json());
        this.app.use(express.static('public'));
        
        // CORS
        this.app.use((req, res, next) => {
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
            next();
        });

        // Logging
        this.app.use((req, res, next) => {
            console.log(`[${new Date().toISOString()}] ${req.method} ${req.path} - Helper Cluster`);
            next();
        });
    }

    setupRoutes() {
        // Main dashboard
        this.app.get('/', (req, res) => {
            res.send(this.generateDashboard());
        });

        // Get all helper agents
        this.app.get('/api/agents', (req, res) => {
            res.json({
                agents: Array.from(this.helperAgents.values()),
                metrics: this.systemMetrics,
                pingPong: this.pingPongSystem.metrics
            });
        });

        // Activate specific agent
        this.app.post('/api/agents/:id/activate', (req, res) => {
            const agent = this.helperAgents.get(req.params.id);
            if (!agent) {
                return res.status(404).json({ error: 'Agent not found' });
            }

            this.activateAgent(agent);
            res.json({ 
                message: `Agent ${agent.name} activated`,
                agent: agent
            });
        });

        // Deactivate specific agent
        this.app.post('/api/agents/:id/deactivate', (req, res) => {
            const agent = this.helperAgents.get(req.params.id);
            if (!agent) {
                return res.status(404).json({ error: 'Agent not found' });
            }

            if (agent.id === 'albi-helper-6') {
                return res.status(400).json({ error: 'Performance Monitor cannot be deactivated' });
            }

            this.deactivateAgent(agent);
            res.json({ 
                message: `Agent ${agent.name} deactivated`,
                agent: agent
            });
        });

        // System load simulation (for testing)
        this.app.post('/api/simulate-load', (req, res) => {
            const { load } = req.body;
            this.systemMetrics.totalLoad = Math.max(0, Math.min(100, load || 50));
            this.checkAutoActivation();
            
            res.json({
                message: `System load set to ${this.systemMetrics.totalLoad}%`,
                metrics: this.systemMetrics,
                activeAgents: Array.from(this.helperAgents.values()).filter(a => a.status === 'active')
            });
        });

        // Ping endpoint
        this.app.get('/api/ping', (req, res) => {
            const timestamp = Date.now();
            this.pingPongSystem.metrics.totalPings++;
            
            res.json({
                pong: true,
                timestamp,
                agents: Array.from(this.helperAgents.values()).filter(a => a.status === 'active').length,
                load: this.systemMetrics.totalLoad
            });
        });

        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                service: 'ASI Helper Agents Cluster',
                port: this.port,
                agents: {
                    total: this.helperAgents.size,
                    active: Array.from(this.helperAgents.values()).filter(a => a.status === 'active').length,
                    standby: Array.from(this.helperAgents.values()).filter(a => a.status === 'standby').length
                },
                system: this.systemMetrics,
                pingPong: this.pingPongSystem.metrics,
                uptime: process.uptime()
            });
        });
    }

    setupWebSocket() {
        this.io.on('connection', (socket) => {
            console.log(`WebSocket client connected: ${socket.id}`);
            this.systemMetrics.totalConnections++;

            // Add to ping-pong system
            this.pingPongSystem.connections.set(socket.id, {
                socket: socket,
                lastPing: Date.now(),
                responseTime: 0,
                missedPings: 0
            });

            // Send initial data
            socket.emit('agents-update', {
                agents: Array.from(this.helperAgents.values()),
                metrics: this.systemMetrics
            });

            // Handle ping response
            socket.on('pong', (data) => {
                const connection = this.pingPongSystem.connections.get(socket.id);
                if (connection) {
                    connection.responseTime = Date.now() - data.timestamp;
                    connection.missedPings = 0;
                    this.pingPongSystem.metrics.totalPongs++;
                }
            });

            socket.on('disconnect', () => {
                console.log(`WebSocket client disconnected: ${socket.id}`);
                this.systemMetrics.totalConnections--;
                this.pingPongSystem.connections.delete(socket.id);
            });
        });
    }

    startPingPongSystem() {
        setInterval(() => {
            const timestamp = Date.now();
            this.pingPongSystem.metrics.lastPing = timestamp;

            // Send ping to all WebSocket connections
            this.pingPongSystem.connections.forEach((connection, socketId) => {
                if (connection.socket.connected) {
                    connection.socket.emit('ping', { timestamp });
                    connection.lastPing = timestamp;
                } else {
                    this.pingPongSystem.connections.delete(socketId);
                }
            });

            // Ping other ASI services
            this.pingOtherServices();

        }, this.pingPongSystem.interval);

        // Check for timeouts
        setInterval(() => {
            const now = Date.now();
            this.pingPongSystem.connections.forEach((connection, socketId) => {
                if (now - connection.lastPing > this.pingPongSystem.timeout) {
                    connection.missedPings++;
                    if (connection.missedPings > 3) {
                        connection.socket.disconnect();
                        this.pingPongSystem.connections.delete(socketId);
                    }
                }
            });
        }, 10000); // Check every 10 seconds
    }

    async pingOtherServices() {
        const services = [
            'http://localhost:3001', // Main Platform
            'http://localhost:3002', // ASI SaaS Frontend
            'http://localhost:3003', // API Gateway
            'http://localhost:3004', // ASI Agent Demo
            'http://localhost:3005', // API Producer
            'http://localhost:3006', // Auto Generator
            'http://localhost:3007', // Agent Monitor
            'http://localhost:3008', // Quantum Security
            'http://localhost:3009', // Helper Agent
            'http://localhost:3010', // Emergency Creator
            'http://localhost:3011'  // Backup System
        ];

        let totalLoad = 0;
        let activeServices = 0;

        for (const service of services) {
            try {
                const response = await fetch(service + '/health', { 
                    method: 'GET', 
                    timeout: 5000 
                });
                
                if (response.ok) {
                    activeServices++;
                    const data = await response.json();
                    if (data.load) totalLoad += data.load;
                }
            } catch (error) {
                // Service unavailable
            }
        }

        // Update system metrics
        this.systemMetrics.totalLoad = totalLoad / Math.max(1, activeServices);
        this.checkAutoActivation();
    }

    checkAutoActivation() {
        const currentLoad = this.systemMetrics.totalLoad;

        this.helperAgents.forEach((agent) => {
            if (agent.id === 'albi-helper-6') return; // Always active

            if (currentLoad >= agent.threshold && agent.status === 'standby') {
                this.activateAgent(agent);
                this.systemMetrics.autoActivations++;
                this.systemMetrics.lastActivation = new Date().toISOString();
                
                console.log(`🚀 Auto-activated ${agent.name} due to ${currentLoad}% system load`);
            } else if (currentLoad < (agent.threshold - 10) && agent.status === 'active') {
                // Deactivate if load drops significantly below threshold
                this.deactivateAgent(agent);
                console.log(`💤 Auto-deactivated ${agent.name} - load dropped to ${currentLoad}%`);
            }
        });
    }

    activateAgent(agent) {
        agent.status = 'active';
        agent.load = 0;
        this.systemMetrics.activeAgents++;
        
        // Broadcast to all WebSocket connections
        this.io.emit('agent-activated', {
            agent: agent,
            metrics: this.systemMetrics
        });
    }

    deactivateAgent(agent) {
        agent.status = 'standby';
        agent.load = 0;
        agent.connections = 0;
        this.systemMetrics.activeAgents--;
        
        // Broadcast to all WebSocket connections
        this.io.emit('agent-deactivated', {
            agent: agent,
            metrics: this.systemMetrics
        });
    }

    startLoadMonitoring() {
        setInterval(() => {
            // Simulate some load distribution among active agents
            this.helperAgents.forEach((agent) => {
                if (agent.status === 'active') {
                    agent.load = Math.random() * 100;
                    agent.connections = Math.floor(Math.random() * 50);
                }
            });

            // Broadcast updated metrics
            this.io.emit('metrics-update', {
                agents: Array.from(this.helperAgents.values()),
                metrics: this.systemMetrics,
                pingPong: this.pingPongSystem.metrics
            });
        }, 3000); // Every 3 seconds
    }

    generateDashboard() {
        const activeAgents = Array.from(this.helperAgents.values()).filter(a => a.status === 'active');
        const standbyAgents = Array.from(this.helperAgents.values()).filter(a => a.status === 'standby');

        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>🤖 ASI Helper Agents Cluster</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
                        min-height: 100vh; color: white; padding: 20px;
                    }
                    .container { max-width: 1400px; margin: 0 auto; }
                    .header { text-align: center; margin-bottom: 40px; }
                    .header h1 { font-size: 3em; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
                    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
                    .stat-card { 
                        background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; 
                        backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);
                        text-align: center;
                    }
                    .stat-number { font-size: 2.5em; font-weight: bold; color: #FFD700; }
                    .agents-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }
                    .agent-card { 
                        background: rgba(255,255,255,0.1); padding: 25px; border-radius: 15px; 
                        backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);
                        transition: transform 0.3s ease;
                    }
                    .agent-card:hover { transform: translateY(-5px); }
                    .agent-header { display: flex; align-items: center; margin-bottom: 15px; }
                    .agent-avatar { font-size: 2.5em; margin-right: 15px; }
                    .status-active { color: #4CAF50; }
                    .status-standby { color: #FF9800; }
                    .status-critical { color: #F44336; }
                    .load-bar { 
                        width: 100%; height: 20px; background: rgba(255,255,255,0.1); 
                        border-radius: 10px; overflow: hidden; margin: 10px 0;
                    }
                    .load-fill { height: 100%; background: linear-gradient(90deg, #4CAF50, #FFD700, #FF5722); transition: width 0.5s ease; }
                    .ping-pong { 
                        background: rgba(0,255,0,0.1); padding: 15px; border-radius: 10px; 
                        border-left: 4px solid #4CAF50; margin: 20px 0;
                    }
                    .controls { margin: 20px 0; }
                    .btn { 
                        background: linear-gradient(45deg, #FF6B6B, #4ECDC4); border: none; 
                        padding: 10px 20px; border-radius: 25px; color: white; 
                        font-weight: bold; cursor: pointer; margin: 5px;
                        transition: transform 0.2s ease;
                    }
                    .btn:hover { transform: scale(1.05); }
                    .auto-refresh { position: fixed; top: 20px; right: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🤖 ASI Helper Agents Cluster</h1>
                        <p>7 Helper Agents me Auto-Activation në Mbingarkese</p>
                        <p>Port 3012 - Ping-Pong System Active</p>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-number">${this.helperAgents.size}</div>
                            <div>Total Helper Agents</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="active-count">${activeAgents.length}</div>
                            <div>Active Agents</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="system-load">${Math.round(this.systemMetrics.totalLoad)}</div>
                            <div>System Load %</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="auto-activations">${this.systemMetrics.autoActivations}</div>
                            <div>Auto Activations</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number" id="ping-pongs">${this.pingPongSystem.metrics.totalPongs}</div>
                            <div>Ping-Pong Responses</div>
                        </div>
                    </div>

                    <div class="ping-pong">
                        <h3>🏓 Ping-Pong System Status</h3>
                        <p>Total Pings: <span id="total-pings">${this.pingPongSystem.metrics.totalPings}</span></p>
                        <p>Total Pongs: <span id="total-pongs">${this.pingPongSystem.metrics.totalPongs}</span></p>
                        <p>Active Connections: <span id="connections">${this.pingPongSystem.connections.size}</span></p>
                        <p>Last Ping: <span id="last-ping">${this.pingPongSystem.metrics.lastPing ? new Date(this.pingPongSystem.metrics.lastPing).toLocaleTimeString() : 'Never'}</span></p>
                    </div>

                    <div class="controls">
                        <h3>🎛️ Manual Controls</h3>
                        <button class="btn" onclick="simulateLoad(30)">Low Load (30%)</button>
                        <button class="btn" onclick="simulateLoad(60)">Medium Load (60%)</button>
                        <button class="btn" onclick="simulateLoad(90)">High Load (90%)</button>
                        <button class="btn" onclick="resetSystem()">Reset System</button>
                    </div>

                    <div class="agents-grid" id="agents-grid">
                        ${Array.from(this.helperAgents.values()).map(agent => `
                            <div class="agent-card" data-agent-id="${agent.id}">
                                <div class="agent-header">
                                    <div class="agent-avatar">${this.getAgentIcon(agent)}</div>
                                    <div>
                                        <h3>${agent.name}</h3>
                                        <p style="opacity: 0.8;">${agent.specialty}</p>
                                        <div class="status-${agent.status}">
                                            ● ${agent.status.toUpperCase()} 
                                            (Threshold: ${agent.threshold}%)
                                        </div>
                                    </div>
                                </div>
                                <div class="load-bar">
                                    <div class="load-fill" style="width: ${agent.load}%"></div>
                                </div>
                                <p>Load: ${Math.round(agent.load)}% | Connections: ${agent.connections} | Priority: ${agent.priority}</p>
                                
                                <div class="controls">
                                    ${agent.id !== 'albi-helper-6' ? `
                                        <button class="btn" onclick="toggleAgent('${agent.id}')" id="toggle-${agent.id}">
                                            ${agent.status === 'active' ? 'Deactivate' : 'Activate'}
                                        </button>
                                    ` : '<span style="opacity: 0.7;">Always Active</span>'}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="auto-refresh">
                    <span id="refresh-indicator">🔄 Auto-refresh: ON</span>
                </div>

                <script src="/socket.io/socket.io.js"></script>
                <script>
                    const socket = io();
                    let autoRefresh = true;

                    // WebSocket event handlers
                    socket.on('connect', () => {
                        console.log('Connected to Helper Agents Cluster');
                    });

                    socket.on('ping', (data) => {
                        socket.emit('pong', { timestamp: data.timestamp });
                    });

                    socket.on('metrics-update', (data) => {
                        if (autoRefresh) {
                            updateDashboard(data);
                        }
                    });

                    socket.on('agent-activated', (data) => {
                        console.log('Agent activated:', data.agent.name);
                        // Show notification or update UI
                    });

                    socket.on('agent-deactivated', (data) => {
                        console.log('Agent deactivated:', data.agent.name);
                    });

                    function updateDashboard(data) {
                        // Update stats
                        document.getElementById('active-count').textContent = 
                            data.agents.filter(a => a.status === 'active').length;
                        document.getElementById('system-load').textContent = 
                            Math.round(data.metrics.totalLoad);
                        document.getElementById('auto-activations').textContent = 
                            data.metrics.autoActivations;
                        
                        if (data.pingPong) {
                            document.getElementById('total-pings').textContent = data.pingPong.totalPings;
                            document.getElementById('total-pongs').textContent = data.pingPong.totalPongs;
                            if (data.pingPong.lastPing) {
                                document.getElementById('last-ping').textContent = 
                                    new Date(data.pingPong.lastPing).toLocaleTimeString();
                            }
                        }

                        // Update agent cards
                        data.agents.forEach(agent => {
                            const card = document.querySelector(\`[data-agent-id="\${agent.id}"]\`);
                            if (card) {
                                const loadFill = card.querySelector('.load-fill');
                                if (loadFill) {
                                    loadFill.style.width = agent.load + '%';
                                }
                                
                                const toggleBtn = document.getElementById(\`toggle-\${agent.id}\`);
                                if (toggleBtn) {
                                    toggleBtn.textContent = agent.status === 'active' ? 'Deactivate' : 'Activate';
                                }
                            }
                        });
                    }

                    async function simulateLoad(load) {
                        try {
                            const response = await fetch('/api/simulate-load', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ load })
                            });
                            const data = await response.json();
                            console.log('Load simulation:', data);
                        } catch (error) {
                            console.error('Failed to simulate load:', error);
                        }
                    }

                    async function toggleAgent(agentId) {
                        try {
                            const agent = document.querySelector(\`[data-agent-id="\${agentId}"]\`);
                            const currentStatus = agent.textContent.includes('ACTIVE') ? 'active' : 'standby';
                            const action = currentStatus === 'active' ? 'deactivate' : 'activate';
                            
                            const response = await fetch(\`/api/agents/\${agentId}/\${action}\`, {
                                method: 'POST'
                            });
                            const data = await response.json();
                            console.log(\`Agent \${action}d:\`, data);
                        } catch (error) {
                            console.error('Failed to toggle agent:', error);
                        }
                    }

                    function resetSystem() {
                        simulateLoad(0);
                    }

                    // Auto-refresh toggle
                    document.getElementById('refresh-indicator').addEventListener('click', () => {
                        autoRefresh = !autoRefresh;
                        document.getElementById('refresh-indicator').textContent = 
                            \`🔄 Auto-refresh: \${autoRefresh ? 'ON' : 'OFF'}\`;
                    });

                    // Initial load
                    setTimeout(() => {
                        fetch('/api/agents')
                            .then(response => response.json())
                            .then(data => updateDashboard(data))
                            .catch(error => console.error('Failed to load initial data:', error));
                    }, 1000);
                </script>
            </body>
            </html>
        `;
    }

    getAgentIcon(agent) {
        const icons = {
            'albi-helper-1': '⚖️', // Load Balancing
            'albi-helper-2': '💾', // Database
            'albi-helper-3': '🧠', // Memory
            'albi-helper-4': '🛡️', // Security
            'albi-helper-5': '🚑', // Recovery
            'albi-helper-6': '📊', // Analytics
            'albi-helper-7': '💽'  // Backup
        };
        return icons[agent.id] || '🤖';
    }

    start() {
        this.server.listen(this.port, () => {
            console.log(`🤖 ASI Helper Agents Cluster started on port ${this.port}`);
            console.log(`📊 Dashboard: http://localhost:${this.port}`);
            console.log(`🏓 Ping-Pong System: Active`);
            console.log(`🔄 Auto-Activation: Enabled`);
            console.log(`\n🚀 Helper Agents Status:`);
            
            this.helperAgents.forEach((agent) => {
                console.log(`   ${this.getAgentIcon(agent)} ${agent.name}: ${agent.status.toUpperCase()} (Threshold: ${agent.threshold}%)`);
            });
            
            console.log('\n⚡ System ready for auto-scaling!');
        });
    }
}

// Create and start the Helper Agents Cluster
const helperCluster = new ASIHelperAgentsCluster();
helperCluster.start();

module.exports = ASIHelperAgentsCluster;
