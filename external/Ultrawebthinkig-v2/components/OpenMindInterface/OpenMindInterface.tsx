'use client';
'use strict';

import { useState, useEffect, useCallback, type ChangeEvent, type KeyboardEvent } from 'react';
import { motion, AnimatePresence } from '@/lib/web8-motion';
import { cva } from 'class-variance-authority';
import OpenMindClient, { type OpenMindResponse, type ConversationHistory } from '@/scripts/openmind-client';
import styles from './OpenMindInterface.module.css';

interface OpenMindInterfaceProps {
  theme?: 'neural' | 'creative' | 'analytical' | 'minimal';
  mode?: 'chat' | 'analysis' | 'exploration' | 'research';
  autoSave?: boolean;
  showMetadata?: boolean;
  onResponse?: (response: OpenMindResponse) => void;
}

export type { OpenMindInterfaceProps };

const interfaceContainerVariants = cva(styles.interfaceContainer, {
  variants: {
    theme: {
      neural: styles.neuralTheme,
      creative: styles.creativeTheme,
      analytical: styles.analyticalTheme,
      minimal: styles.minimalTheme
    },
    mode: {
      chat: styles.chatMode,
      analysis: styles.analysisMode,
      exploration: styles.explorationMode,
      research: styles.researchMode
    }
  },
  defaultVariants: {
    theme: 'neural',
    mode: 'chat'
  }
});

const messageVariants = cva(styles.message, {
  variants: {
    type: {
      user: styles.userMessage,
      assistant: styles.assistantMessage,
      system: styles.systemMessage,
      error: styles.errorMessage
    },
    confidence: {
      low: styles.lowConfidence,
      medium: styles.mediumConfidence,
      high: styles.highConfidence,
      very_high: styles.veryHighConfidence
    }
  }
});

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'error';
  content: string;
  timestamp: number;
  metadata?: {
    confidence?: number;
    processingTime?: number;
    complexity?: number;
    perspectives?: unknown;
  };
}

export const OpenMindInterface = ({
  theme = 'neural',
  mode = 'chat',
  autoSave = true,
  showMetadata = true,
  onResponse
}: OpenMindInterfaceProps) => {
  const [client] = useState(() => new OpenMindClient({ debug: true }));
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedMode, setSelectedMode] = useState<'analysis' | 'creative' | 'logical' | 'emotional' | 'comprehensive'>('comprehensive');
  const [selectedDepth, setSelectedDepth] = useState<'surface' | 'medium' | 'deep' | 'profound'>('medium');
  const [showPerspectives, setShowPerspectives] = useState(false);
  const [conversationStats, setConversationStats] = useState({
    totalQueries: 0,
    averageConfidence: 0,
    averageProcessingTime: 0,
    totalTokensUsed: 0
  });

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: ChatMessage = {
      id: 'welcome',
      type: 'system',
      content: '🧠 Welcome to OpenMind - Multi-perspective AI reasoning system. Ask me anything and I\'ll provide insights from logical, creative, emotional, and analytical perspectives.',
      timestamp: Date.now()
    };
    setMessages([welcomeMessage]);
  }, []);

  // Update conversation statistics
  useEffect(() => {
    const assistantMessages = messages.filter(m => m.type === 'assistant' && m.metadata);
    if (assistantMessages.length > 0) {
      const totalQueries = assistantMessages.length;
      const averageConfidence = assistantMessages.reduce((acc, m) => acc + (m.metadata?.confidence || 0), 0) / totalQueries;
      const averageProcessingTime = assistantMessages.reduce((acc, m) => acc + (m.metadata?.processingTime || 0), 0) / totalQueries;
      const totalTokensUsed = assistantMessages.reduce((acc, m) => acc + (m.metadata?.processingTime || 0), 0);

      setConversationStats({
        totalQueries,
        averageConfidence,
        averageProcessingTime,
        totalTokensUsed
      });
    }
  }, [messages]);

  const addMessage = useCallback((message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now()
    };
    
    setMessages(prev => [...prev, newMessage]);
  }, []);

  const handleSubmit = useCallback(async (input: string) => {
    if (!input.trim()) return;
    
    // Add user message
    addMessage({
      type: 'user',
      content: input.trim()
    });
    
    try {
      const response = await client.sendMessage(input.trim());
      
      // Add assistant response
      addMessage({
        type: 'assistant',
        content: response.content,
        metadata: {
          confidence: response.confidence,
          processingTime: response.processingTime,
          complexity: response.complexity,
          perspectives: response.perspectives
        }
      });
      
      if (onResponse) {
        onResponse(response);
      }
    } catch (error) {
      addMessage({
        type: 'error',
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      });
    }
  }, [client, addMessage, onResponse]);

  return (
    <div className={interfaceContainerVariants({ theme, mode })}>
      <div className={styles['messagesContainer']}>
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              className={`${styles['message']} ${styles[`${message.type}Message`]}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className={styles['messageContent']}>
                {message.content}
              </div>
              {showMetadata && message.metadata && (
                <div className={styles['messageMetadata']}>
                  {message.metadata.confidence && (
                    <span>Confidence: {(message.metadata.confidence * 100).toFixed(1)}%</span>
                  )}
                  {message.metadata.processingTime && (
                    <span>Time: {message.metadata.processingTime}ms</span>
                  )}
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
      
      <div className={styles['inputContainer']}>
        <input
          type="text"
          value={inputValue}
          onChange={(e: ChangeEvent<HTMLInputElement>) => setInputValue(e.target.value)}
          onKeyPress={(e: KeyboardEvent<HTMLInputElement>) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(inputValue);
              setInputValue('');
            }
          }}
          placeholder="Ask OpenMind anything..."
          className={styles['messageInput']}
        />
        <button
          onClick={() => {
            handleSubmit(inputValue);
            setInputValue('');
          }}
          disabled={!inputValue.trim()}
          className={styles['sendButton']}
        >
          Send
        </button>
      </div>
    </div>
  );
};