#!/usr/bin/env python3
"""Veille des sources officielles GTA 6 : Rockstar Newswire, YouTube Rockstar, r/GTA6 (nouveautés).
Écrit un JSON {maj, items:[{src, prio, t, u, d, nouveau}]} ; 'nouveau' = jamais vu au passage précédent (état dans <sortie>.vu).
Usage : python3 tools/veille.py [sortie.json]   (serveur : cron 5 min -> live/veille.json ; GitHub : data/veille.json)
Ne casse rien si une source tombe : chaque source est isolée."""
import json, re, sys, html, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from update import rockstar, UA_NAV

SORTIE = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "data" / "veille.json")
ATOM = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
GTA = re.compile(r"GTA|Grand Theft Auto|Vice City|Leonida|Lucia|Jason|Rockstar|VI\b", re.I)

def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA_NAV), timeout=25).read()

def newswire():
    return [{"src": "Rockstar Newswire", "prio": 1, "t": r.get("en") or r.get("fr") or "", "u": r["u"], "d": r.get("d", "")} for r in rockstar()]

def youtube():
    x = ET.fromstring(get("https://www.youtube.com/feeds/videos.xml?channel_id=UCULwHhkI31JHAKe57LZdzcA"))
    out = []
    for e in x.findall("a:entry", ATOM)[:10]:
        t = e.findtext("a:title", "", ATOM)
        if GTA.search(t): out.append({"src": "YouTube Rockstar", "prio": 1, "t": t, "u": "https://www.youtube.com/watch?v=" + e.findtext("yt:videoId", "", ATOM), "d": e.findtext("a:published", "", ATOM)})
    return out

def reddit():
    x = ET.fromstring(get("https://www.reddit.com/r/GTA6/top/.rss?t=day"))
    out = []
    for e in x.findall("a:entry", ATOM)[:10]:
        link = e.find("a:link", ATOM)
        out.append({"src": "r/GTA6", "prio": 2, "t": html.unescape(e.findtext("a:title", "", ATOM)), "u": link.get("href") if link is not None else "", "d": e.findtext("a:updated", "", ATOM)})
    return out

def main():
    vu_f = SORTIE.with_suffix(".vu")
    vu = set(vu_f.read_text().split()) if vu_f.exists() else None
    items = []
    for nom, f in (("newswire", newswire), ("youtube", youtube), ("reddit", reddit)):
        try: items += f()
        except Exception as e: print("veille", nom, str(e)[:100])
    for it in items: it["nouveau"] = bool(vu is not None and it["u"] and it["u"] not in vu)
    items.sort(key=lambda x: (x["d"] or ""), reverse=True)
    SORTIE.write_text(json.dumps({"maj": datetime.now(timezone.utc).isoformat(timespec="seconds"), "items": items}, ensure_ascii=False, indent=1))
    vu_f.write_text("\n".join(sorted((vu or set()) | {i["u"] for i in items if i["u"]})))
    n = [i for i in items if i["nouveau"]]
    print(f"veille : {len(items)} éléments, {len(n)} nouveaux" + "".join(f"\n  NOUVEAU [{i['src']}] {i['t'][:80]}" for i in n))

if __name__ == "__main__":
    main()
