# Hub soluce GTA 6 (18/11/2026)

Pages : `guide.html` (hub « Soluce GTA 6 »), `carte.html` (Leaflet 1.9.4 cdnjs, CRS.Simple), `trophees.html`, `collectibles.html`, `missions.html`, ×17 langues via `tools/prerender.py` (PAGES).

Données :
- `data/trophees.json` : 55 trophées PSN (nom officiel, grade, catégorie, description en/fr, compteur `max`, `couche` de carte, `spoiler`).
- `data/carte.json` : `regions` (polygones du schéma), `couches` (totaux d'après les trophées), `points` (vides au départ, ajoutés seulement vérifiés). Repère `schema-v1` = notre schéma 1000×1000 `assets/img/carte/leonida-schema.svg`, pas la carte officielle. Quand Rockstar publie la carte officielle : nouveau fond, `repere` changé, x/y recalés.
- `data/soluce/gta6.json` : fiches missions (schéma `data/soluce/schema.json`) + `hub_articles`.

Build : `python3 tools/soluce.py && python3 tools/prerender.py && python3 tools/pub.py && python3 tools/version.py`.
`tools/soluce.py` remplit les blocs `<!--sl:…-->` des pages et écrit les textes dans `tools/i18n/fr.json`/`en.json` (titres d'articles : 17 langues) ; les autres langues : `tools/traduire_i18n.py` (workflow traduire.yml quand `en.json` change). Idempotent.
JS : `assets/soluce.js` (progression dans localStorage `gtavif-soluce-v1`, try/catch). CSS : `assets/soluce.css` (sombre). Liens profonds : `carte.html#c=<couche>`, `carte.html#p=<id point>`.
Routine qui alimente : `~/.claude/scheduled-tasks/gtavifrance-solutions/SKILL.md`.

## V2 (18/11/2026)
- `tools/soluce_import.py` : relit PowerPyx + GTABase, remplit chapitres, triches (triches.html), points méditation/drones/banques/garages/braquages/stands de tir (positions approximatives, `approx: true`). À lancer avant soluce.py, puis traduire_i18n.py.

## Carte : positions réelles uniquement (18/11/2026)
Aucun x/y estimé. `carte.json.fond_officiel` = image officielle Rockstar (fichier local) ; positions dans `data/carte_positions.json` ({id: {x, y, captures:[2 URL distinctes]}}), appliquées par soluce_import seulement si fond officiel + 2 captures. Sans fond : carte remplacée par un encart, liste filtrable `#ct-liste`. La tâche gtavifrance-soluce-horaire signale la carte officielle Rockstar dès le 19/11 0 h.
