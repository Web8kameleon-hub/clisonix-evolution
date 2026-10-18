const express = require('express');
const getPort = require('get-port');
const axios = require('axios');

class ApiGatewayModule {
    constructor() {
        this.name = 'api-gateway';
        this.port = null;
        this.app = express();
        this.registryUrl = 'http://localhost:2999';
        this.heartbeatInterval = 15000; // 15 seconds
        this.heartbeatTimer = null;
        this.metrics = {
            requests: 0,
            proxiedRequests: 0,
            startTime: Date.now(),
            memory: 0,
            routingErrors: 0
        };
        
        this.setupMiddleware();
        this.setupRoutes();
    }

    setupMiddleware() {
        this.app.use(express.json());
        
        // Request counter middleware
        this.app.use((req, res, next) => {
            this.metrics.requests++;
            next();
        });

        // CORS middleware
        this.app.use((req, res, next) => {
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
            res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
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
        
        // API Health check
        this.app.get('/api/health', (req, res) => {
            res.json({
                service: this.name,
                status: 'healthy',
                port: this.port,
                metrics: this.getMetrics()
            });
        });

        // Gateway metrics
        this.app.get('/metrics', (req, res) => {
            res.json(this.getMetrics());
        });

        // Main gateway route
        this.app.get('/', (req, res) => {
            res.json({
                message: 'ASI API Gateway Service',
                service: this.name,
                port: this.port,
                version: '1.0.0',
                endpoints: [
                    '/health',
                    '/metrics',
                    '/gateway/routes',
                    '/gateway/services',
                    '/api/*'
                ]
            });
        });

        // Gateway routes info
        this.app.get('/gateway/routes', async (req, res) => {
            try {
                const services = await this.getRegisteredServices();
                const routes = services.map(service => ({
                    path: `/api/${service.name}`,
                    target: `http://localhost:${service.port}`,
                    status: service.status,
                    lastHeartbeat: service.lastHeartbeat
                }));
                
                res.json({
                    gateway: this.name,
                    routes: routes,
                    count: routes.length
                });
            } catch (error) {
                res.status(500).json({
                    error: 'Failed to fetch routes',
                    message: error.message
                });
            }
        });

        // Services status
        this.app.get('/gateway/services', async (req, res) => {
            try {
                const services = await this.getRegisteredServices();
                res.json({
                    services: services,
                    gateway: this.name,
                    total: services.length,
                    active: services.filter(s => s.status === 'active').length
                });
            } catch (error) {
                res.status(500).json({
                    error: 'Failed to fetch services',
                    message: error.message
                });
            }
        });

        // API proxy routes
        this.app.use('/api/:serviceName/*', async (req, res) => {
            const serviceName = req.params.serviceName;
            const apiPath = req.params[0];
            
            try {
                const services = await this.getRegisteredServices();
                const targetService = services.find(s => 
                    s.name === serviceName || 
                    s.name.includes(serviceName)
                );
                
                if (!targetService) {
                    return res.status(404).json({
                        error: 'Service not found',
                        service: serviceName,
                        available: services.map(s => s.name)
                    });
                }
                
                if (targetService.status !== 'active') {
                    return res.status(503).json({
                        error: 'Service unavailable',
                        service: serviceName,
                        status: targetService.status
                    });
                }
                
                const targetUrl = `http://localhost:${targetService.port}/${apiPath}`;
                this.log(`Proxying ${req.method} ${req.path} -> ${targetUrl}`);
                
                const response = await axios({
                    method: req.method,
                    url: targetUrl,
                    data: req.body,
                    params: req.query,
                    headers: {
                        ...req.headers,
                        host: `localhost:${targetService.port}`
                    }
                });
                
                this.metrics.proxiedRequests++;
                res.status(response.status).json(response.data);
                
            } catch (error) {
                this.metrics.routingErrors++;
                this.logError(`Proxy error for ${serviceName}: ${error.message}`);
                
                if (error.response) {
                    res.status(error.response.status).json({
                        error: 'Upstream service error',
                        message: error.response.data || error.message,
                        service: serviceName
                    });
                } else {
                    res.status(502).json({
                        error: 'Gateway error',
                        message: error.message,
                        service: serviceName
                    });
                }
            }
        });

        // Direct service proxy (fallback)
        this.app.use('/proxy/:port/*', async (req, res) => {
            const port = req.params.port;
            const apiPath = req.params[0];
            
            try {
                const targetUrl = `http://localhost:${port}/${apiPath}`;
                this.log(`Direct proxy ${req.method} ${req.path} -> ${targetUrl}`);
                
                const response = await axios({
                    method: req.method,
                    url: targetUrl,
                    data: req.body,
                    params: req.query,
                    headers: {
                        ...req.headers,
                        host: `localhost:${port}`
                    }
                });
                
                this.metrics.proxiedRequests++;
                res.status(response.status).json(response.data);
                
            } catch (error) {
                this.metrics.routingErrors++;
                this.logError(`Direct proxy error for port ${port}: ${error.message}`);
                
                res.status(502).json({
                    error: 'Proxy error',
                    message: error.message,
                    port: port
                });
            }
        });
    }

    getMetrics() {
        this.metrics.memory = Math.round(process.memoryUsage().heapUsed / 1024 / 1024);
        return {
            ...this.metrics,
            uptime: Date.now() - this.metrics.startTime,
            uptimeSeconds: Math.floor((Date.now() - this.metrics.startTime) / 1000),
            proxySuccessRate: this.metrics.proxiedRequests > 0 ? 
                Math.round(((this.metrics.proxiedRequests - this.metrics.routingErrors) / this.metrics.proxiedRequests) * 100) : 100
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
                        this.log(`API Gateway service running on port ${this.port}`);
                        
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
                this.log('API Gateway service stopped');
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
        process.stdout.write(`[API-GATEWAY] ${new Date().toISOString()} - INFO: ${message}\n`);
    }

    logError(message) {
        process.stderr.write(`[API-GATEWAY] ${new Date().toISOString()} - ERROR: ${message}\n`);
    }
}

// Auto-start if run directly
if (require.main === module) {
    const gateway = new ApiGatewayModule();
    
    gateway.start().catch(error => {
        process.stderr.write(`API Gateway startup failed: ${error.message}\n`);
        process.exit(1);
    });
    
    // Graceful shutdown
    process.on('SIGINT', async () => {
        process.stdout.write('\nShutting down API Gateway Module...\n');
        await gateway.stop();
        process.exit(0);
    });
    
    process.on('SIGTERM', async () => {
        await gateway.stop();
        process.exit(0);
    });
}

module.exports = ApiGatewayModule;
