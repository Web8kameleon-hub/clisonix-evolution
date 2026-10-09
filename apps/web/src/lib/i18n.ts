/**
 * i18n Module - Re-exports from full implementation
 * This file provides backwards compatibility for imports from '@/lib/i18n'
 */

// Re-export everything from the full i18n implementation
export { useTranslation } from "./i18n/useTranslation";
export type { Language } from "./i18n/translations";
export {
  translations,
  defaultLanguage,
  t,
  languageNames,
  LANGUAGES,
} from "./i18n/translations";

// No default export needed - use named exports
