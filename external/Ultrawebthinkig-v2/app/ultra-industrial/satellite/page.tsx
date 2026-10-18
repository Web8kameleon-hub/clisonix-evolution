'use client';

export default function SatellitePage() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-purple-400 mb-4">🛰️ Satellite Monitor</h1>
        <p className="text-xl text-gray-300">NASA Earth Data & Satellite Imagery</p>
        <p className="text-lg text-gray-400 mt-2">Real-time Satellite Monitoring Coming Soon</p>
        <div className="mt-6">
          <a 
            href="/ultra-industrial" 
            className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors"
          >
            ← Back to Ultra Industrial
          </a>
        </div>
      </div>
    </div>
  );
}