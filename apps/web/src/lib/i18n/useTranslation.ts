"use client";

import { useState, useEffect, useCallback } from "react";
import {
  translations,
  defaultLanguage,
  t as translate,
  languageNames,
  type Language,
} from "./translations";
import { SUPPORTED_LANGUAGES_102 } from "../language_detection_102";

const SUPPORTED_LANGUAGES_72 = SUPPORTED_LANGUAGES_102;

const STORAGE_KEY = "clisonix_language";
const COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 365;

function normalizeLanguageTag(value?: string | null): Language | null {
  if (!value) {
    return null;
  }

  const baseLanguage = value.toLowerCase().split("-")[0];
  return (SUPPORTED_LANGUAGES_72 as readonly string[]).includes(baseLanguage)
    ? (baseLanguage as Language)
    : null;
}

function readLanguageCookie(): Language | null {
  if (typeof document === "undefined") {
    return null;
  }

  const cookies = document.cookie
    .split(";")
    .map((cookie) => cookie.trim())
    .filter(Boolean);

  for (const cookie of cookies) {
    if (!cookie.startsWith(`${STORAGE_KEY}=`)) {
      continue;
    }

    const rawValue = decodeURIComponent(
      cookie.substring(STORAGE_KEY.length + 1),
    );
    return normalizeLanguageTag(rawValue);
  }

  return null;
}

function writeLanguageCookie(language: Language): void {
  if (typeof document === "undefined") {
    return;
  }

  document.cookie = `${STORAGE_KEY}=${encodeURIComponent(language)}; path=/; max-age=${COOKIE_MAX_AGE_SECONDS}; samesite=lax`;
}

function getAutoDetectedLanguage(): Language {
  if (typeof navigator === "undefined") {
    return defaultLanguage;
  }

  const languageCandidates = [
    ...(Array.isArray(navigator.languages) ? navigator.languages : []),
    navigator.language,
  ];

  for (const candidate of languageCandidates) {
    const normalized = normalizeLanguageTag(candidate);
    if (normalized) {
      return normalized;
    }
  }

  return defaultLanguage;
}

export function useTranslation() {
  const [language, setLanguageState] = useState<Language>(defaultLanguage);
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    const stored = normalizeLanguageTag(localStorage.getItem(STORAGE_KEY));
    const cookieStored = readLanguageCookie();
    const detected = stored || cookieStored || getAutoDetectedLanguage();

    setLanguageState(detected);
    localStorage.setItem(STORAGE_KEY, detected);
    writeLanguageCookie(detected);
    document.documentElement.lang = detected;
    setIsLoaded(true);
  }, []);

  useEffect(() => {
    if (typeof document !== "undefined") {
      document.documentElement.lang = language;
    }
  }, [language]);

  const setLanguage = useCallback((lang: Language) => {
    const normalized = normalizeLanguageTag(lang);
    if (!normalized) {
      return;
    }

    setLanguageState(normalized);
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY, normalized);
      writeLanguageCookie(normalized);
      document.documentElement.lang = normalized;
    }
  }, []);

  // Translation function
  const t = useCallback(
    (key: string): string => {
      return translate(key, language);
    },
    [language],
  );

  return {
    language,
    setLanguage,
    t,
    isLoaded,
    languages: languageNames,
    availableLanguages: SUPPORTED_LANGUAGES_102,
  };
}

// Static translation function (for server-side or non-hook usage)
export { translate as t, languageNames, defaultLanguage };
