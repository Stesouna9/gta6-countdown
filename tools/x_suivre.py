"""Abonnements X de @gtavifrancecom (17/10/2026) : un compte neuf gagne ses premiers abonnés en suivant des fans actifs, dont une
partie suit en retour. Chaque jour, suit au plus 20 comptes qui viennent de poster sur GTA 6 en français (pas les gros
comptes : ils ne suivent pas en retour), espacés de 1 à 3 min. Publié depuis le Chrome du Mac comme tools/x_chrome.py.
Lancé par launchd com.gtavifrance.xsuivre (14 h). Usage : python3 tools/x_suivre.py [--essai]"""
import json, random, sys, time, datetime, urllib.parse
from pathlib import Path
import x_chrome as X
from x_reponses import ouvre, attend

ETAT = Path.home() / ".config/gtavifrance/x_suivis.json"
ESSAI = "--essai" in sys.argv
X.slot = "suivre"
MAX = 20

REQUETES = ["(GTA 6 OR GTA VI OR GTA6 OR #GTA6) lang:fr", "(Vice City OR Lucia OR Jason Duval OR Leonida) lang:fr"]   # 18/10 : réponses incluses, 1 seul candidat avant

def candidats():
    vus = []
    for q in REQUETES:
        ouvre("https://x.com/search?f=live&q=" + urllib.parse.quote(q))
        try:
            if not attend("document.querySelector('article')?'ok':'non'"): continue
            for _ in range(6):
                vus += json.loads(X.js("""JSON.stringify([...document.querySelectorAll('article [data-testid=User-Name] a[href^="/"]')]
.map(a=>a.getAttribute('href').split('/')[1]))"""))
                X.js("window.scrollBy(0,2500);'ok'"); time.sleep(3)
        finally:
            X.ferme_onglet(); X.ONGLET.clear()
    return list(dict.fromkeys(vus))

def main():
    etat = json.loads(ETAT.read_text()) if ETAT.exists() else {"suivis": {}}
    jour = str(datetime.date.today())
    faits = sum(1 for d in etat["suivis"].values() if d == jour)
    liste = [u for u in candidats() if u and u.lower() not in ("gtafance", "rockstargames") and u not in etat["suivis"]]
    if ESSAI: X.log(f"essai : {len(liste)} comptes à suivre : {liste[:20]}"); return
    for u in liste[:MAX - faits]:
        ouvre(f"https://x.com/{u}")
        try:
            if not attend("document.querySelector('[data-testid$=\"-follow\"],[data-testid$=\"-unfollow\"]')?'ok':'non'", 15): continue
            r = X.js("""(()=>{if(document.querySelector('[data-testid$="-unfollow"]'))return 'deja';
const f=document.querySelector('[data-testid=UserFollowers] , a[href$="/verified_followers"]');const n=(f?.innerText||'').replace(/\\s/g,'');
const v=parseFloat(n.replace(',','.'))*(/[kK]/.test(n)?1000:(/M/.test(n)?1e6:1));if(v>=10000)return 'gros';
document.querySelector('[data-testid$="-follow"]').click();return 'suivi'})()""")
            etat["suivis"][u] = jour
            ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
            X.log(f"{r} @{u}")
        finally:
            X.ferme_onglet(); X.ONGLET.clear()
        time.sleep(random.randint(60, 180))

if __name__ == "__main__":
    main()
