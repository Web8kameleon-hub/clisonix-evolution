import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Message {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    thinking?: boolean;
    source?: string;
    confidence?: number;
    relatedTopics?: string[];
  };
}

interface ChatTopic {
  id: string;
  title: string;
  description: string;
  category: 'technology' | 'science' | 'philosophy' | 'culture' | 'general';
  difficulty: 'basic' | 'intermediate' | 'advanced' | 'expert';
  participants: number;
}

const AdvancedChatSystem: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [currentTopic, setCurrentTopic] = useState<ChatTopic | null>(null);
  const [chatMode, setChatMode] = useState<'general' | 'focused' | 'research' | 'brainstorm'>('general');
  const [aiPersonality, setAiPersonality] = useState<'assistant' | 'philosopher' | 'scientist' | 'creative'>('assistant');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested topics for discussion
  const suggestedTopics: ChatTopic[] = [
    {
      id: 'tech-future',
      title: 'E Ardhmja e Teknologjisë',
      description: 'Diskutim për AI, blockchain, dhe teknologjitë e reja',
      category: 'technology',
      difficulty: 'intermediate',
      participants: 1247
    },
    {
      id: 'philosophy-ai',
      title: 'Filozofia e Inteligjencës Artificiale',
      description: 'A mund të mendojnë makinat? Çfarë është vetëdija?',
      category: 'philosophy',
      difficulty: 'expert',
      participants: 892
    },
    {
      id: 'science-breakthrough',
      title: 'Zbulime Shkencore Revolucionare',
      description: 'Nga kuantumi tek biologjia sintetike',
      category: 'science',
      difficulty: 'advanced',
      participants: 1456
    },
    {
      id: 'albanian-culture',
      title: 'Kultura Shqiptare në Epokën Digjitale',
      description: 'Si ruhet dhe zhvillohet identiteti kulturor',
      category: 'culture',
      difficulty: 'basic',
      participants: 567
    },
    {
      id: 'creative-thinking',
      title: 'Mendimi Kreativ dhe Inovacioni',
      description: 'Teknika për zgjidhjen kreative të problemeve',
      category: 'general',
      difficulty: 'intermediate',
      participants: 923
    }
  ];

  // Advanced AI responses based on mode and personality
  const generateAIResponse = async (userMessage: string): Promise<string> => {
    setIsThinking(true);
    
    // Simulate advanced AI thinking process
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));
    
    const responses = {
      assistant: {
        general: [
          `Kjo është një pyetje shumë interesante! Le të analizojmë së bashku...`,
          `Bazuar në të dhënat dhe kërkimet e fundit, mendoj se...`,
          `Kjo temë ka disa aspekte të rëndësishme që vlen të eksplorojmë...`
        ],
        focused: [
          `Le të fokusohemi në aspektin kryesor të kësaj çështjeje...`,
          `Për të kuptuar plotësisht këtë, duhet të shqyrtojmë...`,
          `Elementi kyç këtu është...`
        ]
      },
      philosopher: {
        general: [
          `Kjo na çon në pyetjen fundamentale: çfarë do të thotë...?`,
          `Nga perspektiva filozofike, kjo ngre çështjen e...`,
          `Socrati do të pyeste: "A e dijmë vërtet se çfarë..."?`
        ],
        research: [
          `Le të shqyrtojmë epistemologjikisht: si mund të dijmë...?`,
          `Kjo prekë thelbin e natyrës së realitetit...`,
          `Duhet të dallojmë midis asaj që duket dhe asaj që është...`
        ]
      },
      scientist: {
        general: [
          `Të dhënat tregojnë një model interesant...`,
          `Hipoteza ime është se...`,
          `Nëse analizojmë këtë shkencërisht...`
        ],
        research: [
          `Studimi më i fundit në këtë fushë tregon...`,
          `Metodologjikisht, duhet të konsiderojmë...`,
          `Evidencat empirike sugjerojnë...`
        ]
      },
      creative: {
        general: [
          `Imagjinoni për një moment nëse...`,
          `Çfarë do të ndodhte sikur të...?`,
          `Le të shpikjmë një qasje krejtësisht të re...`
        ],
        brainstorm: [
          `Idetë më të çmendura shpesh janë më të mira! Çfarë për...?`,
          `Le të thyejmë të gjitha rregullat dhe të mendojmë...`,
          `Në një botë ideale, si do ta zgjidhnim këtë...?`
        ]
      }
    };

    const personalityResponses = responses[aiPersonality];
    const modeResponses = personalityResponses[chatMode] || personalityResponses.general;
    const baseResponse = modeResponses[Math.floor(Math.random() * modeResponses.length)];

    // Add contextual content based on user message
    let contextualResponse = '';
    if (userMessage.toLowerCase().includes('teknologji')) {
      contextualResponse = ' Teknologjia po ndryshon botën me një shpejtësi të paparë. AI, blockchain, dhe IoT po krijojnë mundësi të reja çdo ditë.';
    } else if (userMessage.toLowerCase().includes('shqipëri') || userMessage.toLowerCase().includes('shqip')) {
      contextualResponse = ' Shqipëria ka një potencial të madh në fushën e teknologjisë dhe inovacionit. Tradita jonë e fortë kulturore mund të kombinohet bukur me zhvillimin modern.';
    } else if (userMessage.toLowerCase().includes('e ardhmja')) {
      contextualResponse = ' E ardhmja është plot mundësi të panjohura. Çdo hap që marrim sot formon botën e nesërme.';
    } else if (userMessage.toLowerCase().includes('ai') || userMessage.toLowerCase().includes('inteligjenc')) {
      contextualResponse = ' AI është një nga zhvillimet më revolucionare të kohës sonë. Pyetja nuk është nëse do të ndryshojë gjithçka, por si do ta bëjë këtë.';
    }

    setIsThinking(false);
    return baseResponse + contextualResponse + '\n\nÇfarë mendoni ju për këtë? A keni përvoja të veçanta në këtë drejtim?';
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // Generate AI response
    const aiResponse = await generateAIResponse(inputValue);
    
    const aiMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: 'ai',
      content: aiResponse,
      timestamp: new Date(),
      metadata: {
        source: aiPersonality,
        confidence: 0.85 + Math.random() * 0.15,
        relatedTopics: ['AI', 'Innovation', 'Future']
      }
    };

    setMessages(prev => [...prev, aiMessage]);
  };

  const startTopicDiscussion = (topic: ChatTopic) => {
    setCurrentTopic(topic);
    const systemMessage: Message = {
      id: Date.now().toString(),
      type: 'system',
      content: `🎯 Filloi diskutimi: "${topic.title}"\n${topic.description}\n\nSi do të dëshironit të eksploroni këtë temë?`,
      timestamp: new Date()
    };
    setMessages([systemMessage]);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize with welcome message
  useEffect(() => {
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'system',
      content: `🚀 Mirë se vini në Sistemin e Avancuar të Diskutimit!\n\nKy është një hapësirë e lirë për diskutime të thella mbi çdo temë. Mund të flisni për teknologji, shkencë, filozofi, kulturë, ose çdo gjë tjetër që ju intereson.\n\n✨ Zgjidhni një mënyrë diskutimi dhe fillojmë!`,
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, []);

  return (
    <div className="h-screen flex bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Sidebar with topics and settings */}
      <motion.div 
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        className="w-80 bg-black/20 backdrop-blur-xl p-6 border-r border-purple-500/20"
      >
        <div className="mb-6">
          <h2 className="text-xl font-bold text-white mb-4">🎯 Tema Diskutimi</h2>
          <div className="space-y-3">
            {suggestedTopics.map((topic) => (
              <motion.div
                key={topic.id}
                whileHover={{ scale: 1.02 }}
                onClick={() => startTopicDiscussion(topic)}
                className="p-3 bg-gradient-to-r from-purple-600/20 to-blue-600/20 rounded-lg cursor-pointer border border-purple-500/30 hover:border-purple-500/60 transition-all"
              >
                <h3 className="text-sm font-semibold text-white">{topic.title}</h3>
                <p className="text-xs text-gray-300 mt-1">{topic.description}</p>
                <div className="flex justify-between items-center mt-2">
                  <span className={`text-xs px-2 py-1 rounded ${
                    topic.difficulty === 'basic' ? 'bg-green-500/20 text-green-300' :
                    topic.difficulty === 'intermediate' ? 'bg-yellow-500/20 text-yellow-300' :
                    topic.difficulty === 'advanced' ? 'bg-orange-500/20 text-orange-300' :
                    'bg-red-500/20 text-red-300'
                  }`}>
                    {topic.difficulty}
                  </span>
                  <span className="text-xs text-gray-400">{topic.participants} pjesëmarrës</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Chat Mode Selector */}
        <div className="mb-6">
          <h3 className="text-sm font-bold text-white mb-3">🎭 Mënyra Diskutimi</h3>
          <div className="grid grid-cols-2 gap-2">
            {[
              { mode: 'general' as const, icon: '💬', label: 'E Përgjithshme' },
              { mode: 'focused' as const, icon: '🎯', label: 'E Fokusuar' },
              { mode: 'research' as const, icon: '🔬', label: 'Kërkimore' },
              { mode: 'brainstorm' as const, icon: '🧠', label: 'Brainstorm' }
            ].map(({ mode, icon, label }) => (
              <button
                key={mode}
                onClick={() => setChatMode(mode)}
                className={`p-2 rounded text-xs transition-all ${
                  chatMode === mode 
                    ? 'bg-purple-600 text-white' 
                    : 'bg-purple-600/20 text-gray-300 hover:bg-purple-600/40'
                }`}
              >
                {icon} {label}
              </button>
            ))}
          </div>
        </div>

        {/* AI Personality Selector */}
        <div>
          <h3 className="text-sm font-bold text-white mb-3">🤖 Personaliteti AI</h3>
          <div className="space-y-2">
            {[
              { personality: 'assistant' as const, icon: '🤝', label: 'Asistent' },
              { personality: 'philosopher' as const, icon: '🏛️', label: 'Filozof' },
              { personality: 'scientist' as const, icon: '🔬', label: 'Shkencëtar' },
              { personality: 'creative' as const, icon: '🎨', label: 'Kreativ' }
            ].map(({ personality, icon, label }) => (
              <button
                key={personality}
                onClick={() => setAiPersonality(personality)}
                className={`w-full p-2 rounded text-xs transition-all text-left ${
                  aiPersonality === personality 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-blue-600/20 text-gray-300 hover:bg-blue-600/40'
                }`}
              >
                {icon} {label}
              </button>
            ))}
          </div>
        </div>
      </motion.div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-black/20 backdrop-blur-xl p-4 border-b border-purple-500/20">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold text-white">
                💫 Diskutim i Avancuar
              </h1>
              {currentTopic && (
                <p className="text-sm text-gray-300">📋 {currentTopic.title}</p>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-300">
                Mënyrë: <span className="text-purple-300">{chatMode}</span>
              </div>
              <div className="text-sm text-gray-300">
                AI: <span className="text-blue-300">{aiPersonality}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-2xl p-4 rounded-2xl ${
                  message.type === 'user' 
                    ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white ml-auto' 
                    : message.type === 'ai'
                    ? 'bg-gradient-to-r from-gray-800 to-gray-700 text-white'
                    : 'bg-gradient-to-r from-green-700 to-teal-700 text-white mx-auto'
                }`}>
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">
                      {message.type === 'user' ? '👤' : message.type === 'ai' ? '🤖' : '⚡'}
                    </div>
                    <div className="flex-1">
                      <p className="whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </p>
                      <div className="flex justify-between items-center mt-2 text-xs opacity-70">
                        <span>{message.timestamp.toLocaleTimeString('sq-AL')}</span>
                        {message.metadata?.confidence && (
                          <span>Besueshmëria: {Math.round(message.metadata.confidence * 100)}%</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {isThinking && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="bg-gradient-to-r from-gray-800 to-gray-700 p-4 rounded-2xl">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">🤖</div>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                  <span className="text-gray-300">Po mendoj...</span>
                </div>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="bg-black/20 backdrop-blur-xl p-6 border-t border-purple-500/20">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Shkruani pyetjen tuaj këtu... (mund të flisni për çdo gjë)"
              className="flex-1 bg-gray-800/50 border border-purple-500/30 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:border-purple-500 focus:outline-none"
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isThinking}
              className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Dërgo 🚀
            </motion.button>
          </div>
          <div className="mt-3 text-xs text-gray-400 text-center">
            💡 Këshillë: Mund të diskutoni për teknologji, shkencë, filozofi, kulturë shqiptare, ose çdo temë tjetër që ju intereson!
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdvancedChatSystem;
