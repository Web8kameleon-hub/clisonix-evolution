/**
 * Clisonix Login Security Module
 * Implements rate limiting, account lockout, IP tracking, and strong authentication
 */

interface LoginAttempt {
  timestamp: number;
  ip: string;
  success: boolean;
  email: string;
}

interface LockedAccount {
  email: string;
  lockedUntil: number;
  failedAttempts: number;
  lastAttemptIp: string;
}

// In-memory storage (should use Redis in production)
const loginAttempts: LoginAttempt[] = [];
const lockedAccounts = new Map<string, LockedAccount>();
const ipRateLimits = new Map<string, { count: number; resetTime: number }>();

// Configuration
const MAX_FAILED_ATTEMPTS = 5;
const LOCKOUT_DURATION_MS = 15 * 60 * 1000; // 15 minutes
const RATE_LIMIT_WINDOW_MS = 5 * 60 * 1000; // 5 minutes
const MAX_REQUESTS_PER_IP = 20; // per window

/**
 * Check if email account is locked due to too many failed attempts
 */
export function isAccountLocked(email: string): boolean {
  const locked = lockedAccounts.get(email.toLowerCase());
  if (!locked) return false;

  if (Date.now() > locked.lockedUntil) {
    lockedAccounts.delete(email.toLowerCase());
    return false;
  }

  return true;
}

/**
 * Check IP-based rate limiting
 */
export function checkIpRateLimit(ip: string): boolean {
  const limit = ipRateLimits.get(ip);

  if (!limit || Date.now() > limit.resetTime) {
    ipRateLimits.set(ip, {
      count: 1,
      resetTime: Date.now() + RATE_LIMIT_WINDOW_MS,
    });
    return true;
  }

  if (limit.count >= MAX_REQUESTS_PER_IP) {
    return false;
  }

  limit.count++;
  return true;
}

/**
 * Record a failed login attempt
 */
export function recordFailedLogin(email: string, ip: string): void {
  const emailLower = email.toLowerCase();

  loginAttempts.push({
    timestamp: Date.now(),
    ip,
    success: false,
    email: emailLower,
  });

  // Check failed attempts in last hour
  const oneHourAgo = Date.now() - 60 * 60 * 1000;
  const recentFailures = loginAttempts.filter(
    (attempt) =>
      attempt.email === emailLower &&
      !attempt.success &&
      attempt.timestamp > oneHourAgo,
  ).length;

  if (recentFailures >= MAX_FAILED_ATTEMPTS) {
    lockedAccounts.set(emailLower, {
      email: emailLower,
      lockedUntil: Date.now() + LOCKOUT_DURATION_MS,
      failedAttempts: recentFailures,
      lastAttemptIp: ip,
    });
  }

  // Clean up old attempts
  while (loginAttempts.length > 10000) {
    loginAttempts.shift();
  }
}

/**
 * Record a successful login
 */
export function recordSuccessfulLogin(email: string, ip: string): void {
  const emailLower = email.toLowerCase();

  loginAttempts.push({
    timestamp: Date.now(),
    ip,
    success: true,
    email: emailLower,
  });

  // Clear failed attempts on success
  lockedAccounts.delete(emailLower);
}

/**
 * Get login history for an email
 */
export function getLoginHistory(
  email: string,
  hours: number = 24,
): LoginAttempt[] {
  const emailLower = email.toLowerCase();
  const cutoffTime = Date.now() - hours * 60 * 60 * 1000;

  return loginAttempts.filter(
    (attempt) => attempt.email === emailLower && attempt.timestamp > cutoffTime,
  );
}

/**
 * Get account lock status
 */
export function getAccountLockStatus(email: string): {
  isLocked: boolean;
  lockedUntil?: number;
  failedAttempts?: number;
} {
  const emailLower = email.toLowerCase();
  const locked = lockedAccounts.get(emailLower);

  if (!locked || Date.now() > locked.lockedUntil) {
    if (locked) {
      lockedAccounts.delete(emailLower);
    }
    return { isLocked: false };
  }

  return {
    isLocked: true,
    lockedUntil: locked.lockedUntil,
    failedAttempts: locked.failedAttempts,
  };
}

/**
 * Validate password strength
 */
export function validatePasswordStrength(password: string): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (password.length < 12) {
    errors.push("Password must be at least 12 characters long");
  }

  if (!/[A-Z]/.test(password)) {
    errors.push("Password must contain at least one uppercase letter");
  }

  if (!/[a-z]/.test(password)) {
    errors.push("Password must contain at least one lowercase letter");
  }

  if (!/[0-9]/.test(password)) {
    errors.push("Password must contain at least one number");
  }

  if (!/[!@#$%^&*()_\-+=\[\]{};:'",.<>?/\\|`~]/.test(password)) {
    errors.push("Password must contain at least one special character");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Check if IP is suspicious (changed since last login)
 */
export function isSuspiciousIp(email: string, currentIp: string): boolean {
  const emailLower = email.toLowerCase();
  const recentLogins = loginAttempts
    .filter(
      (attempt) =>
        attempt.email === emailLower &&
        attempt.success &&
        attempt.timestamp > Date.now() - 30 * 24 * 60 * 60 * 1000, // Last 30 days
    )
    .sort((a, b) => b.timestamp - a.timestamp);

  if (recentLogins.length === 0) return false; // First login, not suspicious

  const previousLogin = recentLogins[0];
  if (!previousLogin) {
    return false;
  }

  const previousIp = previousLogin.ip;
  return previousIp !== currentIp && recentLogins.length > 0;
}

/**
 * Export login metrics for monitoring
 */
export function getSecurityMetrics(): {
  totalAttempts: number;
  lockedAccounts: number;
  failedAttemptsLast24h: number;
  suspiciousIps: number;
} {
  const now = Date.now();
  const oneDayAgo = now - 24 * 60 * 60 * 1000;

  const failedAttemptsLast24h = loginAttempts.filter(
    (a) => !a.success && a.timestamp > oneDayAgo,
  ).length;

  const suspiciousIps = new Set(
    loginAttempts
      .filter((a) => !a.success && a.timestamp > oneDayAgo)
      .map((a) => a.ip),
  ).size;

  return {
    totalAttempts: loginAttempts.length,
    lockedAccounts: lockedAccounts.size,
    failedAttemptsLast24h,
    suspiciousIps,
  };
}
