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
    var filtre = "tout", rang = "", manq = false, voirSpoil = !!S.o.spoil, cacheFaits = !!S.o.faits, rev = S.o.rev || (S.o.rev = {});
    var pts = { platine: 300, or: 90, argent: 30, bronze: 15 };
    function maj() {
      var n = 0, p = 0, tot = 0;
      items.forEach(function (li) {
        var id = li.getAttribute("data-id"), fait = !!S.t[id], cat = li.getAttribute("data-cat"), spoil = li.classList.contains("spoil");
        li.classList.toggle("fait", fait);
        li.querySelector("input[type=checkbox]").checked = fait;
        var g = li.getAttribute("data-grade"); tot += pts[g] || 0; if (fait) { n++; p += pts[g] || 0; }
        li.hidden = (filtre !== "tout" && cat !== filtre) || (rang && g !== rang) || (manq && !li.hasAttribute("data-manq")) || (cacheFaits && fait);
        li.classList.toggle("flou", spoil && !voirSpoil && !rev[id]);
        var c = li.querySelector(".cpt input"); if (c && document.activeElement !== c) c.value = S.c[id] || 0;
      });
      var b = document.getElementById("tp-n"); if (b) b.textContent = n + "/" + items.length;
      var q = document.getElementById("tp-pts"); if (q) q.textContent = p + "/" + tot + " pts";
      var j = document.getElementById("tp-jauge"); if (j) j.style.width = (n / items.length * 100).toFixed(1) + "%";
      var nb = document.getElementById("tp-spoil-n"); if (nb) nb.hidden = voirSpoil;
      [].forEach.call(document.querySelectorAll("[data-rang]"), function (x) { x.setAttribute("aria-pressed", x.getAttribute("data-rang") === rang ? "true" : "false"); });
      var mb = document.querySelector("[data-manqf]"); if (mb) mb.setAttribute("aria-pressed", manq ? "true" : "false");
    }
    items.forEach(function (li) {
      var id = li.getAttribute("data-id"), max = +li.getAttribute("data-max") || 0;
      li.querySelector("input[type=checkbox]").addEventListener("change", function () { if (this.checked) S.t[id] = 1; else delete S.t[id]; sauve(); maj(); });
      var rv = li.querySelector(".tp-rev"); if (rv) rv.addEventListener("click", function () { rev[id] = 1; sauve(); maj(); });
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
    [].forEach.call(document.querySelectorAll("[data-rang]"), function (x) { x.addEventListener("click", function () { var v = x.getAttribute("data-rang"); rang = rang === v ? "" : v; maj(); }); });
    var mb = document.querySelector("[data-manqf]"); if (mb) mb.addEventListener("click", function () { manq = !manq; maj(); });
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

  /* ---------- Carte officielle, refaite de zéro le 19/11/2026 (Gabriel : « reprends tout à zéro ») ----------
     Molette, pincement, double-clic, plein écran, image HD, 87 lieux officiels étiquetés selon le zoom,
     recherche, panneau (lieux, collectibles cochables, mes repères), case du quadrillage, lien partageable. */
  function carteOff(el, D, C) {
    var OW = D.fond_officiel_l || 2200, OH = D.fond_officiel_h || 3012, OB = [[0, 0], [OH, OW]], kx = OW / 1000;
    var LO = (D.lieux_officiels || []).slice().sort(function (a, b) { return a.n.localeCompare(b.n); });
    var mob = matchMedia("(max-width: 820px)").matches;
    var z = el.closest(".ct-zone"); if (z) z.classList.add("ct-seule", "cx-zone");
    el.className = "cx"; el.innerHTML =
      '<div class="cx-map"></div>' +
      '<div class="cx-haut"><div class="cx-rech"><span aria-hidden="true">⌕</span><input type="search" autocomplete="off"><ul hidden></ul></div>' +
      '<button type="button" class="cx-b cx-b-pan"></button></div>' +
      '<div class="cx-outils"><button type="button" class="cx-b cx-b-plein" aria-label="Plein écran">⛶</button><button type="button" class="cx-b cx-b-cadre" aria-label="Recadrer">⌂</button><button type="button" class="cx-b cx-b-part" aria-label="Partager">↗</button><button type="button" class="cx-b cx-b-noms on" aria-label="Noms">Aa</button></div>' +
      '<aside class="cx-pan"' + (mob ? " hidden" : "") + '><div class="cx-onglets"></div><div class="cx-corps"></div></aside>' +
      '<div class="cx-bas"></div><div class="cx-toast" hidden></div>';
    var h0 = ""; try { h0 = decodeURIComponent(location.hash.slice(1)); } catch (e) {}
    var $ = function (s) { return el.querySelector(s); };
    var mapEl = $(".cx-map"), ri = $(".cx-rech input"), ru = $(".cx-rech ul"), pan = $(".cx-pan"), corps = $(".cx-corps"), ong = $(".cx-onglets"), bas = $(".cx-bas"), toast = $(".cx-toast");
    /* V4 (20/11) : vraie carte détaillée de Leonida en tuiles (gtadb.org, CC BY 4.0), repères recalés par affine sur les 44 lieux communs */
    var CRS = L.extend({}, L.CRS.Simple, { transformation: new L.Transformation(0.052351, 42.201, -0.0536904, 202.6127) });
    var mo = L.map(mapEl, { crs: CRS, minZoom: 0, maxZoom: 9.5, zoomSnap: 0, zoomDelta: 0.5, wheelPxPerZoomLevel: 110, wheelDebounceTime: 20, scrollWheelZoom: true, doubleClickZoom: true, touchZoom: true, dragging: true, inertia: true, zoomControl: false, attributionControl: true, tap: true, bounceAtZoomLimits: false });
    L.control.zoom({ position: "bottomright", zoomInTitle: "+", zoomOutTitle: "−" }).addTo(mo);
    mo.attributionControl.setPrefix(false).addAttribution('Fond : <a href="https://gtadb.org" target="_blank" rel="noopener">gtadb.org</a> et contributeurs, CC BY 4.0');
    var RT = (window.devicePixelRatio || 1) > 1.3;
    L.tileLayer(R + "tuiles/leonida/{z}/{z},{y},{x}.jpg", { zoomOffset: RT ? -1 : -2, minNativeZoom: RT ? 1 : 2, maxNativeZoom: RT ? 7 : 8, tileSize: RT ? 128 : 256, bounds: [[-81, -156], [3140, 2402]], keepBuffer: 3, updateWhenZooming: false, className: "cx-tuiles" }).addTo(mo);
    var TERRE = [[248.9, 277.9], [2754.0, 2083.0]];
    var ZB = 0;
    /* Bâtiments gtadb.org (CC BY 4.0) : 3 600 repères au mètre près avec leur équivalent réel, visibles en zoom rapproché */
    var gB = L.layerGroup(), rB = L.canvas({ padding: .4 }), bOk = false;
    function batis() {
      var vis = mo.getZoom() >= ZB + 3.4;
      if (vis && !bOk) { bOk = true; fetch(R + "data/carte_gtadb.json").then(function (r) { return r.json(); }).then(function (G) {
        G.b.forEach(function (b) {
          var p = b[0].split(","), nom = p[0].trim() === "?" ? tr("cx_bat", "Bâtiment") : p[0].trim(), lieu = p.slice(1).join(",").trim();
          L.circleMarker([b[1], b[2]], { renderer: rB, radius: 3.5, weight: 1, color: "#0b0812", fillColor: b[4] === "enterable" ? "#3ee08f" : "#f4efe6", fillOpacity: .9 })
            .bindPopup("<b>" + esc(nom) + "</b>" + (lieu ? "<br><small>" + esc(lieu) + "</small>" : "") + (b[3] ? "<br>" + esc(tr("cx_reel", "Dans la vraie vie")) + " : " + esc(b[3]) : "") + (b[4] === "enterable" ? "<br>" + esc(tr("cx_entrer", "On peut y entrer")) : "") + '<br><small style="opacity:.6">gtadb.org</small>', { className: "cx-pop" })
            .addTo(gB);
        });
        batis();
      }).catch(function () { bOk = false; }); return; }
      if (vis && !mo.hasLayer(gB)) gB.addTo(mo); else if (!vis && mo.hasLayer(gB)) mo.removeLayer(gB);
    }
    mo.on("zoomend", function () { batis(); });
    function cadre(anim) { mo.invalidateSize(); var zf = mo.getBoundsZoom(TERRE, false); ZB = zf; mo.setMinZoom(zf - 0.6); var pw = (!mob && !pan.hidden) ? pan.offsetWidth + 24 : 0; mo.fitBounds(TERRE, { animate: !!anim, paddingTopLeft: [10, 60], paddingBottomRight: [pw, 10] }); }
    mo.setMaxBounds([[-2500, -3000], [5500, 5300]]);
    function ll(o) { return L.latLng(OH - o.y * kx, o.x * kx); }
    function caseDe(p) {
      var x = p.lng / kx, y = (OH - p.lat) / kx;
      if (x < 33 || x > 1000 || y < 22 || y > 1350) return "";
      return "ABCDEFGHIJKLM".charAt(Math.min(12, Math.floor((y - 22) / 102))) + Math.min(9, Math.floor((x - 33) / 103.75) + 1);
    }
    function info(m) { toast.textContent = m; toast.hidden = false; clearTimeout(info.t); info.t = setTimeout(function () { toast.hidden = true; }, 2200); }

    /* 87 lieux officiels : point + étiquette (étiquettes visibles dès qu'on zoome un peu) */
    var gL = L.layerGroup().addTo(mo), gH = L.layerGroup().addTo(mo), mk = {}, sel = null, selC = null;
    LO.forEach(function (o) {
      L.circleMarker(ll(o), { radius: 18, stroke: false, fillColor: "#ffd23f", fillOpacity: 0.001, className: "cx-hit" }).on("click", function () { voir(o, true); }).addTo(gH);
      var m = L.circleMarker(ll(o), { radius: 6, color: "#0b0812", weight: 2, fillColor: "#ff2e88", fillOpacity: 1, className: "cx-pt" })
        .bindTooltip(esc(o.n), { permanent: true, direction: "right", offset: [7, 0], className: "cx-lab" })
        .on("click", function () { voir(o, true); }).addTo(gL);
      mk[o.n] = m;
    });
    var NOMS = LO.map(function (o) { return o.n; }).sort(function (a, b) { return b.length - a.length; });
    function secteur(p) {
      var t = [p.en, p.note_en, p.fr, p.note_fr, p.q].join(" "), best = null, bi = 1e9;
      NOMS.forEach(function (n) { var m = new RegExp("\\b" + n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "\\b", "i").exec(t); if (m && m.index < bi) { bi = m.index; best = n; } });
      return best;
    }
    var parS = {}; D.points.forEach(function (p) { p._s = secteur(p); if (p._s) (parS[p._s] = parS[p._s] || []).push(p); });
    var gC = {}, mkC = {};
    D.couches.forEach(function (c) { gC[c.id] = L.layerGroup(); if (!S.o["cx_off_" + c.id]) gC[c.id].addTo(mo); });
    function icoC(p, i, n) {
      var c = C[p.couche] || {}, dx = 0, dy = 0;
      /* petit groupe : anneau ; gros groupe : disque compact en spirale (tournesol) */
      if (n > 1 && n <= 7) { var r0 = 13 + n * 2.4, a = i / n * 2 * Math.PI - Math.PI / 2; dx = Math.round(r0 * Math.cos(a)); dy = Math.round(r0 * Math.sin(a)); }
      else if (n > 7) { var rr = 15 * Math.sqrt(i + .5), aa = i * 2.39996; dx = Math.round(rr * Math.cos(aa)); dy = Math.round(rr * Math.sin(aa)); }
      return L.divIcon({ className: "cx-ic" + (S.p[p.id] ? " fait" : ""), html: '<i style="background:' + esc(c.couleur) + '"><img src="' + R + esc(c.icone) + '" alt=""></i>', iconSize: [26, 26], iconAnchor: [13 - dx, 13 - dy], popupAnchor: [dx, dy - 14] });
    }
    function popC(p) {
      var c = C[p.couche] || {}, o = trouve(p._s);
      var src = (p.sources || []).map(function (u, i) { return '<a href="' + esc(u) + '" target="_blank" rel="noopener nofollow">' + esc(tr("sl_source", "Source")) + " " + (i + 1) + "</a>"; }).join(" · ");
      return '<div class="cx-pop cx-pop-c"><em style="color:' + esc(c.couleur) + '">' + esc(txt(c)) + "</em><b>" + esc(txt(p) || p.id) + "</b><span>" + esc(tr("cx_secteur", "Secteur")) + " : " + esc(p._s) + (o ? " · " + esc(tr("sl_off_case", "Case")) + " " + esc(o.case) : "") + "</span>" +
        (txt(p, "note_") ? "<p>" + esc(txt(p, "note_")) + "</p>" : "") + (p.lien ? '<a class="cx-pop-t cx-pop-lien" href="' + esc(p.lien) + '">' + esc(tr("cx_mis_ouvrir", "Ouvrir la soluce")) + " →</a>" : "") + '<small class="cx-approx">' + esc(tr("cx_approx", "Icône posée sur le secteur que nomme le guide : l'emplacement exact se trouve dans ce secteur.")) + "</small>" + (src ? "<small>" + src + "</small>" : "") +
        '<button type="button" class="cx-pop-t' + (S.p[p.id] ? " fait" : "") + '" data-p="' + esc(p.id) + '">' + esc(S.p[p.id] ? tr("sl_trouve_non", "Pas encore trouvé") : tr("sl_trouve", "Trouvé ✓")) + "</button></div>";
    }
    function dessineC() {
      Object.keys(gC).forEach(function (k) { gC[k].clearLayers(); }); mkC = {};
      var gros = false;
      Object.keys(parS).forEach(function (sn) {
        var o = trouve(sn), l0 = parS[sn].filter(function (p) { return gC[p.couche] && mo.hasLayer(gC[p.couche]); }); if (!o || !l0.length) return;
        if (gros && l0.length > 1) {
          /* vue large : une bulle par secteur (nombre + couleurs des catégories), un clic zoome dessus */
          var cs = []; l0.forEach(function (p) { var c = (C[p.couche] || {}).couleur; if (c && cs.indexOf(c) < 0) cs.push(c); });
          var pas = 100 / cs.length, grad = cs.map(function (c, i) { return c + " " + (i * pas) + "% " + ((i + 1) * pas) + "%"; }).join(",");
          var tl = l0.length > 99 ? 46 : l0.length > 9 ? 40 : 34;
          L.marker(ll(o), { icon: L.divIcon({ className: "cx-bul", html: '<i style="background:conic-gradient(' + grad + ')"><b>' + l0.length + "</b></i>", iconSize: [tl, tl], iconAnchor: [tl / 2, tl / 2] }), title: sn + " · " + l0.length, riseOnHover: true })
            .on("click", function () { mo.flyTo(ll(o), Math.max(mo.getZoom() + 1.4, ZB + 1.6), { duration: .6 }); }).addTo(gC[l0[0].couche]);
          return;
        }
        l0.forEach(function (p, i) {
          if (!gC[p.couche]) return;
          mkC[p.id] = L.marker(ll(o), { icon: icoC(p, i, l0.length), riseOnHover: true, title: txt(p) || p.id, keyboard: true })
            .bindPopup(function () { return popC(p); }, { className: "cx-popup", maxWidth: 290, autoPanPaddingTopLeft: [10, 70], autoPanPaddingBottomRight: [70, 10] }).addTo(gC[p.couche]);
        });
      });
    }
    function ouvreC(id) {
      var p = null; D.points.forEach(function (q) { if (q.id === id) p = q; }); var m = mkC[id]; if (!p || !m) return;
      if (!mo.hasLayer(gC[p.couche])) { gC[p.couche].addTo(mo); delete S.o["cx_off_" + p.couche]; sauve(); }
      var zc = Math.max(mo.getZoom(), mo.getMinZoom() + 2.2);
      mo.flyTo(m.getLatLng(), zc, { duration: .6 }); mo.once("moveend", function () { m.openPopup(); });
      if (mob) { pan.hidden = true; majPanBtn(); }
    }
    function etiquettes() { el.classList.toggle("cx-labs", noms && mo.getZoom() >= mo.getMinZoom() + 1.1); }
    var noms = true;
    function popLieu(o) {
      var l0 = parS[o.n] || [];
      return '<div class="cx-pop"><b>' + esc(o.n) + "</b><span>" + esc(tr("sl_off_case", "Case")) + " " + esc(o.case) + "</span>" +
        (l0.length ? '<em class="cx-pop-h">' + esc(tr("cx_ici", "À faire ici")) + " (" + l0.length + ')</em><ul class="cx-pop-ul">' + l0.map(function (p) { var c = C[p.couche] || {}; return '<li><button type="button" data-pc="' + esc(p.id) + '"' + (S.p[p.id] ? ' class="fait"' : "") + '><i style="background:' + esc(c.couleur) + '"></i>' + esc(txt(p) || p.id) + "</button></li>"; }).join("") + "</ul>" : "") +
        '<button type="button" class="cx-pop-l" data-n="' + esc(o.n) + '">' + esc(tr("cx_lien", "Copier le lien")) + "</button></div>";
    }
    function voir(o, sansVol) {
      var p = ll(o);
      if (selC) mo.removeLayer(selC);
      selC = L.circleMarker(p, { radius: 20, color: "#ffd23f", weight: 3, fill: false, interactive: false, className: "cx-sel" }).addTo(mo);
      var zc = sansVol ? mo.getZoom() : Math.max(mo.getZoom(), mo.getMinZoom() + 2), dx = (!mob && !pan.hidden) ? (pan.offsetWidth + 66) / 2 : 0;
      var cible = dx ? mo.unproject(mo.project(p, zc).add([dx, 0]), zc) : p;
      if (!sansVol) mo.flyTo(cible, zc, { duration: .7 }); else if (dx) mo.setView(cible, zc, { animate: false });
      var pu = L.popup({ offset: [0, -6], className: "cx-popup", maxWidth: 280, autoPanPaddingTopLeft: [10, 70], autoPanPaddingBottomRight: [70, 10] }).setLatLng(p).setContent(popLieu(o)); pu._cxLieu = 1; pu.openOn(mo);
      etat("l=" + encodeURIComponent(o.n));
      if (mob) pan.hidden = true, majPanBtn();
    }

    /* recherche */
    function norm(t) { return (t || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, ""); }
    var act = -1;
    function suggere() {
      var q = norm(ri.value.trim()); act = -1;
      if (q.length < 1) { ru.hidden = true; return; }
      var r = LO.filter(function (o) { return norm(o.n).indexOf(q) >= 0; }).sort(function (a, b) { return norm(a.n).indexOf(q) - norm(b.n).indexOf(q); }).slice(0, 8);
      ru.innerHTML = r.length ? r.map(function (o) { return '<li><button type="button" data-n="' + esc(o.n) + '">' + esc(o.n) + "<small>" + esc(o.case) + "</small></button></li>"; }).join("") : '<li class="cx-vide">' + esc(tr("cx_rien", "Aucun lieu de ce nom sur la carte")) + "</li>";
      ru.hidden = false;
    }
    ri.addEventListener("input", suggere); ri.addEventListener("focus", suggere);
    ri.addEventListener("keydown", function (e) {
      var bs = ru.querySelectorAll("button");
      if (e.key === "ArrowDown" || e.key === "ArrowUp") { e.preventDefault(); act = (act + (e.key === "ArrowDown" ? 1 : -1) + bs.length) % bs.length; [].forEach.call(bs, function (b, i) { b.classList.toggle("on", i === act); }); }
      else if (e.key === "Enter") { var b = bs[act >= 0 ? act : 0]; if (b) b.click(); }
      else if (e.key === "Escape") { ru.hidden = true; ri.blur(); }
    });
    ru.addEventListener("click", function (ev) { var b = ev.target.closest("button[data-n]"); if (!b) return; var o = trouve(b.getAttribute("data-n")); if (o) { ri.value = o.n; ru.hidden = true; ri.blur(); voir(o); } });
    document.addEventListener("click", function (ev) { if (!ev.target.closest(".cx-rech")) ru.hidden = true; });
    function trouve(n) { for (var i = 0; i < LO.length; i++) if (LO[i].n === n) return LO[i]; return null; }

    /* repères perso : clic droit (ordinateur) ou appui long (mobile), ou bouton du panneau */
    var RK = "carte-reperes", MR = [], gM = L.layerGroup().addTo(mo), pose = false;
    try { MR = JSON.parse(localStorage.getItem(RK) || "[]") || []; } catch (e) { MR = []; }
    function sauveR() { try { localStorage.setItem(RK, JSON.stringify(MR)); } catch (e) {} }
    var icR = L.divIcon({ className: "cx-mon", html: "<i></i>", iconSize: [26, 34], iconAnchor: [13, 32], popupAnchor: [0, -30] });
    function dessineR() {
      gM.clearLayers();
      MR.forEach(function (m, i) {
        L.marker([m.a, m.o], { icon: icR, draggable: true, title: m.n }).addTo(gM)
          .bindPopup('<div class="cx-pop"><b>' + esc(m.n) + "</b><span>" + esc(tr("sl_off_case", "Case")) + " " + esc(caseDe(L.latLng(m.a, m.o))) + '</span><button type="button" class="cx-pop-s" data-i="' + i + '">' + esc(tr("sl_off_suppr", "Supprimer")) + "</button></div>", { className: "cx-popup" })
          .on("dragend", function (e) { var p = e.target.getLatLng(); m.a = p.lat; m.o = p.lng; sauveR(); dessineR(); });
      });
      if (onglet === "mes") rendPan();
    }
    function ajoute(p) {
      var n = window.prompt(tr("sl_off_nom", "Nom du repère (ex. carte à collectionner, planque)"), "");
      if (n === null) return;
      MR.push({ n: (n.trim() || tr("cx_repere", "Repère")).slice(0, 60), a: p.lat, o: p.lng }); sauveR(); dessineR();
      info(tr("cx_ajoute", "Repère enregistré sur cet appareil"));
    }
    mo.on("contextmenu", function (e) { ajoute(e.latlng); });
    mo.on("click", function (e) {
      if (pose) { pose = false; el.classList.remove("cx-pose"); ajoute(e.latlng); return; }
      var c = caseDe(e.latlng); if (c) L.popup({ className: "cx-popup cx-popup-case" }).setLatLng(e.latlng).setContent("<b>" + esc(tr("sl_off_case", "Case")) + " " + c + "</b>").openOn(mo);
    });
    mo.on("popupopen", function (e) {
      var r = e.popup.getElement(); if (!r) return;
      var s = r.querySelector(".cx-pop-s"); if (s) s.onclick = function () { MR.splice(+s.getAttribute("data-i"), 1); sauveR(); mo.closePopup(); dessineR(); };
      var l = r.querySelector(".cx-pop-l"); if (l) l.onclick = function () { partage(); };
      [].forEach.call(r.querySelectorAll("[data-pc]"), function (b) { b.onclick = function () { mo.closePopup(); ouvreC(b.getAttribute("data-pc")); }; });
      var tg = r.querySelector(".cx-pop-t"); if (tg) tg.onclick = function () {
        var id = tg.getAttribute("data-p"); if (S.p[id]) delete S.p[id]; else S.p[id] = 1; sauve(); dessineC(); if (onglet === "coll") rendPan();
        if (mkC[id]) mkC[id].openPopup();
      };
    });
    mo.on("popupclose", function (e) { if (selC && e.popup && e.popup._cxLieu) { mo.removeLayer(selC); selC = null; } });
    mapEl.addEventListener("mousemove", function (ev) { var c = caseDe(mo.mouseEventToLatLng(ev)); bas.textContent = c ? tr("sl_off_case", "Case") + " " + c : ""; });
    mapEl.addEventListener("mouseleave", function () { bas.textContent = ""; });

    /* panneau : Lieux / Collectibles / Mes repères */
    var onglet = "lieux", ouv = {};
    function rendOng() {
      ong.innerHTML = [["lieux", tr("cx_o_lieux", "Lieux") + " " + LO.length], ["coll", tr("cx_o_coll", "Collectibles")], ["mes", tr("sl_off_mes", "Mes repères") + (MR.length ? " " + MR.length : "")]].map(function (t) { return '<button type="button" data-o="' + t[0] + '"' + (t[0] === onglet ? ' class="on"' : "") + ">" + esc(t[1]) + "</button>"; }).join("") + (mob ? '<button type="button" class="cx-x" aria-label="Fermer">✕</button>' : "");
    }
    function rendPan() {
      rendOng();
      var h = "";
      var FAMS = [["m", "cx_f_mis", "Missions"], ["l", "cx_f_lieux", "Lieux"], ["c", "cx_f_coll", "Collections"], ["a", "cx_f_act", "Activités"]];
      function famC(c) { return c.famille || ({ garages: "l", banques: "l", bijouteries: "l", wainK: "c", cartes: "c", zones: "c" })[c.id] || "a"; }
      if (onglet === "lieux") {
        var lt = "";
        h = '<p class="cx-aide">' + esc(tr("cx_aide_l", "Les 87 noms écrits sur la carte officielle. Touchez-en un pour y aller.")) + '</p><ul class="cx-l">' + LO.map(function (o) { var l0 = o.n.charAt(0).toUpperCase(), s = l0 !== lt ? '<li class="cx-let">' + l0 + "</li>" : ""; lt = l0; return s + '<li><button type="button" data-n="' + esc(o.n) + '">' + esc(o.n) + "<small>" + esc(o.case) + "</small></button></li>"; }).join("") + "</ul>";
      } else if (onglet === "coll") {
        var tot = 0, fa = 0; D.points.forEach(function (p) { tot++; if (S.p[p.id]) fa++; });
        h = '<div class="cx-tout"><button type="button" data-tout="1">' + esc(tr("cx_tout_aff", "Tout afficher")) + '</button><button type="button" data-tout="0">' + esc(tr("cx_tout_mas", "Tout masquer")) + "</button></div>" + '<div class="cx-prog"><b>' + fa + " / " + tot + "</b> " + esc(tr("cx_trouves", "trouvés")) + '<span><i style="width:' + (tot ? Math.round(fa * 100 / tot) : 0) + '%"></i></span></div>' +
          '<p class="cx-aide">' + esc(tr("cx_aide_c", "Cochez ce que vous avez trouvé : la progression reste sur cet appareil. Les positions exactes s'afficheront sur la carte dès que deux sources de joueurs concordent.")) + "</p>" +
          FAMS.map(function (f) { var hh = D.couches.filter(function (c) { return famC(c) === f[0]; }).map(function (c) {
            var pts = D.points.filter(function (p) { return p.couche === c.id; }); if (!pts.length) return "";
            var n = pts.filter(function (p) { return S.p[p.id]; }).length;
            return '<div class="cx-c' + (ouv[c.id] ? " ouv" : "") + '"><div class="cx-c-h"><button type="button" class="cx-c-t" data-c="' + c.id + '"><i style="background:' + esc(c.couleur) + '"></i>' + esc(txt(c)) + "<small>" + n + "/" + pts.length + "</small></button>" + '<button type="button" class="cx-eye' + (S.o["cx_off_" + c.id] ? "" : " on") + '" data-v="' + c.id + '" aria-label="' + esc(tr("cx_voir", "Afficher sur la carte")) + '" title="' + esc(tr("cx_voir", "Afficher sur la carte")) + '"></button></div>' +
              (ouv[c.id] ? (txt(c, "note_") ? '<p class="cx-aide">' + esc(txt(c, "note_")) + "</p>" : "") + "<ul>" + pts.map(function (p) {
                var src = (p.sources || []).map(function (u, i) { return '<a href="' + esc(u) + '" target="_blank" rel="noopener nofollow">' + esc(tr("sl_source", "Source")) + " " + (i + 1) + "</a>"; }).join(" · ");
                return '<li><label><input type="checkbox" data-p="' + esc(p.id) + '"' + (S.p[p.id] ? " checked" : "") + "><span><b>" + esc(txt(p) || p.id) + "</b>" + (txt(p, "note_") ? "<small>" + esc(txt(p, "note_")) + "</small>" : "") + (src ? "<small>" + src + "</small>" : "") + "</span></label>" + (mkC[p.id] ? '<button type="button" class="cx-go" data-go="' + esc(p.id) + '" aria-label="' + esc(tr("cx_voir", "Afficher sur la carte")) + '">➜</button>' : "") + "</li>";
              }).join("") + "</ul>" : "") + "</div>";
          }).join(""); return hh ? '<h4 class="cx-fam">' + esc(tr(f[1], f[2])) + "</h4>" + hh : ""; }).join("");
      } else {
        h = '<button type="button" class="cx-b-pose' + (pose ? " on" : "") + '">' + esc(pose ? tr("sl_off_pose_on", "Touchez la carte à l'endroit voulu") : tr("sl_off_pose", "📍 Poser un repère")) + '</button><p class="cx-aide">' + esc(tr("cx_aide_m", "Astuce : clic droit sur ordinateur ou appui long sur mobile pour poser un repère. Faites-le glisser pour le déplacer.")) + "</p>" +
          (MR.length ? '<ul class="cx-l">' + MR.map(function (m, i) { return '<li><button type="button" data-m="' + i + '">📍 ' + esc(m.n) + "<small>" + esc(caseDe(L.latLng(m.a, m.o))) + "</small></button></li>"; }).join("") + '</ul><button type="button" class="cx-vider">' + esc(tr("sl_off_vider", "Tout effacer")) + "</button>" : "");
      }
      corps.innerHTML = h;
    }
    ong.addEventListener("click", function (ev) { var b = ev.target.closest("button"); if (!b) return; if (b.classList.contains("cx-x")) { pan.hidden = true; majPanBtn(); return; } onglet = b.getAttribute("data-o"); rendPan(); corps.scrollTop = 0; });
    corps.addEventListener("click", function (ev) {
      var b = ev.target.closest("button"); if (!b) return;
      if (b.hasAttribute("data-n")) { var o = trouve(b.getAttribute("data-n")); if (o) voir(o); }
      else if (b.hasAttribute("data-m")) { var m = MR[+b.getAttribute("data-m")]; mo.flyTo([m.a, m.o], Math.max(mo.getZoom(), mo.getMinZoom() + 2), { duration: .7 }); if (mob) { pan.hidden = true; majPanBtn(); } }
      else if (b.hasAttribute("data-go")) { ouvreC(b.getAttribute("data-go")); }
      else if (b.hasAttribute("data-tout")) { var on = b.getAttribute("data-tout") === "1"; D.couches.forEach(function (c) { if (on) { gC[c.id].addTo(mo); delete S.o["cx_off_" + c.id]; } else { mo.removeLayer(gC[c.id]); S.o["cx_off_" + c.id] = 1; } }); sauve(); dessineC(); rendPan(); }
      else if (b.hasAttribute("data-v")) { var v = b.getAttribute("data-v"); if (mo.hasLayer(gC[v])) { mo.removeLayer(gC[v]); S.o["cx_off_" + v] = 1; } else { gC[v].addTo(mo); delete S.o["cx_off_" + v]; } sauve(); dessineC(); rendPan(); }
      else if (b.hasAttribute("data-c")) { var id = b.getAttribute("data-c"); ouv[id] = !ouv[id]; rendPan(); }
      else if (b.classList.contains("cx-b-pose")) { pose = !pose; el.classList.toggle("cx-pose", pose); rendPan(); if (pose && mob) { pan.hidden = true; majPanBtn(); info(tr("sl_off_pose_on", "Touchez la carte à l'endroit voulu")); } }
      else if (b.classList.contains("cx-vider")) { if (window.confirm(tr("sl_off_vider_q", "Effacer tous vos repères ?"))) { MR = []; sauveR(); dessineR(); } }
    });
    corps.addEventListener("change", function (ev) { var i = ev.target; if (!i.hasAttribute("data-p")) return; var id = i.getAttribute("data-p"); if (i.checked) S.p[id] = 1; else delete S.p[id]; sauve(); dessineC(); rendPan(); });
    L.DomEvent.disableClickPropagation(pan); L.DomEvent.disableScrollPropagation(pan);
    [".cx-haut", ".cx-outils"].forEach(function (s) { L.DomEvent.disableClickPropagation($(s)); L.DomEvent.disableScrollPropagation($(s)); });
    var pb = $(".cx-b-pan");
    function majPanBtn() { pb.textContent = pan.hidden ? "☰ " + tr("cx_panneau", "Lieux et collectibles") : "✕"; pb.classList.toggle("on", !pan.hidden); el.classList.toggle("cx-pan-on", !pan.hidden); setTimeout(function () { mo.invalidateSize(); }, 220); }
    pb.addEventListener("click", function () { pan.hidden = !pan.hidden; majPanBtn(); });

    /* outils */
    function plein() { return document.fullscreenElement === el || document.webkitFullscreenElement === el || el.classList.contains("cx-plein"); }
    $(".cx-b-plein").addEventListener("click", function () {
      if (plein()) { if (document.fullscreenElement || document.webkitFullscreenElement) (document.exitFullscreen || document.webkitExitFullscreen).call(document); else { el.classList.remove("cx-plein"); document.documentElement.classList.remove("cx-bloque"); cadre(); } return; }
      var f = el.requestFullscreen || el.webkitRequestFullscreen;
      if (f) { try { var r = f.call(el); if (r && r.catch) r.catch(function () { el.classList.add("cx-plein"); document.documentElement.classList.add("cx-bloque"); cadre(); }); } catch (e) { el.classList.add("cx-plein"); cadre(); } }
      else { el.classList.add("cx-plein"); document.documentElement.classList.add("cx-bloque"); cadre(); }
    });
    ["fullscreenchange", "webkitfullscreenchange"].forEach(function (t) { document.addEventListener(t, function () { setTimeout(function () { cadre(); }, 120); }); });
    $(".cx-b-cadre").addEventListener("click", function () { mo.closePopup(); cadre(true); });
    $(".cx-b-noms").addEventListener("click", function () { noms = !noms; this.classList.toggle("on", noms); if (noms) gL.addTo(mo); else mo.removeLayer(gL); etiquettes(); });
    function partage() {
      var u = location.href;
      if (navigator.share && mob) { navigator.share({ title: document.title, url: u }).catch(function () {}); return; }
      try { navigator.clipboard.writeText(u).then(function () { info(tr("cx_copie", "Lien copié")); }, function () { window.prompt("", u); }); } catch (e) { window.prompt("", u); }
    }
    $(".cx-b-part").addEventListener("click", partage);

    /* lien partageable : #l=Nom ou #c=zoom,lat,lng */
    var hl = "";
    function etat(h) { hl = h; try { history.replaceState(null, "", location.pathname + location.search + "#" + h); } catch (e) {} }
    mo.on("moveend", function () { etiquettes(); if (hl.indexOf("l=") === 0 && mo._popup && mo.hasLayer(mo._popup)) return; var c = mo.getCenter(); etat("c=" + mo.getZoom().toFixed(2) + "," + Math.round(c.lat) + "," + Math.round(c.lng)); });
    var grosAv = null;
    mo.on("zoomend", function () { etiquettes(); var g = mo.getZoom() < ZB + 1.15; if (g !== grosAv) { grosAv = g; dessineC(); } });

    function textes() {
      ri.placeholder = tr("cx_rech", "Chercher un lieu : Vice Beach, Port Gellhorn…");
      $(".cx-b-plein").title = tr("cx_plein", "Plein écran"); $(".cx-b-cadre").title = tr("cx_cadre", "Toute la carte"); $(".cx-b-part").title = tr("cx_partager", "Partager cette vue"); $(".cx-b-noms").title = tr("cx_noms", "Afficher les noms");
      majPanBtn(); rendPan(); dessineR();
    }
    cadre(); dessineC();
    textes(); document.addEventListener("langchange", function () { dessineC(); textes(); });
    setTimeout(function () { cadre(); grosAv = null; dessineC(); depart(); }, 150);
    function depart() {
      var h = h0;
      if (h.indexOf("l=") === 0) { var o = trouve(h.slice(2)); if (o) { mo.setView(ll(o), mo.getMinZoom() + 2.2); voir(o, true); } }
      else if (h.indexOf("c=") === 0) { var v = h.slice(2).split(",").map(Number); if (v.length === 3 && v.every(isFinite)) mo.setView([v[1], v[2]], v[0]); }
      etiquettes();
    }
    addEventListener("resize", function () { clearTimeout(cadre.t); cadre.t = setTimeout(function () { mo.invalidateSize(); var zf = mo.getBoundsZoom(TERRE, false); ZB = zf; mo.setMinZoom(zf - 0.6); }, 150); });
  }

  function carte() {
    var el = document.getElementById("carte");
    /* la barre flottante « Suivre GTA 6 » ne doit jamais recouvrir la carte */
    if (el) {
      var zc = el.closest(".ct-zone") || el;
      var masque = function () { var sv = document.getElementById("suivre"); if (!sv) return; var a = zc.getBoundingClientRect(); sv.classList.toggle("ct-masque", a.bottom > 0 && a.top < innerHeight - 10); };
      addEventListener("scroll", masque, { passive: true }); addEventListener("resize", masque); setTimeout(masque, 600);
    }
    if (!el || !window.L) { if (el) el.innerHTML = '<p class="cl-vide" style="padding:20px">' + esc(tr("sl_err", "La carte n'a pas pu se charger.")) + "</p>"; return; }
    fetch("data/carte.json", { cache: "no-cache" }).then(function (r) { return r.json(); }).then(function (D) {
      var C = {}; D.couches.forEach(function (c) { C[c.id] = c; }); D.regions.forEach(function (g) { RN[g.id] = g.nom; });
      liste(D, C);
      /* pas de faux : la carte ne s'affiche qu'avec un fond officiel Rockstar et des points réellement situés */
      var situes = D.points.filter(function (p) { return p.x != null && p.y != null; });
      if (!D.fond_officiel || !situes.length) {
        var z = el.closest(".ct-zone"); if (z) z.classList.add("ct-seule");
        var pa = document.querySelector(".ct-panneau"); if (pa) pa.hidden = true;
        /* 19/11 Gabriel : « la carte n'apparaît pas sur mobile, simple et agréable » : en attendant le fond officiel,
           schéma des 6 régions cliquable (aucun point inventé) ; toucher une région filtre la liste des lieux */
        el.innerHTML = "";
        /* 19/11 15 h : carte officielle Rockstar (« Leonida Map & Cover Art Poster », rockstargames.com/VI/media) : zoomable, sans point inventé */
        if (D.fond_officiel) {
        fetch("data/carte_missions.json", { cache: "no-cache" }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (M) {
          if (M && M.points && M.points.length) { D.couches.push(M.couche); C[M.couche.id] = M.couche; M.points.forEach(function (p) { D.points.push(p); }); }
          carteOff(el, D, C);
        });
        return;
      }
        el.classList.add("ct-schema");
        var Hs = 1000, ms = L.map(el, { crs: L.CRS.Simple, minZoom: -2, maxZoom: 1.5, zoomSnap: 0.25, attributionControl: false, scrollWheelZoom: false, tap: true });
        var Bs = [[0, 0], [Hs, Hs]];
        L.imageOverlay(R + D.fond, Bs, { alt: "Leonida" }).addTo(ms);
        var terre = [[70, 80], [900, 840]]; ms.fitBounds(terre); ms.on("resize", function () { ms.fitBounds(terre); }); ms.setMaxBounds([[-200, -200], [Hs + 200, Hs + 200]]);
        function lls(x, y) { return [Hs - y, x]; }
        var nbr = {}; D.points.forEach(function (p) { if (p.region) nbr[p.region] = (nbr[p.region] || 0) + 1; });
        var polys = {};
        function choisir(id) {
          Object.keys(polys).forEach(function (k) { polys[k].setStyle({ fillOpacity: k === id ? .35 : .08, weight: k === id ? 3 : 1.5 }); });
          var fR = document.getElementById("lf-reg"), fT = document.getElementById("lf-type"), fS = document.getElementById("lf-stat");
          if (fR) { if (fT) fT.value = ""; if (fS) fS.value = ""; fR.value = id; fR.dispatchEvent(new Event("change")); }
          var li = document.getElementById("ct-liste"); if (li) li.scrollIntoView({ behavior: "smooth", block: "start" });
        }
        D.regions.forEach(function (g) {
          var pg = L.polygon(g.poly.map(function (q) { return lls(q[0], q[1]); }), { color: "#ffd23f", weight: 1.5, fillColor: "#ff2e88", fillOpacity: .08 }).addTo(ms);
          pg.on("click", function () { choisir(g.id); });
          polys[g.id] = pg;
          L.marker(lls(g.centre[0], g.centre[1]), { icon: L.divIcon({ className: "ct-reg-lab", html: "<b>" + esc(g.nom) + "</b><small>" + (nbr[g.id] || 0) + " " + esc(tr("sl_lieux", "lieux")) + "</small>", iconSize: [130, 44], iconAnchor: [65, 22] }), keyboard: true, title: g.nom })
            .on("click", function () { choisir(g.id); }).addTo(ms);
        });
        var cap = document.createElement("p"); cap.className = "ct-schema-cap";
        function capt() { cap.textContent = tr("sl_schema_cap", "Touchez une région pour voir ses lieux. Schéma des régions : les emplacements précis s'afficheront sur la carte officielle de Rockstar dès sa publication."); }
        capt(); el.parentNode.insertBefore(cap, el.nextSibling);
        document.addEventListener("langchange", capt);
        setTimeout(function () { ms.invalidateSize(); ms.fitBounds(terre); }, 200);
        return;
      }
      D.fond = D.fond_officiel;
      var H = 1000, map = L.map(el, { crs: L.CRS.Simple, minZoom: -1.2, maxZoom: 3, zoomSnap: 0.25, attributionControl: true, maxBoundsViscosity: .8 });
      var B = [[0, 0], [H, H]];
      L.imageOverlay(R + D.fond, B, { alt: "Leonida" }).addTo(map);
      map.setMaxBounds([[-150, -150], [H + 150, H + 150]]);
      map.fitBounds(B);
      map.attributionControl.setPrefix(false).addAttribution(esc(tr("sl_attr_off", "Carte officielle Rockstar Games")));
      function ll(x, y) { return [H - y, x]; }
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
        if (e) e.textContent = D.points.length ? D.points.length + " " + tr("sl_pts_ok", "points placés sur la carte") + " · " + tr("sl_conf_n", "confirmés") + " : " + D.points.filter(function (p) { return p.statut === "confirme"; }).length + "/" + D.points.length : tr("sl_pts_vide", "Les emplacements sont ajoutés dès qu'ils sont vérifiés (2 sources concordantes ou source officielle).");
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

  /* ---------- CARTE : liste des lieux connus, filtrable (type, région, statut, recherche) ---------- */
  function liste(D, C) {
    var z = document.getElementById("ct-liste-z"); if (!z) return;
    var fT = document.getElementById("lf-type"), fR = document.getElementById("lf-reg"), fS = document.getElementById("lf-stat"), fQ = document.getElementById("lf-q"), nb = document.getElementById("lf-nb");
    var h = location.hash.slice(1).split("="); if (h[0] === "c") S.o.lft = decodeURIComponent(h[1] || "");
    function opts() {
      var types = D.couches.filter(function (c) { return D.points.some(function (p) { return p.couche === c.id; }); });
      fT.innerHTML = '<option value="">' + esc(tr("sl_f_types", "Tous les types")) + "</option>" + types.map(function (c) { return '<option value="' + c.id + '">' + esc(txt(c)) + "</option>"; }).join("");
      fR.innerHTML = '<option value="">' + esc(tr("sl_f_regs", "Toutes les régions")) + "</option>" + D.regions.map(function (g) { return '<option value="' + g.id + '">' + esc(g.nom) + "</option>"; }).join("") + '<option value="-">' + esc(tr("sl_f_noreg", "Région non précisée")) + "</option>";
      fS.innerHTML = '<option value="">' + esc(tr("sl_f_stats", "Tous les statuts")) + '</option><option value="confirme">' + esc(tr("sl_conf", "Confirmé")) + '</option><option value="a_confirmer">' + esc(tr("sl_aconf", "À confirmer")) + "</option>";
      fQ.placeholder = tr("sl_rech", "Rechercher un lieu");
      fT.value = S.o.lft || ""; fR.value = S.o.lfr || ""; fS.value = S.o.lfs || "";
    }
    function dom(u) { try { return new URL(u).hostname.replace("www.", ""); } catch (e) { return u; } }
    function rend() {
      var t = fT.value, r = fR.value, st = fS.value, q = (fQ.value || "").toLowerCase().trim();
      var ordre = {}; D.regions.forEach(function (g, i) { ordre[g.id] = i; });
      var pts = D.points.filter(function (p) {
        return (!t || p.couche === t) && (!r || (r === "-" ? !p.region : p.region === r)) && (!st || p.statut === st) && (!q || ((txt(p) || "") + " " + (txt(p, "note_") || "")).toLowerCase().indexOf(q) >= 0);
      }).sort(function (a, b) { return (ordre[a.region] == null ? 99 : ordre[a.region]) - (ordre[b.region] == null ? 99 : ordre[b.region]) || a.couche.localeCompare(b.couche) || a.id.localeCompare(b.id); });
      nb.textContent = pts.length + " / " + D.points.length;
      var html = "", reg = null;
      pts.forEach(function (p) {
        var rk = p.region || "-";
        if (rk !== reg) { if (reg !== null) html += "</ul>"; reg = rk; html += "<h3>" + esc(p.region ? (RN[p.region] || p.region) : tr("sl_f_noreg", "Région non précisée")) + '</h3><ul class="lf-liste">'; }
        var c = C[p.couche] || {};
        html += '<li class="lf-item' + (S.p[p.id] ? " fait" : "") + '"><input type="checkbox" data-pt="' + esc(p.id) + '"' + (S.p[p.id] ? " checked" : "") + ' aria-label="' + esc(tr("sl_trouve", "Trouvé")) + '">' +
          (c.icone ? '<img src="' + R + c.icone + '" alt="" width="26" height="26">' : "<span></span>") +
          "<div><b>" + esc(txt(p) || p.id) + "</b>" + (txt(p) !== p.en ? '<small class="tr-off" lang="en">' + esc(p.en) + "</small>" : "") + ' <span class="ms-tag">' + esc(txt(c)) + '</span> <span class="ms-tag' + (p.statut === "confirme" ? "" : " ko") + '">' + esc(p.statut === "confirme" ? tr("sl_conf", "Confirmé") : tr("sl_aconf", "À confirmer")) + "</span>" +
          (txt(p, "note_") ? "<p>" + esc(txt(p, "note_")) + "</p>" : "") +
          '<small>' + esc(tr("sl_source", "Source")) + " : " + (p.sources || []).map(function (u) { return '<a href="' + esc(u) + '" target="_blank" rel="noopener nofollow">' + esc(dom(u)) + "</a>"; }).join(" · ") + "</small></div></li>";
      });
      z.innerHTML = pts.length ? html + "</ul>" : '<p class="cl-vide">' + esc(tr("sl_f_vide", "Aucun lieu ne correspond à ces filtres.")) + "</p>";
    }
    opts(); rend();
    [fT, fR, fS].forEach(function (f) { f.addEventListener("change", function () { S.o.lft = fT.value; S.o.lfr = fR.value; S.o.lfs = fS.value; sauve(); rend(); }); });
    fQ.addEventListener("input", rend);
    z.addEventListener("change", function (ev) { var i = ev.target; if (!i.getAttribute || !i.getAttribute("data-pt")) return; var id = i.getAttribute("data-pt"); if (i.checked) S.p[id] = 1; else delete S.p[id]; sauve(); rend(); });
    document.addEventListener("langchange", function () { opts(); rend(); });
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
          var RG = {}; (D.regions || []).forEach(function (g, i) { RG[g.id] = [i, g.nom]; });
          pts.sort(function (a, b) { return ((RG[a.region] || [99])[0] - (RG[b.region] || [99])[0]) || a.id.localeCompare(b.id); });
          var der = null;
          ul.innerHTML = pts.length ? pts.map(function (p) {
            var h = ""; if (p.region !== der) { der = p.region; h = '<li class="cl-reg">' + esc((RG[p.region] || [0, tr("sl_f_noreg", "Région non précisée")])[1]) + "</li>"; }
            return h + '<li><input type="checkbox" data-pt="' + esc(p.id) + '"' + (S.p[p.id] ? " checked" : "") + '><div><b>' + esc(txt(p) || p.id) + "</b>" + (txt(p) !== p.en ? '<small class="tr-off" lang="en">' + esc(p.en) + "</small>" : "") +
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

  /* ---------- TRICHES : plateforme, recherche, filtres, copier ---------- */
  function triches() {
    var plat = S.o.plat || "ps", cat = "", conf = false, q = document.getElementById("tr-q");
    var cartes = [].slice.call(document.querySelectorAll(".tr-carte"));
    function maj() {
      [].forEach.call(document.querySelectorAll("[data-plat]"), function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-plat") === plat ? "true" : "false"); });
      [].forEach.call(document.querySelectorAll("kbd[data-ps]"), function (k) { k.textContent = k.getAttribute("data-" + plat); k.className = "bt bt-" + plat; });
      [].forEach.call(document.querySelectorAll("[data-trf]"), function (b) { b.setAttribute("aria-pressed", b.getAttribute("data-trf") === cat ? "true" : "false"); });
      var cb = document.querySelector("[data-trc]"); if (cb) cb.setAttribute("aria-pressed", conf ? "true" : "false");
      var v = norm(q ? q.value : ""), n = 0;
      [].forEach.call(document.querySelectorAll(".tr-cat"), function (sec) {
        var vis = 0, okc = !cat || sec.getAttribute("data-cat") === cat;
        [].forEach.call(sec.querySelectorAll(".tr-carte"), function (c) {
          var on = okc && (!conf || c.getAttribute("data-st") === "ok") && (!v || norm(c.textContent).indexOf(v) >= 0);
          c.hidden = !on; if (on) vis++;
        });
        sec.hidden = !vis; n += vis;
      });
      var nb = document.getElementById("tr-nb"); if (nb) nb.textContent = n + " / " + cartes.length;
      [].forEach.call(document.querySelectorAll(".tr-off"), function (o) { var h = o.parentNode.querySelector("h3"); o.hidden = !h || norm(h.textContent) === norm(o.textContent); });
    }
    [].forEach.call(document.querySelectorAll("[data-plat]"), function (b) { b.addEventListener("click", function () { plat = S.o.plat = b.getAttribute("data-plat"); sauve(); maj(); }); });
    [].forEach.call(document.querySelectorAll("[data-trf]"), function (b) { b.addEventListener("click", function () { cat = b.getAttribute("data-trf"); maj(); }); });
    var cb = document.querySelector("[data-trc]"); if (cb) cb.addEventListener("click", function () { conf = !conf; maj(); });
    if (q) q.addEventListener("input", maj);
    document.addEventListener("click", function (ev) {
      var b = ev.target.closest && ev.target.closest(".tr-copie"); if (!b) return;
      var sq = b.parentNode.querySelector(".tr-seq"); if (!sq) return;
      var t = sq.getAttribute("data-code"), fin = function () { b.textContent = tr("sl_copie", "Copié !"); b.classList.add("ok"); setTimeout(function () { b.textContent = tr("sl_copier", "Copier"); b.classList.remove("ok"); }, 1600); };
      if (navigator.clipboard) navigator.clipboard.writeText(t).then(fin, fin); else fin();
    });
    document.addEventListener("langchange", maj);
    maj();
  }
  function norm(s) { return String(s || "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim(); }

  /* ---------- COMMUN : sommaire collant, recherche sur la page, haut de page ---------- */
  function outils() {
    var tete = document.querySelector(".sl-tete"); if (!tete) return;
    var h2s = [].slice.call(document.querySelectorAll(".sl-sec h2")).filter(function (h) { return !h.closest(".tr-mode") && !h.closest(".sl-tuiles") && h.getAttribute("data-i18n") !== "sl_hub_t" && h.offsetParent !== null; });
    var nav = document.createElement("nav"); nav.className = "sl-som"; nav.setAttribute("aria-label", tr("sl_som", "Sommaire"));
    function rend() {
      nav.innerHTML = '<div class="wrap"><div class="sl-som-l">' + h2s.map(function (h, i) { if (!h.id) h.id = "s-" + i; return '<a href="#' + h.id + '">' + esc(h.textContent.replace(/\s+\d+$/, "")) + "</a>"; }).join("") + "</div>" +
        (page !== "triches" && page !== "carte" ? '<input type="search" class="sl-som-q" placeholder="' + esc(tr("sl_rech_page", "Rechercher sur la page")) + '" aria-label="' + esc(tr("sl_rech_page", "Rechercher sur la page")) + '">' : "") + "</div>";
      var qi = nav.querySelector(".sl-som-q"); if (qi) qi.addEventListener("input", function () { cherche(qi.value); });
    }
    if (h2s.length > 1 || (page !== "triches" && page !== "carte")) { rend(); tete.parentNode.insertBefore(nav, tete.nextSibling); document.addEventListener("langchange", rend); }
    function cherche(v) {
      v = norm(v);
      var it = document.querySelectorAll(".tp, .ms-carte, .ms-liste li, .cl-pts li:not(.cl-reg):not(.cl-vide), .sl-liste li");
      [].forEach.call(it, function (x) { x.classList.toggle("q-non", !!v && norm(x.textContent).indexOf(v) < 0); });
      [].forEach.call(document.querySelectorAll(".ms-chap"), function (d) { if (v) d.open = !!d.querySelector(".ms-liste li:not(.q-non)"); });
    }
    var haut = document.createElement("button"); haut.type = "button"; haut.className = "sl-haut"; haut.setAttribute("aria-label", tr("sl_haut", "Haut de page")); haut.textContent = "↑";
    haut.addEventListener("click", function () { scrollTo({ top: 0, behavior: "smooth" }); });
    document.body.appendChild(haut);
    var avant = scrollY;
    addEventListener("scroll", function () {
      haut.classList.toggle("on", scrollY > 700);
      // barre « Suivre GTA 6 » : cachée quand on descend (elle ne masque aucune carte), revient quand on remonte ou en bas de page
      var sv = document.getElementById("suivre");
      if (sv && page !== "carte") { var bas = innerHeight + scrollY >= document.documentElement.scrollHeight - 40; sv.classList.toggle("ct-masque", scrollY > 300 && scrollY > avant && !bas); }
      avant = scrollY;
    }, { passive: true });
  }

  if (page === "triches") triches();
  if (page === "trophees") trophees();
  else if (page === "carte") carte();
  else if (page === "collectibles") collectibles();
  else if (page === "missions") missions();
  outils();
})();
