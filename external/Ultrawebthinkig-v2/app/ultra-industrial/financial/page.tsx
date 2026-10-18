'use client';

export default function FinancialPage() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-green-400 mb-4">💰 Financial Markets</h1>
        <p className="text-xl text-gray-300">Real-time Stock Market Data</p>
        <p className="text-lg text-gray-400 mt-2">Advanced Financial Analytics Coming Soon</p>
        <div className="mt-6">
          <a 
            href="/ultra-industrial" 
            className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg transition-colors"
          >
            ← Back to Ultra Industrial
          </a>
        </div>
      </div>
    </div>
  );
}