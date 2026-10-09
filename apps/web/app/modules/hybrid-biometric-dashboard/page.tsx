'use client';

import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

/**
 * HYBRID BIOMETRIC DASHBOARD
 * Shfaq të dhëna nga telefon + klinika në të njëjtën vend
 */

interface PhoneMetrics {
  timestamp: number;
  heartRate?: number;
  temperature?: number;
  accelerationX?: number;
  accelerationY?: number;
  accelerationZ?: number;
}

interface ClinicalMetric {
  deviceId: string;
  deviceName: string;
  deviceType: string;
  value: number;
  unit: string;
  quality: number;
  timestamp: number;
}

export default function HybridBiometricDashboard() {
  // Default values - can be set via URL params or context
  const sessionId = undefined;
  const userId = undefined;
  const clinicId = undefined;
  
  const [phoneMetrics, setPhoneMetrics] = useState<PhoneMetrics[]>([]);
  const [clinicalMetrics, setClinicalMetrics] = useState<ClinicalMetric[]>([]);
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [currentPhoneData, setCurrentPhoneData] = useState<PhoneMetrics | null>(null);
  const [syncStatus, setSyncStatus] = useState('disconnected');
  const [dataSource, setDataSource] = useState<'phone' | 'clinic' | 'hybrid'>('hybrid');

  // Start session
  const handleStartSession = async () => {
    try {
      const res = await fetch('/api/session/start-hybrid', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: userId || 'demo_user',
          clinic_id: clinicId || null,
          data_source: dataSource,
        }),
      });

      if (res.ok) {
        await res.json();
        setIsSessionActive(true);
        setSyncStatus('connected');
      }
    } catch (error) {
      console.error('Failed to start session:', error);
    }
  };

  // Stop session
  const handleStopSession = async () => {
    if (!sessionId) return;

    try {
      const res = await fetch(`/api/session/${sessionId}/stop`, {
        method: 'POST',
      });

      if (res.ok) {
        setIsSessionActive(false);
        setSyncStatus('disconnected');
      }
    } catch (error) {
      console.error('Failed to stop session:', error);
    }
  };

  // Simulate phone sensors
  useEffect(() => {
    if (!isSessionActive) return;

    const interval = setInterval(() => {
      const newMetric: PhoneMetrics = {
        timestamp: Date.now(),
        heartRate: 60 + Math.random() * 40,
        temperature: 36.5 + (Math.random() - 0.5) * 2,
        accelerationX: Math.random() * 20 - 10,
        accelerationY: Math.random() * 20 - 10,
        accelerationZ: Math.random() * 20 - 10,
      };

      setPhoneMetrics(prev => [...prev, newMetric].slice(-100));
      setCurrentPhoneData(newMetric);

      // Send to API
      fetch('/api/phone/sensor-reading', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          accelerometer: {
            x: newMetric.accelerationX,
            y: newMetric.accelerationY,
            z: newMetric.accelerationZ,
            timestamp: newMetric.timestamp,
          },
          heart_rate: {
            bpm: newMetric.heartRate,
            confidence: 0.8,
            timestamp: newMetric.timestamp,
          },
          temperature: {
            celsius: newMetric.temperature,
            timestamp: newMetric.timestamp,
          },
          session_id: sessionId || 'demo_session',
          user_id: userId || 'demo_user',
        }),
      }).catch(console.error);
    }, 1000);

    return () => clearInterval(interval);
  }, [isSessionActive, sessionId, userId]);

  // Fetch clinical data
  useEffect(() => {
    if (!clinicId || !isSessionActive) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`/api/clinic/${clinicId}/readings`);
        if (res.ok) {
          const data = await res.json();
          setClinicalMetrics(data.readings);
          setSyncStatus('synced');
        }
      } catch (error) {
        console.error('Failed to fetch clinical data:', error);
        setSyncStatus('sync_error');
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [clinicId, isSessionActive]);

  // Prepare chart data
  const chartData = phoneMetrics.map(m => ({
    time: new Date(m.timestamp).toLocaleTimeString(),
    heartRate: Math.round(m.heartRate || 0),
    temperature: parseFloat((m.temperature || 0).toFixed(1)),
    accelX: parseFloat((m.accelerationX || 0).toFixed(1)),
  }));

  return (
    <div className="w-full max-w-7xl mx-auto p-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg shadow-xl">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-4xl font-bold text-white mb-2">🔗 Hybrid Biometric Monitor</h1>
        <p className="text-gray-300">Telefon + Klinika në kohë reale</p>
      </div>

      {/* Session Controls */}
      <div className="mb-6 p-4 bg-slate-800 rounded-lg border border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className={`w-3 h-3 rounded-full ${isSessionActive ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
            <span className="text-white font-semibold">
              {isSessionActive ? 'SESSION ACTIVE' : 'SESSION INACTIVE'}
            </span>
            <span className={`px-3 py-1 rounded text-sm font-medium ${
              syncStatus === 'synced' ? 'bg-green-600 text-white' :
              syncStatus === 'connected' ? 'bg-violet-600 text-white' :
              'bg-gray-600 text-white'
            }`}>
              {syncStatus.toUpperCase()}
            </span>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleStartSession}
              disabled={isSessionActive}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded font-semibold disabled:opacity-50"
            >
              ▶ Start Session
            </button>
            <button
              onClick={handleStopSession}
              disabled={!isSessionActive}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded font-semibold disabled:opacity-50"
            >
              ⏹ Stop Session
            </button>
          </div>
        </div>

        {/* Data Source Selection */}
        <div className="flex gap-4">
          <label className="flex items-center gap-2 text-white cursor-pointer">
            <input
              type="radio"
              value="phone"
              checked={dataSource === 'phone'}
              onChange={() => setDataSource('phone')}
              disabled={isSessionActive}
            />
            📱 Phone Only
          </label>
          <label className="flex items-center gap-2 text-white cursor-pointer">
            <input
              type="radio"
              value="clinic"
              checked={dataSource === 'clinic'}
              onChange={() => setDataSource('clinic')}
              disabled={isSessionActive}
            />
            🏥 Clinic Only
          </label>
          <label className="flex items-center gap-2 text-white cursor-pointer">
            <input
              type="radio"
              value="hybrid"
              checked={dataSource === 'hybrid'}
              onChange={() => setDataSource('hybrid')}
              disabled={isSessionActive}
            />
            🔗 Hybrid (Both)
          </label>
        </div>
      </div>

      {/* Real-time metrics */}
      {currentPhoneData && (
        <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Heart Rate */}
          <div className="p-4 bg-red-900 bg-opacity-50 border border-red-700 rounded-lg">
            <div className="text-red-200 text-sm font-semibold mb-1">❤️ Heart Rate</div>
            <div className="text-3xl font-bold text-red-100">
              {Math.round(currentPhoneData.heartRate || 0)} <span className="text-lg">BPM</span>
            </div>
            <div className="text-red-300 text-xs mt-1">Normal: 60-100 BPM</div>
          </div>

          {/* Temperature */}
          <div className="p-4 bg-orange-900 bg-opacity-50 border border-orange-700 rounded-lg">
            <div className="text-orange-200 text-sm font-semibold mb-1">🌡️ Temperature</div>
            <div className="text-3xl font-bold text-orange-100">
              {(currentPhoneData.temperature || 0).toFixed(1)} <span className="text-lg">°C</span>
            </div>
            <div className="text-orange-300 text-xs mt-1">Normal: 36.5-37.5°C</div>
          </div>

          {/* Acceleration */}
          <div className="p-4 bg-slate-900 bg-opacity-50 border border-violet-700 rounded-lg">
            <div className="text-violet-200 text-sm font-semibold mb-1">📊 Movement</div>
            <div className="text-3xl font-bold text-violet-100">
              {Math.sqrt(
                (currentPhoneData.accelerationX || 0) ** 2 +
                (currentPhoneData.accelerationY || 0) ** 2 +
                (currentPhoneData.accelerationZ || 0) ** 2
              ).toFixed(1)} <span className="text-lg">m/s²</span>
            </div>
            <div className="text-violet-300 text-xs mt-1">Active Motion</div>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Heart Rate Chart */}
        <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
          <h3 className="text-white font-semibold mb-4">❤️ Heart Rate Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" domain={[40, 120]} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                labelStyle={{ color: '#fff' }}
              />
              <Line
                type="monotone"
                dataKey="heartRate"
                stroke="#ef4444"
                strokeWidth={2}
                dot={false}
                name="BPM"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Temperature Chart */}
        <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
          <h3 className="text-white font-semibold mb-4">🌡️ Temperature Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" domain={[35, 39]} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                labelStyle={{ color: '#fff' }}
              />
              <Line
                type="monotone"
                dataKey="temperature"
                stroke="#f97316"
                strokeWidth={2}
                dot={false}
                name="°C"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Clinical Data */}
      {clinicalMetrics.length > 0 && (
        <div className="p-4 bg-slate-800 rounded-lg border border-slate-700">
          <h3 className="text-white font-semibold mb-4">🏥 Clinical Device Data</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {clinicalMetrics.map((metric, idx) => (
              <div key={idx} className="p-3 bg-slate-700 rounded border border-slate-600">
                <div className="text-gray-300 text-xs font-semibold mb-1">{metric.deviceName}</div>
                <div className="text-2xl font-bold text-white mb-1">
                  {typeof metric.value === 'number' ? metric.value.toFixed(2) : metric.value} {metric.unit}
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-400">{metric.deviceType}</span>
                  <span className={`px-2 py-1 rounded ${
                    metric.quality > 80 ? 'bg-green-600' :
                    metric.quality > 60 ? 'bg-yellow-600' :
                    'bg-red-600'
                  } text-white`}>
                    {metric.quality}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Status Info */}
      <div className="mt-6 p-4 bg-slate-800 rounded-lg border border-slate-700 text-gray-300 text-sm">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-gray-500">Phone Readings</div>
            <div className="text-2xl font-bold text-white">{phoneMetrics.length}</div>
          </div>
          <div>
            <div className="text-gray-500">Clinical Readings</div>
            <div className="text-2xl font-bold text-white">{clinicalMetrics.length}</div>
          </div>
          <div>
            <div className="text-gray-500">Data Source</div>
            <div className="text-2xl font-bold text-white capitalize">{dataSource}</div>
          </div>
          <div>
            <div className="text-gray-500">Session ID</div>
            <div className="text-sm font-mono text-gray-400">{sessionId || 'Not started'}</div>
          </div>
        </div>
      </div>
    </div>
  );
}







