// core/monitoring/AuditLogger.ts
/**
 * 📊 AUDIT LOGGER
 * Comprehensive Medical Activity Logging
 */

export interface AuditEntry {
  id: string;
  timestamp: Date;
  action: string;
  details: any;
  ipAddress: string;
  userAgent: string;
  sessionId?: string;
  professionalId?: string;
}

export class AuditLogger {
  private auditTrail: AuditEntry[] = [];

  createEntry(action: string, details: any, options?: {
    ipAddress?: string;
    userAgent?: string;
  }): AuditEntry {
    return {
      id: `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date(),
      action,
      details,
      ipAddress: options?.ipAddress || 'unknown',
      userAgent: options?.userAgent || 'unknown'
    };
  }

  async logViolation(type: string, details: any): Promise<void> {
    const entry = this.createEntry(`security_violation_${type}`, details);
    this.auditTrail.push(entry);
    console.warn('[AUDIT] Security Violation:', entry);
  }

  async logSuccess(action: string, details: any): Promise<void> {
    const entry = this.createEntry(`success_${action}`, details);
    this.auditTrail.push(entry);
    console.log('[AUDIT] Success:', entry);
  }

  async logError(action: string, error: any, context?: any): Promise<void> {
    const entry = this.createEntry(`error_${action}`, { error: error.message, context });
    this.auditTrail.push(entry);
    console.error('[AUDIT] Error:', entry);
  }

  async logSessionStart(session: any): Promise<void> {
    const entry = this.createEntry('session_start', {
      sessionId: session.sessionId,
      professionalId: session.professional?.id
    });
    this.auditTrail.push(entry);
    console.log('[AUDIT] Session Started:', entry);
  }

  async logComponentAccess(component: string, sessionId: string): Promise<void> {
    const entry = this.createEntry('component_access', {
      component,
      sessionId
    });
    this.auditTrail.push(entry);
    console.log('[AUDIT] Component Access:', entry);
  }

  getAuditTrail(): AuditEntry[] {
    return [...this.auditTrail];
  }

  async exportAuditTrail(): Promise<string> {
    return JSON.stringify(this.auditTrail, null, 2);
  }
}
