import fs from 'fs';
import { parsePromText } from '../../lib/prometheus-parse.js';
import { log } from '../../lib/log.js';
import { RingBuffer } from '../../lib/ringbuffer.js';

const MEMORY_FILE = process.env.MEMORY_FILE || './agi/memory.jsonl';
const MAX = parseInt(process.env.MAX_INMEM_SAMPLES||'2048',10);
export const ring = new RingBuffer(MAX);

async function fetchText(url, ms=2500){
  const ctrl = new AbortController();
  const t = setTimeout(()=>ctrl.abort(), ms);
  try{
    const r = await fetch(url, {signal: ctrl.signal, headers:{accept:'text/plain'}});
    if(!r.ok) throw new Error(`HTTP ${r.status}`);
    return await r.text();
  } finally { clearTimeout(t); }
}

export async function collectBits(){
  const src = process.env.PROM_SOURCE;
  if(!src) throw new Error('PROM_SOURCE not set');
  const text = await fetchText(src);
  const metrics = parsePromText(text);

  const sample = {
    t: Date.now(),
    cpu_user: metrics.euroweb_process_cpu_user_seconds_total ?? null,
    cpu_sys: metrics.euroweb_process_cpu_system_seconds_total ?? null,
    cpu: metrics.euroweb_cpu_load_1 ?? null,
    mem_used_bytes: metrics.euroweb_memory_used_bytes ?? null,
    rss_bytes: metrics.euroweb_process_resident_memory_bytes ?? null,
    evloop_p50: metrics.euroweb_nodejs_eventloop_lag_p50_seconds ?? null,
    evloop_p99: metrics.euroweb_nodejs_eventloop_lag_p99_seconds ?? null,
    uptime_s: metrics.euroweb_process_uptime_seconds ?? null,
  };

  // append-only disk
  fs.appendFileSync(MEMORY_FILE, JSON.stringify(sample) + '\n');
  // ring buffer in-mem
  ring.push(sample);

  log.debug('ALBA bits', sample);
  return sample;
}
