/**
 * EuroWeb Microservices - Shared Middleware
 */

import type { NextFunction, Request, Response } from 'express';
import jwt from 'jsonwebtoken';
import { JWT_CONFIG } from './config.js';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    email: string;
    role: string;
  };
}

export function authMiddleware(req: AuthenticatedRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Token mungon' });
  }

  const token = authHeader.split(' ')[1];

  try {
    const decoded = jwt.verify(token, JWT_CONFIG.secret) as AuthenticatedRequest['user'];
    req.user = decoded;
    next();
  } catch {
    return res.status(401).json({ error: 'Token i pavlefshëm' });
  }
}

export function errorHandler(err: Error, req: Request, res: Response, _next: NextFunction) {
  console.error('Error:', err.message);
  res.status(500).json({ 
    error: 'Gabim i brendshëm',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
}

export function requestLogger(serviceName: string) {
  return (req: Request, _res: Response, next: NextFunction) => {
    console.log(`[${serviceName}] ${req.method} ${req.path}`);
    next();
  };
}
