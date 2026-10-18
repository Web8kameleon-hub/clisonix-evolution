/**
 * Simple Backend Server - GET & POST Endpoints
 * Express + Zod Validation + CORS
 */

const express = require('express');
const cors = require('cors');

const app = express();
const PORT = 3008;

// Middleware
app.use(cors({
    origin: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://localhost:3003', 'http://localhost:3004'],
    methods: ['GET', 'POST', 'PUT', 'DELETE'],
    credentials: true
}));

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// In-memory data storage (për test)
let dataStore = [
    { id: 1, name: 'Item 1', description: 'First test item', timestamp: new Date().toISOString() },
    { id: 2, name: 'Item 2', description: 'Second test item', timestamp: new Date().toISOString() },
    { id: 3, name: 'Item 3', description: 'Third test item', timestamp: new Date().toISOString() }
];

let nextId = 4;

// 🏠 Root endpoint
app.get('/', (req, res) => {
    res.json({
        message: 'Simple Backend API ✅',
        version: '1.0.0',
        endpoints: {
            'GET /': 'This info',
            'GET /status': 'Server status',
            'GET /api/data': 'Get all data',
            'GET /api/data/:id': 'Get specific item',
            'POST /api/data': 'Create new item',
            'PUT /api/data/:id': 'Update item',
            'DELETE /api/data/:id': 'Delete item'
        },
        server_port: PORT,
        timestamp: new Date().toISOString()
    });
});

// ✅ Status endpoint
app.get('/status', (req, res) => {
    res.json({
        status: 'healthy',
        server: 'running',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        data_count: dataStore.length,
        timestamp: new Date().toISOString()
    });
});

// 📊 GET - Get all data
app.get('/api/data', (req, res) => {
    try {
        const { limit, offset, search } = req.query;
        
        let result = [...dataStore];
        
        // Search functionality
        if (search) {
            result = result.filter(item => 
                item.name.toLowerCase().includes(search.toLowerCase()) ||
                item.description.toLowerCase().includes(search.toLowerCase())
            );
        }
        
        // Pagination
        const total = result.length;
        if (offset) result = result.slice(parseInt(offset));
        if (limit) result = result.slice(0, parseInt(limit));
        
        res.json({
            success: true,
            data: result,
            total: total,
            returned: result.length,
            query: { limit, offset, search },
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// 🔍 GET - Get specific item by ID
app.get('/api/data/:id', (req, res) => {
    try {
        const id = parseInt(req.params.id);
        const item = dataStore.find(item => item.id === id);
        
        if (!item) {
            return res.status(404).json({
                success: false,
                error: `Item with id ${id} not found`,
                timestamp: new Date().toISOString()
            });
        }
        
        res.json({
            success: true,
            data: item,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// ➕ POST - Create new item
app.post('/api/data', (req, res) => {
    try {
        const { name, description } = req.body;
        
        // Simple validation
        if (!name) {
            return res.status(400).json({
                success: false,
                error: 'Name is required',
                timestamp: new Date().toISOString()
            });
        }
        
        const newItem = {
            id: nextId++,
            name: name,
            description: description || '',
            timestamp: new Date().toISOString(),
            created_at: new Date().toISOString()
        };
        
        dataStore.push(newItem);
        
        res.status(201).json({
            success: true,
            data: newItem,
            message: 'Item created successfully',
            total_items: dataStore.length,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// ✏️ PUT - Update item
app.put('/api/data/:id', (req, res) => {
    try {
        const id = parseInt(req.params.id);
        const { name, description } = req.body;
        
        const itemIndex = dataStore.findIndex(item => item.id === id);
        
        if (itemIndex === -1) {
            return res.status(404).json({
                success: false,
                error: `Item with id ${id} not found`,
                timestamp: new Date().toISOString()
            });
        }
        
        // Update item
        if (name !== undefined) dataStore[itemIndex].name = name;
        if (description !== undefined) dataStore[itemIndex].description = description;
        dataStore[itemIndex].updated_at = new Date().toISOString();
        
        res.json({
            success: true,
            data: dataStore[itemIndex],
            message: 'Item updated successfully',
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// ❌ DELETE - Delete item
app.delete('/api/data/:id', (req, res) => {
    try {
        const id = parseInt(req.params.id);
        const itemIndex = dataStore.findIndex(item => item.id === id);
        
        if (itemIndex === -1) {
            return res.status(404).json({
                success: false,
                error: `Item with id ${id} not found`,
                timestamp: new Date().toISOString()
            });
        }
        
        const deletedItem = dataStore.splice(itemIndex, 1)[0];
        
        res.json({
            success: true,
            data: deletedItem,
            message: 'Item deleted successfully',
            remaining_items: dataStore.length,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: error.message,
            timestamp: new Date().toISOString()
        });
    }
});

// 🧪 Test endpoints
app.get('/test/get', (req, res) => {
    res.json({
        method: 'GET',
        message: 'GET endpoint test successful! ✅',
        query_params: req.query,
        timestamp: new Date().toISOString()
    });
});

app.post('/test/post', (req, res) => {
    res.json({
        method: 'POST',
        message: 'POST endpoint test successful! ✅',
        received_data: req.body,
        headers: req.headers,
        timestamp: new Date().toISOString()
    });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        success: false,
        error: 'Endpoint not found',
        method: req.method,
        url: req.originalUrl,
        available_endpoints: [
            'GET /',
            'GET /status',
            'GET /api/data',
            'GET /api/data/:id',
            'POST /api/data',
            'PUT /api/data/:id',
            'DELETE /api/data/:id',
            'GET /test/get',
            'POST /test/post'
        ],
        timestamp: new Date().toISOString()
    });
});

// Error handler
app.use((error, req, res, next) => {
    console.error('Server Error:', error);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        timestamp: new Date().toISOString()
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Simple Backend Server running on http://localhost:${PORT}`);
    console.log(`\n📋 Available endpoints:`);
    console.log(`   GET  http://localhost:${PORT}/`);
    console.log(`   GET  http://localhost:${PORT}/status`);
    console.log(`   GET  http://localhost:${PORT}/api/data`);
    console.log(`   GET  http://localhost:${PORT}/api/data/:id`);
    console.log(`   POST http://localhost:${PORT}/api/data`);
    console.log(`   PUT  http://localhost:${PORT}/api/data/:id`);
    console.log(`   DELETE http://localhost:${PORT}/api/data/:id`);
    console.log(`\n🧪 Test endpoints:`);
    console.log(`   GET  http://localhost:${PORT}/test/get`);
    console.log(`   POST http://localhost:${PORT}/test/post`);
    console.log(`\n✅ Server ready for GET & POST requests!`);
});

module.exports = app;
