import { NextRequest } from 'next/server';
import crypto from 'crypto';

// Security Configuration Types
interface SecurityConfig {
  rateLimit: {
    windowMs: number;
    max: number;
    skipSuccessfulRequests: boolean;
    skipFailedRequests: boolean;
  };
  bruteForce: {
    freeRetries: number;
    minWait: number;
    maxWait: number;
    lifetime: number;
  };
  encryption: {
    algorithm: string;
    keyLength: number;
    ivLength: number;
  };
  validation: {
    maxInputLength: number;
    allowedFileTypes: string[];
    maxFileSize: number;
  };
}

interface RateLimitEntry {
  count: number;
  resetTime: number;
  blocked: boolean;
}

interface BruteForceEntry {
  attempts: number;
  lastAttempt: number;
  blockedUntil: number;
}

interface SecurityAuditLog {
  timestamp: number;
  event: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  details: Record<string, any>;
  blocked: boolean;
}

class SecurityManager {
  private config: SecurityConfig;
  private rateLimitStore: Map<string, RateLimitEntry> = new Map();
  private bruteForceStore: Map<string, BruteForceEntry> = new Map();
  private auditLogs: SecurityAuditLog[] = [];
  private encryptionKey: Buffer;
  private readonly maxAuditLogs = 10000;

  constructor() {
    this.config = {
      rateLimit: {
        windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000'), // 15 minutes
        max: parseInt(process.env.RATE_LIMIT_MAX || '100'),
        skipSuccessfulRequests: false,
        skipFailedRequests: false,
      },
      bruteForce: {
        freeRetries: parseInt(process.env.BRUTE_FORCE_FREE_RETRIES || '5'),
        minWait: parseInt(process.env.BRUTE_FORCE_MIN_WAIT || '300000'), // 5 minutes
        maxWait: parseInt(process.env.BRUTE_FORCE_MAX_WAIT || '3600000'), // 1 hour
        lifetime: parseInt(process.env.BRUTE_FORCE_LIFETIME || '86400000'), // 24 hours
      },
      encryption: {
        algorithm: 'aes-256-gcm',
        keyLength: 32,
        ivLength: 16,
      },
      validation: {
        maxInputLength: parseInt(process.env.MAX_INPUT_LENGTH || '10000'),
        allowedFileTypes: (process.env.ALLOWED_FILE_TYPES || 'jpg,jpeg,png,gif,pdf,doc,docx').split(','),
        maxFileSize: parseInt(process.env.MAX_FILE_SIZE || '10485760'), // 10MB
      },
    };

    // Initialize encryption key
    this.encryptionKey = Buffer.from(
      process.env.ENCRYPTION_KEY || crypto.randomBytes(32).toString('hex'),
      'hex'
    );
  }

  // Rate Limiting
  checkRateLimit(identifier: string, endpoint?: string): { allowed: boolean; remaining: number; resetTime: number } {
    const key = endpoint ? `${identifier}:${endpoint}` : identifier;
    const now = Date.now();
    
    let entry = this.rateLimitStore.get(key);
    
    if (!entry || now > entry.resetTime) {
      entry = {
        count: 0,
        resetTime: now + this.config.rateLimit.windowMs,
        blocked: false,
      };
    }

    entry.count++;
    
    if (entry.count > this.config.rateLimit.max) {
      entry.blocked = true;
      this.logSecurityEvent({
        event: 'rate_limit_exceeded',
        severity: 'medium',
        source: identifier,
        details: { endpoint, count: entry.count, limit: this.config.rateLimit.max },
        blocked: true,
      });
    }

    this.rateLimitStore.set(key, entry);

    return {
      allowed: !entry.blocked,
      remaining: Math.max(0, this.config.rateLimit.max - entry.count),
      resetTime: entry.resetTime,
    };
  }

  // Brute Force Protection
  checkBruteForce(identifier: string, success: boolean = false): { allowed: boolean; blockedUntil?: number } {
    const now = Date.now();
    let entry = this.bruteForceStore.get(identifier);

    if (!entry) {
      entry = {
        attempts: 0,
        lastAttempt: now,
        blockedUntil: 0,
      };
    }

    // Clear old entries
    if (now - entry.lastAttempt > this.config.bruteForce.lifetime) {
      entry.attempts = 0;
      entry.blockedUntil = 0;
    }

    // Check if currently blocked
    if (entry.blockedUntil > now) {
      this.logSecurityEvent({
        event: 'brute_force_blocked_attempt',
        severity: 'high',
        source: identifier,
        details: { blockedUntil: entry.blockedUntil, attempts: entry.attempts },
        blocked: true,
      });
      
      return { allowed: false, blockedUntil: entry.blockedUntil };
    }

    if (success) {
      // Reset on successful attempt
      this.bruteForceStore.delete(identifier);
      return { allowed: true };
    }

    // Failed attempt
    entry.attempts++;
    entry.lastAttempt = now;

    if (entry.attempts > this.config.bruteForce.freeRetries) {
      const waitTime = Math.min(
        this.config.bruteForce.minWait * Math.pow(2, entry.attempts - this.config.bruteForce.freeRetries),
        this.config.bruteForce.maxWait
      );
      
      entry.blockedUntil = now + waitTime;
      
      this.logSecurityEvent({
        event: 'brute_force_protection_triggered',
        severity: 'high',
        source: identifier,
        details: { attempts: entry.attempts, blockedFor: waitTime },
        blocked: true,
      });
    }

    this.bruteForceStore.set(identifier, entry);
    
    return {
      allowed: entry.blockedUntil <= now,
      blockedUntil: entry.blockedUntil > now ? entry.blockedUntil : undefined,
    };
  }

  // Input Validation
  validateInput(input: string, type: 'text' | 'email' | 'url' | 'json' = 'text'): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Length check
    if (input.length > this.config.validation.maxInputLength) {
      errors.push(`Input exceeds maximum length of ${this.config.validation.maxInputLength} characters`);
    }

    // SQL Injection patterns
    const sqlPatterns = [
      /(\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b)/gi,
      /(--|\/\*|\*\/|;|'|"|`)/g,
      /(\b(or|and)\b\s*\d+\s*=\s*\d+)/gi,
    ];

    sqlPatterns.forEach((pattern, index) => {
      if (pattern.test(input)) {
        errors.push(`Potential SQL injection detected (pattern ${index + 1})`);
      }
    });

    // XSS patterns
    const xssPatterns = [
      /<script[^>]*>.*?<\/script>/gi,
      /javascript:/gi,
      /on\w+\s*=/gi,
      /<iframe[^>]*>/gi,
      /<object[^>]*>/gi,
      /<embed[^>]*>/gi,
    ];

    xssPatterns.forEach((pattern, index) => {
      if (pattern.test(input)) {
        errors.push(`Potential XSS attack detected (pattern ${index + 1})`);
      }
    });

    // Type-specific validation
    switch (type) {
      case 'email':
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(input)) {
          errors.push('Invalid email format');
        }
        break;
      case 'url':
        try {
          new URL(input);
        } catch {
          errors.push('Invalid URL format');
        }
        break;
      case 'json':
        try {
          JSON.parse(input);
        } catch {
          errors.push('Invalid JSON format');
        }
        break;
    }

    if (errors.length > 0) {
      this.logSecurityEvent({
        event: 'input_validation_failed',
        severity: 'medium',
        source: 'validation',
        details: { inputType: type, errors, inputLength: input.length },
        blocked: true,
      });
    }

    return { valid: errors.length === 0, errors };
  }

  // File Upload Validation
  validateFile(filename: string, mimetype: string, size: number): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Size check
    if (size > this.config.validation.maxFileSize) {
      errors.push(`File size exceeds limit of ${this.config.validation.maxFileSize} bytes`);
    }

    // Extension check
    const extension = filename.split('.').pop()?.toLowerCase();
    if (!extension || !this.config.validation.allowedFileTypes.includes(extension)) {
      errors.push(`File type '${extension}' is not allowed`);
    }

    // MIME type check (basic)
    const allowedMimeTypes = [
      'image/jpeg', 'image/png', 'image/gif',
      'application/pdf',
      'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ];

    if (!allowedMimeTypes.includes(mimetype)) {
      errors.push(`MIME type '${mimetype}' is not allowed`);
    }

    if (errors.length > 0) {
      this.logSecurityEvent({
        event: 'file_validation_failed',
        severity: 'medium',
        source: 'file_upload',
        details: { filename, mimetype, size, errors },
        blocked: true,
      });
    }

    return { valid: errors.length === 0, errors };
  }

  // Encryption/Decryption
  encrypt(text: string): { encrypted: string; iv: string; tag: string } {
    const iv = crypto.randomBytes(this.config.encryption.ivLength);
    const cipher = crypto.createCipheriv(this.config.encryption.algorithm, this.encryptionKey, iv);
    
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    return {
      encrypted,
      iv: iv.toString('hex'),
      tag: '', // For compatibility
    };
  }

  decrypt(encrypted: string, iv: string, tag: string): string {
    const decipher = crypto.createDecipheriv(
      this.config.encryption.algorithm, 
      this.encryptionKey, 
      Buffer.from(iv, 'hex')
    );
    
    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }

  // Request Analysis
  analyzeRequest(request: NextRequest): { risk: 'low' | 'medium' | 'high'; reasons: string[] } {
    const reasons: string[] = [];
    let riskLevel: 'low' | 'medium' | 'high' = 'low';

    // Check user agent
    const userAgent = request.headers.get('user-agent') || '';
    if (!userAgent || userAgent.length < 10) {
      reasons.push('Missing or suspicious user agent');
      riskLevel = 'medium';
    }

    // Check for common bot patterns
    const botPatterns = ['bot', 'crawler', 'spider', 'scraper', 'automated'];
    if (botPatterns.some(pattern => userAgent.toLowerCase().includes(pattern))) {
      reasons.push('Bot-like user agent detected');
      if (riskLevel === 'low') riskLevel = 'medium';
    }

    // Check for suspicious headers
    const suspiciousHeaders = ['x-forwarded-for', 'x-real-ip', 'proxy-authorization'];
    suspiciousHeaders.forEach(header => {
      if (request.headers.get(header)) {
        reasons.push(`Suspicious header detected: ${header}`);
        if (riskLevel === 'low') riskLevel = 'medium';
      }
    });

    // Check request frequency (basic check)
    const clientIP = this.getClientIP(request);
    const recentRequests = this.auditLogs.filter(
      log => log.source === clientIP && 
             log.timestamp > Date.now() - 60000 && // Last minute
             log.event.includes('request')
    ).length;

    if (recentRequests > 30) {
      reasons.push('High frequency requests detected');
      riskLevel = 'high';
    }

    return { risk: riskLevel, reasons };
  }

  // Utility Methods
  getClientIP(request: NextRequest): string {
    return request.headers.get('x-forwarded-for')?.split(',')[0] ||
           request.headers.get('x-real-ip') ||
           request.ip ||
           'unknown';
  }

  generateSecureToken(length: number = 32): string {
    return crypto.randomBytes(length).toString('hex');
  }

  hashPassword(password: string): { hash: string; salt: string } {
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
    return { hash, salt };
  }

  verifyPassword(password: string, hash: string, salt: string): boolean {
    const computed = crypto.pbkdf2Sync(password, salt, 100000, 64, 'sha512').toString('hex');
    return computed === hash;
  }

  // Audit Logging
  private logSecurityEvent(event: Omit<SecurityAuditLog, 'timestamp'>): void {
    const logEntry: SecurityAuditLog = {
      timestamp: Date.now(),
      ...event,
    };

    this.auditLogs.push(logEntry);

    // Keep only recent logs
    if (this.auditLogs.length > this.maxAuditLogs) {
      this.auditLogs = this.auditLogs.slice(-this.maxAuditLogs);
    }

    // Log critical events to console
    if (event.severity === 'critical') {
      console.error('🚨 CRITICAL SECURITY EVENT:', logEntry);
    }
  }

  // Security Reporting
  getSecurityReport(timeWindow: number = 3600000): {
    summary: any;
    events: SecurityAuditLog[];
    threats: any;
  } {
    const now = Date.now();
    const cutoff = now - timeWindow;
    const recentEvents = this.auditLogs.filter(log => log.timestamp > cutoff);

    const eventCounts = recentEvents.reduce((acc, event) => {
      acc[event.event] = (acc[event.event] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const severityCounts = recentEvents.reduce((acc, event) => {
      acc[event.severity] = (acc[event.severity] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const topThreats = Object.entries(eventCounts)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 10);

    return {
      summary: {
        totalEvents: recentEvents.length,
        blockedEvents: recentEvents.filter(e => e.blocked).length,
        severityBreakdown: severityCounts,
        timeWindow: timeWindow / 1000 / 60, // minutes
      },
      events: recentEvents.slice(-100), // Last 100 events
      threats: {
        topEventTypes: topThreats,
        activeBruteForce: this.bruteForceStore.size,
        activeRateLimits: Array.from(this.rateLimitStore.values()).filter(e => e.blocked).length,
      },
    };
  }

  // Cleanup old entries
  cleanup(): void {
    const now = Date.now();
    
    // Clean rate limit entries
    this.rateLimitStore.forEach((entry, key) => {
      if (now > entry.resetTime) {
        this.rateLimitStore.delete(key);
      }
    });

    // Clean brute force entries
    this.bruteForceStore.forEach((entry, key) => {
      if (now - entry.lastAttempt > this.config.bruteForce.lifetime) {
        this.bruteForceStore.delete(key);
      }
    });

    // Clean old audit logs
    const cutoff = now - 86400000; // 24 hours
    this.auditLogs = this.auditLogs.filter(log => log.timestamp > cutoff);
  }
}

// Singleton instance
export const securityManager = new SecurityManager();
export default securityManager;
