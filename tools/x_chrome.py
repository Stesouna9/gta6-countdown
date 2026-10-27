"""Publie la routine X de @gtavifrancecom depuis le Chrome du Mac de Gabriel (session déjà connectée), comme le pacer Instagram
de Jackpot : sans API ni crédits. Décision de Gabriel, 14/10/2026.
Le serveur prépare le post (tools/x_routine.py <slot> --json : texte + image, article le plus vu, état anti-doublon),
ce script l'injecte dans le composeur de x.com/home par AppleScript/JavaScript (Chrome n'est jamais mis au premier plan :
Gabriel dicte avec Wispr Flow), clique Post, vérifie, puis marque le post côté serveur (--marque).
Lancé par launchd (~/Library/LaunchAgents/com.gtavifrance.xchrome.<slot>.plist) à 9 h (actu), 13 h (compte à rebours) et 19 h (article le plus vu des 24 h), avec 0 à 50 min
de décalage au hasard. Journal : ~/Library/Logs/gtavifrance-x.log.
Prérequis : Chrome > Présentation > Développeur > « Autoriser JavaScript à partir des événements Apple ».
Usage : python3 tools/x_chrome.py actu|site|top [--maintenant] [--essai]   (--essai : remplit sans publier)"""
import json, random, subprocess, sys, time, datetime
from pathlib import Path

SERVEUR = "root@2.29.41.109"
TMP = Path("/tmp/gtavifrance-x"); TMP.mkdir(exist_ok=True)
slot = next((a for a in sys.argv[1:] if not a.startswith("--")), "actu")
ESSAI = "--essai" in sys.argv

def log(m):
    print(f"{datetime.datetime.now():%Y-%m-%d %H:%M} {slot} : {m}", flush=True)

def osa(script):
    r = subprocess.run(["osascript", "-"], input=script, capture_output=True, text=True, timeout=120)
    if r.returncode: raise RuntimeError(r.stderr.strip()[:300])
    return r.stdout.strip()

ONGLET = {}   # {"w": id fenêtre, "t": id onglet} : la routine ne touche qu'à SON onglet (un autre onglet figé bloquait tout)

def js(code):
    """Exécute du JS dans l'onglet de la routine (via fichier : gros contenus)."""
    f = TMP / "code.js"; f.write_text(code, encoding="utf-8")
    return osa(f'''set js to read POSIX file "{f}" as «class utf8»
with timeout of 60 seconds
tell application "Google Chrome" to execute (first tab of window id {ONGLET["w"]} whose id is {ONGLET["t"]}) javascript js
end timeout''')

# Garde-fous (24/10, montée en charge validée par Gabriel) : gel de 24 h dès que X montre une limite, un captcha ou « automatisé »
GEL = Path.home() / ".config/gtavifrance/x_gel"
ALERTES = ("rate limit", "limite de", "automated", "automatisé", "unusual activity", "activité inhabituelle", "verify you are human",
           "prouvez que vous", "temporarily restricted", "temporairement restreint", "arkose", "try again later", "réessayez plus tard")
def gel_actif():
    return GEL.exists() and time.time() - GEL.stat().st_mtime < 86400
def surveille():
    """Lit la page de la routine ; si X avertit : gel 24 h, ligne au journal, arrêt."""
    try: t = js("(()=>{const b=document.body.cloneNode(true);b.querySelectorAll('article,script,style,noscript,template,iframe,[data-testid=tweetText],[data-testid=UserDescription]').forEach(e=>e.remove());return (b.innerText||b.textContent||'').toLowerCase().slice(0,20000)})()")   # 28/10 : hors texte des tweets (faux gel du 27/10 19 h 10 sur un tweet contenant « automated »)
    except Exception: return
    a = next((x for x in ALERTES if x in t), None)
    if a:
        GEL.parent.mkdir(parents=True, exist_ok=True); GEL.write_text(f"{datetime.datetime.now():%Y-%m-%d %H:%M} {slot} : « {a} »")
        log(f"GEL 24 h : X affiche « {a} »"); raise SystemExit(1)

def hasard(max_min, saut=0.0):
    """Horaires humains (27/10, Gabriel : « vachement aléatoire ») : départ décalé de 0 à max_min, 3 heures de repos par jour tirées
    au sort (différentes chaque jour) et une part de lancements sautés au hasard. Rien avec --maintenant ou --essai."""
    if "--maintenant" in sys.argv or "--essai" in sys.argv: return
    repos = set(random.Random(datetime.date.today().isoformat()).sample(range(9, 24), 3))
    if saut and (datetime.datetime.now().hour in repos or random.random() < saut): log("pause (hasard)"); raise SystemExit(0)
    time.sleep(random.randint(0, max_min * 60))

def aujourdhui():
    """Repère de date pour l'IA (27/10 : une réponse disait « encore deux ans » avant la sortie)."""
    j = (datetime.date(2026, 11, 19) - datetime.date.today()).days
    return f"Nous sommes le {datetime.date.today():%d/%m/%Y} : GTA 6 sort dans {j} jours (le 19/11/2026)." if j > 0 else f"Nous sommes le {datetime.date.today():%d/%m/%Y} : GTA 6 est sorti le 19/11/2026."

def ia(consigne, max_tokens=1500):
    """Texte court via l'API Anthropic (clé du trousseau, crédits autorisés par Gabriel le 24/10)."""
    import urllib.request
    cle = subprocess.run(["security", "find-generic-password", "-s", "Anthropic API key (routines)", "-w"], capture_output=True, text=True).stdout.strip()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", headers={"x-api-key": cle, "anthropic-version": "2023-06-01", "content-type": "application/json"},
        data=json.dumps({"model": "claude-haiku-5-5", "max_tokens": max_tokens, "messages": [{"role": "user", "content": consigne}]}).encode())
    r = json.load(urllib.request.urlopen(req, timeout=60))
    try:   # 27/10 : compteur de consommation de la clé API (point global de Gabriel)
        u = r.get("usage", {}); f = Path.home() / ".config/gtavifrance/ia_usage.jsonl"
        with open(f, "a") as o: o.write(json.dumps({"t": f"{datetime.datetime.now():%Y-%m-%d %H:%M}", "slot": slot, "in": u.get("input_tokens", 0), "out": u.get("output_tokens", 0)}) + "\n")
    except Exception: pass
    return "".join(b.get("text", "") for b in r["content"] if b.get("type") == "text").strip()

def colle(texte):
    """Écrit dans la zone de texte de X par un « coller » : garde les retours à la ligne (insertText les perdait, 24/10)."""
    return js("""(()=>{const e=document.querySelector('[data-testid=tweetTextarea_0]');if(!e)return 'pas de zone texte';e.focus();
document.execCommand('selectAll',false,null);document.execCommand('delete',false,null);
const t=%s,d=new DataTransfer();d.setData('text/plain',t);e.dispatchEvent(new ClipboardEvent('paste',{clipboardData:d,bubbles:true,cancelable:true}));
const L=()=>e.innerText.split(String.fromCharCode(10)).join('').length;if(L()<10)document.execCommand('insertText',false,t);
const n=L();return n>10&&n<1300?'texte ok':'texte '+n})()""" % json.dumps(texte))   # X ignore le coller simulé depuis le 24/10 19 h : insertText en secours

def ouvre_onglet():
    """Nouvel onglet x.com/home dans la fenêtre 1, sans activer Chrome."""
    r = osa('''tell application "Google Chrome"
  if (count of windows) = 0 then make new window
  set w to window 1
  set t to make new tab at end of tabs of w with properties {URL:"https://x.com/home"}
  return ((id of w) as text) & "/" & ((id of t) as text)
end tell''')
    ONGLET["w"], ONGLET["t"] = r.split("/")
    for k in range(60):
        time.sleep(2)
        if k == 30: osa(f'tell application "Google Chrome" to reload (first tab of window id {ONGLET["w"]} whose id is {ONGLET["t"]})')   # onglet de fond figé (Mac en veille d'écran) : on recharge une fois
        try:
            if js("document.querySelector('[data-testid=tweetTextarea_0]')&&document.querySelector('input[type=file]')?'pret':'non'") == "pret": return
        except Exception: pass
    raise RuntimeError("x.com/home ne charge pas (session déconnectée ?)")

def ferme_onglet():
    """Vide le brouillon (sinon Chrome bloque sur « Quitter le site ? ») puis ferme l'onglet de la routine."""
    if not ONGLET: return
    try: surveille()
    except SystemExit:
        _ferme(); raise
    _ferme()

def _ferme():
    try:
        js("(()=>{document.querySelectorAll('[data-testid=removeMedia]').forEach(b=>b.click());const e=document.querySelector('[data-testid=tweetTextarea_0]');if(e){e.focus();document.execCommand('selectAll',false,null);document.execCommand('delete',false,null)}return 1})()")
        time.sleep(1)
        osa(f'''with timeout of 20 seconds
tell application "Google Chrome" to close (first tab of window id {ONGLET["w"]} whose id is {ONGLET["t"]})
end timeout''')
    except Exception as e:
        log(f"fermeture onglet : {e}")

def main():
    hasard(8 if slot == "chaud" else 55)
    if gel_actif(): log("gel en cours (" + GEL.read_text() + "), rien publié"); return
    r = subprocess.run(["ssh", "-o", "ConnectTimeout=20", SERVEUR, f"cd /var/www/gtavifrance && python3 tools/x_routine.py {slot} --json"],
                       capture_output=True, text=True, timeout=120)
    if not r.stdout.strip().startswith("{"): log("rien à poster (" + (r.stdout.strip() or r.stderr.strip())[:120] + ")"); return
    p = json.loads(r.stdout)
    try:
        ouvre_onglet()
        # 1) image dans le composeur de la page d'accueil (input file + DataTransfer)
        js("window.__gtaxImg='';'ok'")   # image envoyée par morceaux : AppleScript renvoie « missing value » au-delà de ~100 Ko
        for k in range(0, len(p["image"]), 60000): js("window.__gtaxImg+=%s;'ok'" % json.dumps(p["image"][k:k + 60000]))
        res = js("""(()=>{const i=document.querySelector('input[type=file][data-testid=fileInput]')||document.querySelector('input[type=file]');
if(!i)return 'pas de champ image';const b=atob(window.__gtaxImg);const a=new Uint8Array(b.length);for(let k=0;k<b.length;k++)a[k]=b.charCodeAt(k);
const d=new DataTransfer();d.items.add(new File([a],'gtavifrance.jpg',{type:'image/jpeg'}));i.files=d.files;i.dispatchEvent(new Event('change',{bubbles:true}));return 'image ok'})()""")
        if res != "image ok": raise RuntimeError(f"image : {res}")
        time.sleep(5)
        # 2) texte (collé : garde les retours à la ligne)
        res = colle(p["texte"])
        if res != "texte ok": raise RuntimeError(f"texte : {res}")
        time.sleep(3)
        etat = js("""(()=>{const b=document.querySelector('[data-testid=tweetButtonInline]');const img=document.querySelector('[data-testid=attachments] img');
return (b&&b.getAttribute('aria-disabled')!=='true'?'bouton actif':'bouton inactif')+(img?' + image':' sans image')})()""")
        if etat != "bouton actif + image": raise RuntimeError(etat)
        if ESSAI: log("essai OK, rempli sans publier : " + p["texte"].split("\n")[0][:80]); return
        js("document.querySelector('[data-testid=tweetButtonInline]').click();'clic'")
        time.sleep(8)
        pid = js("""(()=>{const a=[...document.querySelectorAll('article a[href*="/gtavifrancecom/status/"]')].map(x=>x.href.split('/status/')[1].split('/')[0]);
return a.sort().pop()||''})()""")
        subprocess.run(["ssh", SERVEUR, f"cd /var/www/gtavifrance && python3 tools/x_routine.py {slot} --marque '{p['cle']}' '{pid or 'inconnu'}'"], capture_output=True, timeout=60)
        log(f"posté {p['cle']} https://x.com/gtavifrancecom/status/{pid}")
        # 22/10 (go Gabriel) : lien du site en réponse à notre propre post (portée du post intacte, Grok relie le compte au site)
        if pid and p.get("lien"):
            try:
                js("location.href='https://x.com/gtavifrancecom/status/%s';'ok'" % pid); time.sleep(8)
                res = js("""(()=>{const e=document.querySelector('[data-testid=tweetTextarea_0]');if(!e)return 'pas de zone';e.focus();
document.execCommand('insertText',false,%s);return 'ok'})()""" % json.dumps("👉 À lire en entier sur " + p["lien"]))
                time.sleep(3)
                if res == "ok": js("(document.querySelector('[data-testid=tweetButtonInline]')||{click(){}}).click();'clic'"); time.sleep(6); log("lien en réponse : " + p["lien"])
                else: log(f"lien en réponse : {res}")
            except Exception as e:
                log(f"lien en réponse : {e}")
    except Exception as e:
        log(f"ÉCHEC {e}")
        sys.exit(1)
    finally:
        ferme_onglet()

if __name__ == "__main__":
    # 15/10 : le post de 9 h a échoué (x.com/home pas chargé) → jusqu'à 3 tentatives, 10 min d'écart
    for essai in range(3):
        try: main(); break
        except SystemExit as e:
            if e.code in (0, None) or essai == 2: raise
            log(f"nouvelle tentative dans 10 min ({essai + 2}/3)"); sys.argv.append("--maintenant"); ONGLET.clear(); time.sleep(600)
