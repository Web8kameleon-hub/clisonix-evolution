'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { IntlProvider } from 'react-intl';
import { SupportedLocale, DEFAULT_LOCALE, LOCALE_CONFIGS } from './locales';

interface I18nContextValue {
  locale: SupportedLocale;
  setLocale: (locale: SupportedLocale) => void;
  isLoading: boolean;
}

const I18nContext = createContext<I18nContextValue | undefined>(undefined);

export const useI18n = () => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};

interface I18nProviderProps {
  children: ReactNode;
  initialLocale?: SupportedLocale;
}

export const I18nProvider: React.FC<I18nProviderProps> = ({ 
  children, 
  initialLocale = DEFAULT_LOCALE 
}) => {
  const [locale, setLocaleState] = useState<SupportedLocale>(initialLocale);
  const [messages, setMessages] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);

  const loadMessages = async (targetLocale: SupportedLocale) => {
    setIsLoading(true);
    try {
      const messageModule = await import(`./messages/${targetLocale}`);
      setMessages(messageModule.messages);
    } catch (error) {
      console.warn(`Failed to load messages for locale ${targetLocale}, falling back to English`);
      const fallbackModule = await import('./messages/en');
      setMessages(fallbackModule.messages);
    } finally {
      setIsLoading(false);
    }
  };

  const setLocale = async (newLocale: SupportedLocale) => {
    if (newLocale !== locale) {
      setLocaleState(newLocale);
      await loadMessages(newLocale);
      
      // Save to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('euroweb-locale', newLocale);
      }
      
      // Update document language
      if (typeof document !== 'undefined') {
        document.documentElement.lang = newLocale;
      }
    }
  };

  useEffect(() => {
    // Load initial locale from localStorage or browser
    let initialLoc = initialLocale;
    
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('euroweb-locale') as SupportedLocale;
      if (saved && LOCALE_CONFIGS[saved]) {
        initialLoc = saved;
      } else {
        // Try to detect from browser language
        const browserLang = navigator.language.split('-')[0] as SupportedLocale;
        if (LOCALE_CONFIGS[browserLang]) {
          initialLoc = browserLang;
        }
      }
    }
    
    setLocaleState(initialLoc);
    loadMessages(initialLoc);
  }, [initialLocale]);

  const value: I18nContextValue = {
    locale,
    setLocale,
    isLoading
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <I18nContext.Provider value={value}>
      <IntlProvider 
        locale={locale} 
        messages={messages}
        defaultLocale={DEFAULT_LOCALE}
      >
        {children}
      </IntlProvider>
    </I18nContext.Provider>
  );
};
