'use client';

/**
 * 🚀 UltraCom React Client
 * WebSocket chat integration with Web8 Motion animations
 * Real-time client ↔ technician ↔ AGI communication
 * 
 * @version 3.0 PRODUCTION
 * @author UltraWebThinking Team
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { io, Socket } from 'socket.io-client';

/* ----------------------------- Types ----------------------------- */

interface Message {
  id: string | number;
  sender: string;
  role: 'client' | 'technician' | 'admin' | 'system';
  text: string;
  timestamp: string;
  type?: 'chat' | 'auto-response' | 'system';
  source?: string;
  priority?: 'low' | 'normal' | 'high';
}

interface RoomStats {
  roomId: string;
  clients: number;
  technicians: number;
  admins: number;
  total: number;
}

interface UltraComClientProps {
  serverUrl?: string;
  userId: string;
  role?: 'client' | 'technician' | 'admin';
  roomId: string;
  token?: string;
  className?: string;
}

/* ----------------------------- Animation Variants ----------------------------- */

const messageVariants = {
  incoming: {
    hidden: { opacity: 0, x: -30, scale: 0.95 },
    visible: { 
      opacity: 1, 
      x: 0, 
      scale: 1,
      transition: { type: 'spring', stiffness: 400, damping: 25 }
    },
    exit: { opacity: 0, x: -20, transition: { duration: 0.2 } }
  },
  
  outgoing: {
    hidden: { opacity: 0, x: 30, scale: 0.95 },
    visible: { 
      opacity: 1, 
      x: 0, 
      scale: 1,
      transition: { type: 'spring', stiffness: 400, damping: 25 }
    },
    exit: { opacity: 0, x: 20, transition: { duration: 0.2 } }
  },
  
  system: {
    hidden: { opacity: 0, y: -10, scale: 0.9 },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { type: 'spring', stiffness: 500, damping: 30 }
    },
    exit: { opacity: 0, scale: 0.9, transition: { duration: 0.2 } }
  }
};

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1
    }
  }
};

/* ----------------------------- Message Component ----------------------------- */

interface MessageProps {
  message: Message;
  isOwn: boolean;
  currentUserId: string;
}

const MessageBubble: React.FC<MessageProps> = ({ message, isOwn, currentUserId }) => {
  const getMessageStyle = () => {
    if (message.role === 'system') {
      return {
        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
        color: 'white',
        textAlign: 'center' as const,
        fontSize: '0.9rem',
        padding: '8px 16px',
        borderRadius: '12px',
        margin: '8px auto',
        maxWidth: '80%'
      };
    }

    if (isOwn) {
      return {
        background: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
        color: 'white',
        marginLeft: 'auto',
        marginRight: '0',
        borderRadius: '18px 18px 4px 18px'
      };
    }

    // Incoming messages with role-based colors
    const roleColors = {
      technician: 'linear-gradient(135deg, #10b981, #059669)',
      admin: 'linear-gradient(135deg, #f59e0b, #d97706)',
      client: 'linear-gradient(135deg, #e5e7eb, #f3f4f6)',
      system: 'linear-gradient(135deg, #6366f1, #8b5cf6)'
    };

    return {
      background: roleColors[message.role] || roleColors.client,
      color: message.role === 'client' ? '#1f2937' : 'white',
      marginLeft: '0',
      marginRight: 'auto',
      borderRadius: '18px 18px 18px 4px'
    };
  };

  const getRoleIcon = () => {
    const icons = {
      client: '👤',
      technician: '🔧',
      admin: '👑',
      system: '🤖'
    };
    return icons[message.role] || '💬';
  };

  const messageType = message.role === 'system' ? 'system' : (isOwn ? 'outgoing' : 'incoming');

  return (
    <motion.div
      className="message-container"
      variants={messageVariants[messageType]}
      initial="hidden"
      animate="visible"
      exit="exit"
      style={{
        display: 'flex',
        flexDirection: isOwn ? 'row-reverse' : 'row',
        alignItems: 'flex-end',
        gap: '8px',
        marginBottom: '12px'
      }}
    >
      {!isOwn && message.role !== 'system' && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: 'spring', stiffness: 500 }}
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: message.role === 'technician' ? '#10b981' : message.role === 'admin' ? '#f59e0b' : '#6b7280',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '16px',
            flexShrink: 0
          }}
        >
          {getRoleIcon()}
        </motion.div>
      )}

      <div style={{ maxWidth: message.role === 'system' ? '100%' : '70%' }}>
        <motion.div
          style={{
            ...getMessageStyle(),
            padding: '12px 16px',
            wordWrap: 'break-word',
            boxShadow: '0 2px 12px rgba(0,0,0,0.1)',
            position: 'relative'
          }}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <div>{message.text}</div>
          
          {/* Message metadata */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.7 }}
            transition={{ delay: 0.5 }}
            style={{
              fontSize: '0.75rem',
              marginTop: '6px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <span>
              {message.sender !== currentUserId && `${message.sender} • `}
              {message.source && `[${message.source}]`}
            </span>
            <span>
              {new Date(message.timestamp).toLocaleTimeString('sq-AL', {
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  );
};

/* ----------------------------- Typing Indicator ----------------------------- */

const TypingIndicator: React.FC<{ users: Array<{userId: string, role: string}> }> = ({ users }) => {
  if (users.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 16px',
        background: '#f3f4f6',
        borderRadius: '12px',
        margin: '8px 0',
        fontSize: '0.9rem',
        color: '#6b7280'
      }}
    >
      <div style={{ display: 'flex', gap: '4px' }}>
        {[0, 1, 2].map(i => (
          <motion.div
            key={i}
            animate={{
              y: [0, -6, 0],
              opacity: [0.5, 1, 0.5]
            }}
            transition={{
              duration: 0.8,
              repeat: Infinity,
              delay: i * 0.1,
              ease: 'easeInOut'
            }}
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: '#6b7280'
            }}
          />
        ))}
      </div>
      <span>
        {users.length === 1 
          ? `${users[0].userId} po shkruan...`
          : `${users.length} përdorues po shkruajnë...`
        }
      </span>
    </motion.div>
  );
};

/* ----------------------------- Main UltraCom Client Component ----------------------------- */

export const UltraComClient: React.FC<UltraComClientProps> = ({
  serverUrl = '/backend',
  userId,
  role = 'client',
  roomId,
  token,
  className = ''
}) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [roomStats, setRoomStats] = useState<RoomStats | null>(null);
  const [typingUsers, setTypingUsers] = useState<Array<{userId: string, role: string}>>([]);
  const [error, setError] = useState<string | null>(null);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  /* ----------------------------- WebSocket Connection ----------------------------- */

  useEffect(() => {
    let newSocket: Socket;

    const connectSocket = async () => {
      try {
        // Get token if not provided
        let authToken = token;
        if (!authToken) {
          const tokenResponse = await fetch(`${serverUrl}/api/auth/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ userId, role })
          });
          const tokenData = await tokenResponse.json();
          authToken = tokenData.token;
        }

        newSocket = io(serverUrl, {
          auth: { token: authToken },
          transports: ['websocket', 'polling']
        });

        // Connection handlers
        newSocket.on('connect', () => {
          console.log('🔗 Connected to UltraCom server');
          setIsConnected(true);
          setError(null);
          
          // Join room immediately
          newSocket.emit('joinRoom', { roomId });
        });

        newSocket.on('disconnect', () => {
          console.log('❌ Disconnected from UltraCom server');
          setIsConnected(false);
        });

        newSocket.on('connect_error', (err) => {
          console.error('🚫 Connection error:', err.message);
          setError(`Connection error: ${err.message}`);
        });

        // Room events
        newSocket.on('roomJoined', (data) => {
          console.log('🏠 Joined room:', data.roomId);
          setMessages(data.messages || []);
          setRoomStats(data.stats);
        });

        // Message events
        newSocket.on('message', (message: Message) => {
          setMessages(prev => [...prev, message]);
        });

        // Typing events
        newSocket.on('typing', (data) => {
          setTypingUsers(prev => {
            const filtered = prev.filter(u => u.userId !== data.userId);
            if (data.typing) {
              return [...filtered, { userId: data.userId, role: data.role }];
            }
            return filtered;
          });
        });

        // User presence events
        newSocket.on('userJoined', (data) => {
          console.log(`👤 ${data.userId} (${data.role}) joined the room`);
        });

        newSocket.on('userLeft', (data) => {
          console.log(`👤 ${data.userId} (${data.role}) left the room`);
          setTypingUsers(prev => prev.filter(u => u.userId !== data.userId));
        });

        // System events
        newSocket.on('systemInfo', (data) => {
          console.log('ℹ️ System info:', data);
        });

        newSocket.on('escalation', (data) => {
          console.log('🚨 Escalation alert:', data);
          // Could trigger notifications here
        });

        setSocket(newSocket);

      } catch (error) {
        console.error('Failed to connect:', error);
        setError(`Failed to connect: ${error}`);
      }
    };

    connectSocket();

    return () => {
      if (newSocket) {
        newSocket.disconnect();
      }
    };
  }, [serverUrl, userId, role, roomId, token]);

  /* ----------------------------- Auto-scroll ----------------------------- */

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  /* ----------------------------- Send Message ----------------------------- */

  const sendMessage = useCallback(() => {
    if (!socket || !inputText.trim()) return;

    socket.emit('message', {
      text: inputText.trim(),
      type: 'chat'
    });

    setInputText('');
  }, [socket, inputText]);

  /* ----------------------------- Typing Handler ----------------------------- */

  const handleTyping = useCallback(() => {
    if (!socket) return;

    socket.emit('typing', { typing: true });

    // Clear previous timeout
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }

    // Stop typing after 2 seconds
    typingTimeoutRef.current = setTimeout(() => {
      socket.emit('typing', { typing: false });
    }, 2000);
  }, [socket]);

  /* ----------------------------- Input Handlers ----------------------------- */

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
    handleTyping();
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  /* ----------------------------- Render ----------------------------- */

  return (
    <div className={`ultracom-client ${className}`} style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      maxHeight: '600px',
      border: '1px solid #e5e7eb',
      borderRadius: '16px',
      overflow: 'hidden',
      background: '#ffffff',
      fontFamily: 'system-ui, -apple-system, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px',
        background: 'linear-gradient(135deg, #667eea, #764ba2)',
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ fontSize: '24px' }}>🚀</div>
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>
              UltraCom {role === 'client' ? 'Support' : 'Dashboard'}
            </h3>
            <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.9 }}>
              Room: {roomId} • {roomStats ? `${roomStats.total} online` : 'Connecting...'}
            </p>
          </div>
        </div>
        <div style={{
          width: '12px',
          height: '12px',
          borderRadius: '50%',
          background: isConnected ? '#10b981' : '#ef4444'
        }} />
      </div>

      {/* Error Display */}
      {error && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          style={{
            padding: '12px',
            background: '#fef2f2',
            color: '#dc2626',
            fontSize: '0.9rem',
            textAlign: 'center'
          }}
        >
          {error}
        </motion.div>
      )}

      {/* Messages Area */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        style={{
          flex: 1,
          overflow: 'auto',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              isOwn={message.sender === userId}
              currentUserId={userId}
            />
          ))}
        </AnimatePresence>
        
        <AnimatePresence>
          {typingUsers.length > 0 && (
            <TypingIndicator users={typingUsers} />
          )}
        </AnimatePresence>
        
        <div ref={messagesEndRef} />
      </motion.div>

      {/* Input Area */}
      <div style={{
        padding: '16px',
        borderTop: '1px solid #e5e7eb',
        background: '#f8fafc'
      }}>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
          <textarea
            value={inputText}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder={`Shkruaj mesazhin tuaj këtu... (Enter për dërgim)`}
            disabled={!isConnected}
            style={{
              flex: 1,
              resize: 'none',
              border: '2px solid #e5e7eb',
              borderRadius: '12px',
              padding: '12px',
              fontSize: '0.95rem',
              maxHeight: '120px',
              outline: 'none',
              transition: 'border-color 0.2s',
              background: isConnected ? 'white' : '#f3f4f6',
              cursor: isConnected ? 'text' : 'not-allowed'
            }}
            rows={1}
          />
          <motion.button
            onClick={sendMessage}
            disabled={!inputText.trim() || !isConnected}
            whileHover={{ scale: isConnected && inputText.trim() ? 1.05 : 1 }}
            whileTap={{ scale: isConnected && inputText.trim() ? 0.95 : 1 }}
            style={{
              padding: '12px 20px',
              background: isConnected && inputText.trim() 
                ? 'linear-gradient(135deg, #3b82f6, #1d4ed8)' 
                : '#d1d5db',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              fontSize: '0.9rem',
              fontWeight: 600,
              cursor: isConnected && inputText.trim() ? 'pointer' : 'not-allowed'
            }}
          >
            Dërgo
          </motion.button>
        </div>
      </div>
    </div>
  );
};

export default UltraComClient;
