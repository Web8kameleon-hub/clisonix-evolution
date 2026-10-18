#!/usr/bin/env node

/**
 * UltraWebThinking - Module Discovery & Universal Dashboard Generator
 * Gjen TË GJITHA modulet dhe krijon dashboard-in e plotë
 */

const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');

console.log('🔍 UltraWebThinking - Module Discovery Starting...\n');

// Gjej të gjitha modulet në /app directory
async function discoverAllModules() {
  const appDir = path.join(process.cwd(), 'app');
  
  try {
    const entries = await fs.readdir(appDir, { withFileTypes: true });
    const modules = entries
      .filter(entry => entry.isDirectory())
      .filter(entry => !entry.name.startsWith('.'))
      .filter(entry => !['api', 'components'].includes(entry.name))
      .map(entry => ({
        name: entry.name,
        path: `/${entry.name}`,
        category: categorizeModule(entry.name),
        displayName: formatDisplayName(entry.name)
      }));
    
    return modules;
  } catch (error) {
    console.error('❌ Error discovering modules:', error.message);
    return [];
  }
}

// Kategorizoj modulet sipas emrit
function categorizeModule(name) {
  if (name.includes('agi') || name.includes('asi')) return 'AI & AGI Core';
  if (name.includes('neural') || name.includes('openmind')) return 'AI & Neural Networks';
  if (name.includes('med') || name.includes('bio') || name.includes('alba')) return 'Medical AI';
  if (name.includes('search')) return 'Search Engines';
  if (name.includes('security') || name.includes('guardian') || name.includes('cyber')) return 'Security Systems';
  if (name.includes('ultra') || name.includes('quantum') || name.includes('speed') || name.includes('latency')) return 'Performance Systems';
  if (name.includes('lora') || name.includes('iot') || name.includes('mesh') || name.includes('bandwidth')) return 'Network & IoT';
  if (name.includes('saas') || name.includes('eco') || name.includes('dashboard')) return 'Business & SaaS';
  if (name.includes('demo')) return 'Demos & Testing';
  if (name.includes('aviation') || name.includes('weather') || name.includes('radio')) return 'Specialized Systems';
  return 'System Utilities';
}

// Format emrat për display
function formatDisplayName(name) {
  return name
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Krijon API endpoint për secilin modul
function generateAPIEndpoint(moduleName) {
  const category = categorizeModule(moduleName);
  
  if (category === 'AI & AGI Core') return `/api/agi/${moduleName.replace(/^agi-?/, '')}`;
  if (category === 'AI & Neural Networks') return `/api/neural/${moduleName.replace(/^neural-?/, '')}`;
  if (category === 'Medical AI') return `/api/medical/${moduleName.replace(/^(agimed|alba|bio).*/, '$1')}`;
  if (category === 'Search Engines') return `/api/search/${moduleName.replace(/-search.*/, '')}`;
  if (category === 'Security Systems') return `/api/security/${moduleName.replace(/^(guardian|cyber|advanced).*/, '$1')}`;
  if (category === 'Performance Systems') return `/api/performance/${moduleName}`;
  if (category === 'Network & IoT') return `/api/network/${moduleName}`;
  if (category === 'Business & SaaS') return `/api/saas/${moduleName}`;
  if (category === 'Specialized Systems') return `/api/specialized/${moduleName}`;
  return `/api/utilities/${moduleName}`;
}

// Generate unified Next.js routing configuration
function generateUnifiedRouting(modules) {
  const routingRules = modules.map(module => {
    const endpoint = generateAPIEndpoint(module.name);
    return `      { source: '${module.path}:path*', destination: '${endpoint}:path*' },`;
  });
  
  return `
  // ========== UNIFIED ROUTING - AUTO-GENERATED ==========
  async rewrites() {
    return [
${routingRules.join('\n')}
    ];
  },`;
}

// Generate HTML dashboard
function generateHTMLDashboard(modules) {
  const modulesByCategory = modules.reduce((acc, module) => {
    if (!acc[module.category]) acc[module.category] = [];
    acc[module.category].push(module);
    return acc;
  }, {});

  const categoryHTML = Object.entries(modulesByCategory)
    .map(([category, categoryModules]) => `
        <div class="category">
          <h2>🔥 ${category} (${categoryModules.length} module)</h2>
          <div class="modules">
            ${categoryModules.map(module => `
              <div class="module-card" onclick="testModule('${module.name}', '${module.path}')">
                <h3>${module.displayName}</h3>
                <p>Endpoint: ${generateAPIEndpoint(module.name)}</p>
                <p>Path: ${module.path}</p>
                <div class="status" id="status-${module.name}">⏳ Ready</div>
              </div>
            `).join('')}
          </div>
        </div>
    `).join('');

  return `<!DOCTYPE html>
<html lang="sq">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 UltraWebThinking - TË GJITHA MODULET</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        .stats {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }
        .stat {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            text-align: center;
        }
        .stat h3 { font-size: 2rem; }
        .category {
            margin-bottom: 40px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }
        .category h2 {
            color: #ffd700;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }
        .modules {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .module-card {
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .module-card:hover {
            background: rgba(255,255,255,0.2);
            border-color: #ffd700;
            transform: translateY(-5px);
        }
        .module-card h3 {
            color: #ffd700;
            margin-bottom: 10px;
            font-size: 1.2rem;
        }
        .module-card p {
            margin-bottom: 8px;
            opacity: 0.8;
            font-size: 0.9rem;
        }
        .status {
            padding: 8px 15px;
            border-radius: 25px;
            font-weight: bold;
            text-align: center;
            margin-top: 10px;
        }
        .status.ready { background: #4CAF50; }
        .status.testing { background: #FF9800; }
        .status.success { background: #2196F3; }
        .status.error { background: #F44336; }
        .controls {
            position: fixed;
            bottom: 20px;
            right: 20px;
        }
        .btn {
            background: #ffd700;
            color: #333;
            border: none;
            padding: 15px 25px;
            border-radius: 50px;
            font-weight: bold;
            cursor: pointer;
            margin-left: 10px;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background: #ffed4e;
            transform: scale(1.05);
        }
        .log {
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 400px;
            max-height: 300px;
            background: rgba(0,0,0,0.8);
            border-radius: 15px;
            padding: 15px;
            overflow-y: auto;
            display: none;
        }
        .log-entry {
            margin-bottom: 5px;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 UltraWebThinking Platform</h1>
        <p>TË GJITHA MODULET - Arkitekturë e unifikuar me një port të vetëm</p>
    </div>

    <div class="stats">
        <div class="stat">
            <h3>${modules.length}</h3>
            <p>Totali Moduleve</p>
        </div>
        <div class="stat">
            <h3>${Object.keys(modulesByCategory).length}</h3>
            <p>Kategori</p>
        </div>
        <div class="stat">
            <h3>1</h3>
            <p>Port (3000)</p>
        </div>
        <div class="stat">
            <h3 id="active-count">0</h3>
            <p>Aktive</p>
        </div>
    </div>

    ${categoryHTML}

    <div class="controls">
        <button class="btn" onclick="testAllModules()">🧪 Test TË GJITHA</button>
        <button class="btn" onclick="toggleLog()">📊 Log</button>
        <button class="btn" onclick="startUnifiedSystem()">🚀 Nis Sistemin</button>
    </div>

    <div class="log" id="log"></div>

    <script>
        let activeModules = 0;

        async function testModule(name, path) {
            const statusEl = document.getElementById('status-' + name);
            statusEl.textContent = '🔄 Testing...';
            statusEl.className = 'status testing';
            
            log('🧪 Testing: ' + name);
            
            try {
                const response = await fetch(path);
                if (response.ok) {
                    statusEl.textContent = '✅ Active';
                    statusEl.className = 'status success';
                    activeModules++;
                    log('✅ ' + name + ': SUCCESS');
                } else {
                    statusEl.textContent = '⚠️ Error';
                    statusEl.className = 'status error';
                    log('⚠️ ' + name + ': HTTP ' + response.status);
                }
            } catch (error) {
                statusEl.textContent = '❌ Offline';
                statusEl.className = 'status error';
                log('❌ ' + name + ': ' + error.message);
            }
            
            document.getElementById('active-count').textContent = activeModules;
        }

        async function testAllModules() {
            activeModules = 0;
            log('🚀 Testing all ${modules.length} modules...');
            
            const modules = [
                ${modules.map(m => `{ name: '${m.name}', path: '${m.path}' }`).join(',\n                ')}
            ];
            
            for (const module of modules) {
                await testModule(module.name, module.path);
                await new Promise(resolve => setTimeout(resolve, 100));
            }
            
            log(\`🎯 Completed! \${activeModules}/\${modules.length} active modules\`);
        }

        function startUnifiedSystem() {
            log('🚀 Starting UltraWebThinking unified system...');
            log('🌐 All modules available on: http://localhost:3000');
            alert('🚀 Sistema po niset...\\n\\nTë gjitha modulet do të jenë të disponueshme në:\\nhttp://localhost:3000');
        }

        function log(message) {
            const logEl = document.getElementById('log');
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = \`[\${new Date().toLocaleTimeString()}] \${message}\`;
            logEl.appendChild(entry);
            logEl.scrollTop = logEl.scrollHeight;
        }

        function toggleLog() {
            const logEl = document.getElementById('log');
            logEl.style.display = logEl.style.display === 'none' ? 'block' : 'none';
        }

        // Initialize
        log('📊 UltraWebThinking Dashboard loaded');
        log('📈 Found ${modules.length} modules in ${Object.keys(modulesByCategory).length} categories');
    </script>
</body>
</html>`;
}

// Main execution
async function main() {
  try {
    console.log('🔍 Discovering all UltraWebThinking modules...');
    const modules = await discoverAllModules();
    
    console.log(`✅ Found ${modules.length} modules in ${Object.keys(modules.reduce((acc, m) => ({ ...acc, [m.category]: true }), {})).length} categories:`);
    
    // Group and display by category
    const byCategory = modules.reduce((acc, module) => {
      if (!acc[module.category]) acc[module.category] = [];
      acc[module.category].push(module);
      return acc;
    }, {});
    
    Object.entries(byCategory).forEach(([category, categoryModules]) => {
      console.log(`\n🔥 ${category} (${categoryModules.length} modules):`);
      categoryModules.forEach(module => {
        console.log(`   ${module.displayName} → ${module.path} → ${generateAPIEndpoint(module.name)}`);
      });
    });
    
    // Generate unified dashboard
    console.log('\n📊 Generating unified dashboard...');
    const dashboardHTML = generateHTMLDashboard(modules);
    await fs.writeFile('ultrawebthinking-dashboard.html', dashboardHTML);
    console.log('✅ Dashboard created: ultrawebthinking-dashboard.html');
    
    // Generate routing configuration
    console.log('\n🔄 Generating unified routing...');
    const routingConfig = generateUnifiedRouting(modules);
    console.log('✅ Routing configuration generated');
    
    console.log(`\n🎯 SUMMARY:`);
    console.log(`📊 Total Modules: ${modules.length}`);
    console.log(`📂 Categories: ${Object.keys(byCategory).length}`);
    console.log(`🌐 Unified Port: 3000`);
    console.log(`📄 Dashboard: ultrawebthinking-dashboard.html`);
    console.log(`\n🚀 Open dashboard në browser për të testuar modulet!`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { discoverAllModules, generateUnifiedRouting, generateHTMLDashboard };
