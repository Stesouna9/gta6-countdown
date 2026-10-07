// Configuration commune du site. Modifier ici uniquement.
window.SITE = {
  sortie: "2026-11-19T00:00:00+01:00",   // minuit heure de Paris
  annonce: "2025-11-06T00:00:00+01:00",  // annonce de la date finale
  amazonTag: "okalamstudio-21",          // tag Amazon Partenaires (à remplacer par le vrai)
  adsensePub: "ca-pub-8121423865459620", // même identifiant éditeur que l'AdMob OKALAM
  discord: "https://discord.gg/TSaxEnt2dG",
  radio: "https://vicebayradio.com",
  vicebreak: "https://okalamstudio.com/vicebreak.html",
  petition: "https://www.change.org/p/add-arabic-language-support-in-gta-vi"
};

(function () {
  var pages = [["index.html", "nav_home"], ["actus.html", "nav_news"], ["radio.html", "nav_radio"], ["vicebreak.html", "nav_vb"], ["goodies.html", "nav_goodies"], ["acheter.html", "nav_buy"], ["faq.html", "nav_faq"]];
  var ici = location.pathname.split("/").pop() || "index.html";
  var nav = document.createElement("nav");
  nav.className = "nav";
  nav.innerHTML = '<a class="logo" href="index.html"><b>VI</b><span>Countdown</span></a>' +
    pages.map(function (p) { return '<a href="' + p[0] + '"' + (p[0] === ici ? ' class="actif"' : "") + ' data-i18n="' + p[1] + '"></a>'; }).join("") +
    '<div class="droite"><span class="jours" id="nav-jours"></span><select class="lang" id="lang" aria-label="Language">' + langOptions() + "</select></div>";
  document.body.prepend(nav);
  document.getElementById("lang").addEventListener("change", function () { setLang(this.value); });

  var footer = document.createElement("footer");
  footer.innerHTML = '<div class="wrap"><div class="marque">Leonida</div><div class="bas"><div>' +
    '<div class="liens"><a href="' + SITE.radio + '" target="_blank" rel="noopener">Vice Bay Radio</a>' +
    '<a href="vicebreak.html">Vice Break</a><a href="' + SITE.discord + '" target="_blank" rel="noopener">Discord</a>' +
    '<a href="https://okalamstudio.com" target="_blank" rel="noopener">OKALAM Studio</a><a href="mentions.html" data-i18n="mentions"></a></div>' +
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

  // Journal : actus automatiques (data/news_<lang>.json), mises à jour 2 fois par jour
  window.chargeActus = function (el, n, tete) {
    function rend(l) {
      fetch("data/news_" + l + ".json").then(function (r) { return r.json(); }).then(function (lst) {
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

  // Publicité Google AdSense (annonces automatiques). Active seulement sur un domaine approuvé.
  if (SITE.adsensePub && !/github\.io$|localhost/.test(location.hostname)) {
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
