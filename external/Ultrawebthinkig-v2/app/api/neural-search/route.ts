/**
 * Web8 Neural Search API - Real Implementation
 * API endpoint që integrohet me Neural Search Engine
 * 
 * @route GET /api/neural-search
 * @author UltraWeb Neural Team
 * @version 8.0.0-NEURAL-API
 */

import { NextRequest, NextResponse } from 'next/server';
import { neuralSearchEngine, NeuralSearchResult, NeuralContext } from '../../../backend/search/neuralSearchEngine';

// Rate limiting map (simple in-memory for demo)
const rateLimitMap = new Map<string, { count: number; resetTime: number }>();

// Rate limiting configuration
const RATE_LIMIT = {
  maxRequests: 50, // 50 requests per window
  windowMs: 15 * 60 * 1000, // 15 minutes
  maxQueryLength: 200
};

/**
 * GET /api/neural-search
 * Main Neural Search API endpoint
 */
export async function GET(request: NextRequest) {
  const startTime = Date.now();
  const clientIP = getClientIP(request);
  
  try {
    // Rate limiting check
    if (!checkRateLimit(clientIP)) {
      return NextResponse.json(
        { 
          error: 'Rate limit exceeded', 
          message: 'Too many requests. Try again later.',
          retryAfter: Math.ceil((getRateLimitReset(clientIP) - Date.now()) / 1000)
        },
        { status: 429 }
      );
    }
    
    // Extract and validate query parameters
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q') || searchParams.get('query') || '';
    const intent = searchParams.get('intent') as NeuralContext['intent'] || 'search';
    const depth = searchParams.get('depth') as NeuralContext['depth'] || 'surface';
    const format = searchParams.get('format') || 'json';
    const limit = Math.min(parseInt(searchParams.get('limit') || '20'), 50);
    
    // Query validation
    if (!query || query.trim().length < 2) {
      return NextResponse.json(
        { 
          error: 'Invalid query', 
          message: 'Query must be at least 2 characters long' 
        },
        { status: 400 }
      );
    }
    
    if (query.length > RATE_LIMIT.maxQueryLength) {
      return NextResponse.json(
        { 
          error: 'Query too long', 
          message: `Query must be less than ${RATE_LIMIT.maxQueryLength} characters` 
        },
        { status: 400 }
      );
    }
    
    // Build neural context
    const neuralContext: Partial<NeuralContext> = {
      intent,
      depth,
      userContext: {
        previousQueries: [],
        preferences: [],
        expertise: 'intermediate'
      }
    };
    
    // Perform neural search
    const searchResults = await neuralSearchEngine.searchNeural(query, neuralContext);
    
    // Limit results
    const limitedResults = searchResults.slice(0, limit);
    
    // Get search stats
    const stats = neuralSearchEngine.getSearchStats();
    
    // Calculate response time
    const responseTime = Date.now() - startTime;
    
    // Build response
    const response = {
      success: true,
      query,
      results: limitedResults,
      metadata: {
        total: limitedResults.length,
        responseTime: `${responseTime}ms`,
        intent,
        depth,
        searchStats: {
          totalQueries: stats.totalQueries,
          cacheSize: stats.cacheSize
        }
      },
      timestamp: new Date().toISOString(),
      version: '8.0.0-NEURAL'
    };
    
    // Handle different response formats
    if (format === 'minimal') {
      return NextResponse.json({
        success: true,
        results: limitedResults.map((r: NeuralSearchResult) => ({
          title: r.title,
          url: r.url,
          description: r.description
        }))
      });
    }
    
    if (format === 'urls') {
      return NextResponse.json({
        success: true,
        urls: limitedResults.map((r: NeuralSearchResult) => r.url)
      });
    }
    
    // Add CORS headers
    const responseHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'X-Response-Time': `${responseTime}ms`,
      'X-Search-Results': limitedResults.length.toString(),
      'X-Neural-Version': '8.0.0'
    };
    
    return NextResponse.json(response, { headers: responseHeaders });
    
  } catch (error) {
    console.error('❌ Neural API Error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Neural search failed',
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        query: request.url.includes('q=') ? new URL(request.url).searchParams.get('q') : null,
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

/**
 * POST /api/neural-search
 * Advanced neural search with complex queries
 */
export async function POST(request: NextRequest) {
  const startTime = Date.now();
  const clientIP = getClientIP(request);
  
  try {
    // Rate limiting
    if (!checkRateLimit(clientIP)) {
      return NextResponse.json(
        { error: 'Rate limit exceeded' },
        { status: 429 }
      );
    }
    
    const body = await request.json();
    const { query, context, options } = body;
    
    if (!query || query.trim().length < 2) {
      return NextResponse.json(
        { error: 'Invalid query' },
        { status: 400 }
      );
    }
    
    // Advanced neural search with full context
    const searchResults = await neuralSearchEngine.searchNeural(query, context);
    
    const responseTime = Date.now() - startTime;
    
    return NextResponse.json({
      success: true,
      query,
      results: searchResults.slice(0, options?.limit || 20),
      metadata: {
        responseTime: `${responseTime}ms`,
        searchContext: context,
        options
      },
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ Neural API POST Error:', error);
    
    return NextResponse.json(
      {
        success: false,
        error: 'Advanced neural search failed',
        message: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

/**
 * GET /api/neural-search/suggestions
 */
export async function suggestions(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q') || '';
    
    if (query.length < 2) {
      return NextResponse.json({ suggestions: [] });
    }
    
    const suggestions = await neuralSearchEngine.searchSuggestions(query);
    
    return NextResponse.json({
      success: true,
      query,
      suggestions,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Suggestions failed' },
      { status: 500 }
    );
  }
}

/**
 * DELETE /api/neural-search/cache
 */
export async function DELETE(request: NextRequest) {
  try {
    neuralSearchEngine.clearNeuralCache();
    neuralSearchEngine.clearQueryHistory();
    
    return NextResponse.json({
      success: true,
      message: 'Neural cache and history cleared',
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Cache clear failed' },
      { status: 500 }
    );
  }
}

/**
 * OPTIONS /api/neural-search
 * CORS preflight
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      'Access-Control-Max-Age': '86400'
    }
  });
}

// Utility functions

function getClientIP(request: NextRequest): string {
  const forwarded = request.headers.get('x-forwarded-for');
  const realIP = request.headers.get('x-real-ip');
  const remoteAddr = request.headers.get('remote-addr');
  
  if (forwarded) {
    return forwarded.split(',')[0].trim();
  }
  
  return realIP || remoteAddr || 'unknown';
}

function checkRateLimit(clientIP: string): boolean {
  const now = Date.now();
  const limit = rateLimitMap.get(clientIP);
  
  if (!limit || now > limit.resetTime) {
    // Reset or create new limit
    rateLimitMap.set(clientIP, {
      count: 1,
      resetTime: now + RATE_LIMIT.windowMs
    });
    return true;
  }
  
  if (limit.count >= RATE_LIMIT.maxRequests) {
    return false;
  }
  
  limit.count++;
  return true;
}

function getRateLimitReset(clientIP: string): number {
  const limit = rateLimitMap.get(clientIP);
  return limit?.resetTime || Date.now();
}

// Export for use in other files
export { neuralSearchEngine };
