import { Sparkles } from 'lucide-react';
import { CuriosityUiStrings } from '../../../lib/i18n/curiosity-ocean';
import { Message } from './types';

interface MessagesPanelProps {
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  t: CuriosityUiStrings;
  onSendMessage: (question?: string) => void;
  normalizeContent: (raw: string) => string;
  messagesEndRef: { current: HTMLDivElement | null };
  onContainerClick: () => void;
}

export function MessagesPanel({
  messages,
  isLoading,
  isStreaming,
  t,
  onSendMessage,
  normalizeContent,
  messagesEndRef,
  onContainerClick,
}: MessagesPanelProps) {
  return (
    <main className="flex-1 overflow-y-auto" onClick={onContainerClick}>
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-6 space-y-5">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className="max-w-[88%] sm:max-w-[80%]">
              {message.type === 'ai' && (
                <div className="flex items-center gap-1.5 mb-1.5 ml-0.5">
                  <div className="w-5 h-5 rounded-md bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                    <Sparkles className="w-3 h-3 text-white" />
                  </div>
                  <span className="text-[11px] font-medium text-gray-400">{t.assistantName}</span>
                  {message.isStreaming && (
                    <span className="text-[10px] text-emerald-500 animate-pulse ml-1">● {t.streamingIndicator}</span>
                  )}
                </div>
              )}

              <div
                className={`rounded-2xl px-4 py-3 ${
                  message.type === 'user'
                    ? 'bg-emerald-600 text-white rounded-tr-md'
                    : 'bg-white text-gray-800 shadow-sm shadow-gray-100 border border-gray-100 rounded-tl-md'
                }`}
              >
                <div className="whitespace-pre-wrap text-[14.5px] leading-relaxed">{normalizeContent(message.content)}</div>

              </div>

              <div className={`mt-1 text-[10px] text-gray-300 ${message.type === 'user' ? 'text-right mr-1' : 'ml-1'}`}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {isLoading && !isStreaming && (
          <div className="flex justify-start">
            <div>
              <div className="flex items-center gap-1.5 mb-1.5 ml-0.5">
                <div className="w-5 h-5 rounded-md bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center">
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
                <span className="text-[11px] font-medium text-gray-400">{t.assistantName}</span>
              </div>
              <div className="bg-white shadow-sm shadow-gray-100 border border-gray-100 rounded-2xl rounded-tl-md px-4 py-4">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                  <span className="text-xs text-gray-400">{t.thinking}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </main>
  );
}
