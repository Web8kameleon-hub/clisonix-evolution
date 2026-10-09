'use client';

import { useState, useRef, useCallback, useEffect } from 'react';

// ─────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────

interface ShopItem {
  id: string;
  url: string;
  name: string;
  category: string;
  description: string;
  tags: string[];
  image_url: string;
  price_range: string;
  rating: number;
  verified: boolean;
  read_snippet: string;
}

interface LinkPreview {
  url: string;
  title: string;
  description: string;
  image_url: string;
  price_hints: string[];
  snippet: string;
  error?: string;
}

interface OceanMessage {
  id: string;
  role: 'user' | 'ai';
  content: string;
  isStreaming?: boolean;
}

// ─────────────────────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────────────────────

const CATEGORIES = [
  { slug: '', label: 'Të gjitha', emoji: '🛍️' },
  { slug: 'fashion',  label: 'Modë',     emoji: '👗' },
  { slug: 'beauty',   label: 'Bukuri',   emoji: '💄' },
  { slug: 'wellness', label: 'Mirëqenie',emoji: '🧘' },
  { slug: 'home',     label: 'Shtëpi',   emoji: '🏠' },
  { slug: 'food',     label: 'Ushqim',   emoji: '🍽️' },
  { slug: 'gadgets',  label: 'Teknologji',emoji: '📱' },
  { slug: 'gifts',    label: 'Dhurata',  emoji: '🎁' },
  { slug: 'sports',   label: 'Sport',    emoji: '🏋️' },
  { slug: 'kids',     label: 'Fëmijë',   emoji: '🧸' },
  { slug: 'books',    label: 'Libra',    emoji: '📚' },
  { slug: 'other',    label: 'Tjera',    emoji: '✨' },
];

// ─────────────────────────────────────────────────────────────
// HELPERS
// ─────────────────────────────────────────────────────────────

function categoryEmoji(slug: string): string {
  return CATEGORIES.find(c => c.slug === slug)?.emoji ?? '🛍️';
}

function parseSseChunk(raw: string): string {
  let text = '';
  for (const line of raw.split('\n')) {
    if (!line.startsWith('data: ')) continue;
    const payload = line.slice(6).trim();
    if (payload === '[DONE]') continue;
    try {
      const obj = JSON.parse(payload) as Record<string, unknown>;
      if (typeof obj.choices !== 'undefined') {
        // OpenAI-style token
        const delta = (obj.choices as Array<{ delta?: { content?: string } }>)[0]?.delta?.content;
        if (delta) text += delta;
      } else if (typeof obj.response === 'string') {
        text += obj.response;
      } else if (typeof obj.content === 'string') {
        text += obj.content;
      } else if (typeof obj.text === 'string') {
        text += obj.text;
      }
      // skip shopping-therapy catalogue SSE events
    } catch {
      if (payload && payload !== '[DONE]') text += payload;
    }
  }
  return text;
}

// ─────────────────────────────────────────────────────────────
// SUB-COMPONENTS
// ─────────────────────────────────────────────────────────────

function ShopCard({ item }: { item: ShopItem }) {
  const emoji = categoryEmoji(item.category);
  const catLabel = CATEGORIES.find(c => c.slug === item.category)?.label ?? item.category;

  return (
    <div className="group bg-white/5 border border-white/10 rounded-2xl overflow-hidden hover:border-purple-400/50 hover:bg-white/8 transition-all duration-200 flex flex-col">
      {/* Image */}
      <div className="relative h-40 bg-gradient-to-br from-purple-900/40 to-pink-900/30 overflow-hidden flex items-center justify-center">
        {item.image_url ? (
          <img
            src={item.image_url}
            alt={item.name}
            className="w-full h-full object-cover opacity-80 group-hover:opacity-100 transition-opacity"
            onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
          />
        ) : (
          <span className="text-5xl opacity-40">{emoji}</span>
        )}
        {item.verified && (
          <span className="absolute top-2 right-2 bg-green-500/80 text-white text-xs px-2 py-0.5 rounded-full">
            ✓ Verifikuar
          </span>
        )}
      </div>

      {/* Content */}
      <div className="p-4 flex flex-col gap-2 flex-1">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-semibold text-white text-sm leading-tight">{item.name}</h3>
          <span className="text-lg flex-shrink-0">{emoji}</span>
        </div>

        <p className="text-white/60 text-xs leading-relaxed line-clamp-2">{item.description}</p>

        {item.price_range && (
          <span className="text-purple-300 text-xs bg-purple-500/20 px-2 py-0.5 rounded-full self-start">
            {item.price_range}
          </span>
        )}

        {item.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-auto pt-1">
            {item.tags.slice(0, 3).map(tag => (
              <span key={tag} className="text-white/40 text-xs bg-white/5 px-2 py-0.5 rounded">
                #{tag}
              </span>
            ))}
          </div>
        )}

        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-2 text-center text-xs font-medium text-purple-300 border border-purple-400/30 rounded-lg py-1.5 hover:bg-purple-500/20 hover:text-white transition-all"
        >
          Vizito {catLabel} →
        </a>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// BROWSE TAB
// ─────────────────────────────────────────────────────────────

function BrowseTab() {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [items, setItems] = useState<ShopItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  // Load catalogue on mount
  useEffect(() => {
    loadCatalogue('');
  }, []);

  const loadCatalogue = useCallback(async (cat: string) => {
    setLoading(true);
    setSearched(false);
    try {
      const url = `/api/shopping-therapy?path=catalogue${cat ? `&category=${cat}` : ''}`;
      const res = await fetch(url);
      const data = await res.json();
      setItems(data.items || []);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleCategoryClick = (slug: string) => {
    setCategory(slug);
    if (!query.trim()) {
      loadCatalogue(slug);
    } else {
      handleSearch(slug);
    }
  };

  const handleSearch = useCallback(async (catOverride?: string) => {
    const cat = catOverride !== undefined ? catOverride : category;
    if (!query.trim() && !cat) {
      loadCatalogue('');
      return;
    }
    abortRef.current?.abort();
    abortRef.current = new AbortController();
    setLoading(true);
    setSearched(true);

    const streamItems: ShopItem[] = [];
    setItems([]);

    try {
      const res = await fetch('/api/shopping-therapy?path=stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query.trim(), category: cat || null }),
        signal: abortRef.current.signal,
      });

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let buf = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buf += decoder.decode(value, { stream: true });
          const lines = buf.split('\n');
          buf = lines.pop() ?? '';
          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            const payload = line.slice(6).trim();
            if (payload === '[DONE]') continue;
            try {
              const ev = JSON.parse(payload) as { event: string; item?: ShopItem };
              if (ev.event === 'item' && ev.item) {
                streamItems.push(ev.item);
                setItems([...streamItems]);
              }
            } catch { /* ignore */ }
          }
        }
      }
    } catch (e: unknown) {
      if ((e as Error).name !== 'AbortError') setItems([]);
    } finally {
      setLoading(false);
    }
  }, [query, category, loadCatalogue]);

  return (
    <div className="flex flex-col gap-4">
      {/* Category pills */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map(cat => (
          <button
            key={cat.slug}
            onClick={() => handleCategoryClick(cat.slug)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
              category === cat.slug
                ? 'bg-purple-500 text-white shadow-lg shadow-purple-500/30'
                : 'bg-white/5 text-white/60 hover:bg-white/10 hover:text-white'
            }`}
          >
            {cat.emoji} {cat.label}
          </button>
        ))}
      </div>

      {/* Search bar */}
      <div className="flex gap-2">
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
          placeholder="Kërko shërbime shopping... (p.sh. veshje luksoze, libra të lirë)"
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/30 focus:outline-none focus:border-purple-400/60 focus:bg-white/8 transition-all"
        />
        <button
          onClick={() => handleSearch()}
          disabled={loading}
          className="px-5 py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white text-sm font-medium rounded-xl transition-colors flex items-center gap-2"
        >
          {loading ? <span className="animate-spin">⟳</span> : '🔍'}
          Kërko
        </button>
      </div>

      {/* Results */}
      {loading && items.length === 0 && (
        <div className="flex items-center gap-3 text-white/50 text-sm py-4">
          <span className="animate-spin text-lg">⟳</span> Duke ngarkuar shërbimet...
        </div>
      )}

      {!loading && searched && items.length === 0 && (
        <div className="text-center py-12 text-white/30">
          <div className="text-4xl mb-3">🛍️</div>
          <p>Nuk u gjet asnjë shërbim për këtë kërkim.</p>
        </div>
      )}

      {items.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {items.map(item => <ShopCard key={item.id} item={item} />)}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// OCEAN CHAT TAB
// ─────────────────────────────────────────────────────────────

function OceanChatTab() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<OceanMessage[]>([
    {
      id: 'welcome',
      role: 'ai',
      content: '🌊 Përshëndetje! Jam Ocean Curiosity, i lidhur me katalogun e Shopping Therapy.\n\nPyetmë çfarë të duash: "Çfarë të blej si dhuratë për dikë që dashuron yoga?" ose "Më rekomando produkte bukurie organike".',
    },
  ]);
  const [streaming, setStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || streaming) return;

    const userMsg: OceanMessage = { id: `u-${Date.now()}`, role: 'user', content: text };
    const aiId = `ai-${Date.now()}`;
    const aiMsg: OceanMessage = { id: aiId, role: 'ai', content: '', isStreaming: true };

    setMessages(prev => [...prev, userMsg, aiMsg]);
    setInput('');
    setStreaming(true);

    abortRef.current?.abort();
    abortRef.current = new AbortController();

    try {
      const conversationHistory = messages
        .filter(m => m.role !== 'ai' || m.id !== 'welcome')
        .map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content }));

      const res = await fetch('/api/shopping-therapy?path=ocean-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text, messages: conversationHistory }),
        signal: abortRef.current.signal,
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let fullContent = '';
      let buf = '';

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buf += decoder.decode(value, { stream: true });
          const accumulated = parseSseChunk(buf);
          if (accumulated) {
            fullContent += accumulated;
            buf = '';
            setMessages(prev =>
              prev.map(m => m.id === aiId ? { ...m, content: fullContent } : m),
            );
          }
        }
      }

      setMessages(prev =>
        prev.map(m => m.id === aiId ? { ...m, content: fullContent || '…', isStreaming: false } : m),
      );
    } catch (e: unknown) {
      if ((e as Error).name !== 'AbortError') {
        setMessages(prev =>
          prev.map(m =>
            m.id === aiId
              ? { ...m, content: '⚠️ Ocean nuk u përgjigj. Provo sërish.', isStreaming: false }
              : m,
          ),
        );
      }
    } finally {
      setStreaming(false);
    }
  }, [input, streaming, messages]);

  return (
    <div className="flex flex-col h-[calc(100vh-320px)] min-h-[400px]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-4 pr-1 pb-4 scrollbar-thin scrollbar-track-transparent scrollbar-thumb-white/10">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-base ${
              msg.role === 'user'
                ? 'bg-purple-600'
                : 'bg-gradient-to-br from-blue-600 to-cyan-600'
            }`}>
              {msg.role === 'user' ? '👤' : '🌊'}
            </div>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
                msg.role === 'user'
                  ? 'bg-purple-600/30 text-white rounded-tr-sm'
                  : 'bg-white/5 text-white/90 rounded-tl-sm border border-white/8'
              }`}
            >
              {msg.content}
              {msg.isStreaming && (
                <span className="inline-block w-1 h-4 bg-cyan-400 ml-1 animate-pulse rounded" />
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested prompts */}
      {messages.length <= 1 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {[
            '🎁 Dhuratë për dikë që dashuron leximin',
            '💄 Produkte bukurie organike',
            '🏋️ Pajisje sportive me buxhet të ulët',
            '🏠 Aksesore moderne shtëpie',
          ].map(prompt => (
            <button
              key={prompt}
              onClick={() => { setInput(prompt); }}
              className="text-xs text-white/50 bg-white/5 hover:bg-white/10 hover:text-white/80 px-3 py-1.5 rounded-full transition-all"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="flex gap-2 mt-auto">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
          placeholder="Pyet Ocean Curiosity për shopping therapy..."
          disabled={streaming}
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/30 focus:outline-none focus:border-cyan-400/50 disabled:opacity-50 transition-all"
        />
        <button
          onClick={sendMessage}
          disabled={streaming || !input.trim()}
          className="px-4 py-2.5 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 disabled:opacity-40 text-white text-sm font-medium rounded-xl transition-all flex items-center gap-2 flex-shrink-0"
        >
          {streaming ? <span className="animate-spin">⟳</span> : '🌊'}
          {streaming ? 'Duke u menduar...' : 'Dërgo'}
        </button>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// LINK READER TAB
// ─────────────────────────────────────────────────────────────

function LinkReaderTab() {
  const [url, setUrl] = useState('');
  const [preview, setPreview] = useState<LinkPreview | null>(null);
  const [loading, setLoading] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [registered, setRegistered] = useState(false);
  const [regName, setRegName] = useState('');
  const [regCategory, setRegCategory] = useState('other');

  const readUrl = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setPreview(null);
    setRegistered(false);
    try {
      const res = await fetch('/api/shopping-therapy?path=read', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: url.trim() }),
      });
      const data = await res.json() as LinkPreview;
      setPreview(data);
      setRegName(data.title || '');
    } catch {
      setPreview({ url: url.trim(), title: '', description: '', image_url: '', price_hints: [], snippet: '', error: 'Nuk mund të lexohet URL-ja.' });
    } finally {
      setLoading(false);
    }
  };

  const registerLink = async () => {
    if (!preview || preview.error) return;
    setRegistering(true);
    try {
      await fetch('/api/shopping-therapy?path=register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: preview.url,
          name: regName || preview.title,
          category: regCategory,
          description: preview.description,
        }),
      });
      setRegistered(true);
    } catch { /* ignore */ }
    finally { setRegistering(false); }
  };

  return (
    <div className="flex flex-col gap-5">
      <p className="text-white/50 text-sm">
        Ngjit URL-në e çdo shërbimi shopping — sistemi lexon faqen dhe e shton në katalog.
      </p>

      {/* URL input */}
      <div className="flex gap-2">
        <input
          type="url"
          value={url}
          onChange={e => setUrl(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && readUrl()}
          placeholder="https://www.shembull.com"
          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/30 focus:outline-none focus:border-pink-400/50 transition-all"
        />
        <button
          onClick={readUrl}
          disabled={loading || !url.trim()}
          className="px-5 py-2.5 bg-pink-600 hover:bg-pink-500 disabled:opacity-40 text-white text-sm font-medium rounded-xl transition-colors flex items-center gap-2"
        >
          {loading ? <span className="animate-spin">⟳</span> : '🔗'}
          Lexo
        </button>
      </div>

      {/* Preview */}
      {preview && !preview.error && (
        <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
          <div className="flex gap-4 p-4">
            {preview.image_url && (
              <img
                src={preview.image_url}
                alt=""
                className="w-24 h-24 object-cover rounded-xl flex-shrink-0"
                onError={(e) => { (e.currentTarget as HTMLImageElement).style.display = 'none'; }}
              />
            )}
            <div className="flex flex-col gap-1 min-w-0">
              <h3 className="font-semibold text-white text-base">{preview.title}</h3>
              <p className="text-white/60 text-sm line-clamp-3">{preview.description}</p>
              {preview.price_hints.length > 0 && (
                <div className="flex gap-1 flex-wrap mt-1">
                  {preview.price_hints.map((p, i) => (
                    <span key={i} className="text-xs bg-green-500/20 text-green-300 px-2 py-0.5 rounded">
                      {p}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Register form */}
          {!registered ? (
            <div className="border-t border-white/8 p-4 flex flex-col gap-3">
              <p className="text-white/50 text-xs">Shto në katalog:</p>
              <div className="flex gap-2">
                <input
                  value={regName}
                  onChange={e => setRegName(e.target.value)}
                  placeholder="Emri i shërbimit"
                  className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder-white/30 focus:outline-none"
                />
                <select
                  value={regCategory}
                  onChange={e => setRegCategory(e.target.value)}
                  className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none"
                >
                  {CATEGORIES.filter(c => c.slug).map(c => (
                    <option key={c.slug} value={c.slug} className="bg-gray-900">
                      {c.emoji} {c.label}
                    </option>
                  ))}
                </select>
              </div>
              <button
                onClick={registerLink}
                disabled={registering}
                className="self-start px-4 py-1.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-40 text-white text-xs font-medium rounded-lg transition-colors"
              >
                {registering ? 'Duke shtuar...' : '+ Shto në katalog'}
              </button>
            </div>
          ) : (
            <div className="border-t border-white/8 p-4">
              <p className="text-green-400 text-sm">✓ Shërbimi u shtua me sukses në katalog!</p>
            </div>
          )}
        </div>
      )}

      {preview?.error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-red-300 text-sm">
          ⚠️ {preview.error}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────
// MAIN PAGE
// ─────────────────────────────────────────────────────────────

type Tab = 'browse' | 'ocean' | 'link';

export default function ShoppingTherapyPage() {
  const [tab, setTab] = useState<Tab>('browse');

  const tabs: { id: Tab; label: string; icon: string; desc: string }[] = [
    { id: 'browse', label: 'Shfleto',    icon: '🛍️', desc: 'Kërko & filtro shërbimet' },
    { id: 'ocean',  label: 'Pyet Ocean', icon: '🌊', desc: 'AI rekomandime shopping' },
    { id: 'link',   label: 'Lexo Link',  icon: '🔗', desc: 'Shto shërbim të ri' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-950 via-purple-950/20 to-gray-950 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-4xl">🛍️</span>
            <div>
              <h1 className="text-2xl font-bold text-white">Shopping Therapy</h1>
              <p className="text-white/40 text-sm">
                Zbulo shërbime shopping · Pyet Ocean Curiosity · Shto lidhje të reja
              </p>
            </div>
          </div>

          {/* Ocean connection badge */}
          <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600/20 to-cyan-600/20 border border-cyan-500/30 rounded-full px-4 py-1.5 mt-2">
            <span className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
            <span className="text-cyan-300 text-xs font-medium">I lidhur me Ocean Curiosity</span>
            <span className="text-white/30 text-xs">· Rekomandime AI në kohë reale</span>
          </div>
        </div>

        {/* Tab navigation */}
        <div className="flex gap-1 bg-white/5 rounded-2xl p-1 mb-6 w-fit">
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-medium transition-all ${
                tab === t.id
                  ? 'bg-white/10 text-white shadow'
                  : 'text-white/40 hover:text-white/70'
              }`}
            >
              <span>{t.icon}</span>
              <span className="hidden sm:inline">{t.label}</span>
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div>
          {tab === 'browse' && <BrowseTab />}
          {tab === 'ocean'  && <OceanChatTab />}
          {tab === 'link'   && <LinkReaderTab />}
        </div>
      </div>
    </div>
  );
}
