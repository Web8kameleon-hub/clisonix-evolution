#!/usr/bin/env node

/**
 * UltraWebThinking - Yarn Berry Verification & Setup
 * Verifikoi dhe konfiguron Yarn Berry për platformën
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧶 UltraWebThinking - Yarn Berry Setup & Verification\n');

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m'
};

// Check functions
const checks = {
  // Check if Yarn is installed
  yarnInstalled() {
    try {
      const version = execSync('yarn --version', { encoding: 'utf8' }).trim();
      return { success: true, version };
    } catch (error) {
      return { success: false, error: 'Yarn not installed' };
    }
  },

  // Check Yarn version (should be Berry/4.x)
  yarnVersion() {
    try {
      const version = execSync('yarn --version', { encoding: 'utf8' }).trim();
      const isBerry = version.startsWith('4.') || version.startsWith('3.');
      return { 
        success: isBerry, 
        version,
        message: isBerry ? 'Yarn Berry detected' : 'Classic Yarn detected (should upgrade to Berry)'
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },

  // Check package.json packageManager field
  packageManager() {
    try {
      const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      const hasPackageManager = packageJson.packageManager && packageJson.packageManager.includes('yarn');
      return {
        success: hasPackageManager,
        packageManager: packageJson.packageManager || 'Not specified',
        message: hasPackageManager ? 'PackageManager field configured' : 'PackageManager field missing'
      };
    } catch (error) {
      return { success: false, error: 'Could not read package.json' };
    }
  },

  // Check for .yarnrc.yml
  yarnrcConfig() {
    const yarnrcPath = '.yarnrc.yml';
    const exists = fs.existsSync(yarnrcPath);
    let config = {};
    
    if (exists) {
      try {
        // Simple YAML parsing for basic config
        const content = fs.readFileSync(yarnrcPath, 'utf8');
        config.content = content;
      } catch (error) {
        return { success: false, error: 'Could not read .yarnrc.yml' };
      }
    }
    
    return {
      success: exists,
      config,
      message: exists ? '.yarnrc.yml configuration found' : '.yarnrc.yml not found'
    };
  },

  // Check workspace configuration
  workspaceConfig() {
    try {
      const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      const hasWorkspaces = Array.isArray(packageJson.workspaces) && packageJson.workspaces.length > 0;
      return {
        success: hasWorkspaces,
        workspaces: packageJson.workspaces || [],
        message: hasWorkspaces ? `${packageJson.workspaces.length} workspaces configured` : 'No workspaces configured'
      };
    } catch (error) {
      return { success: false, error: 'Could not read workspace config' };
    }
  },

  // Check if node_modules exists and has .yarn structure
  nodeModulesStructure() {
    const nodeModulesExists = fs.existsSync('node_modules');
    const yarnCacheExists = fs.existsSync('.yarn/cache');
    const pnpExists = fs.existsSync('.pnp.cjs') || fs.existsSync('.pnp.js');
    
    return {
      success: nodeModulesExists || pnpExists,
      nodeModules: nodeModulesExists,
      yarnCache: yarnCacheExists,
      pnp: pnpExists,
      message: pnpExists ? 'PnP mode detected' : nodeModulesExists ? 'Node modules mode' : 'Dependencies not installed'
    };
  }
};

// Display check result
function displayResult(name, result) {
  const icon = result.success ? `${colors.green}✅` : `${colors.red}❌`;
  console.log(`${icon} ${colors.bold}${name}${colors.reset}`);
  
  if (result.success) {
    if (result.version) console.log(`   Version: ${colors.cyan}${result.version}${colors.reset}`);
    if (result.message) console.log(`   ${colors.green}${result.message}${colors.reset}`);
    if (result.workspaces) console.log(`   Workspaces: ${colors.blue}${result.workspaces.join(', ')}${colors.reset}`);
    if (result.packageManager) console.log(`   Package Manager: ${colors.cyan}${result.packageManager}${colors.reset}`);
  } else {
    console.log(`   ${colors.red}${result.error || result.message}${colors.reset}`);
  }
  console.log();
}

// Setup recommendations
function displayRecommendations(results) {
  console.log(`${colors.bold}${colors.yellow}🔧 RECOMMENDATIONS:${colors.reset}\n`);
  
  if (!results.yarnInstalled.success) {
    console.log(`${colors.red}1. Install Yarn Berry:${colors.reset}`);
    console.log('   npm install -g yarn');
    console.log('   yarn set version berry\n');
  }
  
  if (!results.yarnVersion.success || !results.yarnVersion.version.startsWith('4.')) {
    console.log(`${colors.yellow}2. Upgrade to Yarn Berry:${colors.reset}`);
    console.log('   yarn set version stable');
    console.log('   yarn set version berry\n');
  }
  
  if (!results.packageManager.success) {
    console.log(`${colors.yellow}3. Add packageManager to package.json:${colors.reset}`);
    console.log('   "packageManager": "yarn@4.10.3"\n');
  }
  
  if (!results.yarnrcConfig.success) {
    console.log(`${colors.yellow}4. Create .yarnrc.yml configuration:${colors.reset}`);
    console.log('   nodeLinker: node-modules');
    console.log('   enableGlobalCache: true\n');
  }
  
  if (!results.nodeModulesStructure.success) {
    console.log(`${colors.red}5. Install dependencies:${colors.reset}`);
    console.log('   yarn install\n');
  }
}

// Create optimal .yarnrc.yml
function createOptimalYarnrc() {
  const optimalConfig = `# UltraWebThinking - Yarn Berry Configuration
nodeLinker: node-modules
enableGlobalCache: true
enableTelemetry: false
enableScripts: true
compressionLevel: mixed

# Performance optimizations
pnpMode: loose
nmHoistingLimits: workspaces

# Development settings
preferAggregateCacheInfo: true
supportedArchitectures:
  os: [win32, darwin, linux]
  cpu: [x64, arm64]
`;
  
  try {
    fs.writeFileSync('.yarnrc.yml', optimalConfig);
    console.log(`${colors.green}✅ Created optimal .yarnrc.yml configuration${colors.reset}`);
    return true;
  } catch (error) {
    console.log(`${colors.red}❌ Failed to create .yarnrc.yml: ${error.message}${colors.reset}`);
    return false;
  }
}

// Install dependencies with Yarn Berry
function installDependencies() {
  console.log(`${colors.blue}📦 Installing dependencies with Yarn Berry...${colors.reset}`);
  
  try {
    execSync('yarn install', { stdio: 'inherit' });
    console.log(`${colors.green}✅ Dependencies installed successfully${colors.reset}`);
    return true;
  } catch (error) {
    console.log(`${colors.red}❌ Failed to install dependencies: ${error.message}${colors.reset}`);
    return false;
  }
}

// Main verification function
async function main() {
  console.log(`${colors.bold}${colors.cyan}🔍 YARN BERRY SYSTEM VERIFICATION${colors.reset}\n`);
  
  // Run all checks
  const results = {};
  for (const [name, checkFn] of Object.entries(checks)) {
    results[name] = checkFn();
    displayResult(name.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()), results[name]);
  }
  
  // Calculate overall health
  const totalChecks = Object.keys(results).length;
  const passedChecks = Object.values(results).filter(r => r.success).length;
  const healthScore = (passedChecks / totalChecks) * 100;
  
  console.log(`${colors.bold}📊 SYSTEM HEALTH: ${healthScore >= 80 ? colors.green : healthScore >= 60 ? colors.yellow : colors.red}${healthScore.toFixed(1)}%${colors.reset} (${passedChecks}/${totalChecks} checks passed)\n`);
  
  // Show recommendations if needed
  if (healthScore < 100) {
    displayRecommendations(results);
  }
  
  // Auto-fix options
  if (healthScore < 80) {
    console.log(`${colors.bold}${colors.magenta}🛠️  AUTO-FIX OPTIONS:${colors.reset}\n`);
    
    if (!results.yarnrcConfig.success) {
      console.log('Creating optimal .yarnrc.yml configuration...');
      createOptimalYarnrc();
      console.log();
    }
    
    if (!results.nodeModulesStructure.success) {
      console.log('Installing dependencies...');
      installDependencies();
      console.log();
    }
  }
  
  // Final status
  if (healthScore >= 90) {
    console.log(`${colors.bold}${colors.green}🚀 YARN BERRY SETUP EXCELLENT!${colors.reset}`);
    console.log(`${colors.green}Ready to launch UltraWebThinking platform${colors.reset}\n`);
    console.log(`${colors.cyan}Next steps:${colors.reset}`);
    console.log('   yarn dev      # Start development server');
    console.log('   node unified-launcher.js   # Launch unified system');
  } else {
    console.log(`${colors.bold}${colors.yellow}⚠️  SETUP NEEDS ATTENTION${colors.reset}`);
    console.log(`${colors.yellow}Please address the recommendations above${colors.reset}`);
  }
}

// Export for testing
module.exports = {
  checks,
  createOptimalYarnrc,
  installDependencies
};

// Run if called directly
if (require.main === module) {
  main();
}
