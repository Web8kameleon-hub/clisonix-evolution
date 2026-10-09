import { RefreshCw, Settings2 } from 'lucide-react';
import { CuriosityLevel } from './types';
import { CuriosityUiStrings } from '../../../lib/i18n/curiosity-ocean';

interface HeaderControlsProps {
  language: string;
  setLanguage: (next: string) => void;
  supportedLocales: string[];
  showSettings: boolean;
  setShowSettings: (next: boolean) => void;
  curiosityLevel: CuriosityLevel;
  setCuriosityLevel: (next: CuriosityLevel) => void;
  clearChat: () => void;
  t: CuriosityUiStrings;
}

export function HeaderControls({
  language,
  setLanguage,
  supportedLocales,
  showSettings,
  setShowSettings,
  curiosityLevel,
  setCuriosityLevel,
  clearChat,
  t,
}: HeaderControlsProps) {
  return (
    <div className="flex items-center gap-1">
      <select
        value={language}
        onChange={(e) => {
          const nextLanguage = e.target.value;
          setLanguage(nextLanguage);
          try {
            window.localStorage.setItem('curiosity-ocean-language', nextLanguage);
          } catch {
            // ignore storage failures
          }
        }}
        className="appearance-none bg-transparent border-none text-sm cursor-pointer focus:outline-none px-1"
        title={t.language}
      >
        {supportedLocales.map((localeCode) => (
          <option key={localeCode} value={localeCode}>{localeCode.toUpperCase()}</option>
        ))}
      </select>

      <div className="relative">
        <button
          onClick={() => setShowSettings(!showSettings)}
          className={`p-2 rounded-lg transition-colors ${showSettings ? 'bg-gray-100 text-gray-700' : 'text-gray-400 hover:text-gray-600 hover:bg-gray-50'}`}
        >
          <Settings2 className="w-[18px] h-[18px]" />
        </button>

        {showSettings && (
          <div className="absolute right-0 top-full mt-2 w-60 bg-white rounded-2xl shadow-2xl shadow-gray-200/60 border border-gray-100 p-4 z-50 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-600">{t.streamingLabel}</span>
              <button
                onClick={() => {}}
                className="relative w-11 h-6 rounded-full transition-colors bg-emerald-500 opacity-90 cursor-not-allowed"
                title={t.streamOnlyMode}
                disabled
              >
                <div className="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm transition-all left-6" />
              </button>
            </div>

            <div className="h-px bg-gray-100" />

            <div>
              <span className="text-xs font-medium text-gray-600 block mb-2">{t.curiosityLevel}</span>
              <div className="grid grid-cols-2 gap-1.5">
                {(['curious', 'wild', 'chaos', 'genius'] as const).map((level) => (
                  <button
                    key={level}
                    onClick={() => setCuriosityLevel(level)}
                    className={`text-xs px-3 py-2 rounded-xl transition-all capitalize ${
                      curiosityLevel === level
                        ? 'bg-emerald-50 text-emerald-700 font-semibold ring-1 ring-emerald-200'
                        : 'bg-gray-50 text-gray-500 hover:bg-gray-100'
                    }`}
                  >
                    {t[level]}
                  </button>
                ))}
              </div>
            </div>

            <div className="h-px bg-gray-100" />

            <button
              onClick={clearChat}
              className="w-full text-xs text-gray-500 hover:text-red-500 hover:bg-red-50 rounded-xl py-2 transition-colors flex items-center justify-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              {t.clearConversation}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
