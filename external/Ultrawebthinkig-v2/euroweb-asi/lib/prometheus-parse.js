// Parser i shpejtë për Prometheus text exposition; kthen { metricName: number, ... }
export function parsePromText(text){
  const out = {};
  const lines = text.split(/\r?\n/);
  for (const line of lines){
    if (!line || line.startsWith('#')) continue;
    // shembull: euroweb_process_uptime_seconds 4.3880852
    const sp = line.trim().split(/\s+/);
    const nameAndLabels = sp[0]; const val = parseFloat(sp[1]);
    if (Number.isFinite(val)) {
      // heq labels nëse ka { … }
      const name = nameAndLabels.includes('{')
        ? nameAndLabels.slice(0, nameAndLabels.indexOf('{'))
        : nameAndLabels;
      out[name] = val;
    }
  }
  return out;
}
