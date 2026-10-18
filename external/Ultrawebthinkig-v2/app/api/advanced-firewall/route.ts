import { NextRequest, NextResponse } from 'next/server';

interface IPLog {
  [ip: string]: {
    count: number;
    lastAccess: number;
    threatLevel: number;
    blocked: boolean;
    location?: string;
    userAgent?: string | undefined;
    requests: Array<{
      timestamp: number;
      path: string;
      method: string;
      statusCode: number;
    }>;
  };
}

interface FirewallStats {
  totalRequests: number;
  blockedRequests: number;
  uniqueIPs: number;
  blockedIPs: number;
  highThreatIPs: number;
  averageThreatLevel: number;
  lastUpdate: string;
}

interface ThreatAlert {
  id: string;
  ip: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  timestamp: string;
  blocked: boolean;
  location?: string | undefined;
}

// In-memory storage (in production, use Redis or database)
let ipLog: IPLog = {};
let threatAlerts: ThreatAlert[] = [];

// Advanced firewall function based on the git security firewall
const advancedFirewall = (ip: string, userAgent?: string, path?: string, method?: string): { 
  blocked: boolean; 
  reason?: string; 
  threatLevel: number;
  alert?: ThreatAlert;
} => {
  const now = Date.now();

  // Initialize IP log if not exists
  if (!ipLog[ip]) {
    ipLog[ip] = { 
      count: 1, 
      lastAccess: now, 
      threatLevel: 0, 
      blocked: false,
      userAgent,
      requests: []
    };
    return { blocked: false, threatLevel: 0 };
  }

  const ipData = ipLog[ip];
  const timeDiff = now - ipData.lastAccess;
  ipData.lastAccess = now;
  ipData.userAgent = userAgent || ipData.userAgent;

  // Add request to history
  ipData.requests.push({
    timestamp: now,
    path: path || '/',
    method: method || 'GET',
    statusCode: 200
  });

  // Keep only last 100 requests
  if (ipData.requests.length > 100) {
    ipData.requests = ipData.requests.slice(-100);
  }

  // Rate limiting analysis
  if (timeDiff < 1000) { // Less than 1 second
    ipData.count += 2; // Higher penalty for rapid requests
    ipData.threatLevel += 2;
  } else if (timeDiff < 5000) { // Less than 5 seconds
    ipData.count += 1;
    ipData.threatLevel += 1;
  } else {
    ipData.count = Math.max(1, ipData.count - 1);
    ipData.threatLevel = Math.max(0, ipData.threatLevel - 0.5);
  }

  // Suspicious pattern detection
  let suspiciousScore = 0;
  
  // Check for bot-like behavior
  if (userAgent) {
    const botPatterns = ['bot', 'crawler', 'spider', 'scraper'];
    if (botPatterns.some(pattern => userAgent.toLowerCase().includes(pattern))) {
      suspiciousScore += 1;
    }
  }

  // Check for suspicious paths
  if (path) {
    const suspiciousPaths = ['/admin', '/wp-admin', '/.env', '/config', '/api/admin'];
    if (suspiciousPaths.some(suspPath => path.includes(suspPath))) {
      suspiciousScore += 2;
      ipData.threatLevel += 1;
    }
  }

  // Check for SQL injection patterns
  if (path && (path.includes('union') || path.includes('select') || path.includes('drop'))) {
    suspiciousScore += 3;
    ipData.threatLevel += 3;
  }

  ipData.threatLevel += suspiciousScore;

  // Determine if IP should be blocked
  const shouldBlock = ipData.count > 10 || ipData.threatLevel > 15 || suspiciousScore >= 3;

  if (shouldBlock && !ipData.blocked) {
    ipData.blocked = true;
    
    // Create threat alert
    const alert: ThreatAlert = {
      id: `alert-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      ip,
      severity: ipData.threatLevel > 20 ? 'critical' : 
               ipData.threatLevel > 15 ? 'high' : 
               ipData.threatLevel > 10 ? 'medium' : 'low',
      description: `IP ${ip} blocked: ${ipData.count} requests, threat level ${ipData.threatLevel}`,
      timestamp: new Date().toISOString(),
      blocked: true,
      location: ipData.location
    };
    
    threatAlerts.unshift(alert);
    
    // Keep only last 1000 alerts
    if (threatAlerts.length > 1000) {
      threatAlerts = threatAlerts.slice(0, 1000);
    }

    console.warn(`🚨 ADVANCED FIREWALL: IP ${ip} blocked - Threat Level: ${ipData.threatLevel}`);
    
    return { 
      blocked: true, 
      reason: `High threat level (${ipData.threatLevel}) and suspicious activity`,
      threatLevel: ipData.threatLevel,
      alert
    };
  }

  if (ipData.blocked) {
    return { 
      blocked: true, 
      reason: 'IP previously blocked',
      threatLevel: ipData.threatLevel
    };
  }

  return { blocked: false, threatLevel: ipData.threatLevel };
};

// Get firewall statistics
const getFirewallStats = (): FirewallStats => {
  const ips = Object.keys(ipLog);
  const totalRequests = ips.reduce((sum, ip) => sum + (ipLog[ip]?.requests.length || 0), 0);
  const blockedIPs = ips.filter(ip => ipLog[ip]?.blocked).length;
  const blockedRequests = ips.reduce((sum, ip) => 
    sum + (ipLog[ip]?.blocked ? ipLog[ip]?.requests.length || 0 : 0), 0);
  const highThreatIPs = ips.filter(ip => (ipLog[ip]?.threatLevel || 0) > 10).length;
  const avgThreatLevel = ips.length > 0 ? 
    ips.reduce((sum, ip) => sum + (ipLog[ip]?.threatLevel || 0), 0) / ips.length : 0;

  return {
    totalRequests,
    blockedRequests,
    uniqueIPs: ips.length,
    blockedIPs,
    highThreatIPs,
    averageThreatLevel: Math.round(avgThreatLevel * 100) / 100,
    lastUpdate: new Date().toISOString()
  };
};

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action') || 'stats';

    switch (action) {
      case 'stats':
        const stats = getFirewallStats();
        return NextResponse.json({
          success: true,
          data: stats,
          timestamp: new Date().toISOString()
        });

      case 'blocked-ips':
        const blockedIPs = Object.entries(ipLog)
          .filter(([_, data]) => data.blocked)
          .map(([ip, data]) => ({
            ip,
            threatLevel: data.threatLevel,
            requestCount: data.count,
            lastAccess: new Date(data.lastAccess).toISOString(),
            userAgent: data.userAgent,
            location: data.location,
            recentRequests: data.requests.slice(-10)
          }));

        return NextResponse.json({
          success: true,
          data: { blockedIPs, count: blockedIPs.length },
          timestamp: new Date().toISOString()
        });

      case 'alerts':
        const limit = parseInt(searchParams.get('limit') || '50');
        const severity = searchParams.get('severity');
        
        let filteredAlerts = threatAlerts;
        if (severity) {
          filteredAlerts = threatAlerts.filter(alert => alert.severity === severity);
        }

        return NextResponse.json({
          success: true,
          data: { 
            alerts: filteredAlerts.slice(0, limit),
            total: filteredAlerts.length
          },
          timestamp: new Date().toISOString()
        });

      case 'ip-details':
        const ip = searchParams.get('ip');
        if (!ip) {
          return NextResponse.json({
            success: false,
            error: 'IP address required'
          }, { status: 400 });
        }

        const ipData = ipLog[ip];
        if (!ipData) {
          return NextResponse.json({
            success: false,
            error: 'IP not found in logs'
          }, { status: 404 });
        }

        return NextResponse.json({
          success: true,
          data: {
            ip,
            ...ipData,
            lastAccess: new Date(ipData.lastAccess).toISOString()
          },
          timestamp: new Date().toISOString()
        });

      case 'test':
        // Test firewall with a sample IP
        const testIP = searchParams.get('ip') || '192.168.1.100';
        const testPath = searchParams.get('path') || '/test';
        const testUserAgent = searchParams.get('userAgent') || 'Test-Agent/1.0';
        
        const result = advancedFirewall(testIP, testUserAgent, testPath, 'GET');
        
        return NextResponse.json({
          success: true,
          data: {
            testIP,
            testPath,
            testUserAgent,
            result
          },
          timestamp: new Date().toISOString()
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action'
        }, { status: 400 });
    }
  } catch (error) {
    console.error('Advanced Firewall API Error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, ip, reason } = body;

    switch (action) {
      case 'block':
        if (!ip) {
          return NextResponse.json({
            success: false,
            error: 'IP address required'
          }, { status: 400 });
        }

        // Manually block an IP
        if (!ipLog[ip]) {
          ipLog[ip] = {
            count: 0,
            lastAccess: Date.now(),
            threatLevel: 20,
            blocked: true,
            requests: []
          };
        } else {
          ipLog[ip].blocked = true;
          ipLog[ip].threatLevel = Math.max(20, ipLog[ip].threatLevel);
        }

        // Create alert
        const blockAlert: ThreatAlert = {
          id: `manual-block-${Date.now()}`,
          ip,
          severity: 'high',
          description: `Manually blocked: ${reason || 'No reason provided'}`,
          timestamp: new Date().toISOString(),
          blocked: true
        };
        
        threatAlerts.unshift(blockAlert);

        return NextResponse.json({
          success: true,
          data: {
            message: `IP ${ip} has been blocked`,
            reason: reason || 'Manual block',
            alert: blockAlert
          }
        });

      case 'unblock':
        if (!ip) {
          return NextResponse.json({
            success: false,
            error: 'IP address required'
          }, { status: 400 });
        }

        if (ipLog[ip]) {
          ipLog[ip].blocked = false;
          ipLog[ip].threatLevel = Math.max(0, ipLog[ip].threatLevel - 10);
        }

        return NextResponse.json({
          success: true,
          data: {
            message: `IP ${ip} has been unblocked`,
            newThreatLevel: ipLog[ip]?.threatLevel || 0
          }
        });

      case 'clear-logs':
        // Clear all logs (use with caution)
        const backupCount = Object.keys(ipLog).length;
        ipLog = {};
        threatAlerts = [];

        return NextResponse.json({
          success: true,
          data: {
            message: 'All firewall logs cleared',
            clearedIPs: backupCount
          }
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action'
        }, { status: 400 });
    }
  } catch (error) {
    console.error('Advanced Firewall POST Error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

// Export the firewall function for use in middleware
export { advancedFirewall };
