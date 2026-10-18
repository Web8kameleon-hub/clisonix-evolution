/**
 * 🚀 UltraCom WebSocket Client
 * FastAPI + WebSocket Integration for Client ↔ Technician Communication
 * 
 * Features:
 * - JWT Authentication 
 * - Real-time messaging with WebSocket
 * - REST API fallback
 * - Role-based messaging (client/technician/admin)
 * - Room-based chat system
 * 
 * @version 1.0.0 ULTRACOM CLIENT
 * @author UltraWebThinking Team
 */

export interface UltraComMessage {
  id: number;
  room: string;
  role: 'client' | 'technician' | 'admin';
  sender: string;
  text: string;
  ts: string;
}

export interface UltraComPresence {
  user: string;
  role: 'client' | 'technician' | 'admin';
  event: 'join' | 'leave';
  ts: string;
}

export interface UltraComConfig {
  baseUrl: string;
  token: string;
  room: string;
  onMessage?: (message: UltraComMessage) => void;
  onPresence?: (presence: UltraComPresence) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: any) => void;
}

export class UltraComClient {
  private ws: WebSocket | null = null;
  private config: UltraComConfig;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(config: UltraComConfig) {
    this.config = config;
  }

  // Connect to WebSocket
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        const wsUrl = `${this.config.baseUrl.replace('http', 'ws')}/chat/ws/${this.config.room}?token=${encodeURIComponent(this.config.token)}`;
        
        console.log('[UltraCom] Connecting to:', wsUrl);
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('[UltraCom] Connected successfully');
          this.reconnectAttempts = 0;
          this.config.onConnect?.();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'message') {
              this.config.onMessage?.(data.data);
            } else if (data.type === 'presence') {
              this.config.onPresence?.(data.data);
            }
          } catch (error) {
            console.error('[UltraCom] Message parse error:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('[UltraCom] Connection closed:', event.code);
          this.ws = null;
          this.config.onDisconnect?.();
          
          // Auto-reconnect with exponential backoff
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            setTimeout(() => {
              this.reconnectAttempts++;
              console.log(`[UltraCom] Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
              this.connect();
            }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
          }
        };

        this.ws.onerror = (error) => {
          console.error('[UltraCom] WebSocket error:', error);
          this.config.onError?.(error);
          reject(error);
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  // Send message via WebSocket
  sendMessage(text: string): boolean {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('[UltraCom] WebSocket not connected');
      return false;
    }

    try {
      this.ws.send(JSON.stringify({ text }));
      return true;
    } catch (error) {
      console.error('[UltraCom] Send error:', error);
      return false;
    }
  }

  // Send message via REST API (fallback)
  async sendMessageREST(text: string, role?: string, sender?: string): Promise<UltraComMessage | null> {
    try {
      const response = await fetch(`${this.config.baseUrl}/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-auth-token': this.config.token
        },
        body: JSON.stringify({
          room: this.config.room,
          role: role || 'client',
          sender: sender || 'client',
          text
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[UltraCom] REST send error:', error);
      this.config.onError?.(error);
      return null;
    }
  }

  // Get message history via REST
  async getHistory(limit = 50, offset = 0): Promise<UltraComMessage[]> {
    try {
      const response = await fetch(`${this.config.baseUrl}/chat/history?room=${this.config.room}&limit=${limit}&offset=${offset}`, {
        headers: {
          'x-auth-token': this.config.token
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('[UltraCom] History error:', error);
      this.config.onError?.(error);
      return [];
    }
  }

  // Check system health
  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.config.baseUrl}/health`);
      const data = await response.json();
      return data.ok === true;
    } catch (error) {
      console.error('[UltraCom] Health check failed:', error);
      return false;
    }
  }

  // Disconnect
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  // Get connection status
  get isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

// JWT Token Generator (for testing)
export class UltraComAuth {
  static async createToken(secret: string, sub: string, role: 'client' | 'technician' | 'admin'): Promise<string> {
    // This is a basic implementation - in production, call your backend
    const header = {
      alg: 'HS256',
      typ: 'JWT'
    };

    const now = Math.floor(Date.now() / 1000);
    const payload = {
      sub,
      role,
      iss: 'ultracom',
      aud: 'ultracom-clients',
      iat: now,
      exp: now + (7 * 24 * 60 * 60) // 7 days
    };

    // In browser, you'd need a JWT library or call backend
    console.warn('[UltraCom] Token generation should be done on backend');
    return `fake.jwt.token.${role}.${sub}`;
  }
}

// Usage example
export const UltraComExample = {
  async initialize() {
    // Get JWT token from your auth system
    const token = await UltraComAuth.createToken('secret', 'client-007', 'client');
    
    const client = new UltraComClient({
      baseUrl: 'http://localhost:8080',
      token,
      room: 'support-ACME-42',
      
      onMessage: (msg) => {
        console.log('[Message]', msg);
        // Update UI with new message
      },
      
      onPresence: (presence) => {
        console.log('[Presence]', presence);
        // Update online users list
      },
      
      onConnect: () => {
        console.log('[Connected] Ready to chat');
      },
      
      onDisconnect: () => {
        console.log('[Disconnected] Connection lost');
      },
      
      onError: (error) => {
        console.error('[Error]', error);
      }
    });

    // Connect and load history
    await client.connect();
    const history = await client.getHistory(20);
    console.log('[History]', history);

    // Send a message
    client.sendMessage('Përshëndetje! Si mund t\'ju ndihmoj?');

    return client;
  }
};

console.log('🚀 UltraCom WebSocket Client - LOADED');
console.log('💬 FastAPI Integration: READY');
console.log('🔐 JWT Authentication: SUPPORTED');
console.log('📡 WebSocket + REST: ENABLED');
