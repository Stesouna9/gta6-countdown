"""Publie la routine X de @GTAfance depuis le Chrome du Mac de Gabriel (session déjà connectée), comme le pacer Instagram
de Jackpot : sans API ni crédits. Décision de Gabriel, 14/10/2026.
Le serveur prépare le post (tools/x_routine.py <slot> --json : texte + image, article le plus vu, état anti-doublon),
ce script l'injecte dans le composeur de x.com/home par AppleScript/JavaScript (Chrome n'est jamais mis au premier plan :
Gabriel dicte avec Wispr Flow), clique Post, vérifie, puis marque le post côté serveur (--marque).
Lancé par launchd (~/Library/LaunchAgents/com.gtavifrance.xchrome.<slot>.plist) à 9 h, 13 h, 16 h et 19 h, avec 0 à 50 min
de décalage au hasard. Journal : ~/Library/Logs/gtavifrance-x.log.
Prérequis : Chrome > Présentation > Développeur > « Autoriser JavaScript à partir des événements Apple ».
Usage : python3 tools/x_chrome.py actu|site|cyberleek|top [--maintenant] [--essai]   (--essai : remplit sans publier)"""
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

def js(code, tab_url_part="x.com/"):
    """Exécute du JS dans l'onglet x.com de la routine (fichier, pour les gros contenus comme l'image en base64)."""
    f = TMP / "code.js"; f.write_text(code, encoding="utf-8")
    return osa(f'''set js to read POSIX file "{f}" as «class utf8»
tell application "Google Chrome"
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t contains "x.com/home") and (title of t does not contain "Compose") then
        if (execute t javascript "window.__gtaxRoutine === 1") is true then return (execute t javascript js)
      end if
    end repeat
  end repeat
end tell
return "pas d'onglet"''')

def ouvre_onglet():
    """Onglet dédié x.com/home, ouvert dans une fenêtre existante sans l'activer, marqué window.__gtaxRoutine."""
    osa('''tell application "Google Chrome"
  if (count of windows) = 0 then make new window
  set t to make new tab at end of tabs of window 1 with properties {URL:"https://x.com/home"}
end tell''')
    time.sleep(9)
    osa('''tell application "Google Chrome"
  set t to last tab of window 1
  execute t javascript "window.__gtaxRoutine = 1; 'ok'"
end tell''')

def ferme_onglet():
    try: osa('''tell application "Google Chrome"
  repeat with w in windows
    repeat with t in tabs of w
      if (URL of t contains "x.com/") then
        if (execute t javascript "window.__gtaxRoutine === 1") is true then close t
      end if
    end repeat
  end repeat
end tell''')
    except Exception: pass

def main():
    if "--maintenant" not in sys.argv and not ESSAI: time.sleep(random.randint(0, 50 * 60))
    r = subprocess.run(["ssh", "-o", "ConnectTimeout=20", SERVEUR, f"cd /var/www/gtavifrance && python3 tools/x_routine.py {slot} --json"],
                       capture_output=True, text=True, timeout=120)
    if not r.stdout.strip().startswith("{"): log("rien à poster (" + (r.stdout.strip() or r.stderr.strip())[:120] + ")"); return
    p = json.loads(r.stdout)
    ouvre_onglet()
    try:
        # 1) image dans le composeur de la page d'accueil (input file + DataTransfer)
        res = js("""(()=>{const i=document.querySelector('input[type=file][data-testid=fileInput]')||document.querySelector('input[type=file]');
if(!i)return 'pas de champ image';const b=atob(%s);const a=new Uint8Array(b.length);for(let k=0;k<b.length;k++)a[k]=b.charCodeAt(k);
const d=new DataTransfer();d.items.add(new File([a],'gtavifrance.jpg',{type:'image/jpeg'}));i.files=d.files;i.dispatchEvent(new Event('change',{bubbles:true}));return 'image ok'})()""" % json.dumps(p["image"]))
        if res != "image ok": raise RuntimeError(res)
        time.sleep(5)
        # 2) texte (insertText : l'éditeur de X le prend comme une frappe)
        res = js("""(()=>{const e=document.querySelector('[data-testid=tweetTextarea_0]');if(!e)return 'pas de zone texte';e.focus();
document.execCommand('insertText',false,%s);return e.innerText.length>20?'texte ok':'texte vide'})()""" % json.dumps(p["texte"]))
        if res != "texte ok": raise RuntimeError(res)
        time.sleep(3)
        etat = js("""(()=>{const b=document.querySelector('[data-testid=tweetButtonInline]');const img=document.querySelector('[data-testid=attachments] img');
return (b&&b.getAttribute('aria-disabled')!=='true'?'bouton actif':'bouton inactif')+(img?' + image':' sans image')})()""")
        if etat != "bouton actif + image": raise RuntimeError(etat)
        if ESSAI: log("essai OK, rempli sans publier : " + p["texte"].split("\n")[0][:80]); return
        js("document.querySelector('[data-testid=tweetButtonInline]').click();'clic'")
        time.sleep(8)
        pid = js("""(()=>{const a=[...document.querySelectorAll('article a[href*="/GTAfance/status/"]')].map(x=>x.href.split('/status/')[1].split('/')[0]);
return a.sort().pop()||''})()""")
        subprocess.run(["ssh", SERVEUR, f"cd /var/www/gtavifrance && python3 tools/x_routine.py {slot} --marque '{p['cle']}' '{pid or 'inconnu'}'"], capture_output=True, timeout=60)
        log(f"posté {p['cle']} https://x.com/GTAfance/status/{pid}")
    except Exception as e:
        log(f"ÉCHEC {e}")
        sys.exit(1)
    finally:
        if not ESSAI: ferme_onglet()

if __name__ == "__main__":
    main()
