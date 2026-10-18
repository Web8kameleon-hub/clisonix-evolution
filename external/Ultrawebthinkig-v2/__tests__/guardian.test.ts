/**
 * Guardian Security System Tests
 * Comprehensive testing for DDoS protection and threat detection
 * 
 * @version 8.0.0
 * @author Ledjan Ahmati
 * @contact dealsjona@gmail.com
 */

import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';
import { Request, Response } from 'express';
import { Guardian } from '../backend/guardian/Guardian-web8';

// Mock express objects
const mockRequest = (overrides = {}) => ({
  method: 'GET',
  url: '/test',
  path: '/test',
  headers: {},
  body: {},
  query: {},
  params: {},
  ip: '127.0.0.1',
  connection: { remoteAddress: '127.0.0.1' },
  get: vi.fn(),
  on: vi.fn(),
  ...overrides
}) as unknown as Request;

const mockResponse = () => {
  const res = {
    status: vi.fn().mockReturnThis(),
    json: vi.fn().mockReturnThis(),
    setHeader: vi.fn().mockReturnThis(),
    end: vi.fn()
  } as unknown as Response;
  return res;
};

const mockNext = vi.fn();

describe('Guardian Security System', () => {
  let guardian: ReturnType<typeof Guardian>;

  beforeEach(() => {
    vi.clearAllMocks();
    guardian = Guardian({
      maxRequestsPerMinute: 10,
      maxPayloadSize: 1024,
      blockDuration: 60000,
      logPath: './test-logs/guardian.log',
      blocklistPath: './test-data/blocklist.json'
    });
  });

  describe('Basic Functionality', () => {
    it('should initialize with default configuration', () => {
      const defaultGuardian = Guardian();
      expect(defaultGuardian).toBeDefined();
      const stats = defaultGuardian.getStats();
      expect(stats.totalRequests).toBe(0);
      expect(stats.blockedRequests).toBe(0);
    });

    it('should create middleware function', () => {
      const middleware = guardian.middleware();
      expect(typeof middleware).toBe('function');
    });

    it('should allow normal requests', () => {
      const req = mockRequest();
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(mockNext).toHaveBeenCalled();
      expect(res.status).not.toHaveBeenCalled();
    });
  });

  describe('Rate Limiting', () => {
    it('should block IPs exceeding rate limit', () => {
      const req = mockRequest({ ip: '192.168.1.100' });
      const res = mockResponse();
      const middleware = guardian.middleware();

      // Simulate multiple requests from same IP
      for (let i = 0; i < 12; i++) {
        middleware(req, res, mockNext);
      }

      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Access Denied',
          reason: 'Rate Limit Exceeded'
        })
      );
    });

    it('should track unique IPs correctly', () => {
      const middleware = guardian.middleware();

      // Simulate requests from different IPs
      ['192.168.1.1', '192.168.1.2', '192.168.1.3'].forEach(ip => {
        const req = mockRequest({ ip });
        const res = mockResponse();
        middleware(req, res, mockNext);
      });

      const stats = guardian.getStats();
      expect(stats.uniqueIPs).toBeGreaterThan(0);
    });
  });

  describe('SQL Injection Detection', () => {
    it('should detect SQL injection in query parameters', () => {
      const req = mockRequest({
        query: { search: "'; DROP TABLE users; --" },
        ip: '192.168.1.200'
      });
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          reason: 'Security Violation'
        })
      );
    });

    it('should detect SQL injection in request body', () => {
      const req = mockRequest({
        body: { username: 'admin', password: "' OR '1'='1" },
        ip: '192.168.1.201'
      });
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(res.status).toHaveBeenCalledWith(403);
    });
  });

  describe('XSS Detection', () => {
    it('should detect XSS attempts in requests', () => {
      const req = mockRequest({
        query: { comment: '<script>alert("xss")</script>' },
        ip: '192.168.1.300'
      });
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(res.status).toHaveBeenCalledWith(403);
    });

    it('should detect JavaScript injection', () => {
      const req = mockRequest({
        body: { data: 'javascript:alert(1)' },
        ip: '192.168.1.301'
      });
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(res.status).toHaveBeenCalledWith(403);
    });
  });

  describe('Path Traversal Detection', () => {
    it('should detect path traversal attempts', () => {
      const req = mockRequest({
        path: '/files/../../etc/passwd',
        ip: '192.168.1.400'
      });
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(res.status).toHaveBeenCalledWith(403);
    });

    it('should detect encoded path traversal', () => {
      const req = mockRequest({
        path: '/files/%2e%2e%2f%2e%2e%2fetc%2fpasswd',
        ip: '192.168.1.401'
      });
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(res.status).toHaveBeenCalledWith(403);
    });
  });

  describe('User Agent Detection', () => {
    it('should block suspicious user agents', () => {
      const req = mockRequest({
        ip: '192.168.1.500'
      });
      (req.get as Mock).mockReturnValue('python-requests/2.25.1');
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          reason: 'Suspicious User Agent'
        })
      );
    });

    it('should allow legitimate user agents', () => {
      const req = mockRequest({
        ip: '192.168.1.501'
      });
      (req.get as Mock).mockReturnValue('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36');
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(mockNext).toHaveBeenCalled();
      expect(res.status).not.toHaveBeenCalled();
    });
  });

  describe('Security Headers', () => {
    it('should add security headers to responses', () => {
      const req = mockRequest();
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(res.setHeader).toHaveBeenCalledWith('X-Guardian-Status', 'Active');
      expect(res.setHeader).toHaveBeenCalledWith('X-Frame-Options', 'DENY');
      expect(res.setHeader).toHaveBeenCalledWith('X-Content-Type-Options', 'nosniff');
      expect(res.setHeader).toHaveBeenCalledWith('X-XSS-Protection', '1; mode=block');
    });
  });

  describe('Manual IP Management', () => {
    it('should manually block IP addresses', () => {
      guardian.manualBlockIP('192.168.1.666', 'Manual test block');
      
      const req = mockRequest({ ip: '192.168.1.666' });
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(res.status).toHaveBeenCalledWith(403);
      expect(res.json).toHaveBeenCalledWith(
        expect.objectContaining({
          reason: 'IP Blacklisted'
        })
      );
    });

    it('should manually unblock IP addresses', () => {
      guardian.manualBlockIP('192.168.1.777', 'Test block');
      guardian.manualUnblockIP('192.168.1.777');
      
      const req = mockRequest({ ip: '192.168.1.777' });
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(mockNext).toHaveBeenCalled();
      expect(res.status).not.toHaveBeenCalled();
    });
  });

  describe('Statistics and Monitoring', () => {
    it('should track request statistics', () => {
      const req = mockRequest();
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      const stats = guardian.getStats();
      expect(stats.totalRequests).toBeGreaterThan(0);
    });

    it('should provide threat logs', () => {
      const req = mockRequest({
        query: { malicious: "'; DROP TABLE test; --" },
        ip: '192.168.1.888'
      });
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      const threatLogs = guardian.getThreatLogs();
      expect(threatLogs.length).toBeGreaterThan(0);
      expect(threatLogs[0]).toHaveProperty('ip', '192.168.1.888');
      expect(threatLogs[0]).toHaveProperty('reason');
      expect(threatLogs[0]).toHaveProperty('severity');
    });

    it('should provide dashboard data', () => {
      const dashboard = guardian.getDashboard();
      
      expect(dashboard).toHaveProperty('status');
      expect(dashboard).toHaveProperty('stats');
      expect(dashboard).toHaveProperty('recentThreats');
      expect(dashboard).toHaveProperty('blockedIPs');
      expect(dashboard).toHaveProperty('config');
    });
  });

  describe('System Health', () => {
    it('should report healthy status initially', () => {
      const stats = guardian.getStats();
      expect(stats.systemHealth).toBe('healthy');
    });

    it('should activate and deactivate Guardian', () => {
      guardian.setActive(false);
      const req = mockRequest();
      const res = mockResponse();
      const middleware = guardian.middleware();

      middleware(req, res, mockNext);

      expect(mockNext).toHaveBeenCalled();
      expect(res.status).not.toHaveBeenCalled();

      guardian.setActive(true);
    });
  });

  describe('Edge Cases', () => {
    it('should handle missing IP addresses gracefully', () => {
      const req = mockRequest({
        ip: undefined,
        connection: { remoteAddress: undefined },
        headers: {}
      });
      const res = mockResponse();
      const middleware = guardian.middleware();

      expect(() => {
        middleware(req, res, mockNext);
      }).not.toThrow();
    });

    it('should handle malformed requests', () => {
      const req = mockRequest({
        query: null,
        body: null
      });
      const res = mockResponse();
      const middleware = guardian.middleware();

      expect(() => {
        middleware(req, res, mockNext);
      }).not.toThrow();
    });
  });
});
