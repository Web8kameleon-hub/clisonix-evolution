/**
 * EuroWeb Auth Service - Port 4001
 * Autentifikimi dhe autorizimi
 */

import bcrypt from 'bcryptjs';
import cors from 'cors';
import express from 'express';
import helmet from 'helmet';
import jwt from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';
import { CORS_OPTIONS, JWT_CONFIG, PORTS } from '../shared/config.js';
import { createLogger } from '../shared/logger.js';
import { authMiddleware, errorHandler, requestLogger, type AuthenticatedRequest } from '../shared/middleware.js';

const app = express();
const logger = createLogger('auth');

app.use(helmet());
app.use(cors(CORS_OPTIONS));
app.use(express.json());
app.use(requestLogger('auth'));

// In-memory storage (replace with database in production)
const users = new Map<string, { id: string; email: string; password: string; role: string; createdAt: Date }>();
const refreshTokens = new Set<string>();

// Health check
app.get('/health', (_req, res) => {
  res.json({ service: 'auth', status: 'healthy', timestamp: new Date().toISOString() });
});

// Register
app.post('/register', async (req, res) => {
  try {
    const { email, password, role = 'user' } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'Email dhe fjalëkalimi janë të detyrueshme' });
    }

    if (Array.from(users.values()).find(u => u.email === email)) {
      return res.status(409).json({ error: 'Përdoruesi ekziston' });
    }

    const hashedPassword = await bcrypt.hash(password, 12);
    const id = uuidv4();

    users.set(id, {
      id,
      email,
      password: hashedPassword,
      role,
      createdAt: new Date()
    });

    const token = jwt.sign({ id, email, role }, JWT_CONFIG.secret, { expiresIn: JWT_CONFIG.expiresIn });
    const refreshToken = jwt.sign({ id }, JWT_CONFIG.secret, { expiresIn: JWT_CONFIG.refreshExpiresIn });
    refreshTokens.add(refreshToken);

    logger.info(`Përdorues i ri regjistruar: ${email}`);
    res.status(201).json({ token, refreshToken, user: { id, email, role } });
  } catch (error) {
    logger.error('Gabim në regjistrim:', error);
    res.status(500).json({ error: 'Gabim i brendshëm' });
  }
});

// Login
app.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    const user = Array.from(users.values()).find(u => u.email === email);
    if (!user) {
      return res.status(401).json({ error: 'Kredenciale të pavlefshme' });
    }

    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) {
      return res.status(401).json({ error: 'Kredenciale të pavlefshme' });
    }

    const token = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      JWT_CONFIG.secret,
      { expiresIn: JWT_CONFIG.expiresIn }
    );
    const refreshToken = jwt.sign({ id: user.id }, JWT_CONFIG.secret, { expiresIn: JWT_CONFIG.refreshExpiresIn });
    refreshTokens.add(refreshToken);

    logger.info(`Përdoruesi hyri: ${email}`);
    res.json({ token, refreshToken, user: { id: user.id, email: user.email, role: user.role } });
  } catch (error) {
    logger.error('Gabim në login:', error);
    res.status(500).json({ error: 'Gabim i brendshëm' });
  }
});

// Refresh token
app.post('/refresh', (req, res) => {
  const { refreshToken } = req.body;

  if (!refreshToken || !refreshTokens.has(refreshToken)) {
    return res.status(401).json({ error: 'Refresh token i pavlefshëm' });
  }

  try {
    const decoded = jwt.verify(refreshToken, JWT_CONFIG.secret) as { id: string };
    const user = users.get(decoded.id);

    if (!user) {
      return res.status(401).json({ error: 'Përdoruesi nuk ekziston' });
    }

    const newToken = jwt.sign(
      { id: user.id, email: user.email, role: user.role },
      JWT_CONFIG.secret,
      { expiresIn: JWT_CONFIG.expiresIn }
    );

    res.json({ token: newToken });
  } catch {
    res.status(401).json({ error: 'Refresh token i pavlefshëm' });
  }
});

// Get current user
app.get('/me', authMiddleware, (req: AuthenticatedRequest, res) => {
  res.json({ user: req.user });
});

// Logout
app.post('/logout', (req, res) => {
  const { refreshToken } = req.body;
  if (refreshToken) {
    refreshTokens.delete(refreshToken);
  }
  res.json({ message: 'Logout i suksesshëm' });
});

app.use(errorHandler);

app.listen(PORTS.AUTH, () => {
  logger.info(`🔐 Auth Service running on http://localhost:${PORTS.AUTH}`);
});

export default app;
