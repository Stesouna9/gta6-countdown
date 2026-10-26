#!/usr/bin/env python3
"""Construit la rubrique Buzz à partir de data/buzz.json. Ne collecte aucun chiffre fictif."""
import json, html, re, hashlib
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent.parent
E=lambda s:html.escape(str(s or ""),quote=True)
def date(s):
    if not s:return "Premier passage en préparation"
    return datetime.fromisoformat(s).strftime("%d.%m.%Y · %H:%M")
def safe(u):
    p=urlparse(u or "")
    if p.scheme!="https" or not p.netloc:raise ValueError("Source HTTPS requise")
    return E(u)
def render():
    d=json.loads((ROOT/'data/buzz.json').read_text())
    ids=set(); urls=set(); cards=[]
    for a in d['items']:
        if a['id'] in ids or a['url'] in urls:raise ValueError("Doublon buzz")
        ids.add(a['id']);urls.add(a['url']);u=safe(a['url'])
        label=a.get('status','Rapporté');platform=a['platform']
        image=a.get('image')
        visual=(f'<img class="buzz-card-img" src="{safe(image)}" alt="" width="640" height="360" loading="lazy">' if image else f'<div class="buzz-art" aria-hidden="true"><small>{E(platform)} / GTA VI</small><strong>{E(a.get("visual","LE BUZZ"))}</strong><small>LA SÉLECTION GTAVIFRANCE</small></div>')
        article=f'<a class="lien" href="{E(a["article"])}">Lire notre décryptage →</a>' if a.get('article') else ''
        cards.append(f'<article class="buzz-card" data-platform="{E(platform)}">{visual}<div class="buzz-content"><div class="buzz-meta"><span>{E(platform)}</span><span class="buzz-tag {"rumeur" if label=="Rumeur" else ""}">{E(label)}</span></div><h2>{E(a["title"])}</h2><p>{E(a["summary"])}</p><div class="buzz-evidence">{E(a.get("evidence","Popularité non mesurée. Sujet sélectionné pour son intérêt éditorial."))}</div><p class="buzz-date">Publication : {E(a.get("published_at","date non vérifiée"))} · Vérifié le {E(date(a["checked_at"]))}</p>{article}<a class="buzz-source" href="{u}" target="_blank" rel="noopener noreferrer">{E(a["author"])} · Voir la source ↗</a></div></article>')
    runs=''.join(f'<li><time datetime="{E(x["at"])}">{E(date(x["at"]))}</time><div><b>{E(x["label"])}</b><p>{E(x["summary"])}</p></div></li>' for x in reversed(d.get('runs',[])[-30:]))
    filters=''.join(f'<button type="button" data-buzz-filter="{x}" aria-pressed="{str(x=="Tous").lower()}">{x}</button>' for x in ['Tous','X','Instagram','TikTok','Rockstar','YouTube'])
    assets=''.join((ROOT/'assets'/f).read_text() for f in ['buzz.css','buzz.js'])
    v=hashlib.sha256(assets.encode()).hexdigest()[:10]
    title='Le buzz GTA6 : réseaux sociaux et communauté | GTAVIFRANCE'
    page=f"""<!DOCTYPE html>
<html lang="fr" dir="ltr" data-l="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title><meta name="description" content="La sélection GTA6 sur X, Instagram et TikTok : sources, créations de fans et actualités vérifiées. Officiel, rumeur ou rapporté, chaque sujet est identifié.">
<link rel="canonical" href="https://gtavifrance.com/buzz.html"><meta property="og:title" content="Le buzz GTA6"><meta property="og:description" content="Les réseaux s’emballent. On fait le tri."><meta property="og:url" content="https://gtavifrance.com/buzz.html"><meta property="og:type" content="website"><meta property="og:image" content="https://gtavifrance.com/assets/og/fr/actus.jpg"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#16111d">
<link rel="icon" href="assets/icons/icon-192.png"><link rel="stylesheet" href="assets/style.css"><link rel="stylesheet" href="assets/buzz.css?v={v}"><script src="assets/lang/fr.js"></script><script src="assets/i18n.js"></script></head>
<body><header class="tete-page actus-tete"><div class="wrap"><span class="kicker">Vice City · La communauté</span><h1>Le buzz GTA6</h1><p class="buzz-intro">Les réseaux s’emballent. On fait le tri. Vidéos, trouvailles, créations de fans et annonces : la sélection GTA VI France, avec une source à chaque fois.</p></div></header>
<main><section class="actus-nuit"><div class="wrap"><p class="maj"><i></i><b>La sélection</b> · Dernier passage : <time datetime="{E(d.get('updated_at') or '')}">{E(date(d.get('updated_at')))}</time></p>
<div class="buzz-toolbar"><div class="buzz-filters" role="group" aria-label="Filtrer par réseau">{filters}</div><label class="buzz-search" for="buzz-search">Chercher dans le buzz<input id="buzz-search" type="search" placeholder="Trailer, Vice City, création…" autocomplete="off"></label></div>
<p id="buzz-count" class="buzz-total" aria-live="polite">{len(cards)} sujets dans la sélection</p><div id="buzz-grid" class="buzz-grid">{''.join(cards)}</div><p id="buzz-no-results" class="buzz-empty" {'hidden' if cards else ''}>Aucun sujet pour ce filtre. Les prochaines trouvailles apparaîtront ici après vérification.</p>
<noscript><p>Tous les sujets sont affichés. Activez JavaScript pour utiliser les filtres.</p></noscript>
<aside class="buzz-note"><b>Du contexte, pas du bruit.</b> Une sélection éditoriale ne prouve pas qu’un sujet est viral. Les chiffres de vues et de partages sont affichés uniquement lorsqu’ils ont été constatés et datés. Les rumeurs restent étiquetées. Les médias restent chez leurs créateurs ; les liens renvoient aux publications originales.</aside></div></section>
<section class="papier"><div class="wrap"><div class="rubrique"><span class="num">01</span><h2>À toi de jouer</h2><p>Une trouvaille à partager, une théorie à discuter ? Retrouve la communauté sur le Mur de Vice City.</p></div><div class="boutons"><a class="btn" href="communaute.html">Rejoindre la discussion →</a><a class="lien" href="https://x.com/gtavifrancecom" target="_blank" rel="noopener noreferrer">GTA VI France sur X ↗</a></div></div></section>
<section><div class="wrap"><div class="rubrique"><span class="num">02</span><h2>Le journal de veille</h2><p>Cinq passages de démarrage espacés de deux minutes, puis une veille horaire jusqu’au 27 octobre à 6 h, heure de Paris. Les restrictions des plateformes peuvent limiter la couverture.</p></div><p class="buzz-date">{E(d.get('schedule','Initialisation'))}</p><ol class="buzz-journal">{runs or '<li>Le premier passage est en préparation.</li>'}</ol></div></section></main>
<script src="assets/site.js"></script><script src="assets/buzz.js?v={v}"></script></body></html>
"""
    (ROOT/'buzz.html').write_text(page)
    print('Buzz:',len(cards),'sujets;',len(d.get('runs',[])),'passages')
if __name__=='__main__':render()
