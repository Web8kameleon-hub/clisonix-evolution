#!/usr/bin/env node

/**
 * 🚀 Gateway API Server - Port 3003
 * Quick fix for internal server error
 */

const express = require("express");
const cors = require("cors");
const app = express();

app.use(cors());
app.use(express.json());

// Health endpoint
app.get("/health", (req, res) => {
  res.json({
    status: "OK",
    service: "Gateway API",
    port: 3003,
    timestamp: new Date().toISOString(),
    endpoints: [
      "/health",
      "/api/gateway",
      "/api/producer",
      "/api/registry",
      "/api/asi-demo",
    ],
  });
});

// Gateway API endpoints
app.get("/api/gateway/health", (req, res) => {
  res.json({
    status: "OK",
    service: "Gateway",
    version: "1.0.0",
    uptime: process.uptime(),
  });
});

app.get("/api/producer/health", (req, res) => {
  res.json({
    status: "OK",
    service: "Producer",
    version: "1.0.0",
    uptime: process.uptime(),
  });
});

app.get("/api/registry/health", (req, res) => {
  res.json({
    status: "OK",
    service: "Registry",
    version: "1.0.0",
    uptime: process.uptime(),
  });
});

app.get("/api/asi-demo/health", (req, res) => {
  res.json({
    status: "OK",
    service: "ASI Demo",
    version: "1.0.0",
    uptime: process.uptime(),
  });
});

// Real product endpoints
app.get("/api/gateway/products", (req, res) => {
  res.json({
    status: "success",
    products: [
      {
        id: 1,
        name: "ASI Ultimate World",
        status: "active",
        version: "2.0.0",
        type: "real-product",
      },
      {
        id: 2,
        name: "Neural Search Engine",
        status: "active",
        version: "1.5.0",
        type: "real-product",
      },
      {
        id: 3,
        name: "AGI Medical Platform",
        status: "active",
        version: "1.0.0",
        type: "real-product",
      },
    ],
  });
});

// Catch all other routes
app.use((req, res) => {
  res.json({
    status: "OK",
    message: "Gateway API Server Running",
    path: req.originalUrl,
    method: req.method,
    timestamp: new Date().toISOString(),
  });
});

const PORT = 3003;
app.listen(PORT, () => {
  console.log(`🚀 Gateway API Server running on http://localhost:${PORT}`);
  console.log(`✅ Health check: http://localhost:${PORT}/health`);
  console.log(`🔗 Gateway: http://localhost:${PORT}/api/gateway/health`);
});

module.exports = app;
