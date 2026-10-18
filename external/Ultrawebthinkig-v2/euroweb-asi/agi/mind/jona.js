export function policy(decisionInput){
  const { cpu, memGB } = decisionInput;
  const lagP99 = decisionInput.evloop_p99 || 0;

  const limits = {
    cpuZMax: Number(process.env.CPU_Z_THRESHOLD||'3.0'),
    memZMax: Number(process.env.MEM_Z_THRESHOLD||'3.0'),
    lagMax: 0.1 // 100ms
  };

  const actions = [];
  if (Math.abs(cpu.z) >= limits.cpuZMax) actions.push({type:'ALERT', what:'CPU_Z', reason:`z=${cpu.z.toFixed(2)} ≥ ${limits.cpuZMax}`});
  if (Math.abs(memGB.z) >= limits.memZMax) actions.push({type:'ALERT', what:'MEM_Z', reason:`z=${memGB.z.toFixed(2)} ≥ ${limits.memZMax}`});
  if (lagP99 > limits.lagMax) actions.push({type:'THROTTLE', what:'POLLING', reason:`eventLoop p99=${lagP99}s > ${limits.lagMax}s`});

  // rekomandime të buta
  if (cpu.last > cpu.ewma*1.2) actions.push({type:'ADVISE', what:'REDISTRIBUTE_LOAD', reason:'CPU > 120% e trendit'});
  if (memGB.last > memGB.ewma*1.15) actions.push({type:'ADVISE', what:'CACHE_TRIM', reason:'MEM mbi trend'});

  const ethics = actions.length ? 'protect_system_integrity' : 'proceed_normal';
  return { ethics, limits, actions };
}
