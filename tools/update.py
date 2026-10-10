#!/usr/bin/env python3
"""Mise à jour automatique (chaque minute en mode --vite et toutes les 10 min en complet, cron serveur ; GitHub Actions en secours) :
- data/news_<lang>.json : dernières actus GTA 6 par langue (Google News RSS)
- data/videos.json      : dernières vidéos GTA de la chaîne YouTube Rockstar Games
- data/deals.json       : offres et prix repérés dans les actus (précommandes, consoles)
Bibliothèque standard uniquement."""
import json, re, html, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import os
ROOT = Path(__file__).resolve().parent.parent / os.environ.get("OUT_DIR", "data")
ROOT.mkdir(exist_ok=True)
UA = {"User-Agent": "Mozilla/5.0 (gta6-countdown updater)"}
LANGS = {  # code : (hl, gl, ceid, requête)
    "fr": ("fr", "FR", "FR:fr", "GTA 6"), "en": ("en-US", "US", "US:en", "GTA 6"),
    "es": ("es", "ES", "ES:es", "GTA 6"), "pt": ("pt-BR", "BR", "BR:pt-419", "GTA 6"),
    "de": ("de", "DE", "DE:de", "GTA 6"), "it": ("it", "IT", "IT:it", "GTA 6"),
    "ja": ("ja", "JP", "JP:ja", "GTA6"), "zh": ("zh-CN", "CN", "CN:zh-Hans", "GTA6"),
    "ar": ("ar", "SA", "SA:ar", "GTA 6"), "hi": ("hi", "IN", "IN:hi", "GTA 6"),
    "ru": ("ru", "RU", "RU:ru", "GTA 6"), "ko": ("ko", "KR", "KR:ko", "GTA 6"),
    "tw": ("zh-TW", "TW", "TW:zh-Hant", "GTA6"), "tr": ("tr", "TR", "TR:tr", "GTA 6"),
    "id": ("id", "ID", "ID:id", "GTA 6"), "pl": ("pl", "PL", "PL:pl", "GTA 6"),
    "vi": ("vi", "VN", "VN:vi", "GTA 6"),
}
TRAILERS = ["QdBZY2fkU-0", "VQRLujxTm3c", "tJbzMqJGH4k", "evtZ-L7FIbw"]

def vues():
    """Historique des vues YouTube des trailers : data/vues.json {date: {id: vues}}, 90 jours max."""
    f = ROOT / "vues.json"
    h = json.loads(f.read_text()) if f.exists() else {}
    jour = {}
    for v in TRAILERS:
        try:
            m = re.search(rb'"viewCount":"(\d+)"', get(f"https://www.youtube.com/watch?v={v}&hl=en"))
            if m: jour[v] = int(m.group(1))
        except Exception: pass
    if jour: h[datetime.now(timezone.utc).date().isoformat()] = jour
    h = dict(sorted(h.items())[-90:])
    f.write_text(json.dumps(h))
    return jour

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()

def news(lang):
    hl, gl, ceid, q = LANGS[lang]
    url = f"https://news.google.com/rss/search?q={urllib.request.quote(q)}&hl={hl}&gl={gl}&ceid={ceid}"
    items = []
    for it in ET.fromstring(get(url)).iter("item"):
        titre = html.unescape(it.findtext("title") or "")
        src = it.find("source")
        src = src.text if src is not None else ""
        titre = re.sub(r"\s+-\s+" + re.escape(src) + r"$", "", titre) if src else titre
        try: d = parsedate_to_datetime(it.findtext("pubDate")).astimezone(timezone.utc).isoformat()
        except Exception: d = ""
        items.append({"t": titre, "u": it.findtext("link"), "s": src, "d": d})
    items.sort(key=lambda x: x["d"], reverse=True)
    return items[:15]

def videos():
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=UCULwHhkI31JHAKe57LZdzcA"
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015", "m": "http://search.yahoo.com/mrss/"}
    out = []
    for e in ET.fromstring(get(url)).findall("a:entry", ns):
        t = e.findtext("a:title", "", ns)
        if not re.search(r"GTA|Grand Theft Auto|VI\b", t, re.I): continue
        out.append({"t": t, "id": e.findtext("yt:videoId", "", ns), "d": e.findtext("a:published", "", ns)[:10]})
    return out[:8]

def deals(all_news):
    mots = re.compile(r"pr[ée]commande|pre-?order|prix|price|promo|bon plan|deal|offre|PS5|Xbox|console|€|\$", re.I)
    vus, out = set(), []
    for lang in ("fr", "en"):
        for n in all_news.get(lang, []):
            if mots.search(n["t"]) and n["u"] not in vus:
                vus.add(n["u"]); out.append(dict(n, lang=lang))
    return out[:12]

def youtube():
    """Vidéos GTA 6 publiées aujourd'hui sur YouTube (recherche triée par date), sans clé API."""
    h = get("https://www.youtube.com/results?search_query=gta+6&sp=CAISBAgCEAE%3D").decode("utf-8", "ignore")
    out, vus = [], set()
    for m in re.finditer(r'"videoId":"([A-Za-z0-9_-]{11})".{0,600}?"title":\{"runs":\[\{"text":"((?:[^"\\]|\\.)*)"', h):
        vid, t = m.group(1), json.loads('"' + m.group(2) + '"')
        if vid in vus or len(t) < 8: continue
        vus.add(vid); out.append({"id": vid, "t": t})
        if len(out) >= 12: break
    return out

def merch(lang):
    hl, gl, ceid, _ = LANGS[lang]
    q = "GTA 6 (figurine OR merch OR t-shirt OR poster OR collector OR console OR manette)" if lang == "fr" else "GTA 6 (merch OR figure OR t-shirt OR poster OR collector OR console OR controller)"
    url = f"https://news.google.com/rss/search?q={urllib.request.quote(q)}&hl={hl}&gl={gl}&ceid={ceid}"
    out = []
    for it in ET.fromstring(get(url)).iter("item"):
        t = html.unescape(it.findtext("title") or ""); src = it.findtext("source") or ""
        t = re.sub(r"\s+-\s+[^-]+$", "", t)
        out.append({"t": t, "u": it.findtext("link"), "s": src, "d": (it.findtext("pubDate") or "")[:16]})
        if len(out) >= 12: break
    return out

def communaute():
    ns = {"a": "http://www.w3.org/2005/Atom"}
    x = ET.fromstring(get("https://www.reddit.com/r/GTA6/top/.rss?t=day"))
    out = []
    for e in x.findall("a:entry", ns):
        t = html.unescape(e.findtext("a:title", default="", namespaces=ns))
        u = e.find("a:link", ns).get("href")
        if "reddit.com" in u and t: out.append({"t": t, "u": u, "s": "r/GTA6", "d": (e.findtext("a:updated", default="", namespaces=ns))[:10]})
        if len(out) >= 8: break
    return out

UA_NAV = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"}

def boutique():
    """Boutique Rockstar, collection GTA VI : titre, prix, lien, image (page HTML, pas d'API)."""
    s = urllib.request.urlopen(urllib.request.Request("https://store.rockstargames.com/grand-theft-auto-vi-collection", headers=UA_NAV), timeout=30).read().decode("utf8", "ignore")
    out, vus = [], set()
    for m in re.finditer(r'<a[^>]+href="(/merchandise/[^"]+|/game/[^"]+)"[^>]*>(.*?)</a>', s, re.S):
        h, inner = m.group(1), m.group(2)
        img = re.search(r'<img alt="([^"]*)"[^>]*srcSet="([^"\s]+)"', inner)
        prix = re.search(r'(€|\$|£)\s?(\d+[.,]\d{2})', html.unescape(re.sub(r'<[^>]+>', ' ', inner)))
        etat = "soon" if re.search(r'COMING SOON', inner, re.I) else ("new" if re.search(r'>\s*New\s*<', inner) else "")
        if not img or h in vus: continue
        vus.add(h)
        out.append({"t": html.unescape(img.group(1)).strip(), "p": (prix.group(1) + prix.group(2)) if prix else "", "u": "https://store.rockstargames.com" + h, "img": img.group(2).split("?")[0] + "?w=480&fm=webp&q=75", "e": etat})
    # Stock : la fiche produit expose schema.org ; sans aucune offre InStock, l'article est en rupture.
    for it in out[:40]:
        try:
            pg = urllib.request.urlopen(urllib.request.Request(it["u"], headers=UA_NAV), timeout=30).read().decode("utf8", "ignore")
            it["stock"] = ('schema.org/InStock' in pg) or ('schema.org/PreOrder' in pg) or ('availability' not in pg)
        except Exception: it["stock"] = True
    return out

def rockstar():
    """Newswire Rockstar : articles liés à GTA VI listés sur rockstargames.com/VI (titre en fr via la page article)."""
    s = urllib.request.urlopen(urllib.request.Request("https://www.rockstargames.com/VI", headers=UA_NAV), timeout=30).read().decode("utf8", "ignore")
    liens = list(dict.fromkeys(re.findall(r'https://www\.rockstargames\.com/newswire/article/[a-z0-9]+', s)))[:6]
    out = []
    for u in liens:
        it = {"u": u}
        for l in ("fr", "en"):
            try:
                a = urllib.request.urlopen(urllib.request.Request(u.replace("rockstargames.com/", "rockstargames.com/fr/") if l == "fr" else u, headers=UA_NAV), timeout=30).read().decode("utf8", "ignore")
                t = re.search(r'<title>([^<]*)</title>', a); d = re.search(r'"datePublished":"([^"]+)"', a) or re.search(r'property="article:published_time" content="([^"]+)"', a)
                it[l] = html.unescape(t.group(1)).replace(" - Rockstar Games", "").strip() if t else ""
                if d: it["d"] = d.group(1)[:10]
            except Exception: it[l] = ""
        out.append(it)
    return out

if __name__ == "__main__":
    import sys
    VITE = "--vite" in sys.argv  # passage minute : actus 17 langues + newswire Rockstar seulement
    all_news, erreurs = {}, []
    for lang in LANGS:
        try: all_news[lang] = news(lang); (ROOT / f"news_{lang}.json").write_text(json.dumps(all_news[lang], ensure_ascii=False))
        except Exception as e: erreurs.append(f"{lang}: {e}")
    if VITE:
        try: (ROOT / "rockstar.json").write_text(json.dumps(rockstar(), ensure_ascii=False))
        except Exception as e: erreurs.append(f"rockstar: {e}")
        (ROOT / "deals.json").write_text(json.dumps(deals(all_news), ensure_ascii=False))
        (ROOT / "meta.json").write_text(json.dumps({"maj": datetime.now(timezone.utc).isoformat(), "erreurs": erreurs}))
        print("vite OK", sum(len(v) for v in all_news.values()), "erreurs:", erreurs); sys.exit(0)
    try: (ROOT / "videos.json").write_text(json.dumps(videos(), ensure_ascii=False))
    except Exception as e: erreurs.append(f"videos: {e}")
    for lang in ("fr", "en"):
        try: (ROOT / f"merch_{lang}.json").write_text(json.dumps(merch(lang), ensure_ascii=False))
        except Exception as e: erreurs.append(f"merch {lang}: {e}")
    try: (ROOT / "youtube.json").write_text(json.dumps(youtube(), ensure_ascii=False))
    except Exception as e: erreurs.append(f"youtube: {e}")
    try: (ROOT / "communaute.json").write_text(json.dumps(communaute(), ensure_ascii=False))
    except Exception as e: erreurs.append(f"communaute: {e}")
    try: (ROOT / "boutique.json").write_text(json.dumps(boutique(), ensure_ascii=False))
    except Exception as e: erreurs.append(f"boutique: {e}")
    try: (ROOT / "rockstar.json").write_text(json.dumps(rockstar(), ensure_ascii=False))
    except Exception as e: erreurs.append(f"rockstar: {e}")
    try: print("vues", vues())
    except Exception as e: erreurs.append(f"vues: {e}")
    (ROOT / "deals.json").write_text(json.dumps(deals(all_news), ensure_ascii=False))
    (ROOT / "meta.json").write_text(json.dumps({"maj": datetime.now(timezone.utc).isoformat(), "erreurs": erreurs}))
    print("OK", {k: len(v) for k, v in all_news.items()}, "erreurs:", erreurs)
