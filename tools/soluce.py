"""Hub soluce GTA 6 : remplit les sections générées des pages guide/carte/trophees/collectibles/missions
à partir de data/trophees.json, data/carte.json, data/soluce/gta6.json, et écrit les textes dans tools/i18n/*.json
(fr + en ; les 15 autres langues sont traduites par tools/traduire_i18n.py, workflow traduire.yml).
Idempotent : n'écrit un fichier que s'il change. À lancer avant tools/prerender.py :
  python3 tools/soluce.py && python3 tools/prerender.py && python3 tools/pub.py && python3 tools/version.py"""
import json, os, re, html
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
e = lambda s: html.escape(str(s or ""), quote=True)
tx = lambda s: html.escape(str(s or ""), quote=False)   # texte d'un élément data-i18n : même échappement que prerender.py (idempotent)
LANGS = ["fr", "en", "es", "pt", "de", "it", "ja", "zh", "tw", "ar", "hi", "ru", "ko", "tr", "id", "pl", "vi"]
ART_L = {"id": "idn"}

UI = {  # clé : (fr, en)
 "sl_cat_tr_Screen Filter": ("Filtres d'écran", 'Screen filters'),
 "sl_cat_tr_Environment": ('Environnement', 'Environment'),
 "sl_cat_tr_Spawn Vehicle": ('Véhicules', 'Vehicle spawns'),
 "sl_cat_tr_Combat": ('Combat', 'Combat'),
 "sl_cat_tr_Player": ('Joueur', 'Player'),
 "sl_tr_inc": ('pas encore connue', 'not known yet'),
 "sl_tr_deb": ('Déblocage', 'Unlock'),
 "sl_tr_code": ('Combinaison', 'Combo'),
 "sl_tr_a2": ('Oui : un code activé désactive les trophées et succès ainsi que la sauvegarde. Aucun code ne rend invincible.', 'Yes: an active cheat disables trophies, achievements and saving. No code makes you invincible.'),
 "sl_tr_q2": ('Les triches désactivent-elles les trophées ?', 'Do cheats disable trophies?'),
 "sl_tr_a": ("Les triches n'existent qu'après la fin de l'histoire : la liste apparaît dans Progression > Triches, et chaque code doit d'abord être débloqué par un défi. Ensuite, sortez le téléphone (croix directionnelle haut), maintenez L1 (LB sur Xbox), appuyez sur R1 (RB), puis entrez la combinaison à la croix directionnelle. Les combinaisons sont identiques sur PS5 et Xbox.", 'Cheats only exist after the story ends: the list appears under Progress > Cheats, and each code must first be unlocked through a challenge. Then pull out the phone (D-pad up), hold L1 (LB on Xbox), press R1 (RB) and enter the combo on the D-pad. Combos are the same on PS5 and Xbox.'),
 "sl_tr_q": ('Comment activer les codes de triche dans GTA 6 ?', 'How do you enter cheat codes in GTA 6?'),
 "md_triches": ("Les 61 codes de triche de GTA 6 sur PS5 et Xbox Series : combinaisons, conditions de déblocage, et ce qu'ils désactivent (trophées et sauvegarde).", 'All 61 GTA 6 cheat codes on PS5 and Xbox Series: button combos, unlock requirements, and what they disable (trophies and saving).'),
 "mt_triches": ('Codes de triche GTA 6 : tous les cheats PS5 et Xbox et comment les débloquer', 'GTA 6 cheat codes: every PS5 and Xbox cheat and how to unlock it'),
 "sl_t_tr": ('61 codes de triche', '61 cheat codes'),
 "sl_d_tr": ("Toutes les combinaisons PS5 et Xbox et comment débloquer chaque code.", "Every PS5 and Xbox combo and how to unlock each code."),
 "nav_triches": ('Codes de triche', 'Cheat codes'),
 "sl_conf_n": ('confirmés (2 sources nomment le lieu)', 'confirmed (2 sources name the place)'), "sl_total": ('Total', 'Total'), "sl_total_g": ('Total (principales + optionnelles)', 'Total (main + optional)'),
 "sl_ms_tab": ('Nombre de missions par chapitre', 'Missions per chapter'),
 "sl_aconf_c": ('à confirmer', 'to be confirmed'),
 "sl_lucia": ('Lucia seule', 'Lucia only'),
 "sl_jason": ('Jason seul', 'Jason only'),
 "sl_manquable": ('manquable', 'missable'),
 "sl_tr_mode": ("Comment entrer un code", "How to enter a code"),
 "sl_tr_e1": ("Sortez le téléphone", "Take out the phone"),
 "sl_tr_e2": ("Maintenez", "Hold"),
 "sl_tr_e2b": ("puis appuyez sur", "then press"),
 "sl_tr_e3": ("Entrez la combinaison à la croix directionnelle", "Enter the combination on the D-pad"),
 "sl_tr_e4": ("Combinaisons identiques sur PS5 et Xbox. Un code actif désactive trophées, succès et sauvegarde.", "Same combinations on PS5 and Xbox. An active code disables trophies, achievements and saving."),
 "sl_tr_rech": ("Rechercher un code (véhicule, arme, argent…)", "Search a code (vehicle, weapon, money…)"),
 "sl_conf_seul": ("Confirmés seulement", "Confirmed only"),
 "sl_copier": ("Copier", "Copy"),
 "sl_copie": ("Copié !", "Copied!"),
 "sl_aconf": ("À confirmer", "To be confirmed"),
 "sl_g_platine": ("Platine", "Platinum"), "sl_g_or": ("Or", "Gold"), "sl_g_argent": ("Argent", "Silver"), "sl_g_bronze": ("Bronze", "Bronze"),
 "sl_manq_f": ("Manquables", "Missable"),
 "sl_rev": ("Spoiler : touchez pour révéler", "Spoiler: tap to reveal"),
 "sl_spoil_f": ("Les trophées d'histoire sont floutés : touchez-en un pour le révéler.", "Story trophies are blurred: tap one to reveal it."),
 "sl_som": ("Sommaire", "Contents"),
 "sl_rech_page": ("Rechercher sur la page", "Search this page"),
 "sl_haut": ("Haut de page", "Back to top"),
 "sl_n_res": ("résultats", "results"),
 "sl_optionnelles": ('Optionnelles', 'Optional'),
 "sl_principales": ('Principales', 'Main'),
 "sl_prologue": ('Prologue', 'Prologue'),
 "sl_chap": ('Chapitre', 'Chapter'),
 "nav_soluce": ("Soluce", "Walkthrough"),
 "nav_carte": ("Carte interactive", "Interactive map"),
 "nav_trophees": ("Trophées", "Trophies"),
 "nav_collect": ("Collectibles", "Collectibles"),
 "nav_missions": ("Missions", "Missions"),
 "mt_guide": ("Soluce GTA 6 : guide complet, carte interactive, trophées et missions", "GTA 6 walkthrough: complete guide, interactive map, trophies and missions"),
 "md_guide": ("Soluce GTA 6 en français : carte interactive de Leonida, liste des 55 trophées avec suivi, collectibles, missions et astuces vérifiées, mis à jour chaque jour.",
              "GTA 6 walkthrough: interactive Leonida map, all 55 trophies with a tracker, collectibles, missions and verified tips, updated daily."),
 "gu_t": ("Soluce GTA 6", "GTA 6 walkthrough"),
 "gu_i": ("Carte interactive, trophées, collectibles, missions et astuces : tout pour finir GTA 6 à 100 %, uniquement avec des infos vérifiées.",
          "Interactive map, trophies, collectibles, missions and tips: everything to finish GTA 6 at 100%, verified information only."),
 "mt_carte": ("Carte interactive GTA 6 : tous les lieux et collectibles de Leonida", "GTA 6 interactive map: every Leonida location and collectible"),
 "md_carte": ("Carte interactive de GTA 6 : lieux de méditation, courses de drones, stands de tir, garages, banques, lieux WAiNK et zones de Leonida, à cocher au fil de la partie.",
              "GTA 6 interactive map: meditation spots, drone races, shooting ranges, garages, banks, WAiNK locations and Leonida areas, with progress tracking."),
 "mt_trophees": ("Trophées GTA 6 : les 55 trophées PS5 et le suivi du platine", "GTA 6 trophy list: all 55 PS5 trophies and platinum tracker"),
 "md_trophees": ("Liste officielle des 55 trophées de GTA 6 sur PS5 (1 platine, 2 or, 6 argent, 46 bronze) avec cases à cocher, compteurs et trophées d'histoire masqués.",
                 "Official list of all 55 GTA 6 PS5 trophies (1 platinum, 2 gold, 6 silver, 46 bronze) with checkboxes, counters and hidden story trophies."),
 "mt_collectibles": ("Collectibles GTA 6 : méditation, WAiNK, cartes, drones et garages", "GTA 6 collectibles: meditation, WAiNK, cards, drones and garages"),
 "md_collectibles": ("Tous les collectibles de GTA 6 et combien il y en a : 18 lieux de méditation, 100 lieux WAiNK, 14 courses de drones, 8 garages, 52 zones. Listes cochables.",
                     "Every GTA 6 collectible and how many there are: 18 meditation spots, 100 WAiNK locations, 14 drone races, 8 garages, 52 areas. Checklists."),
 "mt_missions": ("Missions GTA 6 : liste des missions d'histoire et secondaires", "GTA 6 missions: story and side mission list"),
 "md_missions": ("Toutes les missions de GTA 6 : 5 chapitres et un prologue, environ 119 missions principales, missions optionnelles, Strangers & Freaks et durée de l'histoire (60 à 80 h).", 'Every GTA 6 mission: 5 chapters plus a prologue, about 119 main missions, optional missions, Strangers & Freaks and story length (60-80 hours).'),
 "sl_hub_t": ("Soluce GTA 6", "GTA 6 walkthrough"),
 "sl_hub_i": ("Les outils pour finir le jeu, mis à jour chaque jour. Uniquement des infos vérifiées : deux sources concordantes ou une source officielle.",
              "Tools to finish the game, updated daily. Verified information only: two matching sources or one official source."),
 "sl_t_carte": ("Carte interactive", "Interactive map"), "sl_d_carte": ("Leonida, couche par couche : méditation, drones, tir, garages, banques…", "Leonida layer by layer: meditation, drones, shooting, garages, banks…"),
 "sl_t_tp": ("55 trophées", "55 trophies"), "sl_d_tp": ("Liste officielle PS5, cases à cocher et compteurs vers le platine.", "Official PS5 list, checkboxes and counters to the platinum."),
 "sl_t_cl": ("Collectibles", "Collectibles"), "sl_d_cl": ("Combien il y en a, où les trouver, et ce que vous avez déjà.", "How many there are, where to find them, and what you already have."),
 "sl_t_ms": ("Missions", "Missions"), "sl_d_ms": ("Missions secondaires et d'histoire (spoilers masqués).", "Side and story missions (spoilers hidden)."),
 "sl_t_art": ("Astuces et articles soluce", "Tips and walkthrough articles"),
 "sl_nouveau": ("Nouveau", "New"), "sl_maj": ("Mis à jour chaque jour", "Updated daily"),
 "sl_fil": ("Soluce GTA 6", "GTA 6 walkthrough"),
 "sl_avert_carte": ("Carte officielle de Leonida (Rockstar, 19 novembre) avec 86 collectibles et activités : banques, bijouteries, drones, garages, méditations, stands de tir. Touchez un nom de lieu pour voir ce qu'on y fait, cochez vos trouvailles, posez vos repères.", "Official Leonida map (Rockstar, November 19) with 86 collectibles and activities: banks, jewelry stores, drones, garages, meditation spots, shooting ranges. Tap a place name to see what's there, tick off finds, drop your own markers."),
 "sl_schema_cap": ("Touchez une région pour voir ses lieux. Schéma des régions : les emplacements précis s'afficheront sur la carte officielle de Rockstar dès sa publication.", "Tap a region to see its places. Region diagram: exact locations will appear on Rockstar's official map as soon as it is published."),
 "sl_lieux": ("lieux", "places"),
 "sl_off_rech": ("Trouver un lieu sur la carte (ex. Vice Beach, Key Lento)", "Find a place on the map (e.g. Vice Beach, Key Lento)"),
 "sl_off_case": ("Case", "Grid square"),
 "cx_o_its": ("Itinéraires", "Routes"),
 "cx_it_moi": ("Mon itinéraire", "My route"),
 "cx_it_ajouter": ("Ajouter à mon itinéraire", "Add to my route"),
 "cx_it_retirer": ("Retirer de mon itinéraire", "Remove from my route"),
 "cx_it_aj": ("Ajouté à mon itinéraire", "Added to my route"),
 "cx_it_ret": ("Retiré de mon itinéraire", "Removed from my route"),
 "cx_it_rest": ("à trouver", "remaining"),
 "cx_it_vider": ("Vider mon itinéraire", "Clear my route"),
 "cx_it_vide": ("Mon itinéraire : ouvrez un lieu sur la carte, puis « Ajouter à mon itinéraire ».", "My route: open a place on the map, then choose \"Add to my route\"."),
 "cx_it_aide": ("Choisissez une tournée : les étapes sont numérotées dans l'ordre le plus court, à vol d'oiseau. Les lieux trouvés en sortent. Sans position exacte, l'étape est le secteur nommé par le guide.", "Pick a route: stops are numbered in the shortest straight-line order. Found places drop out. Without an exact position, the stop is the area named by the guide."),
 "cx_r_rech": ("Recherche", "Search"),
 "cx_r_pan": ("Panneau", "Panel"),
 "cx_r_nuit": ("Jour / nuit", "Day / night"),
 "cx_r_hasard": ("Lieu au hasard", "Random place"),
 "cx_voir": ("Afficher sur la carte", "Show on map"),
 "cx_ici": ("À faire ici", "Things to do here"),
 "cx_approx": ("Icône posée sur le secteur que nomme le guide : l'emplacement exact se trouve dans ce secteur.", "Icon placed on the area named by the guide: the exact spot is within this area."),
 "cx_secteur": ("Secteur", "Area"),
 "cx_noms": ("Afficher les noms", "Show names"),
 "cx_partager": ("Partager cette vue", "Share this view"),
 "cx_cadre": ("Toute la carte", "Whole map"),
 "cx_plein": ("Plein écran", "Full screen"),
 "cx_rech": ("Chercher un lieu, une banque, un magasin…", "Search a place, bank or shop…"),
 "cx_copie": ("Lien copié", "Link copied"),
 "cx_panneau": ("Lieux et collectibles", "Places and collectibles"),
 "cx_aide_m": ("Astuce : clic droit sur ordinateur ou appui long sur mobile pour poser un repère. Faites-le glisser pour le déplacer.", "Tip: right-click on desktop or long-press on mobile to drop a marker. Drag it to move it."),
 "cx_aide_c": ("Chaque icône est posée sur le secteur que nomme le guide. Touchez-la pour la fiche, cochez ce que vous avez trouvé (progression gardée sur cet appareil). L'œil masque ou affiche un type.", "Each icon sits on the area named by the guide. Tap it for details, tick what you found (progress saved on this device). The eye shows or hides a type."),
 "cx_trouves": ("trouvés", "found"),
 "cx_aide_l": ("Les 87 lieux de la carte officielle. Touchez-en un (ou son nom sur la carte) pour voir ce qu'il y a à faire.", "The 87 places on the official map. Tap one (or its name on the map) to see what to do there."),
 "cx_o_coll": ("Collectibles", "Collectibles"),
 "cx_o_lieux": ("Lieux", "Places"),
 "cx_ajoute": ("Repère enregistré sur cet appareil", "Marker saved on this device"),
 "cx_repere": ("Repère", "Marker"),
 "cx_rien": ("Aucun lieu de ce nom sur la carte", "No place with that name on the map"),
 "cx_lien": ("Copier le lien", "Copy link"),
 "sl_off_vider_q": ("Effacer tous vos repères ?", "Delete all your markers?"),
 "sl_off_vider": ("Tout effacer", "Clear all"),
 "sl_off_mes": ("Mes repères", "My markers"),
 "sl_off_noms": ("Lieux officiels", "Official places"),
 "sl_off_suppr": ("Supprimer", "Delete"),
 "sl_off_nom": ("Nom du repère (ex. carte à collectionner, planque)", "Marker name (e.g. collectible card, hideout)"),
 "sl_off_pose_on": ("Touchez la carte à l'endroit voulu", "Tap the map where you want it"),
 "sl_off_pose": ("📍 Poser un repère", "📍 Drop a marker"),
 "sl_regs_t": ("Lieux par région :", "Places by region:"),
 "sl_off_cap": ("Carte officielle de Leonida (Rockstar, 19 novembre). Touchez un point rose pour son nom, n'importe où pour la case du quadrillage. Posez vos propres repères : ils restent enregistrés sur votre appareil, et se déplacent en les faisant glisser.", "Official Leonida map (Rockstar, November 19). Tap a pink dot for its name, anywhere for the grid square. Drop your own markers: they stay saved on your device and can be dragged."),
 "sl_off_plein": ("Ouvrir en plein écran", "Open full screen"),
 "sl_attente_t": ("Carte réelle dès que Rockstar publie la carte officielle, mise à jour en direct", "Real map as soon as Rockstar publishes the official map, updated live"),
 "sl_attente_p": ("Nous n'affichons aucun emplacement approximatif. Dès que Rockstar publie la carte officielle de Leonida, elle devient le fond de cette page et chaque lieu y est placé à partir de captures de joueurs vérifiées (deux sources). En attendant, tous les lieux connus sont listés ci-dessous.", "We don't show approximate locations. As soon as Rockstar publishes the official Leonida map, it becomes this page's background and each place is pinned from verified player captures (two sources). Meanwhile, every known location is listed below."),
 "sl_attente_l": ("Voir la liste des lieux", "See the list of locations"),
 "sl_liste_h": ("Tous les lieux connus de GTA 6, par région", "Every known GTA 6 location, by region"),
 "sl_liste_p": ("Chaque lieu est relevé dans un guide publié depuis la sortie, avec sa source. « Confirmé » : deux sources indépendantes le nomment. Cochez ceux que vous avez trouvés.", "Each place comes from a guide published since launch, with its source. \"Confirmed\": two independent sources name it. Tick the ones you've found."),
 "sl_f_types": ("Tous les types", "All types"), "sl_f_regs": ("Toutes les régions", "All regions"), "sl_f_noreg": ("Région non précisée", "Region not specified"),
 "sl_f_stats": ("Tous les statuts", "All statuses"), "sl_rech": ("Rechercher un lieu", "Search a location"), "sl_f_vide": ("Aucun lieu ne correspond à ces filtres.", "No location matches these filters."),
 "sl_trouve": ("Trouvé", "Found"), "sl_attr_off": ("Carte officielle Rockstar Games", "Official Rockstar Games map"),
 "sl_couches": ("Couches", "Layers"), "sl_tout": ("Tout", "All"), "sl_rien": ("Aucune", "None"),
 "sl_cache_faits": ("Masquer les lieux trouvés", "Hide found locations"),
 "sl_carte_h": ("Que trouve-t-on sur la carte de GTA 6 ?", "What is on the GTA 6 map?"),
 "sl_carte_p": ("Leonida compte six régions nommées par Rockstar : Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia et Mount Kalaga. Le tableau ci-dessous donne le nombre de lieux à trouver par catégorie, d'après la liste officielle des trophées.",
                "Leonida has six regions named by Rockstar: Vice City, Leonida Keys, Grassrivers, Port Gellhorn, Ambrosia and Mount Kalaga. The table below gives the number of locations per category, based on the official trophy list."),
 "sl_cat": ("Catégorie", "Category"), "sl_nb": ("Nombre", "Count"), "sl_inconnu": ("non communiqué", "not disclosed"),
 "sl_tp_h": ("Combien de trophées compte GTA 6 ?", "How many trophies does GTA 6 have?"),
 "sl_tp_p": ("GTA 6 compte 55 trophées sur PS5 : 1 platine (« Vice Got a Price! »), 2 or, 6 argent et 46 bronze, pour 1 350 points. Sur Xbox, la liste vaut 1 000 G avec les mêmes noms. Aucun trophée en ligne.",
             "GTA 6 has 55 PS5 trophies: 1 platinum (\"Vice Got a Price!\"), 2 gold, 6 silver and 46 bronze, worth 1,350 points. On Xbox the list is worth 1,000 G with the same names. No online trophies."),
 "sl_tp_q2": ("Quel trophée peut-on rater ?", "Which trophy is missable?"),
 "sl_tp_a2": ("Positive Mental Attitude : la première méditation a lieu pendant le chapitre 1, chez Jason. Les codes de triche désactivent les trophées.",
              "Positive Mental Attitude: the first meditation happens during Chapter 1, at Jason's house. Cheat codes disable trophies."),
 "sl_obtenus": ("obtenus", "earned"), "sl_tous": ("Tous", "All"),
 "sl_cat_collectibles": ("Collectibles", "Collectibles"), "sl_cat_activites": ("Activités", "Activities"), "sl_cat_braquages": ("Braquages", "Heists"),
 "sl_cat_personnages": ("Personnages", "Characters"), "sl_cat_secrets": ("Secrets", "Secrets"), "sl_cat_divers": ("Divers", "Misc"),
 "sl_cat_completion": ("Complétion", "Completion"), "sl_cat_histoire": ("Histoire", "Story"), "sl_cat_platine": ("Platine", "Platinum"),
 "sl_voir_spoil": ("Afficher les trophées d'histoire (spoilers)", "Show story trophies (spoilers)"),
 "sl_spoil_n": ("12 trophées d'histoire sont masqués pour ne rien vous gâcher.", "12 story trophies are hidden to avoid spoilers."),
 "sl_masque_faits": ("Masquer les obtenus", "Hide earned"),
 "sl_raz": ("Remettre à zéro", "Reset"), "sl_raz_ok": ("Remettre toute la progression à zéro ?", "Reset all progress?"),
 "sl_local": ("Votre progression reste sur cet appareil (navigateur), sans compte.", "Your progress stays on this device (browser), no account needed."),
 "sl_sur_carte": ("Sur la carte", "On the map"), "sl_voir": ("Voir sur la carte", "Show on map"),
 "sl_source": ("Source", "Source"), "sl_conf": ("Confirmé", "Confirmed"), "sl_aconf": ("À confirmer", "Unconfirmed"),
 "sl_trouve": ("Trouvé ✓", "Found ✓"), "sl_trouve_non": ("Pas encore trouvé", "Not found yet"),
 "sl_pts_ok": ("points placés sur la carte", "points on the map"),
 "sl_pts_vide": ("Les emplacements sont ajoutés dès qu'ils sont vérifiés (2 sources concordantes ou source officielle).", "Locations are added as soon as they are verified (two matching sources or an official source)."),
 "sl_err": ("La carte n'a pas pu se charger.", "The map could not be loaded."),
 "sl_attr": ("Schéma GTAVIFRANCE, non officiel", "GTAVIFRANCE diagram, unofficial"),
 "sl_cl_q": ("Où trouver", "Where to find"), "sl_trophee": ("Trophée", "Trophy"),
 "sl_cl_i": ("Emplacements réels relevés depuis la sortie : 10 lieux de méditation, 14 lieux de courses de drones, 22 banques, 12 garages, 18 séries de cartes. Les totaux sont confirmés par deux guides indépendants ; chaque lieu cite sa source et reste « à confirmer » tant qu'une seconde source ne l'a pas recoupé.", 'Real locations gathered since launch: 10 meditation spots, 14 drone race locations, 22 banks, 12 garages, 18 card sets. Totals are confirmed by two independent guides; each location cites its source and stays "to be confirmed" until a second source matches it.'),
 "sl_ms_side": ("Missions secondaires : les personnages", "Side missions: the characters"),
 "sl_ms_side_p": ("Sept personnages ont un trophée lié à leurs missions. Terminer leur dernière mission débloque le trophée.", "Seven characters have a trophy tied to their missions. Finishing their last mission unlocks it."),
 "sl_ms_sf": ("Strangers & Freaks : 8 séries", "Strangers & Freaks: 8 strands"),
 "sl_ms_sf_p": ("Il faut terminer 8 séries précises de missions d'inconnus (trophée argent « Strangers & Freaks ») : celles de Kirk, Kyle, Yago et Pilot Pete en font partie ; Shirley, Billy, Andy, Yasmani, Tyrone et Eddie Acosta ne comptent pas. Toutes restent faisables après l'histoire.", 'You must finish 8 specific Strangers & Freaks questlines (silver trophy): Kirk, Kyle, Yago and Pilot Pete count; Shirley, Billy, Andy, Yasmani, Tyrone and Eddie Acosta do not. All remain available after the story.'),
 "sl_ms_hist": ("Missions d'histoire (spoilers)", "Story missions (spoilers)"),
 "sl_ms_hist_p": ("Liste complète des missions par chapitre (titres affichés à l'écran, sans résumé). Les missions optionnelles marquées « manquable » disparaissent si on avance trop.", 'Full mission list per chapter (on-screen titles, no plot summary). Optional missions marked "missable" disappear if you progress too far.'),
 "cx_f_lieux": ("Lieux", "Locations"), "cx_f_coll": ("Collections", "Collections"), "cx_f_act": ("Activités", "Activities"), "sl_w_toutes": ("Toutes les missions", "All missions"), "sl_w_titre": ("soluce complète de la mission", "full mission walkthrough"), "sl_w_k": ("Soluce GTA 6", "GTA 6 walkthrough"), "sl_w_carte": ("Ouvrir la carte de Leonida", "Open the Leonida map"), "sl_w_page": ("Page de la mission", "Mission page"), "cx_f_mis": ("Missions", "Missions"), "cx_mis_ouvrir": ("Ouvrir la soluce", "Open the walkthrough"), "cx_bat": ("Bâtiment", "Building"), "cx_reel": ("Dans la vraie vie", "In real life"), "cx_entrer": ("On peut y entrer", "Can be entered"), "cx_tout_aff": ("Tout afficher", "Show all"), "cx_tout_mas": ("Tout masquer", "Hide all"), "cx_marquer": ("☐ Marquer comme trouvé", "☐ Mark as found"), "cx_deja": ("✓ Trouvé (annuler)", "✓ Found (undo)"), "cx_cache_f": ("Masquer les trouvés", "Hide found"), "cx_f_ville": ("En ville", "Around town"), "cx_src_v": ("Lieux : gtadb.org et contributeurs, CC BY 4.0", "Places: gtadb.org and contributors, CC BY 4.0"), "mt_coffres": ("Codes des coffres GTA 6 : toutes les combinaisons et où les trouver", "GTA 6 safe codes: every combination and where to find it"), "md_coffres": ("Tous les codes de coffres et de portes de GTA 6 vérifiés : Kingpin Bowling 0300, opérations des gangs, missions et monde ouvert, avec le lieu et le chapitre.", "Every verified GTA 6 safe and door code: Kingpin Bowling 0300, gang operations, missions and free roam, with location and chapter."), "sl_t_cf": ("Codes des coffres", "Safe codes"), "cf_q": ("Comment ouvrir un coffre dans GTA 6 ?", "How do you open a safe in GTA 6?"), "cf_a": ("Les coffres des missions et des opérations des gangs ont un code fixe, le même dans toutes les parties : il est dans la liste ci-dessous. Ceux des magasins braqués en monde ouvert changent à chaque fois : menacez un employé ou le patron, ou cherchez une note dans l'arrière-boutique (le mode Focus aide). Sans code, une bombe collante achetée chez Ammu-Nation ouvre la plupart des coffres, mais fait du bruit et peut abîmer le butin. Les coffres des banques ne s'ouvrent pas ainsi.", "Mission and gang operation safes have a fixed code, the same in every playthrough: it is in the list below. Store safes in free roam change every time: threaten an employee or the owner, or look for a note in the back room (Focus mode helps). Without a code, a sticky bomb from Ammu-Nation opens most safes, but it is loud and can damage the loot. Bank vaults cannot be opened this way."), "cf_zero": ("Tapez toujours les 4 chiffres, zéro compris : 0300 marche, 300 est refusé.", "Always type all 4 digits, zero included: 0300 works, 300 is rejected."), "cf_ch": ("Chapitre", "Chapter"), "cf_maj": ("Codes vérifiés sur au moins deux guides. Mise à jour :", "Codes checked against at least two guides. Updated:"), "cf_rech": ("Chercher un lieu ou un code…", "Search a place or a code…"), "cx_f_jeu": ("Dans le jeu", "In the game"), "cx_code": ("Code", "Code"), "sl_w_voir": ("Soluce", "Walkthrough"), "sl_w_astuce": ("Astuce", "Tip"), "sl_w_choix": ("Choix", "Choice"), "sl_w_recomp": ("Récompense", "Reward"), "sl_w_partiel": ("Soluce partielle, complétée dès que deux sources concordent.", "Partial walkthrough, completed once two sources agree."),
 "sl_ms_voir": ("Afficher les missions d'histoire", "Show story missions"),
 "sl_ms_q": ("Combien de missions dans GTA 6 ?", "How many missions are in GTA 6?"),
 "sl_ms_a": ("L'histoire de GTA 6 compte un prologue et 5 chapitres, soit environ 119 missions principales (25, 18, 31, 34 et 10 selon le chapitre), plus une trentaine de missions optionnelles. Comptez 60 à 80 heures ; Rockstar parle de 80 heures avec une partie du contenu optionnel. Pas de médailles ni de rejouer les missions : faites une sauvegarde manuelle au début et à la fin de chaque chapitre.", "GTA 6's story has a prologue and 5 chapters: about 119 main missions (25, 18, 31, 34 and 10 per chapter), plus around thirty optional missions. Expect 60-80 hours; Rockstar quotes 80 hours with some optional content. There are no mission medals and no mission replay: keep a manual save at the start and end of each chapter."),
 "sl_fait": ("Terminé", "Done"), "sl_sources_t": ("Sources", "Sources"),
 "sl_home_t": ("Soluce GTA 6 : la carte interactive est en ligne", "GTA 6 walkthrough: the interactive map is live"),
 "sl_home_i": ("Carte de Leonida, 55 trophées à cocher, collectibles et missions. Mis à jour chaque jour, sans spoiler.", "Leonida map, 55 trophies to tick off, collectibles and missions. Updated daily, spoiler-free."),
}

def sub(src, nom, contenu):
    rx = re.compile(r"(<!--sl:%s-->).*?(<!--/sl:%s-->)" % (nom, nom), re.S)
    assert rx.search(src), nom
    return rx.sub(lambda m: m.group(1) + contenu + m.group(2), src, count=1)

def ecrit(p, s):
    if not os.path.exists(p) or open(p, encoding="utf-8").read() != s:
        open(p, "w", encoding="utf-8").write(s); print("soluce : écrit", p)

def k(id_): return re.sub(r"[^a-zA-Z0-9]", "_", id_)

def main():
    TP = json.load(open("data/trophees.json", encoding="utf-8"))
    CA = json.load(open("data/carte.json", encoding="utf-8"))
    G6 = json.load(open("data/soluce/gta6.json", encoding="utf-8"))
    FR, EN = {}, {}
    autres = {l: {} for l in LANGS if l not in ("fr", "en")}
    for key, (f, en) in UI.items(): FR[key], EN[key] = f, en
    # chiffres des missions et des lieux calculés depuis les données (même ventilation partout)
    ch = G6.get("chapitres") or []
    if ch:
        mp = [sum(1 for m in c["missions"] if not m.get("opt")) for c in ch]
        mo = sum(1 for c in ch for m in c["missions"] if m.get("opt")); P = sum(mp); T = P + mo
        nc = sum(1 for c in ch for m in c["missions"] if m.get("statut") != "confirme")
        det = ", ".join(str(x) for x in mp[1:]); dl = det.rsplit(", ", 1)
        FR["sl_ms_a"] = (f"L'histoire de GTA 6 compte un prologue et {len(ch) - 1} chapitres : {T} missions au total, dont {P} principales ({mp[0]} au prologue, puis {' et '.join(dl)} selon le chapitre) et {mo} optionnelles (sources : PowerPyx et GTABase ; {nc} titres pas encore recoupés sont marqués « à confirmer »). "
                         "Comptez 60 à 80 heures. Pas de médailles ni de rejouer les missions : faites une sauvegarde manuelle au début et à la fin de chaque chapitre.")
        EN["sl_ms_a"] = (f"GTA 6's story has a prologue and {len(ch) - 1} chapters: {T} missions in total, {P} main ({mp[0]} in the prologue, then {' and '.join(dl)} per chapter) and {mo} optional (sources: PowerPyx and GTABase; {nc} titles not yet cross-checked are flagged \"to be confirmed\"). "
                         "Expect 60-80 hours. There are no mission medals and no mission replay: keep a manual save at the start and end of each chapter.")
        FR["md_missions"] = f"Toutes les missions de GTA 6 : un prologue et {len(ch) - 1} chapitres, {T} missions dont {P} principales et {mo} optionnelles, Strangers & Freaks et durée de l'histoire (60 à 80 h)."
        EN["md_missions"] = f"Every GTA 6 mission: a prologue and {len(ch) - 1} chapters, {T} missions ({P} main, {mo} optional), Strangers & Freaks and story length (60-80 h)."
    from collections import Counter
    nb = Counter(pt["couche"] for pt in CA.get("points", []))
    noms = {c["id"]: (c.get("fr", c["id"]).lower(), c.get("en", c["id"])) for c in CA["couches"]}
    lst = [(n, noms[c]) for c, n in nb.items() if c in noms]
    if lst:
        FR["sl_cl_i"] = "Emplacements réels relevés depuis la sortie : " + ", ".join(f"{n} {f}" for n, (f, _) in lst) + ". Les totaux sont confirmés par deux guides indépendants ; un lieu reste « à confirmer » tant qu'une seconde source ne le nomme pas. Il n'apparaît sur la carte qu'une fois situé sur la carte officielle par deux captures de joueurs."
        EN["sl_cl_i"] = "Real locations gathered since launch: " + ", ".join(f"{n} {en_.lower()}" for n, (_, en_) in lst) + ". Totals are confirmed by two independent guides; a location stays \"to be confirmed\" until a second source names it. It only appears on the map once two player captures pin it on the official map."
    # --- trophées
    cats = ["collectibles", "activites", "braquages", "personnages", "secrets", "completion", "divers", "histoire"]
    lis = []
    for t in TP["trophees"]:
        kd = "tpd_" + k(t["id"]); FR[kd], EN[kd] = t["fr"], t["en"]
        cpt = ""
        if t.get("max"):
            cpt = f'<div class="cpt"><button type="button" class="moins" aria-label="-1">−</button><input type="number" min="0" max="{t["max"]}" value="0" inputmode="numeric" aria-label="{e(t["nom"])}"><span>/ {t["max"]}</span><button type="button" class="plus" aria-label="+1">+</button></div>'
        lien = f'<div class="lien"><a href="carte.html#c={t["couche"]}" data-i18n="sl_sur_carte">Sur la carte</a></div>' if t.get("couche") else ""
        rg = f'<img class="tp-ic" src="assets/img/soluce/ic/rang-{t["grade"]}.svg" alt="" width="40" height="40" loading="lazy">' if os.path.exists(f'assets/img/soluce/ic/rang-{t["grade"]}.svg') else ""
        mq = '<span class="sl-badge ko" data-i18n="sl_manquable">manquable</span>' if t.get("manquable") else ""
        lis.append(f'<li class="tp{" spoil" if t["spoiler"] else ""}" data-id="{t["id"]}" data-cat="{t["cat"]}" data-grade="{t["grade"]}"{" data-manq=1" if t.get("manquable") else ""}{" data-max=%s" % t["max"] if t.get("max") else ""}>'
                   f'<input type="checkbox" aria-label="{e(t["nom"])}">{rg}<div class="tp-corps"><h3>{e(t["nom"])}</h3><p class="tp-meta"><span class="gr gr-{t["grade"]}" data-i18n="sl_g_{t["grade"]}">{UI["sl_g_" + t["grade"]][0]}</span>{mq}</p><p class="tp-desc" data-i18n="{kd}">{tx(t["fr"])}</p>{cpt}{lien}</div>'
                   + ('<button type="button" class="tp-rev" data-i18n="sl_rev">Spoiler : touchez pour révéler</button>' if t["spoiler"] else "") + '</li>')
    filtres = '<button type="button" data-filtre="tout" aria-pressed="true" data-i18n="sl_tous">Tous</button>' + "".join(
        f'<button type="button" data-filtre="{c}" aria-pressed="false" data-i18n="sl_cat_{c}">{UI["sl_cat_" + c][0]}</button>' for c in cats if c != "histoire") + '<span class="sl-sep"></span>' + "".join(
        f'<button type="button" data-rang="{g}" aria-pressed="false" data-i18n="sl_g_{g}">{UI["sl_g_" + g][0]}</button>' for g in ("platine", "or", "argent", "bronze")) + '<button type="button" data-manqf="1" aria-pressed="false" data-i18n="sl_manq_f">Manquables</button>'
    # --- couches
    C = {c["id"]: c for c in CA["couches"]}
    rows, blocs = [], []
    for c in CA["couches"]:
        kc = "cl_" + k(c["id"]); FR[kc], EN[kc] = c["fr"], c["en"]
        tot = str(c["total"]) if c["total"] else '<span data-i18n="sl_inconnu">non communiqué</span>'
        rows.append(f'<tr><td><span class="ct-pt" style="background:{c["couleur"]}"></span> <a href="carte.html#c={c["id"]}" data-i18n="{kc}">{tx(c["fr"])}</a></td><td>{tot}</td></tr>')
        note = ""
        if c.get("note_fr"):
            kn = "cln_" + k(c["id"]); FR[kn], EN[kn] = c["note_fr"], c["note_en"]; note = f'<p data-i18n="{kn}">{tx(c["note_fr"])}</p>'
        tp = next((t for t in TP["trophees"] if t["id"] == c.get("trophee")), None)
        tpl = f'<p><span data-i18n="sl_trophee">Trophée</span> : <a href="trophees.html">{e(tp["nom"])}</a> ({tp["grade"]})</p>' if tp else ""
        icl = f'<img class="sl-ic" src="assets/img/soluce/ic/cl-{c["id"]}.svg" alt="" width="32" height="32" loading="lazy">' if os.path.exists(f'assets/img/soluce/ic/cl-{c["id"]}.svg') else f'<span class="ct-pt" style="background:{c["couleur"]}"></span> '
        blocs.append(f'<div class="cl-bloc" id="{c["id"]}"><h2>{icl}<span data-i18n="{kc}">{tx(c["fr"])}</span> <small id="cln-{c["id"]}">0/{c["total"] or "?"}</small></h2>'
                     f'{note}{tpl}<p><a href="carte.html#c={c["id"]}" data-i18n="sl_voir">Voir sur la carte</a></p><ul class="cl-pts" id="cl-{c["id"]}"><li class="cl-vide" data-i18n="sl_pts_vide">{tx(UI["sl_pts_vide"][0])}</li></ul></div>')
    table = '<table class="sl-table"><thead><tr><th data-i18n="sl_cat">Catégorie</th><th data-i18n="sl_nb">Nombre</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>"
    # --- missions
    side, hist = [], []
    for f in G6["fiches"]:
        kf = "ms_" + k(f["id"]); FR[kf], EN[kf] = f["fr"]["t"], f["en"]["t"]
        tp = next((t for t in TP["trophees"] if t["id"] == f.get("trophee")), None)
        tpn = f'<p><span data-i18n="sl_trophee">Trophée</span> : {e(tp["nom"])}</p>' if tp else ""
        carte = f'<div class="ms-carte"><label><input type="checkbox" data-ms="{f["id"]}"> <span data-i18n="sl_fait">Terminé</span></label><h3 data-i18n="{kf}">{tx(f["fr"]["t"])}</h3>{tpn}</div>'
        (hist if f["type"] == "mission" else side).append(carte)
    # --- chapitres (V2 18/11 : PowerPyx + GTABase)
    chap_tab, chap_l = "", ""
    if G6.get("chapitres"):
        rows, tot = [], [0, 0]
        for c in G6["chapitres"]:
            a = sum(not m["opt"] for m in c["missions"]); b = len(c["missions"]) - a; tot[0] += a; tot[1] += b
            nom = '<span data-i18n="sl_prologue">Prologue</span>' if c["n"] == 0 else f'<span data-i18n="sl_chap">Chapitre</span> {c["n"]}'
            rows.append(f"<tr><td>{nom}</td><td>{a}</td><td>{b}</td></tr>")
            lis_m = []
            for m in c["missions"]:
                tags = []
                if m["opt"]: tags.append('<span class="ms-tag" data-i18n="sl_optionnelles">Optionnelles</span>')
                if m.get("manquable"): tags.append('<span class="ms-tag ko" data-i18n="sl_manquable">manquable</span>')
                if m.get("perso"): tags.append(f'<span class="ms-tag" data-i18n="sl_{m["perso"]}">{"Jason seul" if m["perso"] == "jason" else "Lucia seule"}</span>')
                if m["statut"] != "confirme": tags.append('<span class="ms-tag ko" data-i18n="sl_aconf_c">à confirmer</span>')
                w = m.get("w") or {}; wh = ""
                if w.get("fr"):
                    bk = f'mw_{c["n"]}_{k(m["t"]).lower()}'; et = []
                    for i, (sf, se) in enumerate(zip(w["fr"], w.get("en") or w["fr"])):
                        FR[f"{bk}_{i}"], EN[f"{bk}_{i}"] = sf, se; et.append(f'<li data-i18n="{bk}_{i}">{e(sf)}</li>')
                    ex = ""
                    for suf, lab, cle in (("a", "sl_w_astuce", "Astuce"), ("c", "sl_w_choix", "Choix"), ("r", "sl_w_recomp", "Récompense")):
                        vf = w.get(suf + "f") or (w.get("r") if suf == "r" else ""); ve = w.get(suf + "e") or vf
                        if vf:
                            FR[f"{bk}_{suf}"], EN[f"{bk}_{suf}"] = vf, ve
                            ex += f'<p class="ms-w-x"><b data-i18n="{lab}">{cle}</b> : <span data-i18n="{bk}_{suf}">{e(vf)}</span></p>'
                    if w.get("statut") == "partiel": ex += '<p class="ms-w-x ko" data-i18n="sl_w_partiel">Soluce partielle, complétée dès que deux sources concordent.</p>'
                    slg = f'{c["n"]}-' + re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", m["t"].lower())).strip("-")
                    ex += f'<p class="ms-w-x"><a href="mission/{slg}.html" data-i18n="sl_w_page">Page de la mission</a> →</p>'
                    wh = f'<details class="ms-w"><summary data-i18n="sl_w_voir">Soluce</summary><ol>{"".join(et)}</ol>{ex}</details>'
                lis_m.append(f'<li><label><input type="checkbox" data-ms="ch{c["n"]}-{k(m["t"]).lower()}"> {e(m["t"])}</label> {" ".join(tags)}{wh}</li>')
            chap_l += f'<details class="ms-chap"><summary><span class="ms-n">{c["n"]}</span><b>{nom}</b><small>{a} + {b}</small></summary><ol class="ms-liste">' + "".join(lis_m) + "</ol></details>"
        sources = " · ".join(f'<a href="{e(u)}" target="_blank" rel="noopener nofollow">{e(u.split("/")[2].replace("www.", ""))}</a>' for u in G6.get("missions_sources", []))
        chap_tab = ('<table class="sl-table"><thead><tr><th data-i18n="sl_chap">Chapitre</th><th data-i18n="sl_principales">Principales</th><th data-i18n="sl_optionnelles">Optionnelles</th></tr></thead><tbody>'
                    + "".join(rows) + f'<tr><th data-i18n="sl_total">Total</th><th>{tot[0]}</th><th>{tot[1]}</th></tr><tr><th data-i18n="sl_total_g">Total (principales + optionnelles)</th><th colspan="2">{tot[0] + tot[1]}</th></tr></tbody></table><p class="ct-etat"><span data-i18n="sl_sources_t">Sources</span> : {sources}</p>')
    # --- carte : une icône par mission détaillée, posée par le JS sur le premier lieu officiel cité (20/11/2026)
    cm = []
    for c in G6.get("chapitres", []):
        for m in c["missions"]:
            w = m.get("w") or {}
            if not w.get("fr"): continue
            slg = f'{c["n"]}-' + re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", m["t"].lower())).strip("-")
            cm.append({"id": "mis-" + slg, "couche": "missions", "ch": c["n"], "en": m["t"], "fr": m["t"], "note_en": (w.get("en") or w["fr"])[0], "note_fr": w["fr"][0], "q": " ".join(w.get("en") or []) + " " + " ".join(w["fr"]), "lien": f"mission/{slg}.html", "sources": w.get("sources", [])})
    json.dump({"couche": {"id": "missions", "fr": "Missions (soluce)", "en": "Missions (walkthrough)", "couleur": "#ffd23f", "famille": "m", "icone": "assets/img/carte/icones/missions.svg",
               "note_fr": "Chaque mission détaillée est posée sur le premier lieu officiel que cite sa soluce. Touchez-la pour ouvrir sa page.", "note_en": "Each detailed mission sits on the first official place its walkthrough names. Tap it to open its page."}, "points": cm},
              open("data/carte_missions.json", "w", encoding="utf-8"), ensure_ascii=False)
    # --- triches
    trh = ""
    if G6.get("triches"):
        cats_tr = list(dict.fromkeys(t["cat"] for t in G6["triches"]))
        # noms français des codes (le nom officiel anglais reste affiché en petit) ; noms propres (véhicules, filtres) inchangés
        TRN = {"Drunk": "Ivre", "Raise Heat Level": "Augmenter la chaleur", "Raise Wanted Level": "Augmenter le niveau de recherche", "Unlimited Focus": "Concentration illimitée", "No Fall Damage": "Pas de dégâts de chute", "Parachute": "Parachute", "Body Armor": "Gilet pare-balles", "Repair Vehicle": "Réparer le véhicule", "Unlimited Nitrous": "Nitro illimitée", "Max Ammo": "Munitions au maximum", "Infinite Ammo": "Munitions infinies", "No Reload": "Sans rechargement", "All Explosive Weapons": "Toutes les armes explosives", "Incendiary Ammo": "Munitions incendiaires", "Exploding Bottles": "Bouteilles explosives", "Explosive Shotgun": "Fusil à pompe explosif", "Attack Force": "Force d'attaque", "Exploding Balls": "Balles explosives", "Vehicle Force": "Force des véhicules", "Inflatable Flamingo": "Flamant rose gonflable", "Move Time Forward": "Avancer l'heure", "Pause Time of Day": "Figer l'heure", "Cycle Weather": "Changer la météo", "Golden Hour": "Heure dorée", "Powdered Sugar": "Sucre glace", "Neon Jungle": "Jungle néon", "Yesteryear": "Autrefois", "Videotape": "Cassette vidéo", "Dark Mirror": "Miroir sombre", "Dollhouse": "Maison de poupée", "Fast Forward": "Avance rapide", "Fisheye": "Fish-eye", "Faded Glory": "Gloire fanée", "Pixel Art": "Pixel art", "Hellscape": "Paysage infernal", "$250,000": "250 000 $", "Interstate Ambulance": "Ambulance Interstate"}
        ICT = {"Player": "player", "Combat": "combat", "Spawn Vehicle": "spawn", "Screen Filter": "filter", "Environment": "environment"}
        def ic(nom): return f'<img class="sl-ic" src="assets/img/soluce/ic/{nom}.svg" alt="" width="28" height="28" loading="lazy">' if os.path.exists(f"assets/img/soluce/ic/{nom}.svg") else ""
        FL = {"UP": ("u", "▲"), "DOWN": ("d", "▼"), "LEFT": ("l", "◀"), "RIGHT": ("r", "▶")}
        trh += ('<div class="tr-mode"><h2 data-i18n="sl_tr_mode">Comment entrer un code</h2>'
                '<div class="tr-plat" role="group"><button type="button" data-plat="ps" aria-pressed="true">PS5</button><button type="button" data-plat="xb" aria-pressed="false">Xbox Series</button></div>'
                '<ol class="tr-etapes"><li><span data-i18n="sl_tr_e1">Sortez le téléphone</span> <kbd class="pad pad-u" aria-label="↑">▲</kbd></li>'
                '<li><span data-i18n="sl_tr_e2">Maintenez</span> <kbd class="bt" data-ps="L1" data-xb="LB">L1</kbd> <span data-i18n="sl_tr_e2b">puis appuyez sur</span> <kbd class="bt" data-ps="R1" data-xb="RB">R1</kbd></li>'
                '<li><span data-i18n="sl_tr_e3">Entrez la combinaison à la croix directionnelle</span> <kbd class="pad pad-u">▲</kbd><kbd class="pad pad-r">▶</kbd><kbd class="pad pad-d">▼</kbd><kbd class="pad pad-l">◀</kbd></li></ol>'
                '<p class="tr-note" data-i18n="sl_tr_e4">Combinaisons identiques sur PS5 et Xbox. Un code actif désactive trophées, succès et sauvegarde.</p></div>')
        trh += ('<div class="sl-outils"><input type="search" id="tr-q" data-i18n-ph="sl_tr_rech" placeholder="Rechercher un code (véhicule, arme, argent…)" autocomplete="off">'
                '<div class="sl-chips" id="tr-f"><button type="button" data-trf="" aria-pressed="true" data-i18n="sl_tous">Tous</button>'
                + "".join(f'<button type="button" data-trf="{k(ct).lower()}" aria-pressed="false" data-i18n="sl_cat_tr_{ct}">{tx(UI.get("sl_cat_tr_" + ct, (ct,))[0])}</button>' for ct in cats_tr)
                + '<button type="button" data-trc="1" aria-pressed="false" data-i18n="sl_conf_seul">Confirmés seulement</button></div><p class="sl-nb" id="tr-nb"></p></div>')
        for ct in cats_tr:
            lst = [t for t in G6["triches"] if t["cat"] == ct]
            trh += f'<section class="tr-cat" data-cat="{k(ct).lower()}"><h2 id="tr-{k(ct).lower()}">{ic("tr-" + ICT.get(ct, "player"))}<span data-i18n="sl_cat_tr_{ct}">{tx(UI.get("sl_cat_tr_" + ct, (ct,))[0])}</span> <small>{len(lst)}</small></h2><div class="tr-grille">'
            for t in lst:
                ke, kd = "tre_" + k(t["id"]), "trd_" + k(t["id"])
                FR[ke], EN[ke] = t["fr"][:1].upper() + t["fr"][1:], t["en"][:1].upper() + t["en"][1:]
                FR[kd], EN[kd] = t["deblocage_fr"], t["deblocage_en"]
                ok = t["code"] and t["code_statut"] == "confirme"
                badge = '<span class="sl-badge ok" data-i18n="sl_conf">Confirmé</span>' if ok else '<span class="sl-badge ko" data-i18n="sl_aconf">À confirmer</span>'
                if t["code"]:
                    fl = [FL.get(x.strip(), ("", x.strip())) for x in t["code"].split(">")]
                    seq = "".join(f'<kbd class="pad pad-{c}">{g}</kbd>' for c, g in fl)
                    code = f'<div class="tr-seq" data-code="{" ".join(g for _, g in fl)}">{seq}</div><button type="button" class="tr-copie" data-i18n="sl_copier">Copier</button>'
                else:
                    code = '<p class="tr-inc" data-i18n="sl_tr_inc">pas encore connue</p>'
                kn = "trn_" + k(t["id"]); FR[kn], EN[kn] = TRN.get(t["nom"], t["nom"]), t["nom"]
                if t["nom"] not in TRN or t["nom"] == "Parachute":  # nom propre : identique dans toutes les langues
                    for l in autres: autres[l][kn] = t["nom"]
                trh += (f'<article class="tr-carte" data-st="{"ok" if ok else "ko"}"><header><div><h3 data-i18n="{kn}">{e(FR[kn])}</h3><small class="tr-off" lang="en">{e(t["nom"])}</small></div>{badge}</header><p class="tr-eff" data-i18n="{ke}">{tx(FR[ke])}</p>'
                        f'<div class="tr-code">{code}</div><p class="tr-deb"><b data-i18n="sl_tr_deb">Déblocage</b> : <span data-i18n="{kd}">{tx(t["deblocage_fr"])}</span></p></article>')
            trh += "</div></section>"
        trh += '<p class="ct-etat"><span data-i18n="sl_sources_t">Sources</span> : ' + " · ".join(f'<a href="{e(u)}" target="_blank" rel="noopener nofollow">{e(u.split("/")[2].replace("www.", ""))}</a>' for u in G6.get("triches_sources", [])) + "</p>"
    # --- articles soluce (titres dans les 17 langues depuis data/articles.json)
    ARTS = {a["id"]: a for a in json.load(open("data/articles.json", encoding="utf-8"))}
    arts = []
    for i, aid in enumerate(G6.get("hub_articles", [])):
        a = ARTS.get(aid)
        if not a: continue
        ka = f"sa_{i}"
        FR[ka] = a["fr"]["t"]; EN[ka] = (a.get("en") or a["fr"])["t"]
        for l in autres:
            x = a.get(ART_L.get(l, l))
            if x and x.get("t"): autres[l][ka] = x["t"]
        arts.append(f'<li><a href="journal/{aid}.html" data-i18n="{ka}">{tx(a["fr"]["t"])}</a></li>')
    # --- codes des coffres (21/11/2026, data/soluce/coffres.json)
    cfh = ""
    CF = json.load(open("data/soluce/coffres.json", encoding="utf-8"))
    cfh += '<h2 data-i18n="cf_q">' + tx(UI["cf_q"][0]) + '</h2><p data-i18n="cf_a">' + tx(UI["cf_a"][0]) + '</p><p class="cf-zero" data-i18n="cf_zero">' + tx(UI["cf_zero"][0]) + "</p>"
    cfh += '<div class="sl-outils"><input type="search" id="cf-q" data-i18n-ph="cf_rech" placeholder="' + e(UI["cf_rech"][0]) + '" autocomplete="off"></div>'
    for g in CF["groupes"]:
        kg = "cf_g_" + g["id"]; FR[kg], EN[kg] = g["fr"], g["en"]
        lst = [(i, c) for i, c in enumerate(CF["codes"]) if c["g"] == g["id"]]
        cfh += f'<section class="cf-gr"><h2 data-i18n="{kg}">{tx(g["fr"])}</h2><div class="cf-grille">'
        for i, c in lst:
            kn = f"cf_n_{i}"; FR[kn], EN[kn] = c["fr"], c["en"]
            cfh += (f'<article class="cf-carte" data-q="{e((c["lieu"] + " " + c["qui"] + " " + c["zone"] + " " + c["code"]).lower())}"><header><div><h3>{e(c["lieu"])}</h3>'
                    + (f'<small>{e(c["qui"])}</small>' if c["qui"] else "") + f'</div><b class="cf-code">{e(c["code"])}</b></header>'
                    + f'<p class="cf-lieu">📍 {e(c["zone"])} · <span data-i18n="cf_ch">{tx(UI["cf_ch"][0])}</span> {c["ch"]}</p><p data-i18n="{kn}">{tx(c["fr"])}</p></article>')
        cfh += "</div></section>"
    cfh += '<p class="ct-etat"><span data-i18n="cf_maj">' + tx(UI["cf_maj"][0]) + "</span> " + CF["maj"] + ' · <span data-i18n="sl_sources_t">Sources</span> : ' + " · ".join(f'<a href="{e(u)}" target="_blank" rel="noopener nofollow">{e(u.split("/")[2].replace("www.", ""))}</a>' for u in CF["sources"]) + "</p>"
    # --- pages
    P = {}
    for p in ["guide", "carte", "trophees", "collectibles", "missions", "triches", "coffres"]: P[p] = open(p + ".html", encoding="utf-8").read()
    if chap_tab: P["missions"] = sub(sub(P["missions"], "chap", chap_tab), "chapl", chap_l)
    if trh: P["triches"] = sub(P["triches"], "triches", trh)
    P["coffres"] = sub(P["coffres"], "coffres", cfh)
    P["trophees"] = sub(sub(P["trophees"], "liste", '<ul class="tp-liste">' + "".join(lis) + "</ul>"), "filtres", filtres)
    P["carte"] = sub(P["carte"], "table", table)
    P["collectibles"] = sub(sub(P["collectibles"], "table", table), "blocs", "".join(blocs))
    P["missions"] = sub(sub(P["missions"], "side", '<div class="ms-grille">' + "".join(side) + "</div>"), "hist", '<div class="ms-grille">' + "".join(hist) + "</div>")
    P["guide"] = sub(P["guide"], "articles", '<ul class="sl-liste">' + "".join(arts) + "</ul>")
    for p, s in P.items(): ecrit(p + ".html", s)
    # --- i18n
    for l, vals in [("fr", FR), ("en", EN)] + list(autres.items()):
        f = f"tools/i18n/{l}.json"
        d = json.load(open(f, encoding="utf-8")); avant = json.dumps(d, ensure_ascii=False, sort_keys=True)
        if l == "en":
            # textes anglais modifiés : effacer l'ancienne traduction dans les autres langues pour qu'elle soit refaite
            for kk, v in vals.items():
                if d.get(kk) != v:
                    for o in autres:
                        if kk not in autres[o]: P2 = f"tools/i18n/{o}.json"; dd = json.load(open(P2, encoding="utf-8"))
                        else: continue
                        if kk in dd: dd.pop(kk); json.dump(dd, open(P2, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        d.update(vals)
        if json.dumps(d, ensure_ascii=False, sort_keys=True) != avant:
            json.dump(d, open(f, "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("soluce : i18n", l, len(vals))

if __name__ == "__main__":
    main()
