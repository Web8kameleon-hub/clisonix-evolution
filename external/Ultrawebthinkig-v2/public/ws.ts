/**
 * UltraWeb Service Worker - Ultra Speed Caching
 * Advanced caching and performance optimization
 * 
 * @author Ledjan Ahmati
 * @version 8.0.0-WS-ULTRA
 * @license MIT
 */

// @ts-nocheck
/* eslint-disable */

const CACHE_NAME_WS = 'ultraweb-cache-v8.0.0';
const STATIC_CACHE_WS = 'ultraweb-static-v8.0.0';
const DYNAMIC_CACHE_WS = 'ultraweb-dynamic-v8.0.0';

// Critical resources to cache immediately
const CRITICAL_RESOURCES = [
  '/',
  '/ultra-speed',
  '/web-search-demo',
  '/overview',
  '/agi-demo',
  '/_next/static/css/',
  '/_next/static/js/',
  '/favicon.ico'
];

// Cache strategies
const CACHE_STRATEGIES = {
  CACHE_FIRST: 'cache-first',
  NETWORK_FIRST: 'network-first',
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate'
};

// Install event - cache critical resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE_WS)
      .then(cache => {
        return cache.addAll(CRITICAL_RESOURCES);
      })
      .then(() => {
        return self.skipWaiting();
      })
  );
});

// Activate event - clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => {
              return cacheName !== STATIC_CACHE_WS && 
                     cacheName !== DYNAMIC_CACHE_WS &&
                     cacheName !== CACHE_NAME_WS;
            })
            .map(cacheName => {
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        return self.clients.claim();
      })
  );
});

// Fetch event - ultra-fast response strategy
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip external requests
  if (url.origin !== location.origin) {
    return;
  }
  
  event.respondWith(
    handleRequest(request)
  );
});

// Ultra-fast request handler
async function handleRequest(request) {
  const url = new URL(request.url);
  const path = url.pathname;
  
  try {
    // Strategy 1: Static resources (CSS, JS, images) - Cache First
    if (isStaticResource(path)) {
      return await cacheFirst(request, STATIC_CACHE_WS);
    }
    
    // Strategy 2: API calls - Network First
    if (isAPICall(path)) {
      return await networkFirst(request, DYNAMIC_CACHE_WS);
    }
    
    // Strategy 3: Pages - Stale While Revalidate
    return await staleWhileRevalidate(request, DYNAMIC_CACHE_WS);
    
  } catch (error) {
    console.error('Fetch failed:', error);
    
    // Fallback to cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Ultimate fallback
    return new Response('Offline - UltraWeb', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// Cache First Strategy (for static resources)
async function cacheFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    // Return cached version immediately
    return cachedResponse;
  }
  
  // Fetch and cache if not found
  const networkResponse = await fetch(request);
  if (networkResponse.ok) {
    cache.put(request, networkResponse.clone());
  }
  
  return networkResponse;
}

// Network First Strategy (for API calls)
async function networkFirst(request, cacheName) {
  const cache = await caches.open(cacheName);
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    // Fallback to cache
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Stale While Revalidate Strategy (for pages)
async function staleWhileRevalidate(request, cacheName) {
  const cache = await caches.open(cacheName);
  const cachedResponse = await cache.match(request);
  
  // Always try to fetch in background
  const fetchPromise = fetch(request)
    .then(networkResponse => {
      if (networkResponse.ok) {
        cache.put(request, networkResponse.clone());
      }
      return networkResponse;
    })
    .catch(() => null);
  
  // Return cached version immediately if available
  if (cachedResponse) {
    return cachedResponse;
  }
  
  // Wait for network if no cache
  return await fetchPromise;
}

// Helper functions
function isStaticResource(path) {
  return /\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$/i.test(path) ||
         path.startsWith('/_next/static/');
}

function isAPICall(path) {
  return path.startsWith('/api/') || 
         path.includes('/search') ||
         path.includes('/data');
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(
      syncData()
    );
  }
});

async function syncData() {
  // Sync logic would go here
}

// Push notifications
self.addEventListener('push', (event) => {
  if (!event.data) return;
  
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/icon-192x192.png',
    badge: '/icon-72x72.png',
    tag: 'ultraweb-notification',
    renotify: true,
    actions: [
      {
        action: 'open',
        title: 'Open UltraWeb'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Message handling
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({
      version: '8.0.0-ULTRA',
      cache: CACHE_NAME_WS
    });
  }
});

