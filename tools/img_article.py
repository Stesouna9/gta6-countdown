"""Image d'article trouvée par mot-clé (11/10/2026).
Usage : python3 tools/img_article.py <id> "<mot-clé précis>" [--rang N] [--url URL]
- cherche le mot-clé en images (DuckDuckGo, résultats Bing/Google-like avec dimensions),
- prend la première image nette (1000 px de large minimum, format paysage de préférence)
  qui n'est PAS déjà utilisée par un autre article (comparaison d'empreinte visuelle),
- l'enregistre dans assets/img/articles/<id>.jpg (JPEG, 1200 px de large, qualité 85),
- affiche le site d'origine (pour la légende « Image : <site> »).
--rang N : saute les N premiers candidats valides (si le premier est hors sujet).
--url URL : prend directement cette image (trouvée à la main sur Google Images).
Toujours OUVRIR l'image produite (Read) pour vérifier qu'elle montre le sujet."""
import io, json, re, ssl, sys, time, urllib.parse, urllib.request
from pathlib import Path
from PIL import Image

RACINE = Path(__file__).resolve().parent.parent
DOSSIER = RACINE / "assets/img/articles"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}
CTX = ssl._create_unverified_context()


def get(url, ref=None, t=20):
    h = dict(UA, **({"Referer": ref} if ref else {}))
    return urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=t, context=CTX).read(15_000_000)


def candidats(q):
    for essai in range(3):
        try:
            h = get("https://duckduckgo.com/?ia=images&iax=images&q=" + urllib.parse.quote_plus(q)).decode()
            vqd = re.search(r'vqd=["\']?([\d-]+)', h).group(1)
            r = get(f"https://duckduckgo.com/i.js?l=us-en&o=json&q={urllib.parse.quote_plus(q)}&vqd={vqd}&f=,,,,,&p=1",
                    ref="https://duckduckgo.com/")
            return [(x["image"], x["width"], x["height"], x.get("url", "")) for x in json.loads(r)["results"]]
        except Exception:
            time.sleep(15 * (essai + 1))
    return []


def empreinte(im):
    g = im.convert("L").resize((9, 8), Image.LANCZOS)
    p = list(g.getdata())
    return sum(1 << i for i in range(64) if p[(i // 8) * 9 + i % 8] > p[(i // 8) * 9 + i % 8 + 1])


def deja_utilisees(sauf):
    e = {}
    for f in DOSSIER.glob("*.jpg"):
        if f.stem != sauf:
            try: e[f.stem] = empreinte(Image.open(f))
            except Exception: pass
    return e


def doublon(im, connues):
    h = empreinte(im)
    return next((k for k, v in connues.items() if bin(h ^ v).count("1") <= 8), None)


def enregistre(aid, im):
    DOSSIER.mkdir(parents=True, exist_ok=True)
    im = im.convert("RGB")
    w, h = im.size
    if w != 1200: im = im.resize((1200, round(h * 1200 / w)), Image.LANCZOS)
    im.save(DOSSIER / f"{aid}.jpg", "JPEG", quality=85, optimize=True, progressive=True)


def site(u):
    return re.sub(r"^www\.", "", urllib.parse.urlparse(u).netloc)


def main():
    a = sys.argv[1:]
    aid, q = a[0], (a[1] if len(a) > 1 and not a[1].startswith("--") else "")
    rang = int(a[a.index("--rang") + 1]) if "--rang" in a else 0
    connues = deja_utilisees(aid)
    if "--url" in a:
        u = a[a.index("--url") + 1]
        im = Image.open(io.BytesIO(get(u, ref="https://www.google.com/"))); im.load()
        d = doublon(im, connues)
        if d: sys.exit(f"DOUBLON de {d} : choisis une autre image")
        enregistre(aid, im); print(json.dumps({"id": aid, "src": u, "site": site(u), "w": im.size[0]})); return
    cands = sorted(candidats(q), key=lambda c: -((c[1] >= 1000) * 2 + (1.2 <= c[1] / max(c[2], 1) <= 2.2)))
    for u, w, h, page in cands:
        if w < 700: continue
        if re.search(r"istockphoto|shutterstock|gettyimages|alamy|dreamstime|123rf|depositphotos|stock\.adobe|freepik|vectorstock|canstockphoto|bigstock", u + page): continue  # filigrane
        try:
            im = Image.open(io.BytesIO(get(u, ref=page or None))); im.load()
        except Exception:
            continue
        if doublon(im, connues): continue
        if rang: rang -= 1; continue
        enregistre(aid, im)
        print(json.dumps({"id": aid, "src": u, "site": site(page or u), "w": im.size[0]}))
        return
    sys.exit("AUCUNE image valable : change de mot-clé")


if __name__ == "__main__":
    main()
