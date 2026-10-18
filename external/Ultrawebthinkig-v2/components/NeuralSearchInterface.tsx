/**
 * Web8 Neural Search Interface - Real Frontend Component
 * Komponent i plotë për Neural Search me integrimin e vërtetë API
 * 
 * @author UltraWeb Neural Team
 * @version 8.0.0-NEURAL-UI
 */

'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, Brain, Zap, Filter, Clock, Star, ExternalLink, Loader2, AlertCircle } from 'lucide-react';

// Types from backend
interface NeuralSearchResult {
  id: string;
  title: string;
  url: string;
  description: string;
  relevanceScore: number;
  neuralScore: number;
  category: 'web' | 'neural' | 'agi' | 'technical' | 'documentation';
  timestamp: Date;
  source: 'web8-neural' | 'agi-core' | 'external-api' | 'neural-index';
  metadata: {
    keywords: string[];
    semanticTags: string[];
    contextScore: number;
    agiRelevance: number;
  };
}

interface SearchStats {
  totalQueries: number;
  cacheSize: number;
  avgResponseTime: number;
  topQueries: string[];
}

interface NeuralSearchResponse {
  success: boolean;
  query: string;
  results: NeuralSearchResult[];
  metadata: {
    total: number;
    responseTime: string;
    intent: string;
    depth: string;
    searchStats: {
      totalQueries: number;
      cacheSize: number;
    };
  };
  timestamp: string;
  version: string;
  error?: string;
}

const SEARCH_INTENTS = [
  { value: 'search', label: 'Search', icon: Search, color: '#3b82f6' },
  { value: 'learn', label: 'Learn', icon: Brain, color: '#10b981' },
  { value: 'code', label: 'Code', icon: Zap, color: '#f59e0b' },
  { value: 'analyze', label: 'Analyze', icon: Filter, color: '#8b5cf6' },
  { value: 'create', label: 'Create', icon: Star, color: '#ef4444' }
];

const SEARCH_DEPTHS = [
  { value: 'surface', label: 'Quick' },
  { value: 'deep', label: 'Deep' },
  { value: 'neural', label: 'Neural' },
  { value: 'agi', label: 'AGI' }
];

export default function NeuralSearchInterface() {
  // State management
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<NeuralSearchResult[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchStats, setSearchStats] = useState<SearchStats | null>(null);
  
  // Search configuration
  const [selectedIntent, setSelectedIntent] = useState('search');
  const [selectedDepth, setSelectedDepth] = useState('surface');
  const [showAdvanced, setShowAdvanced] = useState(false);
  
  // UI state
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchHistory, setSearchHistory] = useState<string[]>([]);
  const [responseTime, setResponseTime] = useState<string>('');
  
  // Refs
  const searchInputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  
  // Auto-focus search input
  useEffect(() => {
    searchInputRef.current?.focus();
  }, []);
  
  // Load search history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem('neural-search-history');
    if (saved) {
      try {
        setSearchHistory(JSON.parse(saved));
      } catch (error) {
        console.warn('Failed to load search history:', error);
      }
    }
  }, []);
  
  // Save search history
  useEffect(() => {
    if (searchHistory.length > 0) {
      localStorage.setItem('neural-search-history', JSON.stringify(searchHistory.slice(0, 10)));
    }
  }, [searchHistory]);
  
  // Debounced suggestions
  useEffect(() => {
    if (query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    
    const timeoutId = setTimeout(async () => {
      try {
        const startTime = performance.now();
        const response = await fetch(`/api/neural-search?q=${encodeURIComponent(query)}&format=minimal&limit=5`);
        
        if (!response.ok) {
          throw new Error(`Search failed: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        const endTime = performance.now();
        setResponseTime(`${Math.round(endTime - startTime)}ms`);
        
        if (data.results) {
          setSuggestions(data.results.slice(0, 5));
          setShowSuggestions(true);
        }
      } catch (error) {
        console.error('Neural search suggestions error:', error);
        setSuggestions([]);
        setShowSuggestions(false);
      }
    }, 300); // debounce delay

    return () => clearTimeout(timeoutId);
  }, [query]);

  // Handle search
  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const startTime = performance.now();
      const response = await fetch('/api/neural-search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery,
          intent: selectedIntent,
          depth: selectedDepth
        })
      });
      
      if (!response.ok) {
        throw new Error(`Search failed: ${response.status}`);
      }
      
      const data: NeuralSearchResponse = await response.json();
      const endTime = performance.now();
      
      setResults(data.results || []);
      setResponseTime(`${Math.round(endTime - startTime)}ms`);
      const stats = data.metadata?.searchStats;
      if (stats) {
        setSearchStats({
          totalQueries: stats.totalQueries || 0,
          cacheSize: stats.cacheSize || 0,
          avgResponseTime: Math.round(endTime - startTime),
          topQueries: []
        });
      }
      
      // Add to history
      setSearchHistory(prev => [searchQuery, ...prev.filter(q => q !== searchQuery)].slice(0, 10));
      
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Search failed');
    } finally {
      setIsLoading(false);
      setShowSuggestions(false);
    }
  };

  return (
    <div className="neural-search-interface">
      <div className="search-header">
        <h1>🧠 Neural Search</h1>
        <p>Advanced AI-powered search with neural intelligence</p>
      </div>
      
      <div className="search-box">
        <input
          ref={searchInputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
          placeholder="Ask anything... Neural AI will understand"
          className="search-input"
        />
        <button 
          onClick={() => handleSearch(query)}
          disabled={isLoading}
          className="search-button"
        >
          {isLoading ? <Loader2 className="animate-spin" /> : <Search />}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle /> {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="results-section">
          <div className="results-header">
            <span>{results.length} results found in {responseTime}</span>
          </div>
          
          {results.map((result) => (
            <div key={result.id} className="result-item">
              <h3>{result.title}</h3>
              <p>{result.description}</p>
              <div className="result-meta">
                <span>Score: {result.neuralScore.toFixed(2)}</span>
                <span>Category: {result.category}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      <style jsx>{`
        .neural-search-interface {
          max-width: 800px;
          margin: 0 auto;
          padding: 2rem;
        }
        .search-header {
          text-align: center;
          margin-bottom: 2rem;
        }
        .search-box {
          display: flex;
          gap: 0.5rem;
          margin-bottom: 2rem;
        }
        .search-input {
          flex: 1;
          padding: 0.75rem;
          border: 2px solid #e2e8f0;
          border-radius: 0.5rem;
          font-size: 1rem;
        }
        .search-button {
          padding: 0.75rem 1.5rem;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
        }
        .error-message {
          background: #fee2e2;
          color: #dc2626;
          padding: 1rem;
          border-radius: 0.5rem;
          margin-bottom: 1rem;
        }
        .results-section {
          margin-top: 2rem;
        }
        .result-item {
          border: 1px solid #e2e8f0;
          border-radius: 0.5rem;
          padding: 1rem;
          margin-bottom: 1rem;
        }
      `}</style>
    </div>
  );
}