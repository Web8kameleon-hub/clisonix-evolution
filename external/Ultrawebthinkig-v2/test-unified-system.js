#!/usr/bin/env node

/**
 * UltraWebThinking - Unified System Test Script
 * Tests all 40+ modules in the unified single-port architecture
 */

const http = require('http');
const https = require('https');
const { URL } = require('url');

// Configuration
const BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://ultrawebthinking.com' 
  : 'http://localhost:3000';

// TË GJITHA MODULET E UltraWebThinking - 50+ Module!
const MODULES = {
  // ========== AI & AGI CORE MODULES (11 module) ==========
  'AGI Core': '/agi',
  'AGI Demo': '/agi-demo',
  'AGI Search Demo': '/agi-search-demo',  
  'AGI Tunnel': '/agi-tunnel',
  'Neural Network': '/neural-demo',
  'Neural Dev': '/neural-dev',
  'Neural Acceleration': '/neural-acceleration',
  'OpenMind Chat': '/openmind-chat',
  'OpenMind Demo': '/openmind-demo',
  'OpenMind Enhanced': '/openmind-enhanced',
  'CVA Demo': '/cva-demo',
  
  // ========== ASI SYSTEM MODULES (3 module) ==========
  'ASI 12-Layer': '/asi-12layer',
  'ASI Dashboard': '/asi-dashboard',
  'ASI Ultimate': '/asi-ultimate',
  
  // ========== MEDICAL AI SUITE (3 module) ==========
  'AGIMed Professional': '/agimed-professional',
  'AlbaMed Demo': '/albamed-demo',
  'Bio Nature AI': '/agixbionature-demo',
  
  // ========== ECONOMICS & BUSINESS (3 module) ==========
  'AGIxEco Demo': '/agixeco-demo',
  'Ultra SaaS': '/ultra-saas',
  'SaaS Dashboard': '/saas-dashboard',
  
  // ========== SEARCH & DISCOVERY (3 module) ==========
  'Neural Search': '/neural-search-demo',
  'Real Search': '/real-search-demo',
  'Web Search': '/web-search-demo',
  
  // ========== PERFORMANCE & INFRASTRUCTURE (6 module) ==========
  'Ultra Industrial': '/ultra-industrial',
  'Light Speed IO': '/light-speed-io',
  'Zero Latency': '/zero-latency',
  'Quantum Processing': '/quantum-processing',
  'Ultra Speed': '/ultra-speed',
  'Time Compression': '/time-compression',
  
  // ========== SECURITY & GUARDIAN (3 module) ==========
  'Guardian Demo': '/guardian-demo',
  'Advanced Security': '/advanced-security',
  'Cyber Security': '/cyber-security',
  
  // ========== NETWORK & COMMUNICATION (3 module) ==========
  'LoRa Mesh': '/lora-mesh',
  'IoT Manager': '/iot-manager',
  'Infinite Bandwidth': '/infinite-bandwidth',
  
  // ========== SPECIALIZED APPLICATIONS (6 module) ==========
  'Aviation Weather': '/aviation-weather',
  'Radio Propaganda': '/radio-propaganda',
  'Albion UTT': '/albion-utt',
  'UTT Tools': '/utt-tools',
  'Fluid Demo': '/fluid-demo',
  'Lazy Demo': '/lazy-demo',
  
  // ========== SYSTEM UTILITIES (4 module) ==========
  'Browser': '/browser',
  'Overview': '/overview',
  'API Gateway': '/api-gateway',
  'Revolution': '/revolution',
  
  // ========== LEGACY COMPATIBILITY (3 module) ==========
  'Gateway (Legacy)': '/gateway',
  'Producer (Legacy)': '/producer',
  'Base JSON': '/base.json',
};

// Color codes for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bold: '\x1b[1m'
};

/**
 * Make HTTP request to test a module
 */
function testModule(name, path) {
  return new Promise((resolve) => {
    const url = new URL(path, BASE_URL);
    const client = url.protocol === 'https:' ? https : http;
    
    const startTime = Date.now();
    
    const req = client.get(url, (res) => {
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      resolve({
        name,
        path,
        status: res.statusCode,
        responseTime,
        success: res.statusCode >= 200 && res.statusCode < 400
      });
    });
    
    req.on('error', (err) => {
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      
      resolve({
        name,
        path,
        status: 'ERROR',
        responseTime,
        success: false,
        error: err.message
      });
    });
    
    req.setTimeout(10000, () => {
      req.destroy();
      resolve({
        name,
        path,
        status: 'TIMEOUT',
        responseTime: 10000,
        success: false,
        error: 'Request timeout'
      });
    });
  });
}

/**
 * Run tests for all modules
 */
async function runTests() {
  console.log(`${colors.bold}${colors.cyan}🚀 UltraWebThinking - Unified System Test${colors.reset}`);
  console.log(`${colors.blue}Testing ${Object.keys(MODULES).length} modules on ${BASE_URL}${colors.reset}\n`);
  
  const results = [];
  let successCount = 0;
  let failureCount = 0;
  
  // Test all modules concurrently (but limit concurrency)
  const batchSize = 5;
  const moduleEntries = Object.entries(MODULES);
  
  for (let i = 0; i < moduleEntries.length; i += batchSize) {
    const batch = moduleEntries.slice(i, i + batchSize);
    const batchPromises = batch.map(([name, path]) => testModule(name, path));
    
    const batchResults = await Promise.all(batchPromises);
    results.push(...batchResults);
    
    // Display results for this batch
    batchResults.forEach(result => {
      const statusColor = result.success ? colors.green : colors.red;
      const statusSymbol = result.success ? '✅' : '❌';
      
      console.log(
        `${statusSymbol} ${colors.bold}${result.name}${colors.reset} ` +
        `${statusColor}(${result.status})${colors.reset} ` +
        `${colors.yellow}${result.responseTime}ms${colors.reset} ` +
        `${colors.cyan}${result.path}${colors.reset}`
      );
      
      if (result.error) {
        console.log(`   ${colors.red}Error: ${result.error}${colors.reset}`);
      }
      
      if (result.success) successCount++;
      else failureCount++;
    });
    
    console.log(); // Empty line between batches
  }
  
  // Summary
  console.log(`${colors.bold}${colors.cyan}📊 Test Summary${colors.reset}`);
  console.log(`${colors.green}✅ Successful: ${successCount}${colors.reset}`);
  console.log(`${colors.red}❌ Failed: ${failureCount}${colors.reset}`);
  console.log(`${colors.blue}📈 Success Rate: ${((successCount / results.length) * 100).toFixed(1)}%${colors.reset}`);
  
  const avgResponseTime = results.reduce((sum, r) => sum + r.responseTime, 0) / results.length;
  console.log(`${colors.yellow}⏱️  Average Response Time: ${avgResponseTime.toFixed(0)}ms${colors.reset}`);
  
  // Routing verification
  console.log(`\n${colors.bold}${colors.magenta}🔄 Unified Routing Status${colors.reset}`);
  if (failureCount === 0) {
    console.log(`${colors.green}🎉 All modules successfully unified on single port!${colors.reset}`);
    console.log(`${colors.green}🎯 No more port conflicts - routing works perfectly!${colors.reset}`);
  } else {
    console.log(`${colors.yellow}⚠️  Some modules need attention for complete unification${colors.reset}`);
  }
}

/**
 * Main execution
 */
if (require.main === module) {
  runTests().catch(err => {
    console.error(`${colors.red}❌ Test execution failed:${colors.reset}`, err);
    process.exit(1);
  });
}

module.exports = { runTests, testModule, MODULES };
