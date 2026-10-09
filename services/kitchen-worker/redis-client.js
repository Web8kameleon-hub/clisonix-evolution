/**
 * Redis Client & BullMQ Queue for Kitchen Worker v2.0
 * Production queue replacement for filesystem polling
 */

const Redis = require('ioredis');
const { Queue, QueueEvents, Worker } = require('bullmq');

// Configuration
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const QUEUE_NAME = 'kitchen-jobs';
const CONCURRENCY = parseInt(process.env.MAX_CONCURRENT_JOBS || '2');

// Redis Connection
const connection = new Redis(REDIS_URL, {
  lazyConnect: true,
  maxRetriesPerRequest: 3,
});

// Kitchen Queue
const kitchenQueue = new Queue(QUEUE_NAME, { connection });

// Events
const queueEvents = new QueueEvents(QUEUE_NAME, { connection });

// Export for worker.js
module.exports = {
  connection,
  kitchenQueue,
  queueEvents,
  addJob: async (jobData) => {
    return await kitchenQueue.add('execute', jobData, {
      priority: jobData.priority || 5,
      removeOnComplete: 10, // Keep 10 completed
      removeOnFail: 5,     // Keep 5 failed
    });
  },
  processJobs: (processor) => {
    new Worker(QUEUE_NAME, processor, {
      connection,
      concurrency: CONCURRENCY
    });
  }
};

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('[redis-client] Closing queues...');
  await kitchenQueue.close();
  await connection.quit();
  process.exit(0);
});

console.log(`[redis-client] Connected to Redis: ${REDIS_URL}`);
console.log(`[redis-client] Queue: ${QUEUE_NAME} (concurrency: ${CONCURRENCY})`);

