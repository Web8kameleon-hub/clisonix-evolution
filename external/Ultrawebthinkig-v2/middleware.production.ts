/**
 * Web8 Industrial Middleware Stack
 * Production-ready middleware për security, performance, monitoring
 * 
 * @author UltraWeb Industrial Team
 * @version 8.0.0-MIDDLEWARE
 */

import { NextRequest, NextResponse } from 'next/server';
import { performanceMonitor } from './lib/performanceMonitor';
import { industrialErrorHandler, ErrorType, ErrorSeverity } from './lib/errorHandler';

// Rate limiting store
const rateLimitStore = new Map<string, { count: number; resetTime: number }>();

// Security headers configuration
const SECURITY_HEADERS = {
  'X-Frame-Options': 'DENY',
  'X-Content-Type-Options': 'nosniff',
  'X-XSS-Protection': '1; mode=block',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  'Content-Security-Policy': `
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    connect-src 'self' https://api.github.com https://en.wikipedia.org;
    font-src 'self';
    object-src 'none';
    media-src 'self';
    frame-src 'none';
  `.replace(/\s+/g, ' ').trim()
};

// Rate limiting configuration
const RATE_LIMITS: Record<string, { requests: number; window: number }> = {
  '/api/neural-search': { requests: 100, window: 15 * 60 * 1000 }, // 100 per 15 min
  '/api/health': { requests: 1000, window: 60 * 1000 }, // 1000 per minute
  default: { requests: 300, window: 15 * 60 * 1000 } // 300 per 15 min
};

export async function middleware(request: NextRequest) {
  const startTime = Date.now();
  const requestId = generateRequestId();
  const pathname = request.nextUrl.pathname;
  const clientIP = getClientIP(request);
  
  // Add request ID header
  const requestHeaders = new Headers(request.headers);
  requestHeaders.set('x-request-id', requestId);
  
  try {
    // Start performance tracking
    performanceMonitor.startRequest(requestId, pathname);
    
    // Rate limiting check
    const rateLimitResult = checkRateLimit(clientIP, pathname);
    if (!rateLimitResult.allowed) {
      performanceMonitor.endRequest(requestId, pathname, 429, { 
        rateLimited: true,
        remainingRequests: rateLimitResult.remaining,
        resetTime: rateLimitResult.resetTime
      });
      
      industrialErrorHandler.logError(
        new Error(`Rate limit exceeded for ${clientIP}`),
        ErrorType.RATE_LIMIT,
        ErrorSeverity.MEDIUM,
        { request, userId: undefined }
      );
      
      return new NextResponse('Rate limit exceeded', {
        status: 429,
        headers: {
          'X-RateLimit-Limit': rateLimitResult.limit.toString(),
          'X-RateLimit-Remaining': rateLimitResult.remaining.toString(),
          'X-RateLimit-Reset': rateLimitResult.resetTime.toString(),
          'Retry-After': Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000).toString()
        }
      });
    }
    
    // Create response with security headers
    const response = NextResponse.next({
      request: {
        headers: requestHeaders
      }
    });
    
    // Add security headers
    Object.entries(SECURITY_HEADERS).forEach(([key, value]) => {
      response.headers.set(key, value);
    });
    
    // Add performance and monitoring headers
    response.headers.set('X-Request-ID', requestId);
    response.headers.set('X-Powered-By', 'Web8-Ultra-Industrial');
    response.headers.set('X-Version', '8.0.0-PRODUCTION');
    response.headers.set('X-Response-Time', `${Date.now() - startTime}ms`);
    
    // Add rate limit headers
    response.headers.set('X-RateLimit-Limit', rateLimitResult.limit.toString());
    response.headers.set('X-RateLimit-Remaining', rateLimitResult.remaining.toString());
    response.headers.set('X-RateLimit-Reset', rateLimitResult.resetTime.toString());
    
    // CORS headers for API routes
    if (pathname.startsWith('/api/')) {
      response.headers.set('Access-Control-Allow-Origin', '*');
      response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Request-ID');
      response.headers.set('Access-Control-Expose-Headers', 'X-Request-ID, X-Response-Time');
    }
    
    // End performance tracking on successful response
    const responseTime = performanceMonitor.endRequest(
      requestId, 
      pathname, 
      response.status,
      { 
        userAgent: request.headers.get('user-agent'),
        referer: request.headers.get('referer')
      }
    );
    
    // Log successful request
    if (process.env.NODE_ENV === 'production') {
      }
    
    return response;
    
  } catch (error) {
    // Handle middleware errors
    const responseTime = performanceMonitor.endRequest(requestId, pathname, 500, { 
      error: true,
      errorMessage: error instanceof Error ? error.message : 'Unknown error'
    });
    
    const industrialError = industrialErrorHandler.logError(
      error,
      ErrorType.SYSTEM,
      ErrorSeverity.HIGH,
      { request, additionalContext: { middleware: true, responseTime } }
    );
    
    console.error(`❌ Middleware error: ${industrialError.id} - ${pathname} - ${responseTime}ms`);
    
    return new NextResponse('Internal Server Error', {
      status: 500,
      headers: {
        'X-Request-ID': requestId,
        'X-Error-ID': industrialError.id
      }
    });
  }
}

// Utility functions

function generateRequestId(): string {
  return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIP = request.headers.get('x-real-ip');
  const remoteAddr = request.headers.get('remote-addr');
  
  if (forwarded) {
    return forwarded.split(',')[0].trim();
  }
  
  return realIP || remoteAddr || 'unknown';
}

function checkRateLimit(clientIP: string, pathname: string): {
  allowed: boolean;
  remaining: number;
  resetTime: number;
  limit: number;
} {
  const now = Date.now();
  
  // Get rate limit config for this path
  const config = RATE_LIMITS[pathname] || RATE_LIMITS.default;
  const key = `${clientIP}:${pathname}`;
  
  let bucket = rateLimitStore.get(key);
  
  // Initialize or reset bucket if expired
  if (!bucket || now > bucket.resetTime) {
    bucket = {
      count: 0,
      resetTime: now + config.window
    };
  }
  
  // Check if request is allowed
  if (bucket.count >= config.requests) {
    rateLimitStore.set(key, bucket);
    return {
      allowed: false,
      remaining: 0,
      resetTime: bucket.resetTime,
      limit: config.requests
    };
  }
  
  // Increment count and allow request
  bucket.count++;
  rateLimitStore.set(key, bucket);
  
  return {
    allowed: true,
    remaining: config.requests - bucket.count,
    resetTime: bucket.resetTime,
    limit: config.requests
  };
}

// Cleanup old rate limit entries periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, bucket] of rateLimitStore.entries()) {
    if (now > bucket.resetTime) {
      rateLimitStore.delete(key);
    }
  }
}, 5 * 60 * 1000); // Every 5 minutes

// Middleware configuration
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    '/((?!_next/static|_next/image|favicon.ico|public/).*)',
  ],
};
