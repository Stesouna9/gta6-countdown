// Configuration commune du site. Modifier ici uniquement.
window.SITE = {
  sortie: "2026-11-19T00:00:00+01:00",   // minuit heure de Paris
  annonce: "2025-11-06T00:00:00+01:00",  // annonce de la date finale
  amazonTag: "okalamstudio-21",          // tag Amazon Partenaires (à remplacer par le vrai)
  adsensePub: "ca-pub-8121423865459620", // même identifiant éditeur que l'AdMob OKALAM
  discord: "https://discord.gg/TSaxEnt2dG",
  radio: "https://vicebayradio.com",
  vicebreak: "https://okalamstudio.com/vicebreak.html"
};

(function () {
  var pages = [
    ["index.html", "Compte à rebours"],
    ["actus.html", "Actus"],
    ["radio.html", "Vice Bay Radio"],
    ["vicebreak.html", "Vice Break"],
    ["goodies.html", "Goodies"],
    ["acheter.html", "Jeu & consoles"]
  ];
  var ici = location.pathname.split("/").pop() || "index.html";
  var nav = document.createElement("nav");
  nav.className = "nav";
  nav.innerHTML = '<a class="logo" href="index.html">GTA VI · J-?</a>' +
    pages.map(function (p) {
      return '<a href="' + p[0] + '"' + (p[0] === ici ? ' class="actif"' : "") + ">" + p[1] + "</a>";
    }).join("") + '<span class="jours" id="nav-jours"></span>';
  document.body.prepend(nav);

  var footer = document.createElement("footer");
  footer.innerHTML = '<div class="liens">' +
    '<a href="' + SITE.radio + '" target="_blank" rel="noopener">Vice Bay Radio</a>' +
    '<a href="' + SITE.vicebreak + '" target="_blank" rel="noopener">Vice Break</a>' +
    '<a href="' + SITE.discord + '" target="_blank" rel="noopener">Discord</a>' +
    '<a href="https://okalamstudio.com" target="_blank" rel="noopener">OKALAM Studio</a>' +
    '<a href="mentions.html">Mentions &amp; affiliation</a></div>' +
    "Site de fans non officiel, édité par OKALAM Studio. GTA et Grand Theft Auto sont des marques de Take-Two Interactive / Rockstar Games. " +
    "Vidéos intégrées depuis la chaîne YouTube officielle de Rockstar Games. Certains liens sont affiliés : le site touche une petite commission sans surcoût pour vous.";
  document.body.append(footer);

  // Jours restants dans la barre de navigation
  function jours() {
    var d = Math.ceil((new Date(SITE.sortie) - Date.now()) / 86400000);
    var el = document.getElementById("nav-jours");
    var logo = nav.querySelector(".logo");
    if (d > 0) { el.textContent = "J-" + d; logo.textContent = "GTA VI · J-" + d; }
    else { el.textContent = "Disponible"; logo.textContent = "GTA VI"; }
  }
  jours(); setInterval(jours, 60000);

  // Liens Amazon affiliés : <a data-amazon="requête">
  document.querySelectorAll("[data-amazon]").forEach(function (a) {
    a.href = "https://www.amazon.fr/s?k=" + encodeURIComponent(a.dataset.amazon) + "&tag=" + SITE.amazonTag;
    a.target = "_blank"; a.rel = "noopener sponsored";
  });

  // Publicité Google AdSense (annonces automatiques). Active seulement si le domaine est approuvé.
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
