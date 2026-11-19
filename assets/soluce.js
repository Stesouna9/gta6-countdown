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
        el.innerHTML = ""; el.classList.add("ct-schema");
        var Hs = 1000, ms = L.map(el, { crs: L.CRS.Simple, minZoom: -2, maxZoom: 1.5, zoomSnap: 0.25, attributionControl: false, scrollWheelZoom: false, tap: true });
        var Bs = [[0, 0], [Hs, Hs]];
        L.imageOverlay(R + D.fond, Bs, { alt: "Leonida" }).addTo(ms);
        ms.fitBounds([[60, 60], [Hs - 60, Hs - 60]]); ms.setMaxBounds([[-200, -200], [Hs + 200, Hs + 200]]);
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
        setTimeout(function () { ms.invalidateSize(); ms.fitBounds([[60, 60], [Hs - 60, Hs - 60]]); }, 200);
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
