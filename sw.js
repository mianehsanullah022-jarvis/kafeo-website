// KAFEO offline helper: keeps the site opening fast and works on weak signal.
const CACHE = "kafeo-v3-15";
const CORE = ["./", "./index.html", "./manifest.json", "./icons/icon-192.png", "./icons/icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const req = e.request; const url = new URL(req.url);
  if (req.method !== "GET" || url.origin !== location.origin) return; // orders, emails and maps always go to the network
  if (req.mode === "navigate") {
    const home = /\/(index\.html)?$/.test(url.pathname); // only the real home page is cached (never preview.html)
    e.respondWith(fetch(req).then(r => { if (home) { const copy = r.clone(); caches.open(CACHE).then(c => c.put("./index.html", copy)); } return r; }).catch(() => caches.match(home ? "./index.html" : req)));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return r; })));
});
