/**
 * EuroWeb API Gateway - Port 4000
 * Pika hyrëse kryesore për të gjitha microservices
 */

import compression from 'compression';
import cors from 'cors';
import express from 'express';
import rateLimit from 'express-rate-limit';
import helmet from 'helmet';
import { createProxyMiddleware } from 'http-proxy-middleware';
import path from 'path';
import { fileURLToPath } from 'url';
import { CORS_OPTIONS, PORTS, SERVICE_REGISTRY } from '../shared/config.js';
import { createLogger } from '../shared/logger.js';
import { errorHandler, requestLogger } from '../shared/middleware.js';

// ES Module __dirname equivalent
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const logger = createLogger('gateway');

// Security & Performance
app.use(helmet());
app.use(cors(CORS_OPTIONS));
app.use(compression());
app.use(express.json());
app.use(requestLogger('gateway'));

// Rate limiting
app.use(rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 1000,
  message: { error: 'Shumë kërkesa. Provo përsëri më vonë.' }
}));

// Health check
app.get('/health', (_req, res) => {
  res.json({
    service: 'gateway',
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

// Service discovery
app.get('/services', (_req, res) => {
  res.json({
    services: Object.entries(SERVICE_REGISTRY).map(([name, url]) => ({
      name,
      url,
      status: 'active'
    }))
  });
});

// Proxy routes to microservices
app.use('/api/auth', createProxyMiddleware({
  target: SERVICE_REGISTRY.auth,
  changeOrigin: true,
  pathRewrite: { '^/api/auth': '' }
}));

app.use('/api/agi', createProxyMiddleware({
  target: SERVICE_REGISTRY.agi,
  changeOrigin: true,
  pathRewrite: { '^/api/agi': '' }
}));

app.use('/api/data', createProxyMiddleware({
  target: SERVICE_REGISTRY.data,
  changeOrigin: true,
  pathRewrite: { '^/api/data': '' }
}));

// Static files for Dashboard UI
const frontendPath = path.resolve(__dirname, '../frontend');
app.use(express.static(frontendPath));

// Default route - Serve Dashboard UI
app.get('/', (_req, res) => {
  res.sendFile(path.join(frontendPath, 'index.html'));
});

// Error handler
app.use(errorHandler);

// Start server
app.listen(PORTS.GATEWAY, () => {
  logger.info(`🚀 Gateway running on http://localhost:${PORTS.GATEWAY}`);
  logger.info('📡 Services:');
  logger.info(`   - Auth:     ${SERVICE_REGISTRY.auth}`);
  logger.info(`   - AGI:      ${SERVICE_REGISTRY.agi}`);
  logger.info(`   - Data:     ${SERVICE_REGISTRY.data}`);
  logger.info(`   - Realtime: ${SERVICE_REGISTRY.realtime}`);
});

export default app;
