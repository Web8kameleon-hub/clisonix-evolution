'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Music, ArrowLeft, Download } from 'lucide-react';
import Link from 'next/link';

export default function JonaSettingsDocumentation() {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    overview: true,
    architecture: true,
    specification: true,
    roadmap: true,
    integration: true,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-950 p-6">
      {/* Header */}
      <div className="max-w-4xl mx-auto mb-8">
        <Link href="/modules/jona-neural">
          <button className="flex items-center gap-2 text-indigo-400 hover:text-indigo-300 mb-6 transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to JONA Neural Synthesis
          </button>
        </Link>

        <div className="flex items-start gap-4 mb-8">
          <div className="p-4 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg">
            <Music className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-black bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
              JONA Neural Synthesis Settings
            </h1>
            <h2 className="text-xl text-indigo-300 mb-2">Professional Audio Synthesis Configuration Guide</h2>
            <p className="text-slate-400 text-sm">Document Version 1.0 • February 19, 2026 • Port 7777</p>
          </div>
        </div>

        {/* Download Button */}
        <button
          onClick={() => {
            const element = document.createElement('a');
            element.href = '/jona-settings-guide.md';
            element.download = 'JONA_Neural_Synthesis_Settings_Guide.md';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold transition-colors mb-8"
        >
          <Download className="w-4 h-4" />
          Download as Markdown
        </button>
      </div>

      {/* Content Sections */}
      <div className="max-w-4xl mx-auto space-y-4">
        
        {/* Executive Summary */}
        <section className="bg-slate-900/50 border border-slate-700 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('overview')}
            className="w-full flex items-center justify-between p-6 hover:bg-slate-800/50 transition-colors"
          >
            <div className="text-left">
              <h2 className="text-2xl font-bold text-indigo-300 flex items-center gap-2">
                <span className="text-3xl">🎵</span>
                Executive Summary
              </h2>
              <p className="text-slate-400 text-sm mt-1">Professional neural synthesis system with therapeutic presets and advanced audio control</p>
            </div>
            {expandedSections['overview'] ? (
              <ChevronUp className="w-6 h-6 text-indigo-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-indigo-400" />
            )}
          </button>
          {expandedSections['overview'] && (
            <div className="px-6 pb-6 border-t border-slate-700 space-y-4">
              <div>
                <h3 className="text-lg font-bold text-cyan-300 mb-2">Current Capabilities</h3>
                <ul className="space-y-2 text-slate-300">
                  <li>✅ Real-time neural audio synthesis (4 waveform types)</li>
                  <li>✅ 6 therapeutic presets (Deep Sleep to Cognition)</li>
                  <li>✅ Live frequency control 0.5-50 Hz</li>
                  <li>✅ WebSocket real-time audio streaming</li>
                  <li>✅ Brainwave band analysis with metrics</li>
                  <li>✅ Professional quality scoring (THD measurement)</li>
                  <li>✅ Audio file library and export</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-bold text-yellow-300 mb-2">Professional Features</h3>
                <div className="grid grid-cols-2 gap-3 text-sm text-slate-300">
                  <div>🎯 Precise frequency targeting</div>
                  <div>🔊 Volume normalization</div>
                  <div>📊 Real-time THD analysis</div>
                  <div>🧠 Brainwave band detection</div>
                  <div>💾 Multi-format export</div>
                  <div>⚡ High-fidelity synthesis</div>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Audio System Architecture */}
        <section className="bg-slate-900/50 border border-slate-700 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('architecture')}
            className="w-full flex items-center justify-between p-6 hover:bg-slate-800/50 transition-colors"
          >
            <div className="text-left">
              <h2 className="text-2xl font-bold text-purple-300 flex items-center gap-2">
                <span className="text-3xl">🏗️</span>
                Audio Processing Architecture
              </h2>
              <p className="text-slate-400 text-sm mt-1">Real-time synthesis engine with signal analysis and quality monitoring</p>
            </div>
            {expandedSections['architecture'] ? (
              <ChevronUp className="w-6 h-6 text-purple-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-purple-400" />
            )}
          </button>
          {expandedSections['architecture'] && (
            <div className="px-6 pb-6 border-t border-slate-700 space-y-4">
              <div className="bg-slate-800/50 rounded p-4 text-sm space-y-2">
                <p className="text-slate-300"><strong>File:</strong> apps/web/app/modules/jona-neural/page.tsx</p>
                <p className="text-slate-300"><strong>API Port:</strong> 7777</p>
                <p className="text-slate-300"><strong>Protocol:</strong> HTTP + WebSocket (ws://127.0.0.1:7777/stream/)</p>
                <p className="text-slate-300"><strong>Sample Rates:</strong> 44100 Hz (CD), 48000 Hz (Pro), 96000 Hz (HD)</p>
              </div>
              <div>
                <h3 className="text-lg font-bold text-cyan-300 mb-2">Signal Pipeline</h3>
                <div className="space-y-2 text-sm text-slate-300">
                  <div className="p-3 bg-indigo-900/30 rounded border border-indigo-600/50">Frequency Input (0.5-50 Hz) + Preset/Waveform Selection</div>
                  <div className="text-center text-indigo-400">↓</div>
                  <div className="p-3 bg-indigo-900/30 rounded border border-indigo-600/50">Waveform Generator (Sine, Binaural, Isochronic, Pink Noise)</div>
                  <div className="text-center text-indigo-400">↓</div>
                  <div className="p-3 bg-indigo-900/30 rounded border border-indigo-600/50">Audio Processing (Volume, Normalization, Filtering)</div>
                  <div className="text-center text-indigo-400">↓</div>
                  <div className="p-3 bg-indigo-900/30 rounded border border-indigo-600/50">FFT Analysis → Brainwave Detection + Quality Metrics</div>
                  <div className="text-center text-indigo-400">↓</div>
                  <div className="p-3 bg-indigo-900/30 rounded border border-indigo-600/50">Output to Device + File Recording</div>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Settings Tab Specification */}
        <section className="bg-slate-900/50 border border-slate-700 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('specification')}
            className="w-full flex items-center justify-between p-6 hover:bg-slate-800/50 transition-colors"
          >
            <div className="text-left">
              <h2 className="text-2xl font-bold text-green-300 flex items-center gap-2">
                <span className="text-3xl">⚙️</span>
                6-Tab Settings Interface
              </h2>
              <p className="text-slate-400 text-sm mt-1">Professional audio configuration with advanced synthesis controls</p>
            </div>
            {expandedSections['specification'] ? (
              <ChevronUp className="w-6 h-6 text-green-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-green-400" />
            )}
          </button>
          {expandedSections['specification'] && (
            <div className="px-6 pb-6 border-t border-slate-700 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">🔊 Audio Configuration</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• Output device selection</li>
                    <li>• Sample rate (44.1/48/96 kHz)</li>
                    <li>• Bit depth (16/24/32-bit)</li>
                    <li>• Volume control (0-100%)</li>
                    <li>• Normalization mode</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">🌊 Waveform Control</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• Primary waveform selection</li>
                    <li>• Secondary waveform mixing</li>
                    <li>• Blend ratio control</li>
                    <li>• Carrier frequency (binaural)</li>
                    <li>• Pulse width (isochronic)</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">🧠 Neural Parameters</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• Target brainwave band</li>
                    <li>• Entrainment mode selection</li>
                    <li>• Frequency sweep control</li>
                    <li>• Ramp-up/down times</li>
                    <li>• Session profiles</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">🎛️ Preset Management</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• 6 therapeutic presets</li>
                    <li>• Custom preset creation</li>
                    <li>• Preset sharing</li>
                    <li>• Quick load/save</li>
                    <li>• Preset library</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">📊 Quality Metrics</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• Real-time THD measurement</li>
                    <li>• Frequency accuracy tracking</li>
                    <li>• Signal-to-noise ratio</li>
                    <li>• Harmonic analysis</li>
                    <li>• Quality alerts</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">💾 File Management</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• WAV/MP3/OGG export</li>
                    <li>• Auto-recording enable</li>
                    <li>• Metadata inclusion</li>
                    <li>• Session archival</li>
                    <li>• File organization</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Implementation Roadmap */}
        <section className="bg-slate-900/50 border border-slate-700 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('roadmap')}
            className="w-full flex items-center justify-between p-6 hover:bg-slate-800/50 transition-colors"
          >
            <div className="text-left">
              <h2 className="text-2xl font-bold text-orange-300 flex items-center gap-2">
                <span className="text-3xl">🗺️</span>
                4-Week Implementation Roadmap
              </h2>
              <p className="text-slate-400 text-sm mt-1">Phased development from settings container to production deployment</p>
            </div>
            {expandedSections['roadmap'] ? (
              <ChevronUp className="w-6 h-6 text-orange-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-orange-400" />
            )}
          </button>
          {expandedSections['roadmap'] && (
            <div className="px-6 pb-6 border-t border-slate-700 space-y-3">
              <div className="bg-blue-900/30 border border-blue-600/50 rounded p-4">
                <p className="font-bold text-blue-300 mb-2">🔹 Phase 1: Settings Container (Week 1)</p>
                <p className="text-sm text-slate-300">Create JonaSettingsContext with Pydantic schema, localStorage/PostgreSQL persistence, and audit trails</p>
              </div>
              <div className="bg-cyan-900/30 border border-cyan-600/50 rounded p-4">
                <p className="font-bold text-cyan-300 mb-2">🔹 Phase 2: UI Components (Week 2)</p>
                <p className="text-sm text-slate-300">Build 6-tab modal interface with audio device selectors, frequency sliders, preset managers</p>
              </div>
              <div className="bg-green-900/30 border border-green-600/50 rounded p-4">
                <p className="font-bold text-green-300 mb-2">🔹 Phase 3: Integration (Week 2)</p>
                <p className="text-sm text-slate-300">Integrate settings into JONA module, apply parameters dynamically, handle real-time synthesis updates</p>
              </div>
              <div className="bg-purple-900/30 border border-purple-600/50 rounded p-4">
                <p className="font-bold text-purple-300 mb-2">🔹 Phase 4: Backend Endpoints (Week 3)</p>
                <p className="text-sm text-slate-300">Add FastAPI endpoints: schema, presets, validate, apply, export, quality metrics</p>
              </div>
            </div>
          )}
        </section>

        {/* Technical Integration */}
        <section className="bg-slate-900/50 border border-slate-700 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('integration')}
            className="w-full flex items-center justify-between p-6 hover:bg-slate-800/50 transition-colors"
          >
            <div className="text-left">
              <h2 className="text-2xl font-bold text-pink-300 flex items-center gap-2">
                <span className="text-3xl">🔗</span>
                Technical Integration
              </h2>
              <p className="text-slate-400 text-sm mt-1">Real-time synthesis updates, audio device routing, and quality monitoring</p>
            </div>
            {expandedSections['integration'] ? (
              <ChevronUp className="w-6 h-6 text-pink-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-pink-400" />
            )}
          </button>
          {expandedSections['integration'] && (
            <div className="px-6 pb-6 border-t border-slate-700 space-y-4">
              <div>
                <h3 className="text-lg font-bold text-cyan-300 mb-2">3-Layer Data Persistence</h3>
                <div className="space-y-2 text-sm text-slate-300">
                  <p><strong className="text-cyan-300">Layer 1: LocalStorage</strong> - User preferences cache (~10MB limit)</p>
                  <p><strong className="text-cyan-300">Layer 2: PostgreSQL</strong> - User profiles with audit trails and compliance</p>
                  <p><strong className="text-cyan-300">Layer 3: Audio Files</strong> - Archived synthesis sessions with metadata</p>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-bold text-green-300 mb-2">New Backend Endpoints (6 Total)</h3>
                <div className="space-y-2 text-sm text-slate-300">
                  <p>🔹 GET /neural/settings/default - Default settings + device enumeration</p>
                  <p>🔹 GET /neural/presets - List therapeutic and custom presets</p>
                  <p>🔹 POST /neural/presets/create - Create custom synthesis preset</p>
                  <p>🔹 POST /neural/synthesis/validate - Validate parameters before applying</p>
                  <p>🔹 POST /neural/audio/export - Export audio in various formats</p>
                  <p>🔹 GET /neural/metrics/quality - Real-time THD and accuracy metrics</p>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-bold text-yellow-300 mb-2">Real-Time Settings Application</h3>
                <div className="space-y-2 text-sm text-slate-300">
                  <p>• Frequency changes applied during active synthesis (no restart)</p>
                  <p>• Waveform switching without audio artifacts</p>
                  <p>• Volume adjustments reflected immediately</p>
                  <p>• Preset changes update all parameters atomically</p>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Success Metrics */}
        <section className="bg-gradient-to-r from-green-900/50 to-indigo-900/50 border border-green-600/50 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-green-300 mb-4 flex items-center gap-2">
            <span className="text-3xl">✅</span>
            Success Metrics & Use Cases
          </h2>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="font-bold text-cyan-300 mb-2">📱 Clinic Users</p>
              <ul className="text-slate-300 space-y-1">
                <li>✓ Therapeutic presets</li>
                <li>✓ Patient protocols</li>
                <li>✓ Session recording</li>
                <li>✓ Data export</li>
              </ul>
            </div>
            <div>
              <p className="font-bold text-cyan-300 mb-2">🔬 Researchers</p>
              <ul className="text-slate-300 space-y-1">
                <li>✓ Precise frequency</li>
                <li>✓ Parameter logging</li>
                <li>✓ Quality metrics</li>
                <li>✓ Reproducibility</li>
              </ul>
            </div>
            <div>
              <p className="font-bold text-cyan-300 mb-2">👥 General Users</p>
              <ul className="text-slate-300 space-y-1">
                <li>✓ Meditation support</li>
                <li>✓ Sleep enhancement</li>
                <li>✓ Focus sessions</li>
                <li>✓ Relaxation</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="bg-indigo-900/50 border border-indigo-600/50 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-indigo-300 mb-3">Ready to Deploy Professional Audio Synthesis?</h2>
          <p className="text-slate-300 mb-4">
            The JONA Neural Synthesis system provides enterprise-grade brainwave entrainment technology with 
            professional audio quality, therapeutic presets, and real-time parameter control.
          </p>
          <div className="flex gap-4">
            <Link href="/modules/jona-neural">
              <button className="px-6 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-bold transition-colors">
                Back to JONA Neural Synthesis
              </button>
            </Link>
            <a
              href="/jona-settings-guide.md"
              download
              className="px-6 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-bold transition-colors inline-flex items-center gap-2"
            >
              <Download className="w-4 h-4" />
              Download Full Guide
            </a>
          </div>
        </section>
      </div>
    </div>
  );
}
