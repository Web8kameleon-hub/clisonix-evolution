'use client';

import { useEffect, useState } from 'react';

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

export default function InstallAppButton({ className = '' }: { className?: string }) {
  const [prompt, setPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [installed, setInstalled] = useState(false);
  const [showHelp, setShowHelp] = useState(false);
  const [twaUrl, setTwaUrl] = useState('');

  useEffect(() => {
    const media = window.matchMedia('(display-mode: standalone)');
    const sync = () => setInstalled(media.matches);
    const capture = (event: Event) => {
      event.preventDefault();
      setPrompt(event as BeforeInstallPromptEvent);
    };
    const markInstalled = () => {
      setInstalled(true);
      setPrompt(null);
      setShowHelp(false);
    };
    sync();
    fetch('/api/install/capabilities', { cache: 'no-store' })
      .then((response) => response.ok ? response.json() : null)
      .then((data) => setTwaUrl(data?.twa?.available && typeof data.twa.url === 'string' ? data.twa.url : ''))
      .catch(() => setTwaUrl(''));
    media.addEventListener('change', sync);
    window.addEventListener('beforeinstallprompt', capture);
    window.addEventListener('appinstalled', markInstalled);
    return () => {
      media.removeEventListener('change', sync);
      window.removeEventListener('beforeinstallprompt', capture);
      window.removeEventListener('appinstalled', markInstalled);
    };
  }, []);

  async function install() {
    if (!prompt && twaUrl && /Android/i.test(navigator.userAgent)) {
      window.location.assign(twaUrl);
      return;
    }
    if (!prompt) {
      setShowHelp((value) => !value);
      return;
    }
    await prompt.prompt();
    const choice = await prompt.userChoice;
    if (choice.outcome === 'accepted') setPrompt(null);
  }

  return (
    <div className="relative">
      <button
        type="button"
        onClick={install}
        disabled={installed}
        className={className || 'rounded-lg bg-slate-900 px-3 py-2 text-sm font-semibold text-white disabled:opacity-60'}
      >
        {installed ? 'App installed' : 'Install app'}
      </button>
      {showHelp && !installed ? (
        <div role="status" className="absolute right-0 z-50 mt-2 w-72 rounded-xl border border-slate-700 bg-slate-950 p-3 text-left text-xs text-slate-200 shadow-xl">
          {twaUrl ? <a className="mb-2 block font-semibold text-emerald-300 underline" href={twaUrl}>Install the Android TWA</a> : null}
          Open the browser menu and choose <strong>Install app</strong> or <strong>Add to Home Screen</strong> for the PWA. The install action remains available whenever Clisonix is not installed.
        </div>
      ) : null}
    </div>
  );
}
