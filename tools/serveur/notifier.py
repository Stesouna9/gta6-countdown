#!/usr/bin/env python3
"""Envoie une notification push aux abonnés quand un nouvel article paraît (ou message forcé).
Usage : notifier.py            -> vérifie data/articles.json du site, envoie si nouvel id
        notifier.py "Titre" "Texte" "URL"   -> envoi manuel
État : /var/lib/mur/push_etat.json. Base : /var/lib/mur/mur.db (table push)."""
import json, os, sqlite3, sys, time
from pywebpush import webpush, WebPushException

DIR = "/var/lib/mur"; SITE = "/var/www/gtavifrance"; ETAT = os.path.join(DIR, "push_etat.json")
KEY = os.path.join(DIR, "private_key.pem"); CLAIMS = {"sub": "mailto:radio@vicebayradio.com"}

def envoyer(titre_par_langue, texte_par_langue, url, tag="vi"):
    c = sqlite3.connect(os.path.join(DIR, "mur.db")); rows = c.execute("SELECT endpoint, sub, l FROM push").fetchall()
    ok = ko = 0
    for endpoint, sub, l in rows:
        t = titre_par_langue.get(l) or titre_par_langue.get("en") or titre_par_langue["fr"]
        x = texte_par_langue.get(l) or texte_par_langue.get("en") or texte_par_langue["fr"]
        u = url if l == "fr" or "/journal/" not in url else url.replace("gtavifrance.com/journal/", f"gtavifrance.com/{l}/journal/")
        try:
            webpush(json.loads(sub), json.dumps({"t": t, "x": x, "u": u, "tag": tag}), vapid_private_key=KEY, vapid_claims=dict(CLAIMS), ttl=86400); ok += 1
        except WebPushException as e:
            ko += 1
            if e.response is not None and e.response.status_code in (404, 410): c.execute("DELETE FROM push WHERE endpoint=?", (endpoint,))
        except Exception: ko += 1
    c.commit(); c.close(); print(f"push: {ok} ok, {ko} ko, {len(rows)} abonnés")

if __name__ == "__main__":
    if len(sys.argv) >= 4:
        envoyer({"fr": sys.argv[1]}, {"fr": sys.argv[2]}, sys.argv[3], tag="manuel"); sys.exit()
    arts = json.load(open(os.path.join(SITE, "data/articles.json"), encoding="utf-8"))
    etat = json.load(open(ETAT)) if os.path.exists(ETAT) else {}
    if not arts: sys.exit()
    a = arts[0]
    if a["id"] == etat.get("dernier"):
        sys.exit()
    if not etat.get("dernier"):  # première exécution : on mémorise sans envoyer
        json.dump({"dernier": a["id"]}, open(ETAT, "w")); sys.exit()
    titres = {l: v["t"] for l, v in a.items() if isinstance(v, dict) and "t" in v}
    textes = {l: v["d"] for l, v in a.items() if isinstance(v, dict) and "d" in v}
    envoyer(titres, textes, f"https://gtavifrance.com/journal/{a['id']}.html", tag=a["id"])
    json.dump({"dernier": a["id"], "t": int(time.time())}, open(ETAT, "w"))
