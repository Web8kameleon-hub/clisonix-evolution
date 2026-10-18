import { sendAlert } from "./alertSystem"; // Për të dërguar alarme në rast të kërcënimeve
import { logToDistributedSystem } from "./distributedLogger"; // Për ruajtje hibride të logjeve

type IPLog = {
  [ip: string]: {
    count: number;
    lastAccess: number;
    threatLevel: number; // Shtohet për të monitoruar nivelin e kërcënimit
  };
};

const ipLog: IPLog = {};

// Funksioni kryesor i firewall-it
export function firewall(ip: string): boolean {
  const now = Date.now();

  if (!ipLog[ip]) {
    ipLog[ip] = { count: 1, lastAccess: now, threatLevel: 0 };
    return false;
  }

  const diff = now - ipLog[ip].lastAccess;
  ipLog[ip].lastAccess = now;

  // Përditëso numrin e kërkesave dhe nivelin e kërcënimit
  if (diff < 2000) {
    ipLog[ip].count++;
    ipLog[ip].threatLevel += 1; // Rrit nivelin e kërcënimit për sjellje të dyshimtë
  } else {
    ipLog[ip].count = 1;
    ipLog[ip].threatLevel = Math.max(0, ipLog[ip].threatLevel - 1); // Ul nivelin e kërcënimit nëse sjellja normalizohet
  }

  // Kontrollo nëse IP duhet të bllokohet
  if (ipLog[ip].count > 5 || ipLog[ip].threatLevel > 10) {
    console.warn(`🚨 FIREWALL: IP ${ip} u bllokua për shkak të sjelljes së dyshimtë`);
    sendAlert(`IP ${ip} është bllokuar për shkak të kërcënimit të lartë!`);
    logToDistributedSystem(ip, ipLog[ip]); // Ruaj logjet në një sistem të decentralizuar
    return true;
  }

  return false;
}
