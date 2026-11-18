/* Hub soluce GTA 6 : progression (localStorage, try/catch), trophées, carte Leaflet, collectibles, missions.
   Données : data/trophees.json, data/carte.json, data/soluce/gta6.json. */
(function () {
  var CLE = "gtavif-soluce-v1";
  function lit() { try { var s = JSON.parse(localStorage.getItem(CLE) || "{}"); return { t: s.t || {}, c: s.c || {}, p: s.p || {}, o: s.o || {} }; } catch (e) { return { t: {}, c: {}, p: {}, o: {} }; } }
  var S = lit();
  function sauve() { try { localStorage.setItem(CLE, JSON.stringify(S)); } catch (e) {} }
  function tr(k, d) { var v = window.T ? T(k) : ""; return v || d || ""; }
  function langue() { return window.LANG || document.documentElement.getAttribute("data-l") || "fr"; }
  function txt(o, base) { var l = langue(); return o[(base || "") + (l === "fr" ? "fr" : "en")] || o[(base || "") + "en"] || o[(base || "") + "fr"] || ""; }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  var R = window.ROOT || "";
  var page = document.body.getAttribute("data-sl");

  /* ---------- TROPHÉES : la liste est déjà dans la page (rendue par tools/soluce.py) ---------- */
  function trophees() {
    var items = [].slice.call(document.querySelectorAll(".tp"));
    var filtre = "tout", voirSpoil = !!S.o.spoil, cacheFaits = !!S.o.faits;
    var pts = { platine: 300, or: 90, argent: 30, bronze: 15 };
    function maj() {
      var n = 0, p = 0, tot = 0;
      items.forEach(function (li) {
        var id = li.getAttribute("data-id"), fait = !!S.t[id], cat = li.getAttribute("data-cat"), spoil = li.classList.contains("spoil");
        li.classList.toggle("fait", fait);
        li.querySelector("input[type=checkbox]").checked = fait;
        var g = li.getAttribute("data-grade"); tot += pts[g] || 0; if (fait) { n++; p += pts[g] || 0; }
        li.hidden = (filtre !== "tout" && cat !== filtre) || (spoil && !voirSpoil) || (cacheFaits && fait);
        var c = li.querySelector(".cpt input"); if (c && document.activeElement !== c) c.value = S.c[id] || 0;
      });
      var b = document.getElementById("tp-n"); if (b) b.textContent = n + "/" + items.length;
      var q = document.getElementById("tp-pts"); if (q) q.textContent = p + "/" + tot + " pts";
      var j = document.getElementById("tp-jauge"); if (j) j.style.width = (n / items.length * 100).toFixed(1) + "%";
      var nb = document.getElementById("tp-spoil-n"); if (nb) nb.hidden = voirSpoil;
    }
    items.forEach(function (li) {
      var id = li.getAttribute("data-id"), max = +li.getAttribute("data-max") || 0;
      li.querySelector("input[type=checkbox]").addEventListener("change", function () { if (this.checked) S.t[id] = 1; else delete S.t[id]; sauve(); maj(); });
      var c = li.querySelector(".cpt input");
      if (c) {
        function pose(v) { v = Math.max(0, Math.min(max, parseInt(v, 10) || 0)); S.c[id] = v; if (v >= max) S.t[id] = 1; sauve(); maj(); }
        c.addEventListener("change", function () { pose(c.value); });
        li.querySelector(".moins").addEventListener("click", function () { pose((S.c[id] || 0) - 1); });
        li.querySelector(".plus").addEventListener("click", function () { pose((S.c[id] || 0) + 1); });
      }
    });
    [].forEach.call(document.querySelectorAll("[data-filtre]"), function (b) {
      b.addEventListener("click", function () {
        filtre = b.getAttribute("data-filtre");
        [].forEach.call(document.querySelectorAll("[data-filtre]"), function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
        maj();
      });
    });
    var sp = document.getElementById("tp-spoil"); if (sp) { sp.checked = voirSpoil; sp.addEventListener("change", function () { voirSpoil = S.o.spoil = sp.checked; sauve(); maj(); }); }
    var cf = document.getElementById("tp-faits"); if (cf) { cf.checked = cacheFaits; cf.addEventListener("change", function () { cacheFaits = S.o.faits = cf.checked; sauve(); maj(); }); }
    var rz = document.getElementById("tp-raz"); if (rz) rz.addEventListener("click", function () { if (confirm(tr("sl_raz_ok", "Remettre la progression à zéro ?"))) { S.t = {}; S.c = {}; sauve(); maj(); } });
    maj();
  }

  /* ---------- Points (carte + collectibles) ---------- */
  var RN = {};
  function popup(p, C, map) {
    var c = C[p.couche] || {}, ok = p.statut === "confirme";
    var src = (p.sources || []).map(function (u, i) { return '<a href="' + esc(u) + '" target="_blank" rel="noopener nofollow">' + tr("sl_source", "Source") + " " + (i + 1) + "</a>"; }).join(" · ");
    return "<b>" + esc(txt(p) || p.id) + "</b><br><small>" + esc(txt(c)) + (p.region ? " · " + esc(RN[p.region] || p.region) : "") + "</small><br>" +
      '<span class="ct-statut ' + (ok ? "ok" : "ko") + '">' + esc(ok ? tr("sl_conf", "Confirmé") : tr("sl_aconf", "À confirmer")) + "</span>" +
      (p.approx ? '<br><small class="ct-approx">' + esc(tr("sl_approx", "Position approximative sur le schéma : repère décrit ci-dessous.")) + "</small>" : "") + (txt(p, "note_") ? "<br>" + esc(txt(p, "note_")) : "") + (src ? "<br>" + src : "") +
      '<br><button type="button" class="ct-btn" data-pt="' + esc(p.id) + '">' + esc(S.p[p.id] ? tr("sl_trouve_non", "Pas encore trouvé") : tr("sl_trouve", "Trouvé ✓")) + "</button>";
  }
  function compteCouche(D, id) { var n = 0, t = 0; D.points.forEach(function (p) { if (p.couche === id) { t++; if (S.p[p.id]) n++; } }); return [n, t]; }

  function carte() {
    var el = document.getElementById("carte");
    if (!el || !window.L) { if (el) el.innerHTML = '<p class="cl-vide" style="padding:20px">' + esc(tr("sl_err", "La carte n'a pas pu se charger.")) + "</p>"; return; }
    fetch("data/carte.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (D) {
      var C = {}; D.couches.forEach(function (c) { C[c.id] = c; }); D.regions.forEach(function (g) { RN[g.id] = g.nom; });
      var H = 1000, map = L.map(el, { crs: L.CRS.Simple, minZoom: -1.2, maxZoom: 3, zoomSnap: 0.25, attributionControl: true, maxBoundsViscosity: .8 });
      var B = [[0, 0], [H, H]];
      L.imageOverlay(R + D.fond, B, { alt: "Leonida" }).addTo(map);
      map.setMaxBounds([[-150, -150], [H + 150, H + 150]]);
      map.fitBounds(B);
      map.attributionControl.setPrefix(false).addAttribution(esc(tr("sl_attr", "Schéma GTAVIFRANCE, non officiel")));
      function ll(x, y) { return [H - y, x]; }
      D.regions.forEach(function (g) {
        L.polygon(g.poly.map(function (p) { return ll(p[0], p[1]); }), { color: "#f2e8d5", weight: 1, opacity: .35, dashArray: "4 6", fillColor: "#ff3b7a", fillOpacity: .04 }).addTo(map)
          .bindTooltip(g.nom, { sticky: true });
        L.marker(ll(g.centre[0], g.centre[1]), { icon: L.divIcon({ className: "ct-region", html: esc(g.nom), iconSize: null }), interactive: false, keyboard: false }).addTo(map);
      });
      var groupes = {}, marqueurs = {}, cacheFaits = !!S.o.cfaits;
      D.couches.forEach(function (c) { groupes[c.id] = L.layerGroup().addTo(map); });
      function dessine() {
        Object.keys(groupes).forEach(function (k) { groupes[k].clearLayers(); });
        D.points.forEach(function (p) {
          if (p.x == null || p.y == null || !groupes[p.couche]) return;
          if (cacheFaits && S.p[p.id]) return;
          var c = C[p.couche], m = c.icone ?
            L.marker(ll(p.x, p.y), { icon: L.divIcon({ className: "ct-ico" + (p.statut === "confirme" ? "" : " ko") + (S.p[p.id] ? " fait" : ""), html: '<img src="' + R + c.icone + '" alt="" width="28" height="28">', iconSize: [34, 34], iconAnchor: [17, 17], popupAnchor: [0, -14] }), title: txt(p) || p.id }) :
            L.circleMarker(ll(p.x, p.y), { radius: 8, color: "#16111d", weight: 2, fillColor: c.couleur, fillOpacity: S.p[p.id] ? .35 : 1, dashArray: p.statut === "confirme" ? null : "3 3" });
          m.bindPopup(function () { return popup(p, C, map); });
          m.addTo(groupes[p.couche]); marqueurs[p.id] = m;
        });
      }
      var pan = document.getElementById("ct-couches");
      function panneau() {
        pan.innerHTML = D.couches.map(function (c) {
          var k = compteCouche(D, c.id), off = S.o["off_" + c.id];
          return '<label class="ct-couche"><input type="checkbox" data-c="' + c.id + '"' + (off ? "" : " checked") + '>' + (c.icone ? '<img class="ct-pti" src="' + R + c.icone + '" alt="" width="22" height="22">' : '<span class="ct-pt" style="background:' + c.couleur + '"></span>') + '<span>' + esc(txt(c)) + "</span><small>" + k[0] + "/" + (k[1] || 0) + (c.total ? " · " + c.total : "") + "</small></label>";
        }).join("");
        [].forEach.call(pan.querySelectorAll("input"), function (i) {
          var id = i.getAttribute("data-c");
          if (!i.checked) map.removeLayer(groupes[id]);
          i.addEventListener("change", function () { if (i.checked) { groupes[id].addTo(map); delete S.o["off_" + id]; } else { map.removeLayer(groupes[id]); S.o["off_" + id] = 1; } sauve(); });
        });
        var e = document.getElementById("ct-etat");
        if (e) e.textContent = D.points.length ? D.points.length + " " + tr("sl_pts_ok", "points placés sur la carte") : tr("sl_pts_vide", "Les emplacements sont ajoutés dès qu'ils sont vérifiés (2 sources concordantes ou source officielle).");
      }
      dessine(); panneau();
      var cf = document.getElementById("ct-faits"); if (cf) { cf.checked = cacheFaits; cf.addEventListener("change", function () { cacheFaits = S.o.cfaits = cf.checked; sauve(); dessine(); }); }
      var tout = document.getElementById("ct-tout"); if (tout) tout.addEventListener("click", function () { [].forEach.call(pan.querySelectorAll("input"), function (i) { if (!i.checked) { i.checked = true; i.dispatchEvent(new Event("change")); } }); });
      var rien = document.getElementById("ct-rien"); if (rien) rien.addEventListener("click", function () { [].forEach.call(pan.querySelectorAll("input"), function (i) { if (i.checked) { i.checked = false; i.dispatchEvent(new Event("change")); } }); });
      el.addEventListener("click", function (ev) {
        var b = ev.target.closest && ev.target.closest(".ct-btn"); if (!b) return;
        var id = b.getAttribute("data-pt"); if (S.p[id]) delete S.p[id]; else S.p[id] = 1; sauve(); map.closePopup(); dessine(); panneau();
      });
      /* liens profonds : #p=<id> ouvre un point, #c=<couche> n'affiche qu'une couche */
      var h = location.hash.slice(1).split("="), hp = h[0] === "p" ? decodeURIComponent(h[1] || "") : "", hc = h[0] === "c" ? decodeURIComponent(h[1] || "") : "";
      if (hc && groupes[hc]) [].forEach.call(pan.querySelectorAll("input"), function (i) { var on = i.getAttribute("data-c") === hc; if (i.checked !== on) { i.checked = on; i.dispatchEvent(new Event("change")); } });
      if (hp && marqueurs[hp]) { map.setView(marqueurs[hp].getLatLng(), 1.5); marqueurs[hp].openPopup(); }
      document.addEventListener("langchange", function () { panneau(); });
    }).catch(function () { el.innerHTML = '<p class="cl-vide" style="padding:20px">' + esc(tr("sl_err", "La carte n'a pas pu se charger.")) + "</p>"; });
  }

  /* ---------- COLLECTIBLES : listes par couche, cochables ---------- */
  function collectibles() {
    fetch("data/carte.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (D) {
      function rend() {
        D.couches.forEach(function (c) {
          var ul = document.getElementById("cl-" + c.id); if (!ul) return;
          var pts = D.points.filter(function (p) { return p.couche === c.id; });
          var k = compteCouche(D, c.id), n = document.getElementById("cln-" + c.id);
          if (n) n.textContent = k[0] + "/" + (c.total || k[1] || "?");
          ul.innerHTML = pts.length ? pts.map(function (p) {
            return '<li><input type="checkbox" data-pt="' + esc(p.id) + '"' + (S.p[p.id] ? " checked" : "") + '><div><b>' + esc(txt(p) || p.id) + "</b>" + (p.region ? " <small>· " + esc(p.region) + "</small>" : "") +
              (txt(p, "note_") ? "<br><small>" + esc(txt(p, "note_")) + "</small>" : "") + "<br><small>" + (p.statut === "confirme" ? esc(tr("sl_conf", "Confirmé")) : esc(tr("sl_aconf", "À confirmer"))) +
              (p.x != null ? ' · <a href="carte.html#p=' + encodeURIComponent(p.id) + '">' + esc(tr("sl_voir", "Voir sur la carte")) + "</a>" : "") + "</small></div></li>";
          }).join("") : '<li class="cl-vide">' + esc(tr("sl_pts_vide", "Les emplacements sont ajoutés dès qu'ils sont vérifiés (2 sources concordantes ou source officielle).")) + "</li>";
        });
        [].forEach.call(document.querySelectorAll(".cl-pts input"), function (i) {
          i.addEventListener("change", function () { var id = i.getAttribute("data-pt"); if (i.checked) S.p[id] = 1; else delete S.p[id]; sauve(); rend(); });
        });
      }
      rend(); document.addEventListener("langchange", rend);
    }).catch(function () {});
  }

  /* ---------- MISSIONS : spoilers masqués par défaut ---------- */
  function missions() {
    var b = document.getElementById("ms-spoil"), z = document.getElementById("ms-histoire");
    if (b && z) { b.checked = !!S.o.mspoil; z.hidden = !b.checked; b.addEventListener("change", function () { z.hidden = !b.checked; S.o.mspoil = b.checked; sauve(); }); }
    [].forEach.call(document.querySelectorAll("[data-ms]"), function (i) {
      var id = i.getAttribute("data-ms"); i.checked = !!S.t["ms:" + id];
      i.addEventListener("change", function () { if (i.checked) S.t["ms:" + id] = 1; else delete S.t["ms:" + id]; sauve(); });
    });
  }

  if (page === "trophees") trophees();
  else if (page === "carte") carte();
  else if (page === "collectibles") collectibles();
  else if (page === "missions") missions();
})();
