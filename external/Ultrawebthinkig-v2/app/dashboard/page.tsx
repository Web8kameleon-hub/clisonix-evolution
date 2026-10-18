'use client';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-cyan-400 mb-4">📊 Dashboard</h1>
        <p className="text-xl text-gray-300">Analytics Dashboard Coming Soon</p>
        <div className="mt-6">
          <a 
            href="/ultra-saas" 
            className="px-6 py-3 bg-cyan-600 hover:bg-cyan-700 rounded-lg transition-colors"
          >
            ← Back to Ultra SaaS
          </a>
        </div>
      </div>
    </div>
  );
}