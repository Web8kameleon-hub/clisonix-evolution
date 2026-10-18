const express = require('express');
const axios = require('axios');

// Agent Demo Module - NO PORT MODE (Integrated into Ultra SaaS Dashboard)

class AgentDemoModule {
    constructor() {
        this.name = 'asi-agent-ultra-demo';
        this.integrated = true; // Integrated into Ultra SaaS Dashboard
        this.app = null; // No standalone server
        this.registryUrl = null; // No external registry needed  
        this.heartbeatInterval = 15000; // 15 seconds
        this.heartbeatTimer = null;
        this.metrics = {
            requests: 0,
            agentRequests: 0,
            startTime: Date.now(),
            memory: 0,
            activeConnections: 0
        };
        
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        this.app.use(express.json());
        
        // Request counter middleware
        this.app.use((req, res, next) => {
            this.metrics.requests++;
            if (req.path.includes('agent')) {
                this.metrics.agentRequests++;
            }
            next();
        });

        // CORS middleware
        this.app.use((req, res, next) => {
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
            res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
            next();
        });
    }

    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                service: this.name,
                status: 'healthy',
                port: this.port,
                metrics: this.getMetrics()
            });
        });

        // Agent demo metrics
        this.app.get('/metrics', (req, res) => {
            res.json(this.getMetrics());
        });

        // Main agent demo route
        this.app.get('/', (req, res) => {
            res.json({
                message: 'ASI Agent Ultra Demo Service',
                service: this.name,
                port: this.port,
                version: '2.0.0',
                endpoints: [
                    '/health',
                    '/metrics',
                    '/agent/demo',
                    '/agent/status',
                    '/agent/capabilities'
                ]
            });
        });

        // Agent demo interface
        this.app.get('/agent/demo', (req, res) => {
            res.json({
                demo: 'ASI Agent Ultra Demo',
                capabilities: [
                    'Natural Language Processing',
                    'Intelligent Responses',
                    'Context Awareness',
                    'Multi-language Support'
                ],
                status: 'active',
                port: this.port
            });
        });

        // Agent capabilities
        this.app.get('/agent/capabilities', (req, res) => {
            res.json({
                ai_features: {
                    nlp: true,
                    context_memory: true,
                    multi_language: true,
                    real_time_response: true
                },
                integrations: [
                    'ASI Core System',
                    'ALBA Analytics',
                    'ALBI Intelligence'
                ],
                performance: this.getMetrics()
            });
        });

        // Agent status
        this.app.get('/agent/status', async (req, res) => {
            try {
                const services = await this.getRegisteredServices();
                const relatedServices = services.filter(s => 
                    s.name.includes('asi') || s.name.includes('api')
                );
                
                res.json({
                    agent: this.name,
                    status: 'operational',
                    connected_services: relatedServices.length,
                    services: relatedServices.map(s => ({
                        name: s.name,
                        port: s.port,
                        status: s.status
                    }))
                });
            } catch (error) {
                res.status(500).json({
                    error: 'Failed to fetch agent status',
                    message: error.message
                });
            }
        });

        // Agent interaction endpoint
        this.app.post('/agent/interact', (req, res) => {
            const { message, context } = req.body;
            
            // Simulate AI response
            const responses = [
                'I understand your request. How can I assist you further?',
                'Processing your input through ASI neural networks...',
                'Your request has been analyzed. Here are the insights:',
                'Connecting to ALBA analytics for enhanced response...'
            ];
            
            const response = responses[Math.floor(Math.random() * responses.length)];
            
            res.json({
                agent_response: response,
                input_message: message,
                context_processed: !!context,
                timestamp: new Date().toISOString(),
                confidence: Math.floor(Math.random() * 30) + 70 // 70-99%
            });
        });

        // WebSocket-like demo endpoint
        this.app.get('/agent/stream', (req, res) => {
            res.writeHead(200, {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            });

            // Send periodic updates
            const interval = setInterval(() => {
                const data = {
                    timestamp: new Date().toISOString(),
                    agent: this.name,
                    status: 'processing',
                    metrics: this.getMetrics()
                };
                res.write(`data: ${JSON.stringify(data)}\n\n`);
            }, 5000);

            // Cleanup on disconnect
            req.on('close', () => {
                clearInterval(interval);
                this.metrics.activeConnections--;
            });

            this.metrics.activeConnections++;
        });
    }

    getMetrics() {
        this.metrics.memory = Math.round(process.memoryUsage().heapUsed / 1024 / 1024);
        return {
            ...this.metrics,
            uptime: Date.now() - this.metrics.startTime,
            uptimeSeconds: Math.floor((Date.now() - this.metrics.startTime) / 1000),
            efficiency: this.metrics.agentRequests > 0 ? 
                Math.round((this.metrics.agentRequests / this.metrics.requests) * 100) : 0
        };
    }

    async allocatePort() {
        try {
            // Automatic port allocation starting from 3000
            this.port = await findAvailablePort(3000);
            this.log(`Allocated port: ${this.port}`);
            return this.port;
        } catch (error) {
            this.logError(`Port allocation failed: ${error.message}`);
            throw error;
        }
    }

    async registerWithRegistry() {
        try {
            const response = await axios.post(`${this.registryUrl}/register`, {
                name: this.name,
                port: this.port,
                status: 'active',
                pid: process.pid
            });
            
            this.log(`Successfully registered with registry: ${response.data.message}`);
            return true;
        } catch (error) {
            this.logError(`Registry registration failed: ${error.message}`);
            return false;
        }
    }

    async sendHeartbeat() {
        try {
            await axios.post(`${this.registryUrl}/heartbeat`, {
                name: this.name,
                metrics: this.getMetrics()
            });
            
            // this.log('Heartbeat sent successfully');
        } catch (error) {
            this.logError(`Heartbeat failed: ${error.message}`);
        }
    }

    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            this.sendHeartbeat();
        }, this.heartbeatInterval);
        
        this.log(`Heartbeat started (${this.heartbeatInterval}ms interval)`);
    }

    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
            this.log('Heartbeat stopped');
        }
    }

    async getRegisteredServices() {
        try {
            const response = await axios.get(`${this.registryUrl}/services`);
            return response.data.services || [];
        } catch (error) {
            this.logError(`Failed to fetch services: ${error.message}`);
            return [];
        }
    }

    async start() {
        try {
            // Allocate port
            await this.allocatePort();
            
            // Start Express server
            return new Promise((resolve, reject) => {
                this.server = this.app.listen(this.port, async (err) => {
                    if (err) {
                        this.logError(`Failed to start server: ${err.message}`);
                        reject(err);
                    } else {
                        this.log(`Agent Demo service running on port ${this.port}`);
                        
                        // Register with registry service
                        setTimeout(async () => {
                            const registered = await this.registerWithRegistry();
                            if (registered) {
                                this.startHeartbeat();
                            }
                        }, 2000); // Wait for registry to be ready
                        
                        resolve(this.server);
                    }
                });
            });
            
        } catch (error) {
            this.logError(`Startup failed: ${error.message}`);
            throw error;
        }
    }

    async stop() {
        try {
            this.stopHeartbeat();
            
            if (this.server) {
                this.server.close();
                this.log('Agent Demo service stopped');
            }
            
            // Deregister from registry
            try {
                await axios.delete(`${this.registryUrl}/services/${this.name}`);
                this.log('Deregistered from registry');
            } catch (error) {
                this.logError(`Deregistration failed: ${error.message}`);
            }
            
        } catch (error) {
            this.logError(`Stop failed: ${error.message}`);
        }
    }

    log(message) {
        process.stdout.write(`[AGENT-DEMO] ${new Date().toISOString()} - INFO: ${message}\n`);
    }

    logError(message) {
        process.stderr.write(`[AGENT-DEMO] ${new Date().toISOString()} - ERROR: ${message}\n`);
    }
}

// Auto-start if run directly
if (require.main === module) {
    const agentDemo = new AgentDemoModule();
    
    agentDemo.start().catch(error => {
        process.stderr.write(`Agent Demo startup failed: ${error.message}\n`);
        process.exit(1);
    });
    
    // Graceful shutdown
    process.on('SIGINT', async () => {
        process.stdout.write('\nShutting down Agent Demo Module...\n');
        await agentDemo.stop();
        process.exit(0);
    });
    
    process.on('SIGTERM', async () => {
        await agentDemo.stop();
        process.exit(0);
    });
}

module.exports = AgentDemoModule;
