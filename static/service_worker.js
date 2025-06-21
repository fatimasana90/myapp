const CACHE_NAME = 'beralin-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/images/icon.png',
  '/static/images/icon-large.png',
  '/static/manifest.json'
];


// نصب Service Worker و کش کردن فایل‌های اولیه
self.addEventListener('install', (event) => {
  self.skipWaiting(); // نصب سریع
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// فعال‌سازی و پاک کردن کش‌های قدیمی
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    )
  );
  self.clients.claim(); // فعال‌سازی فوری در تمام تب‌ها
});

// هندل درخواست‌ها
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request).then((networkResponse) => {
        return caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, networkResponse.clone());
          return networkResponse;
        });
      }).catch(() => cachedResponse); // fallback
      return cachedResponse || fetchPromise;
    })
  );
});
