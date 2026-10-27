"""Routine X quotidienne de @gtavifrancecom (14/10/2026, demande de Gabriel) : 3 posts par jour, format validé ce jour-là.
  9 h  actu   : l'article du jour le plus récent (hors Cyberleek)
  13 h site   : compte à rebours J-xx + un angle du site (visuel généré : J-xx sur l'affiche, gtavifrance.com)
  19 h top    : l'article le plus vu des dernières 24 h (GoatCounter, toutes langues), sinon le plus récent pas encore posté.
               Cyberleek seulement s'il est cet article le plus vu (décision Gabriel 14/10 : 3 posts par jour, pas de créneau Cyberleek).
Texte long (≤ 1 100 car., X Premium+ depuis le 22/10), lien de l'article en réponse (x_chrome.py), hashtags #GTA6 #GTAVI #GTA6France + thème, 1 image.
Jamais deux fois le même article (x_routine_etat.json). Clés : /etc/gtavifrance-relais.env (X_API_KEY, X_API_SECRET,
X_ACCESS_TOKEN, X_ACCESS_SECRET). Crédits API nécessaires (carte ajoutée par Gabriel dans console.x.com).
Usage : python3 tools/x_routine.py actu|site|cyberleek|top [--sec | --json | --marque <cle> <id>]
(--json : le post préparé pour tools/x_chrome.py, qui publie depuis le Chrome du Mac de Gabriel, sans API)   (--sec : affiche le post sans publier)"""
import base64, datetime, hashlib, hmac, io, json, os, re, secrets, sys, time, urllib.parse, urllib.request, uuid
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ETAT = Path(os.environ.get("X_ETAT", "/var/lib/gtavifrance/x_routine_etat.json"))  # hors du dossier web
SORTIE = datetime.date(2026, 11, 19)
TAGS = "#GTA6 #GTAVI #GTA #GrandTheftAuto #GTA6France"   # 22/10 Gabriel : plus de # qui amènent du monde
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

TAGS_CYB = "#GTA6 #GTAVI #GTA #Cyberleek #GTA6News #GTA6France"   # 15/10 Gabriel : # qui ramène du monde, jamais #GTA6Leak / #leak (Rockstar)

def paragraphes(h, n=2):   # 22/10 : X Premium+ (Gabriel) = posts longs, on donne les premiers paragraphes de l'article
    ps = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<p[^>]*>(.*?)</p>", h or "", re.S)]
    return [x for x in ps if len(x) > 40][:n]

LONG = 1100   # Premium : jusqu'à 25 000 car. ; X coupe à ~280 avec « Afficher plus » (temps de lecture = portée)

def compose(tete, corps, theme, suite=(), appel="👇 Article complet en réponse"):
    if theme == "#Cyberleek": pied = "Non confirmé par Rockstar.\n" + appel + "\n" + TAGS_CYB
    else: pied = appel + "\n" + TAGS + (" " + theme if theme else "")
    reste = LONG - len(tete) - len(pied) - 8
    corps = re.sub(r"\s+", " ", corps or "").strip()
    corps = coupe(corps, reste)
    for x in suite:   # paragraphes entiers tant qu'il reste de la place, le dernier coupé proprement
        place = reste - len(corps) - 2
        if place < 120: break
        corps += "\n\n" + coupe(x, place)
    return f"{tete}\n\n{corps}\n\n{pied}" if corps else f"{tete}\n\n{pied}"

def image_article(a):
    f = RACINE / "assets/img/articles" / f"{a['id']}.jpg"
    return f.read_bytes() if f.exists() else None

def visuel_jours(j, fond=None):
    """18/10 (Gabriel trouve les montages faibles) : image officielle Rockstar différente chaque jour, brute,
    avec seulement un petit cartouche « J-xx · gtavifrance.com » en bas à gauche."""
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    if fond is None:
        def scene(f):   # vraies scènes seulement : pas les planches de goodies sur fond blanc
            im = Image.open(f)
            if im.size != (1600, 900) or f.name in ("759875393o5253.jpg", "9k2a49ook82o57.jpg"): return False   # boutique, coffret
            px = list(im.convert("L").resize((40, 22)).getdata())
            return sum(v > 235 for v in px) / len(px) < 0.15
        imgs = [f for f in sorted((RACINE / "assets/img/rockstar").glob("*.jpg")) if scene(f)]
        fond = imgs[datetime.date.today().toordinal() % len(imgs)] if imgs else RACINE / "assets/img/vi-une.jpg"
    im = ImageOps.fit(Image.open(fond).convert("RGB"), (1600, 900))
    d = ImageDraw.Draw(im, "RGBA")
    polices = sorted((RACINE / "tools/fonts").glob("*nton*"))
    f = lambda n: ImageFont.truetype(str(polices[0]), n) if polices else ImageFont.load_default()
    d.rounded_rectangle([40, 730, 470, 860], 18, fill=(22, 17, 29, 225))
    d.text((70, 742), f"J-{j}", font=f(80), fill=(255, 138, 61))
    d.text((72, 826), "GTAVIFRANCE.COM", font=f(26), fill=(242, 232, 213))
    o = io.BytesIO(); im.save(o, "JPEG", quality=88); return o.getvalue()

ANGLES = [  # 13 h : un angle du site par jour, en rotation
    ("⏳", "Le compte à rebours GTA 6 tourne à la seconde, façon panneau d'aéroport, jusqu'à minuit heure de chez vous.", "#ViceCity"),
    ("💶", "Prix, éditions standard et Ultimate, coffret The Goodtime State : tout est vérifié et à jour sur le site.", "#ViceCity"),
    ("📻", "Vice Bay Radio tourne en direct sur le site : les sons de Vice City en attendant le 19 novembre.", "#ViceCity"),
    ("🗺️", "Leonida, Vice City, les personnages, les trailers : notre guide GTA 6 rassemble tout ce qui est confirmé.", "#Leonida"),
    ("🌍", "L'actu GTA 6 vérifiée, chaque jour, en 17 langues. Et l'heure de sortie dans chaque pays.", "#ViceCity"),
    ("🎮", "En attendant, Vice Break : notre casse-briques néon gratuit, 100 niveaux dans Vice Bay et la radio en fond. Sort le 19 novembre comme GTA 6, précommande ouverte sur l'App Store.", "#ViceBreak"),
]

def vues_du_jour():
    """{id article: vues des dernières 24 h, toutes langues} depuis la base GoatCounter (lecture seule)."""
    import sqlite3
    try:
        c = sqlite3.connect("file:/opt/goatcounter/db.sqlite3?mode=ro", uri=True)
        rows = c.execute("select p.path, sum(h.total) from hit_counts h join paths p using(path_id) "
                         "where h.hour >= datetime('now', '-1 day') and p.path like '%journal/%' group by p.path").fetchall()
    except Exception: return {}
    v = {}
    for path, n in rows:
        m = re.search(r"journal/([^/]+)\.html", path)
        if m: v[m.group(1)] = v.get(m.group(1), 0) + n
    return v

def main():
    slot = next((a for a in sys.argv[1:] if not a.startswith("--")), "actu")
    if "--marque" in sys.argv:   # appelé par tools/x_chrome.py (Mac) après publication dans Chrome
        etat = json.loads(ETAT.read_text()) if ETAT.exists() else {"postes": [], "journal": []}
        cle, pid = sys.argv[sys.argv.index("--marque") + 1], sys.argv[sys.argv.index("--marque") + 2]
        etat["postes"].append(cle); etat["postes"] = etat["postes"][-300:]
        etat["journal"].append({"quand": datetime.datetime.now().isoformat(timespec="minutes"), "slot": slot, "id": pid, "cle": cle, "via": "chrome"})
        ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1)); print("marqué", cle); return
    if not SEC and "--json" not in sys.argv and "--maintenant" not in sys.argv:
        import random; time.sleep(random.randint(0, 50 * 60))   # heure variable : jamais pile à l'heure (0 à 50 min de décalage)
    etat = json.loads(ETAT.read_text()) if ETAT.exists() else {"postes": [], "journal": []}
    arts = json.load(open(RACINE / "data/articles.json", encoding="utf-8"))
    arts.sort(key=lambda a: a.get("date", ""), reverse=True)
    j = (SORTIE - datetime.date.today()).days
    if slot == "site":
        e, txt, th = ANGLES[datetime.date.today().toordinal() % len(ANGLES)]
        fond = RACINE / "assets/img/vb-motel.webp" if th == "#ViceBreak" else None   # Vice Break : visuel du jeu
        texte, img, cle = compose(f"{e} J-{j} avant GTA 6.", txt, th, appel="👇 Le site en réponse"), visuel_jours(j, fond), f"site-{datetime.date.today()}"
        lien = "https://gtavifrance.com/"
    elif slot == "radio":   # 27/10 Gabriel : chaque jour une station de Vice Bay Radio, lien direct vers sa page (v2 avec Codex Soso)
        import random, urllib.request
        lit = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "gtavifrance"}), timeout=30).read()
        S = json.loads(lit("https://vicebayradio.com/data.js").decode().split("window.VBR=", 1)[1].rstrip().rstrip(";"))["stations"]
        auj = datetime.date.today(); an, sem, jr = auj.isocalendar()
        def ordre(a, w):   # stations mélangées chaque semaine (pas toujours le même jour), jamais deux fois de suite
            o = list(range(len(S))); random.Random(f"radio-{a}-{w}").shuffle(o); return o
        o = ordre(an, sem); prec = ordre(*(auj - datetime.timedelta(days=7)).isocalendar()[:2])
        if o[0] == prec[-1]: o[0], o[1] = o[1], o[0]
        st = S[o[(jr - 1) % len(o)]]
        jingle = min(st.get("jingles") or [st["slogan"]], key=len)
        ACCROCHES = ["Ton trajet mérite une autre bande-son.", f"Ce soir, {st['host']} prend le micro.", "Ferme les onglets. Ouvre la radio.",
                     f"« {jingle} »", "Le week-end commence sur cette fréquence.", "Une ville imaginaire. Une vraie bande-son pour ta soirée.",
                     "Encore un morceau avant demain ?"]
        acc = ACCROCHES[jr - 1]   # une accroche par jour de la semaine (vendredi : week-end, dimanche : avant demain)
        url = f"https://vicebayradio.com/station/{st['id']}.html?utm_source=x&utm_medium=social&utm_campaign=station_du_jour&utm_content={st['id']}-j{jr}"
        texte = (f"📻 {acc}\n\n{st['name']} {st['f']} FM · {st['genre'].capitalize()}, avec {st['host']}.\n"
                 f"{st['slogan']}\n\n▶ Écouter en direct : {url}\n\n#ViceBayRadio")
        img, cle, lien = lit(f"https://vicebayradio.com/img/share_{st['id']}.jpg"), f"radio-{auj}", ""
    else:
        cyb = slot == "cyberleek"
        cands = [a for a in arts if (slot == "top" or ("cyberleek" in a["id"]) == cyb) and a["id"] not in etat["postes"]
                 and isinstance(a.get("fr"), dict) and image_article(a)][:40 if slot == "top" else 5]
        if slot == "chaud":   # 27/10 Gabriel : lien total site → X : chaque nouvel article de Solange part sur X dans la demi-heure (5 par jour max, 8 h-23 h)
            h = datetime.datetime.now()
            faits = sum(1 for x in etat["journal"] if x.get("slot") == "chaud" and x["quand"][:10] == str(h.date()))
            if not 8 <= h.hour < 23 or faits >= 5: print(f"chaud : hors créneau ou quota ({faits}/5)"); return
            seuil = (h - datetime.timedelta(hours=3)).isoformat()[:16]
            cands = [a for a in arts if "cyberleek" not in a["id"] and a["id"] not in etat["postes"] and a.get("date", "")[:16] >= seuil
                     and isinstance(a.get("fr"), dict) and image_article(a)][:1]
        if slot == "top":
            v = vues_du_jour(); cands.sort(key=lambda a: -v.get(a["id"], 0))
            cyb = bool(cands) and "cyberleek" in cands[0]["id"]
        if not cands: print(f"{slot} : rien de nouveau à poster"); return
        a = cands[0]
        vb = "vice-break" in a["id"]   # notre jeu : pas une alerte
        texte = compose(("🔒 " if cyb else "🎮 " if vb else "🚨 ") + a["fr"]["t"], a["fr"].get("d", ""), "#Cyberleek" if cyb else "#ViceBreak" if vb else "#ViceCity", paragraphes(a["fr"].get("h", "")))
        img, cle = image_article(a), a["id"]
        lien = f"https://gtavifrance.com/journal/{a['id']}.html"
        if slot in ("actu", "chaud"):   # 22/10 Gabriel : au moins une news par jour avec le lien dans le post (9 h), pas en réponse
            texte = texte.replace("👇 Article complet en réponse", "👉 " + lien); lien = ""
    if SEC: print(texte, f"\n[{len(texte)} car., image {len(img)} o]"); return
    if "--json" in sys.argv: print(json.dumps({"slot": slot, "cle": cle, "texte": texte, "lien": lien, "image": base64.b64encode(img).decode()})); return
    try:
        pid = tweet(texte, upload(img))
    except urllib.error.HTTPError as e:
        print(f"{slot} : échec X {e.code} {e.read()[:200]!r}"); sys.exit(1)
    etat["postes"].append(cle); etat["postes"] = etat["postes"][-300:]
    etat["journal"].append({"quand": datetime.datetime.now().isoformat(timespec="minutes"), "slot": slot, "id": pid, "cle": cle})
    ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
    print(f"{slot} : posté https://x.com/gtavifrancecom/status/{pid}")

if __name__ == "__main__":
    main()
