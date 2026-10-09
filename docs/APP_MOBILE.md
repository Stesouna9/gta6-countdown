# App iOS et Android « VI Countdown / GTA Soluce »

Plan du 9 octobre 2026. Objectif : la même chose que le site, installable depuis l'App Store et Google Play, avec notifications et mode hors ligne, puis les soluces (bible dans `docs/BIBLE_SOLUCE_GTA.md`).

## Étape 0 : déjà en place
- gtavifrance.com est une PWA (`manifest.webmanifest`, `sw.js`) : ajout à l'écran d'accueil iPhone et Android possible aujourd'hui. Limite : pas de fiche store, notifications iOS limitées.

## Étape 1 : coquilles natives légères (2 à 3 jours)
- **iOS** : projet Swift/SwiftUI `gtasoluce-ios` sur le modèle de `vicebayradio-app` (Xcode Cloud, environnement Xcode 27, jamais de second Xcode). WKWebView plein écran sur gtavifrance.com avec cache hors ligne, barre d'onglets native (Accueil, Actus, Soluce, Radio, Codes), push via APNs (Supabase Edge comme Vice Break), écran de lancement Lucia et Jason, widget compte à rebours (WidgetKit) en réutilisant `api/gta6.json`.
- **Android** : projet Kotlin `gtasoluce-android` sur le modèle de `vicebreak-android` : Trusted Web Activity (Digital Asset Links sur gtavifrance.com/.well-known/assetlinks.json) + widget compte à rebours + Firebase Cloud Messaging.
- Même bundle/package `com.okalamstudio.gtasoluce`, icône VI dégradé sunset, nom store « VI Countdown : GTA 6 et soluces GTA ».

## Étape 2 : contenu natif (après sortie GTA VI)
- Soluces embarquées : `data/soluce/*.json` copiés dans l'app à chaque build, mis à jour par téléchargement delta.
- Carte interactive (MapKit / Google Maps custom tiles ou simple image zoomable) avec calques collectibles.
- Progression 100 % stockée en local (CoreData / Room), export iCloud / Google Drive optionnel.
- Radio Vice Bay en lecture de fond (AVAudioSession, MediaSession).

## Monétisation
- AdMob (même éditeur ca-pub-8121423865459620, `app-ads.txt` déjà présent sur okalamstudio), bannière basse uniquement, jamais d'interstitiel pendant une mission.
- Achat unique « Sans pub + carte hors ligne » 2,99 €.

## Stores
- App Store : catégorie Référence, 4+ avec avertissement contenu, captures 6,9" et 6,5", texte 17 langues généré depuis `tools/i18n`.
- Google Play : même fiche, Data safety « aucune donnée collectée ».
- Mention obligatoire : application non officielle, non affiliée à Rockstar Games ou Take-Two.

## Ordre de travail proposé
1. Créer les deux dépôts GitHub (Stesouna9/gtasoluce-ios, gtasoluce-android) avec coquilles WebView/TWA et widget.
2. Fiches stores et captures.
3. Soumission avant le 12 novembre (préchargement) pour être en ligne le 19.
4. Soluces GTA VI en continu dès le 19 novembre.
