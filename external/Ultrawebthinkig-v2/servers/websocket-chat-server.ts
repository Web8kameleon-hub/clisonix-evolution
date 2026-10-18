/**
 * 🚀 UltraWebSocket Chat Server
 * Real-time communication between Clients and Technicians through AGI Gateway
 * Production-grade with room management and message routing
 * 
 * @version 1.0 PRODUCTION WEBSOCKET
 * @author UltraWebThinking Team
 */

import express from 'express';
import { Server } from 'socket.io';
import http from 'http';
import cors from 'cors';
import path from 'path';
import fs from 'fs/promises';

/* ----------------------------- Types ----------------------------- */

interface ChatMessage {
  id: string;
  role: 'client' | 'technician' | 'agi' | 'system';
  text: string;
  room: string;
  timestamp: string;
  userId?: string;
  userName?: string;
  isAgiResponse?: boolean;
  confidence?: number;
  intent?: string;
}

interface Room {
  id: string;
  name: string;
  type: 'support' | 'technical' | 'sales' | 'general';
  clients: Set<string>;
  technicians: Set<string>;
  messages: ChatMessage[];
  created: string;
  lastActivity: string;
}

interface UserConnection {
  id: string;
  socketId: string;
  role: 'client' | 'technician';
  name: string;
  room: string;
  connected: string;
}

/* ----------------------------- AGI Integration ----------------------------- */

class AGIGateway {
  async processMessage(message: ChatMessage): Promise<ChatMessage | null> {
    const input = message.text.toLowerCase();
    
    // Simple AGI logic - extend with your actual AGI system
    if (input.includes('hello') || input.includes('përshëndetje') || input.includes('ckemi')) {
      return {
        id: `agi_${Date.now()}`,
        role: 'agi',
        text: `Përshëndetje! Unë jam AGI asistenti i UltraWeb. Si mund t'ju ndihmoj sot?`,
        room: message.room,
        timestamp: new Date().toISOString(),
        isAgiResponse: true,
        confidence: 0.95,
        intent: 'greeting'
      };
    }
    
    if (input.includes('help') || input.includes('ndihmë') || input.includes('problem')) {
      return {
        id: `agi_${Date.now()}`,
        role: 'agi',
        text: `Kuptoj që keni nevojë për ndihmë. Jam duke e analizuar problemin tuaj dhe do t'ju lidh me një teknik të disponueshëm. Ju lutem prisni...`,
        room: message.room,
        timestamp: new Date().toISOString(),
        isAgiResponse: true,
        confidence: 0.88,
        intent: 'support_request'
      };
    }
    
    if (input.includes('price') || input.includes('çmim') || input.includes('cost')) {
      return {
        id: `agi_${Date.now()}`,
        role: 'agi',
        text: `Për informacione të detajuara rreth çmimeve, po ju lidh me specialistin tonë të shitjeve. Do të përgjigjet brenda 2 minutave.`,
        room: message.room,
        timestamp: new Date().toISOString(),
        isAgiResponse: true,
        confidence: 0.85,
        intent: 'sales_inquiry'
      };
    }
    
    // No AGI response needed, let human technicians handle
    return null;
  }
  
  async routeToTechnician(message: ChatMessage, intent: string): Promise<void> {
    // Logic to route to appropriate technician based on intent
    console.log(`[AGI Router] Routing message with intent "${intent}" to technician pool`);
    // Implementation would notify available technicians
  }
}

/* ----------------------------- Chat Server ----------------------------- */

class UltraWebSocketServer {
  private app: express.Application;
  private server: http.Server;
  private io: Server;
  private rooms: Map<string, Room> = new Map();
  private connections: Map<string, UserConnection> = new Map();
  private agiGateway: AGIGateway;
  private logFile: string;

  constructor() {
    this.app = express();
    this.server = http.createServer(this.app);
    this.io = new Server(this.server, {
      cors: {
        origin: "*",
        methods: ["GET", "POST"]
      }
    });
    this.agiGateway = new AGIGateway();
    this.logFile = path.join(process.cwd(), 'logs', 'websocket-chat.log');
    
    this.setupMiddleware();
    this.setupRoutes();
    this.setupSocketHandlers();
  }

  private setupMiddleware() {
    this.app.use(cors());
    this.app.use(express.json());
    this.app.use(express.static('public'));
  }

  private setupRoutes() {
    // Get all messages for a room
    this.app.get('/api/chat/messages/:roomId', (req, res) => {
      const room = this.rooms.get(req.params.roomId);
      if (room) {
        res.json({
          success: true,
          messages: room.messages,
          room: {
            id: room.id,
            name: room.name,
            type: room.type,
            clientCount: room.clients.size,
            technicianCount: room.technicians.size
          }
        });
      } else {
        res.status(404).json({ success: false, error: 'Room not found' });
      }
    });

    // Get server statistics
    this.app.get('/api/chat/stats', (req, res) => {
      res.json({
        success: true,
        stats: {
          totalRooms: this.rooms.size,
          totalConnections: this.connections.size,
          activeClients: Array.from(this.connections.values()).filter(c => c.role === 'client').length,
          activeTechnicians: Array.from(this.connections.values()).filter(c => c.role === 'technician').length,
          uptime: process.uptime(),
          timestamp: new Date().toISOString()
        }
      });
    });

    // Create new room
    this.app.post('/api/chat/rooms', (req, res) => {
      const { name, type = 'general' } = req.body;
      const roomId = `room_${Date.now()}`;
      
      const room: Room = {
        id: roomId,
        name: name || `Room ${roomId}`,
        type,
        clients: new Set(),
        technicians: new Set(),
        messages: [],
        created: new Date().toISOString(),
        lastActivity: new Date().toISOString()
      };
      
      this.rooms.set(roomId, room);
      
      res.json({
        success: true,
        room: {
          id: room.id,
          name: room.name,
          type: room.type,
          created: room.created
        }
      });
    });
  }

  private setupSocketHandlers() {
    this.io.on('connection', (socket) => {
      console.log(`🔗 New connection: ${socket.id}`);

      // User joins with role
      socket.on('join', async (data) => {
        const { room, role, name = 'Anonymous' } = data;
        
        // Create connection record
        const connection: UserConnection = {
          id: socket.id,
          socketId: socket.id,
          role: role || 'client',
          name,
          room: room || 'general',
          connected: new Date().toISOString()
        };
        
        this.connections.set(socket.id, connection);
        
        // Join socket room
        socket.join(room);
        
        // Add to room tracking
        let roomData = this.rooms.get(room);
        if (!roomData) {
          roomData = {
            id: room,
            name: `Room ${room}`,
            type: 'general',
            clients: new Set(),
            technicians: new Set(),
            messages: [],
            created: new Date().toISOString(),
            lastActivity: new Date().toISOString()
          };
          this.rooms.set(room, roomData);
        }
        
        if (role === 'technician') {
          roomData.technicians.add(socket.id);
        } else {
          roomData.clients.add(socket.id);
        }
        
        // Notify room about new user
        const systemMessage: ChatMessage = {
          id: `sys_${Date.now()}`,
          role: 'system',
          text: `${name} (${role}) u bashkua në dhomë`,
          room,
          timestamp: new Date().toISOString()
        };
        
        roomData.messages.push(systemMessage);
        this.io.to(room).emit('message', systemMessage);
        this.io.to(room).emit('userJoined', { user: connection, room: roomData });
        
        await this.logInteraction('user_joined', { connection, room });
        
        console.log(`👤 ${name} (${role}) joined room: ${room}`);
      });

      // Handle new message
      socket.on('message', async (messageData) => {
        try {
          const connection = this.connections.get(socket.id);
          if (!connection) return;

          const message: ChatMessage = {
            id: `msg_${Date.now()}_${socket.id}`,
            role: connection.role,
            text: messageData.text,
            room: messageData.room || connection.room,
            timestamp: new Date().toISOString(),
            userId: socket.id,
            userName: connection.name
          };

          // Store message in room
          const room = this.rooms.get(message.room);
          if (room) {
            room.messages.push(message);
            room.lastActivity = new Date().toISOString();
            
            // Broadcast to room
            this.io.to(message.room).emit('message', message);
            
            // Try AGI processing for client messages
            if (message.role === 'client') {
              const agiResponse = await this.agiGateway.processMessage(message);
              
              if (agiResponse) {
                room.messages.push(agiResponse);
                
                // Send AGI response after short delay
                setTimeout(() => {
                  this.io.to(message.room).emit('message', agiResponse);
                  this.io.to(message.room).emit('typingStop', { user: 'AGI' });
                }, 1500);
                
                // Show typing indicator
                this.io.to(message.room).emit('typingStart', { user: 'AGI Assistant' });
                
                // Route to technician if needed
                if (agiResponse.intent === 'support_request') {
                  await this.agiGateway.routeToTechnician(message, agiResponse.intent);
                }
              }
            }
          }

          await this.logInteraction('message_sent', { message, connection });
          console.log(`💬 [${message.room}] ${connection.name}: ${message.text}`);

        } catch (error) {
          console.error('Message handling error:', error);
          socket.emit('error', { message: 'Failed to process message' });
        }
      });

      // Typing indicators
      socket.on('typing', (data) => {
        const connection = this.connections.get(socket.id);
        if (connection) {
          socket.to(data.room).emit('typingStart', { 
            user: connection.name,
            role: connection.role 
          });
        }
      });

      socket.on('stopTyping', (data) => {
        const connection = this.connections.get(socket.id);
        if (connection) {
          socket.to(data.room).emit('typingStop', { 
            user: connection.name,
            role: connection.role 
          });
        }
      });

      // Handle disconnect
      socket.on('disconnect', async () => {
        const connection = this.connections.get(socket.id);
        if (connection) {
          // Remove from room tracking
          const room = this.rooms.get(connection.room);
          if (room) {
            if (connection.role === 'technician') {
              room.technicians.delete(socket.id);
            } else {
              room.clients.delete(socket.id);
            }
            
            // Notify room about user leaving
            const systemMessage: ChatMessage = {
              id: `sys_${Date.now()}`,
              role: 'system',
              text: `${connection.name} (${connection.role}) doli nga dhoma`,
              room: connection.room,
              timestamp: new Date().toISOString()
            };
            
            room.messages.push(systemMessage);
            this.io.to(connection.room).emit('message', systemMessage);
            this.io.to(connection.room).emit('userLeft', { user: connection });
          }
          
          this.connections.delete(socket.id);
          await this.logInteraction('user_disconnected', { connection });
        }
        
        console.log(`❌ ${socket.id} disconnected`);
      });
    });
  }

  private async logInteraction(type: string, data: any) {
    try {
      const logEntry = {
        timestamp: new Date().toISOString(),
        type,
        data
      };
      
      // Ensure logs directory exists
      await fs.mkdir(path.dirname(this.logFile), { recursive: true });
      await fs.appendFile(this.logFile, JSON.stringify(logEntry) + '\n');
    } catch (error) {
      console.error('[Logging Error]:', error);
    }
  }

  public start(port: number = 8080) {
    this.server.listen(port, () => {
      console.log('🚀 UltraWebSocket Chat Server ACTIVE');
      console.log(`📡 WebSocket Server: http://localhost:${port}`);
      console.log(`🧠 AGI Gateway: ENABLED`);
      console.log(`👥 Multi-Role Support: Client ↔ Technician`);
      console.log(`📊 Real-time Analytics: /api/chat/stats`);
    });
  }
}

/* ----------------------------- Start Server ----------------------------- */

const chatServer = new UltraWebSocketServer();
chatServer.start(8080);

export default UltraWebSocketServer;
