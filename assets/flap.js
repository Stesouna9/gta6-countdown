/* Décompte façon tableau d'aéroport à palettes (Solari), aux couleurs de Vice City (13/10/2026).
   Lit les valeurs que le script de l'accueil écrit dans #jours, #heures, #minutes, #secondes (inchangé),
   et les affiche en palettes qui basculent, avec un cliquetis optionnel (coupé par défaut). */
(function () {
  var c = document.getElementById("compteur"); if (!c) return;
  var ids = ["jours", "heures", "minutes", "secondes"], src = {}, lab = {};
  ids.forEach(function (id) { src[id] = document.getElementById(id); var s = src[id] && (src[id].nextElementSibling || src[id].parentNode.querySelector("span:not(#" + id + ")")); lab[id] = s ? s : null; });
  if (!src.secondes) return;
  var fr = (document.documentElement.lang || "fr").slice(0, 2) === "fr";
  var b = document.createElement("div"); b.className = "flap-board"; b.setAttribute("aria-hidden", "true");
  var vol = fr ? "VOL VI-2026 · VICE CITY INTL → LEONIDA · DÉPART JEUDI 19.11.2026 · À L'HEURE · EMBARQUEMENT IMMINENT · "
               : "FLIGHT VI-2026 · VICE CITY INTL → LEONIDA · DEPARTS THU 19.11.2026 · ON TIME · NOW BOARDING · ";
  b.innerHTML = '<div class="flap-haut"><span class="flap-vol"><i>' + vol + vol + "</i></span>" +
    '<button type="button" class="flap-son" aria-label="Son">🔇</button></div><div class="flap-rangs"></div>';
  var rangs = b.querySelector(".flap-rangs"), cases = {};
  ids.forEach(function (id) {
    var g = document.createElement("div"); g.className = "flap-g flap-" + id;
    g.innerHTML = '<div class="flap-cs"></div><span class="flap-lab">' + (lab[id] ? lab[id].textContent : id) + "</span>";
    rangs.appendChild(g); cases[id] = { el: g.querySelector(".flap-cs"), v: [] };
  });
  c.classList.add("flap-on"); c.insertBefore(b, c.firstChild);

  // son : cliquetis mécanique synthétisé (pas de fichier), seulement après un geste de l'utilisateur
  var ac = null, son = false; try { son = localStorage.getItem("flapSon") === "1"; } catch (e) {}
  var bs = b.querySelector(".flap-son");
  function majBouton() { bs.textContent = son ? "🔊" : "🔇"; bs.classList.toggle("on", son); }
  bs.onclick = function () { son = !son; try { localStorage.setItem("flapSon", son ? "1" : "0"); } catch (e) {} if (son && !ac) try { ac = new (window.AudioContext || window.webkitAudioContext)(); } catch (e) {} majBouton(); };
  majBouton();
  var dernier = 0;
  function clac() {
    if (!son || !ac || ac.state !== "running" && ac.resume() && false) return;
    var t = ac.currentTime; if (t - dernier < 0.025) return; dernier = t;
    var n = ac.createBuffer(1, 900, ac.sampleRate), d = n.getChannelData(0);
    for (var i = 0; i < d.length; i++) d[i] = (Math.random() * 2 - 1) * Math.pow(1 - i / d.length, 6);
    var s = ac.createBufferSource(), f = ac.createBiquadFilter(), g = ac.createGain();
    s.buffer = n; f.type = "bandpass"; f.frequency.value = 2200 + Math.random() * 900; f.Q.value = 1.4; g.gain.value = 0.35;
    s.connect(f); f.connect(g); g.connect(ac.destination); s.start(t);
  }

  function cellule() {
    var e = document.createElement("div"); e.className = "flap";
    e.innerHTML = '<span class="fh"><b></b></span><span class="fb"><b></b></span><span class="ffh"><b></b></span><span class="ffb"><b></b></span>';
    return e;
  }
  function pose(e, ch, anim) {
    var old = e.dataset.v; if (old === ch) return; e.dataset.v = ch;
    var q = function (s) { return e.querySelector(s + " b"); };
    if (!anim || old === undefined) { q(".fh").textContent = q(".fb").textContent = q(".ffh").textContent = q(".ffb").textContent = ch; return; }
    q(".fh").textContent = ch; q(".ffb").textContent = ch;      // nouveau : moitié haute fixe + volet bas qui retombe
    q(".ffh").textContent = old; q(".fb").textContent = old;    // ancien : volet haut qui bascule + moitié basse fixe
    e.classList.remove("tourne"); void e.offsetWidth; e.classList.add("tourne");
    clearTimeout(e._t); e._t = setTimeout(function () { q(".fb").textContent = ch; q(".ffh").textContent = ch; e.classList.remove("tourne"); }, 420);
    clac();
  }
  function affiche(id, txt, anim) {
    var k = cases[id]; txt = String(txt || "00");
    while (k.v.length < txt.length) { var e = cellule(); k.el.appendChild(e); k.v.push(e); }
    while (k.v.length > txt.length) k.el.removeChild(k.v.pop());
    for (var i = 0; i < txt.length; i++) pose(k.v[i], txt[i], anim);
  }
  // ouverture : toutes les palettes tournent puis se posent sur le vrai décompte
  var debut = Date.now(), melange = true;
  ids.forEach(function (id) { affiche(id, src[id].textContent, false); });
  (function brasse() {
    var fini = Date.now() - debut > 1600;
    ids.forEach(function (id, n) {
      var vrai = src[id].textContent;
      if (fini || Date.now() - debut > 700 + n * 250) affiche(id, vrai, true);
      else affiche(id, vrai.replace(/\d/g, function () { return String(Math.floor(Math.random() * 10)); }), true);
    });
    if (!fini) setTimeout(brasse, 110); else melange = false;
  })();
  new MutationObserver(function () { if (!melange) ids.forEach(function (id) { affiche(id, src[id].textContent, true); }); })
    .observe(c, { subtree: true, childList: true, characterData: true });
})();
