'use client';

import React from 'react';
import { useJOANASI } from '../lib/joan-asi-service';

interface ASIStatusProps {
  className?: string;
  minimal?: boolean;
}

export default function ASIStatus({ className = '', minimal = false }: ASIStatusProps) {
  const { frame, planetaryHealth, isConnected, jonaWisdom } = useJOANASI();

  if (minimal) {
    return (
      <div className={`flex items-center gap-2 ${className}`}>
        <div 
          className={`w-3 h-3 rounded-full ${
            isConnected ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'
          }`}
          title={isConnected ? 'JOAN ASI Online' : 'JOAN ASI Offline (Mock Mode)'}
        />
        <span className="text-sm font-medium">
          {isConnected ? 'JOAN ASI' : 'JOAN (Mock)'}
        </span>
      </div>
    );
  }

  return (
    <div className={`bg-gradient-to-br from-blue-900/20 to-purple-900/20 backdrop-blur-lg border border-white/10 rounded-xl p-4 ${className}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          🧠 JOAN ASI System
          <div 
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'
            }`}
          />
        </h3>
        <div className="text-sm text-gray-300">
          {isConnected ? 'Live' : 'Mock Mode'}
        </div>
      </div>

      {frame && (
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-black/20 rounded-lg p-3">
            <div className="text-xs text-gray-400 mb-1">System State</div>
            <div className={`font-semibold ${
              frame.analysis.state === 'optimal' ? 'text-green-400' :
              frame.analysis.state === 'high_load' ? 'text-yellow-400' :
              'text-red-400'
            }`}>
              {frame.analysis.state === 'optimal' ? '✅ Optimal' :
               frame.analysis.state === 'high_load' ? '⚠️ High Load' :
               '🚨 Anomalous'}
            </div>
          </div>

          <div className="bg-black/20 rounded-lg p-3">
            <div className="text-xs text-gray-400 mb-1">Ethics</div>
            <div className={`font-semibold ${
              frame.decision.ethics === 'proceed_normal' ? 'text-green-400' : 'text-yellow-400'
            }`}>
              {frame.decision.ethics === 'proceed_normal' ? '💚 Protecting' : '🛡️ Guarding'}
            </div>
          </div>
        </div>
      )}

      {planetaryHealth && (
        <div className="mb-4">
          <div className="text-sm text-gray-300 mb-2">🌍 Planetary Health Overview</div>
          <div className="grid grid-cols-4 gap-2">
            <div className="text-center">
              <div className="text-xs text-gray-400">Bio</div>
              <div className="text-sm font-semibold text-green-400">
                {planetaryHealth.biodiversityIndex}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-400">Eco</div>
              <div className="text-sm font-semibold text-blue-400">
                {planetaryHealth.ecosystemBalance}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-400">Human</div>
              <div className="text-sm font-semibold text-purple-400">
                {planetaryHealth.humanWellbeing}%
              </div>
            </div>
            <div className="text-center">
              <div className="text-xs text-gray-400">Water</div>
              <div className="text-sm font-semibold text-cyan-400">
                {planetaryHealth.waterPurity}%
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="border-t border-white/10 pt-3">
        <div className="text-xs text-gray-400 mb-1">💝 Jona's Wisdom</div>
        <div className="text-sm italic text-gray-200 leading-relaxed">
          "{jonaWisdom}"
        </div>
      </div>

      <div className="mt-3 flex justify-between items-center text-xs text-gray-400">
        <span>Alba • Albi • Jona</span>
        <span>"Here." - Our home, our responsibility</span>
      </div>
    </div>
  );
}
