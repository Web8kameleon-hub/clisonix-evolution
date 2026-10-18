import { collectBits, ring } from './mind/alba.js';
import { analyzeBits } from './mind/albi.js';
import { policy } from './mind/jona.js';

export async function ASIcycle(){
  // 1) sensorika
  const bits = await collectBits();

  // 2) analiza shkencore
  const analysis = analyzeBits();

  // furnizo Jona me evloop p99 nga mostrat e fundit
  const last = ring.last(1)[0] || {};
  const decision = policy({ ...analysis, evloop_p99: Number(last.evloop_p99||0) });

  return {
    t: new Date().toISOString(),
    bits,
    analysis,
    decision
  };
}
