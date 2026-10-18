const $ = sel => document.querySelector(sel);

const endpoints = {
  revolution: '/api/revolution',
  web8: '/api/web8',
  security: '/api/security',
  iot: '/api/iot',
  api: '/api/api-gateway',
  agi: '/api/agi',
  mesh: '/api/mesh',
  industrial: '/api/ultra-industrial'
};

async function load(id, url) {
  const out = $(`#${id}-json`);
  if (!out) return;
  try {
    const res = await fetch(url, { cache: 'no-store' });
    const text = await res.text();
    try {
      const json = JSON.parse(text);
      out.textContent = JSON.stringify(json, null, 2);
      out.classList.remove('error');
      
      // Add analysis comments
      if (id === 'mesh' && json.signalStrength && json.energyLevel) {
        const eff = (Number(json.signalStrength) * Number(json.energyLevel) / 100).toFixed(1);
        const hintEl = document.querySelector('#mesh .hint');
        if (hintEl) {
          hintEl.textContent = `⚡ Efikasiteti energjetik: ${eff}% — ${json.quality || ''}`;
        }
      }
      
      if (id === 'revolution' && json.Revolution?.Leistung?.memory) {
        const m = json.Revolution.Leistung.memory;
        const used = (m.used_bytes / 1e9).toFixed(1);
        const total = (m.total_bytes / 1e9).toFixed(1);
        const pct = ((m.used_bytes / m.total_bytes) * 100).toFixed(0);
        
        // Remove existing hint
        const existingHint = document.querySelector('#revolution .hint');
        if (existingHint) existingHint.remove();
        
        // Add new hint
        const hint = document.createElement('div');
        hint.className = 'hint';
        hint.textContent = `📊 RAM: ${used}GB / ${total}GB (${pct}%). ${pct > 85 ? '⚠️ Nën presion — mendou për ulje frekuence polling ose lirime cache.' : 'OK.'}`;
        document.querySelector('#revolution').insertBefore(hint, document.querySelector('#rev-json'));
      }
      
    } catch {
      out.textContent = text;
    }
  } catch (e) {
    out.textContent = String(e);
    out.classList.add('error');
  }
}

// Special handler for Ultra Industrial with satellite support
async function loadIndustrial(type = 'default') {
  const url = type === 'satellite' ? '/api/ultra-industrial?type=satellite' : '/api/ultra-industrial';
  await load('industrial', url);
}

function cycle() {
  load('revolution', endpoints.revolution);
  load('web8', endpoints.web8);
  load('security', endpoints.security);
  load('iot', endpoints.iot);
  load('api', endpoints.api);
  load('agi', endpoints.agi);
  load('mesh', endpoints.mesh);
  loadIndustrial('default'); // Load default industrial data
}

// UI nav scroll
document.querySelectorAll('.nav button').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const id = btn.dataset.section;
    const sec = document.getElementById(id);
    if (sec) sec.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
});

// Make loadIndustrial globally available
window.loadIndustrial = loadIndustrial;

cycle();
setInterval(cycle, 4000);
