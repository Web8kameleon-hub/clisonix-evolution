'use client';

import React, { useState } from 'react';

interface SearchResult {
  id: string;
  title: string;
  url: string;
  snippet: string;
}

interface WebSearchComponentProps {
  className?: string;
}

const WebSearchComponent: React.FC<WebSearchComponentProps> = ({ className = '' }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);

  const handleSearch = () => {
    if (!query.trim()) return;
    
    const mockResults: SearchResult[] = [
      {
        id: '1',
        title: `Search results for "${query}"`,
        url: 'https://example.com',
        snippet: `Mock search result for ${query}`
      }
    ];
    
    setResults(mockResults);
  };

  return (
    <div className={`search-container ${className}`}>
      <div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search..."
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      
      {results.length > 0 && (
        <div>
          {results.map((result) => (
            <div key={result.id}>
              <h3>{result.title}</h3>
              <p>{result.snippet}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Export both default and named for compatibility
export { WebSearchComponent };
export default WebSearchComponent;