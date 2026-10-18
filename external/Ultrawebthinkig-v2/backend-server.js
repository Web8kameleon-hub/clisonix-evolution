/**
 * Backend Server - Express me GET dhe POST endpoints
 * Mbështet validation me Zod dhe CORS
 */

const express = require('express');
const cors = require('cors');

// Simulimi i Zod për validation (mund ta importosh si ES6 module nëse duhet)
const validateRequest = (data, schema) => {
  // Validation i thjeshtë - mund ta zëvendësosh me Zod
  return { success: true, data };
};

class BackendServer {
  constructor() {
    this.app = express();
    this.port = 8000;
    this.modules = [
      {
        id: "agi-core",
        name: "AGI Core", 
        path: "backend/agi/core.ts",
        category: "backend",
        description: "Bërthama e AGI: orchestrim i mind/sense/response/monitor/planner.",
        function: "Orkestron inteligjencën, planifikimin dhe përgjigjet e sistemit.",
        version: "1.0.0",
        status: "online",
        endpoints: [
          { name: "health", url: "http://127.0.0.1:7001/health", type: "health" },
          { name: "metrics", url: "http://127.0.0.1:7001/metrics", type: "metrics" }
        ],
        lastUpdated: new Date().toISOString()
      },
      {
        id: "web8-ui",
        name: "WEB8 UI",
        path: "frontend/pages/index.tsx", 
        category: "frontend",
        description: "UI kryesor, surfing fluid, AGISheet, navbar galaktik.",
        function: "Shfaq ndërfaqen kryesore dhe orkestron navigimin live.",
        version: "1.0.0",
        status: "online",
        endpoints: [
          { name: "ui", url: "http://127.0.0.1:3000", type: "ui" }
        ],
        lastUpdated: new Date().toISOString()
      },
      {
        id: "neurosonix-api",
        name: "NeuroSonix API",
        path: "backend/neurosonix/main.py",
        category: "backend", 
        description: "EEG/Audio pipelines industriale, upload real në S3/MinIO, queue.",
        function: "Proceson sinjale EEG/Audio me endpoints realë (pa mock).",
        version: "2.1.3",
        status: "degraded",
        endpoints: [
          { name: "health", url: "http://127.0.0.1:8010/health", type: "health" },
          { name: "metrics", url: "http://127.0.0.1:8010/metrics", type: "metrics" }
        ],
        lastUpdated: new Date().toISOString()
      }
    ];
    this.setupMiddleware();
    this.setupRoutes();
  }

  setupMiddleware() {
    // CORS për të gjitha origjinet lokale
    this.app.use(cors({
      origin: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://localhost:8000'],
      methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      credentials: true
    }));

    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));

    // Logging middleware
    this.app.use((req, res, next) => {
      console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
      next();
    });
  }

  setupRoutes() {
    // 🏠 Root endpoint
    this.app.get('/', (req, res) => {
      res.json({
        service: 'Backend Server',
        version: '1.0.0',
        status: 'running',
        endpoints: {
          modules: 'GET /api/modules - Merr të gjitha modulet',
          module_by_id: 'GET /api/modules/:id - Merr modul specifik',
          create_module: 'POST /api/modules - Krijo modul të ri',
          update_module: 'PUT /api/modules/:id - Përditëso modul',
          delete_module: 'DELETE /api/modules/:id - Fshi modul',
          health: 'GET /api/health - Status i serverit'
        },
        timestamp: new Date().toISOString()
      });
    });

    // 🔍 GET - Merr të gjitha modulet
    this.app.get('/api/modules', (req, res) => {
      const { category, status, limit, offset } = req.query;
      
      let filtered = [...this.modules];
      
      // Filter by category
      if (category) {
        filtered = filtered.filter(m => m.category === category);
      }
      
      // Filter by status
      if (status) {
        filtered = filtered.filter(m => m.status === status);
      }
      
      // Pagination
      const limitNum = parseInt(limit) || filtered.length;
      const offsetNum = parseInt(offset) || 0;
      const paginated = filtered.slice(offsetNum, offsetNum + limitNum);

      res.json({
        ok: true,
        modules: paginated,
        total: filtered.length,
        limit: limitNum,
        offset: offsetNum,
        timestamp: new Date().toISOString()
      });
    });

    // 🔍 GET - Merr modul specifik
    this.app.get('/api/modules/:id', (req, res) => {
      const { id } = req.params;
      const module = this.modules.find(m => m.id === id);
      
      if (!module) {
        return res.status(404).json({
          ok: false,
          error: 'Module not found',
          id: id
        });
      }

      res.json({
        ok: true,
        module: module,
        timestamp: new Date().toISOString()
      });
    });

    // ➕ POST - Krijo modul të ri
    this.app.post('/api/modules', (req, res) => {
      const { name, path, category, description, function: moduleFunction, version, endpoints } = req.body;

      // Validation i thjeshtë
      if (!name || !path || !category || !description || !moduleFunction) {
        return res.status(400).json({
          ok: false,
          error: 'Missing required fields: name, path, category, description, function'
        });
      }

      // Gjeneroj ID të ri
      const id = name.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
      
      // Kontrolloj nëse ekziston
      if (this.modules.find(m => m.id === id)) {
        return res.status(409).json({
          ok: false,
          error: 'Module with this ID already exists',
          id: id
        });
      }

      const newModule = {
        id,
        name,
        path,
        category,
        description,
        function: moduleFunction,
        version: version || '1.0.0',
        status: 'unknown',
        endpoints: endpoints || [],
        lastUpdated: new Date().toISOString()
      };

      this.modules.push(newModule);

      res.status(201).json({
        ok: true,
        message: 'Module created successfully',
        module: newModule,
        timestamp: new Date().toISOString()
      });
    });

    // 🔄 PUT - Përditëso modul
    this.app.put('/api/modules/:id', (req, res) => {
      const { id } = req.params;
      const moduleIndex = this.modules.findIndex(m => m.id === id);

      if (moduleIndex === -1) {
        return res.status(404).json({
          ok: false,
          error: 'Module not found',
          id: id
        });
      }

      // Përditëso vetëm fushat e dërguara
      const allowedFields = ['name', 'path', 'category', 'description', 'function', 'version', 'status', 'endpoints'];
      const updates = {};
      
      for (const field of allowedFields) {
        if (req.body[field] !== undefined) {
          updates[field] = req.body[field];
        }
      }

      updates.lastUpdated = new Date().toISOString();

      this.modules[moduleIndex] = {
        ...this.modules[moduleIndex],
        ...updates
      };

      res.json({
        ok: true,
        message: 'Module updated successfully',
        module: this.modules[moduleIndex],
        timestamp: new Date().toISOString()
      });
    });

    // ❌ DELETE - Fshi modul
    this.app.delete('/api/modules/:id', (req, res) => {
      const { id } = req.params;
      const moduleIndex = this.modules.findIndex(m => m.id === id);

      if (moduleIndex === -1) {
        return res.status(404).json({
          ok: false,
          error: 'Module not found',
          id: id
        });
      }

      const deletedModule = this.modules.splice(moduleIndex, 1)[0];

      res.json({
        ok: true,
        message: 'Module deleted successfully',
        module: deletedModule,
        timestamp: new Date().toISOString()
      });
    });

    // 🏥 Health Check
    this.app.get('/api/health', (req, res) => {
      res.json({
        status: 'healthy',
        service: 'Backend Server',
        uptime: process.uptime(),
        modules_count: this.modules.length,
        memory: process.memoryUsage(),
        timestamp: new Date().toISOString()
      });
    });

    // 🔍 Search modulet
    this.app.get('/api/search', (req, res) => {
      const { q } = req.query;
      
      if (!q) {
        return res.status(400).json({
          ok: false,
          error: 'Query parameter "q" is required'
        });
      }

      const searchTerm = q.toLowerCase();
      const results = this.modules.filter(m => 
        m.name.toLowerCase().includes(searchTerm) ||
        m.description.toLowerCase().includes(searchTerm) ||
        m.function.toLowerCase().includes(searchTerm) ||
        m.category.toLowerCase().includes(searchTerm)
      );

      res.json({
        ok: true,
        query: q,
        results: results,
        count: results.length,
        timestamp: new Date().toISOString()
      });
    });

    // 📊 Statistics
    this.app.get('/api/stats', (req, res) => {
      const stats = {
        total_modules: this.modules.length,
        by_category: {},
        by_status: {},
        latest_updated: null
      };

      let latestDate = 0;
      
      for (const module of this.modules) {
        // Count by category
        stats.by_category[module.category] = (stats.by_category[module.category] || 0) + 1;
        
        // Count by status
        stats.by_status[module.status] = (stats.by_status[module.status] || 0) + 1;
        
        // Find latest updated
        const moduleDate = new Date(module.lastUpdated).getTime();
        if (moduleDate > latestDate) {
          latestDate = moduleDate;
          stats.latest_updated = module;
        }
      }

      res.json({
        ok: true,
        stats: stats,
        timestamp: new Date().toISOString()
      });
    });

    // 404 handler
    this.app.use((req, res) => {
      res.status(404).json({
        ok: false,
        error: 'Endpoint not found',
        path: req.originalUrl,
        method: req.method,
        available_endpoints: ['/api/modules', '/api/health', '/api/search', '/api/stats']
      });
    });

    // Error handler
    this.app.use((err, req, res, next) => {
      console.error('Server Error:', err);
      res.status(500).json({
        ok: false,
        error: 'Internal server error',
        message: err.message,
        timestamp: new Date().toISOString()
      });
    });
  }

  start() {
    this.app.listen(this.port, () => {
      console.log(`🚀 Backend Server running on http://localhost:${this.port}`);
      console.log(`📊 Loaded ${this.modules.length} modules`);
      console.log(`🔗 API endpoints available:`);
      console.log(`   GET  http://localhost:${this.port}/api/modules`);
      console.log(`   POST http://localhost:${this.port}/api/modules`);
      console.log(`   GET  http://localhost:${this.port}/api/modules/:id`);
      console.log(`   PUT  http://localhost:${this.port}/api/modules/:id`);
      console.log(`   DELETE http://localhost:${this.port}/api/modules/:id`);
      console.log(`   GET  http://localhost:${this.port}/api/health`);
      console.log(`   GET  http://localhost:${this.port}/api/search?q=term`);
      console.log(`   GET  http://localhost:${this.port}/api/stats`);
      console.log(`\n✅ Server is ready for GET and POST requests!`);
    });
  }
}

// Start the server
const server = new BackendServer();
server.start();

module.exports = BackendServer;
