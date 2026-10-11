"""Pose sur chaque article l'image trouvée par mot-clé (11/10/2026).
- appliquer(id, site) : img = assets/img/articles/<id>.jpg ; dans CHAQUE langue, la première <figure> du champ h
  devient cette image (alt = titre dans la langue, figcaption = « Image : <site> »), les autres figures sont retirées.
- Lancé sans argument (cron serveur) : pour chaque article dont l'image n'est pas encore assets/img/articles/<id>.jpg,
  cherche avec le champ kw (mot-clé choisi par la rédaction) ou, à défaut, le premier tag, via tools/img_article.py.
Miniature (img / og:image) et photo de l'article sont toujours le même fichier."""
import json, re, subprocess, sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
ARTS = RACINE / "data/articles.json"
BASE = "https://gtavifrance.com/assets/img/articles/"
FIG = re.compile(r"<figure\b.*?</figure>", re.S)


def legende(l, s):
    return ("Image : " if l == "fr" else "Image: ") + s


def appliquer(a, site):
    url = BASE + a["id"] + ".jpg"
    a["img"] = url
    a["img_site"] = site
    for l, v in a.items():
        if not (isinstance(v, dict) and "h" in v): continue
        alt = (v.get("t") or "").replace('"', "&quot;")
        fig = f'<figure><img src="{url}" alt="{alt}" loading="lazy"><figcaption>{legende(l, site)}</figcaption></figure>'
        h = FIG.sub("", v["h"]).strip()
        # après le premier paragraphe, comme avant (jamais tout en haut)
        m = re.search(r"</p>", h)
        v["h"] = (h[:m.end()] + fig + h[m.end():]) if m else fig + h


def charge():
    return json.loads(ARTS.read_text(encoding="utf-8"))


def sauve(arts):
    ARTS.write_text(json.dumps(arts, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def auto():
    arts = charge(); n = 0
    for a in arts:
        if a.get("img") == BASE + a["id"] + ".jpg" and (RACINE / "assets/img/articles" / (a["id"] + ".jpg")).exists():
            continue
        kw = a.get("kw") or (a.get("tags") or [""])[0]
        if not kw: continue
        r = subprocess.run([sys.executable, str(RACINE / "tools/img_article.py"), a["id"], kw], capture_output=True, text=True)
        if r.returncode: print("échec", a["id"], r.stderr.strip()[-200:]); continue
        appliquer(a, json.loads(r.stdout.strip().splitlines()[-1])["site"]); n += 1
    if n: sauve(arts)
    print(n, "image(s) posée(s)")


if __name__ == "__main__":
    auto()
