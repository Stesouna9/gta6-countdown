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

## Images : elles doivent correspondre à l'actu (11/10/2026)
Constat : trop d'articles reçoivent un « Artwork officiel n°X » pris au hasard dans data/images_rockstar.json (descriptions génériques), sans rapport avec le sujet.
- Avant de choisir, OUVRE les candidats avec Read (les images sont dans le dépôt, chemin = champ f) et vérifie ce qu'elles montrent. Ne te fie jamais au seul champ desc quand il vaut « Artwork officiel n°X ».
- Le sujet décide de l'image : personnage nommé (Jason, Lucia, Raul…) = son portrait ; lieu (Vice City, Leonida, Brooklyn, Paris) = vue de lieu ; véhicule, radio, musique, collector, boutique = l'image de cet objet ou de cette scène ; PC, procès, piratage, arrestation = vue neutre de Vice City, jamais un personnage qui n'a rien à voir.
- Source rockstargames.com / boutique / YouTube Rockstar : l'image officielle de la source passe avant la banque.
- Mieux vaut une image un peu répétée mais pertinente qu'une image neuve hors sujet : la règle de variété cède devant la pertinence si aucune image neuve ne convient.
- Quand tu regardes une image de la banque dont desc est générique, corrige desc dans data/images_rockstar.json avec ce que tu vois (personnage, lieu, ambiance) : la banque s'améliore à chaque passage.
