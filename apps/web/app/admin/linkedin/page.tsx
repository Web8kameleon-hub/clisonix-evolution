'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Article {
  id: string;
  title: string;
  description: string;
  slug: string;
  category: string;
  tags: string[];
  publishedAt?: string;
  author?: string;
}

export default function LinkedInAdminPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [postedArticles, setPostedArticles] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [posting, setPosting] = useState<string | null>(null);
  const [customText, setCustomText] = useState('');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load pending articles
      const pendingRes = await fetch('/api/linkedin/pending-articles');
      const pendingData = await pendingRes.json();
      setArticles(pendingData.pending || []);

      // Load posted articles
      const postedRes = await fetch('/api/linkedin/posted-articles');
      const postedData = await postedRes.json();
      setPostedArticles(postedData.posted || []);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  const postArticle = async (articleId: string) => {
    setPosting(articleId);
    setMessage(null);

    try {
      const response = await fetch('/api/linkedin/post-article', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ article_id: articleId }),
      });

      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: `Article posted successfully! Post ID: ${data.post_id}` });
        loadData(); // Refresh data
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to post article' });
      }
    } catch {
      setMessage({ type: 'error', text: 'Error posting article' });
    } finally {
      setPosting(null);
    }
  };

  const postCustom = async () => {
    if (!customText.trim()) return;

    setPosting('custom');
    setMessage(null);

    try {
      const response = await fetch('/api/linkedin/post-custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: customText }),
      });

      const data = await response.json();

      if (data.success) {
        setMessage({ type: 'success', text: `Posted successfully! Post ID: ${data.post_id}` });
        setCustomText('');
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to post' });
      }
    } catch {
      setMessage({ type: 'error', text: 'Error posting content' });
    } finally {
      setPosting(null);
    }
  };

  const triggerDailyPost = async () => {
    setPosting('daily');
    setMessage(null);

    try {
      const response = await fetch('/api/linkedin/post-daily', {
        method: 'POST',
      });

      const data = await response.json();

      if (data.success) {
        if (data.article) {
          setMessage({ type: 'success', text: `Posted: "${data.article}"` });
        } else {
          setMessage({ type: 'success', text: data.message || 'No new articles to post' });
        }
        loadData();
      } else {
        setMessage({ type: 'error', text: data.error || 'Failed to run daily post' });
      }
    } catch {
      setMessage({ type: 'error', text: 'Error running daily post' });
    } finally {
      setPosting(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Link href="/admin" className="text-gray-400 hover:text-white">← Admin</Link>
            <span className="text-gray-600">/</span>
            <h1 className="text-xl font-bold">LinkedIn Auto Poster</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">
              {postedArticles.length} posted / {articles.length + postedArticles.length} total
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Message */}
        {message && (
          <div className={`mb-6 p-4 rounded-xl ${message.type === 'success' ? 'bg-green-500/20 border border-green-500' : 'bg-red-500/20 border border-red-500'}`}>
            {message.text}
          </div>
        )}

        {/* Quick Actions */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="flex gap-4">
            <button
              onClick={triggerDailyPost}
              disabled={posting === 'daily'}
              className="px-6 py-3 bg-violet-600 hover:bg-violet-500 rounded-xl font-semibold transition-colors disabled:opacity-50"
            >
              {posting === 'daily' ? 'Posting...' : '🚀 Run Daily Post'}
            </button>
            <Link
              href="https://www.linkedin.com/feed/"
              target="_blank"
              className="px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-xl font-semibold transition-colors"
            >
              📱 View LinkedIn Feed
            </Link>
          </div>
        </section>

        {/* Custom Post */}
        <section className="mb-8 p-6 rounded-2xl bg-slate-800/50 border border-slate-700">
          <h2 className="text-lg font-semibold mb-4">📝 Custom Post</h2>
          <textarea
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
            placeholder="Write a custom LinkedIn post..."
            className="w-full h-32 p-4 rounded-xl bg-slate-900 border border-slate-700 focus:border-violet-500 focus:outline-none resize-none"
          />
          <div className="flex justify-between items-center mt-4">
            <span className="text-sm text-gray-400">{customText.length} / 3000 characters</span>
            <button
              onClick={postCustom}
              disabled={!customText.trim() || posting === 'custom'}
              className="px-6 py-2 bg-violet-600 hover:bg-violet-500 rounded-lg font-semibold transition-colors disabled:opacity-50"
            >
              {posting === 'custom' ? 'Posting...' : 'Post to LinkedIn'}
            </button>
          </div>
        </section>

        {/* Pending Articles */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold mb-4">📋 Pending Articles ({articles.length})</h2>
          {articles.length === 0 ? (
            <div className="p-6 rounded-xl bg-slate-800/50 border border-slate-700 text-center text-gray-400">
              All articles have been posted! 🎉
            </div>
          ) : (
            <div className="space-y-4">
              {articles.map((article) => (
                <div
                  key={article.id}
                  className="p-4 rounded-xl bg-slate-800/50 border border-slate-700 flex justify-between items-center"
                >
                  <div className="flex-1">
                    <h3 className="font-semibold">{article.title}</h3>
                    <p className="text-sm text-gray-400 mt-1">{article.description?.slice(0, 100)}...</p>
                    <div className="flex gap-2 mt-2">
                      <span className="px-2 py-1 text-xs rounded-full bg-violet-500/20 text-violet-300">
                        {article.category}
                      </span>
                      {article.tags?.slice(0, 3).map((tag) => (
                        <span key={tag} className="px-2 py-1 text-xs rounded-full bg-slate-700 text-gray-400">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button
                    onClick={() => postArticle(article.id)}
                    disabled={posting === article.id}
                    className="ml-4 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg font-semibold transition-colors disabled:opacity-50"
                  >
                    {posting === article.id ? 'Posting...' : '📤 Post'}
                  </button>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Posted History */}
        <section>
          <h2 className="text-lg font-semibold mb-4">✅ Posted Articles ({postedArticles.length})</h2>
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700">
            {postedArticles.length === 0 ? (
              <p className="text-gray-400">No articles posted yet</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {postedArticles.map((id) => (
                  <span key={id} className="px-3 py-1 text-sm rounded-full bg-green-500/20 text-green-300">
                    {id}
                  </span>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
