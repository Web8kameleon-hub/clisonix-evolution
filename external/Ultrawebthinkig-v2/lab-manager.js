#!/usr/bin/env node
/**
 * 🌳 ASI MONOREPO TREE ORCHESTRATOR
 * Hierarchical monorepo laboratory management system
 * 
 * @version 8.0.0 - Tree Architecture 
 * @author Ledjan Ahmati <dealsjona@gmail.com>
 * @description 🌱 ROOTS → 🌲 TRUNK → 🌿 BRANCHES → 🍎 FRUITS
 *              Organic monorepo structure like a living tree
 */

import { spawn } from 'child_process';
import { createServer } from 'http';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { readFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 🧬 Laboratory Configuration
const LAB_CONFIG = {
    version: "1.0.0",
    author: "Ledjan Ahmati",
    email: "dealsjona@gmail.com",
    startPort: 3000,
    services: new Map(),
    processes: new Map(),
    stats: {
        startTime: new Date(),
        totalRequests: 0,
        totalServices: 0,
        uptime: 0
    }
};

// 🎨 Console colors
const colors = {
    reset: '\x1b[0m',
    bright: '\x1b[1m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    white: '\x1b[37m'
};

// 📝 Logging function
function log(message, type = 'INFO') {
    const timestamp = new Date().toLocaleTimeString();
    const icons = {
        SUCCESS: '✅',
        ERROR: '❌', 
        WARNING: '⚠️',
        ASI: '🇦🇱',
        ALBA: '🤖',
        ALBI: '🧠',
        API: '⚡',
        INFO: '📊'
    };
    
    const colorMap = {
        SUCCESS: colors.green,
        ERROR: colors.red,
        WARNING: colors.yellow,
        ASI: colors.cyan,
        ALBA: colors.magenta,
        ALBI: colors.blue,
        API: colors.yellow,
        INFO: colors.white
    };
    
    console.log(`${colorMap[type]}[${timestamp}] ${icons[type]} ${message}${colors.reset}`);
}

// 🔍 Port availability checker
async function isPortAvailable(port) {
    return new Promise((resolve) => {
        const server = createServer();
        server.listen(port, () => {
            server.close(() => resolve(true));
        });
        server.on('error', () => resolve(false));
    });
}

// 🚀 Service starter
async function startService(name, config) {
    try {
        // Find available port
        let port = config.preferredPort || LAB_CONFIG.startPort;
        while (!(await isPortAvailable(port))) {
            port++;
        }
        
        log(`Starting ${name} on port ${port}...`, 'INFO');
        
        // Set environment variables
        const env = { ...process.env, PORT: port, NODE_ENV: 'development' };
        
        // Start the process
        const child = spawn('node', [config.script], {
            cwd: config.workingDir || __dirname,
            env,
            stdio: 'pipe'
        });
        
        // Store process and service info
        LAB_CONFIG.processes.set(name, child);
        LAB_CONFIG.services.set(name, {
            name,
            port,
            pid: child.pid,
            status: 'starting',
            startTime: new Date(),
            url: `http://localhost:${port}`,
            script: config.script,
            workingDir: config.workingDir,
            logs: []
        });
        
        // Handle process output
        child.stdout.on('data', (data) => {
            const service = LAB_CONFIG.services.get(name);
            if (service) {
                service.logs.push({ type: 'stdout', data: data.toString(), timestamp: new Date() });
                if (service.logs.length > 100) service.logs.shift(); // Keep only last 100 logs
            }
        });
        
        child.stderr.on('data', (data) => {
            const service = LAB_CONFIG.services.get(name);
            if (service) {
                service.logs.push({ type: 'stderr', data: data.toString(), timestamp: new Date() });
            }
        });
        
        child.on('close', (code) => {
            log(`${name} process exited with code ${code}`, code === 0 ? 'INFO' : 'ERROR');
            const service = LAB_CONFIG.services.get(name);
            if (service) {
                service.status = code === 0 ? 'stopped' : 'error';
            }
        });
        
        // Wait a bit and check if service started successfully
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        if (!child.killed) {
            const service = LAB_CONFIG.services.get(name);
            service.status = 'running';
            LAB_CONFIG.stats.totalServices++;
            log(`${name} started successfully on ${service.url}`, 'SUCCESS');
            return service;
        } else {
            log(`Failed to start ${name}`, 'ERROR');
            return null;
        }
        
    } catch (error) {
        log(`Error starting ${name}: ${error.message}`, 'ERROR');
        return null;
    }
}

// 🛑 Stop all services
function stopLaboratory() {
    log('Stopping ASI Laboratory...', 'WARNING');
    
    for (const [name, process] of LAB_CONFIG.processes) {
        if (process && !process.killed) {
            log(`Stopping ${name}...`, 'WARNING');
            process.kill('SIGTERM');
        }
    }
    
    LAB_CONFIG.processes.clear();
    LAB_CONFIG.services.clear();
    LAB_CONFIG.stats.totalServices = 0;
    
    log('ASI Laboratory stopped successfully', 'SUCCESS');
}

// 📊 Show laboratory status  
function showStatus() {
    console.log(`${colors.cyan}
🧬 ========================================
🇦🇱      ASI LABORATORY STATUS
🧬 ========================================${colors.reset}`);
    
    console.log(`⏰ Started: ${LAB_CONFIG.stats.startTime.toLocaleString()}`);
    console.log(`👨‍💻 Author: ${LAB_CONFIG.author}`);
    console.log(`📧 Email: ${LAB_CONFIG.email}`);
    console.log(`📊 Active Services: ${LAB_CONFIG.services.size}`);
    console.log('');
    
    if (LAB_CONFIG.services.size === 0) {
        console.log(`${colors.yellow}⚠️ No services are running${colors.reset}`);
        return;
    }
    
    console.log(`${colors.green}🚀 ACTIVE SERVICES:${colors.reset}`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    for (const [name, service] of LAB_CONFIG.services) {
        const uptime = Math.floor((Date.now() - service.startTime) / 1000);
        const status = service.status === 'running' ? '✅' : service.status === 'error' ? '❌' : '⏸️';
        console.log(`  ${status} ${name.padEnd(25)} Port: ${service.port.toString().padStart(4)}  URL: ${service.url}  Uptime: ${uptime}s`);
    }
    
    console.log('');
    console.log(`${colors.cyan}🌍 QUICK LINKS:${colors.reset}`);
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    
    for (const [name, service] of LAB_CONFIG.services) {
        if (service.status === 'running') {
            switch (name) {
                case 'Ultra SaaS Frontend':
                    console.log(`${colors.magenta}  🎨 Ultra SaaS Dashboard: ${service.url}${colors.reset}`);
                    break;
                case 'ASI API Gateway':
                    console.log(`${colors.blue}  🌍 API Gateway: ${service.url}${colors.reset}`);
                    console.log(`${colors.white}     📊 Health Check: ${service.url}/api/health${colors.reset}`);
                    break;
                case 'ASI Agent Ultra Demo':
                    console.log(`${colors.red}  🇦🇱 ASI Demo System: ${service.url}${colors.reset}`);
                    console.log(`${colors.white}     🧠 Interactive Dashboard: ${service.url}/demo/interactive-dashboard${colors.reset}`);
                    break;
                case 'ASI API Producer':
                    console.log(`${colors.yellow}  ⚡ API Producer: ${service.url}${colors.reset}`);
                    console.log(`${colors.white}     📋 API Registry: ${service.url}/asi/apis-registry${colors.reset}`);
                    break;
            }
        }
    }
    
    console.log('');
}

// 🚀 Start the complete laboratory
async function startLaboratory() {
    console.log(`${colors.cyan}
🧬 ========================================
🇦🇱    STARTING ASI LABORATORY
🧬 ========================================${colors.reset}
`);
    
    log('Initializing ASI Laboratory...', 'ASI');
    log('Monorepo integrated orchestration system', 'ASI');
    console.log('');
    
    // Service configurations
    const services = [
        {
            name: 'Ultra SaaS Frontend',
            script: 'node_modules/.bin/next',
            preferredPort: 3002,
            workingDir: join(__dirname, 'asi-saas-frontend')
        },
        {
            name: 'ASI API Gateway', 
            script: 'server.js',
            preferredPort: 3003,
            workingDir: join(__dirname, 'api-gateway')
        },
        {
            name: 'ASI Agent Ultra Demo',
            script: 'asi-agent-ultra-demo.js',
            preferredPort: 3004,
            workingDir: __dirname
        },
        {
            name: 'ASI API Producer',
            script: 'asi-api-producer.js', 
            preferredPort: 3005,
            workingDir: __dirname
        }
    ];
    
    // Start all services
    for (const serviceConfig of services) {
        await startService(serviceConfig.name, serviceConfig);
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1s between services
    }
    
    console.log('');
    log('ASI Laboratory started successfully!', 'SUCCESS');
    log(`Total services: ${LAB_CONFIG.services.size}`, 'SUCCESS');
    console.log('');
    
    showStatus();
    
    console.log(`${colors.green}
🎉 ========================================
🇦🇱 ASI LABORATORY IS READY!
🎉 ========================================${colors.reset}
`);
    
    console.log(`${colors.yellow}💡 Control commands:${colors.reset}`);
    console.log('   node lab-manager.js status    # Show status');
    console.log('   node lab-manager.js stop      # Stop laboratory');
    console.log('   node lab-manager.js restart   # Restart laboratory');
    console.log('   yarn lab                      # Quick start');
    console.log('');
}

// 🎯 Main execution
const action = process.argv[2] || 'start';

switch (action.toLowerCase()) {
    case 'start':
        await startLaboratory();
        break;
        
    case 'stop':
        stopLaboratory();
        break;
        
    case 'status':
        showStatus();
        break;
        
    case 'restart':
        log('Restarting ASI Laboratory...', 'WARNING');
        stopLaboratory();
        await new Promise(resolve => setTimeout(resolve, 2000));
        await startLaboratory();
        break;
        
    default:
        console.log(`${colors.red}❌ Unknown command: ${action}${colors.reset}`);
        console.log(`${colors.green}✅ Valid commands: start, stop, status, restart${colors.reset}`);
}

// Handle process termination
process.on('SIGINT', () => {
    console.log('\n');
    log('Received SIGINT, shutting down gracefully...', 'WARNING');
    stopLaboratory();
    process.exit(0);
});

process.on('SIGTERM', () => {
    log('Received SIGTERM, shutting down gracefully...', 'WARNING'); 
    stopLaboratory();
    process.exit(0);
});
