# INTERNATIONALIZATION (i18n) - IMPLEMENTATION GUIDE

**Status**: Ready to Implement  
**Time Estimate**: 2-3 hours  
**Difficulty**: ⭐⭐ (Medium)  
**Languages**: English (default) + Albanian + extensible

---

## Architecture

```
Browser
  ↓
Detect language (localStorage → navigator.language → 'en')
  ↓
┌─────────────────────────────────────┐
│     react-i18next Configuration     │
├─────────────────────────────────────┤
│ Load translation file based on lang │
│ (public/locales/{lang}/common.json) │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│  React Components use: t('key')     │
│  - dashboard.title                  │
│  - buttons.signIn                   │
│  - errors.notFound                  │
└─────────────────────────────────────┘
  ↓
Language Toggle (+ save to localStorage)
```

---

## STEP 1: Install Dependencies

```bash
cd apps/web

npm install react-i18next i18next i18next-browser-languagedetector i18next-http-backend

npm install --save-dev @types/react-i18next
```

---

## STEP 2: Create i18n Config

**File**: `apps/web/lib/i18n/config.ts` (CREATE)

```typescript
/**
 * i18next Configuration
 * Multi-language support with auto-detection
 */

import i18n from 'i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpBackend from 'i18next-http-backend';
import { initReactI18next } from 'react-i18next';

// Import translation files directly (alternative to HTTP backend)
import enCommon from '@/locales/en/common.json';
import sqCommon from '@/locales/sq/common.json';
import deCommon from '@/locales/de/common.json';

import enErrors from '@/locales/en/errors.json';
import sqErrors from '@/locales/sq/errors.json';
import deErrors from '@/locales/de/errors.json';

import enMusicStudio from '@/locales/en/music-studio.json';
import sqMusicStudio from '@/locales/sq/music-studio.json';
import deMusicStudio from '@/locales/de/music-studio.json';

const resources = {
  en: {
    common: enCommon,
    errors: enErrors,
    musicStudio: enMusicStudio,
  },
  sq: {
    common: sqCommon,
    errors: sqErrors,
    musicStudio: sqMusicStudio,
  },
  de: {
    common: deCommon,
    errors: deErrors,
    musicStudio: deMusicStudio,
  },
};

i18n
  // Use the language detector plugin
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    defaultNS: 'common',
    
    // Detect browser language
    detection: {
      order: [
        'localStorage',      // Check localStorage first
        'navigator',        // Then browser language
        'htmlTag',          // Then html lang attribute
      ],
      caches: ['localStorage'],
    },
    
    // Interpolation
    interpolation: {
      escapeValue: false, // React already escapes
      formatSeparator: ',',
    },
    
    // Debug mode (set to true in development)
    debug: process.env.NODE_ENV === 'development',
    
    // Namespace configuration
    ns: ['common', 'errors', 'musicStudio'],
    defaultNS: 'common',
  });

export default i18n;
```

---

## STEP 3: Create Language Detector Utility

**File**: `apps/web/lib/i18n/detector.ts` (CREATE)

```typescript
/**
 * Language Detection Utility
 * Auto-detect browser language with fallback
 */

export function getDeviceLanguage(): string {
  // 1. Check localStorage (user preference)
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('i18nextLng');
    if (saved) {
      return saved;
    }
  }

  // 2. Check browser language
  if (typeof navigator !== 'undefined') {
    const browserLang = navigator.language.split('-')[0]; // 'sq', 'en', 'de'
    const supported = ['en', 'sq', 'de'];
    
    if (supported.includes(browserLang)) {
      return browserLang;
    }

    // Check if region-specific variant exists
    // e.g., 'en-US' → 'en'
    const baseLanguage = browserLang.split('-')[0];
    if (supported.includes(baseLanguage)) {
      return baseLanguage;
    }
  }

  // 3. Default to English
  return 'en';
}

export function setLanguage(language: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('i18nextLng', language);
    localStorage.setItem('user_language', language); // Backup
  }
}

export function getSupportedLanguages() {
  return [
    { code: 'en', name: 'English', nativeName: 'English', flag: '🇬🇧' },
    { code: 'sq', name: 'Albanian', nativeName: 'Shqip', flag: '🇦🇱' },
    { code: 'de', name: 'German', nativeName: 'Deutsch', flag: '🇩🇪' },
  ];
}
```

---

## STEP 4: Create React Hook

**File**: `apps/web/hooks/useTranslationContext.ts` (CREATE)

```typescript
/**
 * Custom Hook: useTranslationContext
 * Provides translation utilities to components
 */

import { useTranslation } from 'react-i18next';
import { setLanguage } from '@/lib/i18n/detector';
import { useCallback } from 'react';

export function useTranslationContext() {
  const { t, i18n } = useTranslation();

  const changeLanguage = useCallback(
    async (lng: string) => {
      await i18n.changeLanguage(lng);
      setLanguage(lng);
    },
    [i18n]
  );

  return {
    t,
    language: i18n.language,
    changeLanguage,
    isReady: i18n.isInitialized,
  };
}
```

---

## STEP 5: Create Translation Files

**File**: `apps/web/public/locales/en/common.json` (CREATE)

```json
{
  "app": {
    "name": "Clisonix",
    "tagline": "Professional AI for Enterprises",
    "description": "Unified AI platform with 76+ microservices"
  },
  "nav": {
    "home": "Home",
    "features": "Features",
    "pricing": "Pricing",
    "docs": "Documentation",
    "dashboard": "Dashboard",
    "settings": "Settings",
    "profile": "Profile",
    "logout": "Sign Out"
  },
  "dashboard": {
    "title": "Dashboard",
    "welcome": "Welcome {{name}}",
    "lastLogin": "Last login {{date}}",
    "totalServices": "Total Services",
    "onlineServices": "Online Services",
    "recentActivity": "Recent Activity"
  },
  "buttons": {
    "signIn": "Sign In",
    "signUp": "Sign Up",
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete",
    "edit": "Edit",
    "close": "Close",
    "submit": "Submit",
    "subscribe": "Subscribe",
    "learnMore": "Learn More",
    "tryNow": "Try Now"
  },
  "labels": {
    "email": "Email",
    "password": "Password",
    "firstName": "First Name",
    "lastName": "Last Name",
    "language": "Language",
    "timezone": "Timezone",
    "theme": "Theme"
  },
  "messages": {
    "loading": "Loading...",
    "success": "Success!",
    "error": "Error",
    "warning": "Warning",
    "info": "Information",
    "noData": "No data available"
  },
  "services": {
    "oceanCore": {
      "title": "Ocean Core",
      "description": "Knowledge orchestration engine - Global intelligence coordinator"
    },
    "curiosity": {
      "title": "Curiosity Ocean",
      "description": "Hybrid AI assistant - Multilingual knowledge discovery"
    },
    "ai9999": {
      "title": "AI Global 9999",
      "description": "Multimodal engine - Audio, video, text synthesis"
    }
  },
  "musicStudio": {
    "title": "Music Studio",
    "description": "Create music with AI",
    "newComposition": "New Composition",
    "save": "Save Composition",
    "export": "Export as WAV/MP3",
    "tempo": "Tempo (BPM)"
  }
}
```

**File**: `apps/web/public/locales/sq/common.json` (CREATE)

```json
{
  "app": {
    "name": "Clisonix",
    "tagline": "AI Profesional për Sipërmarrje",
    "description": "Platforma uniforme AI me 76+ mikroshërbime"
  },
  "nav": {
    "home": "Ballina",
    "features": "Veçoritë",
    "pricing": "Çmimet",
    "docs": "Dokumentimi",
    "dashboard": "Tabela Kryesore",
    "settings": "Cilësimet",
    "profile": "Profili",
    "logout": "Dil"
  },
  "dashboard": {
    "title": "Tabela Kryesore",
    "welcome": "Mirë se vjen {{name}}",
    "lastLogin": "Hyrja e fundit {{date}}",
    "totalServices": "Shërbime Totale",
    "onlineServices": "Shërbime Online",
    "recentActivity": "Aktiviteti i Fundit"
  },
  "buttons": {
    "signIn": "Hyj",
    "signUp": "Regjistrohu",
    "save": "Ruaj",
    "cancel": "Anullo",
    "delete": "Fshi",
    "edit": "Ndrysho",
    "close": "Mbyll",
    "submit": "Dërgo",
    "subscribe": "Përshkruhu",
    "learnMore": "Mëso më Shumë",
    "tryNow": "Provo Tani"
  },
  "labels": {
    "email": "Email",
    "password": "Fjalëkalim",
    "firstName": "Emri",
    "lastName": "Mbiemri",
    "language": "Gjuha",
    "timezone": "Fusihorari",
    "theme": "Tema"
  },
  "messages": {
    "loading": "Po ngarkohet...",
    "success": "Sukses!",
    "error": "Gabim",
    "warning": "Paralajmërim",
    "info": "Informacion",
    "noData": "Pa të dhëna të disponueshme"
  },
  "services": {
    "oceanCore": {
      "title": "Ocean Core",
      "description": "Motor orkestrim njohurish - Koordinator inteligjence globale"
    },
    "curiosity": {
      "title": "Curiosity Ocean",
      "description": "Asistent AI hibrid - Zbulim njohurish multilingv"
    },
    "ai9999": {
      "title": "AI Global 9999",
      "description": "Motor shumëmodal - Sintezë audio, video, teksti"
    }
  },
  "musicStudio": {
    "title": "Studio Muzike",
    "description": "Krijo muzikë me AI",
    "newComposition": "Kompozim i Ri",
    "save": "Ruaj Kompozimin",
    "export": "Eksporto si WAV/MP3",
    "tempo": "Tempo (BPM)"
  }
}
```

**File**: `apps/web/public/locales/de/common.json` (CREATE)

```json
{
  "app": {
    "name": "Clisonix",
    "tagline": "Professionelle KI für Unternehmen",
    "description": "Einheitliche KI-Plattform mit 76+ Mikrodiensten"
  },
  "nav": {
    "home": "Startseite",
    "features": "Funktionen",
    "pricing": "Preise",
    "docs": "Dokumentation",
    "dashboard": "Dashboard",
    "settings": "Einstellungen",
    "profile": "Profil",
    "logout": "Abmelden"
  },
  "dashboard": {
    "title": "Dashboard",
    "welcome": "Willkommen {{name}}",
    "lastLogin": "Letzte Anmeldung {{date}}",
    "totalServices": "Gesamtdienste",
    "onlineServices": "Online-Dienste",
    "recentActivity": "Aktuelle Aktivitäten"
  },
  "buttons": {
    "signIn": "Anmelden",
    "signUp": "Registrieren",
    "save": "Speichern",
    "cancel": "Abbrechen",
    "delete": "Löschen",
    "edit": "Bearbeiten",
    "close": "Schließen",
    "submit": "Absenden",
    "subscribe": "Abonnieren",
    "learnMore": "Mehr erfahren",
    "tryNow": "Jetzt ausprobieren"
  },
  "labels": {
    "email": "E-Mail",
    "password": "Passwort",
    "firstName": "Vorname",
    "lastName": "Nachname",
    "language": "Sprache",
    "timezone": "Zeitzone",
    "theme": "Design"
  },
  "messages": {
    "loading": "Wird geladen...",
    "success": "Erfolg!",
    "error": "Fehler",
    "warning": "Warnung",
    "info": "Information",
    "noData": "Keine Daten verfügbar"
  },
  "services": {
    "oceanCore": {
      "title": "Ocean Core",
      "description": "Wissens-Orchestrierungsmotor - Globaler Intelligenzkoordinator"
    },
    "curiosity": {
      "title": "Curiosity Ocean",
      "description": "Hybrider KI-Assistent - Multilinguale Wissensentdeckung"
    },
    "ai9999": {
      "title": "AI Global 9999",
      "description": "Multimodales Modul - Audio-, Video-, Textsynthese"
    }
  },
  "musicStudio": {
    "title": "Musikstudio",
    "description": "Erstellen Sie Musik mit KI",
    "newComposition": "Neue Komposition",
    "save": "Komposition speichern",
    "export": "Als WAV/MP3 exportieren",
    "tempo": "Tempo (BPM)"
  }
}
```

**File**: `apps/web/public/locales/en/errors.json` (CREATE)

```json
{
  "404": "Page not found",
  "500": "Server error",
  "unauthorized": "Unauthorized",
  "forbidden": "Forbidden",
  "validation": "Validation error",
  "network": "Network error",
  "timeout": "Request timeout",
  "invalidEmail": "Invalid email address",
  "passwordTooShort": "Password must be at least 8 characters",
  "fieldRequired": "This field is required"
}
```

**File**: `apps/web/public/locales/sq/errors.json` (CREATE)

```json
{
  "404": "Faqja nuk u gjet",
  "500": "Gabim në shërbyes",
  "unauthorized": "I paautorizuar",
  "forbidden": "I ndaluar",
  "validation": "Gabim në validim",
  "network": "Gabim në rrjet",
  "timeout": "Kërkesa ka skaduar",
  "invalidEmail": "Adresa email jo e vlefshme",
  "passwordTooShort": "Fjalëkalimi duhet të ketë të paktën 8 karaktere",
  "fieldRequired": "Ky fushë kërkohet"
}
```

**File**: `apps/web/public/locales/de/errors.json` (CREATE)

```json
{
  "404": "Seite nicht gefunden",
  "500": "Serverfehler",
  "unauthorized": "Nicht autorisiert",
  "forbidden": "Verboten",
  "validation": "Validierungsfehler",
  "network": "Netzwerkfehler",
  "timeout": "Anforderung abgelaufen",
  "invalidEmail": "Ungültige E-Mail-Adresse",
  "passwordTooShort": "Das Passwort muss mindestens 8 Zeichen lang sein",
  "fieldRequired": "Dieses Feld ist erforderlich"
}
```

**File**: `apps/web/public/locales/en/music-studio.json` (CREATE)

```json
{
  "title": "Music Studio",
  "description": "Create beautiful music with AI",
  "waveforms": {
    "sine": "Sine (Pure Tone)",
    "square": "Square (Digital)",
    "sawtooth": "Sawtooth (Bright)",
    "triangle": "Triangle (Soft)",
    "bass": "Bass (Deep)",
    "organ": "Organ (Rich)",
    "piano": "Piano (Warm)"
  },
  "genres": {
    "classical": "Classical",
    "jazz": "Jazz",
    "electronic": "Electronic",
    "ambient": "Ambient",
    "rock": "Rock",
    "hiphop": "Hip-Hop",
    "pop": "Pop"
  },
  "effects": {
    "reverb": "Reverb",
    "echo": "Echo",
    "chorus": "Chorus",
    "vibrato": "Vibrato",
    "tremolo": "Tremolo",
    "distortion": "Distortion"
  },
  "controls": {
    "tempo": "Tempo",
    "volume": "Volume",
    "play": "Play",
    "stop": "Stop",
    "record": "Record",
    "save": "Save",
    "export": "Export"
  },
  "notation": {
    "title": "Solfège Notation",
    "notes": {
      "do": "Do",
      "re": "Re",
      "mi": "Mi",
      "fa": "Fa",
      "sol": "Sol",
      "la": "La",
      "si": "Si"
    }
  }
}
```

**File**: `apps/web/public/locales/sq/music-studio.json` (CREATE)

```json
{
  "title": "Studio Muzike",
  "description": "Krijo muzikë të bukur me AI",
  "waveforms": {
    "sine": "Sine (Ton i Pastër)",
    "square": "Square (Digjital)",
    "sawtooth": "Sawtooth (i Ndritshëm)",
    "triangle": "Triangle (i Butë)",
    "bass": "Bass (i Thellë)",
    "organ": "Organ (i Pasur)",
    "piano": "Piano (i Ngrohtë)"
  },
  "genres": {
    "classical": "Klasike",
    "jazz": "Xhaz",
    "electronic": "Elektronike",
    "ambient": "Ambient",
    "rock": "Rock",
    "hiphop": "Hip-Hop",
    "pop": "Pop"
  },
  "effects": {
    "reverb": "Reverb",
    "echo": "Jehona",
    "chorus": "Kor",
    "vibrato": "Vibrato",
    "tremolo": "Tremolo",
    "distortion": "Distorzion"
  },
  "controls": {
    "tempo": "Tempo",
    "volume": "Volumi",
    "play": "Lej",
    "stop": "Ndal",
    "record": "Regjistro",
    "save": "Ruaj",
    "export": "Eksporto"
  },
  "notation": {
    "title": "Notimi Solfège",
    "notes": {
      "do": "Do",
      "re": "Re",
      "mi": "Mi",
      "fa": "Fa",
      "sol": "Sol",
      "la": "La",
      "si": "Si"
    }
  }
}
```

**File**: `apps/web/public/locales/de/music-studio.json` (CREATE)

```json
{
  "title": "Musikstudio",
  "description": "Erstellen Sie wunderschöne Musik mit KI",
  "waveforms": {
    "sine": "Sinus (Reiner Ton)",
    "square": "Quadrat (Digital)",
    "sawtooth": "Sägezahn (Hell)",
    "triangle": "Dreieck (Weich)",
    "bass": "Bass (Tief)",
    "organ": "Orgel (Reich)",
    "piano": "Klavier (Warm)"
  },
  "genres": {
    "classical": "Klassisch",
    "jazz": "Jazz",
    "electronic": "Elektronisch",
    "ambient": "Ambient",
    "rock": "Rock",
    "hiphop": "Hip-Hop",
    "pop": "Pop"
  },
  "effects": {
    "reverb": "Hall",
    "echo": "Echo",
    "chorus": "Chor",
    "vibrato": "Vibrato",
    "tremolo": "Tremolo",
    "distortion": "Verzerrung"
  },
  "controls": {
    "tempo": "Tempo",
    "volume": "Lautstärke",
    "play": "Wiedergabe",
    "stop": "Stopp",
    "record": "Aufnahme",
    "save": "Speichern",
    "export": "Exportieren"
  },
  "notation": {
    "title": "Solmisation",
    "notes": {
      "do": "Do",
      "re": "Re",
      "mi": "Mi",
      "fa": "Fa",
      "sol": "Sol",
      "la": "La",
      "si": "Si"
    }
  }
}
```

---

## STEP 6: Update App Layout

**File**: `apps/web/app/layout.tsx` (UPDATE)

```typescript
import '@/lib/i18n/config';  // Add this at the top
import type { Metadata } from 'next';
import { I18nextProvider } from 'react-i18next';
import i18n from '@/lib/i18n/config';
import { ClerkProvider } from '@clerk/nextjs';

export const metadata: Metadata = {
  title: 'Clisonix - AI Platform',
  description: 'Professional AI for enterprises',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html suppressHydrationWarning>
      <body>
        <ClerkProvider>
          <I18nextProvider i18n={i18n}>
            {children}
          </I18nextProvider>
        </ClerkProvider>
      </body>
    </html>
  );
}
```

---

## STEP 7: Create Language Switcher Component

**File**: `apps/web/components/LanguageSwitcher.tsx` (CREATE)

```typescript
'use client';

import { useTranslation } from 'react-i18next';
import { getSupportedLanguages } from '@/lib/i18n/detector';
import { useState } from 'react';

export function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const languages = getSupportedLanguages();
  const current = languages.find(l => l.code === i18n.language);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700"
      >
        <span>{current?.flag}</span>
        <span className="text-sm font-medium">{current?.name}</span>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-lg z-50">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => {
                i18n.changeLanguage(lang.code);
                setIsOpen(false);
              }}
              className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-700 ${
                i18n.language === lang.code ? 'bg-blue-600' : ''
              }`}
            >
              <span>{lang.flag}</span> {lang.nativeName}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## STEP 8: Example Component Using i18n

**File**: `apps/web/components/Dashboard.tsx` (EXAMPLE)

```typescript
'use client';

import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from './LanguageSwitcher';

export function Dashboard() {
  const { t } = useTranslation(['common', 'services']);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-white">
          {t('common:dashboard.title')}
        </h1>
        <LanguageSwitcher />
      </div>

      {/* Welcome */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h2 className="text-xl font-semibold text-white">
          {t('common:dashboard.welcome', { name: 'User' })}
        </h2>
        <p className="text-gray-300 text-sm">
          {t('common:dashboard.lastLogin', { date: new Date().toLocaleDateString() })}
        </p>
      </div>

      {/* Services */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <ServiceCard
          title={t('services:oceanCore.title')}
          description={t('services:oceanCore.description')}
        />
        <ServiceCard
          title={t('services:curiosity.title')}
          description={t('services:curiosity.description')}
        />
      </div>
    </div>
  );
}

function ServiceCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
      <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </div>
  );
}
```

---

## STEP 9: Backend i18n (Python Services)

**File**: `services/reporting/main.py` (EXAMPLE CHANGE)

```python
# BEFORE (hardcoded Albanian):
"""Merr CPU/Memory stats REAL për çdo container"""

# AFTER (English docstrings):
"""Get real CPU/Memory stats for each container"""

# For user-facing strings, use a simple translation dict
TRANSLATIONS = {
    "en": {
        "cpu_label": "CPU Usage",
        "memory_label": "Memory Usage",
    },
    "sq": {
        "cpu_label": "Përdorimi i CPU",
        "memory_label": "Përdorimi i Memories",
    },
}

def get_label(key: str, lang: str = "en") -> str:
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
```

---

## Testing Checklist

- [ ] App loads → detects browser language automatically
- [ ] Switch to Albanian → all text translates to Albanian
- [ ] Switch to German → all text translates to German
- [ ] Switch to English → all text in English
- [ ] Refresh page → language preference persists
- [ ] Music Studio labels translate correctly
- [ ] Error messages appear in correct language
- [ ] i18n key missing → shows key (fallback behavior)

---

## Adding New Languages (Future)

To add Spanish, French, etc.:

1. Create `apps/web/public/locales/{lang}/common.json`
2. Create `apps/web/public/locales/{lang}/errors.json`
3. Create `apps/web/public/locales/{lang}/music-studio.json`
4. Add to `getSupportedLanguages()` in `lib/i18n/detector.ts`
5. Import in `lib/i18n/config.ts`

---

## Summary

✅ react-i18next configuration  
✅ Language auto-detection (browser → localStorage)  
✅ 3 languages: English, Albanian, German  
✅ Translation files for: common, errors, music-studio  
✅ Language switcher component  
✅ Backend i18n support  

**Time**: 2-3 hours  
**Difficulty**: Medium (⭐⭐)
