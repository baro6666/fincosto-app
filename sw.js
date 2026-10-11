// fincosto — en sade service worker.
// Sadece kabuk dosyalarını (ikon, sayfa) önbelleğe alır; uygulama verisi her zaman canlı gelir.
var SURUM = 'fincosto-kabuk-v2';
var DOSYALAR = ['./', 'index.html', 'manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'apple-touch-icon.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(SURUM).then(function (c) { return c.addAll(DOSYALAR); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (ks) {
    return Promise.all(ks.filter(function (k) { return k !== SURUM; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

// Kendi kabuk dosyalarımız: önce ağ, ağ yoksa önbellek. Diğer her şey (Apps Script) dokunulmadan geçer.
self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET' || new URL(e.request.url).origin !== self.location.origin) return;
  e.respondWith(fetch(e.request).catch(function () {
    return caches.match(e.request, { ignoreSearch: true });
  }));
});
