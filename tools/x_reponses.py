"""Réponses X de @gtavifrancecom sous les posts GTA 6 qui marchent (16/10/2026, « vas-y, mets tout ça en place », Gabriel).
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
# 29/10 Gabriel : « faut les taquiner avec bienveillance » : Vice Central et GTA 6 Hub (confrères fans), prioritaires, 1 réponse/jour max chacun
# 29/10 bis : « tous les comptes FR qui parlent de GTA, ceux qui sont comme nous » : liste connue + tout compte FR dont le pseudo dit GTA/Rockstar/Leonida/Vice
RIVAUX = {"vicecentralfr", "gta6hubfr", "rockstarnewsfra", "gta6france1", "gtasix_"}   # 29/10 ter : + comptes fans anglais (« même cela en anglais »)
def confrere(p): a = p["auteur"].lower(); return a in RIVAUX or (a not in ("rockstargames", "gtafance", "gtavifrancecom") and re.search(r"gta|rockstar|leonida|vicecity|vice_?city", a) is not None)
RECHERCHES = [("(from:vicecentralFR OR from:gta6hubfr OR from:RockstarNewsFRA OR from:GTA6France1) -filter:replies", "fr"), ("from:gtasix_ -filter:replies", "en"), ("from:RockstarGames", "fr"), ("(GTA 6 OR GTA VI OR GTA6) lang:fr min_faves:100 -filter:replies", "fr"), ("(GTA 6 OR GTA VI OR GTA6 OR Leonida) lang:fr min_faves:20 -filter:replies", "fr"),
              ("(GTA 6 OR GTA VI OR GTA6) lang:en min_faves:2000 -filter:replies", "en"), ("(GTA 6 OR GTA VI OR GTA6) lang:en min_faves:500 -filter:replies", "en")]
# 27/10 Gabriel : viser les posts qui ont déjà beaucoup de vues et de réactions (gros comptes) ; candidats triés par réactions   # 17/10 : + gros posts anglais (réponse en anglais)
GENERIQUES = {"gta 6", "gta vi", "gta", "rockstar", "rockstar games", "take-two", "ps5", "xbox", "trailer", "vice city", "leonida", "jason", "lucia", "jason duval", "lucia caminos", "gta v", "grand theft auto", "trailer 3", "launch trailer", "playstation", "rockstargames", "sortie", "date de sortie", "release", "release date", "bande-annonce", "rumeur", "officiel", "annonce", "précommande", "pre-order", "gameplay", "carte", "map"}
LIEUX = {"miami", "floride", "florida", "los angeles", "vice", "keys", "port gellhorn", "ambrosia", "grassrivers", "mount kalaga"}   # trop vagues seuls
FIN = {"fr": "", "en": ""}   # 24/10 Gabriel : « Tout en français sur notre profil » jugé moyen, la réponse = l'info seule

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
auteur:(l?l.href.split('/')[3]:''),
score:['reply','retweet','like'].reduce((s,k)=>s+parseInt((a.querySelector('[data-testid='+k+']')?.getAttribute('aria-label')||'0').replace(/[^0-9]/g,'')||0),0)}}))""")
            vus += [dict(x, lg=lg) for x in json.loads(r)]
        finally:
            X.ferme_onglet(); X.ONGLET.clear()
    return vus

def choisit(posts, etat, n):
    """Jusqu'à n posts récents (< 24 h), comptes différents, chacun avec l'article qui colle le mieux (ou None)."""
    arts = json.load(open(RACINE / "data/articles.json", encoding="utf-8"))
    arts = sorted([a for a in arts if isinstance(a.get("fr"), dict) and a["fr"].get("d")], key=lambda a: a["date"], reverse=True)[:40]
    maintenant = datetime.datetime.now(datetime.timezone.utc)
    deja = {r["auteur"] for r in etat["reponses"] if r["quand"][:10] == str(datetime.date.today())}
    choix = []
    for p in sorted(posts, key=lambda p: (not confrere(p), -p.get("score", 0))):   # confrères taquinés d'abord, puis les plus gros
        if len(choix) >= n: break
        if not p["url"] or p["url"] in etat["posts"] or p["auteur"].lower() in ("gtafance", "gtavifrancecom") or p["auteur"] in deja or len(p["texte"]) < 25: continue
        try: age = (maintenant - datetime.datetime.fromisoformat(p["quand"].replace("Z", "+00:00"))).total_seconds() / 3600
        except ValueError: continue
        if age > 24: continue
        t = p["texte"].lower(); art = None
        for a in arts:
            if p["auteur"].lower() == "rockstargames" and "cyberleek" in a["id"]: continue
            tags = [g for g in a.get("tags", []) + ([a["kw"]] if a.get("kw") else []) if g.lower() not in GENERIQUES and len(g) > 3]
            trouves = {g.lower() for g in tags if re.search(r"(?<!\w)" + re.escape(g.lower()) + r"(?!\w)", t)} - LIEUX
            if len(trouves) >= 2 or (a.get("kw") and a["kw"].lower() in trouves): art = a; break
        choix.append((p, art)); deja.add(p["auteur"])
    return choix

def texte(p, a, lien):
    """Réponse écrite pour CE post (24/10 : IA, plus de phrase toute faite). Renvoie '' si mieux vaut se taire."""
    lg = p.get("lg", "fr")
    taquin = confrere(p)
    if taquin: a = None
    regle = ("C'est un confrère fan (média GTA 6 français concurrent) : taquine-le avec bienveillance, clin d'œil complice entre passionnés, humour léger, jamais méchant, jamais dénigrant, jamais de critique de son travail, pas de pub pour nous. "
             "Une seule idée, claire et compréhensible du premier coup, accrochée à un élément précis du post (son info, son chiffre, sa formule) ; la vanne doit avoir un sens évident (pas de blague sur le spoil), pas de phrase alambiquée ni absurde ; 1 phrase de préférence. Même si c'est un concours, réponds par une petite taquinerie sympa (sans participer ni demander à gagner). Ne réponds PASSER que si le post est triste, politique ou polémique.\n") if taquin else ""
    info = f"Notre article sur le sujet : « {a['fr']['t']} » : {a['fr']['d']}" if a else "Pas d'article précis : réponds avec ce que tout fan sait (sortie le 19/11/2026 sur PS5 et Xbox Series, Vice City, Leonida, Jason et Lucia)."
    r = X.ia(f"""{X.aujourdhui()} Tu es le community manager de GTAVIFRANCE (@gtavifrancecom), média fan de GTA 6 en français. Écris UNE réponse au post X ci-dessous.
Post de @{p['auteur']} : « {p['texte'][:600]} »
{info}
{regle}Règles : en {'français' if lg == 'fr' else 'anglais'}, 1 ou 2 phrases, ne rappelle la date et les consoles que si le post en parle, 240 caractères max, ton naturel de passionné (pas de pub, pas de « nous » corporate), répondre vraiment à ce que dit la personne, apporter une info ou un avis, 0 ou 1 emoji, pas de hashtag, pas de lien, rien d'inventé.
Si le post est une blague sans rapport, de la politique, une insulte, un concours ou une arnaque, ou si tu n'as rien d'utile à ajouter, réponds exactement : PASSER
Donne seulement le texte de la réponse.""")
    r = r.strip().strip('"«» ')
    if r.upper().startswith("PASSER") or len(r) < 15: return ""
    if len(r) > 270: r = r[:270].rsplit(" ", 1)[0] + "…"
    if lien and a: r += "\n👉 https://gtavifrance.com/" + ("" if lg == "fr" else "en/") + f"journal/{a['id']}.html"
    return r

def repond(p, rep):
    ouvre(p["url"])
    try:
        if not attend("document.querySelector('[data-testid=tweetTextarea_0]')?'ok':'non'"): raise RuntimeError("zone de réponse absente")
        r = X.colle(rep)
        if r != "texte ok": raise RuntimeError("texte : " + r)
        time.sleep(3)
        if X.js("(()=>{const b=document.querySelector('[data-testid=tweetButtonInline]');return b&&b.getAttribute('aria-disabled')!=='true'?'ok':'non'})()") != "ok":
            raise RuntimeError("bouton Répondre inactif")
        X.js("document.querySelector('[data-testid=tweetButtonInline]').click();'clic'")
        time.sleep(6)
        if random.random() < 0.85: X.js("(()=>{const b=document.querySelector('article [data-testid=like]');if(b)b.click();return 1})()"); time.sleep(2)   # 27/10 : on like aussi le post auquel on répond
    finally:
        X.ferme_onglet(); X.ONGLET.clear()

def like(url):
    """Like seul (27/10, Gabriel : « parfois, au lieu de répondre, tu peux juste liker »)."""
    ouvre(url)
    try:
        if not attend("document.querySelector('article [data-testid=like]')?'ok':'non'"): raise RuntimeError("bouton like absent")
        X.js("document.querySelector('article [data-testid=like]').click();'clic'"); time.sleep(3)
    finally:
        X.ferme_onglet(); X.ONGLET.clear()

def main():
    n = int(next((x.split("=")[1] for x in sys.argv if x.startswith("--n=")), "1"))
    n = random.randint(max(1, n - 1), n + 2) if "--essai" not in sys.argv else n   # 28/10 Gabriel : volume aléatoire aussi
    X.hasard(50, 0.2)
    if X.gel_actif(): X.log("gel en cours (" + X.GEL.read_text() + ")"); return
    etat = json.loads(ETAT.read_text()) if ETAT.exists() else {"posts": [], "reponses": []}
    choix = choisit(posts_recents(), etat, n * 2)   # deux fois plus de candidats : l'IA en écarte
    faits = 0
    for p, a in choix:
        if faits >= n: break
        lien = a is not None and len(etat["reponses"]) % 5 == 4   # lien dans 1 réponse sur 5
        try: rep = texte(p, a, lien)
        except Exception as e: X.log(f"IA : {e}"); break
        etat["posts"] = (etat["posts"] + [p["url"]])[-800:]
        if not rep:
            if not ESSAI: ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
            continue
        if ESSAI: X.log(f"essai : sous {p['url']} ({p['texte'][:70]!r}) → {rep!r}"); faits += 1; continue
        if faits: time.sleep(random.randint(60, 420))
        try: repond(p, rep)
        except RuntimeError as e: X.log(f"réponse ratée : {e}"); continue
        etat["reponses"].append({"quand": datetime.datetime.now().isoformat(timespec="minutes"), "sous": p["url"], "auteur": p["auteur"], "article": a["id"] if a else ""})
        ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
        X.log(f"réponse sous {p['url']} : {rep[:90]!r}"); faits += 1
    if not faits: X.log("aucune réponse utile à faire")

if __name__ == "__main__":
    main()
