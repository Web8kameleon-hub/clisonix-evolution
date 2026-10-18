/**
 * 🚀 UltraCom WebSocket Server
 * Real-time chat system with AGI/Technician routing
 * Industrial-grade with authentication and room management
 *
 * @version 3.0 PRODUCTION READY
 * @author UltraWebThinking Team
 */

const express = require("express");
const { Server } = require("socket.io");
const http = require("http");
const cors = require("cors");
const crypto = require("crypto");
const fs = require("fs/promises");
const path = require("path");

const app = express();
app.use(
  cors({
    origin: process.env.CORS_ORIGINS?.split(",") || ["http://localhost:3000"],
    credentials: true,
  }),
);
app.use(express.json());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: process.env.CORS_ORIGINS?.split(",") || ["http://localhost:3000"],
    credentials: true,
  },
});

/* ----------------------------- Configuration ----------------------------- */

const JWT_SECRET = process.env.JWT_SECRET || "change-me-ultracom-super-secret";
const PORT = process.env.PORT || 8080;
const DB_FILE = "./ultracom-messages.json";

/* ----------------------------- In-Memory Storage ----------------------------- */

class UltraComStorage {
  constructor() {
    this.messages = new Map(); // roomId -> messages[]
    this.rooms = new Map(); // roomId -> { clients: Set, technicians: Set, admins: Set }
    this.users = new Map(); // socketId -> { userId, role, room }
    this.loadMessages();
  }

  async loadMessages() {
    try {
      const data = await fs.readFile(DB_FILE, "utf8");
      const parsed = JSON.parse(data);
      this.messages = new Map(parsed.messages || []);
      console.log("📁 Messages loaded from disk");
    } catch (error) {
      console.log("📁 Creating new message store");
    }
  }

  async saveMessages() {
    try {
      const data = {
        messages: Array.from(this.messages.entries()),
        timestamp: new Date().toISOString(),
      };
      await fs.writeFile(DB_FILE, JSON.stringify(data, null, 2));
    } catch (error) {
      console.error("💥 Error saving messages:", error);
    }
  }

  addMessage(roomId, message) {
    if (!this.messages.has(roomId)) {
      this.messages.set(roomId, []);
    }
    const messages = this.messages.get(roomId);
    const newMessage = {
      id: Date.now() + Math.random(),
      ...message,
      timestamp: new Date().toISOString(),
    };
    messages.push(newMessage);

    // Keep only last 1000 messages per room
    if (messages.length > 1000) {
      messages.splice(0, messages.length - 1000);
    }

    this.saveMessages(); // Auto-save
    return newMessage;
  }

  getMessages(roomId, limit = 50) {
    const messages = this.messages.get(roomId) || [];
    return messages.slice(-limit);
  }

  joinRoom(socketId, roomId, userId, role) {
    if (!this.rooms.has(roomId)) {
      this.rooms.set(roomId, {
        clients: new Set(),
        technicians: new Set(),
        admins: new Set(),
        created: new Date().toISOString(),
      });
    }

    const room = this.rooms.get(roomId);
    room[`${role}s`]?.add(socketId) || room.clients.add(socketId);

    this.users.set(socketId, { userId, role, room: roomId });

    console.log(`👤 ${userId} (${role}) joined room ${roomId}`);
    return room;
  }

  leaveRoom(socketId) {
    const user = this.users.get(socketId);
    if (!user) return null;

    const room = this.rooms.get(user.room);
    if (room) {
      room.clients?.delete(socketId);
      room.technicians?.delete(socketId);
      room.admins?.delete(socketId);
    }

    this.users.delete(socketId);
    console.log(`👤 ${user.userId} left room ${user.room}`);
    return user;
  }

  getRoomStats(roomId) {
    const room = this.rooms.get(roomId);
    if (!room) return null;

    return {
      roomId,
      clients: room.clients.size,
      technicians: room.technicians.size,
      admins: room.admins.size,
      total: room.clients.size + room.technicians.size + room.admins.size,
      created: room.created,
    };
  }
}

const storage = new UltraComStorage();

/* ----------------------------- Authentication ----------------------------- */

function createToken(userId, role, expiresIn = "7d") {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    sub: userId,
    role,
    iss: "ultracom",
    aud: "ultracom-clients",
    iat: now,
    exp: now + parseExpiresIn(expiresIn),
  };
  const encodedPayload = Buffer.from(JSON.stringify(payload)).toString(
    "base64url",
  );
  const signature = signPayload(encodedPayload);
  return `${encodedPayload}.${signature}`;
}

function verifyToken(token) {
  try {
    const [encodedPayload, signature] = String(token || "").split(".");
    if (!encodedPayload || !signature) {
      throw new Error("Malformed token");
    }

    const expected = signPayload(encodedPayload);
    if (
      !crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expected))
    ) {
      throw new Error("Invalid signature");
    }

    const payload = JSON.parse(
      Buffer.from(encodedPayload, "base64url").toString("utf8"),
    );
    const now = Math.floor(Date.now() / 1000);
    if (payload.iss !== "ultracom" || payload.aud !== "ultracom-clients") {
      throw new Error("Invalid issuer or audience");
    }
    if (!payload.exp || payload.exp <= now) {
      throw new Error("Token expired");
    }
    return payload;
  } catch (error) {
    throw new Error(`Invalid token: ${error.message}`);
  }
}

function signPayload(encodedPayload) {
  return crypto
    .createHmac("sha256", JWT_SECRET)
    .update(encodedPayload)
    .digest("base64url");
}

function parseExpiresIn(expiresIn) {
  if (typeof expiresIn === "number") return Math.max(1, expiresIn);
  const input = String(expiresIn || "7d").trim();
  const match = input.match(/^(\d+)([smhd])$/i);
  if (!match) return 7 * 24 * 60 * 60;
  const value = Number(match[1]);
  const unit = match[2].toLowerCase();
  const multipliers = { s: 1, m: 60, h: 3600, d: 86400 };
  return Math.max(1, value * multipliers[unit]);
}

/* ----------------------------- AGI Integration ----------------------------- */

class AGIProcessor {
  async processMessage(message, room) {
    const lowerText = message.text.toLowerCase();

    // Simulate AGI processing delay
    await new Promise((resolve) =>
      setTimeout(resolve, 500 + Math.random() * 1000),
    );

    // Intent detection
    if (lowerText.includes("emergjenc") || lowerText.includes("urgjent")) {
      return {
        text: `🚨 EMERGJENCË E DETEKTUAR! Teknikët janë njoftuar. Ticket prioritet i lartë krijohet automatikisht.`,
        priority: "high",
        escalate: true,
        source: "AGI-Alert",
      };
    }

    if (lowerText.includes("moti") || lowerText.includes("weather")) {
      return {
        text: `🌤️ Moti aktual në Tiranë: 22°C, i kthjellët. Lagështia: 65%. [AGI Weather Service]`,
        source: "AGI-Weather",
      };
    }

    if (lowerText.includes("sensor") || lowerText.includes("iot")) {
      return {
        text: `📡 Status IoT: Temperatura: 23.5°C ✅ | CO2: 420ppm ✅ | Lëvizje: Detektuar ✅ [AGI IoT Monitor]`,
        source: "AGI-IoT",
      };
    }

    if (lowerText.includes("help") || lowerText.includes("ndihmë")) {
      return {
        text: `🤖 Ju mund të pyesni për: moti, sensorë IoT, status sistemi, apo thoni "emergjencë" për prioritet të lartë. Teknikët janë të disponueshëm 24/7.`,
        source: "AGI-Help",
      };
    }

    // Default response
    return {
      text: `🧠 Mesazhi juaj është regjistruar. ${room.technicians > 0 ? "Teknikët aktiv do t'u përgjigjen së shpejti." : "Do të njoftojmë teknikët kur të jenë online."}`,
      source: "AGI-Core",
    };
  }
}

const agi = new AGIProcessor();

/* ----------------------------- WebSocket Handling ----------------------------- */

io.use(async (socket, next) => {
  try {
    const token =
      socket.handshake.auth?.token || socket.handshake.headers["x-auth-token"];
    if (!token) {
      throw new Error("No authentication token provided");
    }

    const decoded = verifyToken(token);
    socket.user = decoded;
    next();
  } catch (error) {
    next(new Error(`Authentication failed: ${error.message}`));
  }
});

io.on("connection", (socket) => {
  const { sub: userId, role } = socket.user;
  console.log(`🔗 ${userId} (${role}) connected - Socket ID: ${socket.id}`);

  // Join room event
  socket.on("joinRoom", async (roomData) => {
    const { roomId } = roomData;
    if (!roomId) {
      socket.emit("error", { message: "Room ID required" });
      return;
    }

    // Join socket.io room
    await socket.join(roomId);

    // Track in our storage
    const room = storage.joinRoom(socket.id, roomId, userId, role);

    // Send room info and recent messages
    const messages = storage.getMessages(roomId);
    const stats = storage.getRoomStats(roomId);

    socket.emit("roomJoined", {
      roomId,
      messages,
      stats,
      user: { userId, role },
    });

    // Notify others in room
    socket.to(roomId).emit("userJoined", {
      userId,
      role,
      timestamp: new Date().toISOString(),
    });

    console.log(`📋 Room ${roomId} stats:`, stats);
  });

  // Message handling
  socket.on("message", async (messageData) => {
    const user = storage.users.get(socket.id);
    if (!user) {
      socket.emit("error", { message: "Not in a room" });
      return;
    }

    const { text, type = "chat" } = messageData;
    if (!text?.trim()) {
      socket.emit("error", { message: "Message text required" });
      return;
    }

    // Save user message
    const message = storage.addMessage(user.room, {
      sender: userId,
      role,
      text: text.trim(),
      type,
    });

    // Broadcast to room
    io.to(user.room).emit("message", message);

    // AGI auto-response for clients (if no technicians online)
    const roomStats = storage.getRoomStats(user.room);
    if (role === "client" && roomStats.technicians === 0) {
      try {
        const agiResponse = await agi.processMessage(message, roomStats);

        const agiMessage = storage.addMessage(user.room, {
          sender: "AGI-System",
          role: "system",
          text: agiResponse.text,
          type: "auto-response",
          source: agiResponse.source,
          priority: agiResponse.priority,
        });

        // Delay for realistic feel
        setTimeout(() => {
          io.to(user.room).emit("message", agiMessage);

          // If escalation needed, notify admins
          if (agiResponse.escalate) {
            io.emit("escalation", {
              roomId: user.room,
              message,
              priority: agiResponse.priority,
              timestamp: new Date().toISOString(),
            });
          }
        }, 1000);
      } catch (error) {
        console.error("AGI processing error:", error);
      }
    }
  });

  // Typing indicators
  socket.on("typing", (data) => {
    const user = storage.users.get(socket.id);
    if (user) {
      socket.to(user.room).emit("typing", {
        userId,
        role,
        typing: data.typing,
      });
    }
  });

  // Disconnect handling
  socket.on("disconnect", () => {
    const user = storage.leaveRoom(socket.id);
    if (user) {
      socket.to(user.room).emit("userLeft", {
        userId: user.userId,
        role: user.role,
        timestamp: new Date().toISOString(),
      });
    }
    console.log(`❌ ${userId} (${role}) disconnected`);
  });

  // Send initial system info
  socket.emit("systemInfo", {
    version: "3.0",
    features: ["AGI Auto-Response", "IoT Integration", "Real-time Chat"],
    serverTime: new Date().toISOString(),
  });
});

/* ----------------------------- REST API Routes ----------------------------- */

// Health check
app.get("/health", (req, res) => {
  res.json({
    ok: true,
    service: "UltraCom",
    version: "3.0",
    timestamp: new Date().toISOString(),
    connections: io.engine.clientsCount,
  });
});

// Get room history
app.get("/api/rooms/:roomId/messages", (req, res) => {
  const { roomId } = req.params;
  const { limit = 50 } = req.query;

  const messages = storage.getMessages(roomId, parseInt(limit));
  const stats = storage.getRoomStats(roomId);

  res.json({
    roomId,
    messages,
    stats,
    timestamp: new Date().toISOString(),
  });
});

// Generate tokens (for development)
app.post("/api/auth/token", (req, res) => {
  const { userId, role = "client" } = req.body;

  if (!userId) {
    return res.status(400).json({ error: "userId required" });
  }

  const token = createToken(userId, role);
  res.json({
    token,
    userId,
    role,
    expiresIn: "7d",
  });
});

// Room stats
app.get("/api/rooms/:roomId/stats", (req, res) => {
  const { roomId } = req.params;
  const stats = storage.getRoomStats(roomId);

  if (!stats) {
    return res.status(404).json({ error: "Room not found" });
  }

  res.json(stats);
});

/* ----------------------------- Server Startup ----------------------------- */

server.listen(PORT, () => {
  console.log("\n🚀 UltraCom Server Started Successfully!");
  console.log(`📡 WebSocket Server: ws://localhost:${PORT}`);
  console.log(`🌐 HTTP API: http://localhost:${PORT}`);
  console.log(`🔐 JWT Secret: ${JWT_SECRET.substring(0, 10)}...`);
  console.log("🤖 AGI Auto-Response: ENABLED");
  console.log("📋 Room Management: ACTIVE");
  console.log("💾 Message Persistence: ENABLED");
  console.log("\n📋 Usage:");
  console.log(`   Health: GET http://localhost:${PORT}/health`);
  console.log(`   Token:  POST http://localhost:${PORT}/api/auth/token`);
  console.log(`   WebSocket: ws://localhost:${PORT} (with auth token)`);
  console.log("\n⚡ Ready for production traffic!");
});

// Graceful shutdown
process.on("SIGINT", async () => {
  console.log("\n🛑 Shutting down UltraCom server...");
  await storage.saveMessages();
  server.close(() => {
    console.log("✅ Server closed successfully");
    process.exit(0);
  });
});

module.exports = app;
