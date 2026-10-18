// EuroWeb Ultra - Security & Penetration Testing Dashboard
// Monitorim i sigurisë dhe testim penetrimi

'use client';

import { AnimatePresence, motion } from 'framer-motion';
import { useCallback, useEffect, useState } from 'react';

interface SecurityThreat {
  id: string;
  type: 'ddos' | 'injection' | 'brute_force' | 'malware' | 'phishing' | 'intrusion';
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  timestamp: Date;
  status: 'active' | 'blocked' | 'resolved';
  description: string;
}

interface BiometricData {
  userId: string;
  userName: string;
  authMethod: 'facial' | 'fingerprint' | 'voice' | 'iris';
  confidence: number;
  timestamp: Date;
  location: string;
  device: string;
}

interface SecurityMetrics {
  threatsBlocked: number;
  ddosAttempts: number;
  sqlInjections: number;
  bruteForceAttempts: number;
  biometricAuths: number;
  systemIntegrity: number;
  encryptionStatus: boolean;
  firewallStatus: boolean;
}

const threatIcons = {
  ddos: '🌊',
  injection: '💉',
  brute_force: '🔨',
  malware: '🦠',
  phishing: '🎣',
  intrusion: '🔓'
};

const severityColors = {
  low: 'bg-green-100 text-green-800 border-green-300',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  high: 'bg-orange-100 text-orange-800 border-orange-300',
  critical: 'bg-red-100 text-red-800 border-red-300'
};

export default function SecurityDashboard() {
  const [threats, setThreats] = useState<SecurityThreat[]>([]);
  const [biometricLogs, setBiometricLogs] = useState<BiometricData[]>([]);
  const [metrics, setMetrics] = useState<SecurityMetrics>({
    threatsBlocked: 1247,
    ddosAttempts: 45,
    sqlInjections: 12,
    bruteForceAttempts: 89,
    biometricAuths: 156,
    systemIntegrity: 98.5,
    encryptionStatus: true,
    firewallStatus: true
  });

  const [isScanning, setIsScanning] = useState(false);
  const [scanResults, setScanResults] = useState<string[]>([]);
  const [selectedThreat, setSelectedThreat] = useState<SecurityThreat | null>(null);

  // Simulon kërcënimet e reja të sigurisë
  const generateThreat = useCallback((): SecurityThreat => {
    const types: SecurityThreat['type'][] = ['ddos', 'injection', 'brute_force', 'malware', 'phishing', 'intrusion'];
    const severities: SecurityThreat['severity'][] = ['low', 'medium', 'high', 'critical'];
    const sources = ['192.168.1.100', '10.0.0.50', '203.45.67.89', '172.16.0.25', '8.8.8.8'];
    
    const type = types[Math.floor(Math.random() * types.length)] as SecurityThreat['type'];
    const severity = severities[Math.floor(Math.random() * severities.length)] as SecurityThreat['severity'];
    
    const descriptions: Record<SecurityThreat['type'], string> = {
      ddos: 'DDoS attack detected from multiple sources',
      injection: 'SQL injection attempt on database endpoint',
      brute_force: 'Multiple failed login attempts detected',
      malware: 'Malicious file upload attempted',
      phishing: 'Phishing email campaign detected',
      intrusion: 'Unauthorized access attempt'
    };

    return {
      id: `threat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type,
      severity,
      source: sources[Math.floor(Math.random() * sources.length)] as string,
      timestamp: new Date(),
      status: Math.random() > 0.7 ? 'active' : 'blocked',
      description: descriptions[type]
    };
  }, []);

  // Simulon të dhënat biometrike
  const generateBiometricAuth = useCallback((): BiometricData => {
    const methods: BiometricData['authMethod'][] = ['facial', 'fingerprint', 'voice', 'iris'];
    const users = ['Dr. Silva', 'Admin User', 'AGI Operator', 'Security Analyst'];
    const locations = ['Tiranë Office', 'Remote', 'Prishtinë Branch', 'Mobile'];
    const devices = ['Desktop', 'Mobile', 'Tablet', 'Workstation'];

    return {
      userId: `user-${Math.floor(Math.random() * 1000)}`,
      userName: users[Math.floor(Math.random() * users.length)] as string,
      authMethod: methods[Math.floor(Math.random() * methods.length)] as BiometricData['authMethod'],
      confidence: Math.random() * 20 + 80, // 80-100%
      timestamp: new Date(),
      location: locations[Math.floor(Math.random() * locations.length)] as string,
      device: devices[Math.floor(Math.random() * devices.length)] as string
    };
  }, []);

  // Penetration testing simulation
  const runPenetrationTest = useCallback(async () => {
    setIsScanning(true);
    setScanResults([]);

    const tests = [
      'Scanning network ports...',
      'Testing SQL injection vulnerabilities...',
      'Checking for XSS vulnerabilities...',
      'Testing authentication mechanisms...',
      'Analyzing encryption protocols...',
      'Checking firewall configurations...',
      'Testing DDoS protection...',
      'Scanning for malware signatures...',
      'Verifying biometric security...',
      'Testing API security...'
    ];

    for (let i = 0; i < tests.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 800));
      const testResult = tests[i];
      if (testResult) {
        setScanResults(prev => [...prev, testResult]);
      }
    }

    // Final results
    await new Promise(resolve => setTimeout(resolve, 1000));
    setScanResults(prev => [
      ...prev,
      '',
      '✅ Penetration test completed',
      '📊 Vulnerabilities found: 2 (Low priority)',
      '🔒 Security score: 94/100',
      '🛡️ System integrity: GOOD'
    ]);

    setIsScanning(false);
  }, []);

  // Auto-generate threats dhe biometric data
  useEffect(() => {
    const threatInterval = setInterval(() => {
      if (Math.random() > 0.7) {
        setThreats(prev => [generateThreat(), ...prev.slice(0, 19)]);
      }
    }, 5000);

    const biometricInterval = setInterval(() => {
      if (Math.random() > 0.6) {
        setBiometricLogs(prev => [generateBiometricAuth(), ...prev.slice(0, 9)]);
      }
    }, 3000);

    const metricsInterval = setInterval(() => {
      setMetrics(prev => ({
        ...prev,
        threatsBlocked: prev.threatsBlocked + Math.floor(Math.random() * 3),
        systemIntegrity: Math.max(95, Math.min(100, prev.systemIntegrity + (Math.random() - 0.5) * 2))
      }));
    }, 10000);

    return () => {
      clearInterval(threatInterval);
      clearInterval(biometricInterval);
      clearInterval(metricsInterval);
    };
  }, [generateThreat, generateBiometricAuth]);

  const resolveThreat = (threatId: string) => {
    setThreats(prev => prev.map(threat =>
      threat.id === threatId ? { ...threat, status: 'resolved' } : threat
    ));
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-red-600 to-orange-600 text-white rounded-xl p-6"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">🛡️ Security & Penetration Testing</h1>
            <p className="text-red-100">
              Monitorim në kohë reale i sigurisë dhe testim penetrimi automatik
            </p>
          </div>
          <button
            onClick={runPenetrationTest}
            disabled={isScanning}
            className="bg-white text-red-600 px-6 py-3 rounded-lg hover:bg-gray-100 disabled:opacity-50 font-medium flex items-center gap-2"
          >
            {isScanning ? (
              <>
                <div className="w-4 h-4 border-2 border-red-600 border-t-transparent rounded-full animate-spin" />
                Scanning...
              </>
            ) : (
              <>
                🔍 Run Pen Test
              </>
            )}
          </button>
        </div>
      </motion.div>

      {/* Security Metrics */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-lg shadow-lg p-6"
      >
        <h2 className="text-xl font-semibold mb-6">📊 Security Metrics</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">{metrics.threatsBlocked}</div>
            <div className="text-sm text-gray-600">Threats Blocked</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{metrics.ddosAttempts}</div>
            <div className="text-sm text-gray-600">DDoS Attempts</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-purple-600">{metrics.sqlInjections}</div>
            <div className="text-sm text-gray-600">SQL Injections</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-orange-600">{metrics.bruteForceAttempts}</div>
            <div className="text-sm text-gray-600">Brute Force</div>
          </div>
          <div className="bg-cyan-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-cyan-600">{metrics.biometricAuths}</div>
            <div className="text-sm text-gray-600">Biometric Auths</div>
          </div>
          <div className="bg-indigo-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-indigo-600">{metrics.systemIntegrity.toFixed(1)}%</div>
            <div className="text-sm text-gray-600">System Integrity</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className={`text-2xl ${metrics.encryptionStatus ? 'text-green-600' : 'text-red-600'}`}>
              {metrics.encryptionStatus ? '🔒' : '🔓'}
            </div>
            <div className="text-sm text-gray-600">Encryption</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className={`text-2xl ${metrics.firewallStatus ? 'text-green-600' : 'text-red-600'}`}>
              {metrics.firewallStatus ? '🛡️' : '⚠️'}
            </div>
            <div className="text-sm text-gray-600">Firewall</div>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Detection */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <h2 className="text-xl font-semibold mb-4">🚨 Live Threat Detection</h2>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {threats.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <div className="text-4xl mb-2">✅</div>
                <p>No active threats detected</p>
              </div>
            ) : (
              threats.map((threat) => (
                <motion.div
                  key={threat.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`border rounded-lg p-3 ${severityColors[threat.severity]} cursor-pointer hover:shadow-md transition-all`}
                  onClick={() => setSelectedThreat(threat)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{threatIcons[threat.type]}</span>
                      <div>
                        <div className="font-medium capitalize">{threat.type.replace('_', ' ')}</div>
                        <div className="text-sm opacity-75">{threat.source}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        threat.status === 'active' ? 'bg-red-100 text-red-800' :
                        threat.status === 'blocked' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {threat.status}
                      </div>
                      <div className="text-xs opacity-75 mt-1">
                        {threat.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                  {threat.status === 'active' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        resolveThreat(threat.id);
                      }}
                      className="mt-2 bg-red-600 text-white px-3 py-1 rounded text-xs hover:bg-red-700"
                    >
                      🛡️ Block Threat
                    </button>
                  )}
                </motion.div>
              ))
            )}
          </div>
        </motion.div>

        {/* Biometric Authentication */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white rounded-lg shadow-lg p-6"
        >
          <h2 className="text-xl font-semibold mb-4">👁️ Biometric Authentication</h2>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {biometricLogs.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <div className="text-4xl mb-2">👤</div>
                <p>No biometric authentications yet</p>
              </div>
            ) : (
              biometricLogs.map((log, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="border border-gray-200 rounded-lg p-3 hover:bg-gray-50"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">
                        {log.authMethod === 'facial' && '👤'}
                        {log.authMethod === 'fingerprint' && '👆'}
                        {log.authMethod === 'voice' && '🎤'}
                        {log.authMethod === 'iris' && '👁️'}
                      </div>
                      <div>
                        <div className="font-medium">{log.userName}</div>
                        <div className="text-sm text-gray-600 capitalize">{log.authMethod} auth</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`px-2 py-1 rounded text-xs font-medium ${
                        log.confidence > 95 ? 'bg-green-100 text-green-800' :
                        log.confidence > 85 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {log.confidence.toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500 mt-1">
                        {log.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    📍 {log.location} • 📱 {log.device}
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </motion.div>
      </div>

      {/* Penetration Test Results */}
      <AnimatePresence>
        {scanResults.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-gray-900 text-green-400 rounded-lg p-6 font-mono text-sm"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-white font-semibold">🔍 Penetration Test Results</h3>
              <button
                onClick={() => setScanResults([])}
                className="text-gray-400 hover:text-white"
              >
                ×
              </button>
            </div>
            <div className="space-y-1 max-h-64 overflow-y-auto">
              {scanResults.map((result, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center gap-2"
                >
                  <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span>
                  <span>{result}</span>
                </motion.div>
              ))}
              {isScanning && (
                <motion.div
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  className="flex items-center gap-2"
                >
                  <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span>
                  <span>⌛ Running security scan...</span>
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Threat Details Modal */}
      <AnimatePresence>
        {selectedThreat && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={() => setSelectedThreat(null)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="bg-white rounded-lg p-6 w-96 mx-4"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">🚨 Threat Details</h3>
                <button
                  onClick={() => setSelectedThreat(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{threatIcons[selectedThreat.type]}</span>
                  <div>
                    <div className="font-medium capitalize">{selectedThreat.type.replace('_', ' ')}</div>
                    <div className={`text-sm px-2 py-1 rounded ${severityColors[selectedThreat.severity]}`}>
                      {selectedThreat.severity} severity
                    </div>
                  </div>
                </div>
                
                <div className="space-y-2 text-sm">
                  <div><strong>Source:</strong> {selectedThreat.source}</div>
                  <div><strong>Time:</strong> {selectedThreat.timestamp.toLocaleString()}</div>
                  <div><strong>Status:</strong> {selectedThreat.status}</div>
                  <div><strong>Description:</strong> {selectedThreat.description}</div>
                </div>
                
                {selectedThreat.status === 'active' && (
                  <button
                    onClick={() => {
                      resolveThreat(selectedThreat.id);
                      setSelectedThreat(null);
                    }}
                    className="w-full bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700"
                  >
                    🛡️ Block & Resolve Threat
                  </button>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
