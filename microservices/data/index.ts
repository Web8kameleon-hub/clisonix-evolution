/**
 * EuroWeb Data Service - Port 4003
 * Data Processing & Storage Management
 */

import cors from 'cors';
import express from 'express';
import helmet from 'helmet';
import { v4 as uuidv4 } from 'uuid';
import { CORS_OPTIONS, PORTS } from '../shared/config.js';
import { createLogger } from '../shared/logger.js';
import { authMiddleware, errorHandler, requestLogger, type AuthenticatedRequest } from '../shared/middleware.js';

const app = express();
const logger = createLogger('data');

app.use(helmet());
app.use(cors(CORS_OPTIONS));
app.use(express.json({ limit: '50mb' }));
app.use(requestLogger('data'));

// In-memory data store (replace with database)
const dataStore = new Map<string, { id: string; data: unknown; userId: string; createdAt: Date; updatedAt: Date }>();

// Health check
app.get('/health', (_req, res) => {
  res.json({ service: 'data', status: 'healthy', timestamp: new Date().toISOString() });
});

// Stats
app.get('/stats', (_req, res) => {
  res.json({
    totalRecords: dataStore.size,
    memoryUsage: process.memoryUsage(),
    uptime: process.uptime()
  });
});

// Create data
app.post('/store', authMiddleware, (req: AuthenticatedRequest, res) => {
  try {
    const { data, collection = 'default' } = req.body;
    const id = uuidv4();
    const now = new Date();

    const record = {
      id,
      collection,
      data,
      userId: req.user!.id,
      createdAt: now,
      updatedAt: now
    };

    dataStore.set(id, record);
    logger.info(`Data stored: ${id} by ${req.user?.email}`);

    res.status(201).json({ id, message: 'Data stored successfully' });
  } catch (error) {
    logger.error('Store error:', error);
    res.status(500).json({ error: 'Failed to store data' });
  }
});

// Get data by ID
app.get('/store/:id', authMiddleware, (req: AuthenticatedRequest, res) => {
  const id = req.params.id as string;
  const record = dataStore.get(id);

  if (!record) {
    return res.status(404).json({ error: 'Record not found' });
  }

  if (record.userId !== req.user!.id) {
    return res.status(403).json({ error: 'Access denied' });
  }

  res.json(record);
});

// Update data
app.put('/store/:id', authMiddleware, (req: AuthenticatedRequest, res) => {
  const id = req.params.id as string;
  const record = dataStore.get(id);

  if (!record) {
    return res.status(404).json({ error: 'Record not found' });
  }

  if (record.userId !== req.user!.id) {
    return res.status(403).json({ error: 'Access denied' });
  }

  record.data = req.body.data;
  record.updatedAt = new Date();
  dataStore.set(id, record);

  res.json({ id, message: 'Data updated successfully' });
});

// Delete data
app.delete('/store/:id', authMiddleware, (req: AuthenticatedRequest, res) => {
  const id = req.params.id as string;
  const record = dataStore.get(id);

  if (!record) {
    return res.status(404).json({ error: 'Record not found' });
  }

  if (record.userId !== req.user!.id) {
    return res.status(403).json({ error: 'Access denied' });
  }

  dataStore.delete(id);
  logger.info(`Data deleted: ${id} by ${req.user?.email}`);

  res.json({ message: 'Data deleted successfully' });
});

// List user's data
app.get('/store', authMiddleware, (req: AuthenticatedRequest, res) => {
  const { collection, limit = 100, offset = 0 } = req.query;

  let records = Array.from(dataStore.values())
    .filter(r => r.userId === req.user!.id);

  if (collection) {
    records = records.filter(r => (r as { collection?: string }).collection === collection);
  }

  const total = records.length;
  records = records.slice(Number(offset), Number(offset) + Number(limit));

  res.json({ records, total, limit: Number(limit), offset: Number(offset) });
});

// Batch operations
app.post('/batch', authMiddleware, async (req: AuthenticatedRequest, res) => {
  try {
    const { operations } = req.body;
    const results: { operation: string; id: string; success: boolean }[] = [];

    for (const op of operations) {
      const id = uuidv4();
      if (op.type === 'create') {
        dataStore.set(id, {
          id,
          data: op.data,
          userId: req.user!.id,
          createdAt: new Date(),
          updatedAt: new Date()
        });
        results.push({ operation: 'create', id, success: true });
      }
    }

    res.json({ results, processed: results.length });
  } catch (error) {
    logger.error('Batch error:', error);
    res.status(500).json({ error: 'Batch operation failed' });
  }
});

// Search
app.post('/search', authMiddleware, (req: AuthenticatedRequest, res) => {
  const { query, fields = [] } = req.body;

  const records = Array.from(dataStore.values())
    .filter(r => r.userId === req.user!.id)
    .filter(r => {
      const dataStr = JSON.stringify(r.data).toLowerCase();
      return dataStr.includes((query as string).toLowerCase());
    });

  res.json({ results: records, total: records.length, query });
});

app.use(errorHandler);

app.listen(PORTS.DATA, () => {
  logger.info(`💾 Data Service running on http://localhost:${PORTS.DATA}`);
});

export default app;
