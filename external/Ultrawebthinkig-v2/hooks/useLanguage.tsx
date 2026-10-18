import React from 'react';
'use client';

/**
 * Web8 Industrial Multi-Language React Hook
 * Hook React industrial për gjuhët shumëgjuhëshe
 * 
 * @author UltraWeb International Team
 * @version 8.0.0-MULTILINGUAL
 */

import { useState, useEffect, useCallback, createContext, useContext } from 'react';
import { 
  Language, 
  Translations, 
  TranslationKey,
  LanguageDetector,
  languages,
  translations,
  defaultLanguage,
  fallbackLanguage
} from '../config/languages';

// Language Context Interface
interface LanguageContextType {
  currentLanguage: string;
  availableLanguages: Language[];
  translations: Translations;
  t: (key: string, params?: Record<string, string>) => string;
  changeLanguage: (languageCode: string) => void;
  isRTL: boolean;
  languageInfo: Language | null;
}

// Create Language Context
const LanguageContext = createContext<LanguageContextType | null>(null);

// Language Provider Component
function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [currentLanguage, setCurrentLanguage] = useState<string>(defaultLanguage);
  const [isLoaded, setIsLoaded] = useState(false);

  // Initialize language on mount
  useEffect(() => {
    const initializeLanguage = () => {
      // Check localStorage first
      const savedLanguage = typeof window !== 'undefined' 
        ? localStorage.getItem('web8-language') 
        : null;

      if (savedLanguage && languages.find(lang => lang.code === savedLanguage)) {
        setCurrentLanguage(savedLanguage);
      } else {
        // Auto-detect language
        const detectedLanguage = LanguageDetector.detectRegionLanguage();
        setCurrentLanguage(detectedLanguage);
      }
      
      setIsLoaded(true);
    };

    initializeLanguage();
  }, []);

  // Get current language info
  const languageInfo = languages.find(lang => lang.code === currentLanguage) || null;
  const isRTL = languageInfo?.direction === 'rtl';

  // Translation function with nested key support
  const t = useCallback((key: string, params?: Record<string, string>): string => {
    const keyParts = key.split('.');
    let value: unknown = translations[currentLanguage];
    
    // Navigate through nested keys
    for (const part of keyParts) {
      if (value && typeof value === 'object' && part in value) {
        value = value[part];
      } else {
        // Fallback to fallback language
        value = translations[fallbackLanguage];
        for (const part of keyParts) {
          if (value && typeof value === 'object' && part in value) {
            value = value[part];
          } else {
            return `[${key}]`; // Return key if translation not found
          }
        }
        break;
      }
    }

    let result = typeof value === 'string' ? value : `[${key}]`;

    // Replace parameters if provided
    if (params) {
      Object.entries(params).forEach(([param, paramValue]) => {
        result = result.replace(new RegExp(`{{${param}}}`, 'g'), paramValue);
      });
    }

    return result;
  }, [currentLanguage]);

  // Change language function
  const changeLanguage = useCallback((languageCode: string) => {
    if (languages.find(lang => lang.code === languageCode && lang.enabled)) {
      setCurrentLanguage(languageCode);
      if (typeof window !== 'undefined') {
        localStorage.setItem('web8-language', languageCode);
        // Update HTML lang attribute
        document.documentElement.lang = languageCode;
        document.documentElement.dir = languages.find(lang => lang.code === languageCode)?.direction || 'ltr';
      }
    }
  }, []);

  // Context value
  const contextValue: LanguageContextType = {
    currentLanguage,
    availableLanguages: languages.filter(lang => lang.enabled),
    translations,
    t,
    changeLanguage,
    isRTL,
    languageInfo
  };

  // Don't render until language is loaded
  if (!isLoaded) {
    return (
      <div className="web8-language-loading">
        <div className="loading-spinner">🌐</div>
        <div>Ngarkimi i gjuhës...</div>
      </div>
    );
  }

  return (
    <LanguageContext.Provider value={contextValue}>
      {children}
    </LanguageContext.Provider>
  );
}

// Custom hook to use language context
function useLanguage(): LanguageContextType {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}

// Utility hook for specific features
function useTranslation() {
  const { t, currentLanguage, changeLanguage } = useLanguage();
  return { t, currentLanguage, changeLanguage };
}

// Language selector hook
function useLanguageSelector() {
  const { 
    currentLanguage, 
    availableLanguages, 
    changeLanguage, 
    languageInfo 
  } = useLanguage();

  return {
    currentLanguage,
    currentLanguageInfo: languageInfo,
    availableLanguages,
    changeLanguage,
    formatLanguageOption: (lang: Language) => `${lang.flag} ${lang.nativeName}`
  };
}

// RTL support hook
function useRTL() {
  const { isRTL, languageInfo } = useLanguage();
  
  return {
    isRTL,
    direction: isRTL ? 'rtl' : 'ltr',
    textAlign: isRTL ? 'right' : 'left',
    marginStart: isRTL ? 'marginRight' : 'marginLeft',
    marginEnd: isRTL ? 'marginLeft' : 'marginRight',
    paddingStart: isRTL ? 'paddingRight' : 'paddingLeft',
    paddingEnd: isRTL ? 'paddingLeft' : 'paddingRight'
  };
}

// Export everything needed
export {
  LanguageContext,
  LanguageProvider,
  useLanguage,
  useTranslation,
  useLanguageSelector,
  useRTL
};

// Export types
export type { LanguageContextType };
