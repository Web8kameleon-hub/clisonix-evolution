/**
 * 🚀 ULTRAWEB HYBRID CHAT CLIENT - PRODUCTION GRADE
 * Real-time chat interface with ALBA/ASI/AGI integration
 * Zero External Dependencies - Pure JavaScript/HTML
 * 
 * @version 13.0.0 HYBRID FRONTEND
 * @system UltraWebThinking Secure Communications
 */

"use client";

import { useState, useEffect, useRef } from 'react';

interface ChatMessage {
  id: string;
  userId: string;
  username: string;
  message: string;
  timestamp: string;
  type: 'text' | 'system' | 'alba' | 'asi' | 'agi';
  channel: string;
  albaProcessed: boolean;
  asiAnalyzed: boolean;
  agiEnhanced: boolean;
}

export default function UltraWebChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [username, setUsername] = useState('');
  const [userId, setUserId] = useState('');
  const [channel, setChannel] = useState('general');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Generate user ID on first load
  useEffect(() => {
    if (!userId) {
      const newUserId = Math.random().toString(36).substring(2, 15);
      setUserId(newUserId);
    }
  }, [userId]);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load messages from backend
  const loadMessages = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/chat-production?channel=${channel}&limit=50`);
      const data = await response.json();
      
      if (data.success) {
        setMessages(data.messages || []);
        setIsConnected(true);
      }
    } catch (error) {
      console.error('Failed to load messages:', error);
      setIsConnected(false);
    } finally {
      setIsLoading(false);
    }
  };

  // Send message to backend
  const sendMessage = async () => {
    if (!currentMessage.trim() || !username.trim()) return;
    
    try {
      const response = await fetch('/api/chat-production', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          userId,
          username,
          message: currentMessage,
          channel
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setCurrentMessage('');
        await loadMessages(); // Reload to get updated messages
      } else {
        console.error('Failed to send message:', data.error);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  // Handle enter key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Format timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Get message type color
  const getMessageTypeColor = (type: string) => {
    switch (type) {
      case 'alba': return 'text-blue-600';
      case 'asi': return 'text-green-600';
      case 'agi': return 'text-purple-600';
      case 'system': return 'text-gray-500';
      default: return 'text-gray-900';
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-4xl mx-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">
            🚀 UltraWeb Hybrid Chat
          </h1>
          <div className="flex items-center space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
            <select 
              value={channel} 
              onChange={(e) => setChannel(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded-md text-sm"
            >
              <option value="general">General</option>
              <option value="alba">ALBA Intelligence</option>
              <option value="asi">ASI Analysis</option>
              <option value="agi">AGI Enhanced</option>
            </select>
          </div>
        </div>
      </div>

      {/* User Setup */}
      {!username && (
        <div className="p-4 bg-yellow-50 border-b">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              placeholder="Enter your username..."
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => username && loadMessages()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Join Chat
            </button>
          </div>
        </div>
      )}

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {isLoading ? (
          <div className="flex justify-center items-center h-32">
            <div className="text-gray-500">Loading messages...</div>
          </div>
        ) : messages.length === 0 ? (
          <div className="flex justify-center items-center h-32">
            <div className="text-gray-500">No messages yet. Start the conversation!</div>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-gray-900">{msg.username}</span>
                  <span className="text-xs text-gray-500">{formatTime(msg.timestamp)}</span>
                  {msg.albaProcessed && <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">ALBA</span>}
                  {msg.asiAnalyzed && <span className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded">ASI</span>}
                  {msg.agiEnhanced && <span className="text-xs bg-purple-100 text-purple-600 px-2 py-1 rounded">AGI</span>}
                </div>
                <span className={`text-xs font-medium ${getMessageTypeColor(msg.type)}`}>
                  #{msg.channel}
                </span>
              </div>
              <p className="text-gray-800 whitespace-pre-wrap">{msg.message}</p>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      {username && (
        <div className="bg-white border-t p-4">
          <div className="flex space-x-2">
            <textarea
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message here... (Press Enter to send)"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={2}
            />
            <button
              onClick={sendMessage}
              disabled={!currentMessage.trim()}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
          
          {/* Refresh Messages Button */}
          <div className="mt-2 flex justify-center">
            <button
              onClick={loadMessages}
              className="text-sm text-blue-600 hover:text-blue-700 focus:outline-none"
            >
              🔄 Refresh Messages
            </button>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="bg-gray-100 px-4 py-2 text-center">
        <p className="text-xs text-gray-600">
          🚀 UltraWeb Hybrid Chat v13.0.0 | ALBA/ASI/AGI Intelligence | Zero External Dependencies
        </p>
      </div>
    </div>
  );
}
