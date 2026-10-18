'use client';

import { useEffect, useState } from 'react';

interface SecurityAlert {
  id: string;
  type: 'high_rate' | 'large_payload' | 'suspicious_agent';
  ip: string;
  details: string;
  timestamp: number;
  blocked: boolean;
}

interface BlockedIP {
  ip: string;
  reason: string;
  timestamp: number;
}

export function GuardianPanel() {
  const [alerts, setAlerts] = useState<SecurityAlert[]>([]);
  const [blockedIPs, setBlockedIPs] = useState<BlockedIP[]>([]);
  const [command, setCommand] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [agiCoreEnabled, setAgiCoreEnabled] = useState(true);

  // Simulate real-time alerts
  useEffect(() => {
    const mockAlerts: SecurityAlert[] = [
      {
        id: '1',
        type: 'high_rate',
        ip: '192.168.1.100',
        details: 'High request rate: 105 req/min',
        timestamp: Date.now() - 5000,
        blocked: false,
      },
      {
        id: '2',
        type: 'large_payload',
        ip: '10.0.0.15',
        details: 'Payload i madh: 600000 bytes',
        timestamp: Date.now() - 3000,
        blocked: false,
      },
      {
        id: '3',
        type: 'suspicious_agent',
        ip: '203.0.113.45',
        details: 'User agent i dyshimtë: python-requests/2.28.1',
        timestamp: Date.now() - 1000,
        blocked: false,
      },
    ];
    setAlerts(mockAlerts);
  }, []);

  const executeEmergencyBlock = async (ip: string, reason: string) => {
    setIsProcessing(true);

    try {
      // Call the actual backend API
      const response = await fetch('/api/guardian/emergency-block', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ip, reason }),
      });

      if (response.ok) {
        // Update UI state
        setBlockedIPs(prev => [
          ...prev,
          {
            ip,
            reason,
            timestamp: Date.now(),
          },
        ]);

        setAlerts(prev =>
          prev.map(alert =>
            alert.ip === ip ? { ...alert, blocked: true } : alert
          )
        );

        console.log(`🚨 IP ${ip} has been blocked successfully`);
      }
    } catch (error) {
      console.error('Failed to block IP:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleAGICommand = async () => {
    if (!command.trim() || !agiCoreEnabled) {
      if (!agiCoreEnabled) {
        console.log('⚠️ AGI Core është i fikur - komanda nuk u ekzekutua');
      }
      return;
    }

    // Parse AGI command: "Guardian, blloko IP 203.0.113.45"
    const blockMatch = command.match(/blloko IP ([\d.]+)/i);

    if (blockMatch) {
      const ip = blockMatch[1];
      await executeEmergencyBlock(ip, 'AGI Command Block');
      setCommand('');
    }
  };

  const getAlertIcon = (type: SecurityAlert['type']) => {
    switch (type) {
      case 'high_rate':
        return '🚀';
      case 'large_payload':
        return '📦';
      case 'suspicious_agent':
        return '🕵️';
      default:
        return '⚠️';
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto bg-gray-900 text-white min-h-screen">
      <div className="mb-8">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              🛡️ Guardian Control Panel
            </h1>
            <p className="text-gray-400">
              Real-time Security Monitoring & Emergency Response
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-400 mb-1">System Status</div>
            <div
              className={`px-3 py-1 rounded-full text-sm font-medium ${
                agiCoreEnabled
                  ? 'bg-green-900 text-green-400 border border-green-700'
                  : 'bg-red-900 text-red-400 border border-red-700'
              }`}
            >
              {agiCoreEnabled ? '🟢 AGI Core AKTIV' : '🔴 AGI Core FIKUR'}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {agiCoreEnabled ? 'PC duke u ngarkuar' : 'PC i lehtësuar'}
            </div>
          </div>
        </div>
      </div>

      {/* AGI Command Interface */}
      <div className="mb-8 p-4 bg-blue-900 rounded-lg border border-blue-700">
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-xl font-semibold">🔐 AGI Command Center</h2>
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-300">AGI Core:</span>
            <button
              onClick={() => setAgiCoreEnabled(!agiCoreEnabled)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                agiCoreEnabled ? 'bg-green-600' : 'bg-gray-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  agiCoreEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span
              className={`text-sm font-medium ${
                agiCoreEnabled ? 'text-green-400' : 'text-red-400'
              }`}
            >
              {agiCoreEnabled ? '🟢 AKTIV' : '🔴 FIKUR'}
            </span>
          </div>
        </div>

        {!agiCoreEnabled && (
          <div className="mb-3 p-2 bg-yellow-900 border border-yellow-600 rounded text-yellow-200 text-sm">
            ⚠️ AGI Core është i fikur - komandat nuk do të ekzekutohen (PC nuk
            do të ngarkohet)
          </div>
        )}

        <div className="flex gap-3">
          <input
            type="text"
            value={command}
            onChange={e => setCommand(e.target.value)}
            placeholder="Guardian, blloko IP 203.0.113.45"
            className={`flex-1 px-4 py-2 border rounded text-white ${
              agiCoreEnabled
                ? 'bg-gray-800 border-gray-600'
                : 'bg-gray-700 border-gray-500 opacity-60'
            }`}
            onKeyPress={e => e.key === 'Enter' && handleAGICommand()}
            disabled={!agiCoreEnabled}
          />
          <button
            onClick={handleAGICommand}
            disabled={isProcessing || !agiCoreEnabled}
            className={`px-6 py-2 rounded font-medium ${
              agiCoreEnabled
                ? 'bg-red-600 hover:bg-red-700 disabled:bg-gray-600'
                : 'bg-gray-600 cursor-not-allowed'
            }`}
          >
            {isProcessing ? '⏳ Processing...' : '🚨 Execute'}
          </button>
        </div>
      </div>

      {/* Active Alerts */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold mb-4">
          ⚠️ Active Security Alerts
        </h2>
        <div className="space-y-3">
          {alerts.map(alert => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border ${
                alert.blocked
                  ? 'bg-green-900 border-green-700'
                  : 'bg-red-900 border-red-700'
              }`}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-2xl">{getAlertIcon(alert.type)}</span>
                    <span className="font-semibold">{alert.ip}</span>
                    {alert.blocked && (
                      <span className="text-green-400">✅ BLOCKED</span>
                    )}
                  </div>
                  <p className="text-gray-300">{alert.details}</p>
                  <p className="text-sm text-gray-500">
                    {new Date(alert.timestamp).toLocaleTimeString()}
                  </p>
                </div>
                {!alert.blocked && (
                  <button
                    onClick={() =>
                      executeEmergencyBlock(alert.ip, alert.details)
                    }
                    disabled={isProcessing}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 rounded text-sm font-medium"
                  >
                    🛑 Emergency Block
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Blocked IPs List */}
      <div>
        <h2 className="text-xl font-semibold mb-4">🚫 Blocked IPs</h2>
        {blockedIPs.length === 0 ? (
          <p className="text-gray-400">No IPs currently blocked</p>
        ) : (
          <div className="space-y-2">
            {blockedIPs.map((blocked, index) => (
              <div
                key={index}
                className="p-3 bg-gray-800 rounded border border-gray-600"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <span className="font-mono text-green-400">
                      {blocked.ip}
                    </span>
                    <span className="ml-3 text-gray-400">{blocked.reason}</span>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(blocked.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Auto-recommendations */}
      <div className="mt-8 p-4 bg-yellow-900 border border-yellow-700 rounded-lg">
        <h3 className="font-semibold mb-2">✅ Auto-Recommendations Active:</h3>
        <ul className="text-sm space-y-1 text-yellow-100">
          <li>• Auto-block për IP me më shumë se 100 req/min</li>
          <li>• Kufi për payload size mbi 500KB në /api/*</li>
          <li>• Block python-requests/* nga User-Agent</li>
        </ul>
      </div>
    </div>
  );
}

export default GuardianPanel;
