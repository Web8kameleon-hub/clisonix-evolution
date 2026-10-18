#!/usr/bin/env node
/**
 * 🌳 ASI AUTONOMOUS TREE ORCHESTRATOR
 * Self-healing, auto-discovery monorepo management system
 * 
 * @version 9.0.0 - Autonomous Architecture
 * @author Ledjan Ahmati <dealsjona@gmail.com>
 * @description 🧠 AUTONOMOUS TREE: Self-healing, port discovery, state persistence
 */

import { spawn } from 'child_process';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { createServer } from 'http';

class ASIAutonomousTreeManager {
    constructor() {
        this.treeConfig = this.loadTreeConfig();
        this.services = new Map();
        this.startTime = new Date();
        this.portRange = { min: 3001, max: 3020 };
        this.stateFile = './tree-state.json';
        this.healInterval = null;
        this.metrics = {
            totalRestarts: 0,
            totalRequests: 0,
            averageLatency: 0,
            uptime: 0
        };
    }

    loadTreeConfig() {
        const configPath = './monorepo-tree.json';
        if (existsSync(configPath)) {
            return JSON.parse(readFileSync(configPath, 'utf8'));
        }
        return this.getDefaultConfig();
    }

    getDefaultConfig() {
        return {
            tree: {
                branches: {
                    components: [
                        {
                            name: "asi-saas-frontend",
                            role: "user-interface-branch",
                            command: "cd asi-saas-frontend; npm run dev",
                            preferredPort: 3001,
                            healthEndpoint: "/"
                        },
                        {
                            name: "api-gateway", 
                            role: "data-gateway-branch",
                            command: "cd api-gateway; node server.js",
                            preferredPort: 3003,
                            healthEndpoint: "/health"
                        },
                        {
                            name: "asi-agent-ultra-demo",
                            role: "demonstration-branch",
                            command: "node asi-agent-ultra-demo.js",
                            preferredPort: 3004,
                            healthEndpoint: "/health"
                        },
                        {
                            name: "asi-api-producer",
                            role: "production-branch",
                            command: "node asi-api-producer.js",
                            preferredPort: 3005,
                            healthEndpoint: "/health"
                        }
                    ]
                }
            }
        };
    }

    async findAvailablePort(preferredPort = 3001) {
        // Try preferred port first
        if (await this.isPortAvailable(preferredPort)) {
            return preferredPort;
        }

        // Search range for available port
        for (let port = this.portRange.min; port <= this.portRange.max; port++) {
            if (await this.isPortAvailable(port)) {
                this.log('🔄', `Port ${preferredPort} busy, using ${port}`, 'yellow');
                return port;
            }
        }
        
        throw new Error(`No available ports in range ${this.portRange.min}-${this.portRange.max}`);
    }

    async isPortAvailable(port) {
        return new Promise((resolve) => {
            const server = createServer();
            
            server.listen(port, () => {
                server.close(() => resolve(true));
            });
            
            server.on('error', () => resolve(false));
        });
    }

    async plantTree() {
        this.log('🌳', 'PLANTING ASI AUTONOMOUS TREE...', 'green');
        this.log('🌱', 'Initializing roots with auto-discovery...', 'cyan');
        
        // Load previous state if exists
        this.loadTreeState();
        
        await this.sleep(500);
        this.log('🌱', 'Root configuration loaded', 'green');

        this.log('🌲', 'Growing autonomous trunk - Self-healing coordination active', 'cyan');
        await this.sleep(500);

        this.log('🌿', 'Growing branches with port auto-discovery...', 'cyan');
        await this.startBranches();

        await this.sleep(2000);
        this.log('🍎', 'Harvesting fruits with health validation...', 'cyan');
        await this.validateFruits();

        // Start auto-healing system
        this.startAutoHealing();

        this.showTreeStatus();
        this.saveTreeState();
    }

    async startBranches() {
        const branches = this.treeConfig.tree.branches.components;
        
        for (const branch of branches) {
            try {
                const availablePort = await this.findAvailablePort(branch.preferredPort);
                branch.port = availablePort;
                
                this.log('🌿', `Starting ${branch.name} on port ${availablePort}...`, 'yellow');
                await this.startService(branch);
                await this.sleep(2000); // Give time to start properly
            } catch (error) {
                this.log('❌', `Failed to start ${branch.name}: ${error.message}`, 'red');
            }
        }
    }

    async startService(service) {
        return new Promise((resolve) => {
            // Fix command execution - use shell directly for complex commands
            let command, args, options;
            
            // For Windows PowerShell compatibility
            if (process.platform === 'win32') {
                command = 'powershell.exe';
                args = ['-Command', service.command];
                options = {
                    cwd: process.cwd(),
                    stdio: ['ignore', 'pipe', 'pipe'],
                    env: { ...process.env, PORT: service.port.toString() }
                };
            } else {
                command = 'sh';
                args = ['-c', service.command];
                options = {
                    cwd: process.cwd(),
                    stdio: ['ignore', 'pipe', 'pipe'],
                    env: { ...process.env, PORT: service.port.toString() }
                };
            }

            this.log('🍎', `Growing fruit: ${service.name} (${service.command})`, 'green');
            
            const childProcess = spawn(command, args, options);

            this.services.set(service.name, {
                ...service,
                process: childProcess,
                startTime: new Date(),
                status: 'starting',
                restartCount: 0
            });

            childProcess.stdout?.on('data', (data) => {
                const output = data.toString();
                if (output.includes('ready') || output.includes('started') || output.includes('listening')) {
                    const serviceData = this.services.get(service.name);
                    serviceData.status = 'running';
                    this.services.set(service.name, serviceData);
                    this.log('✅', `${service.name} is ready on port ${service.port}`, 'green');
                }
            });

            childProcess.stderr?.on('data', (data) => {
                const error = data.toString();
                if (!error.includes('ExperimentalWarning') && !error.includes('DeprecationWarning')) {
                    this.log('⚠️', `${service.name}: ${error.trim()}`, 'yellow');
                }
            });

            childProcess.on('error', (err) => {
                this.log('❌', `Error starting ${service.name}: ${err.message}`, 'red');
            });

            childProcess.on('exit', (code) => {
                if (code !== 0) {
                    this.log('🪓', `${service.name} exited with code ${code}`, 'red');
                    const serviceData = this.services.get(service.name);
                    if (serviceData) {
                        serviceData.status = 'crashed';
                        this.services.set(service.name, serviceData);
                    }
                }
            });

            setTimeout(() => {
                const serviceData = this.services.get(service.name);
                if (serviceData && serviceData.status === 'starting') {
                    serviceData.status = 'running';
                    this.services.set(service.name, serviceData);
                }
                resolve();
            }, 1500);
        });
    }

    async validateFruits() {
        const fruits = [];
        
        // Build fruits dynamically from services
        this.services.forEach((service, name) => {
            const endpoint = service.healthEndpoint || '/health';
            fruits.push({
                name,
                url: `http://localhost:${service.port}${endpoint}`,
                port: service.port
            });
        });

        for (const fruit of fruits) {
            try {
                const startTime = Date.now();
                const response = await fetch(fruit.url, { 
                    method: 'GET',
                    signal: AbortSignal.timeout(3000)
                });
                
                const latency = Date.now() - startTime;
                this.metrics.totalRequests++;
                this.metrics.averageLatency = ((this.metrics.averageLatency * (this.metrics.totalRequests - 1)) + latency) / this.metrics.totalRequests;
                
                if (response.ok) {
                    this.log('🍎', `${fruit.name} - Fruit ready! (${latency}ms)`, 'green');
                } else {
                    this.log('🥀', `${fruit.name} - Response ${response.status} (${latency}ms)`, 'yellow');
                }
            } catch (err) {
                this.log('🥀', `${fruit.name} - Connection failed`, 'red');
            }
        }

        // Auto-heal after validation
        await this.autoHealTree();
    }

    async autoHealTree() {
        this.log('🔬', 'Running autonomous tree health scan...', 'cyan');
        
        for (const [name, service] of this.services) {
            if (service.status === 'crashed' || service.status === 'starting') {
                this.log('🪓', `${name} unhealthy - Auto-healing...`, 'yellow');
                
                try {
                    // Kill existing process if still running
                    if (service.process && !service.process.killed) {
                        service.process.kill();
                    }
                    
                    // Find new port and restart
                    const newPort = await this.findAvailablePort(service.preferredPort);
                    service.port = newPort;
                    
                    await this.startService(service);
                    
                    const serviceData = this.services.get(name);
                    serviceData.restartCount = (serviceData.restartCount || 0) + 1;
                    serviceData.status = 'restarted';
                    this.services.set(name, serviceData);
                    
                    this.metrics.totalRestarts++;
                    this.log('🌿', `${name} auto-healed on port ${newPort}`, 'green');
                    
                } catch (error) {
                    this.log('💀', `Failed to heal ${name}: ${error.message}`, 'red');
                }
            }
        }
    }

    startAutoHealing() {
        this.log('🤖', 'Starting autonomous healing system...', 'green');
        
        this.healInterval = setInterval(async () => {
            await this.autoHealTree();
            this.saveTreeState();
        }, 30000); // Check every 30 seconds
    }

    loadTreeState() {
        if (existsSync(this.stateFile)) {
            try {
                const state = JSON.parse(readFileSync(this.stateFile, 'utf8'));
                this.log('🔄', `Loaded previous tree state: ${state.services?.length || 0} services`, 'cyan');
                return state;
            } catch (err) {
                this.log('⚠️', `Failed to load tree state: ${err.message}`, 'yellow');
            }
        }
        return null;
    }

    saveTreeState() {
        const state = {
            timestamp: new Date().toISOString(),
            services: Array.from(this.services.entries()).map(([name, service]) => ({
                name,
                port: service.port,
                status: service.status,
                startTime: service.startTime,
                restartCount: service.restartCount || 0
            })),
            metrics: {
                ...this.metrics,
                uptime: Math.floor((Date.now() - this.startTime.getTime()) / 1000)
            }
        };

        try {
            writeFileSync(this.stateFile, JSON.stringify(state, null, 2));
            this.log('💾', 'Tree state saved', 'green');
        } catch (err) {
            this.log('⚠️', `Failed to save state: ${err.message}`, 'yellow');
        }
    }

    showTreeStatus() {
        console.log('\n🌳 ========================================');
        console.log('🤖    ASI AUTONOMOUS TREE STATUS');  
        console.log('🌳 ========================================');
        console.log(`⏰ Planted: ${this.startTime.toLocaleString()}`);
        console.log(`🤖 Gardener: Autonomous ASI System`);
        console.log(`📊 Active Branches: ${this.services.size}`);
        console.log(`🔄 Total Restarts: ${this.metrics.totalRestarts}`);
        console.log(`⚡ Avg Latency: ${Math.round(this.metrics.averageLatency)}ms`);
        console.log(`⏱️ Uptime: ${Math.floor((Date.now() - this.startTime.getTime()) / 1000)}s\n`);

        console.log('🚀 AUTONOMOUS BRANCHES:');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        this.services.forEach((service, name) => {
            const uptime = Math.floor((Date.now() - service.startTime.getTime()) / 1000);
            const status = service.status === 'running' ? '✅' : 
                          service.status === 'restarted' ? '🔄' : 
                          service.status === 'crashed' ? '💀' : '⚠️';
            const url = `http://localhost:${service.port}`;
            const restarts = service.restartCount ? ` (${service.restartCount} restarts)` : '';
            
            console.log(`  ${status} ${name.padEnd(25)} Port: ${service.port}  ${url}  ${uptime}s${restarts}`);
        });

        console.log('\n🌍 AUTONOMOUS FRUITS:');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        this.services.forEach((service, name) => {
            const endpoint = service.healthEndpoint || '/health';
            console.log(`  🍎 ${name}: http://localhost:${service.port}${endpoint}`);
        });

        console.log('\n🎉 ========================================');
        console.log('🤖 ASI AUTONOMOUS TREE IS SELF-MANAGING!');
        console.log('🎉 ========================================');
        
        console.log('\n💡 Autonomous Features:');
        console.log('   🔄 Auto-healing every 30s');
        console.log('   🔍 Dynamic port discovery');
        console.log('   💾 Persistent state management');
        console.log('   📊 Real-time metrics collection');
        console.log('   🤖 Zero-intervention operation');
    }

    log(icon, message, color = 'white') {
        const colors = {
            red: '\x1b[31m',
            green: '\x1b[32m', 
            yellow: '\x1b[33m',
            blue: '\x1b[34m',
            magenta: '\x1b[35m',
            cyan: '\x1b[36m',
            white: '\x1b[37m',
            reset: '\x1b[0m'
        };
        
        const timestamp = new Date().toLocaleTimeString();
        console.log(`${colors[color]}[${timestamp}] ${icon} ${message}${colors.reset}`);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async stopTree() {
        this.log('🔥', 'Stopping ASI Autonomous Tree...', 'red');
        
        // Stop auto-healing
        if (this.healInterval) {
            clearInterval(this.healInterval);
        }
        
        // Stop all services
        for (const [name, service] of this.services) {
            try {
                if (service.process && !service.process.killed) {
                    service.process.kill();
                    this.log('✅', `Stopped ${name}`, 'yellow');
                }
            } catch (err) {
                this.log('❌', `Error stopping ${name}: ${err.message}`, 'red');
            }
        }
        
        // Save final state
        this.saveTreeState();
        
        this.services.clear();
        this.log('🌳', 'Autonomous tree has been shut down. Seeds preserved for replanting.', 'green');
    }
}

// 🌳 Autonomous Tree Command Handler
const command = process.argv[2];
const autonomousTree = new ASIAutonomousTreeManager();

switch (command) {
    case 'plant':
    case 'start':
    default:
        autonomousTree.plantTree();
        break;
    case 'stop':
    case 'cut':
        autonomousTree.stopTree();
        process.exit(0);
        break;
    case 'status':
    case 'health':
        autonomousTree.showTreeStatus();
        break;
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🔥 Received interrupt signal, shutting down autonomous tree...');
    autonomousTree.stopTree().then(() => process.exit(0));
});

process.on('SIGTERM', () => {
    console.log('\n🔥 Received terminate signal, shutting down autonomous tree...');
    autonomousTree.stopTree().then(() => process.exit(0));
});
