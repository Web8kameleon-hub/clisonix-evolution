'use client'

interface ASIHeaderProps {
  onMenuClick: () => void
  systemStatus: any
  isLoading: boolean
}

export function ASIHeader({ onMenuClick, systemStatus, isLoading }: ASIHeaderProps) {
  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3">
      <div className="flex items-center justify-between">
        
        {/* Logo */}
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold text-gray-900">ASI Dashboard</h1>
        </div>

        {/* Status */}
        <div className="text-sm text-gray-600">
          {isLoading ? 'Loading...' : 'Connected'}
        </div>
      </div>
    </header>
  )
}
