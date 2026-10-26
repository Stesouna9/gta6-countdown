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
        image=a.get('image') or 'https://gtavifrance.com/assets/img/rockstar/lucia.jpg'
        visual=f'<a class="buzz-visual" href="{u}" target="_blank" rel="noopener noreferrer" aria-label="{E(a.get("cta","Ouvrir la source"))}"><img class="buzz-card-img" src="{safe(image)}" alt="{E(a.get("image_alt",a["title"]))}" width="640" height="360" loading="lazy"><span class="buzz-image-credit">{E(a.get("image_credit","Illustration officielle : Rockstar Games"))}</span></a>'
        if a.get('embed_type')=='instagram':
            shortcode=re.search(r'/(?:p|reel)/([A-Za-z0-9_-]+)/?',a['url'])
            if not shortcode:raise ValueError('Publication Instagram invalide')
            visual=f'<div class="buzz-embed buzz-instagram"><iframe src="https://www.instagram.com/p/{shortcode[1]}/embed/" title="Publication Instagram de {E(a["author"])}" loading="lazy" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe><p class="buzz-embed-help">Publication Instagram originale · Si le lecteur ne se charge pas, utilise le bouton ci-dessous.</p></div>'
        elif a.get('embed_type')=='x':
            visual=f'<div class="buzz-embed buzz-x"><blockquote class="twitter-tweet" data-theme="dark" data-dnt="true"><p lang="en">{E(a.get("post_text",""))}</p><a href="{u}">{E(a["author"].split(" · ")[0])} · {E(a["published_at"])}</a></blockquote></div>'
        article=f'<a class="buzz-secondary" href="{E(a["article"])}">Notre décryptage →</a>' if a.get('article') else ''
        if a.get('corroboration'):article+=f'<a class="buzz-secondary" href="{safe(a["corroboration"])}" target="_blank" rel="noopener noreferrer">Source de vérification ↗</a>'
        icon={'X':'𝕏','Instagram':'◎','TikTok':'♪','YouTube':'▶','Rockstar':'R★'}.get(platform,'↗')
        cta=a.get('cta','Ouvrir la publication')
        cards.append(f'<article class="buzz-card" data-platform="{E(platform)}" data-buzz-id="{E(a["id"])}">{visual}<div class="buzz-content"><div class="buzz-meta"><span>{E(platform)}</span><span class="buzz-tag {"rumeur" if label=="Rumeur" else ""}">{E(label)}</span></div><a class="buzz-open buzz-open-{E(platform.lower())}" href="{u}" target="_blank" rel="noopener noreferrer"><span aria-hidden="true">{icon}</span>{E(cta)}<span aria-hidden="true">↗</span></a><h2>{E(a["title"])}</h2><p>{E(a["summary"])}</p><p class="buzz-author">{E(a["author"])}</p><p class="buzz-date">{E(a.get("published_at","date non vérifiée"))}</p><div class="buzz-secondary-links">{article}</div><div class="buzz-votes avis" data-buzz-vote="buzz-{E(a["id"])}"><p>Chargement des notes…</p></div><details class="buzz-evidence"><summary>Vérification et contexte</summary><p>{E(a.get("evidence","Sélection éditoriale ; popularité non mesurée."))}</p><p>Vérifié le {E(date(a["checked_at"]))}</p></details></div></article>')
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
<main><section class="actus-nuit"><div class="wrap"><nav class="buzz-networks" aria-label="Ouvrir les réseaux sociaux"><span>Sur les réseaux</span><a href="https://x.com/rockstargames" target="_blank" rel="noopener noreferrer"><b aria-hidden="true">𝕏</b>Rockstar sur X ↗</a><a href="https://www.instagram.com/rockstargames/" target="_blank" rel="noopener noreferrer"><b aria-hidden="true">◎</b>Instagram ↗</a><a href="https://www.tiktok.com/@rockstargames" target="_blank" rel="noopener noreferrer"><b aria-hidden="true">♪</b>TikTok ↗</a><a href="https://x.com/gtavifrancecom" target="_blank" rel="noopener noreferrer"><b aria-hidden="true">𝕏</b>Notre compte ↗</a></nav><p class="maj"><i></i><b>La sélection</b> · Dernier passage : <time datetime="{E(d.get('updated_at') or '')}">{E(date(d.get('updated_at')))}</time></p>
<div class="buzz-toolbar"><div class="buzz-filters" role="group" aria-label="Filtrer par réseau">{filters}</div><label class="buzz-search" for="buzz-search">Chercher dans le buzz<input id="buzz-search" type="search" placeholder="Trailer, Vice City, création…" autocomplete="off"></label></div>
<p id="buzz-count" class="buzz-total" aria-live="polite">{len(cards)} sujets dans la sélection</p><div id="buzz-grid" class="buzz-grid">{''.join(cards)}</div><p id="buzz-no-results" class="buzz-empty" {'hidden' if cards else ''}>Aucun sujet pour ce filtre. Les prochaines trouvailles apparaîtront ici après vérification.</p>
<noscript><p>Tous les sujets sont affichés. Activez JavaScript pour utiliser les filtres.</p></noscript>
<aside class="buzz-note"><b>Du contexte, pas du bruit.</b> Une sélection éditoriale ne prouve pas qu’un sujet est viral. Les chiffres de vues et de partages sont affichés uniquement lorsqu’ils ont été constatés et datés. Les rumeurs restent étiquetées. Les publications sociales sont intégrées depuis leurs réseaux, avec un lien vers leur auteur. Leur lecture dépend de la disponibilité du réseau et de ses réglages.</aside></div></section>
<section class="papier"><div class="wrap"><div class="rubrique"><span class="num">01</span><h2>À toi de jouer</h2><p>Une trouvaille à partager, une théorie à discuter ? Retrouve la communauté sur le Mur de Vice City.</p></div><div class="boutons"><a class="btn" href="communaute.html">Rejoindre la discussion →</a><a class="lien" href="https://x.com/gtavifrancecom" target="_blank" rel="noopener noreferrer">GTA VI France sur X ↗</a></div></div></section>
<section><div class="wrap"><div class="rubrique"><span class="num">02</span><h2>Le journal de veille</h2><p>Cinq passages de démarrage, puis une veille horaire jusqu’au 27 octobre à 6 h, heure de Paris. Les restrictions des plateformes peuvent limiter la couverture.</p></div><p class="buzz-date">{E(d.get('schedule','Initialisation'))}</p><ol class="buzz-journal">{runs or '<li>Le premier passage est en préparation.</li>'}</ol></div></section></main>
<script src="assets/site.js?v=buzz-social-20261026"></script><script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script><script src="assets/buzz.js?v={v}"></script></body></html>
"""
    (ROOT/'buzz.html').write_text(page)
    print('Buzz:',len(cards),'sujets;',len(d.get('runs',[])),'passages')
if __name__=='__main__':render()
