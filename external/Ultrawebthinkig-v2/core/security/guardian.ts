// Security Guardian - Content Safety & Threat Detection
export interface SecurityScanResult {
  isSafe: boolean;
  violations: SecurityViolation[];
  riskScore: number;
  recommendations: string[];
}

export interface SecurityViolation {
  type: 'content' | 'rate' | 'injection' | 'privacy';
  severity: 'low' | 'medium' | 'high';
  message: string;
  timestamp: Date;
}

export class SecurityGuard {
  private rateLimit: Map<string, number[]> = new Map();
  private dangerousPatterns = [
    /password|secret|key|token/i,
    /hack|exploit|vulnerability/i,
    /personal.*information|social.*security|credit.*card/i,
    /<script|javascript:|data:|vbscript:/i,
    /\b(?:DELETE|DROP|INSERT|UPDATE)\s+/i
  ];

  async scanContent(content: string): Promise<SecurityScanResult> {
    const violations: SecurityViolation[] = [];
    let riskScore = 0;

    // Content safety scan
    for (const pattern of this.dangerousPatterns) {
      if (pattern.test(content)) {
        violations.push({
          type: 'content',
          severity: 'medium',
          message: 'Potentially sensitive content detected',
          timestamp: new Date()
        });
        riskScore += 30;
      }
    }

    // Rate limiting check
    const userId = 'default';
    const now = Date.now();
    const userRequests = this.rateLimit.get(userId) || [];
    const recentRequests = userRequests.filter(time => now - time < 60000);
    
    if (recentRequests.length > 10) {
      violations.push({
        type: 'rate',
        severity: 'high',
        message: 'Rate limit exceeded',
        timestamp: new Date()
      });
      riskScore += 50;
    }

    // Update rate limit
    recentRequests.push(now);
    this.rateLimit.set(userId, recentRequests);

    // Length check
    if (content.length > 10000) {
      violations.push({
        type: 'content',
        severity: 'low',
        message: 'Content exceeds recommended length',
        timestamp: new Date()
      });
      riskScore += 10;
    }

    const isSafe = riskScore < 70;
    const recommendations = violations.length > 0 ? [
      'Review content for sensitive information',
      'Consider breaking long messages into smaller parts',
      'Verify content compliance with usage policies'
    ] : [];

    return {
      isSafe,
      violations,
      riskScore,
      recommendations
    };
  }

  getThreatLevel(riskScore: number): 'low' | 'medium' | 'high' {
    if (riskScore < 30) return 'low';
    if (riskScore < 70) return 'medium';
    return 'high';
  }
}
