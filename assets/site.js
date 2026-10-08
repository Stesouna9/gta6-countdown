// Configuration commune du site. Modifier ici uniquement.
window.SITE = {
  sortie: "2026-11-19T00:00:00+01:00",   // minuit heure de Paris
  annonce: "2025-11-06T00:00:00+01:00",  // annonce de la date finale
  amazonTag: "okalamstudio-21",          // tag Amazon Partenaires (à remplacer par le vrai)
  adsensePub: "ca-pub-8121423865459620", // même identifiant éditeur que l'AdMob OKALAM
  discord: "https://discord.gg/TSaxEnt2dG",
  radio: "https://vicebayradio.com",
  vicebreak: "https://okalamstudio.com/vicebreak.html",
  petition: "https://www.change.org/p/add-arabic-language-support-in-gta-vi",
  verif: "2026-10-07",                   // date de dernière vérification des faits
  base: "https://gtavifrance.com/",
  newsletter: ""                         // identifiant Buttondown ; vide = formulaire caché
};

(function () {
  var pages = [["index.html", "nav_home"], ["actus.html", "nav_news"], ["sortie.html", "nav_sortie"], ["guide.html", "nav_guide"], ["radio.html", "nav_radio"], ["vicebreak.html", "nav_vb"], ["acheter.html", "nav_buy"], ["faq.html", "nav_faq"]];
  var plus = [["goodies.html", "nav_goodies"], ["vraifaux.html", "nav_vf"], ["quiz.html", "nav_quiz"], ["arabe.html", "nav_arabe"], ["integrer.html", "nav_int"], ["apropos.html", "nav_about"]];
  var R = window.ROOT || "";
  var ici = location.pathname.split("/").pop() || "index.html";
  var nav = document.createElement("nav");
  nav.className = "nav";
  nav.innerHTML = '<a class="logo" href="index.html"><b>VI</b><span>Countdown</span></a>' +
    pages.map(function (p) { return '<a href="' + p[0] + '"' + (p[0] === ici ? ' class="actif"' : "") + ' data-i18n="' + p[1] + '"></a>'; }).join("") +
    '<div class="droite"><span class="jours" id="nav-jours"></span><select class="lang" id="lang" aria-label="Language">' + langOptions() + "</select></div>";
  document.body.prepend(nav);
  document.getElementById("lang").addEventListener("change", function () { setLang(this.value); });

  var footer = document.createElement("footer");
  footer.innerHTML = '<div class="wrap"><div class="marque">Leonida</div><nav class="plan"><b data-i18n="foot_plus"></b>' +
    pages.concat(plus).map(function (p) { return '<a href="' + p[0] + '" data-i18n="' + p[1] + '"></a>'; }).join("") + '<a href="' + R + 'feed.xml">RSS</a></nav><div class="bas"><div>' +
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

  // Liste générique depuis un JSON (merch, communauté) : chargeListe(el, "data/x.json", n)
  window.chargeListe = function (el, fichier, n) {
    fetch(R + fichier).then(function (r) { return r.json(); }).then(function (lst) {
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
  // Journal : actus automatiques (data/news_<lang>.json), mises à jour 2 fois par jour
  window.chargeActus = function (el, n, tete) {
    function rend(l) {
      fetch(R + "data/news_" + (/^(fr|en|es|pt|de|it|ja|zh|tw|ar|hi|ru|ko|tr|id|pl|vi)$/.test(l) ? l : "en") + ".json").then(function (r) { return r.json(); }).then(function (lst) {
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

  // Date de vérification des faits, au format de la langue
  function verif() { var hl = document.documentElement.lang, o = { day: "numeric", month: "long", year: "numeric" };
    document.querySelectorAll("[data-verif]").forEach(function (el) { el.textContent = new Date(SITE.verif + "T12:00:00").toLocaleDateString(hl, o); });
    document.querySelectorAll("[data-date]").forEach(function (el) { el.textContent = new Date(el.getAttribute("data-date") + "T12:00:00").toLocaleDateString(hl, o); }); }
  verif(); newsletter(); document.addEventListener("langchange", verif);

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
    var s = document.createElement("script");
    s.async = true; s.crossOrigin = "anonymous";
    s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + SITE.adsensePub;
    document.head.append(s);
    document.querySelectorAll(".pub").forEach(function (p) {
      p.innerHTML = '<ins class="adsbygoogle" style="display:block" data-ad-client="' + SITE.adsensePub + '" data-ad-format="auto" data-full-width-responsive="true"></ins>';
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    });
  }
})();
