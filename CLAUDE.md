# gtavifrance.com : règles pour être trouvé sur Google (11/10/2026)

Constat : presque tous les visiteurs extérieurs arrivent par Google sur UN article qui répond à une recherche précise (la fuite Cyberleek du 08/10 : 28 visites Google en 7 jours, dont la moitié sur les versions traduites zh, pl, tr, ru, it, tw). Chaque article est une porte d'entrée. Ces règles complètent le prompt de la routine journaliste, elles ne le remplacent pas.

## Choix des sujets
- Priorité aux sujets que les gens TAPENT dans Google : fuites, date et heure de sortie, prix, précommande, préchargement, version PC, PS4/PS5/Xbox, trailer, carte, personnages, taille du téléchargement, éditions, collector.
- Un sujet qui buzze chez plusieurs médias = article dans l'heure ; être parmi les premiers compte plus que la longueur.
- S'il n'y a « rien de neuf » : écris à la place UN article « question » qui répond à une recherche fréquente pas encore couverte par un article du site (ex. « GTA 6 sur PC : ce qu'on sait », « GTA 6 sur PS4 ? », « À quelle heure sort GTA 6 ? », « Quelle édition de GTA 6 choisir ? », « Taille de GTA 6 sur PS5 »). Uniquement avec les faits sûrs et des sources présentes dans data/ ; ce qui est inconnu est dit inconnu. Maximum un article question par passage, jamais deux fois la même question (vérifie les titres existants).

## Titre, chapô, adresse
- Titre (t) : commence par « GTA 6 » puis les mots exacts que l'on chercherait (nom propre, chiffre, plateforme). 55 à 75 caractères, factuel, pas de jeu de mots. Ex. « GTA 6 : Cyberleek menace de publier une build complète du jeu ».
- Chapô (d) : répond à la question en une phrase dès le début (qui, quoi, quand), sans suspense : c'est ce que Google affiche.
- id : date + 3 à 6 mots-clés en ascii (ex. 2026-10-08-cyberleek-build-complete-gta6), jamais de mots vides.
- Titre anglais (en.t) : écrit pour les recherches anglaises (« GTA 6 PC release: what we know »), pas une traduction mot à mot.

## Dans le texte
- Un <h2> formulé comme la question que se pose le lecteur, avec la réponse juste dessous.
- 2 à 3 liens internes vers des articles plus anciens du site sur le même sujet (journal/<id>.html, relatifs), en plus du lien vers une page (sortie.html, prix.html…).
- Rebondissement sur un sujet déjà couvert : nouvel article qui renvoie vers le précédent, avec un titre qui dit ce qui change.

## Interdits
- Pas de titre trompeur, pas de rumeur présentée comme un fait, pas de bourrage de mots-clés : Google déclasse, AdSense refuse.

## Images : une photo trouvée par mot-clé, propre à chaque article (11/10/2026)
Articles Cyberleek (id contenant « cyberleek ») : image = logo Cyberleek + bandeau accroche (tools/img_cyberleek.py, kw = accroche), jamais de capture ni vidéo fuitée.
Pour chaque article, cherche une image par mot-clé du sujet et télécharge-la dans assets/img/articles/<id>.jpg ; jamais d'image sans rapport avec le sujet.
- data/images_rockstar.json ne sert plus : aucune image de banque, aucun « Artwork officiel n°X ».
- Mot-clé : 1 ou 2 mots précis du sujet (« PS5 Pro », « Grand Rex », « Cyberleek », « Strauss Zelnick »). L'image montre le sujet lui-même : la console pour une console, le lieu pour un lieu, la personne pour une personne, la jaquette ou la boîte pour un produit, la capture de la page pour un site ou un message cité.
- Avec réseau : `python3 tools/img_article.py <id> "<mot-clé>"` (1200 px, JPEG q85, refuse les doublons), OUVRE l'image (Read) ; hors sujet : `--rang 1`, 2… ou autre mot-clé ; image choisie à la main : `--url <url>`. Puis `python3 -c "import sys;sys.path.insert(0,'tools');import img_auto as m;a=m.charge();x=[y for y in a if y['id']=='<id>'][0];m.appliquer(x,'<site>');m.sauve(a)"`.
- Sans réseau (routine Solange) : écris le champ "kw" (mot-clé) dans l'article ; le serveur lance tools/img_auto.py qui télécharge l'image et pose la figure.
- Jamais deux articles avec la même image. Jamais de lien direct vers le site d'origine : toujours le fichier local. Miniature (img) et figure de l'article = le même fichier ; figcaption « Image : <site d'origine> ».
