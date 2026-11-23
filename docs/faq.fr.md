# FAQ

## Flash-Excel modifie-t-il mon fichier source ? {#does-flash-excel-change-my-source-file}

Non. Chaque exécution écrit un nouveau fichier de sortie, par défaut `Documents\flash-excel\output\<nom>_clean.<extension>`, et laisse la source telle quelle. Seule exception : un modèle de nom `{name}` avec le dossier et le format de la source : la sortie remplace alors la source. Consultez [Formats de fichier](reference/file-formats.md#name-and-location).

## Flash-Excel fonctionne-t-il sous macOS ou Linux ? {#does-flash-excel-run-on-macos-or-linux}

Non. Flash-Excel est une application Windows : son installateur, ses paramètres et sa planification reposent tous sur Windows.

## Ai-je besoin de droits administrateur ? {#do-i-need-administrator-rights}

Non. Flash-Excel s'installe pour votre seul utilisateur Windows, et les mises à jour s'installent de la même façon. Consultez la [prise en main](get-started.md).

## Mes fichiers sont-ils envoyés quelque part ? {#are-my-files-sent-anywhere}

Non. Les fichiers sont lus, transformés et écrits sur votre PC. Le seul accès réseau est la recherche d'une nouvelle version au démarrage de Flash-Excel, et le téléchargement d'une mise à jour quand vous la sélectionnez. Consultez [Mises à jour automatiques](concepts/automatic-updates.md).

## Quels fichiers Flash-Excel sait-il lire et écrire ? {#which-files-can-flash-excel-read-and-write}

Il lit les fichiers `.xlsx`, `.xlsm`, `.xls` et `.csv`, et écrit des fichiers `.xlsx`, `.csv` et `.parquet`. Consultez [Formats de fichier](reference/file-formats.md).

## Puis-je traiter une autre feuille que la première ? {#can-i-process-another-sheet-than-the-first-one}

Non. Flash-Excel ne lit que la première feuille d'un classeur. Placez la feuille voulue en première position dans Excel, enregistrez et relancez.

## Puis-je traiter plusieurs fichiers à la fois ? {#can-i-process-several-files-at-once}

Oui. Sélectionnez ou déposez plusieurs fichiers sur la page **Traitement** : ils sont traités l'un après l'autre avec le même préréglage, chacun vers son propre fichier de sortie. Consultez [Lancer un préréglage](tasks/run/run-a-preset.md).

## Y a-t-il une taille limite pour les fichiers ? {#is-there-a-size-limit-for-files}

Il n'y a pas de limite fixe. Chaque fichier est lu entièrement en mémoire : les très gros fichiers demandent donc assez de mémoire libre sur votre PC.

## Puis-je essayer un préréglage sans écrire de fichier ? {#can-i-try-a-preset-without-writing-a-file}

Oui. **Aperçu** sur la page **Traitement** affiche le résultat sur les 100 premières lignes, sans rien écrire. Consultez [Prévisualiser une transformation](tasks/run/preview-a-transformation.md).

## Puis-je changer l'ordre des étapes ? {#can-i-change-the-order-of-the-steps}

Pas dans l'éditeur : il exécute les étapes configurées dans un ordre fixe, conçu pour que chaque étape trouve les colonnes dont elle a besoin. Un fichier de préréglage écrit à la main exécute ses étapes dans l'ordre du fichier. Consultez [Étapes et ordre](concepts/steps-and-order.md).

## Pourquoi les fonctions des colonnes calculées sont-elles en français ? {#why-are-the-computed-column-functions-in-french}

Elles reprennent les noms de fonctions de la version française d'Excel (`SI`, `CONCATENER`, `ARRONDI`…). Elles restent les mêmes dans toutes les langues de l'interface, pour que les préréglages fonctionnent pour tout le monde. Consultez [Fonctions des colonnes calculées](reference/computed-functions.md).

## Comment partager des préréglages avec des collègues ? {#how-do-i-share-presets-with-colleagues}

Envoyez le fichier de préréglage avec **Exporter**, ou placez les préréglages dans un dossier partagé que chacun ajoute sous **Paramètres** › **Sources de préréglages en lecture seule**. Consultez [Exporter un préréglage](tasks/presets/export-a-preset.md) et [Utiliser des dossiers de préréglages partagés](tasks/presets/use-shared-preset-folders.md).

## Puis-je versionner mes préréglages ? {#can-i-keep-presets-under-version-control}

Oui. Un préréglage est un fichier texte `.toml` : il peut être stocké dans Git ou dans n'importe quel dossier versionné et comparé ligne à ligne. Consultez [Fichier de préréglage](reference/preset-file.md).

## Un préréglage peut-il s'exécuter automatiquement chaque jour ? {#can-a-preset-run-automatically-every-day}

Oui. **Configurer une exécution** sur la page **Traitement** crée une tâche planifiée Windows, ou un lanceur `.cmd` à ouvrir d'un double-clic. Flash-Excel n'a pas besoin d'être ouvert, mais votre session Windows, si. Consultez [Planifier un préréglage](tasks/automate/schedule-a-preset.md).

## Pourquoi Flash-Excel ne gère-t-il pas lui-même la planification ? {#why-doesnt-flash-excel-run-the-schedule-itself}

Le Planificateur de tâches Windows le fait mieux : une tâche survit à un redémarrage, s'exécute sans que Flash-Excel soit ouvert et enregistre le résultat de chaque exécution. **Configurer une exécution** crée cette tâche pour vous. Consultez [Planifier un préréglage](tasks/automate/schedule-a-preset.md).

## Puis-je lancer un préréglage depuis un script ? {#can-i-run-a-preset-from-a-script}

Oui, avec `Flash-Excel.exe --preset … --input …`. Consultez [Ligne de commande](reference/command-line.md).

## Que deviennent mes préréglages quand je mets à jour ou désinstalle ? {#what-happens-to-my-presets-when-i-update-or-uninstall}

Ils restent. Préréglages, paramètres, sorties et journaux sont stockés hors du dossier d'installation, seule chose que les mises à jour remplacent et que la désinstallation retire. Consultez [Emplacements des données](reference/data-locations.md#uninstalling).

## Quelle version est-ce que j'utilise ? {#which-version-am-i-running}

Le numéro de version est affiché dans le coin inférieur droit de la fenêtre, par exemple `v1.5.0`. Consultez les [notes de version](release-notes.md) pour ce qui a changé.

## Comment passer l'interface en anglais ? {#how-do-i-switch-the-interface-to-french}

Sélectionnez **Paramètres** dans la barre latérale, puis **Anglais** sous **Langue**. Consultez [Changer la langue](tasks/settings/change-the-language.md).

## Flash-Excel est-il gratuit ? {#is-flash-excel-free}

Oui. Flash-Excel est open source, sous licence MIT. Son code source est sur [GitHub](https://github.com/neuraaak/Flash-Excel).
