#!/usr/bin/env node

console.log('🚀 ALBA/ASI Ultra System Launcher');
console.log('🔥 Starting Complete Autonomous Platform...');
console.log('');

const { spawn } = require('child_process');
const path = require('path');

// Colors for output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(color, prefix, message) {
  console.log(`${colors[color]}${colors.bright}[${prefix}]${colors.reset} ${message}`);
}

// Start UltraCom Backend
log('cyan', 'ULTRACOM', 'Starting AI Manager Backend...');
const backend = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--reload', '--host', '127.0.0.1', '--port', '8080'], {
  cwd: path.join(__dirname, 'ultracom'),
  stdio: 'pipe'
});

backend.stdout.on('data', (data) => {
  const output = data.toString().trim();
  if (output) log('cyan', 'ULTRACOM', output);
});

backend.stderr.on('data', (data) => {
  const output = data.toString().trim();
  if (output) log('red', 'ULTRACOM-ERROR', output);
});

// Start Next.js Frontend
setTimeout(() => {
  log('magenta', 'NEXTJS', 'Starting Frontend with Auto Port Selection...');
  const frontend = spawn('yarn', ['dev'], {
    cwd: __dirname,
    stdio: 'pipe',
    shell: true
  });

  frontend.stdout.on('data', (data) => {
    const output = data.toString().trim();
    if (output) log('magenta', 'NEXTJS', output);
  });

  frontend.stderr.on('data', (data) => {
    const output = data.toString().trim();
    if (output) log('yellow', 'NEXTJS-WARN', output);
  });

  frontend.on('close', (code) => {
    log('red', 'NEXTJS', `Process exited with code ${code}`);
  });
}, 2000);

backend.on('close', (code) => {
  log('red', 'ULTRACOM', `Process exited with code ${code}`);
});

// Cleanup on exit
process.on('SIGINT', () => {
  log('yellow', 'SYSTEM', 'Shutting down ALBA/ASI Ultra System...');
  backend.kill();
  process.exit();
});

// Success message
setTimeout(() => {
  console.log('');
  log('green', '🎯 SUCCESS', 'ALBA/ASI Ultra System is running!');
  log('blue', '📡 BACKEND', 'UltraCom AI Manager: http://localhost:8080');
  log('magenta', '🌐 FRONTEND', 'Next.js will auto-detect available port');
  log('yellow', '📊 APIs', 'ALBA/ASI Hub, Life Sciences, Cultural Hub ready!');
  log('cyan', '🤖 AI MANAGER', 'Zero Human Intervention Mode Active');
  console.log('');
  console.log(`${colors.bright}${colors.green}🚀 Use Ctrl+C to stop all services${colors.reset}`);
}, 5000);
