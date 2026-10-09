'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, BookOpen, ArrowLeft, Download } from 'lucide-react';
import Link from 'next/link';

export default function AlbiSettingsDocumentation() {
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
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 p-6">
      {/* Header */}
      <div className="max-w-4xl mx-auto mb-8">
        <Link href="/modules/albi-eeg-live">
          <button className="flex items-center gap-2 text-purple-400 hover:text-purple-300 mb-6 transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to ALBI EEG
          </button>
        </Link>

        <div className="flex items-start gap-4 mb-8">
          <div className="p-4 bg-gradient-to-br from-purple-500 to-blue-500 rounded-lg">
            <BookOpen className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-black bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent mb-2">
              ALBI EEG Settings Tab
            </h1>
            <h2 className="text-xl text-purple-300 mb-2">Integration Analysis & Implementation Roadmap</h2>
            <p className="text-slate-400 text-sm">Document Version 1.0 • February 19, 2026</p>
          </div>
        </div>

        {/* Download Button */}
        <button
          onClick={() => {
            const element = document.createElement('a');
            element.href = '/albi-settings-guide.md';
            element.download = 'ALBI_EEG_Settings_Tab_Guide.md';
            document.body.appendChild(element);
            element.click();
            document.body.removeChild(element);
          }}
          className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-bold transition-colors mb-8"
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
              <h2 className="text-2xl font-bold text-purple-300 flex items-center gap-2">
                <span className="text-3xl">📋</span>
                Executive Summary
              </h2>
              <p className="text-slate-400 text-sm mt-1">Current state, gap analysis, and proposed solution</p>
            </div>
            {expandedSections['overview'] ? (
              <ChevronUp className="w-6 h-6 text-purple-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-purple-400" />
            )}
          </button>
          {expandedSections['overview'] && (
            <div className="px-6 pb-6 border-t border-slate-700 space-y-4">
              <div>
                <h3 className="text-lg font-bold text-cyan-300 mb-2">Current State</h3>
                <ul className="space-y-2 text-slate-300">
                  <li>✅ 680 lines of production React code</li>
                  <li>✅ 100% live API integration (zero placeholders)</li>
                  <li>✅ WebSocket streaming for real-time data</li>
                  <li>✅ 8-channel display with 1Hz metrics polling</li>
                  <li>✅ Professional dark UI with clinical status indicators</li>
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-bold text-yellow-300 mb-2">Current Gaps</h3>
                <div className="grid grid-cols-2 gap-3 text-sm text-slate-300">
                  <div>❌ Channel selection persistence</div>
                  <div>❌ API endpoint configuration</div>
                  <div>❌ Display preferences</div>
                  <div>❌ Sampling rate adjustment</div>
                  <div>❌ Export format selection</div>
                  <div>❌ Device/patient profiles</div>
                  <div>❌ Notification settings</div>
                  <div>❌ Custom session metadata</div>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Architecture Analysis */}
        <section className="bg-slate-900/50 border border-slate-700 rounded-lg overflow-hidden">
          <button
            onClick={() => toggleSection('architecture')}
            className="w-full flex items-center justify-between p-6 hover:bg-slate-800/50 transition-colors"
          >
            <div className="text-left">
              <h2 className="text-2xl font-bold text-blue-300 flex items-center gap-2">
                <span className="text-3xl">🏗️</span>
                Current Architecture Analysis
              </h2>
              <p className="text-slate-400 text-sm mt-1">Component structure, data flows, and state management</p>
            </div>
            {expandedSections['architecture'] ? (
              <ChevronUp className="w-6 h-6 text-blue-400" />
            ) : (
              <ChevronDown className="w-6 h-6 text-blue-400" />
            )}
          </button>
          {expandedSections['architecture'] && (
            <div className="px-6 pb-6 border-t border-slate-700 space-y-4">
              <div className="bg-slate-800/50 rounded p-4 text-sm space-y-2">
                <p className="text-slate-300"><strong>File:</strong> apps/web/app/modules/albi-eeg-live/page.tsx</p>
                <p className="text-slate-300"><strong>Size:</strong> 546 lines including UI, WebSocket, metrics polling</p>
                <p className="text-slate-300"><strong>API:</strong> http://127.0.0.1:6681</p>
              </div>
              <div>
                <h3 className="text-lg font-bold text-cyan-300 mb-2">Key State Variables</h3>
                <div className="space-y-2 text-sm text-slate-300">
                  <div className="flex justify-between"><span>sessionId</span><span className="text-red-400">❌ Lost on reload</span></div>
                  <div className="flex justify-between"><span>selectedChannels</span><span className="text-red-400">❌ Resets to defaults</span></div>
                  <div className="flex justify-between"><span>API_BASE</span><span className="text-red-400">❌ Hardcoded</span></div>
                  <div className="flex justify-between"><span>isRecording, metrics</span><span className="text-red-400">❌ Ephemeral</span></div>
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
                Settings Tab Design Specification
              </h2>
              <p className="text-slate-400 text-sm mt-1">6-tab interface with full configuration options</p>
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
                  <p className="font-bold text-cyan-300 mb-2">📟 Device & API</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• API Host & Port</li>
                    <li>• Device Type Selection</li>
                    <li>• Sample Rate Config</li>
                    <li>• Channel Configuration</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">🎨 Display</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• Theme Selection</li>
                    <li>• Channel Layout</li>
                    <li>• Amplitude Scale</li>
                    <li>• Refresh Rate</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">📊 Data</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• Recording Mode</li>
                    <li>• Auto-Export</li>
                    <li>• Export Formats</li>
                    <li>• Compression</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">🔔 Alerts</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• Anomaly Alerts</li>
                    <li>• Quality Threshold</li>
                    <li>• Sound Settings</li>
                    <li>• Notifications</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">👤 Profiles</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• Clinical Standard</li>
                    <li>• Research Lab</li>
                    <li>• Home Monitoring</li>
                    <li>• ICU Monitoring</li>
                  </ul>
                </div>
                <div className="bg-slate-800/50 rounded p-4">
                  <p className="font-bold text-cyan-300 mb-2">📁 Files</p>
                  <ul className="text-sm text-slate-300 space-y-1">
                    <li>• Auto-Save Config</li>
                    <li>• Session Naming</li>
                    <li>• Archive Rules</li>
                    <li>• Retention Policy</li>
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
              <p className="text-slate-400 text-sm mt-1">Phased approach from state management to production deployment</p>
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
                <p className="font-bold text-blue-300 mb-2">Phase 1: Settings State Container (Week 1)</p>
                <p className="text-sm text-slate-300">Create AlbiSettingsContext with Pydantic schema, localStorage persistence, and backend sync</p>
              </div>
              <div className="bg-cyan-900/30 border border-cyan-600/50 rounded p-4">
                <p className="font-bold text-cyan-300 mb-2">Phase 2: Settings UI Components (Week 2)</p>
                <p className="text-sm text-slate-300">Build AlbiSettingsModal with 6 tabs, form controls, validation, and real-time preview</p>
              </div>
              <div className="bg-green-900/30 border border-green-600/50 rounded p-4">
                <p className="font-bold text-green-300 mb-2">Phase 3: Main Component Integration (Week 2)</p>
                <p className="text-sm text-slate-300">Integrate settings into page.tsx, apply settings dynamically, handle API reconfiguration</p>
              </div>
              <div className="bg-purple-900/30 border border-purple-600/50 rounded p-4">
                <p className="font-bold text-purple-300 mb-2">Phase 4: Backend Endpoints (Week 3)</p>
                <p className="text-sm text-slate-300">Add 6 new FastAPI endpoints: schema, profiles, validate, apply, export, import</p>
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
                Technical Integration Points
              </h2>
              <p className="text-slate-400 text-sm mt-1">API configuration, persistence strategies, and real-time settings application</p>
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
                <h3 className="text-lg font-bold text-cyan-300 mb-2">Data Persistence: 3-Layer Strategy</h3>
                <div className="space-y-2 text-sm text-slate-300">
                  <p><strong className="text-cyan-300">Layer 1: Browser LocalStorage</strong> - Immediate user preferences cache (~10MB)</p>
                  <p><strong className="text-cyan-300">Layer 2: PostgreSQL Database</strong> - Persistent user profile with audit trail</p>
                  <p><strong className="text-cyan-300">Layer 3: Cloud Sync</strong> - Optional cross-device synchronization (AWS/Azure/GCS)</p>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-bold text-green-300 mb-2">New Backend Endpoints (6 Total)</h3>
                <div className="space-y-2 text-sm text-slate-300">
                  <p>🔹 GET /settings/schema - Complete settings schema with defaults</p>
                  <p>🔹 GET /settings/profiles - Predefined hospital profiles</p>
                  <p>🔹 POST /settings/validate - Validate before applying</p>
                  <p>🔹 POST /session/{'{id}'}/apply-settings - Real-time application</p>
                  <p>🔹 GET /settings/export - Export as shareable file</p>
                  <p>🔹 POST /settings/import - Import from configuration</p>
                </div>
              </div>
            </div>
          )}
        </section>

        {/* Success Metrics */}
        <section className="bg-gradient-to-r from-green-900/50 to-cyan-900/50 border border-green-600/50 rounded-lg p-6 mb-8">
          <h2 className="text-2xl font-bold text-green-300 mb-4 flex items-center gap-2">
            <span className="text-3xl">✅</span>
            Success Metrics
          </h2>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="font-bold text-cyan-300 mb-2">Clinical Users</p>
              <ul className="text-slate-300 space-y-1">
                <li>✓ Save configurations</li>
                <li>✓ Hospital profiles</li>
                <li>✓ Custom alerts</li>
                <li>✓ Multi-format export</li>
              </ul>
            </div>
            <div>
              <p className="font-bold text-cyan-300 mb-2">Developers</p>
              <ul className="text-slate-300 space-y-1">
                <li>✓ Centralized settings</li>
                <li>✓ Dynamic API config</li>
                <li>✓ Device abstraction</li>
                <li>✓ Audit trails</li>
              </ul>
            </div>
            <div>
              <p className="font-bold text-cyan-300 mb-2">Hospital IT</p>
              <ul className="text-slate-300 space-y-1">
                <li>✓ Profile deployment</li>
                <li>✓ Backup & recovery</li>
                <li>✓ Compliance reports</li>
                <li>✓ Multi-site sync</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="bg-purple-900/50 border border-purple-600/50 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-bold text-purple-300 mb-3">Ready to Implement?</h2>
          <p className="text-slate-300 mb-4">
            This comprehensive analysis provides everything needed to implement a professional Settings Tab for the ALBI EEG module. 
            Start with Phase 1 to establish the settings infrastructure, then progressively add UI components, integration, and backend support.
          </p>
          <div className="flex gap-4">
            <Link href="/modules/albi-eeg-live">
              <button className="px-6 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-bold transition-colors">
                Back to ALBI EEG
              </button>
            </Link>
            <a
              href="/albi-settings-guide.md"
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
