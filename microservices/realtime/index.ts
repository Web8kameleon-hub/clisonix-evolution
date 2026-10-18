/**
 * EuroWeb Realtime Service - Port 4004
 * WebSocket & Real-time Communication
 */

import cors from 'cors';
import express from 'express';
import { createServer } from 'http';
import { v4 as uuidv4 } from 'uuid';
import { WebSocket, WebSocketServer } from 'ws';
import { CORS_OPTIONS, PORTS } from '../shared/config.js';
import { createLogger } from '../shared/logger.js';

const app = express();
const logger = createLogger('realtime');

app.use(cors(CORS_OPTIONS));
app.use(express.json());

// Create HTTP server
const server = createServer(app);

// Create WebSocket server
const wss = new WebSocketServer({ server });

// Connected clients
const clients = new Map<string, { ws: WebSocket; userId?: string; channels: Set<string> }>();

// Channels/Rooms
const channels = new Map<string, Set<string>>();

// Health check via HTTP
app.get('/health', (_req, res) => {
  res.json({
    service: 'realtime',
    status: 'healthy',
    connections: clients.size,
    channels: channels.size,
    timestamp: new Date().toISOString()
  });
});

// Stats
app.get('/stats', (_req, res) => {
  res.json({
    activeConnections: clients.size,
    channels: Array.from(channels.entries()).map(([name, members]) => ({
      name,
      members: members.size
    })),
    uptime: process.uptime()
  });
});

// Broadcast message to a channel via HTTP
app.post('/broadcast', (req, res) => {
  const { channel, message, type = 'message' } = req.body;

  const channelClients = channels.get(channel);
  if (!channelClients) {
    return res.status(404).json({ error: 'Channel not found' });
  }

  let sent = 0;
  channelClients.forEach(clientId => {
    const client = clients.get(clientId);
    if (client && client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(JSON.stringify({ type, channel, data: message, timestamp: new Date().toISOString() }));
      sent++;
    }
  });

  res.json({ success: true, sent, channel });
});

// WebSocket connection handler
wss.on('connection', (ws) => {
  const clientId = uuidv4();
  clients.set(clientId, { ws, channels: new Set() });

  logger.info(`Client connected: ${clientId} | Total: ${clients.size}`);

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'connected',
    clientId,
    message: 'Lidhja me EuroWeb Realtime u krye',
    timestamp: new Date().toISOString()
  }));

  // Handle messages
  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      handleMessage(clientId, message);
    } catch {
      ws.send(JSON.stringify({ type: 'error', message: 'Invalid JSON' }));
    }
  });

  // Handle disconnect
  ws.on('close', () => {
    const client = clients.get(clientId);
    if (client) {
      // Remove from all channels
      client.channels.forEach(channelName => {
        const channel = channels.get(channelName);
        if (channel) {
          channel.delete(clientId);
          if (channel.size === 0) {
            channels.delete(channelName);
          }
        }
      });
    }
    clients.delete(clientId);
    logger.info(`Client disconnected: ${clientId} | Total: ${clients.size}`);
  });

  // Handle errors
  ws.on('error', (error) => {
    logger.error(`WebSocket error for ${clientId}:`, error);
  });
});

function handleMessage(clientId: string, message: { type: string; channel?: string; data?: unknown; userId?: string }) {
  const client = clients.get(clientId);
  if (!client) return;

  switch (message.type) {
    case 'join':
      if (message.channel) {
        if (!channels.has(message.channel)) {
          channels.set(message.channel, new Set());
        }
        channels.get(message.channel)!.add(clientId);
        client.channels.add(message.channel);

        client.ws.send(JSON.stringify({
          type: 'joined',
          channel: message.channel,
          members: channels.get(message.channel)!.size
        }));

        // Notify others in channel
        broadcastToChannel(message.channel, {
          type: 'user_joined',
          channel: message.channel,
          clientId
        }, clientId);

        logger.info(`Client ${clientId} joined channel: ${message.channel}`);
      }
      break;

    case 'leave':
      if (message.channel) {
        const channel = channels.get(message.channel);
        if (channel) {
          channel.delete(clientId);
          client.channels.delete(message.channel);

          if (channel.size === 0) {
            channels.delete(message.channel);
          } else {
            broadcastToChannel(message.channel, {
              type: 'user_left',
              channel: message.channel,
              clientId
            });
          }
        }

        client.ws.send(JSON.stringify({
          type: 'left',
          channel: message.channel
        }));
      }
      break;

    case 'message':
      if (message.channel && client.channels.has(message.channel)) {
        broadcastToChannel(message.channel, {
          type: 'message',
          channel: message.channel,
          from: clientId,
          data: message.data,
          timestamp: new Date().toISOString()
        });
      }
      break;

    case 'auth':
      if (message.userId) {
        client.userId = message.userId;
        client.ws.send(JSON.stringify({
          type: 'authenticated',
          userId: message.userId
        }));
      }
      break;

    case 'ping':
      client.ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
      break;

    default:
      client.ws.send(JSON.stringify({ type: 'error', message: 'Unknown message type' }));
  }
}

function broadcastToChannel(channelName: string, message: unknown, excludeClientId?: string) {
  const channel = channels.get(channelName);
  if (!channel) return;

  const messageStr = JSON.stringify(message);
  channel.forEach(clientId => {
    if (excludeClientId && clientId === excludeClientId) return;
    const client = clients.get(clientId);
    if (client && client.ws.readyState === WebSocket.OPEN) {
      client.ws.send(messageStr);
    }
  });
}

// Start server
server.listen(PORTS.REALTIME, () => {
  logger.info(`⚡ Realtime Service running on ws://localhost:${PORTS.REALTIME}`);
  logger.info('   HTTP Stats: http://localhost:' + PORTS.REALTIME + '/stats');
});

export default server;
