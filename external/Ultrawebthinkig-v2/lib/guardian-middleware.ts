/**
 * Guardian Middleware - Edge Runtime Compatible
 * Pure TypeScript Security Middleware for Vercel Edge
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version Ultra 2.0.0 Edge
 * @license MIT
 */

// Edge Runtime compatible Guardian Middleware
// No Node.js APIs used - compatible with Vercel Edge

interface BlockedIP {
  ip: string;
  reason: string;
  timestamp: number;
  userAgent?: string;
}

interface SecurityMetrics {
  requestCount: number;
  lastRequest: number;
  payloadSizes: number[];
  userAgents: Set<string>;
}

// In-memory storage for Edge Runtime
const securityMetrics = new Map<string, SecurityMetrics>();
const blockedIPs = new Map<string, BlockedIP>();

// Predefined blocked IPs and patterns
const BLOCKED_IPS = new Set([
  '192.168.1.100', // Example blocked IP
]);

const BLOCKED_USER_AGENTS = [
  'bot',
  'crawler',
  'spider',
  'scraper',
  'hack',
  'malware'
];

export function guardianMiddleware(request: Request): Response | null {
  const ip = getClientIP(request);
  const userAgent = request.headers.get('user-agent') || '';
  const currentTime = Date.now();

  // Check if IP is blocked
  if (isIPBlocked(ip)) {
    console.log(`🚫 GUARDIAN: Blocked request from ${ip}`);
    return new Response(
      JSON.stringify({ 
        error: 'Access denied', 
        message: 'Your IP has been blocked for security reasons',
        guardian: true 
      }),
      { 
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }

  // Update metrics
  updateSecurityMetrics(ip, userAgent, currentTime, request);

  // Auto-detection and blocking
  const securityCheck = performSecurityChecks(ip, request);
  if (securityCheck.shouldBlock && securityCheck.reason) {
    console.log(`🚨 AUTO-BLOCK: ${ip} - ${securityCheck.reason}`);
    autoBlockIP(ip, securityCheck.reason);
    
    return new Response(
      JSON.stringify({ 
        error: 'Security violation detected', 
        message: 'Request blocked for security reasons',
        guardian: true 
      }),
      { 
        status: 403,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }

  // Allow request to proceed
  return null;
}

function getClientIP(request: Request): string {
  // Try to get real IP from headers (Vercel, Cloudflare, etc.)
  const xForwardedFor = request.headers.get('x-forwarded-for');
  const xRealIP = request.headers.get('x-real-ip');
  const cfConnectingIP = request.headers.get('cf-connecting-ip');
  
  if (cfConnectingIP) return cfConnectingIP;
  if (xRealIP) return xRealIP;
  if (xForwardedFor) return xForwardedFor.split(',')[0].trim();
  
  return 'unknown';
}

function isIPBlocked(ip: string): boolean {
  try {
    // Check predefined blocked IPs
    if (BLOCKED_IPS.has(ip)) {
      return true;
    }
    
    // Check in-memory blocked IPs
    if (blockedIPs.has(ip)) {
      const blocked = blockedIPs.get(ip)!;
      // Check if block is still valid (24 hours)
      if (Date.now() - blocked.timestamp < 24 * 60 * 60 * 1000) {
        return true;
      } else {
        // Remove expired block
        blockedIPs.delete(ip);
      }
    }
    
    return false;
  } catch (error) {
    console.error('Error checking blocked IPs:', error);
    return false;
  }
}

function updateSecurityMetrics(ip: string, userAgent: string, timestamp: number, request: Request): void {
  if (!securityMetrics.has(ip)) {
    securityMetrics.set(ip, {
      requestCount: 0,
      lastRequest: timestamp,
      payloadSizes: [],
      userAgents: new Set()
    });
  }

  const metrics = securityMetrics.get(ip)!;
  metrics.requestCount++;
  metrics.lastRequest = timestamp;
  metrics.userAgents.add(userAgent);

  // Clean old metrics (keep last 1000 IPs)
  if (securityMetrics.size > 1000) {
    const oldestIP = Array.from(securityMetrics.keys())[0];
    securityMetrics.delete(oldestIP);
  }
}

function performSecurityChecks(ip: string, request: Request): { shouldBlock: boolean; reason?: string } {
  const userAgent = request.headers.get('user-agent') || '';
  const url = new URL(request.url);
  
  // Check for malicious user agents
  const isMaliciousUA = BLOCKED_USER_AGENTS.some(blocked => 
    userAgent.toLowerCase().includes(blocked.toLowerCase())
  );
  
  if (isMaliciousUA) {
    return { shouldBlock: true, reason: 'Malicious User Agent' };
  }

  // Check for SQL injection patterns
  const sqlPatterns = ['union', 'select', 'drop', 'insert', 'delete', 'update', '--', '/*'];
  const queryString = url.search.toLowerCase();
  const hasSQLInjection = sqlPatterns.some(pattern => queryString.includes(pattern));
  
  if (hasSQLInjection) {
    return { shouldBlock: true, reason: 'SQL Injection Attempt' };
  }

  // Check for XSS patterns
  const xssPatterns = ['<script', 'javascript:', 'onerror=', 'onload='];
  const hasXSS = xssPatterns.some(pattern => queryString.includes(pattern.toLowerCase()));
  
  if (hasXSS) {
    return { shouldBlock: true, reason: 'XSS Attempt' };
  }

  // Rate limiting check
  const metrics = securityMetrics.get(ip);
  if (metrics) {
    const timeDiff = Date.now() - metrics.lastRequest;
    const requestsPerMinute = metrics.requestCount / Math.max(1, timeDiff / (60 * 1000));
    
    if (requestsPerMinute > 100) { // More than 100 requests per minute
      return { shouldBlock: true, reason: 'Rate Limit Exceeded' };
    }
  }

  return { shouldBlock: false };
}

function autoBlockIP(ip: string, reason: string): void {
  try {
    const userAgent = 'unknown';
    
    blockedIPs.set(ip, {
      ip,
      reason,
      timestamp: Date.now(),
      userAgent
    });

    console.log(`🛡️ GUARDIAN: Auto-blocked ${ip} for: ${reason}`);
    
    // Clean old blocks (keep last 100)
    if (blockedIPs.size > 100) {
      const oldestIP = Array.from(blockedIPs.keys())[0];
      blockedIPs.delete(oldestIP);
    }
  } catch (error) {
    console.error('Error saving blocked IP:', error);
  }
}

// Guardian status endpoint data
export function getGuardianStatus() {
  return {
    activeBlocks: blockedIPs.size,
    monitoredIPs: securityMetrics.size,
    lastUpdate: Date.now(),
    status: 'active'
  };
}

export default guardianMiddleware;

