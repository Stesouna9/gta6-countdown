#!/usr/bin/env python3
"""Soluce GTA 6 V2 (18/11/2026) : importe les vraies infos publiées depuis la sortie (Océanie).

Sources lues : PowerPyx (guides complets) et GTABase (missions, triches, check-list 100 %).
Règle : « confirme » si 2 sources indépendantes concordent (ou source officielle), sinon « a_confirmer ».
- missions : titre présent chez PowerPyx ET GTABase -> confirme ;
- triches : effet + déblocage chez les deux, combinaison donnée par PowerPyx et non « TBA » chez GTABase -> confirme ;
- emplacements (méditation, drones, banques, garages) : nombre total confirmé par les deux check-lists 100 %,
  description de chaque lieu par PowerPyx seul -> a_confirmer (source citée), position sur NOTRE schéma = approximative.
Les traductions françaises passent par Google (gtx) et sont gardées en cache dans les JSON (rien n'est retraduit).
Usage : python3 tools/soluce_import.py   (puis tools/soluce.py et tools/prerender.py)
"""
import html, json, math, os, re, sys, subprocess
sys.path.insert(0, os.path.dirname(__file__))

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36"
PP = "https://www.powerpyx.com/"
GB = "https://www.gtabase.com/"
PAGES_PP = {"walk": "gta-6-full-walkthrough-all-missions", "cheats": "gta-6-all-cheats", "medit": "gta-6-all-meditation-spot-locations",
            "drones": "gta-6-all-top-fun-drone-race-time-trial-locations", "banks": "gta-6-all-bank-jobs-locations-bank-vaults",
            "garages": "gta-6-all-garage-locations", "cartes": "gta-6-all-collectible-card-sets-locations", "cent": "gta-6-100-completion-checklist-guide"}
PAGES_GB = {"missions": "gta-6/missions", "cheats": "gta-6/gta-6-cheats-ps5-cheat-codes", "cent": "articles/gta-6/gta-6-100-completion-guide-interactive-checklist"}
AUJ = __import__("datetime").date.today().isoformat()


def get(url):
    r = subprocess.run(["curl", "-s", "-L", "--max-time", "40", "-A", UA, url], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")


def texte(s):
    m = re.search(r'<div class="entry-content.*?(?=<div class="(?:post-nav|wpdiscuz|comments|sharedaddy)|<footer)', s, re.S)
    s = m.group(0) if m else s
    s = re.sub(r"<(script|style|nav|header)\b.*?</\1>", "", s, flags=re.S)
    s = re.sub(r"<(br|/p|/li|/h\d|/tr|/div)[^>]*>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\u2019", "'").replace("\u2013", "-").replace("\xa0", " ").replace("\u2026", "...")
    s = re.sub(r"[ \t]+", " ", s)
    return [l.strip() for l in s.split("\n") if l.strip()]


def norm(t):
    return re.sub(r"[^a-z0-9]+", " ", t.lower().replace("’", "'").replace("'", "")).strip()


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower().replace("'", "")).strip("-")[:60]


# ---------------------------------------------------------------- traduction (cache)
def traduit(textes, cache):
    """EN -> FR via Google, en lot, avec cache {en: fr}."""
    manq = [t for t in dict.fromkeys(textes) if t and t not in cache]
    if manq:
        from traduire import gtx
        for i in range(0, len(manq), 40):
            lot = manq[i:i + 40]
            res = gtx([html.escape(t, quote=False) for t in lot], "fr")
            for a, b in zip(lot, res): cache[a] = html.unescape(b).strip()
    return cache


# ---------------------------------------------------------------- régions (placement approximatif)
REG = [("leonida-keys", r"mariana|capri|key lento|hamlet|watson bay|keys"),
       ("grassrivers", r"buckskin|kowaachobee|swamp|moonflower|grassrivers"),
       ("kalaga", r"lummox|kalaga|moreau|tallaloko|millport|rushwood|macalister|adler creek"),
       ("port-gellhorn", r"leonard|gellhorn|waning sands|draper|druthers|red apple|manifest canyon|red rocks"),
       ("ambrosia", r"ambrosia|kelly county|emerald river|allied crystal|o.malley"),
       ("vice-city", r"vice|downtown|ocean beach|peacock|bayside|washington beach|rockridge|tequesta|vcia|dalton|balsero|little|navitrak|flea market")]


def region(*txts):
    t = " ".join(txts).lower()
    for rid, rx in REG:
        if re.search(rx, t): return rid
    return None


def place(points, CA):
    """Pose les points approximatifs en spirale autour du centre de leur région (repère schema-v1)."""
    C = {r["id"]: r["centre"] for r in CA["regions"]}
    rang = {}
    for p in points:
        if not p.get("region") or p["region"] not in C: p["x"] = p["y"] = None; continue
        i = rang.get(p["region"], 0); rang[p["region"]] = i + 1
        a, r = i * 2.39996, 14 + 11 * math.sqrt(i) * 2.2
        cx, cy = C[p["region"]]
        p["x"], p["y"] = round(cx + r * math.cos(a)), round(cy + 26 + r * math.sin(a))
        p["approx"] = True


# ---------------------------------------------------------------- analyses PowerPyx
def missions(L, gbt):
    gb = norm(" ".join(gbt))
    chap, cur, out = None, None, []
    try: L = L[L.index("Prologue"):]
    except ValueError: return []
    for l in L:
        if l.startswith("Strangers & Freaks"): break
        m = re.match(r"^(Prologue|Chapter (\d))$", l)
        if m:
            n = int(m.group(2) or 0)
            if not (cur and cur["n"] == n and l == "Prologue"):
                cur = {"n": n, "missions": []}; out.append(cur); continue
        if not cur: continue
        opt = l.startswith("Optional")
        t = re.sub(r"^Optional - ", "", l)
        t = re.sub(r"\s*\(\*?[A-Z ]+ONLY\*?\).*$", "", t)
        titre = re.sub(r"\s*\(.*$", "", t).strip()
        titre = re.sub(r"^\[[^\]]+\]\s*", "", titre).strip() or t
        if not titre: continue
        perso = "jason" if "JASON ONLY" in l else "lucia" if "LUCIA ONLY" in l else ""
        ok = norm(titre) in gb
        cur["missions"].append({"t": titre, "opt": opt, "perso": perso, "manquable": "Missable" in l or "MISSABLE" in l,
                                "statut": "confirme" if ok else "a_confirmer"})
    return out


def triches(L, gbt):
    gbs = "\n".join(gbt)
    blocs = {}
    for m in re.finditer(r"^(.+?) Cheat\n(.+?)\nHow to unlock: (.+?)\n(Combo TBA\n)?", gbs, re.M):
        blocs[norm(m.group(1))] = {"tba": bool(m.group(4)), "unlock": m.group(3)}
    out, cat = [], None
    for i, l in enumerate(L):
        m = re.match(r"^(.+?) Cheats \((\d+) Total\)$", l)
        if m: cat = m.group(1); continue
        if cat and l.startswith("Cheat Code:") and i >= 1:
            nom_eff = L[i - 1]
            if " - " not in nom_eff: continue
            nom, eff = nom_eff.split(" - ", 1)
            code = l.split(":", 1)[1].strip()
            unl = L[i + 1].split(":", 1)[1].strip() if i + 1 < len(L) and L[i + 1].startswith("Unlock") else ""
            g = blocs.get(norm(nom)) or blocs.get(norm(re.sub(r"^Spawn ", "", nom))) or next((v for k, v in blocs.items() if norm(nom) in k or k in norm(nom)), None)
            code_ok = code and "?" not in code and g and not g["tba"]
            out.append({"id": slug(nom), "cat": cat, "nom": nom.strip(), "en": eff.strip(), "deblocage_en": unl,
                        "code": code if "?" not in code else "", "statut": "confirme" if g else "a_confirmer",
                        "code_statut": "confirme" if code_ok else ("a_confirmer" if code and "?" not in code else "inconnu")})
    return out


def meditations(L):
    pts = []
    for i, l in enumerate(L):
        m = re.match(r"^Meditation Spot #(\d+) \(Meditations? [\d-]+\) - (.+?)(?: \[.*)?$", l)
        if not m: continue
        n, nom = int(m.group(1)), m.group(2).strip()
        loc = next((x for x in L[i + 1:i + 3] if x.startswith("Location:")), "")
        loc = loc.replace("Location:", "").strip()
        fr = None
        if n == 1:
            loc = "Jason's house balcony, Chapter 1 only (missable): talk to Lucia in the morning after she mentions meditating."
            fr = "Balcon de la maison de Jason, uniquement au chapitre 1 (manquable) : parlez à Lucia le matin, quand elle annonce qu'elle va méditer."
        if n == 10: loc = "Peak of Mount Kalaga, in the stone circle: appears on the map after completing all other meditations."
        pts.append({"id": f"meditation-{n:02d}", "couche": "meditation", "en": f"#{n} {nom}", "note_en": loc,
                    "region": region(loc, nom) if n != 1 else None})
        if fr: pts[-1]["note_fr"] = fr
    return pts


def drones(L):
    pts = []
    for i, l in enumerate(L):
        m = re.match(r"^Top Fun Drones #(\d+) - (.+)$", l)
        if not m: continue
        n, zone = int(m.group(1)), m.group(2).strip()
        courses = [x for x in L[i + 1:i + 4] if "Par Time" in x]
        pts.append({"id": f"drones-{n:02d}", "couche": "drones", "en": f"#{n} {zone}", "note_en": "Time trials: " + "; ".join(courses),
                    "note_fr": "Courses contre la montre : " + "; ".join(c.replace("Par Time", "temps à battre") for c in courses),
                    "region": region(zone, " ".join(courses))})
    return pts


def banques(L):
    pts, comte, grand = [], "", False
    for l in L:
        if re.match(r"^(Mariana|Vice-Dale|Leonard|Kelly|Lummox) County", l): comte = l
        if l.startswith("Large Banks (8"): grand = True
        m = re.match(r"^#(\d+) - (.+?) \((\$[\dk$\- ]+)\)$", l)
        if not m: continue
        n, nom, butin = int(m.group(1)), m.group(2), m.group(3)
        pts.append({"id": f"banques-{n:02d}", "couche": "banques", "en": f"#{n} {nom}",
                    "note_en": ("Large bank with vault" if grand else "Small bank: cash drawer + safe") + f", loot {butin}" + (f" ({comte})" if comte and not grand else ""),
                    "note_fr": ("Grande banque avec chambre forte" if grand else "Petite banque : tiroir-caisse + coffre") + f", butin {butin}" + (f" ({comte.replace('County', 'County')})" if comte and not grand else ""),
                    "region": region(nom, "" if grand else comte) or ("vice-city" if grand else None)})
    return pts


def garages(L):
    pts = []
    for l in L:
        m = re.match(r"^Garage #(\d+): (.+?)(?: - (\$[\d,]+))? \((\d) Parking Spots?\)$", l)
        if not m: continue
        n, nom, prix, pl = int(m.group(1)), m.group(2), m.group(3), m.group(4)
        note = (f"Buy via the Vice City Real Estate app: {prix}" if prix else "Story reward (not purchasable)") + f", {pl} parking spot{'s' if pl != '1' else ''}"
        nfr = (f"À acheter dans l'appli Vice City Real Estate : {prix.replace(',', ' ')}" if prix else "Offert par l'histoire (non achetable)") + f", {pl} place{'s' if pl != '1' else ''}"
        pts.append({"id": f"garages-{n:02d}", "couche": "garages", "en": f"#{n} {nom}", "note_en": note, "note_fr": nfr, "region": region(nom), "hors_trophee": not prix})
    return pts


def main():
    src = {k: texte(get(PP + v + "/")) for k, v in PAGES_PP.items()}
    gb = {k: texte(get(GB + v)) for k, v in PAGES_GB.items()}
    if len(src["walk"]) < 50 or len(gb["missions"]) < 50:
        print("soluce_import : sources injoignables, rien changé"); return
    CA = json.load(open("data/carte.json", encoding="utf-8"))
    G6 = json.load(open("data/soluce/gta6.json", encoding="utf-8"))
    cache = G6.setdefault("_trad", {})
    gb100 = norm(" ".join(gb["cent"]))
    pp100 = norm(" ".join(src["cent"]))
    # --- points
    nouv = {"meditation": (meditations(src["medit"]), "medit", "18 meditation spots"),
            "drones": (drones(src["drones"]), "drones", "42 of 42 drone time trials"),
            "banques": (banques(src["banks"]), "banks", "22 of 22 bank jobs"),
            "garages": (garages(src["garages"]), "garages", None)}
    pts = []
    for couche, (lst, cle, controle) in nouv.items():
        compte_ok = bool(controle and norm(controle) in gb100 and norm(controle) in pp100)
        for p in lst:
            p.update({"statut": "a_confirmer", "sources": [PP + PAGES_PP[cle] + "/"] + ([GB + PAGES_GB["cent"]] if compte_ok else []), "maj": AUJ})
        pts += lst
    # points ajoutés à la main (autres sources) : gardés
    gardes = [p for p in CA.get("points", []) if p.get("couche") not in nouv]
    place(pts, CA)
    traduit([p["note_en"] for p in pts if "note_fr" not in p], cache)
    for p in pts:
        p["fr"] = p["en"]
        if "note_fr" not in p: p["note_fr"] = cache[p["note_en"]]
    CA["points"] = gardes + pts
    # totaux confirmés par les deux check-lists 100 %
    tot = {"meditation": 18, "drones": 14, "banques": 22, "garages": 8, "cartes": 18}
    for c in CA["couches"]:
        if c["id"] in tot: c["total"] = tot[c["id"]]
        if c["id"] == "drones":
            c["note_fr"] = "14 lieux, 3 courses contre la montre chacun (42 au total). Gagner une course par lieu débloque le trophée Top Fun."
            c["note_en"] = "14 locations, 3 time trials each (42 total). Win one race per location for the Top Fun trophy."
        if c["id"] == "banques":
            c["note_fr"] = "22 banques : 14 petites (tiroir-caisse + coffre) et 8 grandes avec chambre forte. Piller 5 chambres fortes débloque Maximum Withdrawal."
            c["note_en"] = "22 banks: 14 small (cash drawer + safe) and 8 large with a vault. Rob 5 vaults for Maximum Withdrawal."
        if c["id"] == "garages":
            c["note_fr"] = "8 garages à acheter (160 000 $ au total, appli Vice City Real Estate après la mission Daily Driver) + 4 offerts par l'histoire."
            c["note_en"] = "8 purchasable garages ($160,000 total, Vice City Real Estate app after Daily Driver) + 4 story garages."
        if c["id"] == "cartes":
            c["note_fr"] = "18 séries, 480 cartes. 3 séries complètes pour le trophée Don't Touch My Deck, 15 pour le 100 %."
            c["note_en"] = "18 sets, 480 cards. 3 full sets for Don't Touch My Deck, 15 for 100% completion."
    # --- missions et triches
    ch = missions(src["walk"], gb["missions"])
    if ch:
        G6["chapitres"] = ch
        G6["missions_sources"] = [PP + PAGES_PP["walk"] + "/", GB + PAGES_GB["missions"]]
    tr = triches(src["cheats"], gb["cheats"])
    if tr:
        traduit([t["en"] for t in tr] + [t["deblocage_en"] for t in tr], cache)
        for t in tr: t["fr"] = cache[t["en"]]; t["deblocage_fr"] = cache[t["deblocage_en"]]
        G6["triches"] = tr
        G6["triches_sources"] = [PP + PAGES_PP["cheats"] + "/", GB + PAGES_GB["cheats"]]
    G6["maj"] = AUJ
    json.dump(CA, open("data/carte.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(G6, open("data/soluce/gta6.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nm = sum(len(c["missions"]) for c in ch)
    print(f"soluce_import : {len(pts)} points, {nm} missions ({sum(m['statut']=='confirme' for c in ch for m in c['missions'])} confirmées), {len(tr)} triches ({sum(t['code_statut']=='confirme' for t in tr)} codes confirmés)")


if __name__ == "__main__":
    main()
