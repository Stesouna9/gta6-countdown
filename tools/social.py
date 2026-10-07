#!/usr/bin/env python3
"""Post quotidien automatique (image du jour + texte) sur Mastodon et Bluesky.
   Ne fait rien tant que les secrets ne sont pas posés (MASTODON_URL, MASTODON_TOKEN, BSKY_HANDLE, BSKY_PASS).
   Un seul post par jour et par réseau (marqueur data/social_last.json)."""
import datetime, json, os, re, urllib.request

BASE = "https://gtavifrance.com/"
SORTIE = datetime.date(2026, 11, 19)
J = (SORTIE - datetime.date.today()).days
TXT = {
    "fr": f"J-{J}. GTA VI sort le 19 novembre 2026. L'heure exacte chez toi, les faits vérifiés et le point du jour : {BASE}aujourdhui.html #GTA6 #GTAVI",
    "en": f"{J} days to go. GTA VI launches November 19, 2026. Release time in your city, verified facts and today's briefing: {BASE}en/today.html #GTA6 #GTAVI",
}
MARK = "data/social_last.json"
try: last = json.load(open(MARK))
except Exception: last = {}
today = datetime.date.today().isoformat()

def http(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    with urllib.request.urlopen(req, timeout=30) as r: return r.status, r.read()

def mastodon():
    u, tok = os.environ.get("MASTODON_URL"), os.environ.get("MASTODON_TOKEN")
    if not (u and tok) or last.get("mastodon") == today: return
    u = u.rstrip("/")
    # image
    img = open("assets/jn-fr.jpg", "rb").read()
    bnd = "----gta6"
    body = (f"--{bnd}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"jn.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n").encode() + img + f"\r\n--{bnd}\r\nContent-Disposition: form-data; name=\"description\"\r\n\r\nJ-{J} avant GTA VI\r\n--{bnd}--\r\n".encode()
    st, r = http(f"{u}/api/v2/media", body, {"Authorization": f"Bearer {tok}", "Content-Type": f"multipart/form-data; boundary={bnd}"})
    mid = json.loads(r)["id"]
    st, r = http(f"{u}/api/v1/statuses", json.dumps({"status": TXT["fr"] + "\n\n" + TXT["en"], "media_ids": [mid], "language": "fr"}).encode(),
                 {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    last["mastodon"] = today; print("mastodon", st)

def bluesky():
    h, pw = os.environ.get("BSKY_HANDLE"), os.environ.get("BSKY_PASS")
    if not (h and pw) or last.get("bluesky") == today: return
    api = "https://bsky.social/xrpc/"
    st, r = http(api + "com.atproto.server.createSession", json.dumps({"identifier": h, "password": pw}).encode(), {"Content-Type": "application/json"})
    s = json.loads(r); auth = {"Authorization": "Bearer " + s["accessJwt"]}
    img = open("assets/jn.jpg", "rb").read()
    st, r = http(api + "com.atproto.repo.uploadBlob", img, {**auth, "Content-Type": "image/jpeg"})
    blob = json.loads(r)["blob"]
    text = TXT["en"]
    facets = []
    for m in re.finditer(r"https?://\S+", text):
        b0 = len(text[:m.start()].encode()); b1 = len(text[:m.end()].encode())
        facets.append({"index": {"byteStart": b0, "byteEnd": b1}, "features": [{"$type": "app.bsky.richtext.facet#link", "uri": m.group(0)}]})
    rec = {"$type": "app.bsky.feed.post", "text": text, "createdAt": datetime.datetime.now(datetime.timezone.utc).isoformat(), "facets": facets,
           "embed": {"$type": "app.bsky.embed.images", "images": [{"alt": f"{J} days until GTA VI", "image": blob}]}, "langs": ["en"]}
    st, r = http(api + "com.atproto.repo.createRecord", json.dumps({"repo": s["did"], "collection": "app.bsky.feed.post", "record": rec}).encode(), {**auth, "Content-Type": "application/json"})
    last["bluesky"] = today; print("bluesky", st)

for f in (mastodon, bluesky):
    try: f()
    except Exception as e: print(f.__name__, "erreur :", e)
json.dump(last, open(MARK, "w"))
