"""Réponses X de @GTAfance sous les posts GTA 6 qui marchent (16/10/2026, « vas-y, mets tout ça en place », Gabriel).
Levier n°1 d'un petit compte : être vu sous les gros posts. Publié depuis le Chrome du Mac comme tools/x_chrome.py.
- Cherche les posts récents (< 6 h) : Rockstar Games, et les posts GTA 6 en français avec au moins 30 j'aime.
- Ne répond QUE si le post parle d'un sujet couvert par un de nos articles (tags de l'article trouvés dans le post) :
  la réponse apporte l'info de l'article (sa description), sans lien ni hashtag, + « Tout en français sur notre profil ».
- 1 réponse par lancement, 3 lancements par jour (launchd com.gtavifrance.xrep.{1,2,3}), jamais deux fois le même post
  ni le même compte dans la journée. Jamais de Cyberleek sous un post de Rockstar (on ne met pas Rockstar en porte-à-faux).
Usage : python3 tools/x_reponses.py [--essai] [--maintenant]   (--essai : affiche la réponse choisie sans publier)"""
import json, random, re, sys, time, datetime, urllib.parse
from pathlib import Path
import x_chrome as X

RACINE = Path(__file__).resolve().parent.parent
ETAT = Path.home() / ".config/gtavifrance/x_reponses.json"
ESSAI = "--essai" in sys.argv
X.slot = "reponse"
RECHERCHES = [("from:RockstarGames", "fr"), ("(GTA 6 OR GTA VI OR GTA6) lang:fr min_faves:30 -filter:replies", "fr"),
              ("(GTA 6 OR GTA VI OR GTA6) lang:en min_faves:300 -filter:replies", "en")]   # 17/10 : + gros posts anglais (réponse en anglais)
GENERIQUES = {"gta 6", "gta vi", "gta", "rockstar", "rockstar games", "take-two", "ps5", "xbox", "trailer", "vice city", "leonida", "jason", "lucia", "jason duval", "lucia caminos", "gta v", "grand theft auto", "trailer 3", "launch trailer", "playstation"}
FIN = {"fr": "\nTout en français sur notre profil 🌴", "en": "\nMore GTA 6 news on our profile 🌴"}

def ouvre(url):
    r = X.osa(f'''tell application "Google Chrome"
  if (count of windows) = 0 then make new window
  set w to window 1
  set t to make new tab at end of tabs of w with properties {{URL:"{url}"}}
  return ((id of w) as text) & "/" & ((id of t) as text)
end tell''')
    X.ONGLET["w"], X.ONGLET["t"] = r.split("/")

def attend(test, n=30):
    for _ in range(n):
        time.sleep(2)
        try:
            if X.js(test) == "ok": return True
        except Exception: pass
    return False

def posts_recents():
    vus = []
    for q, lg in RECHERCHES:
        ouvre("https://x.com/search?f=live&q=" + urllib.parse.quote(q))
        try:
            if not attend("document.querySelector('article [data-testid=tweetText]')?'ok':'non'"): continue
            time.sleep(3)
            r = X.js("""JSON.stringify([...document.querySelectorAll('article')].slice(0,15).map(a=>{const l=a.querySelector('a[href*="/status/"] time')?.closest('a');
return {url:l?l.href:'',quand:a.querySelector('time')?.getAttribute('datetime')||'',texte:a.querySelector('[data-testid=tweetText]')?.innerText||'',
auteur:(l?l.href.split('/')[3]:'')}}))""")
            vus += [dict(x, lg=lg) for x in json.loads(r)]
        finally:
            X.ferme_onglet(); X.ONGLET.clear()
    return vus

def choisit(posts, etat):
    arts = json.load(open(RACINE / "data/articles.json", encoding="utf-8"))
    arts = sorted([a for a in arts if isinstance(a.get("fr"), dict) and a["fr"].get("d")], key=lambda a: a["date"], reverse=True)[:40]
    maintenant = datetime.datetime.now(datetime.timezone.utc)
    deja_comptes = {r["auteur"] for r in etat["reponses"] if r["quand"][:10] == str(datetime.date.today())}
    for p in posts:
        if not p["url"] or p["url"] in etat["posts"] or p["auteur"].lower() in ("gtafance",) or p["auteur"] in deja_comptes: continue
        try: age = (maintenant - datetime.datetime.fromisoformat(p["quand"].replace("Z", "+00:00"))).total_seconds() / 3600
        except ValueError: continue
        if age > 12: continue
        t = p["texte"].lower()
        for a in arts:
            if p["auteur"].lower() == "rockstargames" and "cyberleek" in a["id"]: continue
            tags = [g for g in a.get("tags", []) + ([a["kw"]] if a.get("kw") else []) if g.lower() not in GENERIQUES and len(g) > 3]
            if any(g.lower() in t for g in tags):
                return p, a
    return None, None

def texte(a, lg="fr"):
    lg = lg if isinstance(a.get(lg), dict) and a[lg].get("d") else "fr"
    d = re.sub(r"\s+", " ", a[lg]["d"]).strip()
    if len(d) > 230: d = d[:230].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return d + FIN[lg]

def main():
    if not ESSAI and "--maintenant" not in sys.argv: time.sleep(random.randint(0, 40 * 60))
    etat = json.loads(ETAT.read_text()) if ETAT.exists() else {"posts": [], "reponses": []}
    p, a = choisit(posts_recents(), etat)
    if not p: X.log("aucun post récent sur un de nos sujets"); return
    rep = texte(a, p.get("lg", "fr"))
    if ESSAI: X.log(f"essai : sous {p['url']} ({p['texte'][:80]!r}) → {rep!r}"); return
    ouvre(p["url"])
    try:
        if not attend("document.querySelector('[data-testid=tweetTextarea_0]')?'ok':'non'"): raise RuntimeError("zone de réponse absente")
        r = X.js("""(()=>{const e=document.querySelector('[data-testid=tweetTextarea_0]');e.focus();document.execCommand('insertText',false,%s);
return e.innerText.length>20?'ok':'vide'})()""" % json.dumps(rep))
        if r != "ok": raise RuntimeError("texte : " + r)
        time.sleep(3)
        if X.js("(()=>{const b=document.querySelector('[data-testid=tweetButtonInline]');return b&&b.getAttribute('aria-disabled')!=='true'?'ok':'non'})()") != "ok":
            raise RuntimeError("bouton Répondre inactif")
        X.js("document.querySelector('[data-testid=tweetButtonInline]').click();'clic'")
        time.sleep(6)
        etat["posts"] = (etat["posts"] + [p["url"]])[-500:]
        etat["reponses"].append({"quand": datetime.datetime.now().isoformat(timespec="minutes"), "sous": p["url"], "auteur": p["auteur"], "article": a["id"]})
        ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
        X.log(f"réponse sous {p['url']} ({a['id']})")
    finally:
        X.ferme_onglet()

if __name__ == "__main__":
    main()
