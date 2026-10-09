/**
 * Layer 13: API Gateway Middleware
 * Centralized routing, authentication, and request handling
 */

import express, { Request, Response, NextFunction } from "express";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import slowDown from "express-slow-down";
import hpp from "hpp";

// ═══════════════════════════════════════════════════════════════════════════════
// SECURITY MIDDLEWARE
// ═══════════════════════════════════════════════════════════════════════════════

export const securityMiddleware = [
  // Helmet for security headers
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        baseUri: ["'self'"],
        objectSrc: ["'none'"],
        frameAncestors: ["'none'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'"],
        imgSrc: ["'self'", "data:", "https:"],
        connectSrc: ["'self'", "https:", "wss:"],
        upgradeInsecureRequests: [],
      },
    },
    crossOriginEmbedderPolicy: false,
    crossOriginOpenerPolicy: { policy: "same-origin" },
    crossOriginResourcePolicy: { policy: "same-site" },
    referrerPolicy: { policy: "strict-origin-when-cross-origin" },
    hsts: {
      maxAge: 31536000,
      includeSubDomains: true,
      preload: true,
    },
  }),

  // Prevent HTTP Parameter Pollution
  hpp(),
];

// ═══════════════════════════════════════════════════════════════════════════════
// RATE LIMITING
// ═══════════════════════════════════════════════════════════════════════════════

export const rateLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 120,
  message: {
    error: "Too many requests",
    message: "Please try again later",
    retryAfter: "15 minutes",
  },
  standardHeaders: true,
  legacyHeaders: false,
  skip: (req) => req.path === "/health" || req.path === "/status",
});

export const speedLimiter = slowDown({
  windowMs: 15 * 60 * 1000,
  delayAfter: 30,
  delayMs: (hits) => Math.min(400, hits * 100),
});

// ═══════════════════════════════════════════════════════════════════════════════
// API GATEWAY ROUTER
// ═══════════════════════════════════════════════════════════════════════════════

export const gatewayRouter = express.Router();

// Health check
gatewayRouter.get("/health", (req: Request, res: Response) => {
  res.json({
    status: "healthy",
    layer: "gateway",
    version: "1.0.0",
    timestamp: new Date().toISOString(),
  });
});

// Gateway status
gatewayRouter.get("/status", (req: Request, res: Response) => {
  res.json({
    gateway: "active",
    security: "helmet-enabled",
    rateLimit: "100/15min",
    slowDown: "after-50-requests",
  });
});

// Request logging middleware
export const requestLogger = (
  req: Request,
  res: Response,
  next: NextFunction,
) => {
  const start = Date.now();

  res.on("finish", () => {
    const duration = Date.now() - start;
    console.log(
      `[GATEWAY] ${req.method} ${req.path} - ${res.statusCode} - ${duration}ms`,
    );
  });

  next();
};

export default {
  securityMiddleware,
  rateLimiter,
  speedLimiter,
  gatewayRouter,
  requestLogger,
};
