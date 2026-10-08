#!/usr/bin/env python3
"""Archives : chronologie GTA 6 sourcée (data/chronologie.json : date, titre, u, s, u2) -> data/archives.json
avec le texte des sources, pour que Solange écrive les articles rétroactifs sans réseau.
Usage : python3 tools/archives.py [chronologie.json]"""
import json, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(Path(__file__).resolve().parent.parent)
from presse import article, gnews_resoudre
import urllib.request, xml.etree.ElementTree as ET, datetime
from update import get
PREF = ("rockstargames.com","take2games.com","ign.com","theverge.com","bbc.co","bloomberg.com","gamespot.com","eurogamer.net","polygon.com","pcgamer.com","kotaku.com","variety.com","reuters.com","videogameschronicle.com")
def chercher(q, d):
    j = datetime.date.fromisoformat(d)
    url = "https://news.google.com/rss/search?q=" + urllib.request.quote(f"{q} after:{j - datetime.timedelta(days=1)} before:{j + datetime.timedelta(days=4)}") + "&hl=en-US&gl=US&ceid=US:en"
    out = []
    try:
        for it in ET.fromstring(get(url)).iter("item"):
            src = it.find("source"); out.append((it.findtext("link"), src.text if src is not None else "", src.get("url", "") if src is not None else ""))
    except Exception as e: print("  recherche KO", e)
    out.sort(key=lambda x: 0 if any(p in x[2] for p in PREF) else 1)
    return out[:3]


src = Path(sys.argv[1] if len(sys.argv) > 1 else "data/chronologie.json")
chrono = json.load(open(src, encoding="utf-8"))
out = Path("data/archives.json")
done = {x["date"] + x["titre"]: x for x in json.load(open(out, encoding="utf-8"))} if out.exists() else {}
res = []
for ev in chrono:
    k = ev["date"] + ev["titre"]
    if k in done and done[k].get("txt"): res.append(done[k]); continue
    x = {"date": ev["date"], "titre": ev["titre"], "s": ev.get("s", ""), "u": ev.get("u", ""), "fait": done.get(k, {}).get("fait", False), "sources": []}
    cand = [(u, "", "") for u in (ev.get("u"), ev.get("u2")) if u]
    if not cand and ev.get("q"): cand = chercher(ev["q"], ev["date"])
    for u, s_, _ in cand:
        try:
            if "news.google.com" in u: u = gnews_resoudre(u)
            a = article(u); a["u"] = a.get("u") or u; a["s"] = s_ or a.get("s", ""); x["sources"].append(a)
            if len([z for z in x["sources"] if z.get("txt")]) >= 2: break
        except Exception as e:
            x["sources"].append({"u": u, "erreur": str(e)[:120]})
    if not x["s"]: x["s"] = next((z.get("s", "") for z in x["sources"] if z.get("txt")), "")
    if not x["u"]: x["u"] = next((z.get("u", "") for z in x["sources"] if z.get("txt")), "")
    x["txt"] = next((s.get("txt", "") for s in x["sources"] if s.get("txt")), "")
    x["img"] = next((s.get("img", "") for s in x["sources"] if "rockstargames.com" in (s.get("u") or "") and s.get("img")), "")
    res.append(x); print(ev["date"], ev["titre"][:50], "txt", len(x["txt"]))
res.sort(key=lambda x: x["date"])
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(res), "événements,", sum(1 for x in res if x["txt"]), "avec texte")
