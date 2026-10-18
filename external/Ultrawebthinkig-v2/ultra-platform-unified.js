#!/usr/bin/env node

/**
 * 🚀 Ultra Platform Unified - No CD Integration
 * Direktori i integruar për main + asi-saas-frontend
 * Portet: 3000 (Main) | 3111 (ASI SaaS)
 */

const path = require('path');
const { spawn } = require('child_process');

console.log('🚀 Ultra Platform Unified Starting...');
console.log('📁 Working Directory:', __dirname);

// Define paths
const mainDir = __dirname;
const frontendDir = path.join(__dirname, 'asi-saas-frontend');

console.log(`🔹 Main App Directory: ${mainDir}`);
console.log(`🔹 Frontend Directory: ${frontendDir}`);

// Process storage
const processes = [];

// Cleanup function
function cleanup() {
    console.log('\n🧹 Stopping all processes...');
    processes.forEach((proc, index) => {
        if (proc && !proc.killed) {
            console.log(`   Stopping process ${index + 1}...`);
            proc.kill('SIGTERM');
        }
    });
    process.exit(0);
}

// Handle termination signals
process.on('SIGINT', cleanup);
process.on('SIGTERM', cleanup);

// Start Main App (Port 3000)
console.log('\n🔥 Starting Main App on port 3000...');
const mainProcess = spawn('yarn', ['dev'], {
    cwd: mainDir,
    stdio: 'inherit',
    shell: true
});

mainProcess.on('error', (err) => {
    console.error('❌ Main App Error:', err);
});

processes.push(mainProcess);

// Start ASI SaaS Frontend (Port 3111)
console.log('🎨 Starting ASI SaaS Frontend on port 3111...');
const frontendProcess = spawn('yarn', ['dev', '-p', '3111'], {
    cwd: frontendDir,
    stdio: 'inherit',
    shell: true
});

frontendProcess.on('error', (err) => {
    console.error('❌ Frontend App Error:', err);
});

processes.push(frontendProcess);

console.log('\n🎉 Ultra Platform Unified Launched!');
console.log('📋 Access Points:');
console.log('   🔹 Main App: http://localhost:3000');
console.log('   🔹 ASI SaaS: http://localhost:3111');
console.log('\n💡 Press Ctrl+C to stop all services');
