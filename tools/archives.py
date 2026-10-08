#!/usr/bin/env python3
"""Archives : chronologie GTA 6 sourcée (data/chronologie.json : date, titre, u, s, u2) -> data/archives.json
avec le texte des sources, pour que Solange écrive les articles rétroactifs sans réseau.
Usage : python3 tools/archives.py [chronologie.json]"""
import json, sys, os
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(Path(__file__).resolve().parent.parent)
from presse import article

src = Path(sys.argv[1] if len(sys.argv) > 1 else "data/chronologie.json")
chrono = json.load(open(src, encoding="utf-8"))
out = Path("data/archives.json")
done = {x["date"] + x["titre"]: x for x in json.load(open(out, encoding="utf-8"))} if out.exists() else {}
res = []
for ev in chrono:
    k = ev["date"] + ev["titre"]
    if k in done and done[k].get("txt"): res.append(done[k]); continue
    x = {"date": ev["date"], "titre": ev["titre"], "s": ev.get("s", ""), "u": ev.get("u", ""), "fait": done.get(k, {}).get("fait", False), "sources": []}
    for u in (ev.get("u"), ev.get("u2")):
        if not u: continue
        try:
            a = article(u); a["u"] = a.get("u") or u; x["sources"].append(a)
        except Exception as e:
            x["sources"].append({"u": u, "erreur": str(e)[:120]})
    x["txt"] = next((s.get("txt", "") for s in x["sources"] if s.get("txt")), "")
    x["img"] = next((s.get("img", "") for s in x["sources"] if "rockstargames.com" in (s.get("u") or "") and s.get("img")), "")
    res.append(x); print(ev["date"], ev["titre"][:50], "txt", len(x["txt"]))
res.sort(key=lambda x: x["date"])
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(res), "événements,", sum(1 for x in res if x["txt"]), "avec texte")
