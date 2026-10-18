export const SUPPORTED_LOCALES = [
  'en', 'sq', 'de', 'fr', 'it', 'es', 'pt', 'nl', 
  'sv', 'da', 'no', 'fi', 'pl', 'cs', 'hu', 'ro'
] as const;

export type SupportedLocale = typeof SUPPORTED_LOCALES[number];

export const LOCALE_NAMES: Record<SupportedLocale, string> = {
  en: 'English',
  sq: 'Shqip',
  de: 'Deutsch',
  fr: 'Français',
  it: 'Italiano',
  es: 'Español',
  pt: 'Português',
  nl: 'Nederlands',
  sv: 'Svenska',
  da: 'Dansk',
  no: 'Norsk',
  fi: 'Suomi',
  pl: 'Polski',
  cs: 'Čeština',
  hu: 'Magyar',
  ro: 'Română'
};

export const DEFAULT_LOCALE: SupportedLocale = 'en';

export interface LocaleConfig {
  locale: SupportedLocale;
  name: string;
  direction: 'ltr' | 'rtl';
  dateFormat: string;
  numberFormat: {
    decimal: string;
    thousands: string;
  };
}

export const LOCALE_CONFIGS: Record<SupportedLocale, LocaleConfig> = {
  en: {
    locale: 'en',
    name: 'English',
    direction: 'ltr',
    dateFormat: 'MM/dd/yyyy',
    numberFormat: { decimal: '.', thousands: ',' }
  },
  sq: {
    locale: 'sq',
    name: 'Shqip',
    direction: 'ltr',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: { decimal: ',', thousands: '.' }
  },
  de: {
    locale: 'de',
    name: 'Deutsch',
    direction: 'ltr',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: { decimal: ',', thousands: '.' }
  },
  fr: {
    locale: 'fr',
    name: 'Français',
    direction: 'ltr',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: { decimal: ',', thousands: ' ' }
  },
  it: {
    locale: 'it',
    name: 'Italiano',
    direction: 'ltr',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: { decimal: ',', thousands: '.' }
  },
  es: {
    locale: 'es',
    name: 'Español',
    direction: 'ltr',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: { decimal: ',', thousands: '.' }
  },
  pt: {
    locale: 'pt',
    name: 'Português',
    direction: 'ltr',
    dateFormat: 'dd/MM/yyyy',
    numberFormat: { decimal: ',', thousands: '.' }
  },
  nl: {
    locale: 'nl',
    name: 'Nederlands',
    direction: 'ltr',
    dateFormat: 'dd-MM-yyyy',
    numberFormat: { decimal: ',', thousands: '.' }
  },
  sv: {
    locale: 'sv',
    name: 'Svenska',
    direction: 'ltr',
    dateFormat: 'yyyy-MM-dd',
    numberFormat: { decimal: ',', thousands: ' ' }
  },
  da: {
    locale: 'da',
    name: 'Dansk',
    direction: 'ltr',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: { decimal: ',', thousands: '.' }
  },
  no: {
    locale: 'no',
    name: 'Norsk',
    direction: 'ltr',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: { decimal: ',', thousands: ' ' }
  },
  fi: {
    locale: 'fi',
    name: 'Suomi',
    direction: 'ltr',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: { decimal: ',', thousands: ' ' }
  },
  pl: {
    locale: 'pl',
    name: 'Polski',
    direction: 'ltr',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: { decimal: ',', thousands: ' ' }
  },
  cs: {
    locale: 'cs',
    name: 'Čeština',
    direction: 'ltr',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: { decimal: ',', thousands: ' ' }
  },
  hu: {
    locale: 'hu',
    name: 'Magyar',
    direction: 'ltr',
    dateFormat: 'yyyy.MM.dd',
    numberFormat: { decimal: ',', thousands: ' ' }
  },
  ro: {
    locale: 'ro',
    name: 'Română',
    direction: 'ltr',
    dateFormat: 'dd.MM.yyyy',
    numberFormat: { decimal: ',', thousands: '.' }
  }
};
