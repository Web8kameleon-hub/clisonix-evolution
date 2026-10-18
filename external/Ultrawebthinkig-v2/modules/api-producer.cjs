const express = require('express');
const axios = require('axios');

// API Producer Module - NO PORT MODE (Integrated into Ultra SaaS Dashboard)

class ApiProducerModule {
    constructor() {
        this.name = 'asi-api-producer';
        this.integrated = true; // Integrated into Ultra SaaS Dashboard
        this.app = null; // No standalone server
        this.registryUrl = null; // No external registry needed
        this.heartbeatInterval = 15000;
        this.heartbeatTimer = null;
        this.metrics = {
            requests: 0,
            apiCalls: 0,
            dataGenerated: 0,
            startTime: Date.now(),
            memory: 0,
            errors: 0
        };
        
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        this.app.use(express.json());
        
        this.app.use((req, res, next) => {
            this.metrics.requests++;
            if (req.path.includes('/api/')) {
                this.metrics.apiCalls++;
            }
            next();
        });

        this.app.use((req, res, next) => {
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
            res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
            next();
        });
    }

    setupRoutes() {
        this.app.get('/health', (req, res) => {
            res.json({
                service: this.name,
                status: 'healthy',
                port: this.port,
                metrics: this.getMetrics()
            });
        });

        this.app.get('/metrics', (req, res) => {
            res.json(this.getMetrics());
        });

        this.app.get('/', (req, res) => {
            res.json({
                service: this.name,
                status: 'running',
                port: this.port,
                description: 'ASI API Producer - Generates synthetic API data',
                endpoints: {
                    '/health': 'Service health check',
                    '/metrics': 'Service metrics',
                    '/api/cultural': 'Cultural data generator',
                    '/api/financial': 'Financial data generator',
                    '/api/news': 'News data generator',
                    '/api/blockchain': 'Blockchain data generator'
                },
                uptime: Date.now() - this.metrics.startTime
            });
        });

        this.app.get('/api/cultural', (req, res) => {
            this.metrics.dataGenerated++;
            res.json({
                type: 'cultural',
                data: {
                    museums: [
                        { name: 'National History Museum', city: 'Tirana', visitors: 1234 },
                        { name: 'Bunk\'Art', city: 'Tirana', visitors: 856 }
                    ],
                    events: [
                        { name: 'Albanian Cultural Festival', date: '2025-07-15', location: 'Tirana' },
                        { name: 'Eagle Festival', date: '2025-08-20', location: 'Shkodër' }
                    ]
                },
                timestamp: new Date().toISOString(),
                generated_by: 'ASI API Producer'
            });
        });

        this.app.get('/api/financial', (req, res) => {
            this.metrics.dataGenerated++;
            res.json({
                type: 'financial',
                data: {
                    lek_rate: {
                        usd: 92.5 + (Math.random() * 2 - 1),
                        eur: 98.2 + (Math.random() * 2 - 1),
                        gbp: 115.3 + (Math.random() * 2 - 1)
                    },
                    market_indicators: {
                        tse_index: 1250 + (Math.random() * 50 - 25),
                        volume: Math.floor(Math.random() * 1000000)
                    }
                },
                timestamp: new Date().toISOString(),
                generated_by: 'ASI API Producer'
            });
        });
    }

    getMetrics() {
        return {
            ...this.metrics,
            uptime: Date.now() - this.metrics.startTime,
            memory: process.memoryUsage().heapUsed / 1024 / 1024,
            service: this.name,
            port: this.port
        };
    }

    log(message) {
        const timestamp = new Date().toISOString();
        process.stdout.write(`[API-PRODUCER] ${timestamp} - INFO: ${message}\n`);
    }

    async registerWithRegistry() {
        try {
            const response = await axios.post(`${this.registryUrl}/register`, {
                name: this.name,
                port: this.port,
                type: 'api-producer',
                health: `/health`,
                endpoints: ['/api/cultural', '/api/financial', '/api/news', '/api/blockchain']
            });
            this.log(`Successfully registered with registry: ${response.data.message}`);
            return true;
        } catch (error) {
            this.log(`Failed to register with registry: ${error.message}`);
            return false;
        }
    }

    async sendHeartbeat() {
        try {
            await axios.post(`${this.registryUrl}/heartbeat`, {
                name: this.name,
                port: this.port,
                metrics: this.getMetrics()
            });
        } catch (error) {
            this.log(`Heartbeat failed: ${error.message}`);
        }
    }

    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            this.sendHeartbeat();
        }, this.heartbeatInterval);
        this.log(`Heartbeat started (${this.heartbeatInterval}ms interval)`);
    }

    async allocatePort() {
        try {
            this.port = await findAvailablePort(3004);
            this.log(`Allocated port: ${this.port}`);
            return this.port;
        } catch (error) {
            this.log(`Port allocation failed: ${error.message}`);
            throw error;
        }
    }

    async start() {
        try {
            await this.allocatePort();
            
            this.app.listen(this.port, () => {
                this.log(`API Producer service running on port ${this.port}`);
                
                setTimeout(async () => {
                    const registered = await this.registerWithRegistry();
                    if (registered) {
                        this.startHeartbeat();
                    }
                }, 2000);
            });
        } catch (error) {
            this.log(`Failed to start: ${error.message}`);
            process.exit(1);
        }
    }

    async stop() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
        }
        
        try {
            await axios.delete(`${this.registryUrl}/services/${this.name}`);
            this.log('Deregistered from service registry');
        } catch (error) {
            this.log(`Deregistration failed: ${error.message}`);
        }
        
        process.exit(0);
    }
}

if (require.main === module) {
    const apiProducer = new ApiProducerModule();
    
    process.on('SIGINT', () => {
        apiProducer.stop();
    });
    
    process.on('SIGTERM', () => {
        apiProducer.stop();
    });
    
    apiProducer.start();
}

module.exports = ApiProducerModule;
