'use client';

import { useEffect, useState } from 'react';

interface AIResponse {
  provider: string;
  response: string;
  confidence: number;
  source: string;
  timestamp: number;
  ethicalCheck?: {
    passed: boolean;
    concerns?: string[];
    recommendations?: string[];
  };
}

interface ServiceStatus {
  id: string;
  config: {
    name: string;
    description: string;
    status: 'active' | 'inactive' | 'error' | 'initializing';
    capabilities: string[];
  };
  health: {
    status: 'healthy' | 'warning' | 'critical';
    responseTime: number;
  };
}

interface OpenMindResponse {
  query: string;
  responses: AIResponse[];
  serviceResults: Record<string, any>;
  synthesis: {
    mainResponse: string;
    sources: string[];
    confidence: number;
    openMindPrinciples: string[];
  };
  meta: {
    totalResponseTime: number;
    servicesQueried: number;
    ethicallyValidated: boolean;
  };
  error?: string;
  details?: string;
}

interface SystemOverview {
  totalServices: number;
  activeServices: number;
  healthyServices: number;
  capabilities: string[];
}

export default function OpenMindPage() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<OpenMindResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [systemOverview, setSystemOverview] = useState<SystemOverview | null>(null);
  const [showServices, setShowServices] = useState(false);

  // Load service status on component mount
  useEffect(() => {
    loadServiceStatus();
  }, []);

  const loadServiceStatus = async () => {
    try {
      const response = await fetch('/api/openmind?action=services');
      const data = await response.json();
      setServices(data.services || []);
      setSystemOverview(data.overview || null);
    } catch (error) {
      console.error('Failed to load service status:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/openmind', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          options: {
            ethicalCheck: true,
            attributeSource: true,
            maxResults: 10
          }
        }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('OpenMind query failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getHealthIcon = (status: string) => {
    switch (status) {
      case 'healthy': return '🟢';
      case 'warning': return '🟡';
      case 'critical': return '🔴';
      default: return '⚪';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return '✅';
      case 'inactive': return '⏸️';
      case 'error': return '❌';
      case 'initializing': return '🔄';
      default: return '❓';
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-4xl font-bold mb-2">🧠 OpenMind Universal AI</h1>
              <p className="text-gray-400">
                Informacione nga çdo AI që ekziston duke respektuar burimin e informacionit
              </p>
            </div>
            <a 
              href="/openmind/status"
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-sm font-medium"
            >
              📊 System Status
            </a>
          </div>
          
          {/* System Status */}
          {systemOverview && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-gray-800 p-3 rounded-lg">
                <div className="text-2xl font-bold text-blue-400">{systemOverview.totalServices}</div>
                <div className="text-sm text-gray-400">Total Services</div>
              </div>
              <div className="bg-gray-800 p-3 rounded-lg">
                <div className="text-2xl font-bold text-green-400">{systemOverview.activeServices}</div>
                <div className="text-sm text-gray-400">Active Services</div>
              </div>
              <div className="bg-gray-800 p-3 rounded-lg">
                <div className="text-2xl font-bold text-green-400">{systemOverview.healthyServices}</div>
                <div className="text-sm text-gray-400">Healthy Services</div>
              </div>
              <div className="bg-gray-800 p-3 rounded-lg">
                <div className="text-2xl font-bold text-purple-400">{systemOverview.capabilities.length}</div>
                <div className="text-sm text-gray-400">Capabilities</div>
              </div>
            </div>
          )}

          <button
            onClick={() => setShowServices(!showServices)}
            className="mb-4 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
          >
            {showServices ? '🔼 Fshih Shërbimet' : '🔽 Shiko Shërbimet'}
          </button>

          {/* Services Status */}
          {showServices && (
            <div className="mb-6 bg-gray-800 p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-3">🔧 Platform Services Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {services.map((service) => (
                  <div key={service.id} className="bg-gray-700 p-3 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{service.config.name}</span>
                      <div className="flex gap-1">
                        {getStatusIcon(service.config.status)}
                        {getHealthIcon(service.health.status)}
                      </div>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{service.config.description}</p>
                    <div className="flex flex-wrap gap-1">
                      {service.config.capabilities.slice(0, 3).map((cap) => (
                        <span key={cap} className="text-xs bg-blue-600 px-2 py-1 rounded">
                          {cap}
                        </span>
                      ))}
                      {service.config.capabilities.length > 3 && (
                        <span className="text-xs text-gray-400">
                          +{service.config.capabilities.length - 3}
                        </span>
                      )}
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      Response: {service.health.responseTime}ms
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Query Form */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="mb-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Pyet çdo gjë që dëshiron të dish..."
              className="w-full p-4 bg-gray-800 border border-gray-600 rounded-lg focus:border-blue-500 focus:outline-none"
              disabled={loading}
            />
          </div>
          
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg font-medium transition-colors"
          >
            {loading ? '🔍 Kërkuam...' : '🚀 Kërko në OpenMind'}
          </button>
        </form>

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Error handling */}
            {result.error ? (
              <div className="bg-red-900/20 border border-red-500 p-6 rounded-lg">
                <h2 className="text-xl font-bold text-red-400 mb-2">❌ Gabim në Sistem</h2>
                <p className="text-red-300 mb-2">{result.error}</p>
                {result.details && (
                  <details className="mt-4">
                    <summary className="text-red-400 cursor-pointer">Detaje teknike</summary>
                    <pre className="text-xs text-gray-400 mt-2 p-2 bg-gray-800 rounded overflow-x-auto">
                      {result.details}
                    </pre>
                  </details>
                )}
                <div className="mt-4 text-sm text-gray-400">
                  💡 Sistemi është duke u riparuar. Ju lutem provoni përsëri pas pak çastesh.
                </div>
              </div>
            ) : result.synthesis ? (
              <>
                {/* Main Synthesis */}
                <div className="bg-gray-800 p-6 rounded-lg">
                  <h2 className="text-2xl font-bold mb-4">📝 Sinteza e Informacionit</h2>
                  <div className="prose prose-invert max-w-none">
                    <div className="whitespace-pre-wrap">{result.synthesis.mainResponse || "Nuk u gjet përgjigje e vlefshme."}</div>
                  </div>
                  
                  <div className="mt-4 p-4 bg-gray-700 rounded-lg">
                    <h3 className="font-semibold mb-2">🎯 OpenMind Principles</h3>
                    <ul className="space-y-1">
                      {(result.synthesis.openMindPrinciples || []).map((principle, index) => (
                        <li key={index} className="text-sm text-gray-300">{principle}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-yellow-900/20 border border-yellow-500 p-6 rounded-lg">
                <h2 className="text-xl font-bold text-yellow-400 mb-2">⚠️ Përgjigje e papritur</h2>
                <p className="text-yellow-300">Sistemi ktheu një përgjigje që nuk është në formatin e pritur.</p>
              </div>
            )}

            {/* AI Responses */}
            {result.responses && result.responses.length > 0 && (
              <div className="bg-gray-800 p-6 rounded-lg">
                <h2 className="text-2xl font-bold mb-4">🤖 AI Responses</h2>
                <div className="space-y-4">
                  {result.responses.map((response, index) => (
                    <div key={index} className="bg-gray-700 p-4 rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                        <h3 className="font-semibold">{response.provider}</h3>
                        <div className="flex items-center gap-2">
                          <span className="text-sm bg-blue-600 px-2 py-1 rounded">
                            {(response.confidence * 100).toFixed(1)}% confident
                          </span>
                          {response.ethicalCheck?.passed && (
                            <span className="text-sm bg-green-600 px-2 py-1 rounded">
                              ✓ Ethically Validated
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="text-gray-300 mb-2">{response.response}</p>
                      <div className="text-xs text-gray-500">
                        Source: {response.source} | {new Date(response.timestamp).toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Service Results */}
            {result.serviceResults && Object.keys(result.serviceResults).length > 0 && (
              <div className="bg-gray-800 p-6 rounded-lg">
                <h2 className="text-2xl font-bold mb-4">🔧 Service Results</h2>
                <div className="space-y-4">
                  {Object.entries(result.serviceResults).map(([serviceName, serviceResult]) => (
                    <div key={serviceName} className="bg-gray-700 p-4 rounded-lg">
                      <h3 className="font-semibold mb-2">{serviceName.toUpperCase()} Service</h3>
                      {serviceResult.type === 'search_results' && serviceResult.data && (
                        <div>
                          <p className="text-sm text-gray-400 mb-2">Search Results:</p>
                          <div className="space-y-2">
                            {serviceResult.data.slice(0, 3).map((item: any, index: number) => (
                              <div key={index} className="text-sm bg-gray-600 p-2 rounded">
                                {item.title || item.content || JSON.stringify(item).substring(0, 100)}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      {serviceResult.type === 'error' && (
                        <p className="text-red-400 text-sm">Error: {serviceResult.error}</p>
                      )}
                      {serviceResult.type && serviceResult.type !== 'search_results' && serviceResult.type !== 'error' && (
                        <div className="text-sm">
                          <p className="text-gray-400">Type: {serviceResult.type}</p>
                          <pre className="mt-2 text-xs text-gray-300 bg-gray-600 p-2 rounded overflow-x-auto">
                            {JSON.stringify(serviceResult.data, null, 2).substring(0, 300)}
                            {JSON.stringify(serviceResult.data, null, 2).length > 300 && '...'}
                          </pre>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Meta Information */}
            <div className="bg-gray-800 p-6 rounded-lg">
              <h2 className="text-2xl font-bold mb-4">📊 Query Metadata</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-gray-400">Response Time</div>
                  <div className="font-semibold">{result.meta.totalResponseTime}ms</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Services Queried</div>
                  <div className="font-semibold">{result.meta.servicesQueried}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-400">Ethical Validation</div>
                  <div className="font-semibold">
                    {result.meta.ethicallyValidated ? '✅ Enabled' : '❌ Disabled'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
