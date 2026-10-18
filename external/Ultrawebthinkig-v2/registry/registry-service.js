const express = require('express');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

class RegistryService {
    constructor() {
        this.app = express();
        this.services = new Map(); // service registry
        this.metrics = {
            totalServices: 0,
            activeServices: 0,
            failedServices: 0,
            uptime: Date.now(),
            heartbeats: 0
        };
        this.TTL = 30000; // 30 seconds TTL
        this.cleanupInterval = 10000; // Check every 10 seconds
        this.port = 2999;
        
        this.setupMiddleware();
        this.setupRoutes();
        this.startCleanupTimer();
        this.logInfo('Registry Service initialized');
    }

    setupMiddleware() {
        this.app.use(express.json());
        this.app.use((req, res, next) => {
            res.header('Access-Control-Allow-Origin', '*');
            res.header('Access-Control-Allow-Headers', 'Content-Type');
            res.header('Access-Control-Allow-Methods', 'GET, POST, DELETE');
            next();
        });
    }

    setupRoutes() {
        // Service registration endpoint
        this.app.post('/register', (req, res) => {
            const { name, port, status, pid } = req.body;
            
            if (!name || !port) {
                return res.status(400).json({ 
                    error: 'Service name and port required' 
                });
            }

            const service = {
                name,
                port: parseInt(port),
                status: status || 'active',
                pid: pid || null,
                registeredAt: Date.now(),
                lastHeartbeat: Date.now(),
                heartbeatCount: 0,
                metrics: {
                    memory: 0,
                    uptime: 0,
                    requests: 0
                }
            };

            this.services.set(name, service);
            this.metrics.totalServices = this.services.size;
            this.updateActiveCount();

            this.logInfo(`Service registered: ${name} on port ${port}`);
            
            res.json({ 
                success: true, 
                message: `Service ${name} registered successfully`,
                service: service
            });
        });

        // Heartbeat endpoint
        this.app.post('/heartbeat', (req, res) => {
            const { name, metrics: serviceMetrics } = req.body;
            
            if (!name) {
                return res.status(400).json({ 
                    error: 'Service name required' 
                });
            }

            const service = this.services.get(name);
            if (!service) {
                return res.status(404).json({ 
                    error: 'Service not found' 
                });
            }

            // Update heartbeat
            service.lastHeartbeat = Date.now();
            service.heartbeatCount++;
            service.status = 'active';
            
            if (serviceMetrics) {
                service.metrics = { ...service.metrics, ...serviceMetrics };
            }

            this.metrics.heartbeats++;
            this.updateActiveCount();

            res.json({ 
                success: true, 
                message: 'Heartbeat received',
                ttl: this.TTL 
            });
        });

        // Get all services
        this.app.get('/services', (req, res) => {
            const servicesArray = Array.from(this.services.values());
            res.json({
                services: servicesArray,
                count: servicesArray.length,
                metrics: this.getRegistryMetrics()
            });
        });

        // Get specific service
        this.app.get('/services/:name', (req, res) => {
            const service = this.services.get(req.params.name);
            if (!service) {
                return res.status(404).json({ 
                    error: 'Service not found' 
                });
            }
            res.json(service);
        });

        // Registry metrics endpoint
        this.app.get('/metrics', (req, res) => {
            res.json(this.getRegistryMetrics());
        });

        // Deregister service
        this.app.delete('/services/:name', (req, res) => {
            const name = req.params.name;
            const deleted = this.services.delete(name);
            
            if (deleted) {
                this.metrics.totalServices = this.services.size;
                this.updateActiveCount();
                this.logInfo(`Service deregistered: ${name}`);
                res.json({ success: true, message: `Service ${name} deregistered` });
            } else {
                res.status(404).json({ error: 'Service not found' });
            }
        });

        // Health check
        this.app.get('/health', (req, res) => {
            res.json({ 
                status: 'healthy', 
                uptime: Date.now() - this.metrics.uptime,
                services: this.services.size 
            });
        });
    }

    updateActiveCount() {
        const now = Date.now();
        let active = 0;
        let failed = 0;

        for (const service of this.services.values()) {
            if (now - service.lastHeartbeat <= this.TTL) {
                active++;
            } else {
                failed++;
            }
        }

        this.metrics.activeServices = active;
        this.metrics.failedServices = failed;
    }

    getRegistryMetrics() {
        return {
            ...this.metrics,
            uptimeSeconds: Math.floor((Date.now() - this.metrics.uptime) / 1000),
            servicesDetail: {
                total: this.services.size,
                active: this.metrics.activeServices,
                stale: this.metrics.failedServices
            }
        };
    }

    startCleanupTimer() {
        setInterval(() => {
            this.cleanupStaleServices();
        }, this.cleanupInterval);
    }

    cleanupStaleServices() {
        const now = Date.now();
        const staleServices = [];

        for (const [name, service] of this.services.entries()) {
            if (now - service.lastHeartbeat > this.TTL) {
                staleServices.push(name);
            }
        }

        if (staleServices.length > 0) {
            this.logWarning(`Cleaning up stale services: ${staleServices.join(', ')}`);
            
            for (const name of staleServices) {
                const service = this.services.get(name);
                service.status = 'stale';
                
                // Attempt self-healing
                this.attemptServiceHeal(name, service);
            }
            
            this.updateActiveCount();
        }
    }

    async attemptServiceHeal(name, service) {
        this.logInfo(`Attempting to heal service: ${name}`);
        
        try {
            // Try to restart the service using the tree configuration
            const treeConfigPath = path.join(__dirname, '..', 'monorepo-tree.json');
            const treeConfig = JSON.parse(await fs.readFile(treeConfigPath, 'utf8'));
            
            // Find service in tree config
            const branch = treeConfig.trunk.branches.find(b => 
                b.fruits.some(f => f.name === name)
            );
            
            if (branch) {
                const fruit = branch.fruits.find(f => f.name === name);
                if (fruit) {
                    this.logInfo(`Restarting service: ${name} with command: ${fruit.command}`);
                    
                    const child = spawn('node', [fruit.command], {
                        cwd: process.cwd(),
                        detached: true,
                        stdio: 'ignore'
                    });
                    
                    child.unref();
                    service.status = 'healing';
                    
                    // Give the service time to restart
                    setTimeout(() => {
                        service.lastHeartbeat = Date.now();
                    }, 5000);
                }
            }
        } catch (error) {
            this.logError(`Failed to heal service ${name}: ${error.message}`);
            service.status = 'failed';
        }
    }

    logInfo(message) {
        console.log(`[REGISTRY] ${new Date().toISOString()} - INFO: ${message}`);
    }

    logWarning(message) {
        console.log(`[REGISTRY] ${new Date().toISOString()} - WARN: ${message}`);
    }

    logError(message) {
        console.log(`[REGISTRY] ${new Date().toISOString()} - ERROR: ${message}`);
    }

    async start() {
        return new Promise((resolve, reject) => {
            this.server = this.app.listen(this.port, (err) => {
                if (err) {
                    this.logError(`Failed to start registry on port ${this.port}: ${err.message}`);
                    reject(err);
                } else {
                    this.logInfo(`Registry Service running on port ${this.port}`);
                    this.logInfo('Available endpoints:');
                    this.logInfo('  POST /register - Register a service');
                    this.logInfo('  POST /heartbeat - Send heartbeat');
                    this.logInfo('  GET /services - List all services');
                    this.logInfo('  GET /services/:name - Get specific service');
                    this.logInfo('  GET /metrics - Registry metrics');
                    this.logInfo('  DELETE /services/:name - Deregister service');
                    this.logInfo('  GET /health - Health check');
                    resolve(this.server);
                }
            });
        });
    }

    stop() {
        if (this.server) {
            this.server.close();
            this.logInfo('Registry Service stopped');
        }
    }
}

// Start the registry service if this file is run directly
if (require.main === module) {
    const registry = new RegistryService();
    registry.start().catch(error => {
        console.error('Failed to start Registry Service:', error);
        process.exit(1);
    });
    
    // Graceful shutdown
    process.on('SIGINT', () => {
        console.log('\nShutting down Registry Service...');
        registry.stop();
        process.exit(0);
    });
}

module.exports = RegistryService;
