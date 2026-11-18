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
 "md_missions": ("Liste des missions de GTA 6 : missions secondaires d'Andy, Kenton, Billy, Randy, Tyrone, Bret et Cal, Strangers & Freaks, et missions d'histoire masquées (spoilers).",
                 "GTA 6 mission list: side missions for Andy, Kenton, Billy, Randy, Tyrone, Bret and Cal, Strangers & Freaks, and hidden story missions (spoilers)."),
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
 "sl_avert_carte": ("Fond de carte : schéma indicatif dessiné par GTAVIFRANCE, pas à l'échelle, en attendant la carte officielle de Rockstar. Un point n'apparaît que vérifié (2 sources concordantes ou source officielle).",
                    "Map background: indicative diagram drawn by GTAVIFRANCE, not to scale, until Rockstar publishes the official map. A point only appears once verified (two matching sources or an official source)."),
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
 "sl_cl_i": ("Le nombre de chaque collectible vient de la liste officielle des trophées. Les emplacements s'ajoutent au fil des vérifications ; cochez ce que vous avez trouvé.",
             "Each collectible count comes from the official trophy list. Locations are added as they are verified; tick what you have found."),
 "sl_ms_side": ("Missions secondaires : les personnages", "Side missions: the characters"),
 "sl_ms_side_p": ("Sept personnages ont un trophée lié à leurs missions. Terminer leur dernière mission débloque le trophée.", "Seven characters have a trophy tied to their missions. Finishing their last mission unlocks it."),
 "sl_ms_sf": ("Strangers & Freaks : 8 séries", "Strangers & Freaks: 8 strands"),
 "sl_ms_sf_p": ("Il faut terminer 8 séries de missions d'inconnus dans tout Leonida (trophée argent « Strangers & Freaks »). La liste détaillée arrive dès qu'elle est vérifiée.",
                "Finish 8 strands of stranger missions across Leonida (silver trophy \"Strangers & Freaks\"). The detailed list comes as soon as it is verified."),
 "sl_ms_hist": ("Missions d'histoire (spoilers)", "Story missions (spoilers)"),
 "sl_ms_hist_p": ("L'histoire compte au moins 4 chapitres et une mission finale. Les noms ci-dessous viennent de la liste officielle des trophées.",
                  "The story has at least 4 chapters and a final mission. The names below come from the official trophy list."),
 "sl_ms_voir": ("Afficher les missions d'histoire", "Show story missions"),
 "sl_ms_q": ("Combien de missions dans GTA 6 ?", "How many missions are in GTA 6?"),
 "sl_ms_a": ("Rockstar n'a pas publié le nombre total de missions. Les trophées confirment au moins 4 chapitres, une mission finale, 7 personnages secondaires et 8 séries Strangers & Freaks ; les missions restent jouables en monde libre après l'histoire.",
             "Rockstar has not published the total number of missions. Trophies confirm at least 4 chapters, a final mission, 7 side characters and 8 Strangers & Freaks strands; optional missions stay available in free roam after the story."),
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
    for key, (f, en) in UI.items(): FR[key], EN[key] = f, en
    # --- trophées
    cats = ["collectibles", "activites", "braquages", "personnages", "secrets", "completion", "divers", "histoire"]
    lis = []
    for t in TP["trophees"]:
        kd = "tpd_" + k(t["id"]); FR[kd], EN[kd] = t["fr"], t["en"]
        cpt = ""
        if t.get("max"):
            cpt = f'<div class="cpt"><button type="button" class="moins" aria-label="-1">−</button><input type="number" min="0" max="{t["max"]}" value="0" inputmode="numeric" aria-label="{e(t["nom"])}"><span>/ {t["max"]}</span><button type="button" class="plus" aria-label="+1">+</button></div>'
        lien = f'<div class="lien"><a href="carte.html#c={t["couche"]}" data-i18n="sl_sur_carte">Sur la carte</a></div>' if t.get("couche") else ""
        lis.append(f'<li class="tp{" spoil" if t["spoiler"] else ""}" data-id="{t["id"]}" data-cat="{t["cat"]}" data-grade="{t["grade"]}"{" data-max=%s" % t["max"] if t.get("max") else ""}{" hidden" if t["spoiler"] else ""}>'
                   f'<input type="checkbox" aria-label="{e(t["nom"])}"><h3>{e(t["nom"])}<span class="gr gr-{t["grade"]}">{t["grade"]}</span></h3><p data-i18n="{kd}">{tx(t["fr"])}</p>{cpt}{lien}</li>')
    filtres = '<button type="button" data-filtre="tout" aria-pressed="true" data-i18n="sl_tous">Tous</button>' + "".join(
        f'<button type="button" data-filtre="{c}" aria-pressed="false" data-i18n="sl_cat_{c}">{UI["sl_cat_" + c][0]}</button>' for c in cats if c != "histoire")
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
        blocs.append(f'<div class="cl-bloc" id="{c["id"]}"><h2><span class="ct-pt" style="background:{c["couleur"]}"></span> <span data-i18n="{kc}">{tx(c["fr"])}</span> <small id="cln-{c["id"]}">0/{c["total"] or "?"}</small></h2>'
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
    # --- articles soluce (titres dans les 17 langues depuis data/articles.json)
    ARTS = {a["id"]: a for a in json.load(open("data/articles.json", encoding="utf-8"))}
    autres = {l: {} for l in LANGS if l not in ("fr", "en")}
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
    # --- pages
    P = {}
    for p in ["guide", "carte", "trophees", "collectibles", "missions"]: P[p] = open(p + ".html", encoding="utf-8").read()
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
