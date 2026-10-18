import React from 'react';

export const HeroSectionSimple = () => {
  return (
    <section className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto text-center px-6">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          🧠 UltraWeb Thinking
        </h1>
        <h2 className="text-2xl text-gray-700 mb-4">
          EuroWeb Web8 AGI Browser
        </h2>
        <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
          Platforma më e avancuar e shfletuesit Web8 me inteligjencë artificiale të integruar (AGI). 
          Krijuar nga Ledjan Ahmati me arkitekturë industriale dhe sistemet më të reja të AI.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/openmind"
            className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 transition-colors"
          >
            🚀 Eksploro AI Chat
          </a>
          <a
            href="/browser"
            className="inline-flex items-center justify-center px-8 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors"
          >
            🌐 Hap Web8 Browser
          </a>
        </div>
        
        <div className="mt-12 text-sm text-gray-500">
          <p>✅ Live & Working | 🛡️ Industrial Architecture | 🧠 Universal AI Gateway</p>
        </div>
      </div>
    </section>
  );
};

