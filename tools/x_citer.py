"""Citations X de @gtavifrancecom (24/10/2026, montée en charge validée par Gabriel) : cite un post GTA 6 fort (Rockstar, gros comptes)
avec un commentaire en français écrit pour lui (IA), comme un média qui réagit à l'actu. Publié depuis le Chrome du Mac (x_chrome.py).
1 citation par lancement, jamais deux fois le même post ni le même compte dans la journée ; gel 24 h au moindre avertissement de X.
Usage : python3 tools/x_citer.py [--essai] [--maintenant]"""
import json, random, sys, time, datetime
from pathlib import Path
import x_chrome as X
from x_reponses import ouvre, attend
import x_reponses as R

ETAT = Path.home() / ".config/gtavifrance/x_citations.json"
ESSAI = "--essai" in sys.argv
X.slot = "citation"
R.RECHERCHES = [("from:RockstarGames", "fr"), ("(GTA 6 OR GTA VI OR GTA6) min_faves:500 -filter:replies", "en"),
                ("(GTA 6 OR GTA VI OR GTA6) lang:fr min_faves:30 -filter:replies", "fr")]

def main():
    X.hasard(55, 0.2)
    if X.gel_actif(): X.log("gel en cours (" + X.GEL.read_text() + ")"); return
    etat = json.loads(ETAT.read_text()) if ETAT.exists() else {"posts": [], "citations": []}
    jour = str(datetime.date.today()); deja = {c["auteur"] for c in etat["citations"] if c["quand"][:10] == jour}
    maintenant = datetime.datetime.now(datetime.timezone.utc)
    for p in R.posts_recents():
        if not p["url"] or p["url"] in etat["posts"] or p["auteur"] in deja or p["auteur"].lower() == "gtavifrancecom" or len(p["texte"]) < 30: continue
        try:
            if (maintenant - datetime.datetime.fromisoformat(p["quand"].replace("Z", "+00:00"))).total_seconds() > 12 * 3600: continue
        except ValueError: continue
        com = X.ia(f"""Tu es GTAVIFRANCE (@gtavifrancecom), média fan de GTA 6 en français. Tu cites ce post X de @{p['auteur']} :
« {p['texte'][:700]} »
Écris le commentaire de la citation, en français : 1 à 3 phrases, 260 caractères max, ce que ça veut dire pour les joueurs français ou ton avis de fan, ton vivant, 1 emoji max, 1 hashtag max (#GTA6), pas de lien, rien d'inventé au-delà du post.
Si le post est une blague sans intérêt, de la politique, un concours, une arnaque ou une fuite douteuse, réponds exactement : PASSER
Donne seulement le texte.""").strip().strip('"«» ')
        etat["posts"] = (etat["posts"] + [p["url"]])[-500:]
        if com.upper().startswith("PASSER") or len(com) < 20:
            if not ESSAI: ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1))
            continue
        if len(com) > 275: com = com[:275].rsplit(" ", 1)[0] + "…"
        if ESSAI: X.log(f"essai : cite {p['url']} → {com!r}"); return
        X.ouvre_onglet()
        try:
            if X.colle(com + "\n" + p["url"]) != "texte ok": raise RuntimeError("texte")
            time.sleep(6)   # X transforme le lien du post en citation
            if X.js("(()=>{const b=document.querySelector('[data-testid=tweetButtonInline]');return b&&b.getAttribute('aria-disabled')!=='true'?'ok':'non'})()") != "ok": raise RuntimeError("bouton inactif")
            X.js("document.querySelector('[data-testid=tweetButtonInline]').click();'clic'"); time.sleep(8)
        finally:
            X.ferme_onglet(); X.ONGLET.clear()
        etat["citations"].append({"quand": datetime.datetime.now().isoformat(timespec="minutes"), "post": p["url"], "auteur": p["auteur"], "texte": com})
        ETAT.write_text(json.dumps(etat, ensure_ascii=False, indent=1)); X.log(f"cité {p['url']} : {com[:90]!r}"); return
    X.log("rien à citer")

if __name__ == "__main__":
    main()
