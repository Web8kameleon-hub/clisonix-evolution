const express = require('express');
const axios = require('axios');

// Simple port finder function  
async function findAvailablePort(startPort = 3002) {
    const net = require('net');
    
    return new Promise((resolve) => {
        const server = net.createServer();
        server.on('error', () => {
            server.close();
            findAvailablePort(startPort + 1).then(resolve);
        });
        server.listen(startPort, () => {
            const port = server.address().port;
            server.close(() => {
                resolve(port);
            });
        });
    });
}

class ApiProducerModule {
    constructor() {
        this.name = 'asi-api-producer';
        this.port = null;
        this.app = express();
        this.registryUrl = 'http://localhost:2999';
        this.heartbeatInterval = 15000; // 15 seconds
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
        
        // Request counter middleware
        this.app.use((req, res, next) => {
            this.metrics.requests++;
            if (req.path.includes('/api/')) {
                this.metrics.apiCalls++;
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

        // API Producer metrics
        this.app.get('/metrics', (req, res) => {
            res.json(this.getMetrics());
        });

        // Main API Producer route
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

        // Cultural API
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

        // Financial API
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

        // News API
        this.app.get('/api/news', (req, res) => {
            this.metrics.dataGenerated++;
            const newsItems = [
                'Albania strengthens ties with EU partners',
                'Technology sector grows rapidly in Tirana',
                'New infrastructure projects announced',
                'Cultural heritage preservation initiatives launched'
            ];
            
            res.json({
                type: 'news',
                data: {
                    headlines: newsItems.slice(0, Math.ceil(Math.random() * newsItems.length)),
                    breaking: Math.random() > 0.7,
                    sources: ['AlbaniaDaily', 'BalkanTech', 'EuroNews Albania']
                },
                timestamp: new Date().toISOString(),
                generated_by: 'ASI API Producer'
            });
        });

        // Blockchain API
        this.app.get('/api/blockchain', (req, res) => {
            this.metrics.dataGenerated++;
            res.json({
                type: 'blockchain',
                data: {
                    asi_token: {
                        price: 12.34 + (Math.random() * 2 - 1),
                        volume: Math.floor(Math.random() * 100000),
                        market_cap: Math.floor(Math.random() * 10000000)
                    },
                    network_stats: {
                        transactions: Math.floor(Math.random() * 1000),
                        block_height: 845632 + Math.floor(Math.random() * 100),
                        hash_rate: Math.floor(Math.random() * 1000) + 'TH/s'
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
            memory: process.memoryUsage().heapUsed / 1024 / 1024, // MB
            service: this.name,
            port: this.port
        };
    }

    log(message) {
        const timestamp = new Date().toISOString();
        console.log(`[API-PRODUCER] ${timestamp} - INFO: ${message}`);
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
            this.port = await findAvailablePort(3002);
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
                
                // Register with service registry
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

// Create and start the API Producer
if (require.main === module) {
    const apiProducer = new ApiProducerModule();
    
    // Handle shutdown signals
    process.on('SIGINT', () => {
        console.log('\nReceived SIGINT, shutting down gracefully...');
        apiProducer.stop();
    });
    
    process.on('SIGTERM', () => {
        console.log('\nReceived SIGTERM, shutting down gracefully...');
        apiProducer.stop();
    });
    
    // Start the service
    apiProducer.start();
}

module.exports = ApiProducerModule;
