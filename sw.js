// Mode hors ligne minimal : réseau d'abord, copie en cache si pas de connexion.
var C = "vi-v2";
self.addEventListener("install", function (e) { self.skipWaiting(); });
self.addEventListener("activate", function (e) { e.waitUntil(self.clients.claim()); });
self.addEventListener("fetch", function (e) {
  var r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin) return;
  e.respondWith(fetch(r).then(function (res) {
    if (res.ok) { var c = res.clone(); caches.open(C).then(function (k) { k.put(r, c); }); }
    return res;
  }).catch(function () { return caches.match(r); }));
});

self.addEventListener("push", function (e) {
  var d = {}; try { d = e.data.json(); } catch (x) { d = { t: "VI Countdown", x: e.data ? e.data.text() : "" }; }
  e.waitUntil(self.registration.showNotification(d.t || "GTA 6", { body: d.x || "", icon: "assets/icons/icon-192.png", badge: "assets/icons/icon-192.png", tag: d.tag || "vi", renotify: true, data: { u: d.u || "https://gtavifrance.com/" } }));
});
self.addEventListener("notificationclick", function (e) {
  e.notification.close(); var u = (e.notification.data && e.notification.data.u) || "https://gtavifrance.com/";
  e.waitUntil(clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (l) { for (var i = 0; i < l.length; i++) { if ("focus" in l[i]) { l[i].navigate(u); return l[i].focus(); } } return clients.openWindow(u); }));
});
