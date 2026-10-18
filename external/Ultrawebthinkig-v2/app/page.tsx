"use client";

export default function HomePage() {
  // Auto-redirect to Ultra SaaS Platform
  if (typeof window !== 'undefined') {
    window.location.href = '/ultra-saas';
  }
  
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 flex items-center justify-center">
      <div className="text-center text-white">
        <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-white mx-auto mb-4"></div>
        <h2 className="text-2xl font-bold mb-2">🏭 Loading Ultra SaaS Platform...</h2>
        <p className="text-slate-300">Redirecting to main platform...</p>
        <div className="mt-4">
          <a 
            href="/ultra-saas" 
            className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Go to Ultra SaaS Platform →
          </a>
        </div>
      </div>
    </main>
  );
}
