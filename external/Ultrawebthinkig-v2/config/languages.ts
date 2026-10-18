/**
 * Web8 Industrial Multi-Language System
 * Sistema industriale shumëgjuhëshe për Web8 Platform
 * 
 * @author UltraWeb International Team
 * @version 8.0.0-MULTILINGUAL
 */

export interface Language {
  code: string;
  name: string;
  nativeName: string;
  flag: string;
  direction: 'ltr' | 'rtl';
  enabled: boolean;
  fallback?: string;
}

export interface TranslationKey {
  [key: string]: string | TranslationKey;
}

export interface Translations {
  [languageCode: string]: TranslationKey;
}

// Supported Languages Configuration
export const SUPPORTED_LANGUAGES: Language[] = [
  // Albanian - Primary
  {
    code: 'sq',
    name: 'Albanian',
    nativeName: 'Shqip',
    flag: '🇦🇱',
    direction: 'ltr',
    enabled: true
  },
  // English - Global
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    flag: '🇺🇸',
    direction: 'ltr',
    enabled: true
  },
  // German - Europe
  {
    code: 'de',
    name: 'German',
    nativeName: 'Deutsch',
    flag: '🇩🇪',
    direction: 'ltr',
    enabled: true
  },
  // French - Europe
  {
    code: 'fr',
    name: 'French',
    nativeName: 'Français',
    flag: '🇫🇷',
    direction: 'ltr',
    enabled: true
  },
  // Italian - Europe
  {
    code: 'it',
    name: 'Italian',
    nativeName: 'Italiano',
    flag: '🇮🇹',
    direction: 'ltr',
    enabled: true
  },
  // Spanish - Global
  {
    code: 'es',
    name: 'Spanish',
    nativeName: 'Español',
    flag: '🇪🇸',
    direction: 'ltr',
    enabled: true
  },
  // Portuguese - Global
  {
    code: 'pt',
    name: 'Portuguese',
    nativeName: 'Português',
    flag: '🇵🇹',
    direction: 'ltr',
    enabled: true
  },
  // Russian - Eastern Europe
  {
    code: 'ru',
    name: 'Russian',
    nativeName: 'Русский',
    flag: '🇷🇺',
    direction: 'ltr',
    enabled: true
  },
  // Chinese Simplified - Asia
  {
    code: 'zh-CN',
    name: 'Chinese (Simplified)',
    nativeName: '简体中文',
    flag: '🇨🇳',
    direction: 'ltr',
    enabled: true
  },
  // Japanese - Asia
  {
    code: 'ja',
    name: 'Japanese',
    nativeName: '日本語',
    flag: '🇯🇵',
    direction: 'ltr',
    enabled: true
  },
  // Arabic - Middle East
  {
    code: 'ar',
    name: 'Arabic',
    nativeName: 'العربية',
    flag: '🇸🇦',
    direction: 'rtl',
    enabled: true
  },
  // Turkish - Europe/Asia
  {
    code: 'tr',
    name: 'Turkish',
    nativeName: 'Türkçe',
    flag: '🇹🇷',
    direction: 'ltr',
    enabled: true
  },
  // Greek - Europe
  {
    code: 'el',
    name: 'Greek',
    nativeName: 'Ελληνικά',
    flag: '🇬🇷',
    direction: 'ltr',
    enabled: true
  },
  // Serbian - Balkans
  {
    code: 'sr',
    name: 'Serbian',
    nativeName: 'Српски',
    flag: '🇷🇸',
    direction: 'ltr',
    enabled: true
  },
  // Macedonian - Balkans
  {
    code: 'mk',
    name: 'Macedonian',
    nativeName: 'Македонски',
    flag: '🇲🇰',
    direction: 'ltr',
    enabled: true
  },
  // Bulgarian - Balkans
  {
    code: 'bg',
    name: 'Bulgarian',
    nativeName: 'Български',
    flag: '🇧🇬',
    direction: 'ltr',
    enabled: true
  }
];

// Default language settings
const DEFAULT_LANGUAGE = 'sq';
const FALLBACK_LANGUAGE = 'en';

// Core Web8 Translations
export const WEB8_TRANSLATIONS: Translations = {
  // Albanian - Primary Language
  sq: {
    common: {
      loading: 'Duke ngarkuar...',
      error: 'Gabim',
      success: 'Sukses',
      cancel: 'Anulo',
      save: 'Ruaj',
      delete: 'Fshij',
      edit: 'Redakto',
      search: 'Kërko',
      close: 'Mbyll',
      back: 'Kthehu',
      next: 'Tjetër',
      previous: 'I mëparshmi',
      submit: 'Dërgo',
      confirm: 'Konfirmo'
    },
    app: {
      title: 'EuroWeb Ultra Platform',
      tagline: 'Më i Shpejti në Rruzullin Tokësor',
      description: 'Platforma industriale TypeScript me integrimin AGI dhe përpunimin neural në kohë reale'
    },
    navigation: {
      home: 'Kreu',
      neuralDev: 'Zhvillimi Neural',
      neuralSearch: 'Kërkimi Neural',
      agiMed: 'AGI×Med Pro',
      realSearch: 'Kërkimi i Vërtetë',
      ultraSpeed: 'Shpejtësia Ultra',
      settings: 'Cilësimet',
      about: 'Rreth',
      contact: 'Kontakti'
    },
    search: {
      placeholder: 'Kërkoni në rrjetin neural Web8...',
      results: 'Rezultatet',
      noResults: 'Nuk u gjetën rezultate',
      suggestions: 'Sugjerime',
      advanced: 'Kërkimi i përparuar',
      filters: 'Filtrat',
      sortBy: 'Rendit sipas',
      relevance: 'Relevanca',
      date: 'Data',
      score: 'Pikët'
    },
    tabs: {
      newTab: 'Tab i ri',
      closeTab: 'Mbyll tab-in',
      reloadTab: 'Ringarko tab-in',
      duplicateTab: 'Duplikato tab-in',
      moveTab: 'Lëviz tab-in',
      protectedTab: 'Tab i mbrojtur',
      formation: 'Formacioni',
      command: 'Komanda',
      deploy: 'Vendos',
      terminate: 'Përfundo'
    },
    neural: {
      processing: 'Përpunimi neural...',
      analysis: 'Analiza',
      intelligence: 'Inteligjenca',
      learning: 'Të mësuarit',
      prediction: 'Parashikimi',
      optimization: 'Optimizimi',
      accuracy: 'Saktësia',
      confidence: 'Besimi'
    }
  },

  // English - Global Language
  en: {
    common: {
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      cancel: 'Cancel',
      save: 'Save',
      delete: 'Delete',
      edit: 'Edit',
      search: 'Search',
      close: 'Close',
      back: 'Back',
      next: 'Next',
      previous: 'Previous',
      submit: 'Submit',
      confirm: 'Confirm'
    },
    app: {
      title: 'EuroWeb Ultra Platform',
      tagline: 'Fastest on Planet Earth',
      description: 'Industrial TypeScript platform with AGI integration and real-time neural processing'
    },
    navigation: {
      home: 'Home',
      neuralDev: 'Neural Dev',
      neuralSearch: 'Neural Search',
      agiMed: 'AGI×Med Pro',
      realSearch: 'Real Search',
      ultraSpeed: 'Ultra Speed',
      settings: 'Settings',
      about: 'About',
      contact: 'Contact'
    },
    search: {
      placeholder: 'Search Web8 neural grid...',
      results: 'Results',
      noResults: 'No results found',
      suggestions: 'Suggestions',
      advanced: 'Advanced search',
      filters: 'Filters',
      sortBy: 'Sort by',
      relevance: 'Relevance',
      date: 'Date',
      score: 'Score'
    },
    tabs: {
      newTab: 'New tab',
      closeTab: 'Close tab',
      reloadTab: 'Reload tab',
      duplicateTab: 'Duplicate tab',
      moveTab: 'Move tab',
      protectedTab: 'Protected tab',
      formation: 'Formation',
      command: 'Command',
      deploy: 'Deploy',
      terminate: 'Terminate'
    },
    neural: {
      processing: 'Neural processing...',
      analysis: 'Analysis',
      intelligence: 'Intelligence',
      learning: 'Learning',
      prediction: 'Prediction',
      optimization: 'Optimization',
      accuracy: 'Accuracy',
      confidence: 'Confidence'
    }
  },

  // German - European Language
  de: {
    common: {
      loading: 'Wird geladen...',
      error: 'Fehler',
      success: 'Erfolg',
      cancel: 'Abbrechen',
      save: 'Speichern',
      delete: 'Löschen',
      edit: 'Bearbeiten',
      search: 'Suchen',
      close: 'Schließen',
      back: 'Zurück',
      next: 'Weiter',
      previous: 'Vorherige',
      submit: 'Senden',
      confirm: 'Bestätigen'
    },
    app: {
      title: 'EuroWeb Ultra Plattform',
      tagline: 'Das Schnellste auf der Erde',
      description: 'Industrielle TypeScript-Plattform mit AGI-Integration und Echtzeit-Neuralverarbeitung'
    },
    navigation: {
      home: 'Startseite',
      neuralDev: 'Neural Dev',
      neuralSearch: 'Neurale Suche',
      agiMed: 'AGI×Med Pro',
      realSearch: 'Echte Suche',
      ultraSpeed: 'Ultra Geschwindigkeit',
      settings: 'Einstellungen',
      about: 'Über uns',
      contact: 'Kontakt'
    },
    search: {
      placeholder: 'Web8 Neurales Netz durchsuchen...',
      results: 'Ergebnisse',
      noResults: 'Keine Ergebnisse gefunden',
      suggestions: 'Vorschläge',
      advanced: 'Erweiterte Suche',
      filters: 'Filter',
      sortBy: 'Sortieren nach',
      relevance: 'Relevanz',
      date: 'Datum',
      score: 'Bewertung'
    },
    tabs: {
      newTab: 'Neuer Tab',
      closeTab: 'Tab schließen',
      reloadTab: 'Tab neu laden',
      duplicateTab: 'Tab duplizieren',
      moveTab: 'Tab verschieben',
      protectedTab: 'Geschützter Tab',
      formation: 'Formation',
      command: 'Befehl',
      deploy: 'Bereitstellen',
      terminate: 'Beenden'
    },
    neural: {
      processing: 'Neurale Verarbeitung...',
      analysis: 'Analyse',
      intelligence: 'Intelligenz',
      learning: 'Lernen',
      prediction: 'Vorhersage',
      optimization: 'Optimierung',
      accuracy: 'Genauigkeit',
      confidence: 'Vertrauen'
    }
  },

  // French - European Language
  fr: {
    common: {
      loading: 'Chargement...',
      error: 'Erreur',
      success: 'Succès',
      cancel: 'Annuler',
      save: 'Enregistrer',
      delete: 'Supprimer',
      edit: 'Modifier',
      search: 'Rechercher',
      close: 'Fermer',
      back: 'Retour',
      next: 'Suivant',
      previous: 'Précédent',
      submit: 'Soumettre',
      confirm: 'Confirmer'
    },
    app: {
      title: 'Plateforme EuroWeb Ultra',
      tagline: 'Le Plus Rapide sur Terre',
      description: 'Plateforme TypeScript industrielle avec intégration AGI et traitement neural en temps réel'
    },
    navigation: {
      home: 'Accueil',
      neuralDev: 'Dév Neural',
      neuralSearch: 'Recherche Neurale',
      agiMed: 'AGI×Med Pro',
      realSearch: 'Recherche Réelle',
      ultraSpeed: 'Vitesse Ultra',
      settings: 'Paramètres',
      about: 'À propos',
      contact: 'Contact'
    },
    search: {
      placeholder: 'Rechercher dans le réseau neural Web8...',
      results: 'Résultats',
      noResults: 'Aucun résultat trouvé',
      suggestions: 'Suggestions',
      advanced: 'Recherche avancée',
      filters: 'Filtres',
      sortBy: 'Trier par',
      relevance: 'Pertinence',
      date: 'Date',
      score: 'Score'
    },
    tabs: {
      newTab: 'Nouvel onglet',
      closeTab: 'Fermer l\'onglet',
      reloadTab: 'Recharger l\'onglet',
      duplicateTab: 'Dupliquer l\'onglet',
      moveTab: 'Déplacer l\'onglet',
      protectedTab: 'Onglet protégé',
      formation: 'Formation',
      command: 'Commande',
      deploy: 'Déployer',
      terminate: 'Terminer'
    },
    neural: {
      processing: 'Traitement neural...',
      analysis: 'Analyse',
      intelligence: 'Intelligence',
      learning: 'Apprentissage',
      prediction: 'Prédiction',
      optimization: 'Optimisation',
      accuracy: 'Précision',
      confidence: 'Confiance'
    }
  },

  // Add more languages as needed...
  it: {
    common: {
      loading: 'Caricamento...',
      error: 'Errore',
      success: 'Successo',
      cancel: 'Annulla',
      save: 'Salva',
      delete: 'Elimina',
      edit: 'Modifica',
      search: 'Cerca',
      close: 'Chiudi',
      back: 'Indietro',
      next: 'Avanti',
      previous: 'Precedente',
      submit: 'Invia',
      confirm: 'Conferma'
    },
    app: {
      title: 'Piattaforma EuroWeb Ultra',
      tagline: 'Il Più Veloce sulla Terra',
      description: 'Piattaforma TypeScript industriale con integrazione AGI e elaborazione neurale in tempo reale'
    },
    navigation: {
      home: 'Home',
      neuralDev: 'Sviluppo Neurale',
      neuralSearch: 'Ricerca Neurale',
      agiMed: 'AGI×Med Pro',
      realSearch: 'Ricerca Reale',
      ultraSpeed: 'Velocità Ultra',
      settings: 'Impostazioni',
      about: 'Chi siamo',
      contact: 'Contatto'
    },
    search: {
      placeholder: 'Cerca nella rete neurale Web8...',
      results: 'Risultati',
      noResults: 'Nessun risultato trovato',
      suggestions: 'Suggerimenti',
      advanced: 'Ricerca avanzata',
      filters: 'Filtri',
      sortBy: 'Ordina per',
      relevance: 'Rilevanza',
      date: 'Data',
      score: 'Punteggio'
    },
    tabs: {
      newTab: 'Nuova scheda',
      closeTab: 'Chiudi scheda',
      reloadTab: 'Ricarica scheda',
      duplicateTab: 'Duplica scheda',
      moveTab: 'Sposta scheda',
      protectedTab: 'Scheda protetta',
      formation: 'Formazione',
      command: 'Comando',
      deploy: 'Distribuisci',
      terminate: 'Termina'
    },
    neural: {
      processing: 'Elaborazione neurale...',
      analysis: 'Analisi',
      intelligence: 'Intelligenza',
      learning: 'Apprendimento',
      prediction: 'Predizione',
      optimization: 'Ottimizzazione',
      accuracy: 'Precisione',
      confidence: 'Fiducia'
    }
  },

  es: {
    common: {
      loading: 'Cargando...',
      error: 'Error',
      success: 'Éxito',
      cancel: 'Cancelar',
      save: 'Guardar',
      delete: 'Eliminar',
      edit: 'Editar',
      search: 'Buscar',
      close: 'Cerrar',
      back: 'Atrás',
      next: 'Siguiente',
      previous: 'Anterior',
      submit: 'Enviar',
      confirm: 'Confirmar'
    },
    app: {
      title: 'Plataforma EuroWeb Ultra',
      tagline: 'El Más Rápido en la Tierra',
      description: 'Plataforma TypeScript industrial con integración AGI y procesamiento neural en tiempo real'
    },
    navigation: {
      home: 'Inicio',
      neuralDev: 'Desarrollo Neural',
      neuralSearch: 'Búsqueda Neural',
      agiMed: 'AGI×Med Pro',
      realSearch: 'Búsqueda Real',
      ultraSpeed: 'Velocidad Ultra',
      settings: 'Configuración',
      about: 'Acerca de',
      contact: 'Contacto'
    },
    search: {
      placeholder: 'Buscar en la red neural Web8...',
      results: 'Resultados',
      noResults: 'No se encontraron resultados',
      suggestions: 'Sugerencias',
      advanced: 'Búsqueda avanzada',
      filters: 'Filtros',
      sortBy: 'Ordenar por',
      relevance: 'Relevancia',
      date: 'Fecha',
      score: 'Puntuación'
    },
    tabs: {
      newTab: 'Nueva pestaña',
      closeTab: 'Cerrar pestaña',
      reloadTab: 'Recargar pestaña',
      duplicateTab: 'Duplicar pestaña',
      moveTab: 'Mover pestaña',
      protectedTab: 'Pestaña protegida',
      formation: 'Formación',
      command: 'Comando',
      deploy: 'Desplegar',
      terminate: 'Terminar'
    },
    neural: {
      processing: 'Procesamiento neural...',
      analysis: 'Análisis',
      intelligence: 'Inteligencia',
      learning: 'Aprendizaje',
      prediction: 'Predicción',
      optimization: 'Optimización',
      accuracy: 'Precisión',
      confidence: 'Confianza'
    }
  },

  ru: {
    common: {
      loading: 'Загрузка...',
      error: 'Ошибка',
      success: 'Успех',
      cancel: 'Отмена',
      save: 'Сохранить',
      delete: 'Удалить',
      edit: 'Редактировать',
      search: 'Поиск',
      close: 'Закрыть',
      back: 'Назад',
      next: 'Далее',
      previous: 'Предыдущий',
      submit: 'Отправить',
      confirm: 'Подтвердить'
    },
    app: {
      title: 'Платформа EuroWeb Ultra',
      tagline: 'Самый Быстрый на Земле',
      description: 'Промышленная платформа TypeScript с интеграцией AGI и нейронной обработкой в реальном времени'
    },
    navigation: {
      home: 'Главная',
      neuralDev: 'Нейронная Разработка',
      neuralSearch: 'Нейронный Поиск',
      agiMed: 'AGI×Med Pro',
      realSearch: 'Реальный Поиск',
      ultraSpeed: 'Ультра Скорость',
      settings: 'Настройки',
      about: 'О нас',
      contact: 'Контакт'
    },
    search: {
      placeholder: 'Поиск в нейронной сети Web8...',
      results: 'Результаты',
      noResults: 'Результаты не найдены',
      suggestions: 'Предложения',
      advanced: 'Расширенный поиск',
      filters: 'Фильтры',
      sortBy: 'Сортировать по',
      relevance: 'Релевантность',
      date: 'Дата',
      score: 'Оценка'
    },
    tabs: {
      newTab: 'Новая вкладка',
      closeTab: 'Закрыть вкладку',
      reloadTab: 'Перезагрузить вкладку',
      duplicateTab: 'Дублировать вкладку',
      moveTab: 'Переместить вкладку',
      protectedTab: 'Защищенная вкладка',
      formation: 'Формация',
      command: 'Команда',
      deploy: 'Развернуть',
      terminate: 'Завершить'
    },
    neural: {
      processing: 'Нейронная обработка...',
      analysis: 'Анализ',
      intelligence: 'Интеллект',
      learning: 'Обучение',
      prediction: 'Предсказание',
      optimization: 'Оптимизация',
      accuracy: 'Точность',
      confidence: 'Уверенность'
    }
  },

  ar: {
    common: {
      loading: 'جاري التحميل...',
      error: 'خطأ',
      success: 'نجح',
      cancel: 'إلغاء',
      save: 'حفظ',
      delete: 'حذف',
      edit: 'تحرير',
      search: 'بحث',
      close: 'إغلاق',
      back: 'العودة',
      next: 'التالي',
      previous: 'السابق',
      submit: 'إرسال',
      confirm: 'تأكيد'
    },
    app: {
      title: 'منصة EuroWeb Ultra',
      tagline: 'الأسرع على كوكب الأرض',
      description: 'منصة TypeScript صناعية مع تكامل AGI ومعالجة عصبية في الوقت الفعلي'
    },
    navigation: {
      home: 'الرئيسية',
      neuralDev: 'التطوير العصبي',
      neuralSearch: 'البحث العصبي',
      agiMed: 'AGI×Med Pro',
      realSearch: 'البحث الحقيقي',
      ultraSpeed: 'السرعة الفائقة',
      settings: 'الإعدادات',
      about: 'حول',
      contact: 'اتصال'
    },
    search: {
      placeholder: 'البحث في الشبكة العصبية Web8...',
      results: 'النتائج',
      noResults: 'لم يتم العثور على نتائج',
      suggestions: 'اقتراحات',
      advanced: 'بحث متقدم',
      filters: 'المرشحات',
      sortBy: 'ترتيب حسب',
      relevance: 'الصلة',
      date: 'التاريخ',
      score: 'النقاط'
    },
    tabs: {
      newTab: 'علامة تبويب جديدة',
      closeTab: 'إغلاق علامة التبويب',
      reloadTab: 'إعادة تحميل علامة التبويب',
      duplicateTab: 'تكرار علامة التبويب',
      moveTab: 'نقل علامة التبويب',
      protectedTab: 'علامة تبويب محمية',
      formation: 'التشكيل',
      command: 'الأمر',
      deploy: 'نشر',
      terminate: 'إنهاء'
    },
    neural: {
      processing: 'المعالجة العصبية...',
      analysis: 'التحليل',
      intelligence: 'الذكاء',
      learning: 'التعلم',
      prediction: 'التنبؤ',
      optimization: 'التحسين',
      accuracy: 'الدقة',
      confidence: 'الثقة'
    }
  }
};

// Language Detection Utilities
export class LanguageDetector {
  static detectBrowserLanguage(): string {
    if (typeof window === 'undefined') return DEFAULT_LANGUAGE;
    
    const browserLang = navigator.language || (navigator as any).userLanguage;
    const langCode = browserLang.split('-')[0];
    
    // Check if exact match exists
    if (SUPPORTED_LANGUAGES.find(lang => lang.code === browserLang)) {
      return browserLang;
    }
    
    // Check if base language exists
    if (SUPPORTED_LANGUAGES.find(lang => lang.code === langCode)) {
      return langCode;
    }
    
    return DEFAULT_LANGUAGE;
  }

  static detectRegionLanguage(): string {
    if (typeof window === 'undefined') return DEFAULT_LANGUAGE;
    
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    
    // European timezones - prefer Albanian for Balkans
    if (timezone.includes('Europe/Tirane') || timezone.includes('Europe/Skopje')) {
      return 'sq';
    }
    
    if (timezone.includes('Europe/Berlin')) return 'de';
    if (timezone.includes('Europe/Paris')) return 'fr';
    if (timezone.includes('Europe/Rome')) return 'it';
    if (timezone.includes('Europe/Madrid')) return 'es';
    if (timezone.includes('Europe/Moscow')) return 'ru';
    
    return this.detectBrowserLanguage();
  }
}

// Export language utilities
export { 
  SUPPORTED_LANGUAGES as languages, 
  WEB8_TRANSLATIONS as translations, 
  DEFAULT_LANGUAGE as defaultLanguage, 
  FALLBACK_LANGUAGE as fallbackLanguage 
};
