"""Images du site, style couverture de magazine Miami 1986 (papier, encre, ombre dure, grain).
python tools/images.py        -> badge.png, jn.jpg, jn-fr.jpg (le nombre de jours change : lancé 2 fois par jour)
python tools/images.py --tout -> + icônes d'application et fonds d'écran (fixes)"""
import sys, os, random, datetime
from PIL import Image, ImageDraw, ImageFont
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
INK, PAPER, HOT, SUN, GOLD, TEAL = "#16111d", "#f2e8d5", "#ff3b7a", "#ff8a2a", "#ffc93c", "#0fb3a3"
def anton(s): return ImageFont.truetype("tools/fonts/Anton-Regular.ttf", s)
def mono(s, w="Bold"):
    f = ImageFont.truetype("tools/fonts/JetBrainsMono.ttf", s)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
def grain(im, force=18):
    random.seed(7); px = im.load(); W, H = im.size
    for _ in range(W * H // 6):
        x, y = random.randrange(W), random.randrange(H); r, g, b = px[x, y][:3]; d = random.randint(-force, force)
        px[x, y] = (max(0, min(255, r + d)), max(0, min(255, g + d)), max(0, min(255, b + d)))
    return im
def ombre(d, xy, txt, f, coul, ombre_c, dec, anchor="la"):
    d.text((xy[0] + dec, xy[1] + dec), txt, font=f, fill=ombre_c, anchor=anchor)
    d.text(xy, txt, font=f, fill=coul, anchor=anchor)
def ajuste(txt, maxw, taille, police=anton):
    while taille > 10 and police(taille).getlength(txt) > maxw: taille -= 4
    return police(taille)
def jours():
    return (datetime.date(2026, 11, 19) - datetime.date.today()).days

def affiche(W, H, gros, ligne1, ligne2, haut, fichier, fond=PAPER):
    """Couverture : bandeau encre en haut, chiffre géant, deux lignes, pied avec l'adresse."""
    im = Image.new("RGB", (W, H), fond); d = ImageDraw.Draw(im); u = W / 1080
    bh = int(110 * u); d.rectangle([0, 0, W, bh], fill=INK)
    d.text((int(54 * u), bh // 2), haut, font=mono(int(30 * u)), fill=PAPER, anchor="lm")
    d.text((W - int(54 * u), bh // 2), "19.11.2026", font=mono(int(30 * u)), fill=GOLD, anchor="rm")
    for i, c in enumerate((HOT, SUN, GOLD)): d.rectangle([0, bh + i * int(14 * u), W, bh + (i + 1) * int(14 * u)], fill=c)
    f = ajuste(gros, W - int(120 * u), int(H * .44))
    ombre(d, (W // 2, int(H * .42)), gros, f, INK, HOT, int(18 * u), "mm")
    f1 = ajuste(ligne1, W - int(120 * u), int(120 * u)); d.text((W // 2, int(H * .74)), ligne1, font=f1, fill=INK, anchor="mm")
    d.text((W // 2, int(H * .74) + int(100 * u)), ligne2, font=mono(int(32 * u)), fill=INK, anchor="mm")
    d.rectangle([0, H - int(90 * u), W, H], fill=INK)
    d.text((W // 2, H - int(45 * u)), "VI COUNTDOWN · 17 LANGUAGES", font=mono(int(28 * u)), fill=PAPER, anchor="mm")
    grain(im).save(fichier, quality=86, optimize=True)

def badge():
    n = jours(); im = Image.new("RGB", (468, 60), INK); d = ImageDraw.Draw(im)
    for i, c in enumerate((HOT, SUN, GOLD)): d.rectangle([0, 54 + i * 2, 468, 56 + i * 2], fill=c)
    ombre(d, (14, 27), str(max(n, 0)) if n > 0 else "OUT NOW", anton(44), GOLD, HOT, 3, "lm")
    x = 14 + anton(44).getlength(str(max(n, 0)) if n > 0 else "OUT NOW") + 14
    d.text((x, 18), "DAYS UNTIL GTA VI" if n > 0 else "GTA VI", font=mono(15), fill=PAPER, anchor="lm")
    d.text((x, 38), "19.11.2026 · PS5 · XBOX SERIES", font=mono(11, "Regular"), fill=PAPER, anchor="lm")
    d.text((458, 30), "VI", font=anton(30), fill=HOT, anchor="rm")
    im.save("assets/badge.png", optimize=True)

def du_jour():
    n = jours()
    if n > 0:
        affiche(1080, 1350, str(n), "DAYS UNTIL GTA VI", "PS5 · XBOX SERIES X|S · LEONIDA", f"Nº {n:03d}", "assets/jn.jpg")
        affiche(1080, 1350, f"J-{n}", "AVANT GTA VI", "PS5 · XBOX SERIES X|S · LEONIDA", f"Nº {n:03d}", "assets/jn-fr.jpg")
    else:
        affiche(1080, 1350, "VI", "OUT NOW", f"DAY {-n + 1} IN LEONIDA", "GTA VI", "assets/jn.jpg")
        affiche(1080, 1350, "VI", "C'EST SORTI", f"JOUR {-n + 1} À LEONIDA", "GTA VI", "assets/jn-fr.jpg")

def icones():
    for s in (180, 192, 512):
        im = Image.new("RGB", (s, s), INK); d = ImageDraw.Draw(im)
        for i, c in enumerate((HOT, SUN, GOLD)): d.rectangle([0, int(s * (.80 + i * .05)), s, int(s * (.85 + i * .05))], fill=c)
        ombre(d, (s // 2, int(s * .42)), "VI", anton(int(s * .62)), PAPER, HOT, max(2, s // 40), "mm")
        im.save(f"assets/icons/icon-{s}.png", optimize=True)

def fonds():
    for W, H, nom in ((1170, 2532, "telephone"), (2560, 1440, "ordinateur")):
        im = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(im); u = min(W, H) / 1080
        cx, cy, r = W // 2, int(H * (.40 if H > W else .46)), int(min(W, H) * .36)
        bandes = [HOT, SUN, GOLD]
        for i in range(12):   # soleil rayé, découpé en bandes horizontales
            y0 = cy - r + i * (2 * r // 12); y1 = y0 + (2 * r // 12) - (i * 2 * u if i > 5 else 0)
            m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
            band = Image.new("L", (W, H), 0); ImageDraw.Draw(band).rectangle([0, y0, W, y1], fill=255)
            from PIL import ImageChops
            im.paste(bandes[i * 3 // 12], (0, 0), ImageChops.multiply(m, band))
        f = anton(int(r * 1.5)); ombre(d, (cx, cy + int(r * .15)), "VI", f, PAPER, INK, int(14 * u), "mm")
        d.text((cx, cy + r + int(140 * u)), "LEONIDA", font=anton(int(150 * u)), fill=PAPER, anchor="mm")
        d.text((cx, cy + r + int(260 * u)), "19 · 11 · 2026", font=mono(int(46 * u)), fill=GOLD, anchor="mm")
        d.text((cx, H - int(120 * u)), "VI COUNTDOWN", font=mono(int(26 * u)), fill=PAPER, anchor="mm")
        grain(im, 12).save(f"assets/fonds/gta6-{nom}.jpg", quality=88, optimize=True)

badge(); du_jour()
if "--tout" in sys.argv: icones(); fonds()
print("images ok, J-%d" % jours())
