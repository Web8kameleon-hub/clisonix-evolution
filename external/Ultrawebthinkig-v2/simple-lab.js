#!/usr/bin/env node
/**
 * 🌳 ASI MONOREPO SIMPLE STARTER
 * Manual startup sequence with proper port allocation
 */

import { spawn } from 'child_process';
import { setTimeout } from 'timers/promises';

console.log('🌳 ========================================');
console.log('🇦🇱    STARTING ASI MONOREPO TREE');  
console.log('🌳 ========================================\n');

const services = [
    {
        name: "Ultra SaaS Frontend",
        command: "cd asi-saas-frontend && npm run dev",
        port: 3001,
        icon: "🎨",
        delay: 2000
    },
    {
        name: "ASI API Gateway", 
        command: "cd api-gateway && node server.js",
        port: 3003,
        icon: "🌍",
        delay: 3000
    },
    {
        name: "ASI Agent Ultra Demo",
        command: "node asi-agent-ultra-demo.js",
        port: 3004,
        icon: "🇦🇱", 
        delay: 2000
    },
    {
        name: "ASI API Producer",
        command: "node asi-api-producer.js", 
        port: 3005,
        icon: "⚡",
        delay: 2000
    }
];

async function startService(service) {
    console.log(`${service.icon} Starting ${service.name} on port ${service.port}...`);
    
    const [command, ...args] = service.command.split(' ');
    let actualCommand, actualArgs, cwd;
    
    if (command === 'cd') {
        // Handle "cd directory && command"
        cwd = args[0];
        const restCommand = service.command.split(' && ')[1];
        [actualCommand, ...actualArgs] = restCommand.split(' ');
    } else {
        actualCommand = command;
        actualArgs = args;
    }
    
    const child = spawn(actualCommand, actualArgs, {
        cwd: cwd || process.cwd(),
        stdio: ['ignore', 'pipe', 'pipe'],
        shell: true
    });
    
    child.stdout?.on('data', (data) => {
        const output = data.toString();
        if (output.includes('ready') || output.includes('started') || output.includes('listening')) {
            console.log(`✅ ${service.name} is ready on port ${service.port}`);
        }
    });
    
    child.stderr?.on('data', (data) => {
        const error = data.toString();
        if (!error.includes('ExperimentalWarning')) {
            console.log(`⚠️ ${service.name}: ${error.trim()}`);
        }
    });
    
    child.on('error', (err) => {
        console.log(`❌ Error starting ${service.name}: ${err.message}`);
    });
    
    // Wait before starting next service
    await setTimeout(service.delay);
    
    return child;
}

async function startAll() {
    console.log('🌱 Planting ASI Monorepo Tree...\n');
    
    const processes = [];
    
    for (const service of services) {
        const child = await startService(service);
        processes.push({ ...service, process: child });
    }
    
    console.log('\n🌳 ========================================');
    console.log('🇦🇱    ASI MONOREPO TREE STATUS');
    console.log('🌳 ========================================');
    console.log(`⏰ Planted: ${new Date().toLocaleString()}`);
    console.log(`📊 Active Branches: ${processes.length}\n`);
    
    console.log('🚀 TREE BRANCHES:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    processes.forEach(service => {
        const status = '✅';
        const url = `http://localhost:${service.port}`;
        console.log(`  ${status} ${service.name.padEnd(25)} Port: ${service.port}  URL: ${url}`);
    });
    
    console.log('\n🌍 QUICK ACCESS LINKS:');
    console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
    console.log('  🎨 Ultra SaaS Dashboard: http://localhost:3001');
    console.log('  🌍 API Gateway Health: http://localhost:3003/api/health'); 
    console.log('  📊 Interactive Dashboard: http://localhost:3004/demo/interactive-dashboard');
    console.log('  🧠 Ultra Comprehensive: http://localhost:3004/demo/ultra-comprehensive');
    console.log('  🇦🇱 Cultural Analysis: http://localhost:3004/demo/cultural-super-analysis/albania');
    console.log('  ⚡ API Producer Registry: http://localhost:3005/asi/apis-registry');
    
    console.log('\n🎉 ========================================');
    console.log('🇦🇱 ASI MONOREPO TREE IS FLOURISHING!');
    console.log('🎉 ========================================\n');
    
    console.log('💡 Tree Management:');
    console.log('   Ctrl+C           # Stop all services');
    console.log('   node simple-lab.js   # Start tree');
    console.log('   yarn tree        # Alternative start');
    
    // Handle graceful shutdown
    process.on('SIGINT', () => {
        console.log('\n🔥 Cutting down tree...');
        processes.forEach(({ process, name }) => {
            try {
                process.kill();
                console.log(`✅ Stopped ${name}`);
            } catch (err) {
                console.log(`❌ Error stopping ${name}`);
            }
        });
        console.log('🌳 Tree has been cut down. Seeds remain for replanting.');
        process.exit(0);
    });
}

startAll().catch(console.error);
