# Glossaire

Aperçu
:   Le résultat d'un préréglage sur les 100 premières lignes d'un fichier, affiché sans rien écrire. Consultez [Prévisualiser une transformation](../tasks/run/preview-a-transformation.md).

Colonne calculée
:   Une colonne créée par l'étape **Ajouter une colonne calculée** à partir d'une expression. Consultez [Fonctions des colonnes calculées](computed-functions.md).

Console
:   Le panneau en bas de la page **Traitement** qui affiche les messages d'une exécution : fichiers chargés, étapes appliquées, avertissements et erreurs.

Dossier de destination
:   Le dossier où une exécution écrit ses fichiers de sortie. Par défaut : `Documents\flash-excel\output`.

Étape
:   Une transformation d'un préréglage, comme **Renommer les colonnes** ou **Trier les lignes**. Flash-Excel propose 12 types d'étapes. Consultez [Étapes et ordre](../concepts/steps-and-order.md).

Exécution sans fenêtre
:   Une exécution lancée depuis la ligne de commande, un lanceur ou une tâche planifiée, sans ouvrir la fenêtre. Consultez [Ligne de commande](command-line.md).

Expression
:   La formule d'une colonne calculée, par exemple `CONCATENER(prenom, " ", nom)`.

File
:   La liste des fichiers sources chargés sur la page **Traitement**, chacun avec son statut : **En attente**, **En cours**, **Terminé**, **Erreur** ou **Ignoré**.

Fichier de sortie
:   Le fichier qu'écrit une exécution. Le fichier source n'est pas modifié.

Fichier modèle
:   Le fichier chargé sous **Charger le modèle Excel** sur la page **Préréglages**. Il fournit les noms et les types de colonnes proposés par les éditeurs d'étapes. Le préréglage les mémorise : le fichier n'est plus nécessaire ensuite.

Fichier source
:   Un fichier Excel ou CSV auquel vous appliquez un préréglage.

Lanceur
:   Un fichier `.cmd` créé par Flash-Excel qui lance un préréglage sur des fichiers fixes d'un double-clic. Consultez [Créer un lanceur](../tasks/automate/create-a-launcher.md).

Lot
:   Plusieurs fichiers sources traités en une exécution avec le même préréglage. Chaque fichier est traité et écrit séparément.

Mode d'erreur
:   Ce que fait une exécution quand un fichier ou une étape échoue, réglé sous **En cas d'erreur** : **Passer le fichier**, **Tout arrêter** ou **Ignorer**. Consultez [Gestion des erreurs](../concepts/error-handling.md).

Modèle de nom
:   Le nom donné aux fichiers de sortie, sans extension. `{name}` représente le nom du fichier source. Par défaut : `{name}_clean`.

Nom d'action
:   Le nom technique d'un type d'étape dans un fichier de préréglage, comme `filter_rows` pour **Filtrer les lignes**. Consultez [Étapes](steps.md).

Palette
:   Un jeu de couleurs de l'interface (**Blue Gray**, **GitHub**, **Warm Dark**), chacun avec un mode sombre et un mode clair.

Préréglage (preset)
:   Une liste d'étapes enregistrée sous forme de fichier `.toml`, que vous appliquez à des fichiers sources. L'interface l'appelle aussi **Preset**. Consultez [Préréglages](../concepts/presets.md).

Préréglage local
:   Un préréglage stocké dans `Documents\flash-excel\presets`, que vous pouvez modifier, enregistrer, supprimer et exporter.

Source de préréglages en lecture seule
:   Un dossier partagé ajouté dans **Paramètres** dont les préréglages sont listés à côté des vôtres, sans pouvoir être modifiés depuis Flash-Excel. Consultez [Utiliser des dossiers de préréglages partagés](../tasks/presets/use-shared-preset-folders.md).

Tâche planifiée
:   Une tâche du Planificateur de tâches Windows qui lance un préréglage chaque jour à heure fixe. Consultez [Planifier un préréglage](../tasks/automate/schedule-a-preset.md).

TOML
:   Le format texte des fichiers de préréglage. Consultez [Fichier de préréglage](preset-file.md).
