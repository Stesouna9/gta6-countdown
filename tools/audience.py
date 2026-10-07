#!/usr/bin/env python3
"""Bilan d'audience hebdo depuis la base GoatCounter locale (serveur). Écrit data/audience.json (hors git), lisible sur /data/audience.json."""
import datetime, json, sqlite3, sys
DB = sys.argv[1] if len(sys.argv) > 1 else "/opt/goatcounter/db.sqlite3"
c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
site = [r[0] for r in c.execute("select site_id from sites where cname like '%gtavifrance%' or code like '%gta%'")]
sid = site[0] if site else 1
since = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
def q(sql, *a): return c.execute(sql, a).fetchall()
pages = q("select p.path, sum(h.total) from hit_counts h join paths p on p.path_id=h.path_id where h.site_id=? and h.hour>=? group by p.path order by 2 desc limit 20", sid, since)
refs = q("select r.ref, sum(h.total) from ref_counts h join refs r on r.ref_id=h.ref_id where h.site_id=? and h.hour>=? group by r.ref order by 2 desc limit 15", sid, since)
total = q("select sum(total) from hit_counts where site_id=? and hour>=?", sid, since)[0][0] or 0
jours = q("select substr(hour,1,10) d, sum(total) from hit_counts where site_id=? and hour>=? group by d order by d", sid, since)
out = {"depuis": since, "total7j": total, "pages": pages, "sources": refs, "jours": jours, "genere": datetime.datetime.now().isoformat(timespec="minutes")}
json.dump(out, open("data/audience.json", "w"), ensure_ascii=False, indent=1)
print(f"audience 7 j : {total} vues, top : {pages[:3]}")
