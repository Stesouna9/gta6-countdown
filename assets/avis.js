// Avis sous chaque article (22/10/2026, Gabriel) : j'aime, note en étoiles, réactions, commentaires.
// API : mur/api/art (tools du Mur, /opt/mur/mur.py). Commentaires avec le compte du Mur, modérés par l'équipe de Solange.
(function () {
  var m = location.pathname.match(/\/journal\/([a-z0-9-]+)\.html$/); if (!m) return;
  var A = m[1], API = "/mur/api/", B = {}, sec;
  var REACS = ["🔥", "😂", "😮", "😢", "😡"];
  function T(k) { return (window.T && window.T(k)) || k; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k) || ""; if (v) localStorage.setItem(k, v); else localStorage.removeItem(k); } catch (e) { return ""; } }
  var V = ls("visiteur-id"); if (!V) { V = (Date.now().toString(36) + Math.random().toString(36).slice(2, 12)).slice(0, 24); ls("visiteur-id", V); }
  function post(chemin, d) { return fetch(API + chemin, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(d) }).then(function (r) { return r.json().then(function (j) { return [r.status, j]; }); }); }
  function quand(t) { var s = Date.now() / 1000 - t; return s < 3600 ? Math.max(1, Math.round(s / 60)) + " min" : s < 86400 ? Math.round(s / 3600) + " h" : new Date(t * 1000).toLocaleDateString(window.LANG || "fr"); }
  function vote(d) { d.a = A; d.v = V; post("art/vote", d).then(function (x) { if (x[0] === 200) { B = x[1]; rendu(); } }).catch(function () {}); }
  function rendu() {
    var moi = B.moi || {}, tok = ls("mur-token"), pseudo = ls("mur-pseudo"), note = moi.note || 0;
    var etoiles = [1, 2, 3, 4, 5].map(function (i) { return '<button class="av-et' + (i <= note ? " on" : "") + '" data-note="' + i + '" aria-label="' + i + '/5">★</button>'; }).join("");
    var reacs = REACS.map(function (r) { return '<button class="av-re' + (moi.reac === r ? " on" : "") + '" data-reac="' + r + '">' + r + " <i>" + ((B.reac || {})[r] || 0) + "</i></button>"; }).join("");
    var coms = (B.com || []).map(function (c) {
      return '<li><b>' + esc(c.p) + (c.staff ? ' <span class="av-staff">' + esc(T("av_equipe")) + "</span>" : "") + "</b> <time>" + quand(c.t) + "</time>" +
        '<p>' + esc(c.m) + '</p><button class="av-sig" data-sig="' + c.id + '">' + esc(T("av_signaler")) + "</button></li>";
    }).join("") || '<li class="av-vide">' + esc(T("av_vide")) + "</li>";
    var form = tok ? '<form class="av-form" data-f="com"><textarea name="m" maxlength="600" required placeholder="' + esc(T("av_ecrire")) + '"></textarea>' +
        '<div class="av-ligne"><span>' + esc(pseudo) + ' · <a href="#" data-sortir>' + esc(T("av_sortir")) + '</a></span><button class="btn" type="submit">' + esc(T("av_envoyer")) + "</button></div></form>"
      : '<form class="av-form" data-f="cx"><p class="av-cx">' + esc(T("av_cx")) + '</p><input name="i" required autocomplete="username" placeholder="' + esc(T("av_pseudo")) + '">' +
        '<input name="e" type="email" autocomplete="email" placeholder="' + esc(T("av_mail")) + '" hidden><input name="mdp" type="password" required minlength="8" autocomplete="current-password" placeholder="' + esc(T("av_mdp")) + '">' +
        '<div class="av-ligne"><a href="#" data-bascule>' + esc(T("av_inscr")) + '</a><button class="btn" type="submit">' + esc(T("av_connexion")) + "</button></div></form>";
    sec.innerHTML = '<span class="kicker">' + esc(T("av_t")) + "</span>" +
      '<div class="av-haut"><button class="av-lk' + (moi.lk ? " on" : "") + '" data-lk>❤ ' + esc(T("av_like")) + " <i>" + (B.lk || 0) + "</i></button>" +
      '<div class="av-note"><span class="av-ets">' + etoiles + '</span><small>' + (B.nb ? B.moy.toString().replace(".", ",") + "/5 · " + T("av_avis").replace("{n}", B.nb) : esc(T("av_note"))) + "</small></div></div>" +
      '<div class="av-reacs">' + reacs + "</div>" +
      '<h3 class="av-h">' + esc(T("av_com")) + " <i>" + (B.com || []).length + "</i></h3><ul class=\"av-coms\">" + coms + "</ul>" + form +
      '<p class="av-etat" aria-live="polite"></p><p class="av-modo">' + esc(T("av_modo")) + "</p>";
  }
  function etat(t) { var e = sec.querySelector(".av-etat"); if (e) e.textContent = t; }
  function clic(ev) {
    var b = ev.target.closest("button,a"); if (!b) return;
    if (b.hasAttribute("data-lk")) vote({ lk: (B.moi || {}).lk ? 0 : 1 });
    else if (b.hasAttribute("data-note")) vote({ note: +b.getAttribute("data-note") });
    else if (b.hasAttribute("data-reac")) { var r = b.getAttribute("data-reac"); vote({ reac: (B.moi || {}).reac === r ? "" : r }); }
    else if (b.hasAttribute("data-sig")) { post("art/signaler", { id: +b.getAttribute("data-sig") }).catch(function () {}); b.textContent = T("av_signale"); b.disabled = true; }
    else if (b.hasAttribute("data-sortir")) { ev.preventDefault(); post("deconnexion", { token: ls("mur-token") }).catch(function () {}); ls("mur-token", ""); ls("mur-pseudo", ""); rendu(); }
    else if (b.hasAttribute("data-bascule")) {
      ev.preventDefault(); var f = b.closest("form"), ins = f.getAttribute("data-f") === "cx";
      f.setAttribute("data-f", ins ? "ins" : "cx"); f.e.hidden = !ins; f.e.required = ins;
      b.textContent = T(ins ? "av_deja" : "av_inscr"); f.querySelector("[type=submit]").textContent = T(ins ? "av_creer" : "av_connexion");
    }
  }
  function envoi(ev) {
    var f = ev.target; ev.preventDefault(); var k = f.getAttribute("data-f"), L = window.LANG || "fr";
    var p = k === "com" ? post("art/com", { a: A, m: f.m.value.trim(), l: L, token: ls("mur-token") })
      : k === "ins" ? post("inscription", { p: f.i.value.trim(), e: f.e.value.trim(), mdp: f.mdp.value, l: L }) : post("connexion", { i: f.i.value.trim(), mdp: f.mdp.value });
    etat("…");
    p.then(function (x) {
      if (x[0] !== 200) { if (x[0] === 401 && k === "com") { ls("mur-token", ""); rendu(); } return etat(x[1].e === "refusé" ? T("av_refus") : T("mur_err_" + x[1].e) || x[1].e || "erreur"); }
      if (k === "com") { B = x[1]; rendu(); etat(T("av_publie")); } else { ls("mur-token", x[1].token); ls("mur-pseudo", x[1].p); rendu(); }
    }).catch(function () { etat("erreur réseau"); });
  }
  function init() {
    var ref = document.querySelector(".partage"); if (!ref || sec) return;
    sec = document.createElement("section"); sec.className = "avis"; ref.parentNode.insertBefore(sec, ref.nextSibling);
    sec.addEventListener("click", clic); sec.addEventListener("submit", envoi);
    var tok = ls("mur-token");
    if (tok && !ls("mur-pseudo")) fetch(API + "moi?token=" + encodeURIComponent(tok)).then(function (r) { return r.json(); }).then(function (j) { if (j.p) ls("mur-pseudo", j.p); else ls("mur-token", ""); rendu(); }).catch(function () {});
    fetch(API + "art?a=" + A + "&v=" + V).then(function (r) { return r.json(); }).then(function (j) { if (j.reac) { B = j; rendu(); } }).catch(function () {});
    rendu();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
  document.addEventListener("langchange", function () { if (sec) rendu(); });
})();
