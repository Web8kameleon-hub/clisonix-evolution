const express = require('express');
const getPort = require('get-port');
const axios = require('axios');

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
                message: 'ASI API Producer Service',
                service: this.name,
                port: this.port,
                version: '1.0.0',
                capabilities: [
                    'Data Generation',
                    'API Endpoints',
                    'Real-time Processing',
                    'Analytics Integration'
                ],
                endpoints: [
                    '/health',
                    '/metrics',
                    '/api/generate',
                    '/api/analytics',
                    '/api/realtime',
                    '/api/asi-data'
                ]
            });
        });

        // Data generation endpoint
        this.app.post('/api/generate', (req, res) => {
            const { type, count = 10, format = 'json' } = req.body;
            
            try {
                let generatedData = [];
                
                switch (type) {
                    case 'users':
                        generatedData = this.generateUsers(count);
                        break;
                    case 'metrics':
                        generatedData = this.generateMetrics(count);
                        break;
                    case 'events':
                        generatedData = this.generateEvents(count);
                        break;
                    default:
                        generatedData = this.generateGeneric(count);
                }
                
                this.metrics.dataGenerated += count;
                
                res.json({
                    success: true,
                    type: type || 'generic',
                    count: generatedData.length,
                    format: format,
                    data: generatedData,
                    generated_at: new Date().toISOString()
                });
                
            } catch (error) {
                this.metrics.errors++;
                this.logError(`Data generation error: ${error.message}`);
                res.status(500).json({
                    error: 'Data generation failed',
                    message: error.message
                });
            }
        });

        // Analytics endpoint
        this.app.get('/api/analytics', async (req, res) => {
            try {
                const services = await this.getRegisteredServices();
                const analytics = {
                    producer: this.name,
                    timestamp: new Date().toISOString(),
                    service_analytics: {
                        total_services: services.length,
                        active_services: services.filter(s => s.status === 'active').length,
                        service_distribution: this.analyzeServices(services)
                    },
                    system_metrics: this.getMetrics(),
                    performance: {
                        avg_response_time: Math.floor(Math.random() * 100) + 50,
                        throughput: Math.floor(Math.random() * 1000) + 500,
                        error_rate: (this.metrics.errors / this.metrics.requests * 100).toFixed(2)
                    }
                };
                
                res.json(analytics);
            } catch (error) {
                this.metrics.errors++;
                res.status(500).json({
                    error: 'Analytics generation failed',
                    message: error.message
                });
            }
        });

        // Real-time data endpoint
        this.app.get('/api/realtime', (req, res) => {
            res.writeHead(200, {
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            });

            const sendData = () => {
                const data = {
                    timestamp: new Date().toISOString(),
                    producer: this.name,
                    real_time_metrics: {
                        cpu_usage: Math.floor(Math.random() * 100),
                        memory_usage: this.metrics.memory,
                        requests_per_second: Math.floor(Math.random() * 50) + 10,
                        active_connections: Math.floor(Math.random() * 100) + 1
                    },
                    system_status: 'operational'
                };
                res.write(`data: ${JSON.stringify(data)}\n\n`);
            };

            // Send initial data
            sendData();
            
            // Send data every 3 seconds
            const interval = setInterval(sendData, 3000);

            // Cleanup on disconnect
            req.on('close', () => {
                clearInterval(interval);
            });
        });

        // ASI-specific data endpoint
        this.app.get('/api/asi-data', (req, res) => {
            const asiData = {
                asi_system: {
                    version: '2.0.0',
                    status: 'operational',
                    modules: [
                        'Core Intelligence',
                        'ALBA Analytics',
                        'ALBI Processing',
                        'Neural Networks'
                    ]
                },
                intelligence_metrics: {
                    processing_power: Math.floor(Math.random() * 100) + 80,
                    learning_rate: (Math.random() * 0.1 + 0.9).toFixed(3),
                    accuracy: (Math.random() * 0.05 + 0.95).toFixed(3),
                    confidence: Math.floor(Math.random() * 20) + 80
                },
                data_insights: this.generateInsights(),
                timestamp: new Date().toISOString()
            };

            res.json(asiData);
        });
    }

    generateUsers(count) {
        const names = ['Alice', 'Bob', 'Carol', 'David', 'Eve', 'Frank', 'Grace', 'Henry'];
        const domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'company.com'];
        
        return Array.from({ length: count }, (_, i) => ({
            id: i + 1,
            name: names[Math.floor(Math.random() * names.length)],
            email: `user${i + 1}@${domains[Math.floor(Math.random() * domains.length)]}`,
            created_at: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
            active: Math.random() > 0.3
        }));
    }

    generateMetrics(count) {
        return Array.from({ length: count }, (_, i) => ({
            id: i + 1,
            metric_name: `metric_${i + 1}`,
            value: Math.floor(Math.random() * 1000),
            unit: ['requests', 'users', 'bytes', 'ms'][Math.floor(Math.random() * 4)],
            timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
        }));
    }

    generateEvents(count) {
        const events = ['user_login', 'api_call', 'data_process', 'system_alert', 'backup_complete'];
        
        return Array.from({ length: count }, (_, i) => ({
            id: i + 1,
            event_type: events[Math.floor(Math.random() * events.length)],
            severity: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
            message: `Event ${i + 1} occurred`,
            timestamp: new Date(Date.now() - Math.random() * 60 * 60 * 1000).toISOString()
        }));
    }

    generateGeneric(count) {
        return Array.from({ length: count }, (_, i) => ({
            id: i + 1,
            value: Math.random(),
            category: `category_${Math.floor(Math.random() * 5) + 1}`,
            timestamp: new Date().toISOString()
        }));
    }

    generateInsights() {
        return [
            'System performance is optimal',
            'User engagement has increased by 15%',
            'API response times are within acceptable limits',
            'Data processing efficiency improved',
            'Neural network accuracy at 98.5%'
        ][Math.floor(Math.random() * 5)];
    }

    analyzeServices(services) {
        return services.reduce((acc, service) => {
            const category = service.name.includes('api') ? 'api' : 
                           service.name.includes('agent') ? 'agent' : 
                           service.name.includes('frontend') ? 'frontend' : 'other';
            acc[category] = (acc[category] || 0) + 1;
            return acc;
        }, {});
    }

    getMetrics() {
        this.metrics.memory = Math.round(process.memoryUsage().heapUsed / 1024 / 1024);
        return {
            ...this.metrics,
            uptime: Date.now() - this.metrics.startTime,
            uptimeSeconds: Math.floor((Date.now() - this.metrics.startTime) / 1000),
            errorRate: this.metrics.requests > 0 ? 
                ((this.metrics.errors / this.metrics.requests) * 100).toFixed(2) : 0,
            dataPerRequest: this.metrics.requests > 0 ? 
                (this.metrics.dataGenerated / this.metrics.requests).toFixed(2) : 0
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
                        this.log(`API Producer service running on port ${this.port}`);
                        
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
                this.log('API Producer service stopped');
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
        process.stdout.write(`[API-PRODUCER] ${new Date().toISOString()} - INFO: ${message}\n`);
    }

    logError(message) {
        process.stderr.write(`[API-PRODUCER] ${new Date().toISOString()} - ERROR: ${message}\n`);
    }
}

// Auto-start if run directly
if (require.main === module) {
    const apiProducer = new ApiProducerModule();
    
    apiProducer.start().catch(error => {
        process.stderr.write(`API Producer startup failed: ${error.message}\n`);
        process.exit(1);
    });
    
    // Graceful shutdown
    process.on('SIGINT', async () => {
        process.stdout.write('\nShutting down API Producer Module...\n');
        await apiProducer.stop();
        process.exit(0);
    });
    
    process.on('SIGTERM', async () => {
        await apiProducer.stop();
        process.exit(0);
    });
}

module.exports = ApiProducerModule;
