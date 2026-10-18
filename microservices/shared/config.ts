/**
 * EuroWeb Microservices - Konfigurim i Përbashkët
 * Porte të ndryshme për çdo shërbim pa konflikte
 */

export const PORTS = {
  GATEWAY: 4000,      // API Gateway - Pika hyrëse kryesore
  AUTH: 4001,         // Authentication Service
  AGI: 4002,          // AGI Intelligence Service
  DATA: 4003,         // Data Processing Service
  REALTIME: 4004,     // WebSocket / Realtime Service
  ANALYTICS: 4005,    // Analytics Service
  STORAGE: 4006,      // File Storage Service
  NOTIFICATIONS: 4007 // Notification Service
} as const;

export const REDIS_CONFIG = {
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  password: process.env.REDIS_PASSWORD || undefined
};

export const JWT_CONFIG = {
  secret: process.env.JWT_SECRET || 'euroweb-microservices-secret-2026',
  expiresIn: 86400,        // 24 orë në sekonda
  refreshExpiresIn: 604800  // 7 ditë në sekonda
};

export const CORS_OPTIONS = {
  origin: process.env.FRONTEND_URL || 'http://localhost:3000',
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
};

export const SERVICE_REGISTRY = {
  gateway: `http://localhost:${PORTS.GATEWAY}`,
  auth: `http://localhost:${PORTS.AUTH}`,
  agi: `http://localhost:${PORTS.AGI}`,
  data: `http://localhost:${PORTS.DATA}`,
  realtime: `ws://localhost:${PORTS.REALTIME}`
};
