"""Couches de jeu ajoutées à la carte (coffres à code, planques, opérations des gangs…) : data/carte_extra.json.
Entrées : data/soluce/coffres.json, data/soluce/lieux_jeu.json (facultatif). Position : « =Nom » = repère gtadb exact,
sinon nom de lieu officiel (carte.json) ou quartier gtadb (médiane des repères) ; plusieurs refs = milieu."""
import json, math, statistics
from pathlib import Path
R = Path(__file__).resolve().parent.parent
D = json.load(open(R / "data/carte.json")); G = json.load(open(R / "data/carte_gtadb.json"))["b"]
OH, KX = 3012, 2.2
LO = {o["n"]: (OH - o["y"] * KX, o["x"] * KX) for o in D["lieux_officiels"]}
def pos1(r):
    if r.startswith("="):
        n = r[1:].lower()
        for g in G:
            if g[0].split(",")[0].strip().lower() == n: return (g[1], g[2])
        raise SystemExit("repère gtadb absent : " + r)
    if r in LO: return LO[r]
    pts = [(g[1], g[2]) for g in G if r in [x.strip() for x in g[0].split(",")[1:]]]
    if not pts: raise SystemExit("lieu inconnu : " + r)
    return (statistics.median(p[0] for p in pts), statistics.median(p[1] for p in pts))
def pos(refs):
    p = [pos1(r) for r in refs]
    return [sum(a for a, _ in p) / len(p), sum(b for _, b in p) / len(p)]
COUCHES = {
 "coffres": {"fr": "Coffres à code", "en": "Safes with codes", "couleur": "#ffd23f", "famille": "j", "icone": "assets/img/carte/icones/coffres.svg"},
 "planques": {"fr": "Planques et propriétés", "en": "Safehouses & properties", "couleur": "#3ee08f", "famille": "j", "icone": "assets/img/carte/icones/planques.svg"},
 "gangs": {"fr": "Opérations des gangs", "en": "Gang operations", "couleur": "#ff4f4f", "famille": "j", "icone": "assets/img/carte/icones/gangs.svg"},
 "services": {"fr": "Receleurs et services", "en": "Fences & services", "couleur": "#4fc3ff", "famille": "j", "icone": "assets/img/carte/icones/services.svg"},
}
pts, vus = [], {}
def ajoute(couche, i, nom, qui, zone, ch, fr, en, refs, code=None):
    p = pos(refs); k = (round(p[0]), round(p[1])); n = vus.get(k, 0); vus[k] = n + 1
    if n: a = n * 2.39996; r = 14 * math.sqrt(n); p = [p[0] + r * math.sin(a), p[1] + r * math.cos(a)]
    pts.append({"id": f"{couche}-{i}", "couche": couche, "fr": nom, "en": nom, "qui": qui, "zone": zone, "ch": ch, "note_fr": fr, "note_en": en, "code": code, "pos": [round(p[0], 1), round(p[1], 1)]})
CF = json.load(open(R / "data/soluce/coffres.json"))
for i, c in enumerate(CF["codes"]):
    ajoute("gangs" if c["g"] == "ops" else "coffres", i, c["lieu"], c["qui"], c["zone"], c["ch"], c["fr"], c["en"], c["ref"], c["code"])
lj = R / "data/soluce/lieux_jeu.json"
if lj.exists():
    for i, c in enumerate(json.load(open(lj))["lieux"]):
        ajoute(c["couche"], i, c["lieu"], c.get("qui", ""), c["zone"], c.get("ch"), c["fr"], c["en"], c["ref"], c.get("code"))
json.dump({"couches": [dict(id=k, **v) for k, v in COUCHES.items() if any(p["couche"] == k for p in pts)], "points": pts},
          open(R / "data/carte_extra.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(pts), "points")
