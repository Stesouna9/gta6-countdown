"""Routine X quotidienne de @GTAfance (14/10/2026, demande de Gabriel) : 3 posts par jour, format validé ce jour-là.
  9 h  actu   : l'article du jour le plus récent (hors Cyberleek)
  13 h site   : compte à rebours J-xx + un angle du site (visuel généré : J-xx sur l'affiche, gtavifrance.com)
  19 h cyberleek : le dernier article Cyberleek (image = logo Cyberleek de l'article, jamais de contenu fuité)
Texte ≤ 260 caractères, SANS lien (« lien en bio », 0,015 $ le post), hashtags #GTA6 #GTAVI #GTA6France + thème, 1 image.
Jamais deux fois le même article (x_routine_etat.json). Clés : /etc/gtavifrance-relais.env (X_API_KEY, X_API_SECRET,
X_ACCESS_TOKEN, X_ACCESS_SECRET). Crédits API nécessaires (carte ajoutée par Gabriel dans console.x.com).
Usage : python3 tools/x_routine.py actu|site|cyberleek [--sec]   (--sec : affiche le post sans publier)"""
import base64, datetime, hashlib, hmac, io, json, os, re, secrets, sys, time, urllib.parse, urllib.request, uuid
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ETAT = Path(os.environ.get("X_ETAT", "/var/lib/gtavifrance/x_routine_etat.json"))  # hors du dossier web
SORTIE = datetime.date(2026, 11, 19)
TAGS = "#GTA6 #GTAVI #GTA6France"
SEC = "--sec" in sys.argv

def E(k, d=""):
    if k in os.environ: return os.environ[k]
    try:
        for l in open("/etc/gtavifrance-relais.env", encoding="utf-8"):
            if l.startswith(k + "="): return l.split("=", 1)[1].strip().strip('"')
    except OSError: pass
    return d

def _oauth1(method, url):
    p = {"oauth_consumer_key": E("X_API_KEY"), "oauth_nonce": secrets.token_hex(16), "oauth_signature_method": "HMAC-SHA1",
         "oauth_timestamp": str(int(time.time())), "oauth_token": E("X_ACCESS_TOKEN"), "oauth_version": "1.0"}
    q = lambda v: urllib.parse.quote(str(v), safe="~")
    base = "&".join([method, q(url), q("&".join(f"{q(k)}={q(v)}" for k, v in sorted(p.items())))])
    key = q(E("X_API_SECRET")) + "&" + q(E("X_ACCESS_SECRET"))
    p["oauth_signature"] = base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    return "OAuth " + ", ".join(f'{q(k)}="{q(v)}"' for k, v in sorted(p.items()))

def upload(img):
    """Image → media_id (v1.1 media/upload, multipart : le corps n'entre pas dans la signature OAuth)."""
    u = "https://upload.twitter.com/1.1/media/upload.json"
    b = uuid.uuid4().hex
    corps = (f"--{b}\r\nContent-Disposition: form-data; name=\"media\"; filename=\"x.jpg\"\r\nContent-Type: image/jpeg\r\n\r\n").encode() + img + f"\r\n--{b}--\r\n".encode()
    r = urllib.request.Request(u, data=corps, headers={"Authorization": _oauth1("POST", u), "Content-Type": f"multipart/form-data; boundary={b}"})
    return json.load(urllib.request.urlopen(r, timeout=60))["media_id_string"]

def tweet(texte, media_id):
    u = "https://api.x.com/2/tweets"
    r = urllib.request.Request(u, data=json.dumps({"text": texte, "media": {"media_ids": [media_id]}}).encode(),
                               headers={"Authorization": _oauth1("POST", u), "Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r, timeout=30))["data"]["id"]

def coupe(s, n):
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) <= n: return s
    s = s[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return s + "…"

def compose(tete, corps, theme):
    pied = "(lien en bio)\n" + TAGS + (" " + theme if theme else "")
    reste = 255 - len(tete) - len(pied) - 4   # marge : X compte les emojis double
    return f"{tete}\n{coupe(corps, max(reste, 40))}\n{pied}" if corps else f"{tete}\n{pied}"

def image_article(a):
    f = RACINE / "assets/img/articles" / f"{a['id']}.jpg"
    return f.read_bytes() if f.exists() else None

def visuel_jours(j):
    """Affiche du site + gros « J-xx » + bandeau gtavifrance.com (Pillow)."""
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    im = ImageOps.fit(Image.open(RACINE / "assets/img/vi-une.jpg").convert("RGB"), (1600, 900))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle([0, 0, 760, 900], fill=(22, 17, 29, 215))
    polices = sorted((RACINE / "tools/fonts").glob("*nton*"))
    f = lambda n: ImageFont.truetype(str(polices[0]), n) if polices else ImageFont.load_default()
    d.text((70, 120), "GTA VI", font=f(90), fill=(242, 232, 213))
    d.text((60, 220), f"J-{j}", font=f(330), fill=(255, 138, 61))
    d.text((70, 620), "SORTIE LE 19 NOVEMBRE 2026", font=f(52), fill=(255, 59, 122))
    d.text((70, 720), "GTAVIFRANCE.COM", font=f(64), fill=(242, 232, 213))
    o = io.BytesIO(); im.save(o, "JPEG", quality=88); return o.getvalue()

ANGLES = [  # 13 h : un angle du site par jour, en rotation
    ("⏳", "Le compte à rebours GTA 6 tourne à la seconde, façon panneau d'aéroport, jusqu'à minuit heure de chez vous.", "#ViceCity"),
    ("💶", "Prix, éditions standard et Ultimate, coffret The Goodtime State : tout est vérifié et à jour sur le site.", "#ViceCity"),
    ("📻", "Vice Bay Radio tourne en direct sur le site : les sons de Vice City en attendant le 19 novembre.", "#ViceCity"),
    ("🗺️", "Leonida, Vice City, les personnages, les trailers : notre guide GTA 6 rassemble tout ce qui est confirmé.", "#Leonida"),
    ("🌍", "L'actu GTA 6 vérifiée, chaque jour, en 17 langues. Et l'heure de sortie dans chaque pays.", "#ViceCity"),
]

def main():
    slot = next((a for a in sys.argv[1:] if not a.startswith("--")), "actu")
    etat = json.loads(ETAT.read_text()) if ETAT.exists() else {"postes": [], "journal": []}
    arts = json.load(open(RACINE / "data/articles.json", encoding="utf-8"))
    arts.sort(key=lambda a: a.get("date", ""), reverse=True)
    j = (SORTIE - datetime.date.today()).days
    if slot == "site":
        e, txt, th = ANGLES[datetime.date.today().toordinal() % len(ANGLES)]
        texte, img, cle = compose(f"{e} J-{j} avant GTA 6.", txt, th), visuel_jours(j), f"site-{datetime.date.today()}"
    else:
        cyb = slot == "cyberleek"
        cands = [a for a in arts if ("cyberleek" in a["id"]) == cyb and a["id"] not in etat["postes"]
                 and isinstance(a.get("fr"), dict) and image_article(a)][:5]
        if not cands: print(f"{slot} : rien de nouveau à poster"); return
        a = cands[0]
        texte = compose(("🔒 " if cyb else "🚨 ") + a["fr"]["t"], a["fr"].get("d", ""), "#Cyberleek" if cyb else "#ViceCity")
        img, cle = image_article(a), a["id"]
    if SEC: print(texte, f"\n[{len(texte)} car., image {len(img)} o]"); return
    try:
        pid = tweet(texte, upload(img))
    except urllib.error.HTTPError as e:
        print(f"{slot} : échec X {e.code} {e.read()[:200]!r}"); sys.exit(1)
    etat["postes"].append(cle); etat["postes"] = etat["postes"][-300:]
    etat["journal"].append({"quand": datetime.datetime.now().isoformat(timespec="minutes"), "slot": slot, "id": pid, "cle": cle})
    ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
    print(f"{slot} : posté https://x.com/GTAfance/status/{pid}")

if __name__ == "__main__":
    main()
