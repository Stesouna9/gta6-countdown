// Poste Vice Bay Radio : cadran FM 88–108, aiguille, écran LCD, 6 présélections.
// Stations et pistes lues depuis vicebayradio.com/data.js (window.VBR).
(function () {
  var el = document.getElementById("radio");
  if (!el) return;
  var audio = new Audio(); audio.preload = "none";
  var stations = [], cur = null, idx = 0, joue = false;
  var pos = function (f) { return 4 + (f - 88) / 20 * 92; };

  var ech = "";
  for (var f = 88; f <= 108; f++) {
    ech += '<i class="' + (f % 2 === 0 ? "l" : "") + '" style="left:' + ((f - 88) / 20 * 100) + '%"></i>';
    if (f % 4 === 0) ech += '<em style="left:' + ((f - 88) / 20 * 100) + '%">' + f + "</em>";
  }
  el.className = "poste";
  el.innerHTML =
    '<div class="marque"><b>Vice Bay</b><span>FM Stereo · 1986</span></div>' +
    '<div class="cadran" id="r-cadran"><div class="ech">' + ech + '</div><div id="r-st"></div><span class="mhz">MHz</span><div class="aiguille" id="r-aig" style="left:50%"></div></div>' +
    '<div class="facade"><div class="lcd"><div class="l1"><span id="r-lcd">-- . -</span><span class="live off" id="r-live">ON AIR</span></div><div class="l2" id="r-piste">VICE BAY RADIO</div></div>' +
    '<div class="touches"><button class="touche" id="r-prev" aria-label="Station précédente">◀</button><button class="touche play" id="r-play" aria-label="Lecture">▶</button><button class="touche" id="r-next" aria-label="Station suivante">▶</button></div></div>' +
    '<div class="presets" id="r-presets"></div><div class="grille-hp"></div>';

  var $ = function (id) { return document.getElementById(id); };
  var liste = function (st) { return st.live || st.tracks || []; };

  function affiche() {
    if (!cur) return;
    $("r-aig").style.left = pos(cur.f) + "%";
    $("r-lcd").textContent = cur.f.toFixed(1) + "  " + cur.name;
    var p = liste(cur)[idx % (liste(cur).length || 1)];
    $("r-piste").textContent = p ? (p.type === "link" ? (cur.host ? cur.host + " · " : "") + "VICE BAY DJ" : (p.title + (p.artist ? " · " + p.artist : ""))).toUpperCase() : cur.genre;
    $("r-live").classList.toggle("off", !joue);
    $("r-play").textContent = joue ? "❚❚" : "▶";
    document.querySelectorAll("#r-presets button").forEach(function (b) { b.classList.toggle("on", b.dataset.id === cur.id); });
    document.querySelectorAll("#r-st .st").forEach(function (s) { s.classList.toggle("on", s.dataset.id === cur.id); });
  }
  function lance() {
    var l = liste(cur); if (!l.length) return;
    audio.src = new URL(l[idx % l.length].src, "https://vicebayradio.com/").href;
    audio.play().then(function () { joue = true; affiche(); }).catch(function () { joue = false; affiche(); });
  }
  function choisit(st, jouer) {
    cur = st; idx = Math.floor(Math.random() * (liste(st).length || 1));
    try { localStorage.setItem("vbr-station", st.id); } catch (e) {}
    if (jouer || joue) lance(); else affiche();
  }
  function decale(d) { var i = stations.indexOf(cur); choisit(stations[(i + d + stations.length) % stations.length], true); }

  audio.addEventListener("ended", function () { idx++; lance(); });
  audio.addEventListener("error", function () { idx++; if (idx < 40) lance(); });
  $("r-play").onclick = function () {
    if (!cur) return;
    if (joue) { audio.pause(); joue = false; affiche(); }
    else if (audio.src) audio.play().then(function () { joue = true; affiche(); });
    else lance();
  };
  $("r-prev").onclick = function () { decale(-1); };
  $("r-next").onclick = function () { decale(1); };
  $("r-cadran").onclick = function (e) {
    var r = this.getBoundingClientRect(), f = 88 + ((e.clientX - r.left) / r.width * 100 - 4) / 92 * 20;
    var best = stations.reduce(function (a, b) { return Math.abs(b.f - f) < Math.abs(a.f - f) ? b : a; });
    choisit(best, true);
  };

  var s = document.createElement("script");
  s.src = "https://vicebayradio.com/data.js?v=" + Math.floor(Date.now() / 3600000);
  s.onload = function () {
    stations = ((window.VBR && VBR.stations) || []).slice().sort(function (a, b) { return a.f - b.f; });
    $("r-st").innerHTML = stations.map(function (st, i) { return '<span class="st' + (i % 2 ? " bas" : "") + '" data-id="' + st.id + '" style="left:' + pos(st.f) + '%">' + st.name.replace(" DRIVE", "") + "</span>"; }).join("");
    $("r-presets").innerHTML = stations.map(function (st, i) { return '<button data-id="' + st.id + '" style="--st:' + st.c + '"><b>' + (i + 1) + "</b>" + st.name.replace(" DRIVE", "") + "</button>"; }).join("");
    document.querySelectorAll("#r-presets button").forEach(function (b) {
      b.onclick = function () { choisit(stations.find(function (x) { return x.id === b.dataset.id; }), true); };
    });
    var memo = null; try { memo = localStorage.getItem("vbr-station"); } catch (e) {}
    cur = stations.find(function (x) { return x.id === memo; }) || stations.find(function (x) { return x.id === "sunset"; }) || stations[0];
    idx = 0; affiche();
  };
  s.onerror = function () { $("r-piste").textContent = "SIGNAL PERDU"; };
  document.head.append(s);
})();
