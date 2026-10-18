import { log } from '../lib/log.js';

export class Monitor {
  constructor(){ this.state = 'idle'; this.last = 0; }
  transition(next, why=''){
    log.info(`MONITOR ${this.state} -> ${next} ${why?`• ${why}`:''}`);
    this.state = next; this.last = Date.now();
  }
}
