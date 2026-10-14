#!/usr/bin/env python3
"""Relais automatique des nouveaux articles vers Telegram, Bluesky et Discord (API gratuites).
Secrets dans l'environnement (jamais dans git) : TELEGRAM_TOKEN + TELEGRAM_CHAT ; BSKY_HANDLE + BSKY_APP_PASSWORD ; DISCORD_WEBHOOK.
Un canal sans secret est ignoré. 1er passage : marque tous les articles existants comme déjà relayés (pas d'inondation).
Usage : python3 tools/relais.py [etat.json]   (serveur : cron 5 min, EnvironmentFile /etc/gtavifrance-relais.env)
        RELAIS_DRY=1 : affiche sans publier."""
import json, os, re, sys, urllib.request, urllib.parse
from datetime import datetime, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ETAT = Path(sys.argv[1] if len(sys.argv) > 1 else RACINE / "relais_etat.json")
BASE = "https://gtavifrance.com/"
DRY = bool(os.environ.get("RELAIS_DRY"))
MAX = int(os.environ.get("RELAIS_MAX", "3"))
E = os.environ.get

def post_json(url, body, headers=None):
    rq = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json", "User-Agent": "gtavifrance-relais", **(headers or {})})
    return json.loads(urllib.request.urlopen(rq, timeout=25).read() or b"{}")

def telegram(t, u):
    if not (E("TELEGRAM_TOKEN") and E("TELEGRAM_CHAT")): return None
    post_json(f"https://api.telegram.org/bot{E('TELEGRAM_TOKEN')}/sendMessage", {"chat_id": E("TELEGRAM_CHAT"), "text": f"{t}\n{u}"})
    return True

def discord(t, u):
    if not E("DISCORD_WEBHOOK"): return None
    post_json(E("DISCORD_WEBHOOK"), {"content": f"**{t}**\n{u}"})
    return True

def bluesky(t, u, d, img):
    if not (E("BSKY_HANDLE") and E("BSKY_APP_PASSWORD")): return None
    s = post_json("https://bsky.social/xrpc/com.atproto.server.createSession", {"identifier": E("BSKY_HANDLE"), "password": E("BSKY_APP_PASSWORD")})
    txt = f"{t}\n{u}"
    if len(txt) > 300: txt = t[:300 - len(u) - 2] + "…\n" + u
    b = txt.encode(); i = b.find(u.encode())
    rec = {"$type": "app.bsky.feed.post", "text": txt, "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "langs": ["fr"],
           "facets": [{"index": {"byteStart": i, "byteEnd": i + len(u.encode())}, "features": [{"$type": "app.bsky.richtext.facet#link", "uri": u}]}],
           "embed": {"$type": "app.bsky.embed.external", "external": {"uri": u, "title": t[:300], "description": (d or "")[:300]}}}
    post_json("https://bsky.social/xrpc/com.atproto.repo.createRecord", {"repo": s["did"], "collection": "app.bsky.feed.post", "record": rec}, {"Authorization": "Bearer " + s["accessJwt"]})
    return True

def main():
    arts = json.load(open(RACINE / "data" / "articles.json", encoding="utf-8"))
    etat = json.loads(ETAT.read_text()) if ETAT.exists() else None
    if etat is None:
        ETAT.write_text(json.dumps({"faits": [a["id"] for a in arts]})); print("relais : initialisé,", len(arts), "articles marqués"); return
    faits = set(etat["faits"]); nouveaux = [a for a in arts if a["id"] not in faits][:MAX]
    for a in reversed(nouveaux):
        f = a.get("fr") or {}; t = f.get("t") or a["id"]; u = f"{BASE}journal/{a['id']}.html"
        res = {}
        if DRY: print("DRY", t, u); continue
        for nom, fn in (("telegram", lambda: telegram(t, u)), ("discord", lambda: discord(t, u)), ("bluesky", lambda: bluesky(t, u, f.get("d"), a.get("img")))):
            try: res[nom] = fn()
            except Exception as e: res[nom] = "ERR " + str(e)[:80]
        print("relais", a["id"], res)
        faits.add(a["id"])
    if not DRY: ETAT.write_text(json.dumps({"faits": sorted(faits)}))

if __name__ == "__main__":
    main()
