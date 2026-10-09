import { Camera, FileText, Loader2, Mic, Plus, Send, Square } from 'lucide-react';
import type { ChangeEvent, KeyboardEvent } from 'react';
import { CuriosityUiStrings } from '../../../lib/i18n/curiosity-ocean';

interface InputComposerProps {
  isRecording: boolean;
  voiceDiscussionEnabled: boolean;
  isLoading: boolean;
  isStreaming: boolean;
  showAttachMenu: boolean;
  setShowAttachMenu: (next: boolean) => void;
  attachMenuRef: { current: HTMLDivElement | null };
  fileInputRef: { current: HTMLInputElement | null };
  inputRef: { current: HTMLTextAreaElement | null };
  inputValue: string;
  setInputValue: (value: string) => void;
  handleKeyDown: (event: KeyboardEvent) => void;
  handleFileUpload: (event: ChangeEvent<HTMLInputElement>) => void;
  stopStreaming: () => void;
  sendMessage: () => void;
  toggleRecording: () => void | Promise<void>;
  toggleCamera: () => void | Promise<void>;
  toggleVoiceDiscussion: () => void;
  t: CuriosityUiStrings;
}

export function InputComposer({
  isRecording,
  voiceDiscussionEnabled,
  isLoading,
  isStreaming,
  showAttachMenu,
  setShowAttachMenu,
  attachMenuRef,
  fileInputRef,
  inputRef,
  inputValue,
  setInputValue,
  handleKeyDown,
  handleFileUpload,
  stopStreaming,
  sendMessage,
  toggleRecording,
  toggleCamera,
  toggleVoiceDiscussion,
  t,
}: InputComposerProps) {
  return (
    <div className="flex-shrink-0 border-t border-gray-200/60 bg-white/80 backdrop-blur-xl">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-3">
        {isRecording && (
          <div className="flex items-center gap-2.5 mb-3 px-4 py-2.5 bg-red-50 border border-red-100 rounded-xl">
            <div className="w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse" />
            <span className="text-xs text-red-600 font-medium flex-1">{t.recordingAudio}</span>
            <button onClick={toggleRecording} className="text-xs text-red-500 hover:text-red-700 font-semibold transition-colors px-2 py-1 hover:bg-red-100 rounded-lg">
              {t.stopButton}
            </button>
          </div>
        )}

        <div className="relative flex items-end gap-2 bg-gray-50/80 border border-gray-200 rounded-2xl px-3 py-2 focus-within:border-emerald-300 focus-within:ring-2 focus-within:ring-emerald-500/10 focus-within:bg-white transition-all">
          <button
            onClick={toggleVoiceDiscussion}
            type="button"
            className={`self-end text-[10px] px-2.5 py-1.5 rounded-lg border transition-colors ${voiceDiscussionEnabled ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'}`}
            title={t.voiceDiscussion}
          >
            {voiceDiscussionEnabled ? t.voiceDiscussionOn : t.voiceDiscussionOff}
          </button>

          <div className="relative flex-shrink-0 self-end" ref={attachMenuRef}>
            <button
              onClick={(e) => { e.stopPropagation(); setShowAttachMenu(!showAttachMenu); }}
              disabled={isLoading || isStreaming}
              className={`p-2 rounded-xl transition-all ${showAttachMenu ? 'bg-emerald-100 text-emerald-600' : 'hover:bg-gray-200/80 text-gray-400 hover:text-gray-600'}`}
            >
              <Plus className={`w-5 h-5 transition-transform duration-200 ${showAttachMenu ? 'rotate-45' : ''}`} />
            </button>

            {showAttachMenu && (
              <div className="absolute bottom-full left-0 mb-2 bg-white rounded-2xl shadow-2xl shadow-gray-200/50 border border-gray-100 py-2 z-50 min-w-[180px] overflow-hidden">
                <button
                  onClick={toggleRecording}
                  className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 flex items-center justify-center">
                    <Mic className="w-4 h-4 text-emerald-600" />
                  </div>
                  <span className="font-medium">{t.voice}</span>
                </button>
                <button
                  onClick={toggleCamera}
                  className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <div className="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                    <Camera className="w-4 h-4 text-blue-600" />
                  </div>
                  <span className="font-medium">{t.camera}</span>
                </button>
                <button
                  onClick={() => { setShowAttachMenu(false); fileInputRef.current?.click(); }}
                  className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  <div className="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center">
                    <FileText className="w-4 h-4 text-purple-600" />
                  </div>
                  <span className="font-medium">{t.document}</span>
                </button>
              </div>
            )}
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".txt,.pdf,.doc,.docx,.md,.csv,.json"
          />

          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t.askAnything}
            rows={1}
            className="flex-1 bg-transparent border-none resize-none text-sm text-gray-900 placeholder-gray-400 focus:outline-none py-2 max-h-[120px] leading-relaxed"
            disabled={isLoading || isStreaming}
          />

          <div className="flex-shrink-0 self-end">
            {isStreaming ? (
              <button onClick={stopStreaming} className="p-2 bg-red-500 hover:bg-red-600 rounded-xl transition-colors active:scale-95">
                <Square className="w-4 h-4 text-white" />
              </button>
            ) : (
              <button
                onClick={sendMessage}
                disabled={isLoading || !inputValue.trim()}
                className="p-2 bg-emerald-500 hover:bg-emerald-600 disabled:bg-gray-200 disabled:cursor-not-allowed rounded-xl transition-all active:scale-95"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 text-white animate-spin" />
                ) : (
                  <Send className="w-4 h-4 text-white" />
                )}
              </button>
            )}
          </div>
        </div>

        <p className="text-center text-[10px] text-gray-300 mt-2 select-none">{t.footer}</p>
      </div>
    </div>
  );
}
