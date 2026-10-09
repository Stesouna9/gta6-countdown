// Configuration commune du site. Modifier ici uniquement.
window.SITE = {
  sortie: "2026-11-19T00:00:00+01:00",   // minuit heure de Paris
  annonce: "2025-11-06T00:00:00+01:00",  // annonce de la date finale
  amazonTag: "okalamstudio-21",          // tag Amazon Partenaires (à remplacer par le vrai)
  adsensePub: "ca-pub-8121423865459620", // même identifiant éditeur que l'AdMob OKALAM
  // Unités AdSense (créées dans adsense.google.com > Annonces > Par bloc). Vide = emplacement inactif.
  adSlots: { "jr-haut": "4346556577", "jr-milieu": "9805843373", "jr-fin": "4346556577", "liste": "3033474908", "page": "7179680035" },
  discord: "https://discord.gg/TSaxEnt2dG",
  instagram: "https://www.instagram.com/vicebayradio/",
  radio: "https://vicebayradio.com",
  vicebreak: "https://okalamstudio.com/vicebreak.html",
  petition: "https://www.change.org/p/add-arabic-language-support-in-gta-vi",
  verif: "2026-10-07",                   // date de dernière vérification des faits
  base: "https://gtavifrance.com/",
  newsletter: ""                         // identifiant Buttondown ; vide = formulaire caché
};

(function () {
  var pages = [["index.html", "nav_home"], ["actus.html", "nav_news"], ["sortie.html", "nav_sortie"], ["guide.html", "nav_guide"], ["musique.html", "nav_musique"], ["radio.html", "nav_radio"], ["vicebreak.html", "nav_vb"], ["acheter.html", "nav_buy"], ["communaute.html", "nav_commu"]];
  /* Menu plein écran : trois rayons */
  var rayons = [
    ["menu_jeu", [["sortie.html", "nav_sortie"], ["guide.html", "nav_guide"], ["acheter.html", "nav_buy"], ["faq.html", "nav_faq"], ["vraifaux.html", "nav_vf"], ["quiz.html", "nav_quiz"]]],
    ["menu_actu", [["actus.html", "nav_news"], ["musique.html", "nav_musique"], ["goodies.html", "nav_goodies"]]],
    ["menu_commu", [["communaute.html", "nav_commu"], ["radio.html", "nav_radio"], ["vicebreak.html", "nav_vb"], ["arabe.html", "nav_arabe"], ["integrer.html", "nav_int"], ["apropos.html", "nav_about"]]]
  ];
  var R = window.ROOT || "";
  var ici = location.pathname.split("/").pop() || "index.html";
  var nav = document.createElement("nav");
  nav.className = "nav";
  nav.innerHTML = '<a class="logo" href="index.html" aria-label="VI Countdown"><img class="logo-vi" src="' + R + 'assets/img/logo-vi.webp" alt="GTA VI" width="207" height="160"><span>Countdown</span></a>' +
    pages.map(function (p) { return '<a href="' + p[0] + '"' + (p[0] === ici ? ' class="actif"' : "") + ' data-i18n="' + p[1] + '"></a>'; }).join("") +
    '<div class="droite"><span class="jours" id="nav-jours"></span><a class="ig" href="' + SITE.instagram + '" target="_blank" rel="noopener" aria-label="Instagram Vice Bay" title="Instagram"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.2.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.2.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4 1.2-.1 1.6-.1 4.8-.1M12 0C8.7 0 8.3 0 7.1.1 5.8.1 4.9.3 4.1.6c-.8.3-1.5.7-2.2 1.4C1.3 2.6.9 3.3.6 4.1.3 4.9.1 5.8.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.1 1.3.3 2.2.6 3 .3.8.7 1.5 1.4 2.2.7.7 1.4 1.1 2.2 1.4.8.3 1.7.5 3 .6 1.2 0 1.6 0 4.9 0s3.7 0 4.9-.1c1.3-.1 2.2-.3 3-.6.8-.3 1.5-.7 2.2-1.4.7-.7 1.1-1.4 1.4-2.2.3-.8.5-1.7.6-3 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.1-1.3-.3-2.2-.6-3-.3-.8-.7-1.5-1.4-2.2C21.4 1.3 20.7.9 19.9.6c-.8-.3-1.7-.5-3-.6C15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 1 0 0 12.4 6.2 6.2 0 0 0 0-12.4zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.4-11.8a1.4 1.4 0 1 0 0 2.9 1.4 1.4 0 0 0 0-2.9z"/></svg></a><select class="lang" id="lang" aria-label="Language">' + langOptions() + '</select><button type="button" class="burger" id="burger" aria-expanded="false" aria-controls="menu-plein"><span></span><span></span><span data-i18n="nav_menu"></span></button></div>';
  document.body.prepend(nav);
  document.getElementById("lang").addEventListener("change", function () { setLang(this.value); });

  /* Menu plein écran, à la Rockstar : fond nuit, grandes entrées, fermeture Échap */
  var menu = document.createElement("div");
  menu.className = "menu-plein"; menu.id = "menu-plein"; menu.setAttribute("hidden", "");
  menu.innerHTML = '<div class="menu-haut"><a class="logo" href="index.html" aria-label="VI Countdown"><img class="logo-vi" src="' + R + 'assets/img/logo-vi.webp" alt="GTA VI" width="207" height="160"><span>Countdown</span></a><button type="button" class="fermer" id="menu-fermer" data-i18n="nav_fermer"></button></div>' +
    '<nav class="menu-liens menu-rayons">' + rayons.map(function (r, k) { return '<div class="rayon" style="--i:' + k + '"><b data-i18n="' + r[0] + '"></b>' + r[1].map(function (p) { return '<a href="' + p[0] + '"' + (p[0] === ici ? ' class="actif"' : "") + ' data-i18n="' + p[1] + '"></a>'; }).join("") + "</div>"; }).join("") + "</nav>" +
    '<div class="menu-bas"><span data-i18n="menu_hub"></span><a href="' + SITE.radio + '" target="_blank" rel="noopener">Vice Bay Radio</a><a href="https://discord.gg/TSaxEnt2dG" target="_blank" rel="noopener">Discord</a><a href="' + SITE.instagram + '" target="_blank" rel="noopener">Instagram</a><a href="' + R + 'feed.xml">RSS</a></div>';
  document.body.append(menu);
  function menuOuvre(o) {
    var b = document.getElementById("burger");
    if (o) { menu.removeAttribute("hidden"); requestAnimationFrame(function () { menu.classList.add("ouvert"); }); document.documentElement.classList.add("menu-on"); b.setAttribute("aria-expanded", "true"); }
    else { menu.classList.remove("ouvert"); document.documentElement.classList.remove("menu-on"); b.setAttribute("aria-expanded", "false"); setTimeout(function () { if (!menu.classList.contains("ouvert")) menu.setAttribute("hidden", ""); }, 450); }
  }
  document.getElementById("burger").addEventListener("click", function () { menuOuvre(menu.hasAttribute("hidden")); });
  document.getElementById("menu-fermer").addEventListener("click", function () { menuOuvre(false); });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") menuOuvre(false); });
  /* Barre transparente en haut de page, pleine dès qu'on défile */
  function navEtat() { nav.classList.toggle("solide", window.scrollY > 24); }
  navEtat(); window.addEventListener("scroll", navEtat, { passive: true });

  var footer = document.createElement("footer");
  footer.innerHTML = '<div class="wrap"><div class="marque">Leonida</div><nav class="plan"><b data-i18n="foot_plus"></b>' +
    pages.concat(rayons.reduce(function (a, r) { return a.concat(r[1]); }, [])).filter(function (p, i, l) { return l.findIndex(function (q) { return q[0] === p[0]; }) === i; }).map(function (p) { return '<a href="' + p[0] + '" data-i18n="' + p[1] + '"></a>'; }).join("") + '<a href="' + R + 'feed.xml">RSS</a></nav><div class="bas"><div>' +
    '<div class="liens"><a href="' + SITE.radio + '" target="_blank" rel="noopener">Vice Bay Radio</a>' +
    '<a href="vicebreak.html">Vice Break</a><a href="' + SITE.discord + '" target="_blank" rel="noopener">Discord</a>' +
    '<a href="https://okalamstudio.com" target="_blank" rel="noopener">OKALAM Studio</a><a href="' + R + 'mentions.html" data-i18n="mentions"></a></div>' +
    '<p data-i18n="foot"></p></div><div class="okalam">OKALAM Studio<br>Nantes · ' + new Date().getFullYear() + "</div></div></div>";
  document.body.append(footer);

  function jours() {
    var d = Math.ceil((new Date(SITE.sortie) - Date.now()) / 86400000);
    document.getElementById("nav-jours").textContent = d > 0 ? "J-" + d : "";
  }
  jours(); setInterval(jours, 60000);

  document.querySelectorAll("[data-amazon]").forEach(function (a) {
    a.href = "https://www.amazon.fr/s?k=" + encodeURIComponent(a.dataset.amazon) + "&tag=" + SITE.amazonTag;
    a.target = "_blank"; a.rel = "noopener sponsored";
  });

  // Données : live/ (serveur, chaque minute) puis repli data/ (dépôt, GitHub Actions)
  window.donnees = function (f) {
    return fetch(R + "live/" + f.replace(/^data\//, ""), { cache: "no-cache" }).then(function (r) { if (!r.ok) throw 0; return r.json(); })
      .catch(function () { return fetch(R + f, { cache: "no-cache" }).then(function (r) { return r.json(); }); });
  };
  function maj() {
    var els = document.querySelectorAll("[data-maj]"); if (!els.length) return;
    donnees("data/flash.json").then(function (m) {
      var prev = 0; try { prev = +localStorage.getItem("visite") || 0; localStorage.setItem("visite", String(Date.now())); } catch (e) {}
      var arts = m.art || []; if (!arts.length) return;
      var n = prev ? arts.filter(function (a) { return new Date(a.date).getTime() > prev; }).length : 0;
      var a = arts[0], l = window.LANG || "fr", t = a.t[l] || a.t.en || a.t.fr;
      var lab = n ? n + " " + T("suivre_nouveau_n") : T("suivre_flash");
      document.getElementById("suivre-nouveau").innerHTML = '<a href="' + R + (l === "fr" ? "" : l + "/") + "journal/" + a.id + '.html"><small>' + lab + '</small><span>' + t + '</span></a>';
      if (n && !document.title.startsWith("•")) document.title = "• " + document.title;
    }).catch(function () {});
  }
  maj(); setInterval(maj, 60000);
  // YouTube du jour : grille de vignettes depuis data/youtube.json
  window.chargeYoutube = function (el, n) {
    donnees("data/youtube.json").then(function (lst) {
      el.innerHTML = lst.slice(0, n).map(function (v, i) {
        return '<div class="film" data-video="' + v.id + '" role="button" tabindex="0"><div class="cadre"><img src="https://img.youtube.com/vi/' + v.id + '/hqdefault.jpg" alt="" loading="lazy" width="480" height="360"><span class="play"></span></div><div class="legende"><span class="n">' + String(i + 1).padStart(2, "0") + "</span><b>" + v.t.replace(/</g, "&lt;") + "</b></div></div>";
      }).join("");
    }).catch(function () { el.innerHTML = ""; });
  };
  // Liste générique depuis un JSON (merch, communauté) : chargeListe(el, "data/x.json", n)
  window.chargeListe = function (el, fichier, n) {
    donnees(fichier).then(function (lst) {
      el.innerHTML = lst.slice(0, n).map(function (a) {
        return '<a href="' + a.u + '" target="_blank" rel="noopener"><span class="src">' + (a.s || "") + (a.d ? " · " + a.d : "") + "</span><b>" + a.t + "</b></a>";
      }).join("");
    }).catch(function () { el.innerHTML = ""; });
  };
  // Fait du jour : data/faits.json, change chaque jour
  function fait() {
    var el = document.querySelector("[data-fait]"); if (!el) return;
    fetch(R + "data/faits.json").then(function (r) { return r.json(); }).then(function (f) {
      var l = (window.LANG || "fr"); var lst = f[l] || f.en; var j = Math.floor(Date.now() / 864e5);
      el.textContent = lst[j % lst.length];
    }).catch(function () {});
  }
  fait(); document.addEventListener("langchange", fait);
  // Dépêches brutes (data/news_<lang>.json), mises à jour chaque minute via live/
  window.chargeDepeches = function (el, n, tete) {
    function rend(l) {
      donnees("data/news_" + (/^(fr|en|es|pt|de|it|ja|zh|tw|ar|hi|ru|ko|tr|id|pl|vi)$/.test(l) ? l : "en") + ".json").then(function (lst) {
        el.innerHTML = lst.slice(0, n).map(function (a, i) {
          var d = a.d ? new Date(a.d).toLocaleDateString(l) : "";
          var cls = tete && i === 0 ? ' class="tete"' : "";
          return '<a' + cls + ' href="' + a.u + '" target="_blank" rel="noopener"><span class="src">' + (a.s || "") + (d ? " · " + d : "") + "</span><b>" + a.t + "</b></a>";
        }).join("");
      }).catch(function () { el.innerHTML = ""; });
    }
    rend(window.LANG || "fr");
    document.addEventListener("langchange", function (e) { rend(e.detail); });
  };
  // Actus : les articles de Solange (data/articles.json), ouverts sur le site
  window.chargeActus = function (el, n) {
    function rend(l) {
      donnees("data/articles.json").then(function (lst) {
        el.innerHTML = lst.slice(0, n).map(function (x) {
          var a = x[l === "id" ? "idn" : l] || x.en || x.fr; if (!a) return "";
          var d = x.date ? new Date(x.date).toLocaleDateString(l, { day: "numeric", month: "short" }) : "";
          return '<a class="jr-carte" href="journal/' + x.id + '.html"><img src="' + x.img + '" alt="" loading="lazy"><span class="k">' + d + "</span><b>" + a.t + "</b><p>" + (a.d || "") + "</p></a>";
        }).join("");
      }).catch(function () { el.innerHTML = ""; });
    }
    rend(window.LANG || "fr");
    document.addEventListener("langchange", function (e) { rend(e.detail); });
  };

  // Date de vérification des faits, au format de la langue
  function verif() { var hl = document.documentElement.lang, o = { day: "numeric", month: "long", year: "numeric" };
    document.querySelectorAll("[data-verif]").forEach(function (el) { el.textContent = new Date(SITE.verif + "T12:00:00").toLocaleDateString(hl, o); });
    document.querySelectorAll("[data-date]").forEach(function (el) { el.textContent = new Date(el.getAttribute("data-date") + "T12:00:00").toLocaleDateString(hl, o); }); }
  verif(); newsletter(); document.addEventListener("langchange", verif);
  /* Suivre : notifications push, agenda, RSS, Discord, installation. Et « nouveau depuis ta visite ». */
  function b64(s) { var p = "=".repeat((4 - s.length % 4) % 4), b = atob((s + p).replace(/-/g, "+").replace(/_/g, "/")), a = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return a; }
  function suivre() {
    var d = document.createElement("div"); d.className = "suivre"; d.id = "suivre";
    var peut = "Notification" in window && "serviceWorker" in navigator && "PushManager" in window && Notification.permission !== "denied";
    d.innerHTML = '<span class="suivre-t"><i></i><b data-i18n="suivre_t"></b><em id="suivre-nouveau"></em></span><div class="suivre-b">' +
      (peut ? '<button type="button" id="btn-notif"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10 21h4"/></svg><span data-i18n="suivre_notif"></span></button>' : "") +
      '<a href="' + R + 'gta6.ics" download="gta6.ics"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg><span data-i18n="suivre_ics"></span></a>' +
      '<a href="https://discord.gg/TSaxEnt2dG" target="_blank" rel="noopener">Discord</a><a href="' + R + 'feed.xml">RSS</a>' +
      '<button type="button" id="btn-app" hidden><span data-i18n="suivre_app"></span></button><button type="button" class="x" id="suivre-x" aria-label="Fermer">×</button></div>';
    document.body.append(d);
    try { if (localStorage.getItem("suivre-ferme") === "1") d.classList.add("mini"); } catch (e) {}
    document.getElementById("suivre-x").onclick = function () { d.classList.toggle("mini"); try { localStorage.setItem("suivre-ferme", d.classList.contains("mini") ? "1" : "0"); } catch (e) {} };
    var bn = document.getElementById("btn-notif");
    if (bn) {
      function etat() { navigator.serviceWorker.ready.then(function (r) { return r.pushManager.getSubscription(); }).then(function (s) { if (s) { bn.classList.add("on"); bn.querySelector("span").textContent = T("suivre_notif_ok"); } }).catch(function () {}); }
      etat();
      bn.onclick = function () {
        navigator.serviceWorker.ready.then(function (r) {
          return r.pushManager.getSubscription().then(function (s) {
            if (s) { return fetch(R + "mur/api/push/retirer", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ endpoint: s.endpoint }) }).then(function () { return s.unsubscribe(); }).then(function () { bn.classList.remove("on"); bn.querySelector("span").textContent = T("suivre_notif"); }); }
            return fetch(R + "mur/api/push/cle").then(function (x) { return x.json(); }).then(function (k) { return r.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64(k.cle) }); })
              .then(function (s) { return fetch(R + "mur/api/push/abonner", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ sub: s.toJSON(), l: window.LANG || "fr" }) }); })
              .then(function () { bn.classList.add("on"); bn.querySelector("span").textContent = T("suivre_notif_ok"); });
          });
        }).catch(function () { bn.querySelector("span").textContent = T("suivre_notif_non"); });
      };
    }
    var ba = document.getElementById("btn-app"), evInstall = null;
    window.addEventListener("beforeinstallprompt", function (e) { e.preventDefault(); evInstall = e; ba.hidden = false; });
    ba.onclick = function () { if (evInstall) { evInstall.prompt(); evInstall = null; ba.hidden = true; } };
    /* nouveau depuis la dernière visite */
    donnees("data/meta.json").then(function (m) {
      var maj = new Date(m.maj).getTime(), prev = 0; try { prev = +localStorage.getItem("visite") || 0; localStorage.setItem("visite", String(Date.now())); } catch (e) {}
      if (prev && maj > prev) { document.getElementById("suivre-nouveau").innerHTML = '<a href="' + R + 'actus.html">' + T("suivre_nouveau") + ' ›</a>'; if (!document.title.startsWith("•")) document.title = "• " + document.title; }
    }).catch(function () {});
    function txt() { d.querySelectorAll("[data-i18n]").forEach(function (el) { var v = T(el.getAttribute("data-i18n")); if (v) el.textContent = v; }); }
    txt(); document.addEventListener("langchange", txt);
  }
  suivre();

  /* Fin de flux : appel à s'abonner sous chaque liste d'actus et chaque article */
  function finFlux() {
    document.querySelectorAll(".journal, .jr-grille, .jr-sources:not(.haut), #rockstar").forEach(function (el) {
      if (el.nextElementSibling && el.nextElementSibling.classList.contains("flux-fin")) return;
      var d = document.createElement("aside"); d.className = "flux-fin rv";
      d.innerHTML = '<b data-i18n="flux_t"></b><p data-i18n="flux_i"></p><div class="flux-b">' +
        '<button type="button" class="btn" data-flux-notif><span data-i18n="suivre_notif"></span></button>' +
        '<a class="btn fantome" href="' + R + 'gta6.ics" download="gta6.ics" data-i18n="suivre_ics"></a>' +
        '<a class="btn fantome" href="https://discord.gg/TSaxEnt2dG" target="_blank" rel="noopener">Discord</a>' +
        '<a class="btn fantome" href="' + R + 'feed.xml">RSS</a></div>';
      el.insertAdjacentElement("afterend", d);
      d.querySelector("[data-flux-notif]").onclick = function () { var b = document.getElementById("btn-notif"); if (b) { b.click(); setTimeout(function () { d.querySelector("[data-flux-notif] span").textContent = b.querySelector("span").textContent; }, 1500); } else { d.querySelector("[data-flux-notif] span").textContent = T("suivre_notif_non"); } };
      var bn = document.getElementById("btn-notif"); if (bn && bn.classList.contains("on")) d.querySelector("[data-flux-notif] span").textContent = T("suivre_notif_ok");
    });
    document.querySelectorAll(".flux-fin [data-i18n]").forEach(function (el) { var v = T(el.getAttribute("data-i18n")); if (v) el.textContent = v; });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", finFlux); else finFlux();
  document.addEventListener("langchange", finFlux);


  // Partage : bouton natif sur mobile, liens sinon. <div class="partage"></div>
  // Newsletter : formulaire Buttondown dans le pied, seulement si SITE.newsletter est posé
  function newsletter() {
    var p = document.querySelector("footer .plan"); if (!p || !SITE.newsletter) return;
    var f = document.createElement("form"); f.className = "lettre"; f.method = "post"; f.target = "_blank";
    f.action = "https://buttondown.com/api/emails/embed-subscribe/" + SITE.newsletter;
    f.innerHTML = '<input type="email" name="email" required placeholder="email"><button class="btn" type="submit">J-7 / J-1</button>';
    p.parentNode.insertBefore(f, p);
  }
  function partage() {
    document.querySelectorAll(".partage").forEach(function (el) {
      var n = Math.max(0, Math.ceil((new Date(SITE.sortie) - Date.now()) / 86400000));
      var u = SITE.base + (window.LANG === "fr" ? "" : window.LANG + "/"), t = (window.T ? T("sh_txt") : "").replace("{n}", n);
      var e = encodeURIComponent, liens = [["X", "https://x.com/intent/post?text=" + e(t) + "&url=" + e(u)], ["WhatsApp", "https://wa.me/?text=" + e(t + " " + u)],
        ["Telegram", "https://t.me/share/url?url=" + e(u) + "&text=" + e(t)], ["Reddit", "https://www.reddit.com/submit?url=" + e(u) + "&title=" + e(t)], ["Facebook", "https://www.facebook.com/sharer/sharer.php?u=" + e(u)]];
      el.innerHTML = '<span class="kicker" data-i18n="sh_t">' + (window.T ? T("sh_t") : "") + "</span>" + (navigator.share ? '<button class="btn" data-natif>' + T("sh_t") + "</button>" : "") +
        liens.map(function (l) { return '<a class="btn clair" target="_blank" rel="noopener" href="' + l[1] + '">' + l[0] + "</a>"; }).join("") + '<button class="btn clair" data-copie>' + (window.T ? T("sh_copy") : "Link") + "</button>";
      el.onclick = function (ev) {
        if (ev.target.hasAttribute("data-natif")) navigator.share({ title: "GTA VI", text: t, url: u }).catch(function () {});
        if (ev.target.hasAttribute("data-copie")) { navigator.clipboard.writeText(u); ev.target.textContent = T("in_copied"); }
      };
    });
  }
  document.addEventListener("langchange", partage);

  // Lecteur YouTube au clic
  document.addEventListener("click", function (e) {
    var f = e.target.closest(".film[data-video]");
    if (!f) return;
    var c = f.querySelector(".cadre");
    c.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + f.dataset.video + '?autoplay=1&rel=0" title="GTA VI" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>';
    f.removeAttribute("data-video");
  });

  // Révélation au défilement
  var io = "IntersectionObserver" in window ? new IntersectionObserver(function (es) {
    es.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add("vu"); io.unobserve(x.target); } });
  }, { rootMargin: "0px 0px -8% 0px" }) : null;
  window.observeRv = function () { document.querySelectorAll(".rv:not(.vu)").forEach(function (el) { io ? io.observe(el) : el.classList.add("vu"); }); };
  observeRv();

  // Mesure d'audience GoatCounter (sans cookie), hors localhost
  if (!/localhost/.test(location.hostname)) { window.goatcounter = { path: function (p) { return location.host + p; } }; var g = document.createElement("script"); g.async = true; g.src = "https://stats.2-29-41-109.sslip.io/count.js"; g.setAttribute("data-goatcounter", "https://stats.2-29-41-109.sslip.io/count"); document.head.append(g); }

  // Application installable et mode hors ligne
  if ("serviceWorker" in navigator && location.protocol === "https:") navigator.serviceWorker.register((window.ROOT || "") + "sw.js").catch(function () {});

  // Publicité Google AdSense (annonces automatiques). Active seulement sur un domaine approuvé.
  if (SITE.adsensePub && !/localhost/.test(location.hostname)) {
    if (!document.querySelector('script[src*="adsbygoogle.js"]')) {
      var s = document.createElement("script");
      s.async = true; s.crossOrigin = "anonymous";
      s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + SITE.adsensePub;
      document.head.append(s);
    }
    document.querySelectorAll(".pub").forEach(function (p) {
      var k = p.getAttribute("data-pub") || "page", slot = (SITE.adSlots || {})[k];
      if (!slot) { p.remove(); return; }
      var fluid = k === "jr-milieu";
      p.classList.remove("vide");
      p.innerHTML = '<ins class="adsbygoogle" style="display:block' + (fluid ? ';text-align:center' : '') + '" data-ad-client="' + SITE.adsensePub + '" data-ad-slot="' + slot + '"' + (fluid ? ' data-ad-layout="in-article" data-ad-format="fluid"' : ' data-ad-format="auto" data-full-width-responsive="true"') + '></ins>';
      (window.adsbygoogle = window.adsbygoogle || []).push({});
      setTimeout(function () { var i = p.querySelector("ins"); if (!i || !i.querySelector("iframe") || i.getAttribute("data-ad-status") === "unfilled") p.classList.add("vide"); }, 6000);
    });
  } else {
    document.querySelectorAll(".pub").forEach(function (p) { p.remove(); });
  }
})();
