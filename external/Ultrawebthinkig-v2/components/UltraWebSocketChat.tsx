'use client';

/**
 * 🚀 UltraWebSocket Chat Client
 * Real-time React component with ChatMotion integration
 * Connects to WebSocket server for Client ↔ Technician communication
 * 
 * @version 1.0 PRODUCTION CLIENT
 * @author UltraWebThinking Team
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import io, { Socket } from 'socket.io-client';
import { ChatMotion, TypingIndicator } from '../components/Web8ChatMotion';
import { motion } from 'framer-motion';

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

interface TypingUser {
  user: string;
  role: string;
}

interface UltraWebSocketChatProps {
  serverUrl?: string;
  roomId?: string;
  userRole?: 'client' | 'technician';
  userName?: string;
  className?: string;
  autoConnect?: boolean;
  showSystemMessages?: boolean;
}

/* ----------------------------- Main Component ----------------------------- */

export const UltraWebSocketChat: React.FC<UltraWebSocketChatProps> = ({
  serverUrl = '/backend',
  roomId = 'ultra-support',
  userRole = 'client',
  userName = 'User',
  className = '',
  autoConnect = true,
  showSystemMessages = true
}) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [typingUsers, setTypingUsers] = useState<TypingUser[]>([]);
  const [roomStats, setRoomStats] = useState({ clients: 0, technicians: 0 });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Connect to WebSocket server
  const connectToServer = useCallback(() => {
    if (isConnecting || isConnected) return;
    
    setIsConnecting(true);
    
    try {
      const newSocket = io(serverUrl, {
        transports: ['websocket', 'polling'],
        timeout: 10000,
        forceNew: true
      });

      // Connection events
      newSocket.on('connect', () => {
        console.log('🔗 Connected to WebSocket server');
        setIsConnected(true);
        setIsConnecting(false);
        
        // Join room with user info
        newSocket.emit('join', {
          room: roomId,
          role: userRole,
          name: userName
        });
      });

      newSocket.on('disconnect', () => {
        console.log('❌ Disconnected from server');
        setIsConnected(false);
        setIsConnecting(false);
      });

      newSocket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        setIsConnected(false);
        setIsConnecting(false);
      });

      // Message events
      newSocket.on('message', (message: ChatMessage) => {
        setMessages(prev => {
          // Avoid duplicates
          if (prev.find(m => m.id === message.id)) return prev;
          return [...prev, message];
        });
      });

      // Typing events
      newSocket.on('typingStart', (data: TypingUser) => {
        setTypingUsers(prev => {
          if (prev.find(u => u.user === data.user)) return prev;
          return [...prev, data];
        });
      });

      newSocket.on('typingStop', (data: TypingUser) => {
        setTypingUsers(prev => prev.filter(u => u.user !== data.user));
      });

      // Room events
      newSocket.on('userJoined', (data: any) => {
        if (data.room) {
          setRoomStats({
            clients: data.room.clients?.size || 0,
            technicians: data.room.technicians?.size || 0
          });
        }
      });

      newSocket.on('userLeft', (data: any) => {
        setTypingUsers(prev => prev.filter(u => u.user !== data.user?.name));
      });

      setSocket(newSocket);

    } catch (error) {
      console.error('Failed to connect:', error);
      setIsConnecting(false);
    }
  }, [serverUrl, roomId, userRole, userName, isConnecting, isConnected]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connectToServer();
    }

    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, [autoConnect, connectToServer]);

  // Handle typing indicators
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputText(value);

    if (socket && isConnected) {
      // Send typing indicator
      socket.emit('typing', { room: roomId });
      
      // Clear previous timeout
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
      
      // Stop typing after 2 seconds of inactivity
      typingTimeoutRef.current = setTimeout(() => {
        socket.emit('stopTyping', { room: roomId });
      }, 2000);
    }
  };

  // Send message
  const sendMessage = useCallback(() => {
    if (!inputText.trim() || !socket || !isConnected) return;

    const message = {
      text: inputText.trim(),
      room: roomId,
      timestamp: new Date().toISOString()
    };

    socket.emit('message', message);
    socket.emit('stopTyping', { room: roomId });
    
    setInputText('');
    inputRef.current?.focus();
    
    // Clear typing timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
  }, [inputText, socket, isConnected, roomId]);

  // Handle Enter key
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Disconnect from server
  const disconnectFromServer = () => {
    if (socket) {
      socket.disconnect();
      setSocket(null);
      setIsConnected(false);
      setMessages([]);
      setTypingUsers([]);
    }
  };

  // Get message source for ChatMotion
  const getMessageSource = (message: ChatMessage) => {
    switch (message.role) {
      case 'agi': return 'agi';
      case 'technician': return 'user';
      case 'system': return 'system';
      default: return 'user';
    }
  };

  // Get message type for ChatMotion
  const getMessageType = (message: ChatMessage) => {
    if (message.role === 'system') return 'system';
    if (message.role === userRole) return 'outgoing';
    return 'incoming';
  };

  return (
    <div className={`ultra-websocket-chat ${className}`} style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      maxHeight: '600px',
      border: '2px solid #e5e7eb',
      borderRadius: '16px',
      overflow: 'hidden',
      background: '#ffffff',
      boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
    }}>
      {/* Chat Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          padding: '16px',
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          color: 'white',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ fontSize: '24px' }}>
            {userRole === 'client' ? '👤' : '🧑‍🔧'}
          </div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>
              UltraWeb {userRole === 'client' ? 'Support' : 'Technician Portal'}
            </h3>
            <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.9 }}>
              {isConnected ? `Connected as ${userName}` : 'Disconnected'}
            </p>
          </div>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Room Statistics */}
          <div style={{ fontSize: '0.8rem', textAlign: 'right' }}>
            <div>👤 {roomStats.clients} clients</div>
            <div>🧑‍🔧 {roomStats.technicians} techs</div>
          </div>
          
          {/* Connection Status */}
          <div style={{
            width: '12px',
            height: '12px',
            borderRadius: '50%',
            background: isConnected ? '#10b981' : isConnecting ? '#f59e0b' : '#ef4444'
          }} />
        </div>
      </motion.div>

      {/* Messages Area */}
      <div style={{
        flex: 1,
        overflow: 'auto',
        padding: '16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px'
      }}>
        {!isConnected && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            style={{
              textAlign: 'center',
              padding: '32px',
              color: '#6b7280'
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔌</div>
            <h3>Not Connected</h3>
            <p>Click "Connect" to join the chat</p>
            <motion.button
              onClick={connectToServer}
              disabled={isConnecting}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{
                padding: '12px 24px',
                background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
                color: 'white',
                border: 'none',
                borderRadius: '12px',
                fontSize: '0.9rem',
                fontWeight: 600,
                cursor: 'pointer',
                marginTop: '16px'
              }}
            >
              {isConnecting ? 'Connecting...' : 'Connect'}
            </motion.button>
          </motion.div>
        )}

        {isConnected && messages.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            style={{
              textAlign: 'center',
              padding: '32px',
              color: '#6b7280'
            }}
          >
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
            <h3>Chat Started</h3>
            <p>Send your first message to begin the conversation</p>
          </motion.div>
        )}

        {/* Messages */}
        {messages.map(message => {
          if (!showSystemMessages && message.role === 'system') return null;
          
          return (
            <ChatMotion
              key={message.id}
              type={getMessageType(message) as any}
              source={getMessageSource(message)}
              timestamp={message.timestamp}
            >
              <div>
                {message.userName && message.role !== 'system' && (
                  <div style={{ 
                    fontSize: '0.8rem', 
                    fontWeight: 600, 
                    marginBottom: '4px',
                    color: '#6b7280'
                  }}>
                    {message.userName}
                  </div>
                )}
                {message.text}
                {message.isAgiResponse && (
                  <div style={{
                    fontSize: '0.75rem',
                    marginTop: '4px',
                    opacity: 0.7,
                    fontStyle: 'italic'
                  }}>
                    AGI Confidence: {Math.round((message.confidence || 0) * 100)}%
                  </div>
                )}
              </div>
            </ChatMotion>
          );
        })}

        {/* Typing Indicators */}
        {typingUsers.map(user => (
          <TypingIndicator key={user.user} source="agi" />
        ))}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      {isConnected && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            padding: '16px',
            borderTop: '1px solid #e5e7eb',
            background: '#f8fafc'
          }}
        >
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Shkruaj mesazhin tuaj këtu..."
              style={{
                flex: 1,
                border: '2px solid #e5e7eb',
                borderRadius: '12px',
                padding: '12px',
                fontSize: '0.95rem',
                outline: 'none',
                transition: 'border-color 0.2s',
                background: 'white'
              }}
            />
            <motion.button
              onClick={sendMessage}
              disabled={!inputText.trim()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{
                padding: '12px 20px',
                background: inputText.trim() 
                  ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)'
                  : '#e5e7eb',
                color: inputText.trim() ? 'white' : '#9ca3af',
                border: 'none',
                borderRadius: '12px',
                fontSize: '0.9rem',
                fontWeight: 600,
                cursor: inputText.trim() ? 'pointer' : 'not-allowed'
              }}
            >
              Dërgo
            </motion.button>
          </div>
        </motion.div>
      )}
    </div>
  );
};

/* ----------------------------- Example Usage Page ----------------------------- */

export default function UltraChatPage() {
  const [userRole, setUserRole] = useState<'client' | 'technician'>('client');
  const [userName, setUserName] = useState('');
  const [roomId, setRoomId] = useState('ultra-support');

  return (
    <div style={{ 
      padding: '24px', 
      maxWidth: '800px', 
      margin: '0 auto',
      background: '#f9fafb',
      minHeight: '100vh'
    }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: '24px', textAlign: 'center' }}
      >
        <h1 style={{ 
          fontSize: '2.5rem', 
          fontWeight: 700, 
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          color: 'transparent',
          marginBottom: '8px'
        }}>
          UltraWebSocket Chat
        </h1>
        <p style={{ color: '#6b7280', fontSize: '1.1rem' }}>
          Real-time communication with AGI gateway support
        </p>
      </motion.div>

      {/* Settings Panel */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.1 }}
        style={{
          background: 'white',
          padding: '20px',
          borderRadius: '16px',
          marginBottom: '24px',
          boxShadow: '0 4px 16px rgba(0,0,0,0.1)'
        }}
      >
        <h3 style={{ margin: '0 0 16px 0', color: '#374151' }}>Chat Settings</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>
              Your Name:
            </label>
            <input
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              placeholder="Enter your name"
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                padding: '8px 12px'
              }}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>
              Role:
            </label>
            <select
              value={userRole}
              onChange={(e) => setUserRole(e.target.value as 'client' | 'technician')}
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                padding: '8px 12px'
              }}
            >
              <option value="client">Client</option>
              <option value="technician">Technician</option>
            </select>
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 500 }}>
              Room:
            </label>
            <input
              type="text"
              value={roomId}
              onChange={(e) => setRoomId(e.target.value)}
              placeholder="Room ID"
              style={{
                width: '100%',
                border: '1px solid #d1d5db',
                borderRadius: '8px',
                padding: '8px 12px'
              }}
            />
          </div>
        </div>
      </motion.div>

      {/* Chat Component */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <UltraWebSocketChat
          userRole={userRole}
          userName={userName || `${userRole === 'client' ? 'Client' : 'Technician'}_${Math.floor(Math.random() * 1000)}`}
          roomId={roomId || 'ultra-support'}
          autoConnect={false}
        />
      </motion.div>
    </div>
  );
}

console.log('🚀 UltraWebSocket Chat Client - LOADED SUCCESSFULLY');
console.log('💬 Real-time WebSocket: ENABLED');
console.log('🧠 AGI Gateway Integration: READY');
console.log('🎨 ChatMotion Animations: ACTIVE');
