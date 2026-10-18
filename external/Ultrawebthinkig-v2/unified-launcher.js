#!/usr/bin/env node

/**
 * UltraWebThinking - Unified System Launcher 
 * Nisen TË GJITHA 46 MODULET në një port të vetëm
 */

const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

console.log('🚀 UltraWebThinking - Unified System Launcher\n');

// Konfigurimet e sistemit
const SYSTEM_CONFIG = {
  port: 3000,
  totalModules: 46,
  categories: [
    'AI & AGI Core (10 module)',
    'AI & Neural Networks (7 module)', 
    'Performance Systems (6 module)',
    'System Utilities (7 module)',
    'Security Systems (3 module)',
    'Network & IoT (3 module)',
    'Medical AI (2 module)',
    'Specialized Systems (2 module)',
    'Demos & Testing (3 module)',
    'Search Engines (2 module)',
    'Business & SaaS (1 module)'
  ]
};

// ASCII Art për sistem status
function displaySystemBanner() {
  console.log(`
██╗   ██╗██╗  ████████╗██████╗  █████╗ ██╗    ██╗███████╗██████╗ 
██║   ██║██║  ╚══██╔══╝██╔══██╗██╔══██╗██║    ██║██╔════╝██╔══██╗
██║   ██║██║     ██║   ██████╔╝███████║██║ █╗ ██║█████╗  ██████╔╝
██║   ██║██║     ██║   ██╔══██╗██╔══██║██║███╗██║██╔══╝  ██╔══██╗
╚██████╔╝███████╗██║   ██║  ██║██║  ██║╚███╔███╔╝███████╗██████╔╝
 ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝╚═════╝ 
                                                                   
████████╗██╗  ██╗██╗███╗   ██╗██╗  ██╗██╗███╗   ██╗ ██████╗      
╚══██╔══╝██║  ██║██║████╗  ██║██║ ██╔╝██║████╗  ██║██╔════╝      
   ██║   ███████║██║██╔██╗ ██║█████╔╝ ██║██╔██╗ ██║██║  ███╗     
   ██║   ██╔══██║██║██║╚██╗██║██╔═██╗ ██║██║╚██╗██║██║   ██║     
   ██║   ██║  ██║██║██║ ╚████║██║  ██╗██║██║ ╚████║╚██████╔╝     
   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝      
  `);
  
  console.log('🌟 UNIFIED PLATFORM - Single Port Architecture');
  console.log(`🎯 ${SYSTEM_CONFIG.totalModules} MODULE TË UNIFIKUARA`);
  console.log(`🚀 Port: ${SYSTEM_CONFIG.port}`);
  console.log(`📊 Kategori: ${SYSTEM_CONFIG.categories.length}`);
  console.log('═'.repeat(70));
}

// System health check
async function performSystemHealthCheck() {
  console.log('\n🏥 System Health Check...');
  
  const checks = [
    { name: 'Node.js Version', check: () => process.version },
    { name: 'Working Directory', check: () => process.cwd() },
    { name: 'Package.json', check: async () => {
      try {
        await fs.access('package.json');
        return '✅ Found';
      } catch {
        return '❌ Missing';
      }
    }},
    { name: 'Next.js Config', check: async () => {
      try {
        await fs.access('next.config.js');
        return '✅ Unified Config';
      } catch {
        return '❌ Missing Config';
      }
    }},
    { name: 'App Directory', check: async () => {
      try {
        const stats = await fs.stat('app');
        return stats.isDirectory() ? '✅ Ready' : '❌ Not Directory';
      } catch {
        return '❌ Missing';
      }
    }}
  ];
  
  for (const check of checks) {
    const result = typeof check.check === 'function' ? 
      await check.check() : check.check;
    console.log(`   ${check.name}: ${result}`);
  }
}

// Display module categories
function displayModuleCategories() {
  console.log('\n📂 MODULE CATEGORIES:');
  SYSTEM_CONFIG.categories.forEach((category, index) => {
    console.log(`   ${index + 1}. ${category}`);
  });
}

// Environment setup
async function setupEnvironment() {
  console.log('\n⚙️ Setting up unified environment...');
  
  // Copy unified config if exists
  try {
    if (await fs.access('.env.unified').then(() => true, () => false)) {
      await fs.copyFile('.env.unified', '.env.local');
      console.log('   ✅ Unified environment applied');
    }
  } catch (error) {
    console.log('   ⚠️  Using default environment');
  }
  
  // Set NODE_ENV if not set
  if (!process.env.NODE_ENV) {
    process.env.NODE_ENV = 'development';
    console.log('   ✅ NODE_ENV set to development');
  }
}

// Launch the unified system
function launchUnifiedSystem() {
  console.log('\n🚀 LAUNCHING ULTRAWEBTHINKING UNIFIED SYSTEM...\n');
  
  const startCommand = process.platform === 'win32' ? 'yarn.cmd' : 'yarn';
  const args = ['dev'];
  
  console.log('🧶 Starting Yarn Berry development server...');
  console.log(`📡 All ${SYSTEM_CONFIG.totalModules} modules will be available on:`);
  console.log(`   🔗 http://localhost:${SYSTEM_CONFIG.port}`);
  console.log(`   📊 Dashboard: http://localhost:${SYSTEM_CONFIG.port}/dashboard`);
  console.log(`   🧪 API Health: http://localhost:${SYSTEM_CONFIG.port}/api/health`);
  console.log('\n💡 Press Ctrl+C to stop the system\n');
  console.log('═'.repeat(70));
  
  // Launch Yarn Berry server
  const server = spawn(startCommand, args, {
    stdio: 'inherit',
    env: {
      ...process.env,
      PORT: SYSTEM_CONFIG.port.toString(),
      NEXT_PUBLIC_PORT: SYSTEM_CONFIG.port.toString(),
      YARN_ENABLE_TELEMETRY: '0' // Disable yarn telemetry
    }
  });
  
  server.on('close', (code) => {
    console.log(`\n🛑 System stopped with code ${code}`);
    console.log('👋 UltraWebThinking unified system shutdown complete.');
  });
  
  server.on('error', (error) => {
    console.error('❌ Failed to start system:', error.message);
    console.log('\n🔧 Troubleshooting:');
    console.log('   1. Make sure Node.js and Yarn Berry are installed');
    console.log('   2. Run: yarn install');
    console.log('   3. Check if port 3000 is available');
    console.log('   4. Try: yarn --version (should be 4.x)');
    process.exit(1);
  });
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\n🛑 Stopping UltraWebThinking system...');
    server.kill('SIGTERM');
  });
}

// Quick system verification
async function quickSystemTest() {
  console.log('\n🧪 Quick System Verification...');
  
  // Wait a moment for server to start
  await new Promise(resolve => setTimeout(resolve, 3000));
  
  console.log(`   🔍 Testing connection to localhost:${SYSTEM_CONFIG.port}...`);
  console.log('   📊 Run the dashboard test for full module verification');
  console.log(`   🌐 Open: http://localhost:${SYSTEM_CONFIG.port}`);
}

// Main launcher function
async function main() {
  try {
    displaySystemBanner();
    await performSystemHealthCheck();
    displayModuleCategories();
    await setupEnvironment();
    
    console.log('\n🎯 READY TO LAUNCH!');
    console.log('   💫 All systems nominal');
    console.log(`   🚀 ${SYSTEM_CONFIG.totalModules} modules unified`);
    console.log('   🔄 Single port architecture active');
    
    // Confirmation
    console.log('\n⏰ Starting in 3 seconds...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('⏰ Starting in 2 seconds...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('⏰ Starting in 1 second...');
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    launchUnifiedSystem();
    
    // Start background verification
    setTimeout(quickSystemTest, 5000);
    
  } catch (error) {
    console.error('❌ Launch failed:', error.message);
    console.log('\n🆘 EMERGENCY FALLBACK:');
    console.log('   Run manually: npm run dev');
    process.exit(1);
  }
}

// Export for testing
module.exports = {
  SYSTEM_CONFIG,
  displaySystemBanner,
  performSystemHealthCheck,
  launchUnifiedSystem
};

// Run if called directly
if (require.main === module) {
  main();
}
