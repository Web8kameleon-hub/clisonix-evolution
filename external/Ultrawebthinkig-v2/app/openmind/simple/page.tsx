'use client';

import { useEffect, useRef, useState } from 'react';

interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface OpenMindResponse {
  query: string;
  responses: any[];
  serviceResults: Record<string, any>;
  synthesis: {
    mainResponse: string;
    sources: string[];
    confidence: number;
    openMindPrinciples: string[];
  };
  meta: {
    totalResponseTime: number;
    servicesQueried: number;
    ethicallyValidated: boolean;
  };
}

export default function SimpleOpenMindPage() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [isCompactMode, setIsCompactMode] = useState(true);
  const [showMemoryPanel, setShowMemoryPanel] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + 'px';
    }
  }, [query]);

  // Switch to expanded mode when conversation gets longer
  useEffect(() => {
    if (messages.length >= 4) {
      setIsCompactMode(false);
    }
  }, [messages.length]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: query,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const response = await fetch('/api/openmind', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: userMessage.content,
          options: {
            ethicalCheck: true,
            attributeSource: false, // No sources for simple chat
            maxResults: 3
          }
        }),
      });

      const data: OpenMindResponse = await response.json();
      
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: data.synthesis.mainResponse,
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: 'Na vjen keq, ndodhi një gabim. Ju lutem provoni përsëri.',
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([]);
    setIsCompactMode(true);
  };

  const toggleCompactMode = () => {
    setIsCompactMode(!isCompactMode);
  };

  const toggleMemoryPanel = () => {
    setShowMemoryPanel(!showMemoryPanel);
  };

  const handleFileUpload = async (file: File) => {
    setUploadingFile(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/memory', {
        method: 'POST',
        body: formData
      });

      const result = await response.json();
      
      if (result.success) {
        // Add success message to chat
        const successMessage: ChatMessage = {
          id: Date.now().toString(),
          type: 'assistant',
          content: `✅ **Dokumenti u ruajt me sukses!**\n\n📄 **${file.name}**\n💾 Tani OpenMind mund të përdorë këtë dokument për t'ju dhënë përgjigje më të sakta.\n\n💡 **Tip:** Pyesni diçka në lidhje me dokumentin që sapo ngarkuat!`,
          timestamp: Date.now()
        };
        setMessages(prev => [...prev, successMessage]);
      } else {
        throw new Error(result.error || 'Upload failed');
      }
    } catch (error) {
      console.error('File upload error:', error);
      const errorMessage: ChatMessage = {
        id: Date.now().toString(),
        type: 'assistant',
        content: `❌ **Gabim gjatë ngarkimit të dokumentit:** ${error instanceof Error ? error.message : 'Gabim i panjohur'}`,
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setUploadingFile(false);
    }
  };

  const triggerFileUpload = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={`min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col transition-all duration-500 ${
      isCompactMode ? 'max-w-4xl mx-auto' : 'max-w-7xl mx-auto'
    }`}>
      {/* Modern Header */}
      <div className="bg-white/90 backdrop-blur-md border-b border-gray-200/50 px-6 py-4 flex-shrink-0 shadow-sm">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-lg">🧠</span>
            </div>
            <div>
              <h1 className="text-xl font-semibold bg-gradient-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
                OpenMind Chat
              </h1>
              <p className="text-gray-600 text-sm">AI Assistant për çdo pyetje</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {/* File Upload Button */}
            <button
              onClick={triggerFileUpload}
              disabled={uploadingFile}
              className="px-3 py-2 text-sm bg-green-100 hover:bg-green-200 text-green-700 rounded-lg transition-all duration-200 flex items-center gap-2 disabled:opacity-50"
              title="Ngarko dokument"
            >
              {uploadingFile ? '⏳' : '📁'}
              <span className="hidden sm:inline">
                {uploadingFile ? 'Po ngarkon...' : 'Dokument'}
              </span>
            </button>

            {/* Memory Panel Toggle */}
            <button
              onClick={toggleMemoryPanel}
              className={`px-3 py-2 text-sm rounded-lg transition-all duration-200 flex items-center gap-2 ${
                showMemoryPanel 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
              }`}
              title="Shiko memorjen"
            >
              🧠
              <span className="hidden sm:inline">Memoria</span>
            </button>

            {/* Compact/Expanded Toggle */}
            <button
              onClick={toggleCompactMode}
              className="px-3 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-all duration-200 flex items-center gap-2"
              title={isCompactMode ? "Zgëro pamjen" : "Ngjesh pamjen"}
            >
              {isCompactMode ? '📱' : '🖥️'}
              <span className="hidden sm:inline">
                {isCompactMode ? 'Zgëro' : 'Ngjesh'}
              </span>
            </button>
            
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="px-3 py-2 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-all duration-200 flex items-center gap-2"
              >
                🗑️ <span className="hidden sm:inline">Pastro Chat</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Chat Messages - Dynamic Layout */}
      <div className="flex-1 overflow-y-auto">
        <div className={`px-6 py-6 transition-all duration-500 ${
          isCompactMode ? 'max-w-4xl mx-auto' : 'max-w-6xl mx-auto'
        }`}>
          {messages.length === 0 && !loading && (
            <div className="text-center py-16">
              <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-white text-3xl">👋</span>
              </div>
              <h2 className="text-2xl font-medium text-gray-700 mb-3">Mirë se erdhe në OpenMind!</h2>
              <p className="text-gray-600 mb-8 max-w-md mx-auto">
                Një AI i avancuar që kombinon dijen nga të gjitha burimet për t'ju dhënë përgjigje të sakta
              </p>
              
              {/* Quick Examples */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto">
                <button
                  onClick={() => setQuery('du te me ndihmosh te bej nje projekt')}
                  className="p-4 bg-white hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-xl transition-all duration-200 shadow-sm hover:shadow-md group"
                >
                  <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">💼</div>
                  <div className="font-medium text-gray-800">Projekt</div>
                  <div className="text-sm text-gray-600">Ndihma për punë</div>
                </button>
                <button
                  onClick={() => setQuery('me fol per web8')}
                  className="p-4 bg-white hover:bg-green-50 border border-gray-200 hover:border-green-300 rounded-xl transition-all duration-200 shadow-sm hover:shadow-md group"
                >
                  <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">🏢</div>
                  <div className="font-medium text-gray-800">Web8</div>
                  <div className="text-sm text-gray-600">Kompania jonë</div>
                </button>
                <button
                  onClick={() => setQuery('sa eshte data sot')}
                  className="p-4 bg-white hover:bg-purple-50 border border-gray-200 hover:border-purple-300 rounded-xl transition-all duration-200 shadow-sm hover:shadow-md group"
                >
                  <div className="text-2xl mb-2 group-hover:scale-110 transition-transform">📅</div>
                  <div className="font-medium text-gray-800">Data</div>
                  <div className="text-sm text-gray-600">Informacion i shpejtë</div>
                </button>
              </div>
            </div>
          )}

          {/* Messages */}
          <div className={`space-y-6 ${isCompactMode ? '' : 'grid grid-cols-1 lg:grid-cols-2 gap-8'}`}>
            {messages.map((message, index) => (
              <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] px-5 py-4 rounded-2xl transition-all duration-200 ${
                  message.type === 'user' 
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg shadow-blue-500/25' 
                    : 'bg-white text-gray-800 border border-gray-200 shadow-lg hover:shadow-xl'
                } ${!isCompactMode && message.content.length > 200 ? 'lg:max-w-full' : ''}`}>
                  
                  {/* User Avatar */}
                  {message.type === 'user' && (
                    <div className="flex items-start gap-3 mb-2">
                      <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center text-sm">
                        👤
                      </div>
                      <div className="font-medium text-blue-100">Ju</div>
                    </div>
                  )}
                  
                  {/* AI Avatar */}
                  {message.type === 'assistant' && (
                    <div className="flex items-start gap-3 mb-3">
                      <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-sm">
                        🧠
                      </div>
                      <div className="font-medium text-gray-700">OpenMind</div>
                    </div>
                  )}
                  
                  {/* Message Content */}
                  <div className={`whitespace-pre-wrap leading-relaxed ${
                    message.type === 'user' ? 'text-white' : 'text-gray-800'
                  } ${!isCompactMode && message.content.length > 300 ? 'text-sm' : ''}`}>
                    {message.content}
                  </div>
                  
                  {/* Timestamp */}
                  <div className={`text-xs mt-3 opacity-70 ${
                    message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Loading State */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-white text-gray-800 px-5 py-4 rounded-2xl border border-gray-200 shadow-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-sm">
                    🧠
                  </div>
                  <div>
                    <div className="font-medium text-gray-700 mb-1">OpenMind</div>
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-gray-600 text-sm">Duke menduar...</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Auto-scroll anchor */}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Modern Input Form - Fixed at bottom */}
      <div className="bg-white/90 backdrop-blur-md border-t border-gray-200/50 p-6 flex-shrink-0 shadow-lg">
        <div className={`transition-all duration-500 ${
          isCompactMode ? 'max-w-4xl mx-auto' : 'max-w-6xl mx-auto'
        }`}>
          <form onSubmit={handleSubmit} className="flex gap-4 items-end">
            <div className="flex-1 relative">
              <textarea
                ref={textareaRef}
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="Shkruani pyetjen tuaj këtu... (Enter për dërgim, Shift+Enter për rresht të ri)"
                className="w-full px-4 py-3 border border-gray-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200 min-h-[48px] max-h-[120px]"
                disabled={loading}
                rows={1}
              />
              {query.length > 0 && (
                <div className="absolute bottom-2 right-2 text-xs text-gray-400">
                  {query.length} karaktere
                </div>
              )}
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl hover:from-blue-600 hover:to-blue-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200 flex-shrink-0 shadow-lg hover:shadow-xl disabled:shadow-none min-h-[48px] flex items-center justify-center"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <span className="text-lg">📤</span>
              )}
            </button>
          </form>
          
          {/* Input hints */}
          {!loading && query.length === 0 && (
            <div className="mt-3 text-center">
              <div className="text-xs text-gray-500">
                💡 Tip: Përdorni <kbd className="px-1 py-0.5 bg-gray-100 rounded text-xs">Enter</kbd> për dërgim, 
                <kbd className="px-1 py-0.5 bg-gray-100 rounded text-xs">Shift+Enter</kbd> për rresht të ri
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.pdf,.doc,.docx,.md"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            handleFileUpload(file);
          }
        }}
        className="hidden"
      />
    </div>
  );
}
