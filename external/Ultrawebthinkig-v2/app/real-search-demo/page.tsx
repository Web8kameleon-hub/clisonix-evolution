/**
 * Web8 Real Search Demo Page
 * Demonstron sistemin real të kërkimit pa mock
 * 
 * @author UltraWeb Team
 * @version 8.0.0-REAL-SEARCH-DEMO
 */

import { Metadata } from 'next';
import RealSearchInterface from '../../components/RealSearchInterface';

export const metadata: Metadata = {
  title: 'Web8 Real Search Engine - No Mock Data | UltraWeb',
  description: 'Real search engine powered by live APIs and web scraping. No mock data - only real results from the web.',
  keywords: 'real search, web search, API search, no mock, live data, web scraping'
};

export default function RealSearchDemoPage() {
  return (
    <div>
      <RealSearchInterface 
        autoFocus={true}
        showHistory={true}
        maxResults={20}
        searchType="web"
      />
    </div>
  );
}
