#!/usr/bin/env python3
"""Relais automatique des nouveaux articles vers Telegram, Bluesky et Discord (API gratuites).
Secrets dans l'environnement (jamais dans git) : TELEGRAM_TOKEN + TELEGRAM_CHAT ; BSKY_HANDLE + BSKY_APP_PASSWORD ; DISCORD_WEBHOOK ;
X_API_KEY + X_API_SECRET + X_ACCESS_TOKEN + X_ACCESS_SECRET (OAuth 1.0a, app Read and write) ET X_VALIDE=1 (règle d'or : posé seulement après validation par Gabriel du texte exact du 1er post et du format ; X_MODE=direct (défaut) : titre + lien, 0,20 $/post ; X_MODE=texte : titre seul, 0,015 $ ; X_MODE=reply : titre puis lien en réponse. X publie au plus 1 article tous les 2 jours : le meilleur des 48 h).
Un canal sans secret est ignoré. 1er passage : marque tous les articles existants comme déjà relayés (pas d'inondation).
Usage : python3 tools/relais.py [etat.json]   (serveur : cron 5 min, EnvironmentFile /etc/gtavifrance-relais.env)
        RELAIS_DRY=1 : affiche sans publier."""
import base64, hashlib, hmac, json, os, re, secrets, sys, time, urllib.request, urllib.parse
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

def _oauth1(method, url):
    p = {"oauth_consumer_key": E("X_API_KEY"), "oauth_nonce": secrets.token_hex(16), "oauth_signature_method": "HMAC-SHA1",
         "oauth_timestamp": str(int(time.time())), "oauth_token": E("X_ACCESS_TOKEN"), "oauth_version": "1.0"}
    q = lambda v: urllib.parse.quote(str(v), safe="~")
    base = "&".join([method, q(url), q("&".join(f"{q(k)}={q(v)}" for k, v in sorted(p.items())))])
    key = q(E("X_API_SECRET")) + "&" + q(E("X_ACCESS_SECRET"))
    p["oauth_signature"] = base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    return "OAuth " + ", ".join(f'{q(k)}="{q(v)}"' for k, v in sorted(p.items()))

def _tweet(body):
    u = "https://api.x.com/2/tweets"
    return post_json(u, body, {"Authorization": _oauth1("POST", u)})

def x(t, u):
    if not all(E(k) for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")): return None
    if E("X_VALIDE") != "1": return "en attente de validation (X_VALIDE)"
    if E("X_MODE", "direct") == "texte":  # sans lien : 0,015 $ le post au lieu de 0,20 $ avec URL
        _tweet({"text": t[:280]}); return True
    if E("X_MODE", "direct") == "direct":
        _tweet({"text": (t[:255] + "\n" + u)}); return True
    r = _tweet({"text": t[:280]})
    _tweet({"text": u, "reply": {"in_reply_to_tweet_id": r["data"]["id"]}})
    return True

def x_meilleur(arts, etat):
    """X : 1 post tous les 2 jours = le meilleur article des 48 h (vues GoatCounter, puis alerte 🚨, puis le plus récent), titre + lien (0,20 $)."""
    if E("X_VALIDE") != "1" and not DRY: return
    now = datetime.now(timezone.utc)
    der = etat.get("x_dernier")
    if der and (now - datetime.fromisoformat(der)).total_seconds() < 47 * 3600: return
    try: vues = json.load(open(RACINE / "live" / "vues_articles.json"))
    except Exception: vues = {}
    ok = []
    for a in arts:
        try: age = (now - datetime.fromisoformat(a["date"])).total_seconds()
        except Exception: continue
        if age <= 48 * 3600 and a["id"] not in etat.get("x_faits", []): ok.append(a)
    if not ok: return
    m = max(ok, key=lambda a: (vues.get(a["id"], 0), "🚨" in (a.get("fr") or {}).get("t", ""), a["date"]))
    t = (m.get("fr") or {}).get("t") or m["id"]; u = f"{BASE}journal/{m['id']}.html"
    if DRY: print("DRY X", t, u); return
    r = x(t, u)
    print("relais X", m["id"], r)
    if r is True: etat["x_dernier"] = now.isoformat(); etat.setdefault("x_faits", []).append(m["id"])

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
    x_meilleur(arts, etat)
    if not DRY: etat["faits"] = sorted(faits); ETAT.write_text(json.dumps(etat))

if __name__ == "__main__":
    main()
