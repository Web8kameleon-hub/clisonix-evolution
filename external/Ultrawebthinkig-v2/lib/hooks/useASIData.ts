'use client'

import { useState, useEffect } from 'react'

// 🚀 Custom Hook for ASI Data Management
export function useASIData() {
  const [data, setData] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<any>(null)

  useEffect(() => {
    // 🔄 REAL API calls to actual ASI services
    const fetchSystemStatus = async () => {
      try {
        setIsLoading(true)
        
        // 🚀 FETCH REAL SYSTEM DATA from actual API
        const realDataResponse = await fetch('/api/system/real')
        
        if (!realDataResponse.ok) {
          throw new Error('Failed to fetch real system data')
        }
        
        const realSystemStatus = await realDataResponse.json()
        
        setData(realSystemStatus)
        setError(null)
      } catch (err: any) {
        setError(err)
      } finally {
        setIsLoading(false)
      }
    }

    // Initial fetch
    fetchSystemStatus()

    // 🔄 Auto-refresh every 30 seconds
    const interval = setInterval(fetchSystemStatus, 30000)

    return () => clearInterval(interval)
  }, [])

  return { data, isLoading, error }
}

// 🌍 Hook for Cultural Intelligence Data
export function useCulturalData() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const fetchCulturalData = async (query: string = 'albania') => {
    setIsLoading(true)
    try {
      // Simulate API call to /api/cultural
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const mockCulturalData = {
        query,
        data: {
          total_sources: 156,
          museums_connected: 42,
          libraries_connected: 38,
          cultural_sites: 76,
          albanian_connections: query.toLowerCase().includes('albania') ? 89 : 12,
          heritage_items: 247
        },
        asi_cultural_analysis: `Cultural intelligence analysis for "${query}" shows rich heritage connections with global significance.`,
        sources: ['Smithsonian', 'Met Museum', 'Library of Congress', 'British Library'],
        last_updated: new Date().toISOString()
      }
      
      const response = await fetch(`/api/cultural?query=${query}`)
      if (!response.ok) {
        throw new Error('Network response was not ok')
      }
      const culturalData = await response.json()
      setData(culturalData)
    } catch (error) {
      console.error('Error fetching cultural data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return { data, isLoading, fetchCulturalData }
}

// ₿ Hook for Blockchain Data
export function useBlockchainData() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const fetchBlockchainData = async (symbol: string = 'bitcoin') => {
    setIsLoading(true)
    try {
      // Simulate API call to /api/blockchain
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const mockBlockchainData = {
        symbol,
        price: symbol === 'bitcoin' ? 67234.56 : 2456.78,
        change_24h: symbol === 'bitcoin' ? 2.45 : -1.23,
        market_cap: '$1.2T',
        volume_24h: '$45.6B',
        albanian_lek_rate: 95.67,
        exchanges_connected: 12,
        last_updated: new Date().toISOString()
      }
      
      const response = await fetch(`/api/blockchain?symbol=${symbol}`)
      if (!response.ok) {
        throw new Error('Network response was not ok')
      }
      const blockchainData = await response.json()
      setData(blockchainData)
    } catch (error) {
      console.error('Error fetching blockchain data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return { data, isLoading, fetchBlockchainData }
}

// 📰 Hook for News Data
export function useNewsData() {
  const [data, setData] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const fetchNewsData = async () => {
    setIsLoading(true)
    try {
      // Simulate API call to /api/news
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const mockNewsData = {
        articles: [
          {
            source: 'Bloomberg',
            title: 'Global Markets Rally on Economic Data',
            summary: 'International markets show positive trends...',
            time: '2 hours ago',
            category: 'finance'
          },
          {
            source: 'CNN',
            title: 'Breaking: International Relations Update',
            summary: 'Major diplomatic developments...',
            time: '4 hours ago',
            category: 'politics'
          },
          {
            source: 'Al Jazeera',
            title: 'Middle East Economic Forum Highlights',
            summary: 'Key discussions on regional economy...',
            time: '6 hours ago',
            category: 'economics'
          }
        ],
        total_sources: 15,
        articles_today: 247,
        last_updated: new Date().toISOString()
      }
      
      const response = await fetch('/api/news')
      if (!response.ok) {
        throw new Error('Network response was not ok')
      }
      const newsData = await response.json()
      setData(newsData)
    } catch (error) {
      console.error('Error fetching news data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return { data, isLoading, fetchNewsData }
}
