"""Répond aux gens qui répondent à @gtavifrancecom ou le mentionnent (27/10/2026, Gabriel : « c'est l'interaction avec les gens qui fonctionne bien »).
Lit x.com/notifications/mentions dans le Chrome du Mac (comme tools/x_reponses.py), réponse écrite par l'IA pour CE message,
jamais deux fois le même message, au plus 2 réponses par personne et par jour, messages de moins de 24 h, pas de lien.
Usage : python3 tools/x_mentions.py [--n=5] [--essai] [--maintenant]"""
import json, random, sys, time, datetime
from pathlib import Path
import x_chrome as X
from x_reponses import ouvre, attend, repond, like

ETAT = Path.home() / ".config/gtavifrance/x_mentions.json"
ESSAI = "--essai" in sys.argv
X.slot = "mention"

PRET = "document.querySelector('article [data-testid=tweetText]')?'ok':'non'"

def lis(n=20):
    return json.loads(X.js("""JSON.stringify([...document.querySelectorAll('article')].slice(0,%d).map(a=>{const l=a.querySelector('a[href*="/status/"] time')?.closest('a');
return {url:l?l.href:'',quand:a.querySelector('time')?.getAttribute('datetime')||'',texte:a.querySelector('[data-testid=tweetText]')?.innerText||'',
auteur:(l?l.href.split('/')[3]:''),contexte:(a.innerText.match(/(Replying to|En réponse à)[^\\n]*/)||[''])[0]}}))""" % n))

def va(url):
    """Même onglet, autre page : pas de nouvel onglet à chaque post."""
    try: X.js(f"location.href={json.dumps(url)}")
    except Exception: pass
    time.sleep(4)
    return attend(PRET)

def mentions():
    ouvre("https://x.com/notifications/mentions")
    try:
        liste = lis() if attend(PRET) and not time.sleep(3) else []
        # 08/11 Gabriel : répondre à tous les commentaires. L'onglet Mentions en cache une partie (filtre qualité de X),
        # donc on lit aussi les réponses sous nos posts de moins de 48 h.
        limite = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=48)).isoformat()[:19]
        if va("https://x.com/gtavifrancecom"):
            posts = {}
            for _ in range(5):   # le profil n'affiche que ~5 posts : défiler pour couvrir 48 h
                time.sleep(2)
                for p in lis(15):
                    if p["auteur"].lower() == "gtavifrancecom" and p["quand"] >= limite: posts[p["url"]] = p
                X.js("window.scrollBy(0,3000)")
            for p in sorted(posts.values(), key=lambda p: p["quand"], reverse=True)[:12]:
                if not va(p["url"]): continue
                for _ in range(2): X.js("window.scrollBy(0,2500)"); time.sleep(3)
                ctx = f"(en réponse à notre post : « {p['texte'][:200]} »)"
                liste += [dict(r, contexte=ctx) for r in lis(40) if r["auteur"].lower() != "gtavifrancecom" and r["url"] != p["url"]]
        return sorted(liste, key=lambda m: "?" not in m["texte"])   # les questions d'abord
    finally:
        X.ferme_onglet(); X.ONGLET.clear()

def texte(m):
    r = X.ia(f"""{X.aujourdhui()} Tu es le community manager de GTAVIFRANCE (@gtavifrancecom), média fan de GTA 6 en français. @{m['auteur']} nous a écrit sur X :
« {m['texte'][:600]} » {m['contexte']}
Écris NOTRE réponse. Règles : dans la langue du message, 1 ou 2 phrases, 240 caractères max, ton chaleureux de passionné qui discute (pas de pub, pas de « nous » corporate),
répondre vraiment à ce qu'il dit (question : y répondre ; avis : réagir, relancer par une petite question si naturel ; compliment : remercier simplement),
0 ou 1 emoji, pas de hashtag, pas de lien, rien d'inventé (repères sûrs : sortie le 19/11/2026 sur PS5 et Xbox Series, Vice City, Leonida, Jason et Lucia).
Si un simple j'aime suffit (merci, compliment, emoji, message qui n'appelle pas de réponse), réponds exactement : LIKE
Si c'est une insulte, de la politique, une arnaque, un bot, un concours ou s'il n'y a rien à répondre, réponds exactement : PASSER
Donne seulement le texte.""", 400).strip().strip('"«» ')
    if r.upper().startswith("PASSER") or len(r) < 5: return ""
    if r.upper().startswith("LIKE") or (random.random() < 0.2 and "?" not in m["texte"]): return "LIKE"   # 1 fois sur 5 : like au lieu de répondre, jamais pour une question
    return r if len(r) <= 270 else r[:270].rsplit(" ", 1)[0] + "…"

def main():
    n = int(next((x.split("=")[1] for x in sys.argv if x.startswith("--n=")), "5"))
    n = random.randint(max(1, n - 2), n + 2) if "--essai" not in sys.argv else n   # 28/10 Gabriel : volume aléatoire aussi
    X.hasard(25, 0.15)
    if X.gel_actif(): X.log("gel en cours (" + X.GEL.read_text() + ")"); return
    etat = json.loads(ETAT.read_text()) if ETAT.exists() else {"vus": [], "reponses": []}
    jour = datetime.date.today().isoformat()
    par_auteur = {}
    for r in etat["reponses"]:
        if r["quand"].startswith(jour): par_auteur[r["auteur"]] = par_auteur.get(r["auteur"], 0) + 1
    limite = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=48)).isoformat()
    faits = 0
    for m in mentions():
        if faits >= n: break
        if not m["url"] or m["url"] in etat["vus"] or m["auteur"].lower() == "gtavifrancecom" or m["quand"] < limite[:19]: continue
        if par_auteur.get(m["auteur"], 0) >= 2: continue
        try: rep = texte(m)
        except Exception as e: X.log(f"IA : {e}"); break
        etat["vus"] = (etat["vus"] + [m["url"]])[-1500:]
        if rep and ESSAI: X.log(f"essai : à @{m['auteur']} ({m['texte'][:70]!r}) → {rep!r}"); faits += 1; continue
        if rep == "LIKE":
            if ESSAI: X.log(f"essai : like à @{m['auteur']} ({m['texte'][:70]!r})"); faits += 1; continue
            try: like(m["url"]); X.log(f"like à @{m['auteur']} {m['url']}"); faits += 1
            except RuntimeError as e: X.log(f"like raté : {e}")
        elif rep:
            if faits: time.sleep(random.randint(45, 300))
            try:
                repond(m, rep)
                etat["reponses"].append({"quand": datetime.datetime.now().isoformat(timespec="minutes"), "a": m["url"], "auteur": m["auteur"]})
                par_auteur[m["auteur"]] = par_auteur.get(m["auteur"], 0) + 1
                X.log(f"réponse à @{m['auteur']} {m['url']} : {rep[:90]!r}"); faits += 1
            except RuntimeError as e: X.log(f"réponse ratée : {e}")
        if not ESSAI: ETAT.parent.mkdir(parents=True, exist_ok=True); ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
    if not faits: X.log("aucune mention à traiter")

if __name__ == "__main__":
    main()
