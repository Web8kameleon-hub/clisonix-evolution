/**
 * Real Guardian Security Engine
 * Monitorim i vërtetë i sigurisë dhe mbrojtjes
 * 
 * @author Ledjan Ahmati
 * @version 8.1.0-SECURITY
 */

import { Request } from 'express';

export interface SecurityThreat {
  id: string;
  type: 'ddos' | 'injection' | 'brute_force' | 'suspicious_activity';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  timestamp: number;
  description: string;
  blocked: boolean;
}

export interface SecurityStats {
  totalRequests: number;
  blockedRequests: number;
  threatsDetected: number;
  activeConnections: number;
  ipBlacklist: string[];
  lastUpdate: number;
}

export class RealGuardianEngine {
  private threats: SecurityThreat[] = [];
  private stats: SecurityStats;
  private ipRequestCounts: Map<string, { count: number; lastReset: number }> = new Map();
  private blacklistedIPs: Set<string> = new Set();
  private suspiciousPatterns: RegExp[] = [
    /script.*?>/i,
    /union.*?select/i,
    /drop.*?table/i,
    /exec.*?\(/i,
    /<.*?>/
  ];

  constructor() {
    this.stats = {
      totalRequests: 0,
      blockedRequests: 0,
      threatsDetected: 0,
      activeConnections: 0,
      ipBlacklist: [],
      lastUpdate: Date.now()
    };

    // Clean up old data every minute
    setInterval(() => {
      this.cleanupOldData();
    }, 60000);
  }

  public analyzeRequest(req: Request): { allowed: boolean; threat?: SecurityThreat } {
    const ip = this.getClientIP(req);
    this.stats.totalRequests++;

    // Check if IP is blacklisted
    if (this.blacklistedIPs.has(ip)) {
      this.stats.blockedRequests++;
      return {
        allowed: false,
        threat: this.createThreat('ddos', 'high', ip, 'IP is blacklisted')
      };
    }

    // Rate limiting check
    if (this.isRateLimited(ip)) {
      const threat = this.createThreat('ddos', 'medium', ip, 'Rate limit exceeded');
      this.addThreat(threat);
      this.stats.blockedRequests++;
      return { allowed: false, threat };
    }

    // Check for injection attacks
    const injectionThreat = this.checkForInjection(req, ip);
    if (injectionThreat) {
      this.addThreat(injectionThreat);
      this.stats.blockedRequests++;
      return { allowed: false, threat: injectionThreat };
    }

    // Check for suspicious activity
    const suspiciousThreat = this.checkSuspiciousActivity(req, ip);
    if (suspiciousThreat) {
      this.addThreat(suspiciousThreat);
      // Still allow but log
    }

    return { allowed: true };
  }

  private getClientIP(req: Request): string {
    return (req.headers['x-forwarded-for'] as string) ||
           (req.headers['x-real-ip'] as string) ||
           req.socket?.remoteAddress ||
           'unknown';
  }

  private isRateLimited(ip: string): boolean {
    const now = Date.now();
    const current = this.ipRequestCounts.get(ip) || { count: 0, lastReset: now };

    // Reset counter every minute
    if (now - current.lastReset > 60000) {
      current.count = 0;
      current.lastReset = now;
    }

    current.count++;
    this.ipRequestCounts.set(ip, current);

    // Allow 100 requests per minute
    return current.count > 100;
  }

  private checkForInjection(req: Request, ip: string): SecurityThreat | null {
    const body = JSON.stringify(req.body || {});
    const query = JSON.stringify(req.query || {});
    const params = JSON.stringify(req.params || {});
    const allData = body + query + params;

    for (const pattern of this.suspiciousPatterns) {
      if (pattern.test(allData)) {
        return this.createThreat(
          'injection',
          'critical',
          ip,
          `Injection attempt detected: ${pattern.source}`
        );
      }
    }

    return null;
  }

  private checkSuspiciousActivity(req: Request, ip: string): SecurityThreat | null {
    const userAgent = req.headers['user-agent'] || '';
    
    // Check for bot-like user agents
    const botPatterns = [/bot/i, /crawler/i, /spider/i, /scraper/i];
    const isBot = botPatterns.some(pattern => pattern.test(userAgent));

    if (isBot && req.path.includes('/api/')) {
      return this.createThreat(
        'suspicious_activity',
        'low',
        ip,
        'Bot accessing API endpoints'
      );
    }

    return null;
  }

  private createThreat(
    type: SecurityThreat['type'],
    severity: SecurityThreat['severity'],
    source: string,
    description: string
  ): SecurityThreat {
    return {
      id: crypto.randomUUID(),
      type,
      severity,
      source,
      timestamp: Date.now(),
      description,
      blocked: severity === 'critical' || severity === 'high'
    };
  }

  private addThreat(threat: SecurityThreat): void {
    this.threats.push(threat);
    this.stats.threatsDetected++;
    
    if (threat.blocked) {
      this.blacklistedIPs.add(threat.source);
    }

    // Keep only last 1000 threats
    if (this.threats.length > 1000) {
      this.threats = this.threats.slice(-1000);
    }
  }

  private cleanupOldData(): void {
    const oneHourAgo = Date.now() - (60 * 60 * 1000);
    
    // Remove old threats
    this.threats = this.threats.filter(threat => threat.timestamp > oneHourAgo);
    
    // Reset IP request counts
    for (const [ip, data] of this.ipRequestCounts.entries()) {
      if (Date.now() - data.lastReset > 300000) { // 5 minutes
        this.ipRequestCounts.delete(ip);
      }
    }

    this.stats.lastUpdate = Date.now();
  }

  public getSecurityStats(): SecurityStats {
    return {
      ...this.stats,
      ipBlacklist: Array.from(this.blacklistedIPs),
      activeConnections: this.ipRequestCounts.size
    };
  }

  public getRecentThreats(limit: number = 50): SecurityThreat[] {
    return this.threats
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }

  public getDashboardData() {
    const recentThreats = this.getRecentThreats(10);
    const stats = this.getSecurityStats();

    return {
      status: 'active',
      protection: 'enabled',
      version: '8.1.0',
      stats,
      recentThreats,
      timestamp: new Date().toISOString()
    };
  }

  public getLogs(limit: number = 100) {
    return {
      logs: this.threats.slice(-limit).map(threat => ({
        timestamp: new Date(threat.timestamp).toISOString(),
        level: threat.severity,
        message: `${threat.type.toUpperCase()}: ${threat.description}`,
        source: threat.source,
        blocked: threat.blocked
      })),
      status: 'active'
    };
  }

  public blacklistIP(ip: string): void {
    this.blacklistedIPs.add(ip);
  }

  public unblacklistIP(ip: string): void {
    this.blacklistedIPs.delete(ip);
  }
}
