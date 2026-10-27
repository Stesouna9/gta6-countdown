"""Veille X pour Solange (27/10/2026, Gabriel : Vice Central et les comptes d'alerte avaient les 210 Go avant nous).
Lit dans le Chrome du Mac les derniers posts des comptes GTA 6 qui sortent les infos en premier, garde ceux de moins de 12 h,
écrit data/x_alertes.json = {maj, posts: [{url, auteur, quand, texte, vues, image, reactions}]} : des PISTES pour tools/JOURNALISTE.md (étape 2b).
Lancé par ~/La Soso/outils/presse/presse.sh. Lecture seule sur X : aucun like, aucun post.
Usage : python3 tools/x_alertes.py"""
import datetime, json, time, urllib.parse
from pathlib import Path
import x_chrome as X
from x_reponses import ouvre, attend

X.slot = "alertes"
SORTIE = Path(__file__).resolve().parent.parent / "data/x_alertes.json"
COMPTES = ["RockstarGames", "PlaystationSize", "TheGTABase", "GTAVI_Countdown", "GTAlphaintel", "videotech_", "Tez2", "GTA6Alert", "Gameideas_",
           "vicecentralFR", "gta6hubfr", "GTA6France1", "JVMag_ch", "jeuxvideocom", "PlayStation", "XboxWire", "TakeTwo"]
MOTS = ("gta", "grand theft", "rockstar", "leonida", "vice city", "lucia", "jason", "take-two", "take two")

def main():
    q = "(" + " OR ".join(f"from:{c}" for c in COMPTES) + ")"
    ouvre("https://x.com/search?f=live&q=" + urllib.parse.quote(q))
    posts = []
    try:
        if attend("document.querySelector('article [data-testid=tweetText]')?'ok':'non'"):
            for _ in range(4):   # quelques défilements : ~40 posts
                time.sleep(3)
                lot = json.loads(X.js("""JSON.stringify([...document.querySelectorAll('article')].map(a=>{const l=a.querySelector('a[href*="/status/"] time')?.closest('a');
return {url:l?l.href.split('?')[0]:'',quand:a.querySelector('time')?.getAttribute('datetime')||'',texte:a.querySelector('[data-testid=tweetText]')?.innerText||'',
auteur:(l?l.href.split('/')[3]:''),vues:(a.querySelector('a[href$="/analytics"]')?.getAttribute('aria-label')||'').replace(/[^0-9]/g,''),
image:(a.querySelector('[data-testid=tweetPhoto] img')?.src||a.querySelector('video')?.poster||''),reactions:(a.querySelector('[role=group]')?.getAttribute('aria-label')||'')}}))"""))
                posts += [p for p in lot if p["url"] and p["url"] not in {x["url"] for x in posts}]
                X.js("window.scrollBy(0,2500);1")
    finally:
        X.ferme_onglet(); X.ONGLET.clear()
    limite = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=12)).isoformat()[:19]
    garde = [p for p in posts if p["quand"][:19] >= limite and any(m in p["texte"].lower() for m in MOTS)]
    garde.sort(key=lambda p: p["quand"], reverse=True)
    SORTIE.write_text(json.dumps({"maj": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "posts": garde[:40]}, ensure_ascii=False, indent=1))
    print(f"x_alertes : {len(garde)} posts retenus sur {len(posts)}")

if __name__ == "__main__":
    if X.gel_actif(): print("x_alertes : gel X en cours"); raise SystemExit(0)
    main()
