const levels = { error:0, warn:1, info:2, debug:3 };
const LVL = process.env.LOG_LEVEL || 'info';
const CUR = levels[LVL] ?? 2;
const ts = () => new Date().toISOString();

export const log = {
  error: (...a)=> { if(CUR>=0) console.error(`[${ts()}] [ERROR]`, ...a); },
  warn:  (...a)=> { if(CUR>=1) console.warn (`[${ts()}] [WARN ]`, ...a); },
  info:  (...a)=> { if(CUR>=2) console.log  (`[${ts()}] [INFO ]`, ...a); },
  debug: (...a)=> { if(CUR>=3) console.log  (`[${ts()}] [DEBUG]`, ...a); },
};
