/**
 * EuroWeb Service Worker - TypeScript Implementation
 * Industrial Grade PWA Architecture
 * 
 * @author Ledjan Ahmati (100% Owner)
 * @contact dealsjona@gmail.com
 * @version 8.0.0 Industrial
 * @license MIT
 */

/// <reference lib="webworker" />

// Service Worker Global Scope
const sw = self as unknown as ServiceWorkerGlobalScope;

// Cache configuration
const CACHE_NAME = 'euroweb-v8.0.0';
const STATIC_CACHE = 'euroweb-static-v8.0.0';
const DYNAMIC_CACHE = 'euroweb-dynamic-v8.0.0';
const AGI_CACHE = 'euroweb-agi-v8.0.0';

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/favicon.ico',
  '/_next/static/css/app/layout.css',
  '/_next/static/css/app/globals.css'
];

// AGI API endpoints to cache
const AGI_ENDPOINTS = [
  '/api/agi-core',
  '/api/agi-med',
  '/api/agi-office',
  '/api/agi-el',
  '/api/agi-eco'
];

// Install event - cache static assets
sw.addEventListener('install', (event) => {
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE).then((cache) => {
        return cache.addAll(STATIC_ASSETS);
      }),
      
      // Initialize AGI cache
      caches.open(AGI_CACHE).then((cache) => {
        return cache.addAll([]);
      })
    ])
  );

  // Force immediate activation
  sw.skipWaiting();
});

// Activate event - clean old caches
sw.addEventListener('activate', (event) => {
  event.waitUntil(
    Promise.all([
      // Clean old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (
              cacheName !== CACHE_NAME &&
              cacheName !== STATIC_CACHE &&
              cacheName !== DYNAMIC_CACHE &&
              cacheName !== AGI_CACHE
            ) {
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Take control of all clients
      sw.clients.claim()
    ])
  );
});

// Fetch event - handle requests with AGI-optimized caching
sw.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Handle different types of requests
  if (url.pathname.startsWith('/api/agi')) {
    // AGI API requests - cache with network-first strategy
    event.respondWith(handleAGIRequest(request));
  } else if (url.pathname.startsWith('/_next/static/')) {
    // Static Next.js assets - cache-first strategy
    event.respondWith(handleStaticAssets(request));
  } else if (url.pathname === '/' || url.pathname.startsWith('/agi')) {
    // App routes - network-first with offline fallback
    event.respondWith(handleAppRoutes(request));
  } else {
    // Default handling
    event.respondWith(handleDefault(request));
  }
});

// AGI request handler - optimized for AI responses
async function handleAGIRequest(request: Request): Promise<Response> {
  const cache = await caches.open(AGI_CACHE);
  
  try {
    // Try network first for fresh AGI data
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful AGI responses
      const responseClone = networkResponse.clone();
      await cache.put(request, responseClone);
      
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    // Fallback to cache for offline AGI functionality
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline AGI response
    return new Response(
      JSON.stringify({
        error: 'AGI service temporarily offline',
        offline: true,
        timestamp: new Date().toISOString()
      }),
      {
        status: 503,
        headers: {
          'Content-Type': 'application/json',
          'X-EuroWeb-Offline': 'true'
        }
      }
    );
  }
}

// Static assets handler - cache-first strategy
async function handleStaticAssets(request: Request): Promise<Response> {
  const cache = await caches.open(STATIC_CACHE);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      await cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    throw error;
  }
}

// App routes handler - network-first with offline page
async function handleAppRoutes(request: Request): Promise<Response> {
  const cache = await caches.open(DYNAMIC_CACHE);
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      await cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for app routes
    return new Response(`
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EuroWeb - Offline</title>
        <style>
          body {
            font-family: Inter, sans-serif;
            background: linear-gradient(135deg, #0f1419 0%, #1a1d29 25%, #2d2a45 50%, #1e2a4a 75%, #243447 100%);
            color: #f8fafc;
            margin: 0;
            padding: 40px;
            text-align: center;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
          }
          .offline-container {
            max-width: 500px;
          }
          h1 {
            font-size: 48px;
            background: linear-gradient(45deg, #d4af37, #f7e08b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
          }
          p {
            font-size: 18px;
            color: #cbd5e1;
            line-height: 1.6;
          }
          .retry-btn {
            background: linear-gradient(45deg, #d4af37, #f7e08b);
            border: none;
            border-radius: 12px;
            color: #000;
            padding: 16px 32px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 24px;
          }
        </style>
      </head>
      <body>
        <div class="offline-container">
          <h1>🌐 EuroWeb</h1>
          <p>You're currently offline. EuroWeb AGI systems are cached and available for basic operations.</p>
          <button class="retry-btn" onclick="window.location.reload()">
            🔄 Try Again
          </button>
        </div>
      </body>
      </html>
    `, {
      status: 200,
      headers: {
        'Content-Type': 'text/html',
        'X-EuroWeb-Offline': 'true'
      }
    });
  }
}

// Default request handler
async function handleDefault(request: Request): Promise<Response> {
  try {
    return await fetch(request);
  } catch (error) {
    throw error;
  }
}

// Background sync for AGI data
sw.addEventListener('sync', (event: unknown) => {
  if (event.tag === 'agi-sync') {
    event.waitUntil(syncAGIData());
  }
});

// Sync AGI data in background
async function syncAGIData(): Promise<void> {
  try {
    const cache = await caches.open(AGI_CACHE);
    
    // Sync AGI endpoints
    for (const endpoint of AGI_ENDPOINTS) {
      try {
        const response = await fetch(endpoint);
        if (response.ok) {
          await cache.put(endpoint, response.clone());
          }
      } catch (error) {
        }
    }
  } catch (error) {
    }
}

// Push notification handler for AGI alerts
sw.addEventListener('push', (event: unknown) => {
  const options = {
    body: event.data?.text() || 'EuroWeb AGI notification',
    icon: '/favicon.ico',
    badge: '/favicon.ico',
    data: {
      url: '/',
      timestamp: Date.now()
    },
    actions: [
      {
        action: 'open',
        title: 'Open EuroWeb'
      },
      {
        action: 'close',
        title: 'Dismiss'
      }
    ]
  };

  event.waitUntil(
    sw.registration.showNotification('EuroWeb AGI', options)
  );
});

// Notification click handler
sw.addEventListener('notificationclick', (event: unknown) => {
  event.notification.close();

  if (event.action === 'open' || !event.action) {
    event.waitUntil(
      sw.clients.openWindow('/')
    );
  }
});

