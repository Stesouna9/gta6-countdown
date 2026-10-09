# Bible « GTA Soluce » — OKALAM Studio

Version 0.1, 9 octobre 2026. Document de référence pour l'app iOS/Android et le site de soluces couvrant tous les GTA. Base de départ : triches-gta5 (hub codes, 5 jeux, PWA) et gtavifrance.com (17 langues, routines Solange, Vice Bay Radio).

## 1. Promesse

Une seule app pour finir n'importe quel GTA à 100 % : missions pas à pas, médailles d'or, collectibles sur carte, codes de triche, véhicules, trophées, et le jour J pour GTA VI. Gratuite, hors ligne, sans compte, en 17 langues. Ton : rédaction du Virus Bus (Solange, Gabriel Janvier, Daniel, Lara, Amélie, Chloé), jamais de remplissage, jamais de copie de wiki.

## 2. Jeux couverts (ordre de production)

| Priorité | Jeu | Pourquoi | Volume estimé |
|---|---|---|---|
| 1 | GTA VI (2026) | Sortie 19 novembre, trafic maximal, le site est déjà la référence | missions J+1 après sortie, en continu |
| 2 | GTA V + Online | Le plus joué, 69 missions histoire, 3 braquages, 58 Strangers and Freaks | 400 fiches |
| 3 | GTA San Andreas (+ Definitive) | Culte, 100 % long (tags, huîtres, fers à cheval) | 350 fiches |
| 4 | GTA Vice City | Lien direct avec GTA VI, 80s | 200 fiches |
| 5 | GTA IV + Lost and Damned + Ballad of Gay Tony | 88 + 22 + 26 missions, pigeons | 300 fiches |
| 6 | GTA III | 73 missions, paquets cachés | 150 fiches |
| 7 | Liberty City Stories, Vice City Stories, Chinatown Wars | Complétude, faible trafic | 250 fiches |

Les codes de triche de triches-gta5 (San Andreas 57, Vice City 43, III 22, IV 26, V 36) sont repris tels quels dans `cheats`.

## 3. Types de contenu (une fiche = un objet JSON, voir `data/soluce/schema.json`)

- **mission** : titre, donneur, protagoniste, lieu, prérequis, récompense, étapes numérotées, objectifs médaille d'or, astuces, erreurs classiques, choix et conséquences, vidéo (lien YouTube officiel ou propre), carte.
- **heist** (GTA V, VI) : approches, équipe, part de chaque membre, préparations, meilleur gain.
- **side** : Strangers and Freaks, activités, courses, assassinats Lester (avec plan bourse).
- **collectible** : type (lettres, OVNI, tags, huîtres, pigeons, paquets), coordonnées x/y sur carte du jeu, lot, récompense au total.
- **cheat** : nom, catégorie, PC, PlayStation, Xbox, téléphone (schéma triches-gta5).
- **vehicle** : classe, où le trouver, stats, prix, modifiable.
- **trophy** : nom, description, conditions, manquable, lié à missions.
- **guide** : articles transversaux (argent facile, 100 %, bourse, ordre conseillé).
- **map** : image de la carte par jeu avec calques (collectibles, planques, magasins).

Champs communs : `id`, `game`, `type`, `order`, `missable` (bool), `spoiler` (0 à 3), `platforms`, `updated`, `author`, `sources`, puis 17 langues `{t, d, h}` comme `data/articles.json` (clé `idn` pour l'indonésien).

## 4. Règles éditoriales

- Zéro paraphrase de wiki ou de guide concurrent : on joue, on vérifie, on écrit. Sources citées (Rockstar, Game Informer, IGN) uniquement pour les faits de contexte.
- Une étape = une action vérifiable. Phrases courtes. Pas de tiret cadratin, pas de point d'exclamation, pas de « plongée ».
- Spoilers masqués par défaut au delà du niveau 1 (bouton « révéler »).
- Médaille d'or : conditions exactes du jeu, chiffres vérifiés (temps, précision, dégâts).
- Chaque fiche signée par un passager du Virus Bus selon le sujet (Solange missions, Daniel technique PC, Lara carte et nature, Chloé 80s et goodies, Gabriel Janvier véhicules et radio, Amélie secrets et théories).
- Images : captures maison ou banque Rockstar (`data/images_rockstar.json`), jamais d'image d'un média.
- 17 langues obligatoires, fr et en écrites, autres traduites par la routine.

## 5. Production

- Routine cloud « soluce » (même modèle que `journaliste`) : chaque nuit, 5 fiches à partir de `data/soluce/<jeu>.json` (champ `todo`), écrit fr puis en puis 15 traductions, régénère, pousse. Réseau coupé : les faits viennent des fiches `todo` préremplies à la main (titre, donneur, objectifs or) et de la connaissance publique.
- Validation : Gabriel joue et coche `verifie: true`. Fiches non vérifiées affichées avec mention « en relecture ».
- Suivi : `data/soluce/etat.json` (par jeu : total, écrites, vérifiées, 17 langues).

## 6. Produit app (voir `docs/APP_MOBILE.md`)

Écran d'accueil : jeu en cours (choisi une fois), progression 100 % (cases cochées localement), prochaine mission, raccourcis codes et carte. Onglets : Missions, Carte, Codes, Collection, Actus (flux gtavifrance), Radio (Vice Bay). Hors ligne complet, données embarquées et mises à jour par JSON delta. Pas de compte. Pub discrète (AdSense/AdMob, même éditeur ca-pub-8121423865459620) et achat unique « sans pub ». Notifications : sortie GTA VI, nouvelles fiches du jeu suivi.

## 7. Noms et identifiants proposés

- Nom : « GTA Soluce » (FR) / « GTA Guide » (stores internationaux, nom de marque Rockstar non utilisable dans le titre : vérifier, sinon « VI Guide by VI Countdown »).
- Bundle iOS `com.okalamstudio.gtasoluce`, package Android `com.okalamstudio.gtasoluce`.
- Domaine : gtavifrance.com/soluce/ (SEO existant) puis sous-domaine soluce.gtavifrance.com si volume.

## 8. Prochaines étapes

1. Valider la liste des jeux et le nom.
2. Remplir `data/soluce/gta5.json` (missions histoire, déjà listées) avec objectifs or : Gabriel ou routine.
3. Construire la routine « soluce » sur le modèle `journaliste`.
4. Pages web `soluce.html` + `soluce/<jeu>/<id>.html` via `tools/pub.py`.
5. Coquilles iOS et Android (plan dans `docs/APP_MOBILE.md`).
