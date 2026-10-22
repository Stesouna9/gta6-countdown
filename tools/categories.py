"""Niveau de confirmation et catégorie de chaque article (22/10/2026), partagé par pub.py et prerender.py.
statut : conf (source officielle) / rapp (presse) / rum (fuite, rumeur). Champ "statut" de l'article prioritaire.
categorie : fuites / sortie / univers / coulisses / communaute / actu. Champ "cat" de l'article prioritaire."""
import json, re
from pathlib import Path

OFFICIELS = ("rockstargames.com", "playstation.com", "xbox.com", "take2games.com", "x.com/rockstargames", "twitter.com/rockstargames")
CATS = ["fuites", "sortie", "univers", "coulisses", "communaute", "actu"]
REGLES = [("fuites", r"cyberleek|leak|fuite|insider|leaker|build"),
          ("sortie", r"sortie|prix|precommande|pre-commande|edition|prechargement|taille|go-|boite|jaquette|date|heure|ps5|xbox|steam|pc-|ps-plus|amazon|stock|disque"),
          ("univers", r"lucia|jason|leonida|vice-city|personnage|carte|map|vehicule|voiture|arme|faune|animaux|especes|radio|musique|mission|trailer|gameplay|lieu|ville|keys|port-"),
          ("coulisses", r"rockstar|take-two|take2|budget|develop|bloomberg|studio|effectif|houser|zelnick|proces|tribunal|licenci|fbi|plainte|employ"),
          ("communaute", r"fan|mod|communaute|tiktok|instagram|streamer|youtube|record|sondage|soiree|grand-rex|vote|satire|maison-blanche|miami")]

def statut(a):
    if a.get("statut") in ("conf", "rapp", "rum"): return a["statut"]
    t = (a["id"] + " " + " ".join(a.get("tags", []))).lower()
    if re.search(r"cyberleek|leak|fuite|rumeur|insider|leaker", t): return "rum"
    if any(o in u.lower() for u in a.get("src", []) for o in OFFICIELS): return "conf"
    return "rapp"

def categorie(a):
    if a.get("cat") in CATS: return a["cat"]
    t = a["id"].lower() + " " + " ".join(a.get("tags", [])).lower()
    for c, rx in REGLES:
        if re.search(rx, t): return c
    return "actu"
