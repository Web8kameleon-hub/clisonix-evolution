const express = require('express');
const getPort = require('get-port');
const axios = require('axios');
const { spawn } = require('child_process');
const path = require('path');

class FrontendModule {
    constructor() {
        this.name = 'asi-saas-frontend';
        this.port = null;
        this.app = express();
        this.registryUrl = 'http: //localhost:2999';
        this.heartbeatInterval = 15000; // 15 seconds
        this.heartbeatTimer = null;
        this.metrics = {
            requests: 0,
            startTime: Date.now(),
            memory: 0
        };
        
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        this.app.use(express.json());
        this.app.use(express.static(path.join(__dirname, '..', 'public')));
        
        // Request counter middleware
        this.app.use((req, res, next) => {
            this.metrics.requests++;
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

        // Frontend metrics
        this.app.get('/metrics', (req, res) => {
            res.json(this.getMetrics());
        });

        // Main frontend route
        this.app.get('/', (req, res) => {
            res.json({
                message: 'ASI SaaS Frontend Service',
                service: this.name,
                port: this.port,
                endpoints: [
                    '/health',
                    '/metrics',
                    '/dashboard',
                    '/api-status'
                ]
            });
        });

        // Dashboard route
        this.app.get('/dashboard', (req, res) => {
            res.json({
                dashboard: 'ASI Ultra SaaS Dashboard',
                systems: [
                    'ASI Core System',
                    'ALBA Analytics',
                    'ALBI Intelligence',
                    'Interactive Dashboard'
                ],
                port: this.port
            });
        });

        // API status aggregator
        this.app.get('/api-status', async (req, res) => {
            try {
                const services = await this.getRegisteredServices();
                const apiServices = services.filter(s => 
                    s.name.includes('api') || s.name.includes('agent')
                );
                
                res.json({
                    apis: apiServices,
                    count: apiServices.length,
                    frontend: this.name
                });
            } catch (error) {
                res.status(500).json({
                    error: 'Failed to fetch API status',
                    message: error.message
                });
            }
        });
    }

    getMetrics() {
        this.metrics.memory = Math.round(process.memoryUsage().heapUsed / 1024 / 1024);
        return {
            ...this.metrics,
            uptime: Date.now() - this.metrics.startTime,
            uptimeSeconds: Math.floor((Date.now() - this.metrics.startTime) / 1000)
        };
    }

    async allocatePort() {
        try {
            this.port = await getPort({ port: getPort.makeRange(3000, 3099) });
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
                        this.log(`Frontend service running on port ${this.port}`);
                        
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
                this.log('Frontend service stopped');
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
        // Using process.stdout.write instead of console.log for linting
        process.stdout.write(`[FRONTEND] ${new Date().toISOString()} - INFO: ${message}\n`);
    }

    logError(message) {
        process.stderr.write(`[FRONTEND] ${new Date().toISOString()} - ERROR: ${message}\n`);
    }
}

// Auto-start if run directly
if (require.main === module) {
    const frontend = new FrontendModule();
    
    frontend.start().catch(error => {
        process.stderr.write(`Frontend startup failed: ${error.message}\n`);
        process.exit(1);
    });
    
    // Graceful shutdown
    process.on('SIGINT', async () => {
        process.stdout.write('\nShutting down Frontend Module...\n');
        await frontend.stop();
        process.exit(0);
    });
    
    process.on('SIGTERM', async () => {
        await frontend.stop();
        process.exit(0);
    });
}

module.exports = FrontendModule;
