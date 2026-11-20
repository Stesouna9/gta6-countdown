"""Convertit les repères gtadb.org (CC BY 4.0, git pull de rolux/gtadb.org, map/data/6/landmarks.json)
vers le repère de la carte (lat/lng du cadre 2200x3012) : data/carte_gtadb.json.
Fit diagonal calé le 20/11/2026 sur 44 lieux officiels communs (écart médian ~250 m)."""
import json
from pathlib import Path
R = Path(__file__).resolve().parent.parent
A, B, C, D = 14.74204119942186, -10982.277179612121, -15.119220133736107, 11149.163863533953
OW, OH, KX = 2200, 3012, 2.2
def ll(gx, gy):
    x = (gx - B) / A; y = (gy - D) / C
    return round(OH - y * KX, 1), round(x * KX, 1)
L = json.load(open(R / "data/gtadb/landmarks-6.json"))
out = []
for k, v in L.items():
    nom, g, reel, tags = v[0], v[1], v[3], v[6]
    if not g or not nom: continue
    a, o = ll(*g)
    reel = (reel or "").split(",")[0].strip()
    out.append([nom, a, o, reel, (tags or [""])[0]])
json.dump({"source": "gtadb.org et contributeurs, CC BY 4.0", "maj": "2026-11-20", "b": out},
          open(R / "data/carte_gtadb.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(out), "bâtiments")
