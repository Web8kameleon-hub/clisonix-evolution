/**
 * ASI Registry Service - Port 3006
 * Service Discovery and Health Monitoring for ASI Laboratory
 */

import express from 'express';
import cors from 'cors';

class ASIRegistryService {
    constructor() {
        this.app = express();
        this.port = 3006;
        this.services = new Map();
        this.healthChecks = new Map();
        
        this.setupMiddleware();
        this.setupRoutes();
        this.initializeServices();
    }
    
    setupMiddleware() {
        this.app.use(cors({
            origin: ['http://localhost:3001', 'http://localhost:3003', 'http://localhost:3004', 'http://localhost:3005'],
            credentials: true
        }));
        
        this.app.use(express.json({ limit: '50mb' }));
        this.app.use(express.urlencoded({ extended: true, limit: '50mb' }));
        
        // Request logging
        this.app.use((req, res, next) => {
            console.log(`📋 Registry Request: ${req.method} ${req.path} - ${new Date().toISOString()}`);
            next();
        });
    }
    
    setupRoutes() {
        // Health check
        this.app.get('/registry/health', (req, res) => this.healthCheck(req, res));
        
        // Service registry
        this.app.get('/registry/services', (req, res) => this.getServices(req, res));
        this.app.post('/registry/register', (req, res) => this.registerService(req, res));
        this.app.delete('/registry/unregister/:serviceId', (req, res) => this.unregisterService(req, res));
        
        // Metrics and monitoring
        this.app.get('/registry/metrics', (req, res) => this.getMetrics(req, res));
        this.app.get('/registry/status/:serviceId', (req, res) => this.getServiceStatus(req, res));
        
        // Discovery
        this.app.get('/registry/discover/:serviceType', (req, res) => this.discoverServices(req, res));
    }
    
    async initializeServices() {
        // Register core ASI Laboratory services
        this.services.set('frontend', {
            id: 'frontend',
            name: 'Ultra SaaS Frontend',
            type: 'next.js',
            port: 3001,
            status: 'active',
            health_endpoint: 'http://localhost:3001/api/health',
            last_seen: new Date().toISOString()
        });
        
        this.services.set('api-gateway', {
            id: 'api-gateway',
            name: 'ASI API Gateway',
            type: 'node.js',
            port: 3003,
            status: 'active',
            health_endpoint: 'http://localhost:3003/api/health',
            last_seen: new Date().toISOString()
        });
        
        this.services.set('asi-demo', {
            id: 'asi-demo',
            name: 'ASI Agent Ultra Demo',
            type: 'node.js',
            port: 3004,
            status: 'active',
            health_endpoint: 'http://localhost:3004/demo/health',
            last_seen: new Date().toISOString()
        });
        
        this.services.set('api-producer', {
            id: 'api-producer',
            name: 'ASI API Producer',
            type: 'node.js',
            port: 3005,
            status: 'active',
            health_endpoint: 'http://localhost:3005/api/health',
            last_seen: new Date().toISOString()
        });
        
        console.log(`✅ Registry initialized with ${this.services.size} services`);
    }
    
    async healthCheck(req, res) {
        try {
            const healthStatus = {
                status: 'healthy',
                service: 'ASI Registry Service',
                port: this.port,
                timestamp: new Date().toISOString(),
                registered_services: this.services.size,
                active_services: Array.from(this.services.values()).filter(s => s.status === 'active').length
            };
            
            res.json(healthStatus);
        } catch (error) {
            res.status(500).json({ 
                status: 'error', 
                message: error.message 
            });
        }
    }
    
    async getServices(req, res) {
        try {
            const services = Array.from(this.services.values());
            res.json({
                services,
                count: services.length,
                timestamp: new Date().toISOString()
            });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    async registerService(req, res) {
        try {
            const { id, name, type, port, health_endpoint } = req.body;
            
            const service = {
                id,
                name,
                type,
                port,
                status: 'active',
                health_endpoint,
                registered_at: new Date().toISOString(),
                last_seen: new Date().toISOString()
            };
            
            this.services.set(id, service);
            
            res.json({ 
                success: true, 
                service,
                message: `Service ${name} registered successfully` 
            });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    async unregisterService(req, res) {
        try {
            const { serviceId } = req.params;
            
            if (this.services.has(serviceId)) {
                this.services.delete(serviceId);
                res.json({ 
                    success: true, 
                    message: `Service ${serviceId} unregistered successfully` 
                });
            } else {
                res.status(404).json({ 
                    error: `Service ${serviceId} not found` 
                });
            }
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    async getMetrics(req, res) {
        try {
            const services = Array.from(this.services.values());
            const metrics = {
                total_services: services.length,
                active_services: services.filter(s => s.status === 'active').length,
                inactive_services: services.filter(s => s.status === 'inactive').length,
                service_types: [...new Set(services.map(s => s.type))],
                last_updated: new Date().toISOString()
            };
            
            res.json(metrics);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    async getServiceStatus(req, res) {
        try {
            const { serviceId } = req.params;
            const service = this.services.get(serviceId);
            
            if (!service) {
                return res.status(404).json({ error: 'Service not found' });
            }
            
            res.json(service);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    async discoverServices(req, res) {
        try {
            const { serviceType } = req.params;
            const services = Array.from(this.services.values())
                .filter(s => s.type === serviceType && s.status === 'active');
            
            res.json({
                type: serviceType,
                services,
                count: services.length
            });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    }
    
    start() {
        this.server = this.app.listen(this.port, () => {
            console.log(`🚀 ASI Registry Service running on http://localhost:${this.port}`);
            console.log(`📋 Service Registry: http://localhost:${this.port}/registry/services`);
            console.log(`💚 Health Check: http://localhost:${this.port}/registry/health`);
        });
        
        return this.server;
    }
    
    stop() {
        if (this.server) {
            this.server.close();
        }
    }
}

// Start Registry Service
const registryService = new ASIRegistryService();
registryService.start();

export default ASIRegistryService;
