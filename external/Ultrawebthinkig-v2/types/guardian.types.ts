/**
 * 🛡️ GUARDIAN TYPES - TYPE DEFINITIONS FOR GUARDIAN SYSTEMS
 * Type definitions për Guardian Security dhe Monitoring Systems
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0-GUARDIAN-TYPES
 * @license MIT
 */

/**
 * 🛡️ GUARDIAN CONFIGURATION
 */
export interface GuardianConfig {
  security: {
    encryptionLevel: 'basic' | 'standard' | 'advanced' | 'military';
    authenticationRequired: boolean;
    rateLimiting: {
      enabled: boolean;
      requests: number;
      window: number;
    };
    corsPolicy: {
      origins: string[];
      methods: string[];
      headers: string[];
    };
  };
  monitoring: {
    realTime: boolean;
    metricsCollection: boolean;
    errorTracking: boolean;
    performanceMonitoring: boolean;
    userTracking: boolean;
  };
  protection: {
    ddosProtection: boolean;
    sqlInjectionProtection: boolean;
    xssProtection: boolean;
    csrfProtection: boolean;
    contentFiltering: boolean;
  };
  compliance: {
    gdpr: boolean;
    ccpa: boolean;
    hipaa: boolean;
    soc2: boolean;
  };
}

/**
 * 🔐 SECURITY THREAT
 */
export interface SecurityThreat {
  id: string;
  type: 'ddos' | 'injection' | 'xss' | 'csrf' | 'malware' | 'phishing' | 'brute_force' | 'insider';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: {
    ip: string;
    userAgent: string;
    location?: {
      country: string;
      region: string;
      city: string;
    };
    reputation: number;
  };
  target: {
    endpoint: string;
    method: string;
    payload?: unknown;
  };
  detection: {
    timestamp: Date;
    method: 'signature' | 'anomaly' | 'heuristic' | 'ml';
    confidence: number;
    rules: string[];
  };
  impact: {
    affected: string[];
    dataExposed: boolean;
    serviceDisrupted: boolean;
    financialCost: number;
  };
  status: 'detected' | 'investigating' | 'mitigated' | 'resolved' | 'false_positive';
  mitigation?: SecurityMitigation;
}

/**
 * 🛡️ SECURITY MITIGATION
 */
export interface SecurityMitigation {
  id: string;
  threatId: string;
  type: 'block' | 'throttle' | 'challenge' | 'redirect' | 'quarantine' | 'monitor';
  action: string;
  parameters: Record<string, any>;
  applied: Date;
  duration?: number;
  effectiveness: number;
  automatedResponse: boolean;
  approvedBy?: string;
}

/**
 * 📊 SECURITY METRICS
 */
export interface SecurityMetrics {
  threats: {
    total: number;
    blocked: number;
    mitigated: number;
    falsePositives: number;
    byType: Record<string, number>;
    bySeverity: Record<string, number>;
  };
  attacks: {
    attempts: number;
    successful: number;
    sources: Record<string, number>;
    targets: Record<string, number>;
  };
  authentication: {
    attempts: number;
    successful: number;
    failed: number;
    compromised: number;
  };
  compliance: {
    violations: number;
    audits: number;
    certifications: string[];
    lastAssessment: Date;
  };
  performance: {
    averageResponseTime: number;
    securityOverhead: number;
    falsePositiveRate: number;
    detectionAccuracy: number;
  };
}

/**
 * 👤 USER AUTHENTICATION
 */
export interface UserAuthentication {
  id: string;
  userId: string;
  method: 'password' | 'oauth' | 'saml' | 'biometric' | 'mfa' | 'sso';
  status: 'pending' | 'authenticated' | 'failed' | 'expired' | 'locked';
  timestamp: Date;
  location: {
    ip: string;
    country: string;
    city: string;
  };
  device: {
    type: string;
    os: string;
    browser: string;
    fingerprint: string;
  };
  factors: {
    primary: boolean;
    secondary?: boolean;
    biometric?: boolean;
  };
  session: {
    id: string;
    expires: Date;
    active: boolean;
    permissions: string[];
  };
  risk: {
    score: number;
    factors: string[];
    trust: number;
  };
}

/**
 * 🔑 ACCESS CONTROL
 */
export interface AccessControl {
  id: string;
  principal: {
    type: 'user' | 'group' | 'role' | 'service';
    id: string;
    name: string;
  };
  resource: {
    type: string;
    id: string;
    path: string;
  };
  permissions: {
    read: boolean;
    write: boolean;
    execute: boolean;
    delete: boolean;
    admin: boolean;
    custom: Record<string, boolean>;
  };
  conditions: {
    timeRestrictions?: {
      allowed: string[];
      timezone: string;
    };
    locationRestrictions?: {
      allowed: string[];
      blocked: string[];
    };
    deviceRestrictions?: {
      types: string[];
      trusted: boolean;
    };
  };
  inheritance: {
    inherited: boolean;
    source?: string;
    overrides: string[];
  };
  audit: {
    created: Date;
    createdBy: string;
    modified: Date;
    modifiedBy: string;
    accessed: Date[];
  };
}

/**
 * 📋 AUDIT LOG
 */
export interface AuditLog {
  id: string;
  timestamp: Date;
  event: {
    type: 'access' | 'authentication' | 'authorization' | 'configuration' | 'data' | 'system';
    action: string;
    outcome: 'success' | 'failure' | 'partial';
    severity: 'info' | 'warning' | 'error' | 'critical';
  };
  actor: {
    type: 'user' | 'system' | 'service' | 'anonymous';
    id: string;
    name: string;
    ip: string;
    userAgent: string;
  };
  target: {
    type: string;
    id: string;
    name: string;
    path?: string;
  };
  details: {
    description: string;
    before?: unknown;
    after?: unknown;
    metadata: Record<string, any>;
  };
  compliance: {
    regulations: string[];
    retention: number;
    classification: 'public' | 'internal' | 'confidential' | 'restricted';
  };
}

/**
 * 🔍 MONITORING ALERT
 */
export interface MonitoringAlert {
  id: string;
  timestamp: Date;
  type: 'security' | 'performance' | 'availability' | 'compliance' | 'anomaly';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: {
    system: string;
    component: string;
    metric: string;
  };
  condition: {
    rule: string;
    threshold: number;
    actual: number;
    duration: number;
  };
  status: 'open' | 'acknowledged' | 'investigating' | 'resolved' | 'closed';
  assignee?: string;
  escalation: {
    level: number;
    nextEscalation?: Date;
    notifications: string[];
  };
  resolution?: {
    timestamp: Date;
    action: string;
    resolvedBy: string;
    rootCause: string;
  };
}

/**
 * 📈 PERFORMANCE METRICS
 */
export interface PerformanceMetrics {
  system: {
    cpu: number;
    memory: number;
    disk: number;
    network: number;
    uptime: number;
  };
  application: {
    responseTime: number;
    throughput: number;
    errorRate: number;
    availability: number;
    saturation: number;
  };
  security: {
    scanTime: number;
    rulesProcessed: number;
    threatsDetected: number;
    blockedRequests: number;
    falsePositives: number;
  };
  user: {
    sessions: number;
    requests: number;
    errors: number;
    satisfaction: number;
  };
  timestamp: Date;
}

/**
 * 🧠 ANOMALY DETECTION
 */
export interface AnomalyDetection {
  id: string;
  timestamp: Date;
  type: 'statistical' | 'ml' | 'rule_based' | 'hybrid';
  metric: string;
  baseline: {
    mean: number;
    std: number;
    min: number;
    max: number;
    samples: number;
    period: string;
  };
  anomaly: {
    value: number;
    score: number;
    deviation: number;
    confidence: number;
    duration: number;
  };
  context: {
    related: string[];
    correlations: Record<string, number>;
    events: string[];
  };
  classification: {
    category: 'positive' | 'negative' | 'neutral';
    impact: 'low' | 'medium' | 'high';
    urgency: 'low' | 'medium' | 'high';
    predicted: boolean;
  };
  investigation: {
    automated: boolean;
    findings: string[];
    recommendations: string[];
    actions: string[];
  };
}

/**
 * 🛡️ GUARDIAN CONTROLLER
 */
export interface GuardianController {
  id: string;
  config: GuardianConfig;
  
  // Lifecycle
  initialize(): Promise<void>;
  start(): Promise<void>;
  stop(): Promise<void>;
  destroy(): Promise<void>;
  
  // Security
  detectThreats(): Promise<SecurityThreat[]>;
  mitigateThreat(threat: SecurityThreat): Promise<SecurityMitigation>;
  authenticateUser(credentials: unknown): Promise<UserAuthentication>;
  authorizeAccess(request: unknown): Promise<boolean>;
  
  // Monitoring
  collectMetrics(): Promise<PerformanceMetrics>;
  detectAnomalies(): Promise<AnomalyDetection[]>;
  generateAlert(condition: unknown): Promise<MonitoringAlert>;
  
  // Audit
  logEvent(event: Partial<AuditLog>): Promise<void>;
  queryLogs(criteria: unknown): Promise<AuditLog[]>;
  generateReport(type: string, period: string): Promise<any>;
  
  // Management
  updateConfig(config: Partial<GuardianConfig>): Promise<void>;
  getStatus(): Promise<GuardianStatus>;
  healthCheck(): Promise<boolean>;
}

/**
 * 📊 GUARDIAN STATUS
 */
export interface GuardianStatus {
  overall: 'healthy' | 'warning' | 'critical' | 'maintenance';
  components: {
    security: 'active' | 'degraded' | 'offline';
    monitoring: 'active' | 'degraded' | 'offline';
    logging: 'active' | 'degraded' | 'offline';
    authentication: 'active' | 'degraded' | 'offline';
  };
  metrics: {
    uptime: number;
    threatsBlocked: number;
    alertsGenerated: number;
    performanceImpact: number;
  };
  alerts: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  lastUpdate: Date;
}

/**
 * 🔧 GUARDIAN RULE
 */
export interface GuardianRule {
  id: string;
  name: string;
  description: string;
  category: 'security' | 'performance' | 'compliance' | 'anomaly';
  type: 'signature' | 'threshold' | 'pattern' | 'ml';
  condition: {
    logic: string;
    parameters: Record<string, any>;
    threshold?: number;
    pattern?: string;
  };
  action: {
    type: 'alert' | 'block' | 'throttle' | 'log' | 'notify';
    parameters: Record<string, any>;
    severity: 'low' | 'medium' | 'high' | 'critical';
  };
  metadata: {
    enabled: boolean;
    priority: number;
    tags: string[];
    author: string;
    created: Date;
    modified: Date;
    version: string;
  };
  performance: {
    executionTime: number;
    memoryUsage: number;
    accuracy: number;
    falsePositiveRate: number;
  };
}

/**
 * 🌐 GUARDIAN CONTEXT
 */
export interface GuardianContext {
  request: {
    id: string;
    method: string;
    url: string;
    headers: Record<string, string>;
    body?: unknown;
    timestamp: Date;
  };
  user: {
    id?: string;
    authenticated: boolean;
    roles: string[];
    permissions: string[];
    risk: number;
  };
  session: {
    id: string;
    created: Date;
    lastActivity: Date;
    location: string;
    device: string;
  };
  environment: {
    system: string;
    version: string;
    load: number;
    memory: number;
    connections: number;
  };
  threat: {
    level: 'low' | 'medium' | 'high' | 'critical';
    sources: string[];
    indicators: string[];
    score: number;
  };
}

/**
 * 🔍 GUARDIAN SCANNER
 */
export interface GuardianScanner {
  id: string;
  type: 'vulnerability' | 'malware' | 'compliance' | 'configuration' | 'dependency';
  name: string;
  description: string;
  
  // Scanning
  scan(target: unknown): Promise<GuardianScanResult>;
  quickScan(target: unknown): Promise<GuardianScanResult>;
  deepScan(target: unknown): Promise<GuardianScanResult>;
  
  // Configuration
  configure(options: unknown): void;
  getConfiguration(): unknown;
  
  // Status
  isEnabled(): boolean;
  getStatus(): string;
  getStatistics(): unknown;
}

/**
 * 📊 GUARDIAN SCAN RESULT
 */
export interface GuardianScanResult {
  id: string;
  scannerId: string;
  target: {
    type: string;
    identifier: string;
    path?: string;
  };
  scan: {
    started: Date;
    completed: Date;
    duration: number;
    type: 'quick' | 'deep' | 'full';
  };
  findings: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  vulnerabilities: GuardianVulnerability[];
  recommendations: string[];
  compliance: {
    passed: number;
    failed: number;
    skipped: number;
    score: number;
  };
  metadata: Record<string, any>;
}

/**
 * 🔓 GUARDIAN VULNERABILITY
 */
export interface GuardianVulnerability {
  id: string;
  cve?: string;
  title: string;
  description: string;
  severity: 'info' | 'low' | 'medium' | 'high' | 'critical';
  score: number;
  category: string;
  location: {
    file?: string;
    line?: number;
    function?: string;
    component: string;
  };
  impact: {
    confidentiality: 'none' | 'low' | 'high';
    integrity: 'none' | 'low' | 'high';
    availability: 'none' | 'low' | 'high';
  };
  vector: {
    attack: string;
    complexity: 'low' | 'high';
    privileges: 'none' | 'low' | 'high';
    interaction: 'none' | 'required';
    scope: 'unchanged' | 'changed';
  };
  remediation: {
    effort: 'low' | 'medium' | 'high';
    priority: number;
    steps: string[];
    references: string[];
  };
  status: 'open' | 'acknowledged' | 'mitigated' | 'fixed' | 'accepted' | 'false_positive';
}

/**
 * 🎯 GUARDIAN EVENTS
 */
export type GuardianEvent = 
  | { type: 'threat_detected'; data: { threat: SecurityThreat } }
  | { type: 'threat_mitigated'; data: { threat: SecurityThreat; mitigation: SecurityMitigation } }
  | { type: 'user_authenticated'; data: { authentication: UserAuthentication } }
  | { type: 'access_denied'; data: { request: unknown; reason: string } }
  | { type: 'anomaly_detected'; data: { anomaly: AnomalyDetection } }
  | { type: 'alert_generated'; data: { alert: MonitoringAlert } }
  | { type: 'scan_completed'; data: { result: GuardianScanResult } }
  | { type: 'vulnerability_found'; data: { vulnerability: GuardianVulnerability } }
  | { type: 'rule_triggered'; data: { rule: GuardianRule; context: GuardianContext } }
  | { type: 'compliance_violation'; data: { regulation: string; details: unknown } }
  | { type: 'system_health_changed'; data: { status: GuardianStatus } }
  | { type: 'configuration_updated'; data: { changes: Partial<GuardianConfig> } };

/**
 * 📊 GUARDIAN ANALYTICS
 */
export interface GuardianAnalytics {
  security: {
    threatsBlocked: number;
    attacksThwarted: number;
    vulnerabilitiesFixed: number;
    complianceScore: number;
    riskReduction: number;
  };
  performance: {
    averageResponseTime: number;
    systemOverhead: number;
    falsePositiveRate: number;
    detectionAccuracy: number;
    uptime: number;
  };
  users: {
    authenticatedSessions: number;
    failedLogins: number;
    suspiciousActivities: number;
    accessViolations: number;
  };
  trends: {
    threatTrends: Record<string, number[]>;
    performanceTrends: Record<string, number[]>;
    complianceTrends: Record<string, number[]>;
    timestamps: Date[];
  };
  insights: {
    topThreats: string[];
    vulnerableComponents: string[];
    riskAreas: string[];
    recommendations: string[];
  };
}
