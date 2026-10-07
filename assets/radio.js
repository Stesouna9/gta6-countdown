// Lecteur Vice Bay Radio : charge les stations depuis vicebayradio.com (window.VBR).
// Essaie le flux direct de la station, sinon enchaîne les pistes "live" (m4a, OKALAM).
(function () {
  var conteneur = document.getElementById("radio");
  if (!conteneur) return;
  var audio = new Audio();
  audio.preload = "none";
  var stations = [], courante = null, index = 0, joue = false;
  var logoSt = {}; // logos : https://vicebayradio.com/img/st_{id}.webp

  conteneur.innerHTML =
    '<div class="haut">' +
      '<img class="logo-st" id="r-logo" alt="">' +
      '<div class="infos"><div class="st-nom" id="r-nom">Vice Bay Radio</div>' +
      '<div><span class="st-freq" id="r-freq"></span> <span class="st-genre" id="r-genre">Chargement des stations…</span></div>' +
      '<div class="piste" id="r-piste"></div></div>' +
      '<div class="vu"><i></i><i></i><i></i><i></i><i></i></div>' +
      '<button class="play" id="r-play" aria-label="Lecture">▶</button>' +
    '</div><div class="stations" id="r-stations"></div>' +
    '<p class="note">Six stations FM fictives de Vice Bay, 1986. Musique libre (CC BY), jingles et animateurs OKALAM Studio. ' +
    '<a href="https://vicebayradio.com" target="_blank" rel="noopener">Site complet avec le cadran →</a></p>';

  var $ = function (id) { return document.getElementById(id); };

  function piste(st, i) {
    var lst = st.live || st.tracks || [];
    if (!lst.length) return null;
    return lst[i % lst.length];
  }

  function affiche() {
    if (!courante) return;
    $("r-nom").textContent = courante.name;
    $("r-freq").textContent = courante.f + " FM";
    $("r-genre").textContent = courante.genre;
    $("r-logo").src = "https://vicebayradio.com/img/st_" + courante.id + ".webp";
    var p = piste(courante, index);
    $("r-piste").textContent = p ? (p.type === "link" ? "🎙 " + (courante.host || "Vice Bay DJ") : (p.title + (p.artist ? " · " + p.artist : ""))) : "";
    conteneur.style.setProperty("--st", courante.c);
    document.querySelectorAll("#r-stations button").forEach(function (b) {
      b.classList.toggle("actif", b.dataset.id === courante.id);
    });
    $("r-play").textContent = joue ? "⏸" : "▶";
    conteneur.classList.toggle("joue", joue);
  }

  function lance() {
    var p = piste(courante, index);
    if (!p) return;
    audio.src = new URL(p.src, "https://vicebayradio.com/").href;
    audio.play().then(function () { joue = true; affiche(); }).catch(function () { joue = false; affiche(); });
  }

  function choisit(st) {
    courante = st; index = Math.floor(Math.random() * ((st.live || []).length || 1));
    try { localStorage.setItem("vbr-station", st.id); } catch (e) {}
    if (joue || audio.src) lance(); else affiche();
  }

  audio.addEventListener("ended", function () { index++; lance(); });
  audio.addEventListener("error", function () { index++; if (index < 30) lance(); });

  $("r-play").addEventListener("click", function () {
    if (!courante) return;
    if (joue) { audio.pause(); joue = false; affiche(); }
    else if (audio.src) { audio.play().then(function () { joue = true; affiche(); }); }
    else lance();
  });

  var s = document.createElement("script");
  s.src = "https://vicebayradio.com/data.js?v=" + Math.floor(Date.now() / 3600000);
  s.onload = function () {
    stations = (window.VBR && VBR.stations) || [];
    var html = stations.map(function (st) {
      return '<button data-id="' + st.id + '" style="--st:' + st.c + '"><b style="color:' + st.c + '">' + st.name + '</b><small>' + st.f + ' FM · ' + st.genre + '</small></button>';
    }).join("");
    $("r-stations").innerHTML = html;
    document.querySelectorAll("#r-stations button").forEach(function (b) {
      b.addEventListener("click", function () {
        choisit(stations.find(function (x) { return x.id === b.dataset.id; }));
        if (!joue) lance();
      });
    });
    var memo = null; try { memo = localStorage.getItem("vbr-station"); } catch (e) {}
    courante = stations.find(function (x) { return x.id === memo; }) || stations.find(function (x) { return x.id === "neon"; }) || stations[0];
    index = 0; affiche();
  };
  s.onerror = function () { $("r-genre").textContent = "Radio indisponible pour le moment."; };
  document.head.append(s);
})();
