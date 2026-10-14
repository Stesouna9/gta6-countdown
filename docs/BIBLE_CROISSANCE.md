# Bible croissance gtavifrance.com (14/10/2026)

Objectif : passer de ~50 visites/jour à plusieurs centaines avant le 19/11/2026 (sortie GTA 6), pics de plusieurs milliers les jours d'annonce. Budget quasi nul, tout automatisé ou semi-automatique. Source : synthèse ChatGPT + Grok + Gemini + recherche web (14/10/2026). Mise en place par Claude (session La Soso + session GTAVIFRANCE), relue par ChatGPT.

Propriétaires : **LS** = session La Soso (relais, veille, bible) · **GV** = session GTAVIFRANCE (technique site) · **PUB** = session PUB (pubs, ne pas toucher) · **DOC** = Gabriel seul (comptes, jetons, clics d'acceptation).

## Axes, par impact

### 1. Vitesse + valeur ajoutée (impact très élevé)
- [x] Veille officielle Newswire, YouTube Rockstar, r/GTA6 toutes les 5 min : tools/veille.py -> live/veille.json (LS, 14/10)
- [ ] Alerte à Solange quand un élément officiel « nouveau » apparaît (LS)
- [ ] Règle d'écriture : publier < 30 min après la source ; confirmé vs rumeur ; 1 à 2 § de contexte FR ; sources citées ; grande image officielle (GV/routine journaliste)
- [x] Article-alerte avec bandeau 🚨 (Bloomberg, 14/10) : modèle à réutiliser pour tout scoop

### 2. Google Discover + Actualités (impact très élevé)
- [x] max-image-preview:large déjà en place
- [ ] Images ≥ 1200 px paysage sur tous les articles (GV, contrôler tools/img_article.py)
- [ ] NewsArticle : auteur en Person, éditeur GTAVIFRANCE ; pages auteur ; À propos, équipe, corrections (GV)
- [ ] hreflang vérifié sur 17 langues ; Core Web Vitals mobile > 85 PageSpeed (GV)
- [ ] Google Publisher Center : inscrire le site (DOC, connexion Google)
- Interdit : clickbait, titres « ce que vous avez raté » (Discover 2026 le pénalise, nos règles aussi)

### 3. Relais automatiques (impact élevé)
- [x] tools/relais.py : chaque nouvel article -> Telegram, Bluesky, Discord (cron 5 min, serveur Sites). Secrets dans /etc/gtavifrance-relais.env (TELEGRAM_TOKEN, TELEGRAM_CHAT, BSKY_HANDLE, BSKY_APP_PASSWORD, DISCORD_WEBHOOK)
- [ ] DOC : créer canal Telegram + bot, compte Bluesky (mot de passe d'application), webhook Discord ; donner les jetons
- [ ] Compte X : vérifier d'abord si @GTAVIFRANCE (~13k abonnés selon Grok, non vérifié) appartient à Doc ; sinon créer. Texte + image, lien en premier commentaire, jamais de liens nus en rafale. API X payante : publication semi-manuelle
- [ ] WhatsApp Channel : à créer à la main (pas d'API publique)
- [ ] Reddit r/GTA6, r/jeuxvideo : à la main, résumé utile + site en source ; 1 post/jour max, jamais de spam
- [ ] Flipboard / Feedly : flux feed.xml

### 4. Rétention (impact moyen-élevé)
- [ ] Notifications push web (OneSignal gratuit) (GV)
- [ ] Newsletter RSS -> mail hebdo + alertes breaking (Brevo gratuit) (GV)
- [ ] Mesure : compteur de vues par article en ligne (tools/vues_articles.py)

### 5. Audience en plus (impact moyen)
- [x] Galerie photos officielles : photos.html (66 images créditées Rockstar)
- [ ] Shorts / TikTok / Reels : clips auto (tools/clip.py existe) avec lien du site en bio
- [ ] Outils gratuits qui attirent des liens : compteur, comparateur de prix, checklist précommande
- [ ] Instagram @vicebayradio : lien https://gtavifrance.com dans la bio (DOC)
- [ ] Articles evergreen : date/prix/éditions, heure de sortie + préchargement, carte, PC ? ; mots-clés en position 11-20 de Search Console à réoptimiser

## Pièges
Agrégation pure (Discover nul) · images non officielles ou fuitées hébergées (DMCA : embed, pas copie) · fuites publiées sans relecture · comptes neufs qui ne postent que des liens (ban 48 h) · hreflang cassé · sur-automatisation sans contrôle · pubs qui ralentissent le site (PUB).

## Calendrier (J-36 le 14/10)
- 14-21/10 : relais + veille (fait), jetons DOC, compte X, push/newsletter (GV), Publisher Center (DOC), bio Instagram.
- 22-28/10 : 3 à 5 articles/jour sur les sujets chauds, premiers Shorts, 5 à 10 backlinks faciles, Reddit quotidien.
- 29/10-4/11 : volume + guides précommande/préchargement, bilan Search Console, test de charge du serveur.
- 5-14/11 : mode breaking ; préchargement 12/11 en direct ; relance push et newsletter.
- 15-19/11 : modèles d'articles jour J (serveurs, mode performance, guide débutant), live blog ; après le 19 : guides post-lancement.

## Mesures (à relever chaque lundi, journal ci-dessous)
Visites/jour (GoatCounter, data/audience.json) · top 5 articles (vues par article) · clics Search Console · abonnés push/newsletter/Telegram · nombre d'articles publiés < 30 min après la source.

## Journal d'application
- 14/10 : galerie photos, article Bloomberg, compteur de vues, veille, relais, synthèse des 3 IA, bible créée.

## Relecture ChatGPT (14/10/2026) : corrections retenues
Verdict : bon plan, mais trop centré sur la vitesse ; sécuriser d'abord indexation, qualité et fidélisation.
1. Avant d'accélérer : Search Console (pages indexées par langue, erreurs, canoniques, sitemaps) ; analyser les 50 visites actuelles ; maillage interne systématique. (GV, cette semaine)
2. Veille ≠ publication en 30 min garantie : séparer détection, vérification, rédaction, publication, diffusion. Publication auto seulement pour infos confirmées par source fiable ; rumeurs sensibles en validation humaine ; mention confirmé/rumeur/analyse, lien source, heure de vérification, historique des corrections. Newswire et YouTube officiel = sources primaires ; Reddit = piste, jamais source.
3. Discover : aucune garantie. Données structurées avec dates de publication ET de modification. Person seulement pour un auteur humain réel : nos signatures (Solange Rocheval, passagers du Virus Bus) sont des personnages, donc Organization (éditeur GTAVIFRANCE) ou « rédaction » pour ceux-là, sinon risque de faux auteur. Publisher Center n'est pas un préalable.
4. Contenu IA multilingue : Google juge abusif le contenu de masse sans valeur propre, traduit ou non. Valeur distincte obligatoire (contexte FR, comparaison, conséquences pour les joueurs, sources primaires) ; contrôle des traductions ; cadence selon l'actu réelle, pas « 3 à 5 par jour ».
5. Canaux : d'abord Telegram, Discord, Bluesky pendant 2 semaines, puis développer ce qui rapporte. Liens UTM distincts par canal. Push et newsletter avec consentement et désabonnement. X : tester lien dans le post vs en réponse.
6. Backlinks : pas d'annuaires ni d'outils de masse. 1 ou 2 actifs utiles : chronologie interactive des annonces, FAQ documentée, carte de Leonida sourcée, page « informations confirmées » datée. Images officielles : respecter les conditions d'usage de Rockstar.
7. Calendrier révisé : 14-21/10 audit indexation, automatisations, mesure de référence · 22-28/10 guides evergreen, pages thématiques, tests de diffusion, premières vidéos · 29/10-4/11 guides précommande vérifiés, FAQ, test de charge, plan de secours · 5-11/11 veille renforcée, articles conditionnels · 12-18/11 préchargement (minuit heure locale), FAQ technique, préparation du direct · 19/11 direct horodaté · 20/11-3/12 guides débutant, FAQ, solutions aux problèmes.
8. Indicateurs ajoutés : pages indexées par langue ; impressions, clics, CTR, position ; sessions par canal, nouveaux vs récurrents ; inscriptions et clics push/newsletter ; temps de réponse, erreurs de publication, doublons ; temps de maintenance. Bilan hebdo : 3 décisions (arrêter, améliorer, développer).
9. Manquait : plan de secours (source indisponible, automatisation en panne, pic de trafic) ; règles de droit et modération (images, plateformes, données perso) ; objectifs mesurables (proposition : 150 visites/jour à 7 j, 500 à 30 j, 3 000 le 19/11, à valider par Doc).

## Passerelle Claude <-> ChatGPT
Voir section dédiée ci-dessous (à compléter après décision de Doc).
