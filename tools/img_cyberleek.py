"""Image d'article Cyberleek (13/10/2026) : le logo Cyberleek, reconnaissable tout de suite, jamais de capture fuitée.
Usage : python3 tools/img_cyberleek.py <id> "<accroche courte>"
Base tools/cyberleek-base.jpg ; chaque article a son cadrage, sa teinte et son bandeau (accroche), donc jamais deux images identiques.
Écrit assets/img/articles/<id>.jpg et affiche le JSON {id, site} comme img_article.py."""
import hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

RACINE = Path(__file__).resolve().parent.parent
TEINTES = [(43, 255, 140), (255, 46, 136), (77, 208, 225), (255, 122, 61), (242, 179, 61), (170, 120, 255)]


def fabrique(aid, accroche):
    h = int(hashlib.md5(aid.encode()).hexdigest(), 16)
    base = Image.open(RACINE / "tools/cyberleek-base.jpg").convert("RGB")
    W, H = base.size
    z = 1 + (h % 4) * 0.04                      # zoom 1.00 à 1.12, logo toujours entier
    cw, ch = int(W / z), int(H / z)
    x = (W - cw) // 2
    y = (H - ch) // 2 - (H - ch) // 4
    im = base.crop((x, max(0, y), x + cw, max(0, y) + ch)).resize((1200, 675), Image.LANCZOS)
    t = TEINTES[(h >> 8) % len(TEINTES)]
    im = Image.blend(im, ImageOps.colorize(ImageOps.grayscale(im), (6, 8, 20), t), 0.55)
    d = ImageDraw.Draw(im)
    acc = accroche.upper()[:48]
    f = ImageFont.truetype(str(RACINE / "tools/fonts/Anton-Regular.ttf"), 64)
    while d.textlength(acc, font=f) > 1100 and f.size > 34: f = ImageFont.truetype(f.path, f.size - 4)
    d.rectangle((0, 675 - 120, 1200, 675), fill=(10, 10, 22))
    d.rectangle((0, 675 - 120, 1200, 675 - 112), fill=t)
    d.text((50, 675 - 60), acc, font=f, fill=(255, 255, 255), anchor="lm")
    m = ImageFont.truetype(str(RACINE / "tools/fonts/JetBrainsMono.ttf"), 22)
    d.text((1150, 30), "GTAVIFRANCE.COM · DOSSIER CYBERLEEK", font=m, fill=t, anchor="ra")
    out = RACINE / "assets/img/articles" / f"{aid}.jpg"
    im.save(out, "JPEG", quality=85, optimize=True, progressive=True)
    return {"id": aid, "src": "tools/cyberleek-base.jpg", "site": "logo Cyberleek, montage gtavifrance.com", "w": 1200}


if __name__ == "__main__":
    print(json.dumps(fabrique(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "Fuite GTA 6"), ensure_ascii=False))
