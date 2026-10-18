import { ring } from './alba.js';
import { mean, std, zscore, iqrAnomaly, EWMA } from '../../lib/stats.js';

const alpha = Number(process.env.EWMA_ALPHA || '0.2');
const ewCPU = new EWMA(alpha);
const ewMEM = new EWMA(alpha);

function series(field){
  const arr = ring.toArray().map(s => Number(s[field] ?? 0)).filter(Number.isFinite);
  return arr;
}

export function analyzeBits(){
  const cpu = series('cpu');
  const memB = series('mem_used_bytes');
  const rssB = series('rss_bytes');

  const cpuMean = mean(cpu), cpuStd = std(cpu);
  const cpuLast = cpu.length ? cpu[cpu.length-1] : 0;
  const cpuZ = zscore(cpuLast, cpuMean, cpuStd);
  const cpuIqr = iqrAnomaly(cpu);

  const memGB = memB.map(x => x/1e9);
  const memMean = mean(memGB), memStd = std(memGB);
  const memLast = memGB.length ? memGB[memGB.length-1] : 0;
  const memZ = zscore(memLast, memMean, memStd);
  const memIqr = iqrAnomaly(memGB);

  const cpuTrend = ewCPU.next(cpuLast);
  const memTrend = ewMEM.next(memLast);

  // klasifikim shkencor
  let state = 'optimal';
  if (Math.abs(cpuZ) >= (Number(process.env.CPU_Z_THRESHOLD)||3.0) || Math.abs(memZ) >= (Number(process.env.MEM_Z_THRESHOLD)||3.0)) {
    state = 'anomalous';
  } else if (cpuLast > cpuMean*1.5 || memLast > memMean*1.3) {
    state = 'high_load';
  }

  const insight = state==='optimal'
    ? 'Sistemi në ekuilibër termodinamik (CPU/MEM brenda variacionit natyror).'
    : state==='high_load'
    ? 'Ngarkesë e lartë e qëndrueshme; rekomandohet rishpërndarje pune ose rënie frekuence polling.'
    : 'Anomali e detektuar (z-score): hetim i menjëhershëm në shkallë mikro (stack traces / I/O).';

  return {
    state, insight,
    cpu: { last: cpuLast, mean: cpuMean, std: cpuStd, z: cpuZ, iqr: cpuIqr, ewma: cpuTrend },
    memGB: { last: memLast, mean: memMean, std: memStd, z: memZ, iqr: memIqr, ewma: memTrend },
    rssGB: rssB.length ? rssB[rssB.length-1]/1e9 : 0
  };
}
