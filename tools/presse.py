"""Revue de presse pour Solange (routine cloud sans réseau) : résout les liens Google News,
lit chaque article (titre, image, chapeau, texte) et écrit data/presse.json.
Lancé toutes les heures par .github/workflows/presse.yml."""
import json, re, html, sys, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from update import news, rockstar, UA_NAV

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "data" / "presse.json"
MAX_TXT = 4500

def lire(url, timeout=25):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA_NAV), timeout=timeout) as r:
        return r.geturl(), r.read().decode("utf8", "ignore")

def gnews_resoudre(url):
    """Lien Google News -> URL réelle (procédé batchexecute)."""
    gid = url.split("/articles/")[1].split("?")[0]
    _, page = lire(f"https://news.google.com/articles/{gid}")
    sg = re.search(r'data-n-a-sg="([^"]+)"', page); ts = re.search(r'data-n-a-ts="([^"]+)"', page)
    if not (sg and ts): raise ValueError("signature absente")
    req = json.dumps([[["Fbv4je", json.dumps(["garturlreq", [["fr-FR", "FR", ["FINANCE_TOP_INDICES", "WEB_TEST_1_0_0"], None, None, 1, 1, "FR:fr", None, 180, None, None, None, None, None, 0, None, None, [1608992183, 723341000]], "fr-FR", "FR", 1, [2, 3, 4, 8], 1, 0, "655000234", 0, 0, None, 0], gid, int(ts.group(1)), sg.group(1)]), None, "generic"]]])
    data = urllib.parse.urlencode({"f.req": req}).encode()
    rq = urllib.request.Request("https://news.google.com/_/DotsSplashUi/data/batchexecute", data, {**UA_NAV, "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"})
    rep = urllib.request.urlopen(rq, timeout=25).read().decode("utf8", "ignore")
    m = re.search(r'garturlres\\",\\"(https?://[^\\"]+)', rep) or re.search(r'"garturlres","(https?://[^"]+)"', rep)
    if not m: raise ValueError("pas de garturlres")
    return m.group(1)

def meta(page, prop):
    m = re.search(r'<meta[^>]+(?:property|name)=["\']%s["\'][^>]+content=["\']([^"\']+)' % re.escape(prop), page, re.I) or \
        re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']%s["\']' % re.escape(prop), page, re.I)
    return html.unescape(m.group(1)).strip() if m else ""

def texte(page):
    page = re.sub(r"<(script|style|noscript|nav|header|footer|aside|form)[^>]*>.*?</\1>", " ", page, flags=re.S | re.I)
    art = re.search(r"<article[^>]*>(.*?)</article>", page, re.S | re.I)
    corps = art.group(1) if art else page
    paras = [re.sub(r"<[^>]+>", " ", p) for p in re.findall(r"<p[^>]*>(.*?)</p>", corps, re.S | re.I)]
    paras = [re.sub(r"\s+", " ", html.unescape(p)).strip() for p in paras]
    paras = [p for p in paras if len(p) > 60]
    out = "\n".join(paras)
    return out[:MAX_TXT]

def article(u):
    final, page = lire(u)
    t = meta(page, "og:title") or (re.search(r"<title>([^<]*)</title>", page, re.I) or [None, ""])[1]
    return {"u": final, "t": html.unescape(t).strip(), "img": meta(page, "og:image"), "chapeau": meta(page, "og:description") or meta(page, "description"), "txt": texte(page), "pub": meta(page, "article:published_time")}

def main():
    ancien = {}
    if SORTIE.exists():
        try: ancien = {x["gn"]: x for x in json.loads(SORTIE.read_text()) if x.get("gn")}
        except Exception: ancien = {}
    items, vus = [], set()
    for lang in ("fr", "en"):
        try: lst = news(lang)
        except Exception as e: print("news", lang, e); lst = []
        for it in lst:
            if it["u"] in ancien and ancien[it["u"]].get("txt"):
                x = ancien[it["u"]]
            else:
                x = {"gn": it["u"], "s": it["s"], "d": it["d"], "lang": lang, "t": it["t"]}
                try:
                    reel = gnews_resoudre(it["u"]) if "news.google.com" in it["u"] else it["u"]
                    x.update(article(reel)); x["t"] = x["t"] or it["t"]
                except Exception as e:
                    x["erreur"] = str(e)[:120]
            x["lang"] = lang
            if x.get("u", x["gn"]) in vus: continue
            vus.add(x.get("u", x["gn"])); items.append(x)
    try:
        for r in rockstar():
            x = {"gn": r["u"], "s": "Rockstar Newswire", "d": r.get("d", ""), "lang": "en", "t": r.get("en") or r.get("fr")}
            if r["u"] in ancien and ancien[r["u"]].get("txt"): x = ancien[r["u"]]
            else:
                try: x.update(article(r["u"]))
                except Exception as e: x["erreur"] = str(e)[:120]
            if x.get("u", x["gn"]) not in vus: vus.add(x.get("u", x["gn"])); items.append(x)
    except Exception as e: print("rockstar", e)
    items.sort(key=lambda x: x.get("d") or "", reverse=True)
    SORTIE.write_text(json.dumps({"maj": datetime.now(timezone.utc).isoformat(timespec="seconds"), "articles": items[:40]}, ensure_ascii=False, indent=1))
    ok = sum(1 for x in items if x.get("txt"))
    print(f"presse : {len(items)} articles, {ok} avec texte")

if __name__ == "__main__":
    main()
