#!/usr/bin/env node

/**
 * UltraWebThinking - Quick Unification Script
 * Applies unified configuration and starts the system
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

console.log('🚀 UltraWebThinking - Quick Unification Starting...\n');

// Step 1: Apply unified environment
console.log('📝 Step 1: Applying unified environment configuration...');
try {
  if (fs.existsSync('.env.unified')) {
    fs.copyFileSync('.env.unified', '.env.local');
    console.log('✅ Environment configuration applied');
  }
} catch (error) {
  console.log('⚠️  Environment config not found, using defaults');
}

// Step 2: Verify Next.js config
console.log('📝 Step 2: Verifying Next.js unified configuration...');
try {
  const nextConfigExists = fs.existsSync('next.config.js');
  if (nextConfigExists) {
    const configContent = fs.readFileSync('next.config.js', 'utf8');
    if (configContent.includes('UNIFIED ROUTING CONFIGURATION')) {
      console.log('✅ Unified routing configuration detected');
    } else {
      console.log('⚠️  Next.js config may need updating for full unification');
    }
  }
} catch (error) {
  console.log('⚠️  Could not verify Next.js configuration');
}

// Step 3: Install dependencies if needed
console.log('📝 Step 3: Checking dependencies...');
try {
  if (!fs.existsSync('node_modules') || !fs.existsSync('yarn.lock')) {
    console.log('📦 Installing dependencies with Yarn Berry...');
    execSync('yarn install', { stdio: 'inherit' });
    console.log('✅ Dependencies installed');
  } else {
    console.log('✅ Dependencies already installed');
  }
} catch (error) {
  console.log('⚠️  Could not install dependencies:', error.message);
}

// Step 4: Build for optimization (optional)
console.log('📝 Step 4: Preparing optimized build...');
try {
  console.log('🔨 Building UltraWebThinking platform...');
  execSync('yarn build', { stdio: 'inherit' });
  console.log('✅ Build completed successfully');
} catch (error) {
  console.log('⚠️  Build step skipped (will run in development mode)');
}

// Step 5: Start the unified system
console.log('\n🎯 Step 5: Starting UltraWebThinking unified system...');
console.log('🌐 All 40+ modules will be available on: http://localhost:3000');
console.log('📊 Dashboard: http://localhost:3000');
console.log('🔧 API Gateway: http://localhost:3000/api');
console.log('\n🚀 Starting server...\n');

try {
  execSync('yarn dev', { stdio: 'inherit' });
} catch (error) {
  console.log('❌ Could not start server:', error.message);
  console.log('\n🔧 Manual start: yarn dev');
}
