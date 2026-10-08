#!/usr/bin/env python3
"""Collecte exhaustive de la presse GTA 6 depuis le 04/02/2022, semaine par semaine (Google News RSS, en + fr).
Ajoute à data/archives.json des entrées {date, titre, s, gn, u:"", txt:"", lang, fait:false}. Le texte est récupéré ensuite par archives_texte.py."""
import json, os, sys, time, datetime, html, re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path
from email.utils import parsedate_to_datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); os.chdir(Path(__file__).resolve().parent.parent)
from update import get
PREF = ("rockstargames.com","take2games.com","ign.com","theverge.com","bbc.","bloomberg.com","gamespot.com","eurogamer.","polygon.com","pcgamer.com","kotaku.com","variety.com","reuters.com","videogameschronicle.com","gamesradar.com","jeuxvideo.com","gamekult.com","numerama.com","journaldugeek.com","lemonde.fr","ouest-france.fr","bfmtv.com","20minutes.fr","gamergen.com","millenium.org")
Q = {"en": ('"GTA 6" OR "GTA VI" OR "Grand Theft Auto VI"', "en-US", "US", "US:en", 8), "fr": ('"GTA 6" OR "GTA VI"', "fr", "FR", "FR:fr", 4)}
out = Path("data/archives.json"); arch = json.load(open(out, encoding="utf-8")) if out.exists() else []
vus = {re.sub(r"\W+", " ", (x.get("titre") or "").lower())[:60] for x in arch}
debut = datetime.date(2022, 2, 1); fin = datetime.date.today()
j = debut; n = 0
while j < fin:
    k = min(j + datetime.timedelta(days=7), fin)
    for lang, (q, hl, gl, ceid, lim) in Q.items():
        url = "https://news.google.com/rss/search?q=" + urllib.request.quote(f"{q} after:{j} before:{k}") + f"&hl={hl}&gl={gl}&ceid={ceid}"
        items = []
        for essai in range(3):
            try:
                for it in ET.fromstring(get(url)).iter("item"):
                    src = it.find("source"); t = html.unescape(it.findtext("title") or "")
                    s = src.text if src is not None else ""; su = src.get("url", "") if src is not None else ""
                    t = re.sub(r"\s+-\s+" + re.escape(s) + r"$", "", t) if s else t
                    try: d = parsedate_to_datetime(it.findtext("pubDate")).date().isoformat()
                    except Exception: d = j.isoformat()
                    items.append({"date": d, "titre": t, "s": s, "su": su, "gn": it.findtext("link"), "lang": lang})
                break
            except Exception as e:
                time.sleep(5 * (essai + 1))
        items.sort(key=lambda x: (0 if any(p in x["su"] for p in PREF) else 1, x["date"]))
        pris = 0
        for x in items:
            cle = re.sub(r"\W+", " ", x["titre"].lower())[:60]
            if cle in vus or not x["titre"]: continue
            vus.add(cle); del x["su"]; x.update({"u": "", "txt": "", "fait": False}); arch.append(x); pris += 1; n += 1
            if pris >= lim: break
        time.sleep(1.2)
    print(j, n, flush=True)
    if n % 200 < 12: arch.sort(key=lambda x: x["date"]); json.dump(arch, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    j = k
arch.sort(key=lambda x: x["date"]); json.dump(arch, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("total", len(arch))
