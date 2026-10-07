// Langue. Chaque page existe en dur dans chaque langue : / (fr), /en/, /ar/... (générées par tools/prerender.py).
// Les traductions d'une langue sont dans assets/lang/<code>.js (I18N.<code>), chargé par la page.
(function () {
  window.I18N = window.I18N || {};
  var H = document.documentElement;
  var ROOT = H.getAttribute("data-root") || "";
  var PAGE = location.pathname.split("/").pop() || "index.html";
  var LOC = H.getAttribute("data-loc") !== "0";
  var NOMS = { fr: "Français", en: "English", es: "Español", pt: "Português", de: "Deutsch", it: "Italiano", ja: "日本語", zh: "简体中文", tw: "繁體中文",
    ar: "العربية", hi: "हिन्दी", ru: "Русский", ko: "한국어", tr: "Türkçe", id: "Bahasa Indonesia", pl: "Polski", vi: "Tiếng Việt" };
  var LANGS = Object.keys(NOMS);
  var page = H.getAttribute("data-l") || "fr";
  window.LANG = page; window.ROOT = ROOT; window.LANGS = LANGS; window.NOMS = NOMS;
  function url(l) { return ROOT + (l === "fr" ? "" : l + "/") + PAGE + location.hash; }
  function lit() { try { return localStorage.getItem("lang"); } catch (e) { return null; } }
  window.T = function (k) { var d = I18N[LANG] || {}; return d[k] != null ? d[k] : ((I18N.en || {})[k] || ""); };
  function charge(l, fn) {
    if (I18N[l]) return fn();
    var s = document.createElement("script"); s.src = ROOT + "assets/lang/" + l + ".js"; s.onload = fn; document.head.append(s);
  }
  function applique(l) {
    var d = I18N[l]; if (!d) return;
    H.lang = d._hl || l; H.dir = l === "ar" ? "rtl" : "ltr"; window.LANG = l;
    document.querySelectorAll("[data-i18n]").forEach(function (el) { var k = el.getAttribute("data-i18n"); if (d[k] != null) el.textContent = d[k]; });
    var sel = document.getElementById("lang"); if (sel) sel.value = l;
    document.dispatchEvent(new CustomEvent("langchange", { detail: l }));
  }
  window.setLang = function (l) {
    if (!NOMS[l]) return;
    try { localStorage.setItem("lang", l); } catch (e) {}
    if (LOC) location.href = url(l); else charge(l, function () { applique(l); });
  };
  window.langOptions = function () { return LANGS.map(function (l) { return '<option value="' + l + '"' + (l === page ? " selected" : "") + ">" + NOMS[l] + "</option>"; }).join(""); };
  // Choix explicite (sélecteur ou ancien lien ?lang=xx) : on va vers la bonne copie.
  var q = (location.search.match(/[?&]lang=([a-z]{2})/) || [])[1], choix = q || lit();
  if (LOC && choix && choix !== page && NOMS[choix]) { if (q) try { localStorage.setItem("lang", q); } catch (e) {} location.replace(url(choix)); }
  else if (!LOC && choix && NOMS[choix] && choix !== page) { page = choix; charge(choix, function () {}); }
  document.addEventListener("DOMContentLoaded", function () {
    charge(page, function () { applique(page); });
    // Pas de redirection automatique (Google doit voir chaque langue) : simple suggestion.
    var nav = (navigator.language || "").toLowerCase(), n = nav.slice(0, 2);
    if (nav === "zh-tw" || nav === "zh-hk" || nav.indexOf("hant") > -1) n = "tw";
    if (LOC && !choix && NOMS[n] && n !== page) {
      var a = document.createElement("a"); a.className = "lang-sugg"; a.href = url(n); a.lang = n;
      a.textContent = NOMS[n] + " →"; a.addEventListener("click", function () { try { localStorage.setItem("lang", n); } catch (e) {} });
      document.body.append(a);
    }
  });
})();
