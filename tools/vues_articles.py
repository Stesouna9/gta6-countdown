#!/usr/bin/env python3
"""Vues par article (toutes langues cumulées) depuis la base GoatCounter locale -> live/vues_articles.json {id: vues}. Lancé toutes les 5 min par cron (serveur Sites)."""
import json, re, sqlite3, sys, os
DB = "file:/opt/goatcounter/db.sqlite3?mode=ro"
OUT = sys.argv[1] if len(sys.argv) > 1 else "live/vues_articles.json"
c = sqlite3.connect(DB, uri=True)
tot = {}
for path, n in c.execute("select p.path, sum(h.total) from hit_counts h join paths p on p.path_id=h.path_id where p.path like '%/journal/%.html' group by p.path"):
    m = re.search(r"/journal/([^/]+)\.html$", path)
    if m: tot[m.group(1)] = tot.get(m.group(1), 0) + int(n or 0)
os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
json.dump(tot, open(OUT + ".tmp", "w"), separators=(",", ":")); os.replace(OUT + ".tmp", OUT)
print(len(tot), "articles")
