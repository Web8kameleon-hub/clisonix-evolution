/**
 * EuroWeb AGI Module Guard - Siguria dhe kontrolli i moduleve AGI
 * @module AGIModuleGuard
 * @author EuroWeb Development Team
 * @version 8.0.0 Industrial
 */

import type { AGIModule, EuroWebConfig } from '../agi/types';

export class AGIModuleGuard {
  private allowedModules: Set<string> = new Set();
  private trustedModules: Map<string, TrustedModule> = new Map();
  private securityLevel: 'standard' | 'high' | 'military' | 'post-quantum';
  private moduleLimits: ModuleLimits;
  private auditLog: SecurityEvent[] = [];
  
  constructor(config: Partial<EuroWebConfig> = {}) {
    this.securityLevel = config.securityLevel || 'standard';
    this.moduleLimits = this.getDefaultLimits();
    this.initializeDefaultModules();
    this.startSecurityMonitoring();
  }

  private initializeDefaultModules(): void {
    // Core EuroWeb modules që janë të sigurta by default
    const coreModules = [
      'mind', 'sense', 'planner', 'response', 'monitor',
      'echo-engine', 'orchestrator', 'memory-layer',
      'signal-trace', 'intelli-context', 'navigation',
      'mesh-network', 'ddos-protection', 'governance'
    ];

    coreModules.forEach(module => {
      this.allowedModules.add(module);
      this.trustedModules.set(module, {
        name: module,
        trustLevel: 'core',
        permissions: this.getCorePermissions(),
        lastValidated: Date.now(),
        validationHash: this.generateValidationHash(module)
      });
    });

    console.log(`🛡️ AGIModuleGuard: ${coreModules.length} core modules u autorizuan`);
  }

  /**
   * Validate Module - Kontrollon nëse moduli është i sigurt
   */
  public validateModule(moduleName: string, moduleCode?: string): SecurityValidation {
    const validation: SecurityValidation = {
      isValid: false,
      moduleName,
      timestamp: Date.now(),
      securityLevel: this.securityLevel,
      threats: [],
      recommendations: []
    };

    try {
      // 1. Check if module is in allowed list
      if (!this.allowedModules.has(moduleName)) {
        validation.threats.push('Module not in allowed list');
        validation.recommendations.push('Add module to authorized list first');
        this.logSecurityEvent('unauthorized_module_access', moduleName);
        return validation;
      }

      // 2. Check trusted module status
      const trustedModule = this.trustedModules.get(moduleName);
      if (!trustedModule) {
        validation.threats.push('Module not in trusted registry');
        validation.recommendations.push('Register module in trusted registry');
        return validation;
      }

      // 3. Validate module hash if code is provided
      if (moduleCode) {
        const currentHash = this.generateValidationHash(moduleCode);
        if (currentHash !== trustedModule.validationHash) {
          validation.threats.push('Module hash mismatch - possible tampering');
          validation.recommendations.push('Re-validate module integrity');
          this.logSecurityEvent('module_tampering_detected', moduleName);
          return validation;
        }
      }

      // 4. Check security level compatibility
      if (!this.isSecurityLevelCompatible(trustedModule.trustLevel)) {
        validation.threats.push('Module security level incompatible');
        validation.recommendations.push('Upgrade module security or lower system security level');
        return validation;
      }

      // 5. Check resource limits
      const resourceCheck = this.checkResourceLimits(moduleName);
      if (!resourceCheck.allowed) {
        validation.threats.push('Module exceeds resource limits');
        validation.recommendations.push(`Reduce usage: ${resourceCheck.reason}`);
        return validation;
      }

      validation.isValid = true;
      validation.recommendations.push('Module validated successfully');
      this.logSecurityEvent('module_validated', moduleName);
      
      return validation;

    } catch (error: any) {
      validation.threats.push(`Validation error: ${error.message}`);
      this.logSecurityEvent('validation_error', moduleName, error.message);
      return validation;
    }
  }

  /**
   * Add Authorized Module - Shton modul të ri në listën e autorizuar
   */
  public addAuthorizedModule(
    moduleName: string, 
    module: AGIModule,
    trustLevel: TrustLevel = 'third-party'
  ): boolean {
    try {
      // Validate module structure
      if (!this.validateModuleStructure(module)) {
        throw new Error('Invalid module structure');
      }

      // Check permissions
      const permissions = this.getPermissionsForTrustLevel(trustLevel);
      
      // Add to allowed modules
      this.allowedModules.add(moduleName);
      
      // Add to trusted registry
      this.trustedModules.set(moduleName, {
        name: moduleName,
        trustLevel,
        permissions,
        lastValidated: Date.now(),
        validationHash: this.generateValidationHash(module.toString())
      });

      this.logSecurityEvent('module_authorized', moduleName);
      console.log(`🛡️ AGIModuleGuard: Moduli '${moduleName}' u autorizua me trust level '${trustLevel}'`);
      
      return true;

    } catch (error: any) {
      this.logSecurityEvent('authorization_failed', moduleName, error.message);
      console.error(`❌ AGIModuleGuard: Dështoi autorizimi i modulit '${moduleName}': ${error.message}`);
      return false;
    }
  }

  /**
   * Revoke Module Access - Heq aksesin e modulit
   */
  public revokeModuleAccess(moduleName: string, reason: string): void {
    if (this.isCoreModule(moduleName)) {
      console.warn(`⚠️ Cannot revoke core module: ${moduleName}`);
      return;
    }

    this.allowedModules.delete(moduleName);
    this.trustedModules.delete(moduleName);
    
    this.logSecurityEvent('module_revoked', moduleName, reason);
    console.log(`🛡️ AGIModuleGuard: Aksesi i modulit '${moduleName}' u hoq: ${reason}`);
  }

  /**
   * Get Security Report - Raporti i sigurisë
   */
  public getSecurityReport(): SecurityReport {
    return {
      totalModules: this.allowedModules.size,
      trustedModules: this.trustedModules.size,
      securityLevel: this.securityLevel,
      recentEvents: this.auditLog.slice(-10),
      resourceUsage: this.getResourceUsage(),
      lastAudit: Date.now(),
      threats: this.detectActiveThreats(),
      recommendations: this.generateSecurityRecommendations()
    };
  }

  private getDefaultLimits(): ModuleLimits {
    const limits = {
      standard: { maxModules: 50, maxMemory: 100, maxCpu: 70 },
      high: { maxModules: 30, maxMemory: 80, maxCpu: 50 },
      military: { maxModules: 15, maxMemory: 60, maxCpu: 30 },
      'post-quantum': { maxModules: 10, maxMemory: 40, maxCpu: 20 }
    };
    
    return limits[this.securityLevel];
  }

  private getCorePermissions(): ModulePermissions {
    return {
      canAccessMemory: true,
      canModifyState: true,
      canNetworkAccess: true,
      canFileAccess: true,
      canExecuteCode: true,
      securityLevel: 'core'
    };
  }

  private getPermissionsForTrustLevel(trustLevel: TrustLevel): ModulePermissions {
    const permissions = {
      core: {
        canAccessMemory: true,
        canModifyState: true,
        canNetworkAccess: true,
        canFileAccess: true,
        canExecuteCode: true,
        securityLevel: 'core'
      },
      trusted: {
        canAccessMemory: true,
        canModifyState: false,
        canNetworkAccess: true,
        canFileAccess: false,
        canExecuteCode: true,
        securityLevel: 'trusted'
      },
      'third-party': {
        canAccessMemory: false,
        canModifyState: false,
        canNetworkAccess: false,
        canFileAccess: false,
        canExecuteCode: false,
        securityLevel: 'restricted'
      }
    };

    return permissions[trustLevel];
  }

  private generateValidationHash(input: string): string {
    // Simple hash function - në production do të përdoret crypto
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(16);
  }

  private validateModuleStructure(module: AGIModule): boolean {
    return !!(
      module.id &&
      module.name &&
      module.type &&
      typeof module.execute === 'function' &&
      typeof module.validate === 'function' &&
      typeof module.getMetrics === 'function'
    );
  }

  private isSecurityLevelCompatible(trustLevel: TrustLevel): boolean {
    const compatibility = {
      standard: ['core', 'trusted', 'third-party'],
      high: ['core', 'trusted'],
      military: ['core'],
      'post-quantum': ['core']
    };
    
    return compatibility[this.securityLevel].includes(trustLevel);
  }

  private checkResourceLimits(moduleName: string): ResourceCheck {
    // Simulate resource checking
    return {
      allowed: true,
      reason: 'Within limits',
      usage: {
        memory: Math.random() * 30,
        cpu: Math.random() * 20,
        modules: this.allowedModules.size
      }
    };
  }

  private isCoreModule(moduleName: string): boolean {
    const trustedModule = this.trustedModules.get(moduleName);
    return trustedModule?.trustLevel === 'core';
  }

  private logSecurityEvent(
    type: SecurityEventType, 
    moduleName: string, 
    details?: string
  ): void {
    const event: SecurityEvent = {
      type,
      moduleName,
      details,
      timestamp: Date.now(),
      securityLevel: this.securityLevel
    };

    this.auditLog.push(event);
    
    // Keep only last 1000 events
    if (this.auditLog.length > 1000) {
      this.auditLog = this.auditLog.slice(-1000);
    }
  }

  private startSecurityMonitoring(): void {
    setInterval(() => {
      this.performSecurityAudit();
    }, 60000); // Every minute
  }

  private performSecurityAudit(): void {
    // Perform periodic security checks
    const threats = this.detectActiveThreats();
    if (threats.length > 0) {
      console.warn(`⚠️ Security audit detected ${threats.length} threats`);
    }
  }

  private detectActiveThreats(): string[] {
    const threats: string[] = [];
    
    // Check for suspicious activity
    const recentEvents = this.auditLog.slice(-100);
    const failedValidations = recentEvents.filter(e => e.type === 'validation_error').length;
    
    if (failedValidations > 10) {
      threats.push('High number of validation failures');
    }

    return threats;
  }

  private generateSecurityRecommendations(): string[] {
    const recommendations: string[] = [];
    
    if (this.allowedModules.size > this.moduleLimits.maxModules) {
      recommendations.push('Reduce number of active modules');
    }
    
    if (this.securityLevel === 'standard') {
      recommendations.push('Consider upgrading to higher security level');
    }

    return recommendations;
  }

  private getResourceUsage(): ResourceUsage {
    return {
      memory: Math.random() * this.moduleLimits.maxMemory,
      cpu: Math.random() * this.moduleLimits.maxCpu,
      modules: this.allowedModules.size,
      maxModules: this.moduleLimits.maxModules
    };
  }
}

// Type definitions
type TrustLevel = 'core' | 'trusted' | 'third-party';
type SecurityEventType = 'module_authorized' | 'module_revoked' | 'unauthorized_module_access' | 'module_tampering_detected' | 'validation_error' | 'module_validated' | 'authorization_failed';

interface TrustedModule {
  name: string;
  trustLevel: TrustLevel;
  permissions: ModulePermissions;
  lastValidated: number;
  validationHash: string;
}

interface ModulePermissions {
  canAccessMemory: boolean;
  canModifyState: boolean;
  canNetworkAccess: boolean;
  canFileAccess: boolean;
  canExecuteCode: boolean;
  securityLevel: string;
}

interface SecurityValidation {
  isValid: boolean;
  moduleName: string;
  timestamp: number;
  securityLevel: string;
  threats: string[];
  recommendations: string[];
}

interface SecurityEvent {
  type: SecurityEventType;
  moduleName: string;
  details?: string;
  timestamp: number;
  securityLevel: string;
}

interface ModuleLimits {
  maxModules: number;
  maxMemory: number;
  maxCpu: number;
}

interface ResourceCheck {
  allowed: boolean;
  reason: string;
  usage: ResourceUsage;
}

interface ResourceUsage {
  memory: number;
  cpu: number;
  modules: number;
  maxModules?: number;
}

interface SecurityReport {
  totalModules: number;
  trustedModules: number;
  securityLevel: string;
  recentEvents: SecurityEvent[];
  resourceUsage: ResourceUsage;
  lastAudit: number;
  threats: string[];
  recommendations: string[];
}

// Create and export global instance
export const agiModuleGuard = new AGIModuleGuard();

// Export types
export type { 
  SecurityValidation, 
  SecurityReport, 
  TrustedModule, 
  ModulePermissions,
  TrustLevel 
};
