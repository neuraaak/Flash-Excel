# Notes de version

Ce qui a changé pour vous dans chaque version de Flash-Excel, de la plus récente à la plus ancienne. Les installateurs de chaque version sont sur la [page des versions GitHub](https://github.com/neuraaak/Flash-Excel/releases). Pour installer la dernière, consultez [Mettre à jour Flash-Excel](tasks/update/update-flash-excel.md).

## 1.5.1 {#151}

### Nouveautés

- Le lien **Documentation** du pied de page ouvre cette documentation, en français quand l'interface est en français.
- La documentation est disponible en anglais et en français. Utilisez le sélecteur de langue en haut de chaque page.

## 1.5.0 — 2026-10-18 {#150-2026-10-18}

### Nouveautés

- Le pied de page affiche un lien **Dépôt** vers le projet Flash-Excel sur GitHub.
- Le panneau d'exécution de la page **Traitement** peut être redimensionné, et garde sa largeur à la prochaine ouverture de Flash-Excel.

### Améliorations

- Nouvelle icône d'application et nouvelles icônes pour les fichiers Excel et CSV.

### Corrections

- Les préférences de la fenêtre sont désormais conservées d'une session à l'autre au lieu d'être réinitialisées à chaque démarrage.

## 1.4.0 — 2026-10-18 {#140-2026-10-18}

!!! warning "Préréglages enregistrés avant 1.4.0 et fichiers CSV"
    Les séparateurs CSV sont désormais détectés automatiquement, mais les préréglages enregistrés par les versions précédentes contiennent `csv_separator = ";"`, qui continue d'imposer le point-virgule. Si un tel préréglage lit un fichier séparé par des virgules en une seule colonne, supprimez cette ligne du fichier de préréglage. Consultez [Dépannage](troubleshooting.md#csv-source-single-column).

### Nouveautés

- Traitement de plusieurs fichiers en une exécution. Sélectionnez ou déposez plusieurs fichiers sur la page **Traitement** ; chaque fichier a son propre statut dans la file, et **En cas d'erreur** › **Tout arrêter** arrête toute l'exécution.
- Dépôt de fichiers sur la fenêtre, sur les pages **Traitement** et **Préréglages**.
- **Aperçu** montre le résultat d'un préréglage sur les 100 premières lignes sans rien écrire. Consultez [Prévisualiser une transformation](tasks/run/preview-a-transformation.md).
- **Configurer une exécution** crée une tâche planifiée Windows quotidienne ou un lanceur `.cmd` pour un préréglage et ses fichiers. Consultez [Planifier un préréglage](tasks/automate/schedule-a-preset.md).
- Mode ligne de commande : `Flash-Excel.exe --preset … --input …` lance un préréglage sans ouvrir la fenêtre. Consultez [Ligne de commande](reference/command-line.md).
- **Sources de préréglages en lecture seule** dans **Paramètres** : listez les préréglages de dossiers partagés à côté des vôtres. Consultez [Utiliser des dossiers de préréglages partagés](tasks/presets/use-shared-preset-folders.md).
- **Sortie CSV** dans **Paramètres** : choisissez le séparateur et le séparateur décimal des CSV produits. **Auto** suit vos paramètres régionaux Windows, pour que les fichiers produits s'ouvrent en colonnes dans Excel.
- Nouvelle option de préréglage `csv_decimal_comma` pour lire `1,5` comme un nombre dans les fichiers sources CSV.

### Améliorations

- Le séparateur des fichiers sources CSV est détecté automatiquement au lieu d'être toujours `;`.
- Les types de colonnes des fichiers CSV sont déduits de toutes les lignes : une colonne qui devient du texte plus bas ne fait plus échouer tout le chargement.
- Charger un gros modèle Excel ne fige plus la fenêtre.
- Un préréglage endommagé reste dans la liste, marqué **illisible**, au lieu de disparaître.
- **Enregistrer** vous signale les étapes refusées et absentes du fichier.
- Les fichiers de sortie vont par défaut dans `Documents\flash-excel\output`, et le champ **Dossier de destination** affiche ce chemin complet.
- **Filtrer les lignes** avec **contient** compare le texte exactement tel qu'il est saisi : `C++` ne correspond plus à `C+ dev`.
- Une valeur non numérique dans un filtre sur une colonne numérique donne un message clair.
- Les cartes de palette dans **Paramètres** prévisualisent le mode sélectionné.

### Corrections

- Les préréglages utilisant **Valeur au-dessus** ou **Valeur en dessous** dans **Remplir les cellules vides** ne pouvaient pas être relus après l'enregistrement et disparaissaient de la liste.
- Le nom du fichier modèle était perdu à chaque enregistrement d'un préréglage.
- Renommer un préréglage pouvait le perdre si l'enregistrement échouait, et deux noms ne différant que par la ponctuation s'écrasaient l'un l'autre.
- Sans destination choisie, les fichiers de sortie étaient écrits dans le dossier d'installation et perdus à la mise à jour suivante.
- Une exécution sur un fichier verrouillé par Excel avec **En cas d'erreur** › **Ignorer** ne se terminait jamais.
- `DROITE(colonne, 0)` retournait tout le texte au lieu d'un texte vide.

## 1.3.2 {#132}

Version de maintenance sans changement visible. Elle n'a pas été distribuée par les mises à jour automatiques.

## 1.3.1 — 2026-10-09 {#131-2026-10-09}

### Nouveautés

- Éditeurs pour **Supprimer des colonnes** et **Remplir les cellules vides** sur la page **Préréglages**.

### Améliorations

- Les descriptions et exemples des fonctions de colonnes calculées, ainsi que les messages de la page **Préréglages**, sont traduits en français.

## 1.3.0 — 2026-09-30 {#130-2026-09-30}

!!! warning "Paramètres réinitialisés au passage à 1.3.0"
    Les paramètres ont changé d'emplacement et n'ont pas été repris : palette, mode et langue reviennent une fois à leurs valeurs par défaut. Les préréglages sont repris automatiquement.

### Nouveautés

- Un fichier journal de l'application enregistre les démarrages, exécutions et erreurs, dans `%LOCALAPPDATA%\flash-excel\logs`. Démarrez avec `--debug` pour plus de détails.
- Flash-Excel démarre dans la langue choisie dans l'installateur.

### Améliorations

- Vos données se trouvent désormais hors du dossier d'installation, donc les mises à jour et la désinstallation n'y touchent plus : les préréglages dans `Documents\flash-excel\presets` (redirection OneDrive comprise), les paramètres dans `%APPDATA%\flash-excel`. Les préréglages des versions précédentes y sont copiés au premier démarrage. Consultez [Emplacements des données](reference/data-locations.md).
- Si les paramètres nomment une palette qui n'existe pas, Flash-Excel utilise la palette par défaut au lieu de n'afficher aucune couleur.

### Corrections

- La mise à jour automatique vers 1.2.3 pouvait échouer ; elle s'installe désormais correctement.

## 1.2.3 — 2026-07-16 {#123-2026-07-16}

### Nouveautés

- Réordonnancement des colonnes par glisser-déposer dans **Réordonner les colonnes**.
- L'éditeur de colonnes calculées a un bouton de modification pour chaque colonne et des pastilles pour insérer des séparateurs (`_`, `-`, `/`, `.`, espace).

### Améliorations

- Renommer une colonne, ou une colonne calculée, met à jour les étapes qui la suivent.
- La **Console** et le résumé du préréglage affichent les noms d'étapes comme dans l'éditeur, par exemple **Renommer les colonnes** au lieu de `rename_columns`.
- Les messages de la **Console** sont traduits.
- Les valeurs vrai/faux des fichiers Excel produits suivent la langue de l'interface : `True`/`False` en anglais, `VRAI`/`FAUX` en français.
- Tous les textes des éditeurs d'étapes sont traduits.

### Corrections

- L'application installée pouvait échouer à lire les fichiers `.xlsx`.

## 1.2.2 — 2026-07-13 {#122-2026-07-13}

### Nouveautés

- Les colonnes calculées peuvent utiliser des colonnes dont le nom contient des espaces ou des symboles, écrites `[Nom de colonne]`. L'éditeur ajoute les crochets pour vous.
- La **Console** a un filtre **Step**.

### Corrections

- Les messages d'étapes de la **Console** étaient tronqués.

## 1.2.1 — 2026-07-12 {#121-2026-07-12}

### Corrections

- Le menu de navigation et le pied de page n'étaient pas traduits.
- La liste des préréglages de la page **Traitement** n'affichait pas les préréglages créés ou supprimés depuis le démarrage.
- L'icône **Paramètres** du menu affichait un soleil au lieu d'un engrenage.

## 1.2.0 — 2026-07-04 {#120-2026-07-04}

### Nouveautés

- Quand une nouvelle version est disponible, un lien **Mettre à jour vers v*X.Y.Z*** apparaît dans le pied de page et l'installe en un clic. Les mises à jour sont signées et vérifiées avant l'installation. Consultez [Mises à jour automatiques](concepts/automatic-updates.md).
- Le numéro de la version actuelle est affiché dans le pied de page.

## 1.1.0 — 2026-06-02 {#110-2026-06-02}

### Nouveautés

- Installateur Windows qui installe Flash-Excel pour l'utilisateur courant, sans droits administrateur.
- Première version des mises à jour automatiques.
- Icône d'application.

## 1.0.0 — 2026-06-01 {#100-2026-06-01}

### Nouveautés

- Nouvelle interface avec une page **Traitement** pour lancer les préréglages et une page **Préréglages** pour les construire, avec un éditeur pour chaque type d'étape.
- Palettes de couleurs et paramètres de l'interface.
