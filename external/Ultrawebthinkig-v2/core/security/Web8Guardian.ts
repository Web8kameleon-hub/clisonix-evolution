/**
 * Web8 Security Guardian - Industrial Grade Security
 * Advanced Threat Detection and Protection System
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @version 8.0.0 Ultra
 */

export interface SecurityThreat {
  id: string;
  type: 'injection' | 'xss' | 'csrf' | 'dos' | 'malware' | 'suspicious';
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  timestamp: number;
  source: string;
  blocked: boolean;
}

export interface SecurityMetrics {
  totalRequests: number;
  blockedRequests: number;
  threatsDetected: number;
  lastScanTime: number;
  systemStatus: 'secure' | 'warning' | 'critical';
}

export class Web8Security {
  private threats: SecurityThreat[] = [];
  private metrics: SecurityMetrics = {
    totalRequests: 0,
    blockedRequests: 0,
    threatsDetected: 0,
    lastScanTime: Date.now(),
    systemStatus: 'secure'
  };

  private threatPatterns = {
    injection: [
      /(\bSELECT\b.*\bFROM\b)/i,
      /(\bUNION\b.*\bSELECT\b)/i,
      /(\bDROP\b.*\bTABLE\b)/i,
      /(\bEXEC\b.*\bxp_)/i
    ],
    xss: [
      /<script[^>]*>.*?<\/script>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi,
      /<iframe[^>]*>/gi
    ],
    suspicious: [
      /\.\.\//g,
      /\/etc\/passwd/g,
      /cmd\.exe/g,
      /powershell/g
    ]
  };

  constructor() {
    this.initializeSecurity();
  }

  private initializeSecurity(): void {
    console.log('🛡️ Web8Security Guardian initialized');
    this.startMetricsCollection();
  }

  private startMetricsCollection(): void {
    setInterval(() => {
      this.metrics.lastScanTime = Date.now();
      this.updateSystemStatus();
    }, 30000); // Update every 30 seconds
  }

  public async scanContent(content: string, source: string = 'unknown'): Promise<{
    isSafe: boolean;
    threats: SecurityThreat[];
    riskScore: number;
  }> {
    this.metrics.totalRequests++;
    const detectedThreats: SecurityThreat[] = [];

    // Scan for injection attacks
    for (const pattern of this.threatPatterns.injection) {
      if (pattern.test(content)) {
        detectedThreats.push(this.createThreat('injection', 'high', 'SQL injection attempt detected', source));
      }
    }

    // Scan for XSS attacks
    for (const pattern of this.threatPatterns.xss) {
      if (pattern.test(content)) {
        detectedThreats.push(this.createThreat('xss', 'high', 'Cross-site scripting attempt detected', source));
      }
    }

    // Scan for suspicious patterns
    for (const pattern of this.threatPatterns.suspicious) {
      if (pattern.test(content)) {
        detectedThreats.push(this.createThreat('suspicious', 'medium', 'Suspicious pattern detected', source));
      }
    }

    // Calculate risk score
    const riskScore = this.calculateRiskScore(detectedThreats);
    const isSafe = riskScore < 50;

    if (detectedThreats.length > 0) {
      this.threats.push(...detectedThreats);
      this.metrics.threatsDetected += detectedThreats.length;
      
      if (!isSafe) {
        this.metrics.blockedRequests++;
      }
    }

    this.updateSystemStatus();

    return {
      isSafe,
      threats: detectedThreats,
      riskScore
    };
  }

  private createThreat(
    type: SecurityThreat['type'],
    severity: SecurityThreat['severity'],
    description: string,
    source: string
  ): SecurityThreat {
    return {
      id: `threat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      severity,
      description,
      timestamp: Date.now(),
      source,
      blocked: severity === 'high' || severity === 'critical'
    };
  }

  private calculateRiskScore(threats: SecurityThreat[]): number {
    if (threats.length === 0) return 0;

    const severityScores = {
      low: 10,
      medium: 30,
      high: 70,
      critical: 100
    };

    const totalScore = threats.reduce((sum, threat) => sum + severityScores[threat.severity], 0);
    return Math.min(totalScore, 100);
  }

  private updateSystemStatus(): void {
    const recentThreats = this.threats.filter(t => Date.now() - t.timestamp < 300000); // Last 5 minutes
    const criticalThreats = recentThreats.filter(t => t.severity === 'critical');
    const highThreats = recentThreats.filter(t => t.severity === 'high');

    if (criticalThreats.length > 0 || highThreats.length > 5) {
      this.metrics.systemStatus = 'critical';
    } else if (highThreats.length > 0 || recentThreats.length > 10) {
      this.metrics.systemStatus = 'warning';
    } else {
      this.metrics.systemStatus = 'secure';
    }
  }

  public getMetrics(): SecurityMetrics {
    return { ...this.metrics };
  }

  public getThreats(limit: number = 50): SecurityThreat[] {
    return this.threats
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, limit);
  }

  public clearThreats(): void {
    this.threats = [];
    this.metrics.threatsDetected = 0;
    this.metrics.blockedRequests = 0;
    this.updateSystemStatus();
  }

  public async performSecurityScan(): Promise<{
    status: 'clean' | 'threats_detected' | 'critical_threats';
    summary: string;
    recommendations: string[];
  }> {
    const recentThreats = this.getThreats(100);
    const criticalCount = recentThreats.filter(t => t.severity === 'critical').length;
    const highCount = recentThreats.filter(t => t.severity === 'high').length;

    let status: 'clean' | 'threats_detected' | 'critical_threats' = 'clean';
    const recommendations: string[] = [];

    if (criticalCount > 0) {
      status = 'critical_threats';
      recommendations.push('🚨 Immediate security review required');
      recommendations.push('🔒 Consider implementing additional security layers');
    } else if (highCount > 0 || recentThreats.length > 5) {
      status = 'threats_detected';
      recommendations.push('⚠️ Monitor security logs closely');
      recommendations.push('🛡️ Update security rules if needed');
    } else {
      recommendations.push('✅ Security status is good');
      recommendations.push('🔍 Continue regular monitoring');
    }

    const summary = `Security scan completed. Found ${recentThreats.length} threats (${criticalCount} critical, ${highCount} high severity). System status: ${this.metrics.systemStatus.toUpperCase()}.`;

    return {
      status,
      summary,
      recommendations
    };
  }

  public generateSecurityReport(): string {
    const metrics = this.getMetrics();
    const recentThreats = this.getThreats(10);

    let report = `🛡️ WEB8 SECURITY REPORT\n`;
    report += `===============================\n`;
    report += `System Status: ${metrics.systemStatus.toUpperCase()}\n`;
    report += `Total Requests: ${metrics.totalRequests}\n`;
    report += `Blocked Requests: ${metrics.blockedRequests}\n`;
    report += `Threats Detected: ${metrics.threatsDetected}\n`;
    report += `Last Scan: ${new Date(metrics.lastScanTime).toLocaleString()}\n`;
    report += `\nRecent Threats:\n`;
    
    recentThreats.forEach(threat => {
      report += `- ${threat.type.toUpperCase()} (${threat.severity}): ${threat.description}\n`;
    });

    return report;
  }
}
