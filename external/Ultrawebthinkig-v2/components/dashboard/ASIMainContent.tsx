"use client";

interface ASIMainContentProps {
  activeView?: string;
  systemStatus?: any;
}

export function ASIMainContent({ activeView, systemStatus }: ASIMainContentProps) {
  
  const handleASIDashboardClick = () => {
    // Ridrejton tek ASI Dashboard në port 3111
    window.open('http://localhost:3111', '_blank');
  };

  return (
    <div className="bg-white min-h-screen p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🏭 ULTRA SAAS PLATFORM</h1>
        <p className="text-gray-600">
          Complete AI-Powered SaaS Platform • 50+ Active Modules • Albanian System Integration
        </p>
      </div>

      {/* ASI Dashboard Tab - Vetem kaq */}
      <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm max-w-md">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className="text-2xl">🎛️</div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">ASI Dashboard</h3>
              <p className="text-sm text-gray-600">Intelligence Hub</p>
            </div>
          </div>
          <div className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
            active
          </div>
        </div>
        
        <p className="text-gray-600 text-sm mb-4">
          Albanian System Intelligence Control Panel
        </p>
        
        <button
          onClick={handleASIDashboardClick}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Launch → (Port 3111)
        </button>
      </div>

      {/* Info Footer */}
      <div className="mt-8 text-gray-500 text-sm">
        <p>🇦🇱 Albanian Integration • Complete Albanian language support and local system integration</p>
        <p className="mt-2">© 2025 Ultra SaaS Platform • Made with ❤️ in Albania</p>
      </div>

    </div>
  );
}
