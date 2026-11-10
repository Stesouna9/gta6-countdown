"""Vice Break sous NOS posts qui marchent (10/11/2026, levier 3 de RAPPORT-TRAFIC.md, demandé par la session GTAVIFRANCE V7).
Les posts promo Vice Break seuls plafonnent vers 100 vues ; nos posts pratiques montent à 5 000-140 000 : le public est là.
- Lit le profil @gtavifrancecom (onglet Chrome de fond, jamais activé), garde nos posts de moins de 36 h à 5 000 vues ou plus.
- Une seule réponse « en attendant le 19 : Vice Break » par post (état ~/.config/gtavifrance/x_vb_reponse.json), 2 par lancement max.
- Jamais sous un post qui parle déjà de Vice Break (vb_plan, vb_promo : pas de doublon), rien pendant un gel X.
- Liens comptés côté serveur (/go/vb-ios|vb-android?s=x-reponse, voir gtavifrance-redirs.caddy).
Lancé par launchd com.gtavifrance.xvbrep (toutes les heures de 8 h à 23 h). Usage : python3 tools/x_vb_reponse.py [--essai] [--maintenant]"""
import datetime, json, random, re, sys, time
from pathlib import Path
import x_chrome as X

ETAT = Path.home() / ".config/gtavifrance/x_vb_reponse.json"
SEUIL, AGE_MAX, PAR_LANCEMENT = 5000, 36, 2
IOS, AND = "https://gtavifrance.com/go/vb-ios?s=x-reponse", "https://gtavifrance.com/go/vb-android?s=x-reponse"
SORTIE_IOS, SORTIE_GTA = datetime.datetime(2026, 11, 12), datetime.date(2026, 11, 19)

def texte():
    j = (SORTIE_GTA - datetime.date.today()).days
    if j <= 0: tete = "🎮 Une pause entre deux missions : Vice Break, notre casse-briques néon de Vice Bay."
    else: tete = random.choice(["🎮 En attendant le 19 : Vice Break, notre casse-briques néon de Vice Bay.",
                                f"🎮 Encore {j} jour{'s' if j > 1 else ''}. Pour patienter : Vice Break, notre casse-briques néon.",
                                "🎮 Pour patienter jusqu'au 19 : Vice Break, notre casse-briques néon de Vice Bay."])
    dispo = datetime.datetime.now() >= SORTIE_IOS
    corps = "500 niveaux, des boss, la radio en fond. Gratuit." + ("" if dispo else " Précommande ouverte sur iPhone (sortie le 12/11).")
    return f"{tete}\n{corps}\n\niPhone : {IOS}\nAndroid : {AND}"

LIT = """(()=>{const o=[];document.querySelectorAll('article[data-testid=tweet]').forEach(a=>{const l=[...a.querySelectorAll('a[href*="/status/"]')].find(x=>x.querySelector('time'));if(!l)return;
const sc=a.querySelector('[data-testid=socialContext]'),v=a.querySelector('a[href$="/analytics"]');
o.push({id:l.href.split('/status/')[1].split('/')[0],auteur:l.href.split('/')[3],t:l.querySelector('time').getAttribute('datetime'),ctx:sc?sc.innerText:'',
vues:v?(v.getAttribute('aria-label')||''):'',txt:(a.querySelector('[data-testid=tweetText]')||{innerText:''}).innerText})});window.scrollBy(0,900);return JSON.stringify(o)})()"""

def ouvre(url):
    r = X.osa(f'''tell application "Google Chrome"
  if (count of windows) = 0 then make new window
  set t to make new tab at end of tabs of window 1 with properties {{URL:"{url}"}}
  return ((id of window 1) as text) & "/" & ((id of t) as text)
end tell''')
    X.ONGLET["w"], X.ONGLET["t"] = r.split("/")

def attend(test, n=30):
    for _ in range(n):
        time.sleep(2)
        try:
            if X.js(test) == "ok": return True
        except Exception: pass
    return False

def candidats(etat):
    ouvre("https://x.com/gtavifrancecom")
    vus = {}
    try:
        if not attend("document.querySelector('article[data-testid=tweet]')?'ok':'non'"): raise RuntimeError("profil vide")
        X.surveille()
        for _ in range(30):   # ~36 h de posts (30 posts par jour environ)
            for p in json.loads(X.js(LIT) or "[]"): vus[p["id"]] = p
            time.sleep(1.8)
    finally:
        X.ferme_onglet(); X.ONGLET.clear()
    lim = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=AGE_MAX)
    n = lambda s: int(re.sub(r"\D", "", s.split(" ")[0]) or 0) if s else 0
    c = [dict(p, v=n(p["vues"])) for p in vus.values() if p["auteur"].lower() == "gtavifrancecom" and not p["ctx"]   # ni repost ni épinglé
         and datetime.datetime.fromisoformat(p["t"].replace("Z", "+00:00")) >= lim and p["id"] not in etat["faits"]
         and not re.search(r"vice ?break", p["txt"], re.I)]
    tetes = [p for p in c if not any(q["t"] < p["t"] and (datetime.datetime.fromisoformat(p["t"][:19]) - datetime.datetime.fromisoformat(q["t"][:19])).total_seconds() < 180 for q in vus.values())]   # suite de fil (posté < 3 min après un autre) : pas une tête de post
    return sorted([p for p in tetes if p["v"] >= SEUIL], key=lambda p: -p["v"])

def repond(pid, rep):
    ouvre(f"https://x.com/gtavifrancecom/status/{pid}")
    try:
        if not attend("document.querySelector('[data-testid=tweetTextarea_0]')?'ok':'non'"): raise RuntimeError("zone de réponse absente")
        X.surveille()
        r = X.colle(rep)
        if r != "texte ok": raise RuntimeError("texte : " + r)
        time.sleep(3)
        if X.js("(()=>{const b=document.querySelector('[data-testid=tweetButtonInline]');return b&&b.getAttribute('aria-disabled')!=='true'?'ok':'non'})()") != "ok":
            raise RuntimeError("bouton Répondre inactif")
        X.js("document.querySelector('[data-testid=tweetButtonInline]').click();'clic'")
        time.sleep(6)
    finally:
        X.ferme_onglet(); X.ONGLET.clear()

def main():
    X.hasard(20)
    if X.gel_actif(): X.log("vb-réponse : gel en cours"); return
    etat = json.loads(ETAT.read_text()) if ETAT.exists() else {"faits": [], "journal": []}
    try: c = candidats(etat)
    except RuntimeError as e: X.log(f"vb-réponse : {e}"); return
    if not c: X.log(f"vb-réponse : aucun post à {SEUIL} vues ou plus sans réponse Vice Break"); return
    for i, p in enumerate(c[:PAR_LANCEMENT]):
        rep = texte()
        if X.ESSAI: X.log(f"vb-réponse essai : sous {p['id']} ({p['v']} vues) → {rep!r}"); continue
        if i: time.sleep(random.randint(120, 600))
        try: repond(p["id"], rep)
        except RuntimeError as e: X.log(f"vb-réponse ratée sous {p['id']} : {e}"); continue
        etat["faits"] = (etat["faits"] + [p["id"]])[-500:]
        etat["journal"].append({"quand": datetime.datetime.now().isoformat(timespec="minutes"), "sous": p["id"], "vues": p["v"]})
        ETAT.parent.mkdir(parents=True, exist_ok=True); ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
        X.log(f"vb-réponse sous https://x.com/gtavifrancecom/status/{p['id']} ({p['v']} vues)")

if __name__ == "__main__":
    main()
