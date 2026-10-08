#!/usr/bin/env python3
"""Récupère le texte des sources pour les entrées de data/archives.json sans txt (N par passage, les plus anciennes d'abord)."""
import json, os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); os.chdir(Path(__file__).resolve().parent.parent)
from presse import article, gnews_resoudre
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40
out = Path("data/archives.json"); arch = json.load(open(out, encoding="utf-8")); n = 0
for x in arch:
    if x.get("txt") or x.get("erreur") or x.get("fait") not in (False, None): continue
    try:
        u = x.get("u") or (gnews_resoudre(x["gn"]) if x.get("gn") else "")
        if not u: x["erreur"] = "pas de lien"; continue
        a = article(u); x["u"] = a.get("u") or u; x["txt"] = a.get("txt", ""); x["chapeau"] = a.get("chapeau", "")
        if "rockstargames.com" in x["u"] and a.get("img"): x["img"] = a["img"]
        if not x["txt"] and not x["chapeau"]: x["erreur"] = "vide"
    except Exception as e:
        x["erreur"] = str(e)[:100]
    n += 1
    if n >= N: break
json.dump(arch, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("archives_texte", n, "traités ;", sum(1 for x in arch if x.get("txt")), "avec texte /", len(arch))
