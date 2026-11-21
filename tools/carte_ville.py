"""Catégories « En ville » (stations-service, magasins, restos…) à partir des repères gtadb.org (CC BY 4.0).
Entrée : data/gtadb/landmarks-6.json ; sortie : data/carte_ville.json. Relancer après tools/carte_gtadb.py."""
import json, re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
A, B, C, D = 14.74204119942186, -10982.277179612121, -15.119220133736107, 11149.163863533953
OH, KX = 3012, 2.2
def ll(gx, gy):
    x = (gx - B) / A; y = (gy - D) / C
    return round(OH - y * KX, 1), round(x * KX, 1)
CATS = [  # id, fr, en, icône, couleur, motif sur le nom, tags gtadb
 ("armes", "Ammu-Nation", "Ammu-Nation", "🔫", "#e84a3c", r"ammu|gun ?shop|firearm", []),
 ("essence", "Stations-service", "Gas stations", "⛽", "#ff8a1f", r"\bgas\b|xero|globe oil|fuel|petrol", []),
 ("magasins", "Magasins", "Shops", "🛒", "#3fb7ff", r"24/7|store|\bmart\b|market|\bmall\b|minimall|shop|outlet|liquor|\bltd\b|barber|tattoo|pawn", []),
 ("restos", "Restaurants et cafés", "Restaurants & cafés", "🍔", "#ffcf33", r"burger|pizza|cluck|diner|restaurant|grill|taco|caf[eé]|coffee|bistro|bean machine|sushi|bbq|kitchen|seafood|donut|wings|chicken", []),
 ("bars", "Bars et clubs", "Bars & clubs", "🍸", "#ff4fa3", r"\bbar\b|night ?club|lounge|tavern|saloon|\bpub\b|brew|strip", []),
 ("hotels", "Hôtels", "Hotels", "🏨", "#b48cff", r"hotel|motel|\binn\b|resort", ["hotel"]),
 ("police", "Police et prison", "Police & prison", "🚓", "#4f7dff", r"police|sheriff|jail|prison(?! tower)|correctional", []),
 ("sante", "Hôpitaux et pharmacies", "Hospitals & pharmacies", "✚", "#ff5b5b", r"hospital|medical|clinic|pharmacy", []),
 ("autos", "Garages et concessions", "Garages & dealers", "🔧", "#9aa5b1", r"motors|\bauto\b|car wash|dealership|tires?\b|mechanic|body shop|customs|boat works", []),
 ("transport", "Gares, ports et aéroports", "Stations, ports & airports", "✈", "#38d9c0", r"metro|train station|bus station|airport|airfield|terminal|marina|harbou?r|ferry|heliport|\bport\b(?! gellhorn)", ["transportation"]),
 ("sport", "Sport et loisirs", "Sports & leisure", "🏟", "#7ddc4a", r"stadium|arena|\bgym\b|golf|raceway|ballpark|tennis|bowling|soccer|football|baseball|volleyball|skate", []),
 ("plages", "Plages et jetées", "Beaches & piers", "🏖", "#ffe08a", r"\bbeach\b|\bpier\b|boardwalk", []),
 ("nature", "Nature et parcs", "Nature & parks", "🌴", "#3ecf6e", r"\bpark\b|\blake\b|\briver\b|swamp|preserve|trail|falls|waterfall|spring|visitor center", ["natural"]),
 ("reperes", "Autres lieux connus", "Other landmarks", "★", "#f4efe6", r".", []),
]
L = json.load(open(R / "data/gtadb/landmarks-6.json"))
out, nb = [], [0] * len(CATS)
for v in L.values():
    nom, g, reel, tags = v[0], v[1], v[3], v[6] or []
    if not g or not nom: continue
    court = nom.split(",")[0].strip().rstrip("?").strip()
    if court in ("?", "") or re.search(r"prison tower|parking garage", court, re.I): continue
    ci = None
    for i, c in enumerate(CATS):
        if c[0] != "reperes" and re.search(c[5], court, re.I): ci = i; break
    if ci is None:
        for i, c in enumerate(CATS):
            if set(c[6]) & set(tags): ci = i; break
    if ci is None: ci = len(CATS) - 1
    a, o = ll(*g); nb[ci] += 1
    lieu = ", ".join(x.strip() for x in nom.split(",")[1:3])
    out.append([court, a, o, ci, lieu, (reel or "").split(",")[0].strip(), 1 if "enterable" in tags else 0])
json.dump({"source": "gtadb.org et contributeurs, CC BY 4.0", "cats": [dict(id=c[0], fr=c[1], en=c[2], ico=c[3], couleur=c[4], off=c[0] == "reperes") for c in CATS], "p": out},
          open(R / "data/carte_ville.json", "w"), ensure_ascii=False, separators=(",", ":"))
print(len(out), dict(zip([c[0] for c in CATS], nb)))
