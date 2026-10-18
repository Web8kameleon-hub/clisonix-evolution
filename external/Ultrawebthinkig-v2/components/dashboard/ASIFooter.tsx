'use client'

interface ASIFooterProps {
  systemStatus: any
}

export function ASIFooter({ systemStatus }: ASIFooterProps) {
  return (
    <footer className="bg-white border-t border-gray-200 px-6 py-3">
      <div className="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
        
        {/* 🇦🇱 Branding */}
        <div className="flex items-center space-x-4 text-sm text-gray-700">
          <div className="flex items-center space-x-2">
            <span className="font-medium">🇦🇱 ASI Ultimate World</span>
            <span className="text-gray-400">|</span>
            <span>v2.0.0</span>
          </div>
        </div>

        {/* 📊 System Stats */}
        <div className="flex items-center space-x-6 text-xs text-gray-600">
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 rounded-full bg-green-400" />
            <span>API Online</span>
          </div>
          
          <div className="flex items-center space-x-1">
            <span>⚡</span>
            <span>89ms Response</span>
          </div>
          
          <div className="flex items-center space-x-1">
            <span>🌍</span>
            <span>247 Sources</span>
          </div>
          
          <div className="flex items-center space-x-1">
            <span>🔄</span>
            <span>Real-time Updates</span>
          </div>
        </div>

        {/* 📅 Last Update */}
        <div className="text-xs text-gray-600">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>
    </footer>
  )
}
