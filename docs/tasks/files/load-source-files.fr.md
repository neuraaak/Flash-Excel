# Charger des fichiers sources

Chargez les fichiers Excel ou CSV à transformer sur la page **Traitement**. Vous pouvez charger un seul fichier ou tout un lot, qu'un préréglage traite l'un après l'autre.

## 🔧 Prérequis

- Des fichiers dans un format pris en charge : `.xlsx`, `.xls`, `.xlsm` ou `.csv`. Consultez [Formats de fichier](../../reference/file-formats.md).
- Pour un lot, des fichiers ayant les mêmes colonnes : les listes des étapes sont construites à partir du premier fichier seulement.

## 📝 Étapes

=== "Choisir les fichiers"

    1. Dans la barre latérale, sélectionnez **Traitement**.
    2. Cliquez sur la zone de dépôt **Déposez vos fichiers Excel/CSV ici — ou cliquez pour parcourir**.
    3. Dans la boîte de dialogue, sélectionnez un fichier, ou plusieurs avec ++ctrl++ ou ++shift++, puis validez.

=== "Glisser-déposer"

    1. Dans la barre latérale, sélectionnez **Traitement**.
    2. Faites glisser un ou plusieurs fichiers depuis l'Explorateur Windows et déposez-les sur la fenêtre.

    Les fichiers que Flash-Excel ne sait pas lire sont écartés de la liste.

Pour remplacer la liste, sélectionnez **Charger un fichier** au-dessus de la liste et choisissez d'autres fichiers : la nouvelle sélection remplace la précédente. Pour vider la liste, sélectionnez **Effacer**. Ces deux boutons sont indisponibles pendant une exécution.

## ✅ Résultat

Sous **Fichier source**, chaque fichier apparaît sur une ligne avec son nom, sa taille et le statut **En attente**. L'en-tête indique le nombre de fichiers, par exemple **3 fichier(s)**, et la première ligne indique aussi son nombre de colonnes.

!!! note "Comment Flash-Excel lit les fichiers"
    Seule la première feuille d'un classeur Excel est lue. Pour un fichier CSV, le séparateur de colonnes est détecté automatiquement, sauf si le fichier de préréglage en impose un (consultez [Fichier de préréglage](../../reference/preset-file.md)).

## ➡️ Étapes suivantes

- [Prévisualiser une transformation](../run/preview-a-transformation.md)
- [Lancer un préréglage](../run/run-a-preset.md)
- Si un fichier est refusé, consultez [Format de fichier non pris en charge](../../troubleshooting.md#unsupported-file-format) ; si un CSV se charge en une seule colonne, consultez [Une source CSV se charge en une seule colonne](../../troubleshooting.md#csv-source-single-column).
