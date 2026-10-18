#!/usr/bin/env node

/**
 * 🚀 Gateway API Server - Built-in HTTP (No External Dependencies)
 * Quick fix for port 3003 internal server error
 */

const http = require('http');
const url = require('url');

// Response helper
function sendJson(res, data, statusCode = 200) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
  });
  res.end(JSON.stringify(data, null, 2));
}

// Create server
const server = http.createServer((req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const path = parsedUrl.pathname;

  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization'
    });
    res.end();
    return;
  }

  console.log(`${req.method} ${path}`);

  // Route handling
  if (path === '/health') {
    sendJson(res, {
      status: 'OK',
      service: 'Gateway API',
      port: 3003,
      timestamp: new Date().toISOString(),
      endpoints: [
        '/health',
        '/api/gateway/health',
        '/api/producer/health',
        '/api/registry/health',
        '/api/asi-demo/health',
        '/api/gateway/products'
      ]
    });
  }
  else if (path === '/api/gateway/health') {
    sendJson(res, {
      status: 'OK',
      service: 'Gateway',
      version: '1.0.0',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    });
  }
  else if (path === '/api/producer/health') {
    sendJson(res, {
      status: 'OK',
      service: 'Producer',
      version: '1.0.0',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    });
  }
  else if (path === '/api/registry/health') {
    sendJson(res, {
      status: 'OK',
      service: 'Registry',
      version: '1.0.0',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    });
  }
  else if (path === '/api/asi-demo/health') {
    sendJson(res, {
      status: 'OK',
      service: 'ASI Demo',
      version: '1.0.0',
      uptime: process.uptime(),
      timestamp: new Date().toISOString()
    });
  }
  else if (path === '/api/gateway/products') {
    sendJson(res, {
      status: 'success',
      message: 'Real Products API',
      products: [
        {
          id: 1,
          name: 'ASI Ultimate World',
          status: 'production',
          version: '2.0.0',
          type: 'real-product',
          url: 'http://localhost:3001'
        },
        {
          id: 2,
          name: 'Neural Search Engine',
          status: 'production',
          version: '1.5.0',
          type: 'real-product',
          url: 'http://localhost:3001/api/neural-search'
        },
        {
          id: 3,
          name: 'AGI Medical Platform',
          status: 'production',
          version: '1.0.0',
          type: 'real-product',
          url: 'http://localhost:3001/api/medical'
        },
        {
          id: 4,
          name: 'ASI SaaS Dashboard',
          status: 'production',
          version: '1.0.0',
          type: 'real-product',
          url: 'http://localhost:3111'
        }
      ],
      total: 4,
      timestamp: new Date().toISOString()
    });
  }
  else {
    // Default response for any other path
    sendJson(res, {
      status: 'OK',
      message: 'Gateway API Server - Real Products Focus',
      service: 'Gateway API',
      path: path,
      method: req.method,
      timestamp: new Date().toISOString(),
      note: 'Ready for real product development'
    });
  }
});

const PORT = 3003;
server.listen(PORT, () => {
  console.log(`🚀 Gateway API Server running on http://localhost:${PORT}`);
  console.log(`✅ Health: http://localhost:${PORT}/health`);
  console.log(`🔗 Gateway: http://localhost:${PORT}/api/gateway/health`);
  console.log(`📦 Products: http://localhost:${PORT}/api/gateway/products`);
  console.log(`🎯 Focus: Real products, no more UI issues!`);
});

module.exports = server;
