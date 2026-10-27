# Bible GTA 6 — plan (27/10/2026)

Demande de Gabriel (22/10) : une encyclopédie complète de ce qu'on sait du jeu, à dépasser gtasix.fr sans copier. Vérité unique : ce que Rockstar a publié (site officiel, Newswire, trailers 1-3, Extended Look) ou ce que la presse sérieuse rapporte. Jamais de contenu de fuite (Cyberleek, build volée, fuite 2022), jamais de lien vers une fuite.

## Arborescence
- `bible.html` (+ `<l>/bible.html`, 17 langues) : sommaire par rubrique (personnages, lieux, jeu, acheter, guides).
- `bible/<id>.html` (+ `<l>/bible/<id>.html`) : une fiche par entrée.
- Données : `data/bible.json` (liste d'entrées : id, type, img, statut, date, sources, articles liés). Textes : clés i18n `bb_<id>_t` (titre), `_r` (réponse directe), `_c` (encadré confirmé, une puce par ligne), `_b` (corps, paragraphes séparés par ligne vide, puces « - »), dans `tools/i18n/fr.json` et `en.json` ; 15 autres langues par `tools/traduire_i18n.py`.
- Génération : section « 4e. Bible » de `tools/pub.py` (même mécanique que « 4d. Le Verdict du 19 »).

## Modèle de fiche
1. En-tête sombre : rubrique, titre, image officielle Rockstar (`assets/img/rockstar/`), étiquette Confirmé / Rapporté.
2. Réponse directe en 2 lignes (ce que Google et les IA citent).
3. Encadré « Ce qui est confirmé » : 3 à 6 puces, uniquement officiel.
4. Corps : 2 à 4 courts paragraphes (contexte, ce que la presse rapporte, ce qui reste inconnu dit inconnu).
5. Sources datées (Rockstar, Bloomberg, IGN…), liens vers nos articles (`journal/<id>.html`), fiches liées.
6. JSON-LD Article + BreadcrumbList ; hreflang 17 langues ; thème sombre (fond `--ink`, cartes `#1f1828`).

## Ordre de priorité (ce qui sera cherché le 19/11)
1. Personnages : Jason, Lucia, Cal, Boobie, Dre'Quan, Real Dimez, Raul, Brian Heder. **Vague 1 (27/10)**
2. Lieux : Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia, Mount Kalaga. **Vague 1**
3. Acheter : éditions et prix, précommande, plateformes et PC, préchargement et heure. **Vague 1 : éditions**
4. Débuter : premiers pas, Jason ou Lucia, roue des armes, intérieurs, téléphone. **Vague 1 : débuter**
5. Argent : ce qu'on sait des braquages et de la « criminalité improvisée » (Extended Look, Bloomberg).
6. Véhicules et marques (Grotti, Vapid, Shitzu, Dinka…), armes, faune.
7. Radio et musique (8 stations), réseaux in-game, Online (officiel seulement).
8. Chronologie du développement, trailers 1-3, Extended Look, histoire de la série (ordre des GTA).
9. Après sortie (14/11+) : la routine gtavifrance-solutions prend le relais (missions, trophées, carte).

## Règles
- Étiquette Confirmé = source Rockstar/Take-Two. Rapporté = presse (nom + date). Ne jamais présenter un rapporté comme confirmé.
- Thème sombre obligatoire. Mobile : aucune largeur > écran.
- Ne pas toucher aux pubs maison (maison(), .maison-*, assets/img/pub/).
- Après traduction : vérifier les noms propres (Leonida, Vice City, Grassrivers, Port Gellhorn, Jason Duval, Lucia Caminos…) dans les 15 langues.

## Suivi
- 27/10 : plan, générateur, vague 1 (voir BIBLE_CROISSANCE.md).
- 27/10 : vague 1 en ligne, 16 fiches (8 personnages, 6 régions, éditions, débuter). Leçon : un segment de texte = une clé i18n (bb_<id>_c1.., _s1t/_s1p..), Google écrase les sauts de ligne ; noms propres GTA 6 ajoutés à NOMS de traduire.py.
- À faire (vague 2, 28/10) : argent/braquages, véhicules et marques, armes, faune, radio et musique (8 stations), précommande et plateformes/PC, préchargement et heure, chronologie et trailers, Online (officiel), histoire de la série. Ajouter chaque fiche dans data/bible.json + textes fr/en, rebuild, IndexNow.
